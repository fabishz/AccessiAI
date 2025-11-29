# Design Document: AccessiAI

## Overview

AccessiAI is a full-stack web accessibility analysis tool consisting of a Python backend that performs accessibility analysis and a Streamlit frontend that provides user interaction. The system processes webpages to identify accessibility issues and generate actionable recommendations following WCAG standards.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  (URL Input → Analysis Trigger → Results Display)           │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              AccessiAI Analysis Engine                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ Webpage Parser   │  │ Image Analyzer   │                 │
│  │ (BeautifulSoup)  │  │ (BLIP Model)     │                 │
│  └──────────────────┘  └──────────────────┘                 │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ Contrast Checker │  │ ARIA Suggester   │                 │
│  │ (WCAG Formula)   │  │ (Rule-based)     │                 │
│  └──────────────────┘  └──────────────────┘                 │
│  ┌──────────────────────────────────────┐                   │
│  │ Report Generator (JSON)              │                   │
│  └──────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Webpage Parser Module
**Purpose**: Extract accessibility-relevant elements from HTML

**Functions**:
- `fetch_webpage(url: str) -> str`: Downloads HTML content with timeout and error handling
- `parse_images(soup: BeautifulSoup) -> List[Dict]`: Extracts image elements, limiting to 10 images
- `parse_interactive_elements(soup: BeautifulSoup) -> List[Dict]`: Extracts buttons, inputs, links
- `extract_colors(soup: BeautifulSoup) -> List[Dict]`: Extracts text and background colors from elements

**Error Handling**: 
- Invalid URLs caught and reported
- Network timeouts (5 seconds) prevent hanging
- Malformed HTML handled gracefully by BeautifulSoup

### 2. Image Analysis Module
**Purpose**: Generate alt text for images lacking descriptions

**Functions**:
- `download_image(url: str) -> PIL.Image`: Downloads image with error handling
- `generate_alt_text(image: PIL.Image) -> str`: Uses BLIP model to generate caption
- `process_images(images: List[Dict]) -> List[Dict]`: Batch processes images, skipping failures

**Model Details**:
- Model: `Salesforce/blip-image-captioning-base`
- Input: PIL Image
- Output: Concise caption (< 125 characters)
- Device: CPU (with GPU fallback if available)

### 3. Contrast Checker Module
**Purpose**: Validate color contrast ratios per WCAG standards

**Functions**:
- `hex_to_rgb(hex_color: str) -> Tuple[int, int, int]`: Converts hex to RGB
- `calculate_luminance(rgb: Tuple) -> float`: Calculates relative luminance per WCAG formula
- `calculate_contrast_ratio(fg_rgb: Tuple, bg_rgb: Tuple) -> float`: Computes contrast ratio
- `check_contrast(elements: List[Dict]) -> List[Dict]`: Validates all text elements, flags failures
- `suggest_color_fix(current_color: str, bg_color: str) -> str`: Recommends corrected color

**WCAG Formula**:
- Relative Luminance: L = 0.2126 * R + 0.7152 * G + 0.0722 * B (where R, G, B are normalized)
- Contrast Ratio: (L1 + 0.05) / (L2 + 0.05) where L1 is lighter, L2 is darker
- Threshold: 4.5:1 for normal text

### 4. ARIA Suggester Module
**Purpose**: Recommend ARIA labels for interactive elements

**Functions**:
- `suggest_aria_label(element: Dict) -> str`: Generates appropriate aria-label based on element type
- `check_aria_compliance(elements: List[Dict]) -> List[Dict]`: Identifies missing labels and suggests fixes

**Rules**:
- Buttons without text: suggest `aria-label="[Action description]"`
- Inputs without labels: suggest `aria-label="[Field name]"` or recommend `<label>` element
- Links without text: suggest `aria-label="[Link destination]"`

### 5. Report Generator Module
**Purpose**: Compile findings into structured JSON report

**Functions**:
- `generate_report(alt_text_issues: List, contrast_issues: List, aria_issues: List) -> Dict`: Compiles all findings
- `generate_patched_html(original_html: str, fixes: List) -> str`: Creates HTML with suggested fixes applied
- `export_report(report: Dict, format: str) -> str`: Exports report as JSON or HTML

**Report Structure**:
```json
{
  "url": "https://example.com",
  "timestamp": "2025-11-29T10:00:00Z",
  "summary": {
    "total_issues": 5,
    "alt_text_issues": 2,
    "contrast_issues": 2,
    "aria_issues": 1
  },
  "issues": {
    "alt_text": [
      {
        "element_id": "img_1",
        "current_alt": "",
        "suggested_alt": "A red apple on a wooden table",
        "image_url": "https://..."
      }
    ],
    "contrast": [
      {
        "element_id": "p_1",
        "current_fg": "#666666",
        "current_bg": "#f0f0f0",
        "ratio": 3.2,
        "required_ratio": 4.5,
        "suggested_fg": "#000000",
        "suggested_ratio": 7.2
      }
    ],
    "aria": [
      {
        "element_id": "button_1",
        "element_type": "button",
        "issue": "No text or aria-label",
        "suggested_aria_label": "Submit form"
      }
    ]
  }
}
```

### 6. Streamlit Frontend Module
**Purpose**: Provide user interface for analysis

**Components**:
- Title and description
- URL input field with validation
- "Analyze Page" button
- Loading spinner during processing
- Results display with expandable sections
- Error message display
- Export button (optional)

**User Flow**:
1. User enters URL
2. Clicks "Analyze Page"
3. Loading spinner appears
4. Results displayed in organized sections
5. User can expand each section to view details
6. Option to export fixed HTML

## Data Models

### Image Element
```python
{
  "url": str,
  "alt_text": str,
  "has_alt": bool,
  "generated_alt": str (optional)
}
```

### Text Element
```python
{
  "element_id": str,
  "tag": str,
  "text_content": str,
  "fg_color": str,
  "bg_color": str,
  "contrast_ratio": float
}
```

### Interactive Element
```python
{
  "element_id": str,
  "tag": str,
  "text_content": str,
  "aria_label": str,
  "has_label": bool,
  "suggested_aria_label": str (optional)
}
```

## Error Handling

1. **Network Errors**: Catch and report with user-friendly message
2. **Invalid URLs**: Validate format before processing
3. **Image Processing Failures**: Log and skip individual images
4. **Model Loading Failures**: Graceful degradation with informative message
5. **Timeout Protection**: 5-second timeout on webpage fetches
6. **Memory Management**: Limit to 10 images to prevent memory issues

## Testing Strategy

### Unit Tests
- Test color contrast calculation against known WCAG values
- Test hex-to-RGB conversion
- Test ARIA suggestion logic with various element types
- Test HTML parsing with malformed input

### Integration Tests
- Test full pipeline with public URLs (example.com, wikipedia.org)
- Test error handling with invalid URLs
- Test report generation with various issue combinations

### Manual Testing
- Test Streamlit UI with valid and invalid inputs
- Test loading spinner and error messages
- Test export functionality
- Verify performance with large webpages

### Sample Test URLs
- https://example.com (simple, stable)
- https://www.wikipedia.org (complex, many images)
- https://invalid-url-12345.com (error handling)

## Implementation Phases

**Phase 1 (15 min)**: Project setup, dependencies, basic structure
**Phase 2 (20 min)**: Core analysis modules (parser, contrast, ARIA)
**Phase 3 (15 min)**: Image analysis with BLIP model
**Phase 4 (10 min)**: Streamlit UI and report display
**Phase 5 (5 min)**: Testing, documentation, deployment readiness

