"""
Streamlit App for Fact-Checking MVP
Powered by Alibaba Qwen 3 LLM
"""

import os
import tempfile
from typing import List, Dict

import streamlit as st
from dotenv import load_dotenv

from modules.input_processor import SimpleInputProcessor
from modules.claim_extractor import ClaimExtractor
from modules.search_engine import MVPSearchEngine
from modules.context_analyzer import ContextAnalyzer
from modules.verifier import SimpleVerifier

# Load local .env for development; on Streamlit Cloud, use app secrets
load_dotenv()
if "DASHSCOPE_API_KEY" not in os.environ and hasattr(st, 'secrets') and "DASHSCOPE_API_KEY" in st.secrets:
    os.environ["DASHSCOPE_API_KEY"] = st.secrets["DASHSCOPE_API_KEY"]
if "GOOGLE_API_KEY" not in os.environ and hasattr(st, 'secrets') and "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
if "GOOGLE_CSE_ID" not in os.environ and hasattr(st, 'secrets') and "GOOGLE_CSE_ID" in st.secrets:
    os.environ["GOOGLE_CSE_ID"] = st.secrets["GOOGLE_CSE_ID"]

# Configure page
st.set_page_config(
    page_title="Fact-Checker MVP",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .verdict-card {
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid;
        margin: 1rem 0;
    }
    .verdict-true { border-left-color: #4caf50; background: #e8f5e9; }
    .verdict-false { border-left-color: #f44336; background: #ffebee; }
    .verdict-neutral { border-left-color: #ff9800; background: #fff3e0; }
    .context-alert {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
        margin: 1rem 0;
    }
    .source-item {
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 Fact-Checking MVP with Context</h1>
    <p>Powered by Alibaba Qwen 3 LLM</p>
</div>
""", unsafe_allow_html=True)

# Initialize modules (cached for performance)
@st.cache_resource
def get_modules():
    """Initialize and cache all processing modules"""
    return (
        SimpleInputProcessor(),
        ClaimExtractor(),
        MVPSearchEngine(),
        ContextAnalyzer(),
        SimpleVerifier(),
    )

try:
    input_processor, claim_extractor, search_engine, context_analyzer, verifier = get_modules()
except Exception as e:
    st.error(f"Error initializing modules: {str(e)}")
    st.info("Please ensure DASHSCOPE_API_KEY is configured in Streamlit secrets or .env file")
    st.stop()

# Sidebar for input selection
st.sidebar.header("📝 Input")
input_type = st.sidebar.radio(
    "Choose input type",
    ["Text", "URL", "Image"],
    help="Select how you want to submit content for fact-checking"
)

# Input widgets based on type
text_input = None
url_input = None
image_file = None

if input_type == "Text":
    text_input = st.text_area(
        "Enter text to fact-check",
        height=200,
        placeholder="Paste claim or article text here...",
        help="Enter any claim or article text you want to verify"
    )
elif input_type == "URL":
    url_input = st.text_input(
        "Enter article URL",
        placeholder="https://example.com/article",
        help="Paste the URL of an article to fact-check"
    )
elif input_type == "Image":
    image_file = st.file_uploader(
        "Upload image with text (OCR)",
        type=["png", "jpg", "jpeg", "gif"],
        help="Upload an image containing text to extract and verify"
    )
    st.caption("⚠️ Note: OCR may be limited on Streamlit Cloud")

run_btn = st.button("🔍 Check Facts", type="primary", use_container_width=True)

def get_verdict_class(verdict: str) -> str:
    """Get CSS class based on verdict"""
    v = verdict.upper()
    if "VERIFIED" in v or "TRUE" in v:
        return "verdict-true"
    if "FALSE" in v or "MISLEADING" in v:
        return "verdict-false"
    return "verdict-neutral"

def render_sources(evidence: Dict):
    """Render source citations"""
    direct = evidence.get("direct_evidence", []) or []
    factchecks = evidence.get("existing_factchecks", []) or []
    all_sources = (direct + factchecks)[:10]
    
    if not all_sources:
        st.info("No sources found.")
        return
    
    for idx, src in enumerate(all_sources, 1):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{idx}. {src.get('title', 'Untitled')}**")
                st.caption(src.get('snippet', '')[:200] + '...' if len(src.get('snippet', '')) > 200 else src.get('snippet', ''))
                if src.get('factcheck_site'):
                    st.success("✓ Fact-Check Site", icon="✅")
            with col2:
                if src.get('url'):
                    st.link_button("View", src['url'], use_container_width=True)
        st.divider()

def render_timeline(timeline: List[Dict]):
    """Render timeline of events"""
    if not timeline:
        st.info("No timeline events extracted.")
        return
    
    for event in timeline[:10]:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"**{event.get('date', 'Unknown')}**")
        with col2:
            st.write(event.get('event', ''))
    
if run_btn:
    try:
        # Process input
        with st.spinner("Processing input..."):
            if input_type == "Text":
                if not (text_input or "").strip():
                    st.error("Please enter text to fact-check.")
                    st.stop()
                processed = input_processor.process(text_input, "text")

            elif input_type == "URL":
                if not (url_input or "").strip():
                    st.error("Please enter a URL to fact-check.")
                    st.stop()
                processed = input_processor.process(url_input.strip(), "url")

            else:  # Image
                if not image_file:
                    st.error("Please upload an image.")
                    st.stop()
                
                # Save temp file for OCR
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.name)[1]) as tmp:
                    tmp.write(image_file.read())
                    tmp_path = tmp.name
                
                processed = input_processor.process(tmp_path, "image")
                
                # Clean up temp file
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

                if processed.get("error"):
                    st.warning("⚠️ OCR may be unavailable in this environment. Proceeding with limited analysis.")

        # Extract claims
        with st.spinner("Extracting claims using Qwen 3..."):
            claims = claim_extractor.extract_claims(processed["text"])

        # Search evidence
        with st.spinner("Searching and verifying across multiple sources..."):
            evidence = search_engine.search_and_verify(claims)

        # Analyze context
        with st.spinner("Analyzing context and identifying missing information..."):
            context = context_analyzer.analyze_context(claims["main_claim"], evidence)

        # Calculate verdict
        verdict_data = verifier.calculate_verdict(claims["main_claim"], evidence, context)

        # Display results
        st.success("✅ Analysis Complete!")
        st.markdown("---")
        
        # Verdict Card
        st.subheader("📊 Verdict")
        verdict_class = get_verdict_class(verdict_data["verdict"])
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f'<div class="verdict-card {verdict_class}">', unsafe_allow_html=True)
            st.markdown(f"### {verdict_data['verdict']}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.metric("Confidence", f"{int(verdict_data['confidence'] * 100)}%")
            st.progress(verdict_data['confidence'])

        st.markdown("---")
        
        # Main Claim
        st.subheader("📌 Main Claim")
        st.info(claims["main_claim"])

        # Key Facts
        if claims.get("key_facts"):
            with st.expander("🔑 Key Facts Identified", expanded=False):
                for fact in claims["key_facts"][:5]:
                    checkable = "✓ Checkable" if fact.get("checkable") else "○ Not Checkable"
                    st.markdown(f"- {fact.get('claim', '')} _{checkable}_")

        st.markdown("---")
        
        # Missing Context - KEY FEATURE
        st.subheader("📋 Context You Should Know")
        missing_ctx = context.get("missing_context") or []
        
        if missing_ctx:
            st.markdown('<div class="context-alert">', unsafe_allow_html=True)
            if isinstance(missing_ctx, str):
                st.write(missing_ctx)
            else:
                for point in missing_ctx:
                    st.markdown(f"- {point}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No significant missing context identified.")

        # Full Picture
        if context.get("full_picture"):
            with st.expander("📖 Full Picture Summary", expanded=True):
                st.write(context["full_picture"])

        st.markdown("---")
        
        # Timeline
        st.subheader("📅 Timeline")
        timeline = context.get("timeline", [])
        if timeline:
            render_timeline(timeline)
        else:
            st.info("No timeline events extracted.")

        st.markdown("---")
        
        # Sources
        st.subheader("🔗 Sources & Evidence")
        render_sources(evidence)

        st.markdown("---")
        
        # Detailed Scores
        st.subheader("📊 Detailed Scores")
        scores = verdict_data.get("scores", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Source Agreement",
                f"{int(scores.get('source_agreement', 0) * 100)}%",
                help="How well sources agree with each other"
            )
        
        with col2:
            st.metric(
                "Source Quality",
                f"{int(scores.get('reputable_sources', 0) * 100)}%",
                help="Quality and reputation of sources"
            )
        
        with col3:
            st.metric(
                "Context Completeness",
                f"{int(scores.get('context_completeness', 0) * 100)}%",
                help="How complete the context analysis is"
            )
        
        with col4:
            st.metric(
                "Fact-Check Coverage",
                f"{int(scores.get('fact_check_exists', 0) * 100)}%",
                help="Existing fact-check availability"
            )

    except Exception as e:
        st.error(f"❌ An error occurred during fact-checking")
        st.exception(e)
        st.info("If you're seeing SSL errors, this may be due to network configuration. Try deploying on Streamlit Cloud for better reliability.")

# Footer
st.markdown("---")
st.caption("Powered by Alibaba Qwen 3 LLM | Built with Streamlit")
