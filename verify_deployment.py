#!/usr/bin/env python3
"""
Quick deployment verification script for AccessiAI.
Verifies key aspects without running full analysis.
"""

import sys
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def verify_file_structure():
    """Verify all required files exist."""
    logger.info("Checking file structure...")
    required_files = [
        "app.py",
        "requirements.txt",
        "README.md",
        "DEPLOYMENT_GUIDE.md",
        "DEMO_SCRIPT.md",
        "src/parser.py",
        "src/contrast.py",
        "src/aria.py",
        "src/image_analyzer.py",
        "src/report.py",
        "src/analyzer.py",
        "tests/test_parser.py",
        "tests/test_contrast.py",
        "tests/test_aria.py",
        "tests/test_report.py",
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
            logger.error(f"  ✗ Missing: {file_path}")
        else:
            logger.info(f"  ✓ Found: {file_path}")
    
    return len(missing) == 0, missing

def verify_requirements_txt():
    """Verify requirements.txt contains all dependencies."""
    logger.info("\nVerifying requirements.txt...")
    required_packages = [
        "streamlit",
        "transformers",
        "torch",
        "beautifulsoup4",
        "webcolors",
        "pillow",
        "requests",
    ]
    
    with open("requirements.txt", "r") as f:
        content = f.read().lower()
    
    missing = []
    for package in required_packages:
        if package.lower() in content:
            logger.info(f"  ✓ {package} found")
        else:
            missing.append(package)
            logger.error(f"  ✗ {package} NOT found")
    
    return len(missing) == 0, missing

def verify_app_py():
    """Verify app.py has required components."""
    logger.info("\nVerifying app.py...")
    required_components = [
        "streamlit",
        "analyze_webpage_safe",
        "is_valid_url",
        "display_results",
        "display_summary",
        "display_alt_text_issues",
        "display_contrast_issues",
        "display_aria_issues",
    ]
    
    with open("app.py", "r") as f:
        content = f.read()
    
    missing = []
    for component in required_components:
        if component in content:
            logger.info(f"  ✓ {component} found")
        else:
            missing.append(component)
            logger.error(f"  ✗ {component} NOT found")
    
    return len(missing) == 0, missing

def verify_module_structure():
    """Verify all modules have required functions."""
    logger.info("\nVerifying module structure...")
    
    modules = {
        "src/parser.py": ["fetch_webpage", "parse_images", "parse_interactive_elements", "extract_colors"],
        "src/contrast.py": ["hex_to_rgb", "calculate_luminance", "calculate_contrast_ratio", "check_contrast", "suggest_color_fix"],
        "src/aria.py": ["suggest_aria_label", "check_aria_compliance"],
        "src/image_analyzer.py": ["download_image", "generate_alt_text", "process_images"],
        "src/report.py": ["generate_report", "generate_patched_html", "export_report"],
        "src/analyzer.py": ["analyze_webpage", "analyze_webpage_safe"],
    }
    
    all_ok = True
    for module_path, functions in modules.items():
        logger.info(f"  Checking {module_path}...")
        with open(module_path, "r") as f:
            content = f.read()
        
        missing = []
        for func in functions:
            if f"def {func}" in content:
                logger.info(f"    ✓ {func}")
            else:
                missing.append(func)
                logger.error(f"    ✗ {func} NOT found")
                all_ok = False
    
    return all_ok

def verify_documentation():
    """Verify documentation files exist and have content."""
    logger.info("\nVerifying documentation...")
    
    docs = {
        "README.md": ["AccessiAI", "installation", "usage"],
        "DEPLOYMENT_GUIDE.md": ["deployment", "docker", "aws"],
        "DEMO_SCRIPT.md": ["demo", "introduction", "features"],
    }
    
    all_ok = True
    for doc_path, keywords in docs.items():
        logger.info(f"  Checking {doc_path}...")
        if not os.path.exists(doc_path):
            logger.error(f"    ✗ {doc_path} NOT found")
            all_ok = False
            continue
        
        with open(doc_path, "r") as f:
            content = f.read().lower()
        
        for keyword in keywords:
            if keyword.lower() in content:
                logger.info(f"    ✓ Contains '{keyword}'")
            else:
                logger.warning(f"    ⚠ Missing '{keyword}'")
    
    return all_ok

def verify_test_files():
    """Verify test files exist."""
    logger.info("\nVerifying test files...")
    
    test_files = [
        "tests/test_parser.py",
        "tests/test_contrast.py",
        "tests/test_aria.py",
        "tests/test_report.py",
    ]
    
    all_ok = True
    for test_file in test_files:
        if os.path.exists(test_file):
            logger.info(f"  ✓ {test_file} found")
        else:
            logger.error(f"  ✗ {test_file} NOT found")
            all_ok = False
    
    return all_ok

def main():
    """Run all verification checks."""
    logger.info("=" * 60)
    logger.info("AccessiAI Deployment Verification")
    logger.info("=" * 60)
    
    results = {}
    
    # Run all checks
    results["File Structure"] = verify_file_structure()[0]
    results["Requirements.txt"] = verify_requirements_txt()[0]
    results["app.py"] = verify_app_py()[0]
    results["Module Structure"] = verify_module_structure()
    results["Documentation"] = verify_documentation()
    results["Test Files"] = verify_test_files()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{check}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("\n✓ APPLICATION IS READY FOR DEPLOYMENT")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} CHECK(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
