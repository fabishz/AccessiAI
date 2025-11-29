"""
Report generator module for AccessiAI.
Compiles accessibility findings into structured JSON reports and patched HTML.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def generate_report(
    url: str,
    alt_text_issues: List[Dict],
    contrast_issues: List[Dict],
    aria_issues: List[Dict]
) -> Dict:
    """
    Generate a comprehensive accessibility report from all findings.
    
    Args:
        url: The analyzed webpage URL
        alt_text_issues: List of alt text issues from image_analyzer
        contrast_issues: List of contrast issues from contrast checker
        aria_issues: List of ARIA issues from aria suggester
    
    Returns:
        Dictionary containing structured report with summary and categorized issues
    """
    # Calculate summary statistics
    total_issues = len(alt_text_issues) + len(contrast_issues) + len(aria_issues)
    
    report = {
        "url": url,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total_issues": total_issues,
            "alt_text_issues": len(alt_text_issues),
            "contrast_issues": len(contrast_issues),
            "aria_issues": len(aria_issues)
        },
        "issues": {
            "alt_text": _format_alt_text_issues(alt_text_issues),
            "contrast": _format_contrast_issues(contrast_issues),
            "aria": _format_aria_issues(aria_issues)
        }
    }
    
    logger.info(f"Generated report for {url} with {total_issues} issues")
    return report


def _format_alt_text_issues(issues: List[Dict]) -> List[Dict]:
    """
    Format alt text issues for report.
    
    Args:
        issues: List of image dictionaries with generated_alt_text
    
    Returns:
        Formatted list of alt text issues
    """
    formatted_issues = []
    
    for issue in issues:
        # Only include images that lack alt text but have generated suggestions
        if not issue.get("has_alt") and issue.get("generated_alt_text"):
            formatted_issue = {
                "element_id": issue.get("element_id", "unknown"),
                "current_alt": issue.get("alt_text", ""),
                "suggested_alt": issue.get("generated_alt_text", ""),
                "image_url": issue.get("url", "")
            }
            formatted_issues.append(formatted_issue)
    
    return formatted_issues


def _format_contrast_issues(issues: List[Dict]) -> List[Dict]:
    """
    Format contrast issues for report with suggested fixes.
    
    Args:
        issues: List of contrast issues from check_contrast()
    
    Returns:
        Formatted list of contrast issues with suggested fixes
    """
    from src.contrast import suggest_color_fix, calculate_contrast_ratio
    
    formatted_issues = []
    
    for issue in issues:
        current_fg = issue.get("current_fg", "")
        current_bg = issue.get("current_bg", "")
        
        # Get suggested color fix
        try:
            suggested_fg = suggest_color_fix(current_fg, current_bg)
            suggested_ratio = calculate_contrast_ratio(suggested_fg, current_bg)
        except Exception as e:
            logger.warning(f"Could not suggest color fix: {e}")
            suggested_fg = current_fg
            suggested_ratio = issue.get("ratio", 0)
        
        formatted_issue = {
            "element_id": issue.get("element_id", "unknown"),
            "tag": issue.get("tag", ""),
            "text_content": issue.get("text_content", ""),
            "current_fg": current_fg,
            "current_bg": current_bg,
            "ratio": issue.get("ratio", 0),
            "required_ratio": 4.5,
            "suggested_fg": suggested_fg,
            "suggested_ratio": round(suggested_ratio, 2)
        }
        formatted_issues.append(formatted_issue)
    
    return formatted_issues


def _format_aria_issues(issues: List[Dict]) -> List[Dict]:
    """
    Format ARIA issues for report.
    
    Args:
        issues: List of ARIA issues from check_aria_compliance()
    
    Returns:
        Formatted list of ARIA issues
    """
    formatted_issues = []
    
    for issue in issues:
        formatted_issue = {
            "element_id": issue.get("element_id", "unknown"),
            "element_type": issue.get("element_type", ""),
            "issue": issue.get("issue", ""),
            "suggested_aria_label": issue.get("suggested_aria_label", ""),
            "current_aria_label": issue.get("current_aria_label", ""),
            "current_text": issue.get("current_text", "")
        }
        formatted_issues.append(formatted_issue)
    
    return formatted_issues


def generate_patched_html(
    original_html: str,
    alt_text_issues: List[Dict],
    contrast_issues: List[Dict],
    aria_issues: List[Dict]
) -> str:
    """
    Generate HTML with suggested accessibility fixes applied.
    
    Args:
        original_html: Original HTML content
        alt_text_issues: List of alt text issues with suggestions
        contrast_issues: List of contrast issues with suggestions
        aria_issues: List of ARIA issues with suggestions
    
    Returns:
        Modified HTML string with fixes applied
    """
    try:
        soup = BeautifulSoup(original_html, "html.parser")
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return original_html
    
    # Apply alt text fixes
    for issue in alt_text_issues:
        element_id = issue.get("element_id", "")
        suggested_alt = issue.get("suggested_alt", "")
        
        if element_id and suggested_alt:
            try:
                element = soup.find(id=element_id)
                if element and element.name == "img":
                    element["alt"] = suggested_alt
                    logger.debug(f"Applied alt text fix to {element_id}")
            except Exception as e:
                logger.warning(f"Could not apply alt text fix to {element_id}: {e}")
    
    # Apply contrast fixes
    for issue in contrast_issues:
        element_id = issue.get("element_id", "")
        suggested_fg = issue.get("suggested_fg", "")
        
        if element_id and suggested_fg:
            try:
                element = soup.find(id=element_id)
                if element:
                    # Update inline style with new color
                    current_style = element.get("style", "")
                    
                    # Remove existing color property if present
                    style_parts = []
                    for part in current_style.split(";"):
                        if "color:" not in part.lower() or "background" in part.lower():
                            if part.strip():
                                style_parts.append(part.strip())
                    
                    # Add new color
                    new_style = "; ".join(style_parts)
                    if new_style:
                        new_style += f"; color: {suggested_fg}"
                    else:
                        new_style = f"color: {suggested_fg}"
                    
                    element["style"] = new_style
                    logger.debug(f"Applied contrast fix to {element_id}")
            except Exception as e:
                logger.warning(f"Could not apply contrast fix to {element_id}: {e}")
    
    # Apply ARIA fixes
    for issue in aria_issues:
        element_id = issue.get("element_id", "")
        suggested_label = issue.get("suggested_aria_label", "")
        
        if element_id and suggested_label:
            try:
                element = soup.find(id=element_id)
                if element:
                    element["aria-label"] = suggested_label
                    logger.debug(f"Applied ARIA fix to {element_id}")
            except Exception as e:
                logger.warning(f"Could not apply ARIA fix to {element_id}: {e}")
    
    return str(soup.prettify())


def export_report(
    report: Dict,
    format: str = "json",
    output_path: Optional[str] = None
) -> str:
    """
    Export report to file in specified format.
    
    Args:
        report: Report dictionary from generate_report()
        format: Export format ("json" or "html")
        output_path: Path to save file. If None, generates default filename.
    
    Returns:
        Path to exported file
        
    Raises:
        ValueError: If format is not supported
        IOError: If file cannot be written
    """
    if format not in ["json", "html"]:
        raise ValueError(f"Unsupported export format: {format}. Use 'json' or 'html'")
    
    # Generate output path if not provided
    if output_path is None:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"accessibility_report_{timestamp}.{format}"
        output_path = str(Path("reports") / filename)
    
    # Create reports directory if it doesn't exist
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        elif format == "html":
            html_content = _generate_html_report(report)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        
        logger.info(f"Report exported to {output_path}")
        return output_path
    
    except IOError as e:
        logger.error(f"Error writing report to {output_path}: {e}")
        raise IOError(f"Could not write report to {output_path}: {e}")


def _generate_html_report(report: Dict) -> str:
    """
    Generate an HTML representation of the report.
    
    Args:
        report: Report dictionary from generate_report()
    
    Returns:
        HTML string
    """
    url = report.get("url", "Unknown")
    timestamp = report.get("timestamp", "Unknown")
    summary = report.get("summary", {})
    issues = report.get("issues", {})
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AccessiAI Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header p {{
            margin: 5px 0;
            opacity: 0.9;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .summary-card .number {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .issues-section {{
            margin-bottom: 30px;
        }}
        .issues-section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .issue {{
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .issue.alt-text {{
            border-left-color: #f39c12;
        }}
        .issue.contrast {{
            border-left-color: #e74c3c;
        }}
        .issue.aria {{
            border-left-color: #9b59b6;
        }}
        .issue-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        .issue-detail {{
            margin: 8px 0;
            font-size: 14px;
        }}
        .issue-detail strong {{
            color: #555;
            min-width: 120px;
            display: inline-block;
        }}
        .suggestion {{
            background-color: #ecf0f1;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            font-family: monospace;
            font-size: 13px;
        }}
        .no-issues {{
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AccessiAI Accessibility Report</h1>
        <p><strong>URL:</strong> {url}</p>
        <p><strong>Generated:</strong> {timestamp}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>Total Issues</h3>
            <div class="number">{summary.get('total_issues', 0)}</div>
        </div>
        <div class="summary-card">
            <h3>Alt Text Issues</h3>
            <div class="number">{summary.get('alt_text_issues', 0)}</div>
        </div>
        <div class="summary-card">
            <h3>Contrast Issues</h3>
            <div class="number">{summary.get('contrast_issues', 0)}</div>
        </div>
        <div class="summary-card">
            <h3>ARIA Issues</h3>
            <div class="number">{summary.get('aria_issues', 0)}</div>
        </div>
    </div>
"""
    
    # Alt text issues
    alt_text_issues = issues.get("alt_text", [])
    html += '<div class="issues-section">\n<h2>Alt Text Issues</h2>\n'
    if alt_text_issues:
        for issue in alt_text_issues:
            html += f"""    <div class="issue alt-text">
        <div class="issue-title">Image: {issue.get('element_id', 'Unknown')}</div>
        <div class="issue-detail"><strong>Current Alt:</strong> {issue.get('current_alt', '(empty)')}</div>
        <div class="issue-detail"><strong>Image URL:</strong> {issue.get('image_url', 'Unknown')}</div>
        <div class="suggestion"><strong>Suggested Alt:</strong> {issue.get('suggested_alt', '')}</div>
    </div>
"""
    else:
        html += '    <div class="no-issues">✓ No alt text issues found</div>\n'
    html += '</div>\n'
    
    # Contrast issues
    contrast_issues = issues.get("contrast", [])
    html += '<div class="issues-section">\n<h2>Color Contrast Issues</h2>\n'
    if contrast_issues:
        for issue in contrast_issues:
            html += f"""    <div class="issue contrast">
        <div class="issue-title">Element: {issue.get('element_id', 'Unknown')} ({issue.get('tag', '')})</div>
        <div class="issue-detail"><strong>Text:</strong> {issue.get('text_content', '')}</div>
        <div class="issue-detail"><strong>Current Ratio:</strong> {issue.get('ratio', 0)}:1 (Required: {issue.get('required_ratio', 4.5)}:1)</div>
        <div class="issue-detail"><strong>Current Colors:</strong> Text {issue.get('current_fg', '')} on {issue.get('current_bg', '')}</div>
        <div class="suggestion"><strong>Suggested Fix:</strong> Change text color to {issue.get('suggested_fg', '')} for {issue.get('suggested_ratio', 0)}:1 ratio</div>
    </div>
"""
    else:
        html += '    <div class="no-issues">✓ No contrast issues found</div>\n'
    html += '</div>\n'
    
    # ARIA issues
    aria_issues = issues.get("aria", [])
    html += '<div class="issues-section">\n<h2>ARIA Label Issues</h2>\n'
    if aria_issues:
        for issue in aria_issues:
            html += f"""    <div class="issue aria">
        <div class="issue-title">{issue.get('element_type', 'Element').title()}: {issue.get('element_id', 'Unknown')}</div>
        <div class="issue-detail"><strong>Issue:</strong> {issue.get('issue', '')}</div>
        <div class="issue-detail"><strong>Current Text:</strong> {issue.get('current_text', '(empty)')}</div>
        <div class="suggestion"><strong>Suggested aria-label:</strong> "{issue.get('suggested_aria_label', '')}"</div>
    </div>
"""
    else:
        html += '    <div class="no-issues">✓ No ARIA issues found</div>\n'
    html += '</div>\n'
    
    html += """</body>
</html>"""
    
    return html
