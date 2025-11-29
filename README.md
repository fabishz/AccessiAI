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

## Troubleshooting

### Model Download Issues
The first run may take longer as it downloads the BLIP model (~350MB). Subsequent runs will use the cached model.

### Memory Issues
If you encounter memory errors, try analyzing simpler pages or reducing the number of images analyzed.

### Network Timeouts
If a webpage is slow to load, the analysis may timeout. Try with a different URL.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

[Add your license here]

## Support

For issues or questions, please open an issue on the repository.
