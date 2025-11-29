"""
Webpage parser module for AccessiAI.
Extracts accessibility-relevant elements from HTML content.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Constants
FETCH_TIMEOUT = 5  # seconds
MAX_IMAGES = 10
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def fetch_webpage(url: str) -> str:
    """
    Fetch HTML content from a webpage with timeout and error handling.
    
    Args:
        url: The URL to fetch
        
    Returns:
        HTML content as string
        
    Raises:
        ValueError: If URL is invalid or unreachable
        requests.Timeout: If request exceeds timeout
    """
    # Validate URL format
    if not url:
        raise ValueError("URL cannot be empty")
    
    if not url.startswith(("http://", "https://")):
        raise ValueError("Invalid URL format. URL must start with http:// or https://")
    
    try:
        headers = {"User-Agent": DEFAULT_USER_AGENT}
        response = requests.get(url, timeout=FETCH_TIMEOUT, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        raise ValueError(f"Page not accessible: Request timed out after {FETCH_TIMEOUT} seconds")
    except requests.exceptions.ConnectionError:
        raise ValueError("Page not accessible: Connection error. Check URL and internet connection")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"Page not accessible: HTTP {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Page not accessible: {str(e)}")


def parse_images(soup: BeautifulSoup) -> List[Dict]:
    """
    Extract image elements from HTML, limiting to 10 images.
    
    Args:
        soup: BeautifulSoup object of parsed HTML
        
    Returns:
        List of dictionaries containing image information
    """
    images = []
    img_elements = soup.find_all("img")
    
    # Limit to MAX_IMAGES
    for img in img_elements[:MAX_IMAGES]:
        image_data = {
            "url": img.get("src", ""),
            "alt_text": img.get("alt", ""),
            "has_alt": bool(img.get("alt")),
            "title": img.get("title", ""),
            "element_id": img.get("id", f"img_{len(images)}")
        }
        images.append(image_data)
    
    return images


def parse_interactive_elements(soup: BeautifulSoup) -> List[Dict]:
    """
    Extract interactive elements (buttons, inputs, links) from HTML.
    
    Args:
        soup: BeautifulSoup object of parsed HTML
        
    Returns:
        List of dictionaries containing interactive element information
    """
    interactive_elements = []
    
    # Extract buttons
    buttons = soup.find_all("button")
    for idx, button in enumerate(buttons):
        element_data = {
            "tag": "button",
            "text_content": button.get_text(strip=True),
            "aria_label": button.get("aria-label", ""),
            "has_label": bool(button.get("aria-label") or button.get_text(strip=True)),
            "element_id": button.get("id", f"button_{idx}"),
            "type": button.get("type", "button")
        }
        interactive_elements.append(element_data)
    
    # Extract input elements
    inputs = soup.find_all("input")
    for idx, input_elem in enumerate(inputs):
        # Check if input has associated label
        input_id = input_elem.get("id", "")
        associated_label = None
        if input_id:
            associated_label = soup.find("label", {"for": input_id})
        
        element_data = {
            "tag": "input",
            "input_type": input_elem.get("type", "text"),
            "placeholder": input_elem.get("placeholder", ""),
            "aria_label": input_elem.get("aria-label", ""),
            "has_label": bool(associated_label or input_elem.get("aria-label")),
            "element_id": input_id or f"input_{idx}",
            "name": input_elem.get("name", "")
        }
        interactive_elements.append(element_data)
    
    # Extract links
    links = soup.find_all("a")
    for idx, link in enumerate(links):
        element_data = {
            "tag": "a",
            "text_content": link.get_text(strip=True),
            "href": link.get("href", ""),
            "aria_label": link.get("aria-label", ""),
            "has_label": bool(link.get("aria-label") or link.get_text(strip=True)),
            "element_id": link.get("id", f"link_{idx}"),
            "title": link.get("title", "")
        }
        interactive_elements.append(element_data)
    
    return interactive_elements


def extract_colors(soup: BeautifulSoup) -> List[Dict]:
    """
    Extract text and background colors from elements.
    
    Args:
        soup: BeautifulSoup object of parsed HTML
        
    Returns:
        List of dictionaries containing color information for text elements
    """
    color_elements = []
    
    # Find all elements with text content
    text_elements = soup.find_all(["p", "span", "div", "h1", "h2", "h3", "h4", "h5", "h6", "a", "button"])
    
    for idx, element in enumerate(text_elements):
        text_content = element.get_text(strip=True)
        
        # Skip empty elements
        if not text_content:
            continue
        
        # Extract inline styles
        style_attr = element.get("style", "")
        fg_color = _extract_color_from_style(style_attr, "color")
        bg_color = _extract_color_from_style(style_attr, "background-color")
        
        # If no inline styles, try to get from class
        if not fg_color or not bg_color:
            class_attr = element.get("class", [])
            if isinstance(class_attr, list):
                class_attr = " ".join(class_attr)
        
        element_data = {
            "element_id": element.get("id", f"text_{idx}"),
            "tag": element.name,
            "text_content": text_content[:100],  # Limit text preview
            "fg_color": fg_color,
            "bg_color": bg_color,
            "style": style_attr,
            "class": element.get("class", [])
        }
        
        # Only include if we found color information
        if fg_color or bg_color:
            color_elements.append(element_data)
    
    return color_elements


def _extract_color_from_style(style: str, color_property: str) -> Optional[str]:
    """
    Extract color value from CSS style string.
    
    Args:
        style: CSS style string
        color_property: Property name (e.g., "color", "background-color")
        
    Returns:
        Color value (hex or rgb) or None if not found
    """
    if not style:
        return None
    
    # Look for the property in the style string
    properties = style.split(";")
    for prop in properties:
        if ":" in prop:
            key, value = prop.split(":", 1)
            if key.strip().lower() == color_property.lower():
                color_value = value.strip()
                # Remove !important if present
                color_value = color_value.replace("!important", "").strip()
                if color_value:
                    return color_value
    
    return None
