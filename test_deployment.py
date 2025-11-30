#!/usr/bin/env python3
"""
Deployment and final testing script for AccessiAI.
Tests the full application locally with multiple URLs and verifies all functionality.
"""

import sys
import logging
from typing import Dict, List, Tuple
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test URLs
TEST_URLS = [
    "https://example.com",
    "https://www.wikipedia.org",
]

# Invalid URLs for error handling testing
INVALID_URLS = [
    "not-a-url",
    "https://invalid-url-12345-nonexistent.com",
    "",
]


def test_dependencies() -> Tuple[bool, List[str]]:
    """
    Verify all required dependencies are installed.
    
    Returns:
        Tuple of (success: bool, messages: List[str])
    """
    logger.info("=" * 60)
    logger.info("Testing Dependencies")
    logger.info("=" * 60)
    
    messages = []
    required_packages = {
        "streamlit": "Streamlit UI framework",
        "beautifulsoup4": "HTML parsing",
        "transformers": "BLIP model for image captioning",
        "torch": "Deep learning framework",
        "pillow": "Image processing",
        "webcolors": "Color conversion utilities",
        "requests": "HTTP requests",
    }
    
    all_installed = True
    
    for package, description in required_packages.items():
        try:
            __import__(package.replace("-", "_"))
            msg = f"✓ {package}: {description}"
            logger.info(msg)
            messages.append(msg)
        except ImportError:
            msg = f"✗ {package}: NOT INSTALLED - {description}"
            logger.error(msg)
            messages.append(msg)
            all_installed = False
    
    if all_installed:
        logger.info("✓ All dependencies installed successfully")
    else:
        logger.error("✗ Some dependencies are missing. Run: pip install -r requirements.txt")
    
    return all_installed, messages


def test_module_imports() -> Tuple[bool, List[str]]:
    """
    Verify all application modules can be imported.
    
    Returns:
        Tuple of (success: bool, messages: List[str])
    """
    logger.info("\n" + "=" * 60)
    logger.info("Testing Module Imports")
    logger.info("=" * 60)
    
    messages = []
    modules = [
        ("src.parser", "Webpage parser"),
        ("src.contrast", "Contrast checker"),
        ("src.aria", "ARIA suggester"),
        ("src.image_analyzer", "Image analyzer"),
        ("src.report", "Report generator"),
        ("src.analyzer", "Main analyzer"),
    ]
    
    all_imported = True
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            msg = f"✓ {module_name}: {description}"
            logger.info(msg)
            messages.append(msg)
        except ImportError as e:
            msg = f"✗ {module_name}: IMPORT FAILED - {description} - {e}"
            logger.error(msg)
            messages.append(msg)
            all_imported = False
        except Exception as e:
            msg = f"✗ {module_name}: ERROR - {description} - {e}"
            logger.error(msg)
            messages.append(msg)
            all_imported = False
    
    if all_imported:
        logger.info("✓ All modules imported successfully")
    else:
        logger.error("✗ Some modules failed to import")
    
    return all_imported, messages


def test_valid_urls() -> Tuple[bool, List[str]]:
    """
    Test analysis with valid URLs.
    
    Returns:
        Tuple of (success: bool, messages: List[str])
    """
    logger.info("\n" + "=" * 60)
    logger.info("Testing Valid URLs")
    logger.info("=" * 60)
    
    messages = []
    
    try:
        from src.analyzer import analyze_webpage_safe
    except ImportError as e:
        msg = f"✗ Could not import analyzer: {e}"
        logger.error(msg)
        messages.append(msg)
        return False, messages
    
    all_passed = True
    
    for url in TEST_URLS:
        try:
            logger.info(f"\nTesting URL: {url}")
            result = analyze_webpage_safe(url, include_patched_html=True)
            
            if result.get("success"):
                report = result.get("report", {})
                summary = report.get("summary", {})
                
                msg = f"✓ {url}: Analysis successful"
                logger.info(msg)
                messages.append(msg)
                
                # Log summary
                total_issues = summary.get("total_issues", 0)
                alt_text = summary.get("alt_text_issues", 0)
                contrast = summary.get("contrast_issues", 0)
                aria = summary.get("aria_issues", 0)
                
                summary_msg = f"  - Total issues: {total_issues} (Alt text: {alt_text}, Contrast: {contrast}, ARIA: {aria})"
                logger.info(summary_msg)
                messages.append(summary_msg)
                
                # Verify patched HTML
                patched_html = result.get("patched_html")
                if patched_html:
                    msg = f"  - Patched HTML generated: {len(patched_html)} characters"
                    logger.info(msg)
                    messages.append(msg)
                else:
                    msg = f"  - Warning: Patched HTML not generated"
                    logger.warning(msg)
                    messages.append(msg)
            else:
                errors = result.get("errors", [])
                msg = f"✗ {url}: Analysis failed - {', '.join(errors)}"
                logger.error(msg)
                messages.append(msg)
                all_passed = False
        
        except Exception as e:
            msg = f"✗ {url}: Exception during analysis - {e}"
            logger.error(msg)
            messages.append(msg)
            all_passed = False
    
    if all_passed:
        logger.info("\n✓ All valid URL tests passed")
    else:
        logger.error("\n✗ Some valid URL tests failed")
    
    return all_passed, messages


def test_invalid_urls() -> Tuple[bool, List[str]]:
    """
    Test error handling with invalid URLs.
    
    Returns:
        Tuple of (success: bool, messages: List[str])
    """
    logger.info("\n" + "=" * 60)
    logger.info("Testing Invalid URLs (Error Handling)")
    logger.info("=" * 60)
    
    messages = []
    
    try:
        from src.analyzer import analyze_webpage_safe
    except ImportError as e:
        msg = f"✗ Could not import analyzer: {e}"
        logger.error(msg)
        messages.append(msg)
        return False, messages
    
    all_passed = True
    
    for url in INVALID_URLS:
        try:
            logger.info(f"\nTesting invalid URL: '{url}'")
            result = analyze_webpage_safe(url, include_patched_html=False)
            
            if not result.get("success"):
                errors = result.get("errors", [])
                msg = f"✓ Correctly rejected invalid URL: {url}"
                logger.info(msg)
                messages.append(msg)
                
                if errors:
                    error_msg = f"  - Error message: {errors[0]}"
                    logger.info(error_msg)
                    messages.append(error_msg)
            else:
                msg = f"✗ Invalid URL was not rejected: {url}"
                logger.error(msg)
                messages.append(msg)
                all_passed = False
        
        except Exception as e:
            msg = f"✗ Unexpected exception for invalid URL '{url}': {e}"
            logger.error(msg)
            messages.append(msg)
            all_passed = False
    
    if all_passed:
        logger.info("\n✓ All invalid URL tests passed (errors handled correctly)")
    else:
        logger.error("\n✗ Some invalid URL tests failed")
    
    return all_passed, messages


def test_export_functionality() -> Tuple[bool, List[str]]:
    """
    Test report export functionality (JSON and HTML).
    
    Returns:
        Tuple of (success: bool, messages: List[str])
    """
    logger.info("\n" + "=" * 60)
    logger.info("Testing Export Functionality")
    logger.info("=" * 60)
    
    messages = []
    
    try:
        from src.report import export_report, generate_report
    except ImportError as e:
        msg = f"✗ Could not import report module: {e}"
        logger.error(msg)
        messages.append(msg)
        return False, messages
    
    all_passed = True
    
    # Create a sample report
    try:
        logger.info("Creating sample report...")
        sample_report = generate_report(
            url="https://example.com",
            alt_text_issues=[
                {
                    "element_id": "img_1",
                    "alt_text": "",
                    "has_alt": False,
                    "generated_alt_text": "A sample image",
                    "url": "https://example.com/image.jpg"
                }
            ],
            contrast_issues=[
                {
                    "element_id": "p_1",
                    "tag": "p",
                    "text_content": "Sample text",
                    "current_fg": "#666666",
                    "current_bg": "#f0f0f0",
                    "ratio": 3.2
                }
            ],
            aria_issues=[
                {
                    "element_id": "button_1",
                    "element_type": "button",
                    "issue": "No text or aria-label",
                    "suggested_aria_label": "Submit form",
                    "current_aria_label": "",
                    "current_text": ""
                }
            ]
        )
        msg = "✓ Sample report created successfully"
        logger.info(msg)
        messages.append(msg)
    except Exception as e:
        msg = f"✗ Failed to create sample report: {e}"
        logger.error(msg)
        messages.append(msg)
        return False, messages
    
    # Test JSON export
    try:
        logger.info("Testing JSON export...")
        json_path = export_report(sample_report, format="json", output_path="test_report.json")
        msg = f"✓ JSON export successful: {json_path}"
        logger.info(msg)
        messages.append(msg)
        
        # Verify JSON file
        with open(json_path, 'r') as f:
            exported_data = json.load(f)
            if exported_data.get("url") == "https://example.com":
                msg = "  - JSON file verified and readable"
                logger.info(msg)
                messages.append(msg)
            else:
                msg = "  - Warning: JSON file content mismatch"
                logger.warning(msg)
                messages.append(msg)
    except Exception as e:
        msg = f"✗ JSON export failed: {e}"
        logger.error(msg)
        messages.append(msg)
        all_passed = False
    
    # Test HTML export
    try:
        logger.info("Testing HTML export...")
        html_path = export_report(sample_report, format="html", output_path="test_report.html")
        msg = f"✓ HTML export successful: {html_path}"
        logger.info(msg)
        messages.append(msg)
        
        # Verify HTML file
        with open(html_path, 'r') as f:
            html_content = f.read()
            if "AccessiAI" in html_content and "example.com" in html_content:
                msg = "  - HTML file verified and readable"
                logger.info(msg)
                messages.append(msg)
            else:
                msg = "  - Warning: HTML file content mismatch"
                logger.warning(msg)
                messages.append(msg)
    except Exception as e:
        msg = f"✗ HTML export failed: {e}"
        logger.error(msg)
        messages.append(msg)
        all_passed = False
    
    if all_passed:
        logger.info("\n✓ All export tests passed")
    else:
        logger.error("\n✗ Some export tests failed")
    
    return all_passed, messages


def test_streamlit_ui() -> Tuple[bool, List[str]]:
    """
    Verify Streamlit UI can be imported and configured.
    
    Returns:
        Tuple of (success: bool, messages: List[str])
    """
    logger.info("\n" + "=" * 60)
    logger.info("Testing Streamlit UI")
    logger.info("=" * 60)
    
    messages = []
    
    try:
        import streamlit as st
        msg = "✓ Streamlit imported successfully"
        logger.info(msg)
        messages.append(msg)
    except ImportError as e:
        msg = f"✗ Streamlit import failed: {e}"
        logger.error(msg)
        messages.append(msg)
        return False, messages
    
    try:
        # Check if app.py exists and can be parsed
        with open("app.py", "r") as f:
            app_content = f.read()
            
        if "streamlit" in app_content and "analyze_webpage_safe" in app_content:
            msg = "✓ app.py exists and contains expected content"
            logger.info(msg)
            messages.append(msg)
        else:
            msg = "✗ app.py missing expected content"
            logger.error(msg)
            messages.append(msg)
            return False, messages
    except Exception as e:
        msg = f"✗ Error reading app.py: {e}"
        logger.error(msg)
        messages.append(msg)
        return False, messages
    
    msg = "✓ Streamlit UI verification passed"
    logger.info(msg)
    messages.append(msg)
    
    return True, messages


def verify_requirements_txt() -> Tuple[bool, List[str]]:
    """
    Verify requirements.txt contains all necessary dependencies.
    
    Returns:
        Tuple of (success: bool, messages: List[str])
    """
    logger.info("\n" + "=" * 60)
    logger.info("Verifying requirements.txt")
    logger.info("=" * 60)
    
    messages = []
    required_packages = [
        "streamlit",
        "transformers",
        "torch",
        "beautifulsoup4",
        "webcolors",
        "pillow",
        "requests",
    ]
    
    try:
        with open("requirements.txt", "r") as f:
            requirements_content = f.read().lower()
        
        msg = "✓ requirements.txt found"
        logger.info(msg)
        messages.append(msg)
        
        all_present = True
        for package in required_packages:
            if package.lower() in requirements_content:
                msg = f"✓ {package} found in requirements.txt"
                logger.info(msg)
                messages.append(msg)
            else:
                msg = f"✗ {package} NOT found in requirements.txt"
                logger.error(msg)
                messages.append(msg)
                all_present = False
        
        if all_present:
            logger.info("\n✓ All required packages listed in requirements.txt")
            return True, messages
        else:
            logger.error("\n✗ Some packages missing from requirements.txt")
            return False, messages
    
    except FileNotFoundError:
        msg = "✗ requirements.txt not found"
        logger.error(msg)
        messages.append(msg)
        return False, messages
    except Exception as e:
        msg = f"✗ Error reading requirements.txt: {e}"
        logger.error(msg)
        messages.append(msg)
        return False, messages


def generate_test_report(all_results: Dict[str, Tuple[bool, List[str]]]) -> str:
    """
    Generate a comprehensive test report.
    
    Args:
        all_results: Dictionary of test results
    
    Returns:
        Formatted test report string
    """
    report = "\n" + "=" * 60 + "\n"
    report += "DEPLOYMENT AND FINAL TESTING REPORT\n"
    report += "=" * 60 + "\n\n"
    
    total_tests = len(all_results)
    passed_tests = sum(1 for success, _ in all_results.values() if success)
    failed_tests = total_tests - passed_tests
    
    report += f"Test Summary: {passed_tests}/{total_tests} passed\n"
    report += f"Status: {'✓ READY FOR DEPLOYMENT' if failed_tests == 0 else '✗ ISSUES FOUND'}\n\n"
    
    for test_name, (success, messages) in all_results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        report += f"{test_name}: {status}\n"
        for message in messages:
            report += f"  {message}\n"
        report += "\n"
    
    report += "=" * 60 + "\n"
    report += "DEPLOYMENT CHECKLIST\n"
    report += "=" * 60 + "\n"
    report += "- [ ] All dependencies installed (pip install -r requirements.txt)\n"
    report += "- [ ] All modules import successfully\n"
    report += "- [ ] Valid URLs analyzed successfully\n"
    report += "- [ ] Invalid URLs handled with appropriate errors\n"
    report += "- [ ] Export functionality (JSON and HTML) working\n"
    report += "- [ ] Streamlit UI configured correctly\n"
    report += "- [ ] requirements.txt contains all dependencies\n"
    report += "- [ ] README.md documentation complete\n"
    report += "- [ ] Application ready for deployment\n"
    report += "\n"
    
    if failed_tests == 0:
        report += "✓ APPLICATION IS READY FOR DEPLOYMENT\n"
    else:
        report += f"✗ {failed_tests} TEST(S) FAILED - PLEASE FIX BEFORE DEPLOYMENT\n"
    
    report += "=" * 60 + "\n"
    
    return report


def main():
    """Run all deployment tests."""
    logger.info("Starting AccessiAI Deployment and Final Testing")
    logger.info("=" * 60)
    
    all_results = {}
    
    # Run all tests
    all_results["1. Dependencies"] = test_dependencies()
    all_results["2. Module Imports"] = test_module_imports()
    all_results["3. Valid URLs"] = test_valid_urls()
    all_results["4. Invalid URLs (Error Handling)"] = test_invalid_urls()
    all_results["5. Export Functionality"] = test_export_functionality()
    all_results["6. Streamlit UI"] = test_streamlit_ui()
    all_results["7. Requirements.txt"] = verify_requirements_txt()
    
    # Generate and display report
    report = generate_test_report(all_results)
    logger.info(report)
    
    # Save report to file
    try:
        with open("DEPLOYMENT_TEST_REPORT.txt", "w") as f:
            f.write(report)
        logger.info("Test report saved to DEPLOYMENT_TEST_REPORT.txt")
    except Exception as e:
        logger.error(f"Could not save test report: {e}")
    
    # Return exit code based on results
    failed_tests = sum(1 for success, _ in all_results.values() if not success)
    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
