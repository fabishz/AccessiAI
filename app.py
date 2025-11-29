"""
Streamlit frontend application for AccessiAI.
Provides a user-friendly interface for analyzing webpage accessibility.
"""

import streamlit as st
import logging
from urllib.parse import urlparse
from src.analyzer import analyze_webpage_safe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AccessiAI",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-title {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 10px;
    }
    .subtitle {
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 30px;
        font-size: 16px;
    }
    .issue-card {
        border-left: 4px solid #e74c3c;
        padding: 15px;
        margin: 10px 0;
        background-color: #f8f9fa;
        border-radius: 4px;
    }
    .issue-card.alt-text {
        border-left-color: #f39c12;
    }
    .issue-card.contrast {
        border-left-color: #e74c3c;
    }
    .issue-card.aria {
        border-left-color: #9b59b6;
    }
    .success-message {
        color: #27ae60;
        font-weight: bold;
    }
    .error-message {
        color: #e74c3c;
        font-weight: bold;
    }
    .summary-metric {
        text-align: center;
        padding: 20px;
        background-color: #ecf0f1;
        border-radius: 8px;
        margin: 10px 0;
    }
    .summary-metric .number {
        font-size: 32px;
        font-weight: bold;
        color: #2c3e50;
    }
    .summary-metric .label {
        color: #7f8c8d;
        font-size: 14px;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
    
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        if not url or not isinstance(url, str):
            logger.warning("Invalid URL: empty or not a string")
            return False
        
        result = urlparse(url)
        is_valid = all([result.scheme, result.netloc])
        
        if not is_valid:
            logger.warning(f"Invalid URL format: {url}")
        
        return is_valid
    except Exception as e:
        logger.error(f"Error validating URL: {e}")
        return False


def format_color_value(color: str) -> str:
    """
    Format color value for display.
    
    Args:
        color: Color value (hex or rgb)
    
    Returns:
        Formatted color string
    """
    if not color:
        return "Unknown"
    return color.upper() if color.startswith("#") else color


def display_summary(report: dict) -> None:
    """
    Display summary statistics from the report.
    
    Args:
        report: Report dictionary from analyzer
    """
    summary = report.get("summary", {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="summary-metric">
                <div class="number">{summary.get('total_issues', 0)}</div>
                <div class="label">Total Issues</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="summary-metric">
                <div class="number">{summary.get('alt_text_issues', 0)}</div>
                <div class="label">Alt Text Issues</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="summary-metric">
                <div class="number">{summary.get('contrast_issues', 0)}</div>
                <div class="label">Contrast Issues</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="summary-metric">
                <div class="number">{summary.get('aria_issues', 0)}</div>
                <div class="label">ARIA Issues</div>
            </div>
        """, unsafe_allow_html=True)


def display_alt_text_issues(issues: list) -> None:
    """
    Display alt text issues in expandable sections.
    
    Args:
        issues: List of alt text issues from report
    """
    if not issues:
        st.success("✓ No alt text issues found!")
        return
    
    for idx, issue in enumerate(issues, 1):
        with st.expander(f"Image {idx}: {issue.get('element_id', 'Unknown')}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Current Alt Text:**")
                current_alt = issue.get('current_alt', '')
                st.code(current_alt if current_alt else "(empty)", language="text")
            
            with col2:
                st.write("**Suggested Alt Text:**")
                st.code(issue.get('suggested_alt', ''), language="text")
            
            st.write("**Image URL:**")
            st.write(issue.get('image_url', 'Unknown'))


def display_contrast_issues(issues: list) -> None:
    """
    Display color contrast issues in expandable sections.
    
    Args:
        issues: List of contrast issues from report
    """
    if not issues:
        st.success("✓ No color contrast issues found!")
        return
    
    for idx, issue in enumerate(issues, 1):
        element_id = issue.get('element_id', 'Unknown')
        tag = issue.get('tag', '')
        ratio = issue.get('ratio', 0)
        required = issue.get('required_ratio', 4.5)
        
        with st.expander(
            f"Element {idx}: {tag} ({element_id}) - Ratio: {ratio}:1 (Required: {required}:1)",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Current Colors:**")
                st.write(f"Text: {format_color_value(issue.get('current_fg', ''))}")
                st.write(f"Background: {format_color_value(issue.get('current_bg', ''))}")
                st.write(f"Contrast Ratio: **{ratio}:1**")
            
            with col2:
                st.write("**Suggested Fix:**")
                st.write(f"Text: {format_color_value(issue.get('suggested_fg', ''))}")
                st.write(f"Background: {format_color_value(issue.get('current_bg', ''))}")
                st.write(f"New Ratio: **{issue.get('suggested_ratio', 0)}:1**")
            
            st.write("**Text Content:**")
            st.write(issue.get('text_content', ''))


def display_aria_issues(issues: list) -> None:
    """
    Display ARIA label issues in expandable sections.
    
    Args:
        issues: List of ARIA issues from report
    """
    if not issues:
        st.success("✓ No ARIA label issues found!")
        return
    
    for idx, issue in enumerate(issues, 1):
        element_type = issue.get('element_type', 'element').title()
        element_id = issue.get('element_id', 'Unknown')
        
        with st.expander(f"{element_type} {idx}: {element_id}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Issue:**")
                st.write(issue.get('issue', ''))
                st.write("**Current Text:**")
                current_text = issue.get('current_text', '')
                st.code(current_text if current_text else "(empty)", language="text")
            
            with col2:
                st.write("**Suggested aria-label:**")
                st.code(issue.get('suggested_aria_label', ''), language="text")


def display_results(result: dict) -> None:
    """
    Display analysis results with expandable sections.
    
    Args:
        result: Result dictionary from analyzer
    """
    try:
        if not result.get("success"):
            st.error("❌ Analysis Failed")
            errors = result.get("errors", [])
            if errors:
                for error in errors:
                    st.error(f"• {error}")
            else:
                st.error("Unknown error occurred during analysis")
            return
        
        report = result.get("report", {})
        if not report:
            st.error("❌ No report data available")
            return
    
        # Display summary
        st.subheader("📊 Summary")
        display_summary(report)
        
        # Display issues by category
        issues = report.get("issues", {})
        
        st.subheader("🖼️ Alt Text Issues")
        display_alt_text_issues(issues.get("alt_text", []))
        
        st.subheader("🎨 Color Contrast Issues")
        display_contrast_issues(issues.get("contrast", []))
        
        st.subheader("♿ ARIA Label Issues")
        display_aria_issues(issues.get("aria", []))
        
        # Export options
        st.subheader("📥 Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Download JSON Report", key="export_json"):
                try:
                    import json
                    json_str = json.dumps(report, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name="accessibility_report.json",
                        mime="application/json"
                    )
                except Exception as e:
                    logger.error(f"Error preparing JSON export: {e}")
                    st.error("Error preparing JSON export")
        
        with col2:
            if st.button("🔧 Download Patched HTML", key="export_html"):
                try:
                    patched_html = result.get("patched_html")
                    if patched_html:
                        st.download_button(
                            label="Download HTML",
                            data=patched_html,
                            file_name="patched_webpage.html",
                            mime="text/html"
                        )
                    else:
                        st.warning("Patched HTML not available")
                except Exception as e:
                    logger.error(f"Error preparing HTML export: {e}")
                    st.error("Error preparing HTML export")
    
    except Exception as e:
        logger.error(f"Error displaying results: {e}")
        st.error(f"Error displaying results: {e}")


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown(
        '<h1 class="main-title">♿ AccessiAI: AI-Powered Web Accessibility Enhancer</h1>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="subtitle">Analyze webpages and get AI-powered suggestions to improve accessibility</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar information
    with st.sidebar:
        st.header("About AccessiAI")
        st.write("""
        AccessiAI helps you identify and fix accessibility issues on your webpages:
        
        - **Alt Text**: Generates descriptions for images using AI
        - **Color Contrast**: Checks text readability against WCAG standards
        - **ARIA Labels**: Suggests labels for interactive elements
        
        All analysis is performed locally and no data is stored.
        """)
        
        st.header("How to Use")
        st.write("""
        1. Enter a webpage URL
        2. Click "Analyze Page"
        3. Review the findings
        4. Download the report or patched HTML
        """)
    
    # Input section
    st.header("🔍 Analyze a Webpage")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        url_input = st.text_input(
            "Enter webpage URL:",
            placeholder="https://example.com",
            label_visibility="collapsed"
        )
    
    with col2:
        analyze_button = st.button("Analyze Page", type="primary", use_container_width=True)
    
    # Analysis logic
    if analyze_button:
        try:
            if not url_input:
                st.error("❌ Please enter a URL")
                logger.warning("Analysis attempted with empty URL")
            elif not is_valid_url(url_input):
                st.error("❌ Invalid URL format. Please enter a valid URL (e.g., https://example.com)")
                logger.warning(f"Analysis attempted with invalid URL: {url_input}")
            else:
                # Ensure URL has scheme
                if not url_input.startswith(("http://", "https://")):
                    url_input = "https://" + url_input
                    logger.debug(f"Added https:// scheme to URL: {url_input}")
                
                with st.spinner("🔄 Analyzing webpage... This may take a minute."):
                    logger.info(f"Starting analysis for: {url_input}")
                    result = analyze_webpage_safe(url_input, include_patched_html=True)
                    
                    # Store result in session state for display
                    st.session_state.last_result = result
                    st.session_state.last_url = url_input
                    logger.info(f"Analysis completed for: {url_input}")
        
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            st.error(f"❌ An unexpected error occurred: {e}")
    
    # Display results if available
    if "last_result" in st.session_state:
        st.divider()
        display_results(st.session_state.last_result)


if __name__ == "__main__":
    main()
