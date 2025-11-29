"""
Unit tests for the contrast checker module.
"""

import pytest
from src.contrast import (
    hex_to_rgb,
    calculate_luminance,
    calculate_contrast_ratio,
    check_contrast,
    suggest_color_fix,
    _parse_color,
    _normalize_rgb
)


class TestHexToRgb:
    """Tests for hex_to_rgb function."""
    
    def test_hex_to_rgb_with_hash(self):
        """Test converting hex color with # prefix."""
        rgb = hex_to_rgb("#ff0000")
        assert rgb == (255, 0, 0)
    
    def test_hex_to_rgb_without_hash(self):
        """Test converting hex color without # prefix."""
        rgb = hex_to_rgb("00ff00")
        assert rgb == (0, 255, 0)
    
    def test_hex_to_rgb_black(self):
        """Test converting black color."""
        rgb = hex_to_rgb("#000000")
        assert rgb == (0, 0, 0)
    
    def test_hex_to_rgb_white(self):
        """Test converting white color."""
        rgb = hex_to_rgb("#ffffff")
        assert rgb == (255, 255, 255)
    
    def test_hex_to_rgb_invalid_format(self):
        """Test that invalid hex format raises ValueError."""
        with pytest.raises(ValueError):
            hex_to_rgb("#gggggg")
    
    def test_hex_to_rgb_invalid_length(self):
        """Test that invalid hex length raises ValueError."""
        with pytest.raises(ValueError):
            hex_to_rgb("#fff")


class TestNormalizeRgb:
    """Tests for _normalize_rgb helper function."""
    
    def test_normalize_rgb_black(self):
        """Test normalizing black (0)."""
        normalized = _normalize_rgb(0)
        assert normalized == 0.0
    
    def test_normalize_rgb_white(self):
        """Test normalizing white (255)."""
        normalized = _normalize_rgb(255)
        assert normalized > 0.99  # Should be close to 1.0
    
    def test_normalize_rgb_mid_range(self):
        """Test normalizing mid-range value."""
        normalized = _normalize_rgb(128)
        assert 0 < normalized < 1


class TestCalculateLuminance:
    """Tests for calculate_luminance function."""
    
    def test_luminance_black(self):
        """Test luminance of black color."""
        luminance = calculate_luminance((0, 0, 0))
        assert luminance == 0.0
    
    def test_luminance_white(self):
        """Test luminance of white color."""
        luminance = calculate_luminance((255, 255, 255))
        assert luminance > 0.99
    
    def test_luminance_red(self):
        """Test luminance of red color."""
        luminance = calculate_luminance((255, 0, 0))
        assert 0 < luminance < 1
    
    def test_luminance_green(self):
        """Test luminance of green color."""
        luminance = calculate_luminance((0, 255, 0))
        assert 0 < luminance < 1
    
    def test_luminance_blue(self):
        """Test luminance of blue color."""
        luminance = calculate_luminance((0, 0, 255))
        assert 0 < luminance < 1


class TestCalculateContrastRatio:
    """Tests for calculate_contrast_ratio function."""
    
    def test_contrast_black_on_white(self):
        """Test contrast ratio of black text on white background."""
        ratio = calculate_contrast_ratio("#000000", "#ffffff")
        assert ratio == 21.0  # Maximum contrast
    
    def test_contrast_white_on_black(self):
        """Test contrast ratio of white text on black background."""
        ratio = calculate_contrast_ratio("#ffffff", "#000000")
        assert ratio == 21.0  # Maximum contrast
    
    def test_contrast_same_color(self):
        """Test contrast ratio of same foreground and background."""
        ratio = calculate_contrast_ratio("#808080", "#808080")
        assert ratio == 1.0  # Minimum contrast
    
    def test_contrast_gray_on_white(self):
        """Test contrast ratio of gray text on white background."""
        ratio = calculate_contrast_ratio("#666666", "#ffffff")
        assert 5.0 < ratio < 6.0  # Should be in reasonable range
    
    def test_contrast_invalid_color_format(self):
        """Test that invalid color format raises ValueError."""
        with pytest.raises(ValueError):
            calculate_contrast_ratio("#gggggg", "#ffffff")
    
    def test_contrast_ratio_symmetry(self):
        """Test that contrast ratio is same regardless of fg/bg order."""
        ratio1 = calculate_contrast_ratio("#000000", "#ffffff")
        ratio2 = calculate_contrast_ratio("#ffffff", "#000000")
        assert ratio1 == ratio2


class TestParseColor:
    """Tests for _parse_color helper function."""
    
    def test_parse_hex_color(self):
        """Test parsing hex color."""
        color = _parse_color("#ff0000")
        assert color == "#ff0000"
    
    def test_parse_hex_color_without_hash(self):
        """Test parsing hex color without hash."""
        color = _parse_color("00ff00")
        assert color is None  # Should fail without hash
    
    def test_parse_rgb_color(self):
        """Test parsing RGB color."""
        color = _parse_color("rgb(255, 0, 0)")
        assert color == "#ff0000"
    
    def test_parse_rgb_color_with_spaces(self):
        """Test parsing RGB color with extra spaces."""
        color = _parse_color("rgb( 0 , 255 , 0 )")
        assert color == "#00ff00"
    
    def test_parse_invalid_color(self):
        """Test parsing invalid color."""
        color = _parse_color("invalid")
        assert color is None
    
    def test_parse_empty_color(self):
        """Test parsing empty color."""
        color = _parse_color("")
        assert color is None


class TestCheckContrast:
    """Tests for check_contrast function."""
    
    def test_check_contrast_passing(self):
        """Test checking contrast for passing elements."""
        elements = [
            {
                "element_id": "p1",
                "tag": "p",
                "text_content": "Black text",
                "fg_color": "#000000",
                "bg_color": "#ffffff"
            }
        ]
        issues = check_contrast(elements)
        assert len(issues) == 0  # Should pass
    
    def test_check_contrast_failing(self):
        """Test checking contrast for failing elements."""
        elements = [
            {
                "element_id": "p1",
                "tag": "p",
                "text_content": "Gray text",
                "fg_color": "#cccccc",
                "bg_color": "#ffffff"
            }
        ]
        issues = check_contrast(elements)
        assert len(issues) == 1
        assert issues[0]["element_id"] == "p1"
        assert issues[0]["passes"] is False
        assert issues[0]["ratio"] < 4.5
    
    def test_check_contrast_missing_colors(self):
        """Test checking contrast with missing colors."""
        elements = [
            {
                "element_id": "p1",
                "tag": "p",
                "text_content": "Text",
                "fg_color": None,
                "bg_color": "#ffffff"
            }
        ]
        issues = check_contrast(elements)
        assert len(issues) == 0  # Should skip
    
    def test_check_contrast_multiple_elements(self):
        """Test checking contrast for multiple elements."""
        elements = [
            {
                "element_id": "p1",
                "tag": "p",
                "text_content": "Black text",
                "fg_color": "#000000",
                "bg_color": "#ffffff"
            },
            {
                "element_id": "p2",
                "tag": "p",
                "text_content": "Gray text",
                "fg_color": "#cccccc",
                "bg_color": "#ffffff"
            }
        ]
        issues = check_contrast(elements)
        assert len(issues) == 1  # Only one should fail
        assert issues[0]["element_id"] == "p2"
    
    def test_check_contrast_with_rgb_colors(self):
        """Test checking contrast with RGB color format."""
        elements = [
            {
                "element_id": "p1",
                "tag": "p",
                "text_content": "Text",
                "fg_color": "rgb(0, 0, 0)",
                "bg_color": "rgb(255, 255, 255)"
            }
        ]
        issues = check_contrast(elements)
        assert len(issues) == 0  # Should pass


class TestSuggestColorFix:
    """Tests for suggest_color_fix function."""
    
    def test_suggest_color_fix_light_background(self):
        """Test suggesting color for light background."""
        suggested = suggest_color_fix("#cccccc", "#ffffff")
        assert suggested == "#000000"  # Should suggest black
    
    def test_suggest_color_fix_dark_background(self):
        """Test suggesting color for dark background."""
        suggested = suggest_color_fix("#333333", "#000000")
        assert suggested == "#ffffff"  # Should suggest white
    
    def test_suggest_color_fix_achieves_ratio(self):
        """Test that suggested color achieves target ratio."""
        suggested = suggest_color_fix("#cccccc", "#ffffff")
        ratio = calculate_contrast_ratio(suggested, "#ffffff")
        assert ratio >= 4.5
    
    def test_suggest_color_fix_invalid_background(self):
        """Test that invalid background color raises ValueError."""
        with pytest.raises(ValueError):
            suggest_color_fix("#000000", "#gggggg")
