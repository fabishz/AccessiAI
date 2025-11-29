"""
Unit tests for the ARIA suggester module.
"""

import pytest
from src.aria import (
    suggest_aria_label,
    check_aria_compliance,
    _suggest_button_label,
    _suggest_input_label,
    _suggest_link_label,
    _get_issue_description
)


class TestSuggestButtonLabel:
    """Tests for _suggest_button_label function."""
    
    def test_suggest_button_with_text_content(self):
        """Test suggesting label for button with text content."""
        element = {
            "tag": "button",
            "text_content": "Submit",
            "type": "button"
        }
        label = _suggest_button_label(element)
        assert label == "Submit"
    
    def test_suggest_button_with_title(self):
        """Test suggesting label for button with title attribute."""
        element = {
            "tag": "button",
            "text_content": "",
            "title": "Submit the form",
            "type": "button"
        }
        label = _suggest_button_label(element)
        assert label == "Submit the form"
    
    def test_suggest_button_submit_type(self):
        """Test suggesting label for submit button without text."""
        element = {
            "tag": "button",
            "text_content": "",
            "type": "submit"
        }
        label = _suggest_button_label(element)
        assert label == "Submit form"
    
    def test_suggest_button_reset_type(self):
        """Test suggesting label for reset button without text."""
        element = {
            "tag": "button",
            "text_content": "",
            "type": "reset"
        }
        label = _suggest_button_label(element)
        assert label == "Reset form"
    
    def test_suggest_button_generic_type(self):
        """Test suggesting label for generic button without text."""
        element = {
            "tag": "button",
            "text_content": "",
            "type": "button"
        }
        label = _suggest_button_label(element)
        assert label == "Button"
    
    def test_suggest_button_no_type(self):
        """Test suggesting label for button without type attribute."""
        element = {
            "tag": "button",
            "text_content": ""
        }
        label = _suggest_button_label(element)
        assert label == "Button"


class TestSuggestInputLabel:
    """Tests for _suggest_input_label function."""
    
    def test_suggest_input_with_placeholder(self):
        """Test suggesting label for input with placeholder."""
        element = {
            "tag": "input",
            "input_type": "text",
            "placeholder": "Enter your email"
        }
        label = _suggest_input_label(element)
        assert label == "Enter your email"
    
    def test_suggest_input_with_name(self):
        """Test suggesting label for input with name attribute."""
        element = {
            "tag": "input",
            "input_type": "text",
            "placeholder": "",
            "name": "email_address"
        }
        label = _suggest_input_label(element)
        assert label == "Email Address"
    
    def test_suggest_input_with_hyphenated_name(self):
        """Test suggesting label for input with hyphenated name."""
        element = {
            "tag": "input",
            "input_type": "text",
            "placeholder": "",
            "name": "first-name"
        }
        label = _suggest_input_label(element)
        assert label == "First Name"
    
    def test_suggest_input_email_type(self):
        """Test suggesting label for email input without placeholder."""
        element = {
            "tag": "input",
            "input_type": "email",
            "placeholder": "",
            "name": ""
        }
        label = _suggest_input_label(element)
        assert label == "Email address"
    
    def test_suggest_input_password_type(self):
        """Test suggesting label for password input."""
        element = {
            "tag": "input",
            "input_type": "password",
            "placeholder": "",
            "name": ""
        }
        label = _suggest_input_label(element)
        assert label == "Password"
    
    def test_suggest_input_number_type(self):
        """Test suggesting label for number input."""
        element = {
            "tag": "input",
            "input_type": "number",
            "placeholder": "",
            "name": ""
        }
        label = _suggest_input_label(element)
        assert label == "Number input"
    
    def test_suggest_input_checkbox_type(self):
        """Test suggesting label for checkbox input."""
        element = {
            "tag": "input",
            "input_type": "checkbox",
            "placeholder": "",
            "name": ""
        }
        label = _suggest_input_label(element)
        assert label == "Checkbox"
    
    def test_suggest_input_file_type(self):
        """Test suggesting label for file input."""
        element = {
            "tag": "input",
            "input_type": "file",
            "placeholder": "",
            "name": ""
        }
        label = _suggest_input_label(element)
        assert label == "File upload"


class TestSuggestLinkLabel:
    """Tests for _suggest_link_label function."""
    
    def test_suggest_link_with_text_content(self):
        """Test suggesting label for link with text content."""
        element = {
            "tag": "a",
            "text_content": "Click here",
            "href": "/page"
        }
        label = _suggest_link_label(element)
        assert label == "Click here"
    
    def test_suggest_link_with_title(self):
        """Test suggesting label for link with title attribute."""
        element = {
            "tag": "a",
            "text_content": "",
            "title": "Go to home page",
            "href": "/home"
        }
        label = _suggest_link_label(element)
        assert label == "Go to home page"
    
    def test_suggest_link_from_href_simple(self):
        """Test suggesting label from simple href."""
        element = {
            "tag": "a",
            "text_content": "",
            "title": "",
            "href": "/about"
        }
        label = _suggest_link_label(element)
        assert label == "About"
    
    def test_suggest_link_from_href_with_hyphens(self):
        """Test suggesting label from href with hyphens."""
        element = {
            "tag": "a",
            "text_content": "",
            "title": "",
            "href": "/contact-us"
        }
        label = _suggest_link_label(element)
        assert label == "Contact Us"
    
    def test_suggest_link_from_href_with_underscores(self):
        """Test suggesting label from href with underscores."""
        element = {
            "tag": "a",
            "text_content": "",
            "title": "",
            "href": "/privacy_policy"
        }
        label = _suggest_link_label(element)
        assert label == "Privacy Policy"
    
    def test_suggest_link_from_full_url(self):
        """Test suggesting label from full URL."""
        element = {
            "tag": "a",
            "text_content": "",
            "title": "",
            "href": "https://example.com/about-us"
        }
        label = _suggest_link_label(element)
        assert label == "About Us"
    
    def test_suggest_link_with_query_parameters(self):
        """Test suggesting label from href with query parameters."""
        element = {
            "tag": "a",
            "text_content": "",
            "title": "",
            "href": "/products?category=electronics"
        }
        label = _suggest_link_label(element)
        assert label == "Products"
    
    def test_suggest_link_with_file_extension(self):
        """Test suggesting label from href with file extension."""
        element = {
            "tag": "a",
            "text_content": "",
            "title": "",
            "href": "/downloads/guide.pdf"
        }
        label = _suggest_link_label(element)
        assert label == "Guide"
    
    def test_suggest_link_no_href(self):
        """Test suggesting label for link without href."""
        element = {
            "tag": "a",
            "text_content": "",
            "title": "",
            "href": ""
        }
        label = _suggest_link_label(element)
        assert label == "Link"


class TestSuggestAriaLabel:
    """Tests for suggest_aria_label function."""
    
    def test_suggest_aria_label_button(self):
        """Test suggesting aria-label for button."""
        element = {
            "tag": "button",
            "text_content": "Save",
            "type": "button"
        }
        label = suggest_aria_label(element)
        assert label == "Save"
    
    def test_suggest_aria_label_input(self):
        """Test suggesting aria-label for input."""
        element = {
            "tag": "input",
            "input_type": "email",
            "placeholder": "your@email.com"
        }
        label = suggest_aria_label(element)
        assert label == "your@email.com"
    
    def test_suggest_aria_label_link(self):
        """Test suggesting aria-label for link."""
        element = {
            "tag": "a",
            "text_content": "Learn more",
            "href": "/docs"
        }
        label = suggest_aria_label(element)
        assert label == "Learn more"
    
    def test_suggest_aria_label_unknown_tag(self):
        """Test suggesting aria-label for unknown tag."""
        element = {
            "tag": "div",
            "text_content": "Some content"
        }
        label = suggest_aria_label(element)
        assert label is None


class TestCheckAriaCompliance:
    """Tests for check_aria_compliance function."""
    
    def test_check_aria_compliance_button_with_label(self):
        """Test checking button that already has label."""
        elements = [
            {
                "tag": "button",
                "element_id": "btn1",
                "text_content": "Submit",
                "aria_label": "",
                "has_label": True,
                "type": "button"
            }
        ]
        issues = check_aria_compliance(elements)
        assert len(issues) == 0
    
    def test_check_aria_compliance_button_without_label(self):
        """Test checking button that lacks label."""
        elements = [
            {
                "tag": "button",
                "element_id": "btn1",
                "text_content": "",
                "aria_label": "",
                "has_label": False,
                "type": "submit"
            }
        ]
        issues = check_aria_compliance(elements)
        assert len(issues) == 1
        assert issues[0]["element_id"] == "btn1"
        assert issues[0]["element_type"] == "button"
        assert issues[0]["suggested_aria_label"] == "Submit form"
    
    def test_check_aria_compliance_input_without_label(self):
        """Test checking input that lacks label."""
        elements = [
            {
                "tag": "input",
                "element_id": "email1",
                "input_type": "email",
                "placeholder": "",
                "name": "user_email",
                "aria_label": "",
                "has_label": False
            }
        ]
        issues = check_aria_compliance(elements)
        assert len(issues) == 1
        assert issues[0]["element_id"] == "email1"
        assert issues[0]["element_type"] == "input"
        assert issues[0]["suggested_aria_label"] == "User Email"
    
    def test_check_aria_compliance_link_without_label(self):
        """Test checking link that lacks label."""
        elements = [
            {
                "tag": "a",
                "element_id": "link1",
                "text_content": "",
                "href": "/about",
                "aria_label": "",
                "has_label": False,
                "title": ""
            }
        ]
        issues = check_aria_compliance(elements)
        assert len(issues) == 1
        assert issues[0]["element_id"] == "link1"
        assert issues[0]["element_type"] == "a"
        assert issues[0]["suggested_aria_label"] == "About"
    
    def test_check_aria_compliance_multiple_elements(self):
        """Test checking multiple elements with mixed compliance."""
        elements = [
            {
                "tag": "button",
                "element_id": "btn1",
                "text_content": "Submit",
                "aria_label": "",
                "has_label": True,
                "type": "button"
            },
            {
                "tag": "button",
                "element_id": "btn2",
                "text_content": "",
                "aria_label": "",
                "has_label": False,
                "type": "button"
            },
            {
                "tag": "input",
                "element_id": "input1",
                "input_type": "text",
                "placeholder": "Name",
                "name": "",
                "aria_label": "",
                "has_label": False
            }
        ]
        issues = check_aria_compliance(elements)
        assert len(issues) == 2
        assert issues[0]["element_id"] == "btn2"
        assert issues[1]["element_id"] == "input1"
    
    def test_check_aria_compliance_empty_list(self):
        """Test checking empty element list."""
        elements = []
        issues = check_aria_compliance(elements)
        assert len(issues) == 0


class TestGetIssueDescription:
    """Tests for _get_issue_description function."""
    
    def test_get_issue_description_button(self):
        """Test getting issue description for button."""
        element = {"tag": "button"}
        description = _get_issue_description(element)
        assert description == "Button lacks text content and aria-label"
    
    def test_get_issue_description_input(self):
        """Test getting issue description for input."""
        element = {"tag": "input"}
        description = _get_issue_description(element)
        assert description == "Input lacks associated label and aria-label"
    
    def test_get_issue_description_link(self):
        """Test getting issue description for link."""
        element = {"tag": "a"}
        description = _get_issue_description(element)
        assert description == "Link lacks text content and aria-label"
    
    def test_get_issue_description_unknown(self):
        """Test getting issue description for unknown element."""
        element = {"tag": "div"}
        description = _get_issue_description(element)
        assert description == "Element lacks accessible label"
