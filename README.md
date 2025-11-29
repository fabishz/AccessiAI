# AccessiAI: AI-Powered Web Accessibility Enhancer

## Overview

AccessiAI is an intelligent web accessibility analysis tool that automatically identifies and suggests fixes for common accessibility issues on webpages. Using AI models and WCAG standards, it helps developers and content creators make their websites more inclusive for people with disabilities.

## Features

- **Alt Text Generation**: Automatically generates descriptive alt text for images using AI
- **Color Contrast Checking**: Validates text contrast ratios against WCAG standards
- **ARIA Label Suggestions**: Recommends ARIA labels for interactive elements
- **Comprehensive Reporting**: Generates detailed reports with actionable fixes
- **HTML Export**: Download patched HTML with suggested improvements

## Social Impact

AccessiAI democratizes web accessibility by making it easier for developers to identify and fix accessibility barriers. By reducing the effort required to achieve WCAG compliance, we enable more websites to be accessible to the 1.3 billion people worldwide with disabilities, including those with visual impairments, hearing loss, and motor disabilities.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd accessiai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501` and enter a webpage URL to analyze.

## Project Structure

```
accessiai/
├── src/                    # Core analysis modules
│   ├── parser.py          # Webpage parsing
│   ├── contrast.py        # Color contrast checking
│   ├── aria.py            # ARIA suggestions
│   ├── image_analyzer.py  # Image alt text generation
│   ├── report.py          # Report generation
│   └── analyzer.py        # Main orchestrator
├── tests/                 # Unit and integration tests
├── assets/                # Static assets
├── app.py                 # Streamlit frontend
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## How It Works

1. **Input**: User provides a webpage URL
2. **Analysis**: AccessiAI parses the HTML and analyzes:
   - Images without alt text
   - Text with insufficient color contrast
   - Interactive elements missing ARIA labels
3. **AI Processing**: Uses BLIP model to generate alt text descriptions
4. **Report**: Generates a comprehensive report with suggested fixes
5. **Export**: User can download fixed HTML or view detailed recommendations

## WCAG Compliance

AccessiAI checks compliance with WCAG 2.1 Level AA standards, including:
- Text color contrast ratio of at least 4.5:1
- Descriptive alt text for all images
- Proper ARIA labels for interactive elements

## Sample Output

### Report Structure

AccessiAI generates a comprehensive JSON report with the following structure:

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
        "image_url": "https://example.com/apple.jpg"
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

### UI Display

The Streamlit interface displays results in expandable sections:

- **Alt Text Issues**: Shows images missing descriptions with AI-generated suggestions
- **Contrast Issues**: Lists text elements with insufficient contrast and recommended color fixes
- **ARIA Issues**: Highlights interactive elements needing ARIA labels with suggestions
- **Export**: Download button to save fixed HTML with all recommendations applied

## Troubleshooting

### Model Download Issues
**Problem**: First run takes a long time or shows download progress.

**Solution**: The BLIP image captioning model (~350MB) downloads on first use. This is normal and only happens once. Subsequent runs use the cached model. Ensure you have stable internet and sufficient disk space.

### Memory Issues
**Problem**: Application crashes with "Out of memory" error.

**Solution**: 
- Try analyzing simpler pages with fewer images
- Close other applications to free up RAM
- The system limits analysis to 10 images per page to manage memory usage
- If issues persist, consider running on a machine with more RAM

### Network Timeouts
**Problem**: Analysis fails with "Connection timeout" error.

**Solution**:
- Check your internet connection
- Try with a different URL (some servers are slow to respond)
- The system has a 5-second timeout per request; very slow servers may exceed this
- Ensure the URL is publicly accessible and not behind authentication

### Invalid URL Errors
**Problem**: "Invalid URL format" or "Page not accessible" error.

**Solution**:
- Verify the URL is complete (include `https://` or `http://`)
- Check that the website is publicly accessible
- Some websites may block automated access; try a different site
- Ensure the URL doesn't require authentication

### Image Processing Failures
**Problem**: Some images show "Failed to process" in the report.

**Solution**:
- This is normal for images that cannot be downloaded or are in unsupported formats
- The analysis continues with other images
- Check that image URLs are publicly accessible
- Supported formats: JPEG, PNG, GIF, WebP

### Streamlit Connection Issues
**Problem**: Cannot access the application at `http://localhost:8501`.

**Solution**:
- Ensure Streamlit is running (check terminal for "You can now view your Streamlit app")
- Try refreshing the browser
- Check if port 8501 is already in use; Streamlit will use the next available port
- Look at the terminal output for the correct URL

### Color Contrast Calculation Issues
**Problem**: Suggested colors don't seem right or contrast ratio seems incorrect.

**Solution**:
- The system uses WCAG 2.1 relative luminance formula
- Ensure colors are properly extracted from CSS (inline styles and classes are supported)
- Some dynamically-applied colors may not be detected
- Test with simple HTML pages first to verify functionality

### Export/Download Not Working
**Problem**: Export button doesn't download the file.

**Solution**:
- Check browser download settings
- Ensure you have write permissions in your downloads folder
- Try a different browser
- Check browser console for errors (F12 → Console tab)

## Performance Tips

- **Faster Analysis**: Analyze pages with fewer images (system limits to 10)
- **Better Results**: Use well-structured HTML with semantic elements
- **Accurate Colors**: Ensure colors are defined in inline styles or simple CSS classes
- **Reliable Results**: Test with stable, publicly-accessible websites

## Requirements

See `requirements.txt` for all dependencies:
- **streamlit**: Web UI framework
- **beautifulsoup4**: HTML parsing
- **transformers**: BLIP model for image captioning
- **torch**: Deep learning framework
- **pillow**: Image processing
- **webcolors**: Color conversion utilities
- **requests**: HTTP requests

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

[Add your license here]

## Support

For issues or questions, please open an issue on the repository.
