import streamlit as st
import time
import re
import markdown as md_lib
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

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
.stTextInput > div > div > input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,140,50,0.25) !important; border-radius: 10px !important; color: #f0ebe0 !important; font-family: 'DM Sans', sans-serif !important; font-size: 1rem !important; padding: 0.75rem 1rem !important; transition: border-color 0.2s, box-shadow 0.2s !important; }
.stTextInput > div > div > input:focus { border-color: #ff8c32 !important; box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important; }
.stTextInput > label { font-family: 'DM Mono', monospace !important; font-size: 0.72rem !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; color: #ff8c32 !important; font-weight: 500 !important; }
.stButton > button { background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important; color: #0a0a0f !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.95rem !important; letter-spacing: 0.04em !important; border: none !important; border-radius: 10px !important; padding: 0.7rem 2.2rem !important; cursor: pointer !important; transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important; box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important; width: 100%; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important; opacity: 0.95 !important; }
.step-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 1.5rem 1.8rem; margin-bottom: 1.2rem; position: relative; overflow: hidden; transition: border-color 0.4s, background 0.4s, box-shadow 0.4s; }

/* WAITING — subtle fade in */
.step-card { animation: cardIn 0.4s ease both; }
@keyframes cardIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

/* ACTIVE — glowing border + shimmer sweep + pulsing left bar */
.step-card.active {
    border-color: rgba(255,140,50,0.55);
    background: rgba(255,140,50,0.05);
    box-shadow: 0 0 0 1px rgba(255,140,50,0.15), 0 0 32px rgba(255,140,50,0.10);
    animation: cardIn 0.4s ease both, borderPulse 2s ease-in-out infinite;
}
@keyframes borderPulse {
    0%,100% { box-shadow: 0 0 0 1px rgba(255,140,50,0.15), 0 0 24px rgba(255,140,50,0.08); }
    50%      { box-shadow: 0 0 0 1px rgba(255,140,50,0.40), 0 0 48px rgba(255,140,50,0.18); }
}

/* shimmer sweep across active card */
.step-card.active::after {
    content: '';
    position: absolute;
    top: 0; left: -75%;
    width: 50%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.07), transparent);
    animation: shimmer 2s ease-in-out infinite;
}
@keyframes shimmer { to { left: 130%; } }

.step-card.done { border-color: rgba(80,200,120,0.3); background: rgba(80,200,120,0.03); }
.step-card.error { border-color: rgba(255,80,80,0.4); background: rgba(255,80,80,0.03); }

/* left accent bar */
.step-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; border-radius: 14px 0 0 14px; background: rgba(255,255,255,0.05); transition: background 0.4s, box-shadow 0.4s; }
.step-card.active::before { background: #ff8c32; box-shadow: 0 0 12px rgba(255,140,50,0.8); animation: barPulse 1.2s ease-in-out infinite; }
@keyframes barPulse { 0%,100%{opacity:1} 50%{opacity:0.35} }
.step-card.done::before   { background: #50c878; box-shadow: 0 0 8px rgba(80,200,120,0.5); }
.step-card.error::before  { background: #ff5050; }

/* ACTIVE status badge blink */
.status-running { color: #ff8c32; animation: blink 1s step-end infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.step-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.3rem; }
.step-num { font-family: 'DM Mono', monospace; font-size: 0.68rem; font-weight: 500; letter-spacing: 0.15em; color: #ff8c32; opacity: 0.7; }
.step-title { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: #f0ebe0; }
.step-status { margin-left: auto; font-family: 'DM Mono', monospace; font-size: 0.68rem; letter-spacing: 0.1em; }
.status-waiting { color: #555; }
.status-running { color: #ff8c32; }
.status-done    { color: #50c878; }
.status-error   { color: #ff5050; }
.result-panel { background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 1.8rem 2rem; margin-top: 1rem; margin-bottom: 1.5rem; }
.result-panel-title { font-family: 'DM Mono', monospace; font-size: 0.7rem; font-weight: 500; letter-spacing: 0.2em; text-transform: uppercase; color: #ff8c32; margin-bottom: 1rem; padding-bottom: 0.7rem; border-bottom: 1px solid rgba(255,140,50,0.15); }
.result-content { font-size: 0.92rem; line-height: 1.8; color: #cdc8bf; white-space: pre-wrap; font-family: 'DM Sans', sans-serif; }

/* report + feedback boxes — content rendered inside via st.container border */
.report-box {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,140,50,0.2);
    border-radius: 16px;
    padding: 1.5rem 2rem 0.5rem;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}
.feedback-box {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(80,200,120,0.2);
    border-radius: 16px;
    padding: 1.5rem 2rem 1rem;
    margin-top: 1rem;
}
.panel-label { font-family: 'DM Mono', monospace; font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 1rem; padding-bottom: 0.7rem; }
.panel-label.orange { color: #ff8c32; border-bottom: 1px solid rgba(255,140,50,0.15); }
.panel-label.green  { color: #50c878; border-bottom: 1px solid rgba(80,200,120,0.15); }

/* ── HISTORY ── */
.history-drawer {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,140,50,0.15);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(8px);
}
.history-drawer-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #f0ebe0;
    margin-bottom: 1rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(255,140,50,0.12);
}
.history-empty {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #444;
    letter-spacing: 0.1em;
    text-align: center;
    padding: 1.5rem 0;
}
.h-entry {
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    background: rgba(255,255,255,0.02);
    position: relative;
    transition: border-color 0.2s;
}
.h-entry::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 2px;
    background: rgba(255,140,50,0.35);
    border-radius: 10px 0 0 10px;
}
.h-entry:hover { border-color: rgba(255,140,50,0.2); }
.h-topic {
    font-family: 'Syne', sans-serif;
    font-size: 0.88rem;
    font-weight: 700;
    color: #f0ebe0;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.h-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: rgba(255,140,50,0.4);
    letter-spacing: 0.08em;
    display: flex;
    align-items: center;
    gap: 12px;
}
.h-score {
    color: rgba(80,200,120,0.65);
    border: 1px solid rgba(80,200,120,0.18);
    border-radius: 100px;
    padding: 1px 8px;
    background: rgba(80,200,120,0.05);
}
.hist-view-banner {
    background: rgba(255,140,50,0.06);
    border: 1px solid rgba(255,140,50,0.2);
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: rgba(255,140,50,0.7);
    letter-spacing: 0.08em;
}
.hist-view-topic {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    color: #ff8c32;
}

/* history toggle pill button */
.hist-pill > button {
    background: transparent !important;
    border: 1px solid rgba(255,140,50,0.22) !important;
    border-radius: 100px !important;
    color: rgba(255,140,50,0.6) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.14em !important;
    padding: 5px 18px !important;
    width: auto !important;
    box-shadow: none !important;
}
.hist-pill > button:hover {
    border-color: rgba(255,140,50,0.5) !important;
    color: #ff8c32 !important;
    background: rgba(255,140,50,0.07) !important;
    transform: none !important;
    box-shadow: none !important;
}

.stSpinner > div { color: #ff8c32 !important; }
.section-heading { font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 700; color: #f0ebe0; margin: 2rem 0 1rem; }
.notice { font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #605850; text-align: center; margin-top: 3rem; letter-spacing: 0.08em; }
.stAlert { background: rgba(255,180,50,0.05) !important; border: 1px solid rgba(255,180,50,0.2) !important; border-radius: 10px !important; color: rgba(255,180,50,0.8) !important; font-size: 0.8rem !important; }
.stDownloadButton > button { background: transparent !important; border: 1px solid rgba(255,140,50,0.25) !important; border-radius: 10px !important; color: rgba(255,140,50,0.65) !important; font-family: 'DM Mono', monospace !important; font-size: 0.67rem !important; letter-spacing: 0.12em !important; padding: 10px 20px !important; width: auto !important; box-shadow: none !important; }
.stDownloadButton > button:hover { border-color: rgba(255,140,50,0.5) !important; color: #ff8c32 !important; background: rgba(255,140,50,0.06) !important; transform: none !important; }
/* ── Rendered markdown inside boxes ── */
.md-content { font-family: 'DM Sans', sans-serif; font-size: 0.93rem; line-height: 1.82; color: #cdc8bf; }
.md-content h1,.md-content h2,.md-content h3 { font-family: 'Syne', sans-serif; font-weight: 700; color: #f0ebe0; margin: 1.2rem 0 0.5rem; }
.md-content h1 { font-size: 1.3rem; }
.md-content h2 { font-size: 1.05rem; }
.md-content h3 { font-size: 0.9rem; color: #ff8c32; }
.md-content p { margin-bottom: 0.8rem; }
.md-content ul,.md-content ol { padding-left: 1.4rem; margin-bottom: 0.8rem; }
.md-content li { margin-bottom: 0.3rem; }
.md-content strong { color: #f0ebe0; font-weight: 600; }
.md-content a { color: #ff8c32; }
.md-content hr { border: none; border-top: 1px solid rgba(255,140,50,0.12); margin: 1.2rem 0; }

</style>
""", unsafe_allow_html=True)


# ── helpers ───────────────────────────────────────────────────────────────────
def step_card(num, title, state, desc="", error_msg=""):
    status_map = {
        "waiting": ("WAITING",   "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",    "status-done"),
        "error":   ("✗ ERROR",   "status-error"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done", "error": "error"}.get(state, "")

    # Animated dots indicator for running state
    running_indicator = ""
    if state == "running":
        running_indicator = """
        <div style="display:flex;align-items:center;gap:5px;margin-top:8px;">
            <span style="font-family:'DM Mono',monospace;font-size:0.62rem;
                         color:rgba(255,140,50,0.55);letter-spacing:0.1em;">PROCESSING</span>
            <span class="dots"><span>.</span><span>.</span><span>.</span></span>
        </div>"""

    extra = ""
    if desc:
        extra += f"<div style='font-size:0.82rem;color:#706860;margin-top:0.3rem;'>{desc}</div>"
    if error_msg:
        extra += f"<div style='font-size:0.80rem;color:#ff5050;margin-top:0.4rem;'>⚠ {error_msg}</div>"

    st.markdown(f"""
    <style>
    .dots span {{
        font-size: 1rem;
        color: #ff8c32;
        animation: dotBounce 1.2s ease-in-out infinite;
        display: inline-block;
    }}
    .dots span:nth-child(1) {{ animation-delay: 0s; }}
    .dots span:nth-child(2) {{ animation-delay: 0.2s; }}
    .dots span:nth-child(3) {{ animation-delay: 0.4s; }}
    @keyframes dotBounce {{
        0%,80%,100% {{ transform: translateY(0); opacity:0.3; }}
        40%          {{ transform: translateY(-4px); opacity:1; }}
    }}
    </style>
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {extra}
        {running_indicator}
    </div>
    """, unsafe_allow_html=True)

def extract_score(text):
    m = re.search(r'score\s*[:\-]\s*(\d+(?:\.\d+)?)\s*/\s*10', text, re.IGNORECASE)
    return f"{m.group(1)}/10" if m else None

def fmt_time(ts):
    return time.strftime("%d %b %Y · %H:%M", time.localtime(ts))

def extract_first_url(text):
    urls = re.findall(r'https?://[^\s\)\]\"\']+', text)
    for u in urls:
        if "wikipedia" not in u and ".pdf" not in u:
            return u.rstrip(".,;)")
    return urls[0].rstrip(".,;)") if urls else None

def display_results(res):
    """Render search raw, reader raw, report, critic."""
    if "search" in res:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                f'<div class="result-content">{res["search"]}</div></div>',
                unsafe_allow_html=True,
            )

    if "reader" in res:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                f'<div class="result-content">{res["reader"]}</div></div>',
                unsafe_allow_html=True,
            )

    # ── Report box: convert markdown → HTML so it all fits in one st.markdown call ──
    if "writer" in res:
        writer_html = md_lib.markdown(res["writer"], extensions=["extra"])
        st.markdown(f"""
        <div class="report-box">
            <div class="panel-label orange">📝 Final Research Report</div>
            <div class="md-content">{writer_html}</div>
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            label="⬇  Download Report (.md)",
            data=res["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # ── Critic box: same approach ──
    if "critic" in res:
        critic_html = md_lib.markdown(res["critic"], extensions=["extra"])
        st.markdown(f"""
        <div class="feedback-box">
            <div class="panel-label green">🧐 Critic Feedback</div>
            <div class="md-content">{critic_html}</div>
        </div>
        """, unsafe_allow_html=True)


# ── session state ─────────────────────────────────────────────────────────────
for k in ("results", "errors", "running", "done", "show_history", "view_hist_idx"):
    if k not in st.session_state:
        if k in ("results", "errors"):
            st.session_state[k] = {}
        elif k in ("show_history",):
            st.session_state[k] = False
        elif k == "view_hist_idx":
            st.session_state[k] = None
        else:
            st.session_state[k] = False

if "history" not in st.session_state:
    st.session_state.history = []

r = st.session_state.results
e = st.session_state.errors
history = st.session_state.history


# ── HERO ─────────────────────────────────────────────────────────────────────
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


# ── HISTORY TOGGLE ────────────────────────────────────────────────────────────
hist_count = len(history)
tog_col, _ = st.columns([1, 5])
with tog_col:
    badge = f" ({hist_count})" if hist_count else ""
    label = f"{'▾' if st.session_state.show_history else '▸'}  History{badge}"
    st.markdown('<div class="hist-pill">', unsafe_allow_html=True)
    if st.button(label, key="hist_toggle"):
        st.session_state.show_history = not st.session_state.show_history
        st.session_state.view_hist_idx = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── HISTORY DRAWER ────────────────────────────────────────────────────────────
if st.session_state.show_history:
    st.markdown('<div class="history-drawer">', unsafe_allow_html=True)
    st.markdown('<div class="history-drawer-title">🕐 Search History</div>', unsafe_allow_html=True)

    if not history:
        st.markdown('<div class="history-empty">No searches yet. Run your first pipeline to see history here.</div>', unsafe_allow_html=True)
    else:
        clr_col, _ = st.columns([1, 6])
        with clr_col:
            if st.button("🗑  Clear all", key="clear_hist"):
                st.session_state.history = []
                st.session_state.view_hist_idx = None
                st.rerun()

        for i, entry in enumerate(reversed(history)):
            actual_idx = len(history) - 1 - i
            score = extract_score(entry["results"].get("critic", "")) or "—"
            agents = [k for k in ["search","reader","writer","critic"] if k in entry["results"]]

            st.markdown(f"""
            <div class="h-entry">
                <div class="h-topic">{entry['topic']}</div>
                <div class="h-meta">
                    <span>🕐 {fmt_time(entry['ts'])}</span>
                    <span class="h-score">★ {score}</span>
                    <span>{len(agents)}/4 agents</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            v_col, d_col = st.columns([4, 1])
            with v_col:
                if st.button("↗ View report", key=f"view_{actual_idx}"):
                    st.session_state.view_hist_idx = actual_idx
                    st.session_state.show_history = False
                    st.rerun()
            with d_col:
                if st.button("✕", key=f"del_{actual_idx}"):
                    st.session_state.history.pop(actual_idx)
                    if st.session_state.view_hist_idx == actual_idx:
                        st.session_state.view_hist_idx = None
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ── HISTORY REPORT VIEWER ─────────────────────────────────────────────────────
view_idx = st.session_state.view_hist_idx
if view_idx is not None and view_idx < len(history):
    entry = history[view_idx]
    st.markdown(f"""
    <div class="hist-view-banner">
        <span>📂</span>
        <div>
            <div style="font-size:0.6rem;margin-bottom:2px;">VIEWING ARCHIVED REPORT · {fmt_time(entry['ts'])}</div>
            <div class="hist-view-topic">{entry['topic']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    b1, b2, _ = st.columns([1, 1, 5])
    with b1:
        if st.button("← Back to history", key="back_to_hist"):
            st.session_state.show_history = True
            st.session_state.view_hist_idx = None
            st.rerun()
    with b2:
        if st.button("✦ New research", key="new_research"):
            st.session_state.view_hist_idx = None
            st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    display_results(entry["results"])
    st.markdown('<div class="notice">ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit</div>', unsafe_allow_html=True)
    st.stop()


# ── MAIN TWO-COLUMN LAYOUT ────────────────────────────────────────────────────
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

    st.markdown("""
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.5rem;align-items:center;">
        <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#605850;letter-spacing:0.1em;">TRY →</span>
    """, unsafe_allow_html=True)
    for ex in ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]:
        st.markdown(f"""
        <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:6px;
        padding:0.25rem 0.7rem;font-size:0.75rem;color:#a09890;font-family:'DM Sans',sans-serif;">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    def s(step):
        if step in e: return "error"
        if step in r: return "done"
        if st.session_state.running:
            for k in ["search","reader","writer","critic"]:
                if k not in r and k not in e:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent", s("search"), "Gathers recent web information",  e.get("search",""))
    step_card("02", "Reader Agent", s("reader"), "Scrapes & extracts deep content", e.get("reader",""))
    step_card("03", "Writer Chain", s("writer"), "Drafts the full research report", e.get("writer",""))
    step_card("04", "Critic Chain", s("critic"), "Reviews & scores the report",     e.get("critic",""))


# ── RUN PIPELINE ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.errors = {}
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.view_hist_idx = None

if st.session_state.running and not st.session_state.done:
    topic_val = st.session_state.topic_input
    results, errors = {}, {}

    # Step 1 — Search
    with st.spinner("🔍  Search Agent is working…"):
        try:
            sa = build_search_agent()
            sr = sa.invoke({"messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]})
            results["search"] = sr["messages"][-1].content
        except Exception as ex:
            errors["search"] = str(ex)[:120]

    # Step 2 — Reader (extract URL directly, no LLM hallucination risk)
    if "search" in results:
        with st.spinner("📄  Reader Agent is scraping top resources…"):
            try:
                url = extract_first_url(results["search"])
                ra = build_reader_agent()
                msg = f"Scrape this URL: {url}" if url else results["search"][:300]
                rr = ra.invoke({"messages": [("user", msg)]})
                results["reader"] = rr["messages"][-1].content
            except Exception as ex:
                errors["reader"] = str(ex)[:120]
                results["reader"] = results["search"]

    # Step 3 — Writer
    if "search" in results:
        with st.spinner("✍️  Writer is drafting the report…"):
            try:
                results["writer"] = writer_chain.invoke({
                    "topic": topic_val,
                    "research": (
                        f"SEARCH RESULTS:\n{results.get('search','')}\n\n"
                        f"DETAILED SCRAPED CONTENT:\n{results.get('reader','')}"
                    )
                })
            except Exception as ex:
                errors["writer"] = str(ex)[:120]

    # Step 4 — Critic
    if "writer" in results:
        with st.spinner("🧐  Critic is reviewing the report…"):
            try:
                results["critic"] = critic_chain.invoke({"report": results["writer"]})
            except Exception as ex:
                errors["critic"] = str(ex)[:120]

    # Save to history
    if results:
        st.session_state.history.append({
            "topic":   topic_val,
            "ts":      time.time(),
            "results": dict(results),
        })

    st.session_state.results = results
    st.session_state.errors  = errors
    st.session_state.running = False
    st.session_state.done    = True
    st.rerun()


# ── RESULTS ───────────────────────────────────────────────────────────────────
r = st.session_state.results
if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)
    display_results(r)

st.markdown('<div class="notice">ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit</div>', unsafe_allow_html=True)
