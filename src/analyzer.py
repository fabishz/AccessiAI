"""
Main analysis orchestrator module for AccessiAI.
Coordinates all analysis modules to perform comprehensive accessibility analysis.
"""

import logging
from typing import Dict, Optional
from bs4 import BeautifulSoup

from src.parser import fetch_webpage, parse_images, parse_interactive_elements, extract_colors
from src.image_analyzer import process_images, clear_model_cache
from src.contrast import check_contrast
from src.aria import check_aria_compliance
from src.report import generate_report, generate_patched_html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_webpage(url: str, include_patched_html: bool = False) -> Dict:
    """
    Orchestrate complete accessibility analysis of a webpage.
    
    This function coordinates all analysis modules to:
    1. Fetch and parse the webpage
    2. Extract images and generate alt text
    3. Check color contrast ratios
    4. Suggest ARIA labels for interactive elements
    5. Compile findings into a comprehensive report
    
    Args:
        url: The URL of the webpage to analyze
        include_patched_html: Whether to include patched HTML in the report
    
    Returns:
        Dictionary containing:
        - report: Comprehensive accessibility report
        - patched_html: Modified HTML with fixes (if include_patched_html=True)
        - errors: List of errors encountered during analysis
        
    Raises:
        ValueError: If URL is invalid or analysis cannot proceed
    """
    logger.info(f"Starting accessibility analysis for: {url}")
    
    errors = []
    alt_text_issues = []
    contrast_issues = []
    aria_issues = []
    original_html = ""
    
    try:
        # Step 1: Fetch webpage
        logger.info("Step 1: Fetching webpage...")
        try:
            original_html = fetch_webpage(url)
            logger.info("Webpage fetched successfully")
        except ValueError as e:
            logger.error(f"Failed to fetch webpage: {e}")
            raise ValueError(f"Failed to fetch webpage: {e}")
        except Exception as e:
            error_msg = f"Unexpected error fetching webpage: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Parse HTML
        try:
            soup = BeautifulSoup(original_html, "html.parser")
            logger.info("HTML parsed successfully")
        except Exception as e:
            error_msg = f"Failed to parse HTML: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Step 2: Analyze images and generate alt text
        logger.info("Step 2: Analyzing images...")
        try:
            images = parse_images(soup)
            logger.info(f"Found {len(images)} images")
            
            if images:
                # Process images to generate alt text
                processed_images = process_images(images)
                
                # Extract alt text issues (images without alt text but with generated suggestions)
                alt_text_issues = [
                    img for img in processed_images
                    if not img.get("has_alt") and img.get("generated_alt_text")
                ]
                logger.info(f"Found {len(alt_text_issues)} images needing alt text")
            else:
                logger.info("No images found on page")
        
        except Exception as e:
            error_msg = f"Error analyzing images: {e}"
            logger.warning(error_msg)
            errors.append(error_msg)
        
        finally:
            # Clear model cache to free memory
            try:
                clear_model_cache()
                logger.debug("Model cache cleared after image analysis")
            except Exception as e:
                logger.warning(f"Error clearing model cache: {e}")
        
        # Step 3: Check color contrast
        logger.info("Step 3: Checking color contrast...")
        try:
            color_elements = extract_colors(soup)
            logger.info(f"Found {len(color_elements)} elements with color information")
            
            if color_elements:
                contrast_issues = check_contrast(color_elements)
                logger.info(f"Found {len(contrast_issues)} contrast issues")
            else:
                logger.info("No elements with explicit color styling found")
        
        except Exception as e:
            error_msg = f"Error checking contrast: {e}"
            logger.warning(error_msg)
            errors.append(error_msg)
        
        # Step 4: Check ARIA compliance
        logger.info("Step 4: Checking ARIA compliance...")
        try:
            interactive_elements = parse_interactive_elements(soup)
            logger.info(f"Found {len(interactive_elements)} interactive elements")
            
            if interactive_elements:
                aria_issues = check_aria_compliance(interactive_elements)
                logger.info(f"Found {len(aria_issues)} ARIA issues")
            else:
                logger.info("No interactive elements found")
        
        except Exception as e:
            error_msg = f"Error checking ARIA compliance: {e}"
            logger.warning(error_msg)
            errors.append(error_msg)
        
        # Step 5: Generate report
        logger.info("Step 5: Generating report...")
        try:
            report = generate_report(
                url=url,
                alt_text_issues=alt_text_issues,
                contrast_issues=contrast_issues,
                aria_issues=aria_issues
            )
            logger.info("Report generated successfully")
        except Exception as e:
            error_msg = f"Error generating report: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Step 6: Generate patched HTML if requested
        patched_html = None
        if include_patched_html:
            logger.info("Step 6: Generating patched HTML...")
            try:
                patched_html = generate_patched_html(
                    original_html=original_html,
                    alt_text_issues=alt_text_issues,
                    contrast_issues=contrast_issues,
                    aria_issues=aria_issues
                )
                logger.info("Patched HTML generated successfully")
            except Exception as e:
                error_msg = f"Error generating patched HTML: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # Compile results
        result = {
            "report": report,
            "patched_html": patched_html,
            "errors": errors,
            "success": True
        }
        
        logger.info(f"Analysis complete. Found {report['summary']['total_issues']} total issues")
        return result
    
    except ValueError as e:
        # Re-raise validation errors
        logger.error(f"Analysis failed with validation error: {e}")
        raise
    
    except Exception as e:
        # Catch unexpected errors
        error_msg = f"Unexpected error during analysis: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def analyze_webpage_safe(url: str, include_patched_html: bool = False) -> Dict:
    """
    Safely analyze a webpage with comprehensive error handling.
    
    This is a wrapper around analyze_webpage() that catches all exceptions
    and returns a structured error response instead of raising.
    
    Args:
        url: The URL of the webpage to analyze
        include_patched_html: Whether to include patched HTML in the report
    
    Returns:
        Dictionary containing:
        - report: Accessibility report (None if analysis failed)
        - patched_html: Modified HTML with fixes (if requested and successful)
        - errors: List of error messages
        - success: Boolean indicating if analysis succeeded
    """
    try:
        logger.info(f"Safe analysis wrapper called for: {url}")
        result = analyze_webpage(url, include_patched_html)
        logger.info("Analysis completed successfully")
        return result
    
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Validation error during analysis: {error_msg}")
        return {
            "report": None,
            "patched_html": None,
            "errors": [error_msg],
            "success": False
        }
    
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg)
        return {
            "report": None,
            "patched_html": None,
            "errors": [error_msg],
            "success": False
        }
