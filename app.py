import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, build_writer_chain, build_critic_chain

st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #e8e4dc; }
.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }
.hero { text-align: center; padding: 3.5rem 0 2.5rem; position: relative; }
.hero-eyebrow { font-family: 'DM Mono', monospace; font-size: 0.7rem; font-weight: 500; letter-spacing: 0.25em; text-transform: uppercase; color: #ff8c32; margin-bottom: 1rem; opacity: 0.9; }
.hero h1 { font-family: 'Syne', sans-serif; font-size: clamp(2.8rem, 6vw, 5rem); font-weight: 800; line-height: 1.0; letter-spacing: -0.03em; color: #f0ebe0; margin: 0 0 1rem; }
.hero h1 span { color: #ff8c32; }
.hero-sub { font-size: 1.05rem; font-weight: 300; color: #a09890; max-width: 520px; margin: 0 auto; line-height: 1.65; }
.divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent); margin: 2rem 0; }
.input-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,140,50,0.15); border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 2rem; backdrop-filter: blur(8px); }
.stTextInput > div > div > input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,140,50,0.25) !important; border-radius: 10px !important; color: #f0ebe0 !important; font-size: 1rem !important; padding: 0.75rem 1rem !important; }
.stButton > button { background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important; color: #0a0a0f !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; border: none !important; border-radius: 10px !important; padding: 0.7rem 2.2rem !important; width: 100%; }
.step-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 1.5rem 1.8rem; margin-bottom: 1.2rem; position: relative; overflow: hidden; }
.step-card.active { border-color: rgba(255,140,50,0.4); background: rgba(255,140,50,0.04); }
.step-card.done { border-color: rgba(80,200,120,0.3); background: rgba(80,200,120,0.03); }
.step-card.error { border-color: rgba(255,80,80,0.4); background: rgba(255,80,80,0.03); }
.step-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; border-radius: 14px 0 0 14px; background: rgba(255,255,255,0.05); }
.step-card.active::before { background: #ff8c32; }
.step-card.done::before { background: #50c878; }
.step-card.error::before { background: #ff5050; }
.step-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.3rem; }
.step-num { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #ff8c32; opacity: 0.7; }
.step-title { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: #f0ebe0; }
.step-status { margin-left: auto; font-family: 'DM Mono', monospace; font-size: 0.68rem; }
.status-waiting { color: #555; }
.status-running { color: #ff8c32; }
.status-done { color: #50c878; }
.status-error { color: #ff5050; }
.report-panel { background: rgba(255,140,50,0.05); border: 1px solid rgba(255,140,50,0.3); border-radius: 16px; padding: 2rem 2.5rem; margin-top: 1rem; }
.feedback-panel { background: rgba(80,200,120,0.05); border: 1px solid rgba(80,200,120,0.3); border-radius: 16px; padding: 2rem 2.5rem; margin-top: 1rem; }
.panel-label { font-family: 'DM Mono', monospace; font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 1.2rem; padding-bottom: 0.7rem; }
.panel-label.orange { color: #ff8c32; border-bottom: 1px solid rgba(255,140,50,0.15); }
.panel-label.green { color: #50c878; border-bottom: 1px solid rgba(80,200,120,0.15); }
.section-heading { font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 700; color: #f0ebe0; margin: 2rem 0 1rem; }
.result-content { font-size: 0.92rem; line-height: 1.8; color: #cdc8bf; white-space: pre-wrap; }
.notice { font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #605850; text-align: center; margin-top: 3rem; letter-spacing: 0.08em; }
</style>
""", unsafe_allow_html=True)


def step_card(num, title, state, desc="", error_msg=""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
        "error":   ("✗ ERROR",  "status-error"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done", "error": "error"}.get(state, "")
    extra = ""
    if desc:
        extra += f"<div style='font-size:0.82rem;color:#706860;margin-top:0.3rem;'>{desc}</div>"
    if error_msg:
        extra += f"<div style='font-size:0.80rem;color:#ff5050;margin-top:0.4rem;'>⚠ {error_msg}</div>"
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {extra}
    </div>
    """, unsafe_allow_html=True)


for key in ("results", "errors", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key in ("results", "errors") else False

st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)
    r = st.session_state.results
    e = st.session_state.errors

    def s(step):
        if step in e:
            return "error"
        if step in r:
            return "done"
        if st.session_state.running:
            order = ["search", "reader", "writer", "critic"]
            for k in order:
                if k not in r and k not in e:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent", s("search"), "Gathers recent web information",  e.get("search",""))
    step_card("02", "Reader Agent", s("reader"), "Scrapes & extracts deep content", e.get("reader",""))
    step_card("03", "Writer Chain", s("writer"), "Drafts the full research report", e.get("writer",""))
    step_card("04", "Critic Chain", s("critic"), "Reviews & scores the report",     e.get("critic",""))

if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.errors = {}
        st.session_state.running = True
        st.session_state.done = False

if st.session_state.running and not st.session_state.done:
    topic_val = st.session_state.topic_input
    results = {}
    errors = {}

    # Step 1: Search
    with st.spinner("🔍  Search Agent is working…"):
        try:
            search_agent = build_search_agent()
            sr = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
            })
            results["search"] = sr["messages"][-1].content
        except Exception as ex:
            errors["search"] = str(ex)[:120]

    # Step 2: Reader
    if "search" in results:
        with st.spinner("📄  Reader Agent is scraping top resources…"):
            try:
                reader_agent = build_reader_agent()
                rr = reader_agent.invoke({
                    "messages": [("user",
                        f"Based on the following search results about '{topic_val}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{results['search'][:800]}"
                    )]
                })
                results["reader"] = rr["messages"][-1].content
            except Exception as ex:
                errors["reader"] = str(ex)[:120]
                results["reader"] = results["search"]

    # Step 3: Writer
    if "search" in results:
        with st.spinner("✍️  Writer is drafting the report…"):
            try:
                writer_chain = build_writer_chain()
                research_combined = (
                    f"SEARCH RESULTS:\n{results.get('search','')}\n\n"
                    f"DETAILED SCRAPED CONTENT:\n{results.get('reader','')}"
                )
                results["writer"] = writer_chain.invoke({
                    "topic": topic_val,
                    "research": research_combined
                })
            except Exception as ex:
                errors["writer"] = str(ex)[:120]

    # Step 4: Critic
    if "writer" in results:
        with st.spinner("🧐  Critic is reviewing the report…"):
            try:
                critic_chain = build_critic_chain()
                results["critic"] = critic_chain.invoke({"report": results["writer"]})
            except Exception as ex:
                errors["critic"] = str(ex)[:120]

    st.session_state.results = results
    st.session_state.errors = errors
    st.session_state.running = False
    st.session_state.done = True
    st.rerun()

r = st.session_state.results
if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-content">{r["search"]}</div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-content">{r["reader"]}</div>', unsafe_allow_html=True)

    if "writer" in r:
        st.markdown(f"""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
            <div class="result-content">{r["writer"]}</div>
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown(f"""
        <div class="feedback-panel">
            <div class="panel-label green">🧐 Critic Feedback</div>
            <div class="result-content">{r["critic"]}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="notice">ResearchMind · Powered by LangChain multi-agent pipeline · Deployed on Streamlit Cloud</div>', unsafe_allow_html=True)
