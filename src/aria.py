"""
ARIA suggester module for AccessiAI.
Suggests ARIA labels for interactive elements lacking accessibility attributes.
"""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def suggest_aria_label(element: Dict) -> Optional[str]:
    """
    Generate an appropriate aria-label for an interactive element.
    
    Args:
        element: Dictionary containing element information with keys:
                - tag: Element tag name (button, input, a)
                - text_content: Visible text content
                - input_type: Type of input (for input elements)
                - placeholder: Placeholder text (for input elements)
                - href: Link URL (for anchor elements)
                - name: Element name attribute
                - title: Element title attribute
    
    Returns:
        Suggested aria-label string or None if no suggestion can be made
    """
    tag = element.get("tag", "").lower()
    
    if tag == "button":
        return _suggest_button_label(element)
    elif tag == "input":
        return _suggest_input_label(element)
    elif tag == "a":
        return _suggest_link_label(element)
    
    return None


def _suggest_button_label(element: Dict) -> Optional[str]:
    """
    Suggest aria-label for button elements.
    
    Args:
        element: Button element dictionary
        
    Returns:
        Suggested aria-label or None
    """
    # If button has text content, use it
    text_content = element.get("text_content", "").strip()
    if text_content:
        return text_content
    
    # Check for title attribute
    title = element.get("title", "").strip()
    if title:
        return title
    
    # Check for button type to infer action
    button_type = element.get("type", "button").lower()
    if button_type == "submit":
        return "Submit form"
    elif button_type == "reset":
        return "Reset form"
    elif button_type == "button":
        return "Button"
    
    return None


def _suggest_input_label(element: Dict) -> Optional[str]:
    """
    Suggest aria-label for input elements.
    
    Args:
        element: Input element dictionary
        
    Returns:
        Suggested aria-label or None
    """
    input_type = element.get("input_type", "text").lower()
    
    # Check for placeholder
    placeholder = element.get("placeholder", "").strip()
    if placeholder:
        return placeholder
    
    # Check for name attribute
    name = element.get("name", "").strip()
    if name:
        # Convert name to readable label (e.g., "email_address" -> "Email address")
        label = name.replace("_", " ").replace("-", " ").title()
        return label
    
    # Use input type as fallback
    type_labels = {
        "text": "Text input",
        "email": "Email address",
        "password": "Password",
        "number": "Number input",
        "tel": "Telephone number",
        "url": "URL",
        "search": "Search",
        "date": "Date",
        "time": "Time",
        "checkbox": "Checkbox",
        "radio": "Radio button",
        "file": "File upload",
        "submit": "Submit",
        "reset": "Reset",
        "button": "Button"
    }
    
    return type_labels.get(input_type, f"{input_type} input")


def _suggest_link_label(element: Dict) -> Optional[str]:
    """
    Suggest aria-label for link elements.
    
    Args:
        element: Link element dictionary
        
    Returns:
        Suggested aria-label or None
    """
    # If link has text content, use it
    text_content = element.get("text_content", "").strip()
    if text_content:
        return text_content
    
    # Check for title attribute
    title = element.get("title", "").strip()
    if title:
        return title
    
    # Try to extract meaningful text from href
    href = element.get("href", "").strip()
    if href:
        # Remove protocol and domain
        if "://" in href:
            href = href.split("://", 1)[1]
        if "/" in href:
            href = href.split("/", 1)[1]
        
        # Remove file extensions and query parameters
        if "?" in href:
            href = href.split("?")[0]
        if "." in href:
            href = href.rsplit(".", 1)[0]
        
        # Get the last path segment (filename or last directory)
        if "/" in href:
            href = href.split("/")[-1]
        
        # Convert to readable label
        if href:
            label = href.replace("-", " ").replace("_", " ").title()
            return label
    
    return "Link"


def check_aria_compliance(elements: List[Dict]) -> List[Dict]:
    """
    Identify interactive elements lacking ARIA labels and suggest fixes.
    
    Args:
        elements: List of interactive element dictionaries from parse_interactive_elements()
    
    Returns:
        List of dictionaries containing ARIA compliance issues and suggestions
    """
    aria_issues = []
    
    for element in elements:
        tag = element.get("tag", "").lower()
        
        # Check if element already has a label
        has_label = element.get("has_label", False)
        
        if has_label:
            # Element already has accessible label
            continue
        
        # Element lacks accessible label - suggest one
        suggested_label = suggest_aria_label(element)
        
        if suggested_label:
            issue_data = {
                "element_id": element.get("element_id"),
                "element_type": tag,
                "issue": _get_issue_description(element),
                "suggested_aria_label": suggested_label,
                "current_aria_label": element.get("aria_label", ""),
                "current_text": element.get("text_content", "")
            }
            aria_issues.append(issue_data)
    
    return aria_issues


def _get_issue_description(element: Dict) -> str:
    """
    Generate a description of the ARIA compliance issue.
    
    Args:
        element: Element dictionary
        
    Returns:
        Description of the issue
    """
    tag = element.get("tag", "").lower()
    
    if tag == "button":
        return "Button lacks text content and aria-label"
    elif tag == "input":
        return "Input lacks associated label and aria-label"
    elif tag == "a":
        return "Link lacks text content and aria-label"
    
    return "Element lacks accessible label"
