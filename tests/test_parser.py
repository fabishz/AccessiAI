"""
Unit tests for the webpage parser module.
"""

import pytest
from bs4 import BeautifulSoup
from src.parser import (
    parse_images,
    parse_interactive_elements,
    extract_colors,
    _extract_color_from_style,
    fetch_webpage
)


class TestParseImages:
    """Tests for parse_images function."""
    
    def test_parse_images_with_alt_text(self):
        """Test parsing images that have alt text."""
        html = """
        <html>
            <body>
                <img src="image1.jpg" alt="A red apple">
                <img src="image2.jpg" alt="A blue sky">
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        images = parse_images(soup)
        
        assert len(images) == 2
        assert images[0]["url"] == "image1.jpg"
        assert images[0]["alt_text"] == "A red apple"
        assert images[0]["has_alt"] is True
        assert images[1]["alt_text"] == "A blue sky"
    
    def test_parse_images_without_alt_text(self):
        """Test parsing images that lack alt text."""
        html = """
        <html>
            <body>
                <img src="image1.jpg">
                <img src="image2.jpg" alt="">
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        images = parse_images(soup)
        
        assert len(images) == 2
        assert images[0]["has_alt"] is False
        assert images[1]["has_alt"] is False
    
    def test_parse_images_limit_to_10(self):
        """Test that only first 10 images are extracted."""
        html = "<html><body>"
        for i in range(15):
            html += f'<img src="image{i}.jpg" alt="Image {i}">'
        html += "</body></html>"
        
        soup = BeautifulSoup(html, "html.parser")
        images = parse_images(soup)
        
        assert len(images) == 10


class TestParseInteractiveElements:
    """Tests for parse_interactive_elements function."""
    
    def test_parse_buttons(self):
        """Test parsing button elements."""
        html = """
        <html>
            <body>
                <button id="btn1">Submit</button>
                <button aria-label="Close dialog">×</button>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        elements = parse_interactive_elements(soup)
        
        buttons = [e for e in elements if e["tag"] == "button"]
        assert len(buttons) == 2
        assert buttons[0]["text_content"] == "Submit"
        assert buttons[0]["has_label"] is True
        assert buttons[1]["aria_label"] == "Close dialog"
    
    def test_parse_inputs(self):
        """Test parsing input elements."""
        html = """
        <html>
            <body>
                <input type="text" id="email" placeholder="Enter email">
                <input type="password" aria-label="Password field">
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        elements = parse_interactive_elements(soup)
        
        inputs = [e for e in elements if e["tag"] == "input"]
        assert len(inputs) == 2
        assert inputs[0]["input_type"] == "text"
        assert inputs[0]["placeholder"] == "Enter email"
        assert inputs[1]["aria_label"] == "Password field"
    
    def test_parse_links(self):
        """Test parsing link elements."""
        html = """
        <html>
            <body>
                <a href="/home">Home</a>
                <a href="/about" aria-label="About us page">About</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        elements = parse_interactive_elements(soup)
        
        links = [e for e in elements if e["tag"] == "a"]
        assert len(links) == 2
        assert links[0]["text_content"] == "Home"
        assert links[0]["href"] == "/home"
        assert links[1]["aria_label"] == "About us page"


class TestExtractColors:
    """Tests for extract_colors function."""
    
    def test_extract_inline_colors(self):
        """Test extracting colors from inline styles."""
        html = """
        <html>
            <body>
                <p style="color: #000000; background-color: #ffffff;">Black text on white</p>
                <span style="color: rgb(255, 0, 0);">Red text</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        colors = extract_colors(soup)
        
        assert len(colors) >= 2
        assert colors[0]["fg_color"] == "#000000"
        assert colors[0]["bg_color"] == "#ffffff"
        assert colors[1]["fg_color"] == "rgb(255, 0, 0)"
    
    def test_extract_colors_skips_empty_elements(self):
        """Test that empty elements are skipped."""
        html = """
        <html>
            <body>
                <p></p>
                <p style="color: #000000;">Text</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        colors = extract_colors(soup)
        
        # Should only have one element (the one with text)
        assert len(colors) == 1


class TestExtractColorFromStyle:
    """Tests for _extract_color_from_style helper function."""
    
    def test_extract_color_property(self):
        """Test extracting color property."""
        style = "color: #ff0000; margin: 10px;"
        color = _extract_color_from_style(style, "color")
        assert color == "#ff0000"
    
    def test_extract_background_color(self):
        """Test extracting background-color property."""
        style = "background-color: #00ff00; padding: 5px;"
        color = _extract_color_from_style(style, "background-color")
        assert color == "#00ff00"
    
    def test_extract_color_with_important(self):
        """Test extracting color with !important flag."""
        style = "color: #0000ff !important;"
        color = _extract_color_from_style(style, "color")
        assert color == "#0000ff"
    
    def test_extract_color_not_found(self):
        """Test when color property is not found."""
        style = "margin: 10px; padding: 5px;"
        color = _extract_color_from_style(style, "color")
        assert color is None


class TestFetchWebpage:
    """Tests for fetch_webpage function."""
    
    def test_fetch_webpage_invalid_url_format(self):
        """Test that invalid URL format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            fetch_webpage("not-a-url")
    
    def test_fetch_webpage_empty_url(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="URL cannot be empty"):
            fetch_webpage("")
    
    def test_fetch_webpage_valid_url(self):
        """Test fetching a valid webpage."""
        # Using example.com as a stable test URL
        html = fetch_webpage("https://example.com")
        assert html is not None
        assert len(html) > 0
        assert "example" in html.lower()
