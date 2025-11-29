"""
Unit tests for the report generator module.
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.report import (
    generate_report,
    generate_patched_html,
    export_report,
    _format_alt_text_issues,
    _format_contrast_issues,
    _format_aria_issues
)


class TestGenerateReport:
    """Tests for generate_report function."""
    
    def test_generate_report_empty_issues(self):
        """Test generating report with no issues."""
        report = generate_report(
            url="https://example.com",
            alt_text_issues=[],
            contrast_issues=[],
            aria_issues=[]
        )
        
        assert report["url"] == "https://example.com"
        assert report["summary"]["total_issues"] == 0
        assert report["summary"]["alt_text_issues"] == 0
        assert report["summary"]["contrast_issues"] == 0
        assert report["summary"]["aria_issues"] == 0
        assert "timestamp" in report
        assert "issues" in report
    
    def test_generate_report_with_alt_text_issues(self):
        """Test generating report with alt text issues."""
        alt_text_issues = [
            {
                "element_id": "img_1",
                "url": "https://example.com/image.jpg",
                "alt_text": "",
                "has_alt": False,
                "generated_alt_text": "A red apple"
            }
        ]
        
        report = generate_report(
            url="https://example.com",
            alt_text_issues=alt_text_issues,
            contrast_issues=[],
            aria_issues=[]
        )
        
        assert report["summary"]["total_issues"] == 1
        assert report["summary"]["alt_text_issues"] == 1
        assert len(report["issues"]["alt_text"]) == 1
        assert report["issues"]["alt_text"][0]["suggested_alt"] == "A red apple"
    
    def test_generate_report_with_contrast_issues(self):
        """Test generating report with contrast issues."""
        contrast_issues = [
            {
                "element_id": "p_1",
                "tag": "p",
                "text_content": "Gray text",
                "current_fg": "#cccccc",
                "current_bg": "#ffffff",
                "ratio": 3.2,
                "passes": False
            }
        ]
        
        report = generate_report(
            url="https://example.com",
            alt_text_issues=[],
            contrast_issues=contrast_issues,
            aria_issues=[]
        )
        
        assert report["summary"]["total_issues"] == 1
        assert report["summary"]["contrast_issues"] == 1
        assert len(report["issues"]["contrast"]) == 1
        assert report["issues"]["contrast"][0]["ratio"] == 3.2
    
    def test_generate_report_with_aria_issues(self):
        """Test generating report with ARIA issues."""
        aria_issues = [
            {
                "element_id": "button_1",
                "element_type": "button",
                "issue": "No text or aria-label",
                "suggested_aria_label": "Submit form",
                "current_aria_label": "",
                "current_text": ""
            }
        ]
        
        report = generate_report(
            url="https://example.com",
            alt_text_issues=[],
            contrast_issues=[],
            aria_issues=aria_issues
        )
        
        assert report["summary"]["total_issues"] == 1
        assert report["summary"]["aria_issues"] == 1
        assert len(report["issues"]["aria"]) == 1
        assert report["issues"]["aria"][0]["suggested_aria_label"] == "Submit form"
    
    def test_generate_report_mixed_issues(self):
        """Test generating report with mixed issues."""
        alt_text_issues = [
            {
                "element_id": "img_1",
                "url": "https://example.com/image.jpg",
                "alt_text": "",
                "has_alt": False,
                "generated_alt_text": "A red apple"
            }
        ]
        contrast_issues = [
            {
                "element_id": "p_1",
                "tag": "p",
                "text_content": "Gray text",
                "current_fg": "#cccccc",
                "current_bg": "#ffffff",
                "ratio": 3.2,
                "passes": False
            }
        ]
        aria_issues = [
            {
                "element_id": "button_1",
                "element_type": "button",
                "issue": "No text or aria-label",
                "suggested_aria_label": "Submit form",
                "current_aria_label": "",
                "current_text": ""
            }
        ]
        
        report = generate_report(
            url="https://example.com",
            alt_text_issues=alt_text_issues,
            contrast_issues=contrast_issues,
            aria_issues=aria_issues
        )
        
        assert report["summary"]["total_issues"] == 3
        assert report["summary"]["alt_text_issues"] == 1
        assert report["summary"]["contrast_issues"] == 1
        assert report["summary"]["aria_issues"] == 1


class TestFormatAltTextIssues:
    """Tests for _format_alt_text_issues function."""
    
    def test_format_alt_text_issues_with_suggestions(self):
        """Test formatting alt text issues with suggestions."""
        issues = [
            {
                "element_id": "img_1",
                "url": "https://example.com/image.jpg",
                "alt_text": "",
                "has_alt": False,
                "generated_alt_text": "A red apple"
            }
        ]
        
        formatted = _format_alt_text_issues(issues)
        
        assert len(formatted) == 1
        assert formatted[0]["element_id"] == "img_1"
        assert formatted[0]["suggested_alt"] == "A red apple"
        assert formatted[0]["current_alt"] == ""
    
    def test_format_alt_text_issues_skip_with_alt(self):
        """Test that images with alt text are skipped."""
        issues = [
            {
                "element_id": "img_1",
                "url": "https://example.com/image.jpg",
                "alt_text": "Existing alt text",
                "has_alt": True,
                "generated_alt_text": None
            }
        ]
        
        formatted = _format_alt_text_issues(issues)
        
        assert len(formatted) == 0


class TestFormatContrastIssues:
    """Tests for _format_contrast_issues function."""
    
    def test_format_contrast_issues(self):
        """Test formatting contrast issues."""
        issues = [
            {
                "element_id": "p_1",
                "tag": "p",
                "text_content": "Gray text",
                "current_fg": "#cccccc",
                "current_bg": "#ffffff",
                "ratio": 3.2,
                "passes": False
            }
        ]
        
        formatted = _format_contrast_issues(issues)
        
        assert len(formatted) == 1
        assert formatted[0]["element_id"] == "p_1"
        assert formatted[0]["ratio"] == 3.2
        assert formatted[0]["required_ratio"] == 4.5
        assert "suggested_fg" in formatted[0]
        assert "suggested_ratio" in formatted[0]


class TestFormatAriaIssues:
    """Tests for _format_aria_issues function."""
    
    def test_format_aria_issues(self):
        """Test formatting ARIA issues."""
        issues = [
            {
                "element_id": "button_1",
                "element_type": "button",
                "issue": "No text or aria-label",
                "suggested_aria_label": "Submit form",
                "current_aria_label": "",
                "current_text": ""
            }
        ]
        
        formatted = _format_aria_issues(issues)
        
        assert len(formatted) == 1
        assert formatted[0]["element_id"] == "button_1"
        assert formatted[0]["element_type"] == "button"
        assert formatted[0]["suggested_aria_label"] == "Submit form"


class TestGeneratePatchedHtml:
    """Tests for generate_patched_html function."""
    
    def test_generate_patched_html_with_alt_text(self):
        """Test generating patched HTML with alt text fixes."""
        original_html = '<html><body><img id="img_1" src="test.jpg" alt=""></body></html>'
        alt_text_issues = [
            {
                "element_id": "img_1",
                "suggested_alt": "A red apple"
            }
        ]
        
        patched = generate_patched_html(
            original_html,
            alt_text_issues=alt_text_issues,
            contrast_issues=[],
            aria_issues=[]
        )
        
        assert "A red apple" in patched
        assert 'alt="A red apple"' in patched
    
    def test_generate_patched_html_with_aria(self):
        """Test generating patched HTML with ARIA fixes."""
        original_html = '<html><body><button id="button_1"></button></body></html>'
        aria_issues = [
            {
                "element_id": "button_1",
                "suggested_aria_label": "Submit form"
            }
        ]
        
        patched = generate_patched_html(
            original_html,
            alt_text_issues=[],
            contrast_issues=[],
            aria_issues=aria_issues
        )
        
        assert 'aria-label="Submit form"' in patched
    
    def test_generate_patched_html_invalid_html(self):
        """Test that invalid HTML is handled gracefully."""
        original_html = "not valid html"
        
        patched = generate_patched_html(
            original_html,
            alt_text_issues=[],
            contrast_issues=[],
            aria_issues=[]
        )
        
        # Should return original or parsed version
        assert patched is not None


class TestExportReport:
    """Tests for export_report function."""
    
    def test_export_report_json(self):
        """Test exporting report as JSON."""
        report = {
            "url": "https://example.com",
            "timestamp": "2025-11-29T10:00:00Z",
            "summary": {"total_issues": 0},
            "issues": {}
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test_report.json")
            result_path = export_report(report, format="json", output_path=output_path)
            
            assert Path(result_path).exists()
            
            # Verify JSON content
            with open(result_path, "r") as f:
                loaded = json.load(f)
                assert loaded["url"] == "https://example.com"
    
    def test_export_report_html(self):
        """Test exporting report as HTML."""
        report = {
            "url": "https://example.com",
            "timestamp": "2025-11-29T10:00:00Z",
            "summary": {
                "total_issues": 0,
                "alt_text_issues": 0,
                "contrast_issues": 0,
                "aria_issues": 0
            },
            "issues": {
                "alt_text": [],
                "contrast": [],
                "aria": []
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test_report.html")
            result_path = export_report(report, format="html", output_path=output_path)
            
            assert Path(result_path).exists()
            
            # Verify HTML content
            with open(result_path, "r") as f:
                content = f.read()
                assert "AccessiAI" in content
                assert "https://example.com" in content
    
    def test_export_report_invalid_format(self):
        """Test that invalid format raises ValueError."""
        report = {"url": "https://example.com"}
        
        with pytest.raises(ValueError):
            export_report(report, format="invalid")
    
    def test_export_report_creates_directory(self):
        """Test that export creates necessary directories."""
        report = {
            "url": "https://example.com",
            "timestamp": "2025-11-29T10:00:00Z",
            "summary": {},
            "issues": {}
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "nested" / "dir" / "report.json")
            result_path = export_report(report, format="json", output_path=output_path)
            
            assert Path(result_path).exists()
            assert Path(result_path).parent.exists()
