"""
Contrast checker module for AccessiAI.
Validates color contrast ratios per WCAG standards.
"""

import re
from typing import Tuple, List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# WCAG contrast ratio threshold for normal text
WCAG_CONTRAST_THRESHOLD = 4.5


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.
    
    Args:
        hex_color: Color in hex format (e.g., "#ff0000" or "ff0000")
        
    Returns:
        Tuple of (R, G, B) values (0-255)
        
    Raises:
        ValueError: If hex color format is invalid
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip("#")
    
    # Validate hex format
    if not re.match(r"^[0-9a-fA-F]{6}$", hex_color):
        raise ValueError(f"Invalid hex color format: {hex_color}")
    
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return (r, g, b)


def _normalize_rgb(value: int) -> float:
    """
    Normalize RGB value to 0-1 range for luminance calculation.
    
    Args:
        value: RGB value (0-255)
        
    Returns:
        Normalized value (0-1)
    """
    normalized = value / 255.0
    if normalized <= 0.03928:
        return normalized / 12.92
    else:
        return ((normalized + 0.055) / 1.055) ** 2.4


def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    Calculate relative luminance of a color using WCAG formula.
    
    Formula: L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    where R, G, B are normalized values
    
    Args:
        rgb: Tuple of (R, G, B) values (0-255)
        
    Returns:
        Relative luminance (0-1)
    """
    r, g, b = rgb
    
    # Normalize RGB values
    r_norm = _normalize_rgb(r)
    g_norm = _normalize_rgb(g)
    b_norm = _normalize_rgb(b)
    
    # Apply WCAG formula
    luminance = 0.2126 * r_norm + 0.7152 * g_norm + 0.0722 * b_norm
    
    return luminance


def calculate_contrast_ratio(fg_color: str, bg_color: str) -> float:
    """
    Calculate contrast ratio between foreground and background colors.
    
    Contrast Ratio = (L1 + 0.05) / (L2 + 0.05)
    where L1 is the lighter color's luminance and L2 is the darker color's luminance
    
    Args:
        fg_color: Foreground color in hex format (e.g., "#000000")
        bg_color: Background color in hex format (e.g., "#ffffff")
        
    Returns:
        Contrast ratio (1-21)
        
    Raises:
        ValueError: If color format is invalid
    """
    try:
        fg_rgb = hex_to_rgb(fg_color)
        bg_rgb = hex_to_rgb(bg_color)
    except ValueError as e:
        raise ValueError(f"Invalid color format: {e}")
    
    fg_luminance = calculate_luminance(fg_rgb)
    bg_luminance = calculate_luminance(bg_rgb)
    
    # Ensure L1 is the lighter color
    l1 = max(fg_luminance, bg_luminance)
    l2 = min(fg_luminance, bg_luminance)
    
    # Calculate contrast ratio
    contrast_ratio = (l1 + 0.05) / (l2 + 0.05)
    
    return round(contrast_ratio, 2)


def _parse_color(color_str: str) -> Optional[str]:
    """
    Parse color string and convert to hex format if needed.
    
    Args:
        color_str: Color string (hex, rgb, or color name)
        
    Returns:
        Hex color string or None if parsing fails
    """
    if not color_str:
        return None
    
    color_str = color_str.strip()
    
    # Already hex format
    if color_str.startswith("#"):
        try:
            hex_to_rgb(color_str)
            return color_str
        except ValueError:
            return None
    
    # RGB format: rgb(r, g, b)
    if color_str.startswith("rgb"):
        match = re.search(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color_str)
        if match:
            r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return f"#{r:02x}{g:02x}{b:02x}"
    
    return None


def check_contrast(elements: List[Dict]) -> List[Dict]:
    """
    Validate color contrast ratios for text elements and flag failures.
    
    Args:
        elements: List of element dictionaries with fg_color and bg_color
        
    Returns:
        List of elements with contrast ratio and pass/fail status
    """
    if not elements:
        logger.info("No elements to check for contrast")
        return []
    
    logger.info(f"Checking contrast for {len(elements)} elements")
    contrast_issues = []
    successful_count = 0
    failed_count = 0
    skipped_count = 0
    
    for element in elements:
        try:
            fg_color = element.get("fg_color")
            bg_color = element.get("bg_color")
            element_id = element.get("element_id", "unknown")
            
            # Skip if colors are missing
            if not fg_color or not bg_color:
                logger.debug(f"Element {element_id}: Skipped (missing color information)")
                skipped_count += 1
                continue
            
            # Parse colors to hex format
            fg_hex = _parse_color(fg_color)
            bg_hex = _parse_color(bg_color)
            
            if not fg_hex or not bg_hex:
                logger.warning(f"Element {element_id}: Could not parse colors - FG: {fg_color}, BG: {bg_color}")
                skipped_count += 1
                continue
            
            try:
                ratio = calculate_contrast_ratio(fg_hex, bg_hex)
                
                issue_data = {
                    "element_id": element_id,
                    "tag": element.get("tag"),
                    "text_content": element.get("text_content"),
                    "current_fg": fg_hex,
                    "current_bg": bg_hex,
                    "ratio": ratio,
                    "passes": ratio >= WCAG_CONTRAST_THRESHOLD
                }
                
                # Only include failures
                if not issue_data["passes"]:
                    logger.warning(f"Element {element_id}: Contrast ratio {ratio}:1 below threshold {WCAG_CONTRAST_THRESHOLD}:1")
                    contrast_issues.append(issue_data)
                    failed_count += 1
                else:
                    logger.debug(f"Element {element_id}: Contrast ratio {ratio}:1 passes threshold")
                    successful_count += 1
            
            except ValueError as e:
                logger.warning(f"Element {element_id}: Error calculating contrast - {e}")
                skipped_count += 1
                continue
        
        except Exception as e:
            logger.error(f"Unexpected error checking contrast for element: {e}")
            skipped_count += 1
            continue
    
    logger.info(f"Contrast check complete: {successful_count} passed, {failed_count} failed, {skipped_count} skipped")
    return contrast_issues


def suggest_color_fix(current_fg: str, bg_color: str, target_ratio: float = 4.5) -> str:
    """
    Suggest a corrected foreground color to achieve target contrast ratio.
    
    Args:
        current_fg: Current foreground color in hex format
        bg_color: Background color in hex format
        target_ratio: Target contrast ratio (default 4.5 for WCAG AA)
        
    Returns:
        Suggested hex color that achieves target contrast ratio
        
    Raises:
        ValueError: If color format is invalid
    """
    try:
        logger.debug(f"Suggesting color fix for FG: {current_fg}, BG: {bg_color}")
        
        bg_hex = _parse_color(bg_color)
        if not bg_hex:
            raise ValueError(f"Invalid background color: {bg_color}")
        
        bg_rgb = hex_to_rgb(bg_hex)
        bg_luminance = calculate_luminance(bg_rgb)
        logger.debug(f"Background luminance: {bg_luminance}")
    
    except ValueError as e:
        error_msg = f"Error processing background color: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        # Determine if we should use black or white based on background luminance
        # If background is light, use black; if dark, use white
        if bg_luminance > 0.5:
            # Light background - use black
            suggested_color = "#000000"
            logger.debug("Light background detected, suggesting black text")
        else:
            # Dark background - use white
            suggested_color = "#ffffff"
            logger.debug("Dark background detected, suggesting white text")
        
        # Verify the suggested color achieves target ratio
        try:
            ratio = calculate_contrast_ratio(suggested_color, bg_hex)
            logger.debug(f"Suggested color ratio: {ratio}:1 (target: {target_ratio}:1)")
            if ratio >= target_ratio:
                logger.info(f"Suggested color {suggested_color} achieves target ratio {ratio}:1")
                return suggested_color
        except ValueError as e:
            logger.warning(f"Error verifying suggested color: {e}")
        
        # If simple black/white doesn't work, try to find optimal color
        # For now, return the best of black/white
        logger.debug("Comparing black and white for best contrast")
        black_ratio = calculate_contrast_ratio("#000000", bg_hex)
        white_ratio = calculate_contrast_ratio("#ffffff", bg_hex)
        
        best_color = "#000000" if black_ratio >= white_ratio else "#ffffff"
        best_ratio = max(black_ratio, white_ratio)
        logger.info(f"Selected {best_color} with ratio {best_ratio}:1")
        return best_color
    
    except Exception as e:
        logger.error(f"Unexpected error suggesting color fix: {e}")
        # Fallback to black
        logger.warning("Falling back to black text color")
        return "#000000"
