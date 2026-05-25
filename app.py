import os
import streamlit as st

from file_handler import extract_zip, read_project_files, create_code_summary, get_readme_content
from rule_analyzer import rule_based_analysis
from agents import code_style_agent, documentation_agent, viva_question_agent, risk_scoring_agent
from report_builder import get_category, build_simple_report

UPLOAD_FOLDER = "uploads"
EXTRACT_FOLDER = "extracted_projects"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACT_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="CodeTrace AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* ── Root variables ── */
:root {
    --bg-primary:    #080c14;
    --bg-secondary:  #0d1520;
    --bg-card:       #111927;
    --bg-card-hover: #162030;
    --border:        #1e3048;
    --border-bright: #1e4a72;
    --cyan:          #00d4ff;
    --cyan-dim:      #00a3c4;
    --cyan-glow:     rgba(0, 212, 255, 0.15);
    --amber:         #f59e0b;
    --amber-dim:     #b45309;
    --green:         #10b981;
    --red:           #ef4444;
    --text-primary:  #e2eaf4;
    --text-secondary:#7a9ab8;
    --text-muted:    #3d5a78;
    --mono:          'Space Mono', monospace;
    --sans:          'Outfit', sans-serif;
}

/* ── Global reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--sans) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--bg-secondary) !important; }

/* Hide default Streamlit chrome */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

/* ── Main container ── */
.block-container {
    padding: 0 2.5rem 4rem !important;
    max-width: 1280px !important;
}

/* ── Hero header ── */
.hero-wrap {
    position: relative;
    padding: 3.5rem 0 2.5rem;
    margin-bottom: 2rem;
    overflow: hidden;
}
.hero-grid {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,212,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: linear-gradient(180deg, transparent, rgba(0,0,0,0.6) 30%, rgba(0,0,0,0.6) 70%, transparent);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--cyan-glow);
    border: 1px solid var(--cyan-dim);
    border-radius: 100px;
    padding: 4px 14px;
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--cyan);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}
.hero-badge::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--cyan);
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.4; transform: scale(0.8); }
}
.hero-title {
    font-family: var(--sans);
    font-size: 3.4rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #e2eaf4 30%, var(--cyan) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.8rem;
}
.hero-sub {
    font-family: var(--sans);
    font-size: 1.05rem;
    font-weight: 400;
    color: var(--text-secondary);
    max-width: 560px;
    line-height: 1.7;
    margin-bottom: 2rem;
}
.hero-divider {
    height: 1px;
    background: linear-gradient(90deg, var(--cyan-dim), transparent 70%);
    margin-top: 1rem;
}

/* ── Cards ── */
.ct-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    transition: border-color 0.25s, background 0.25s;
    position: relative;
    overflow: hidden;
}
.ct-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--cyan), transparent 60%);
    opacity: 0;
    transition: opacity 0.25s;
}
.ct-card:hover { border-color: var(--border-bright); background: var(--bg-card-hover); }
.ct-card:hover::before { opacity: 1; }

.ct-card-cyan::before { opacity: 1; }
.ct-card-amber::before { background: linear-gradient(90deg, var(--amber), transparent 60%); opacity: 1; }
.ct-card-green::before { background: linear-gradient(90deg, var(--green), transparent 60%); opacity: 1; }
.ct-card-red::before   { background: linear-gradient(90deg, var(--red),   transparent 60%); opacity: 1; }

/* ── Section headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid var(--border);
}
.section-num {
    width: 30px; height: 30px;
    border-radius: 8px;
    background: var(--cyan-glow);
    border: 1px solid var(--cyan-dim);
    display: flex; align-items: center; justify-content: center;
    font-family: var(--mono);
    font-size: 0.72rem;
    color: var(--cyan);
    font-weight: 700;
    flex-shrink: 0;
}
.section-title {
    font-family: var(--sans);
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: 0.02em;
    text-transform: uppercase;
}
.section-tag {
    margin-left: auto;
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1.5px dashed var(--border-bright) !important;
    border-radius: 14px !important;
    padding: 1.5rem !important;
    transition: border-color 0.25s, background 0.25s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--cyan-dim) !important;
    background: var(--bg-card-hover) !important;
}
[data-testid="stFileUploader"] label {
    color: var(--text-secondary) !important;
    font-family: var(--sans) !important;
}
[data-testid="stFileUploadDropzone"] {
    background: transparent !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.4rem !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: var(--cyan) !important;
    font-family: var(--mono) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #0d4f7a, #0a3a5c) !important;
    border: 1px solid var(--cyan-dim) !important;
    border-radius: 10px !important;
    color: var(--cyan) !important;
    font-family: var(--sans) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.7rem 2rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.08) !important;
}
[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #1a6fa8, #0d4f7a) !important;
    border-color: var(--cyan) !important;
    box-shadow: 0 0 30px rgba(0,212,255,0.22) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    font-family: var(--sans) !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    padding: 0.8rem 1.2rem !important;
}
[data-testid="stExpander"] summary:hover { color: var(--cyan) !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: var(--sans) !important;
}
.stSuccess {
    background: rgba(16,185,129,0.1) !important;
    border-color: var(--green) !important;
    color: #6ee7b7 !important;
}
.stInfo {
    background: rgba(0,212,255,0.07) !important;
    border-color: var(--cyan-dim) !important;
    color: var(--cyan) !important;
}
.stWarning {
    background: rgba(245,158,11,0.1) !important;
    border-color: var(--amber) !important;
    color: #fcd34d !important;
}
.stError {
    background: rgba(239,68,68,0.1) !important;
    border-color: var(--red) !important;
    color: #fca5a5 !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--cyan) !important; }

/* ── Text & write ── */
.stMarkdown p, .stText, [data-testid="stText"] {
    color: var(--text-secondary) !important;
    font-family: var(--sans) !important;
    font-size: 0.95rem !important;
    line-height: 1.75 !important;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: var(--text-primary) !important;
    font-family: var(--sans) !important;
    font-weight: 700 !important;
}

/* ── Code / pre ── */
pre, code, [data-testid="stCode"] {
    background: #0a121e !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
    font-size: 0.82rem !important;
    color: #7dd3fc !important;
}

/* ── Dividers ── */
hr { border-color: var(--border) !important; }

/* ── Status pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 100px;
    font-family: var(--mono);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.pill-low    { background: rgba(16,185,129,0.12); border: 1px solid var(--green); color: var(--green); }
.pill-medium { background: rgba(245,158,11,0.12); border: 1px solid var(--amber); color: var(--amber); }
.pill-high   { background: rgba(239,68,68,0.12);  border: 1px solid var(--red);   color: var(--red); }
.pill-low::before, .pill-medium::before, .pill-high::before {
    content: ''; width: 5px; height: 5px; border-radius: 50%; background: currentColor;
}

/* ── Info strip ── */
.info-strip {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1.6rem;
}
.info-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 14px;
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--text-secondary);
}
.info-chip span { color: var(--cyan); font-weight: 700; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan-dim); }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-grid"></div>
    <div class="hero-badge">● Agentic Analysis Engine — v1.0</div>
    <div class="hero-title">CodeTrace AI</div>
    <div class="hero-sub">
        Multi-agent forensic analysis of software projects. Detects AI-generated code patterns,
        evaluates documentation authenticity, and generates academic integrity reports.
    </div>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

# ── Upload Section ────────────────────────────────────────────────────────────
st.markdown("""
<div class="ct-card ct-card-cyan">
    <div class="section-header">
        <div class="section-num">01</div>
        <div class="section-title">Project Upload</div>
        <div class="section-tag">ZIP Archive</div>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop your project ZIP here, or click to browse",
    type=["zip"],
    label_visibility="visible"
)

# ── Process Upload ────────────────────────────────────────────────────────────
if uploaded_file is not None:
    zip_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    project_name = uploaded_file.name.replace(".zip", "")
    extract_path = os.path.join(EXTRACT_FOLDER, project_name)
    extract_zip(zip_path, extract_path)

    st.success(f"✓  **{uploaded_file.name}** uploaded and extracted successfully.")

    files_data = read_project_files(extract_path)

    st.markdown(f"""
    <div class="info-strip">
        <div class="info-chip">📁 Project <span>{project_name}</span></div>
        <div class="info-chip">🗂️ Source Files <span>{len(files_data)} detected</span></div>
        <div class="info-chip">📦 Archive Size <span>{round(uploaded_file.size / 1024, 1)} KB</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Run Analysis Button ───────────────────────────────────────────────────
    col_btn, col_note = st.columns([2, 5])
    with col_btn:
        run_analysis = st.button("⚡ Run Agentic AI Analysis", use_container_width=True)
    with col_note:
        st.markdown("""
        <p style="color:var(--text-muted);font-size:0.8rem;padding-top:0.7rem;font-family:var(--mono);">
        5 agents · Rule engine + 4 AI models · ~60–90 sec
        </p>""", unsafe_allow_html=True)

    if run_analysis:
        if len(files_data) == 0:
            st.error("⚠️  No supported code files found in the uploaded project.")
        else:
            code_summary   = create_code_summary(files_data)
            readme_content = get_readme_content(files_data)

            # ── Agent 1 — Rule-Based Analyzer ────────────────────────────────
            st.markdown("""
            <div class="ct-card ct-card-cyan" style="margin-top:2rem;">
                <div class="section-header">
                    <div class="section-num">01</div>
                    <div class="section-title">Rule-Based Analyzer</div>
                    <div class="section-tag">Heuristic Engine</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            rule_score, rule_evidence = rule_based_analysis(files_data)
            category = get_category(rule_score)

            # Choose pill colour
            pill_cls = "pill-low" if rule_score < 40 else ("pill-medium" if rule_score < 70 else "pill-high")

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Rule-Based Score", f"{rule_score} / 100")
            with m2:
                st.markdown(f"""
                <div style="padding:1.2rem 1.4rem;background:var(--bg-card);
                     border:1px solid var(--border);border-radius:12px;">
                    <div style="font-family:var(--mono);font-size:0.72rem;
                         color:var(--text-secondary);letter-spacing:0.08em;
                         text-transform:uppercase;margin-bottom:6px;">Risk Category</div>
                    <span class="status-pill {pill_cls}">{category}</span>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div style="padding:1.2rem 1.4rem;background:var(--bg-card);
                     border:1px solid var(--border);border-radius:12px;">
                    <div style="font-family:var(--mono);font-size:0.72rem;
                         color:var(--text-secondary);letter-spacing:0.08em;
                         text-transform:uppercase;margin-bottom:6px;">Evidence Flags</div>
                    <div style="font-family:var(--mono);font-size:2rem;
                         font-weight:700;color:var(--amber);">{len(rule_evidence)}</div>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("🔍  View Rule-Based Evidence Flags"):
                for i, item in enumerate(rule_evidence, 1):
                    st.markdown(f"""
                    <div style="display:flex;align-items:flex-start;gap:10px;
                         padding:8px 0;border-bottom:1px solid var(--border);">
                        <span style="font-family:var(--mono);font-size:0.7rem;
                              color:var(--text-muted);min-width:24px;padding-top:2px;">
                              {i:02d}</span>
                        <span style="color:var(--text-secondary);font-size:0.9rem;">{item}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Agent 2 — Code Style ──────────────────────────────────────────
            st.markdown("""
            <div class="ct-card ct-card-cyan" style="margin-top:1.5rem;">
                <div class="section-header">
                    <div class="section-num">02</div>
                    <div class="section-title">Code Style Agent</div>
                    <div class="section-tag">AI · Stylometric Analysis</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Code Style Agent scanning patterns…"):
                style_output = code_style_agent(code_summary)
            st.write(style_output)

            # ── Agent 3 — Documentation ───────────────────────────────────────
            st.markdown("""
            <div class="ct-card ct-card-cyan" style="margin-top:1.5rem;">
                <div class="section-header">
                    <div class="section-num">03</div>
                    <div class="section-title">Documentation Agent</div>
                    <div class="section-tag">AI · README & Comments</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Documentation Agent reviewing README and inline docs…"):
                docs_output = documentation_agent(readme_content, code_summary)
            st.write(docs_output)

            # ── Agent 4 — Viva Questions ──────────────────────────────────────
            st.markdown("""
            <div class="ct-card ct-card-amber" style="margin-top:1.5rem;">
                <div class="section-header">
                    <div class="section-num">04</div>
                    <div class="section-title">Viva Question Agent</div>
                    <div class="section-tag">AI · Oral Defence Prep</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Viva Question Agent generating targeted questions…"):
                viva_output = viva_question_agent(code_summary)
            st.write(viva_output)

            # ── Agent 5 — Final Risk Score ────────────────────────────────────
            st.markdown("""
            <div class="ct-card ct-card-red" style="margin-top:1.5rem;">
                <div class="section-header">
                    <div class="section-num">05</div>
                    <div class="section-title">Final Risk Scoring Agent</div>
                    <div class="section-tag">AI · Synthesis & Verdict</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Risk Scoring Agent synthesising all signals…"):
                final_report = risk_scoring_agent(
                    rule_score,
                    rule_evidence,
                    style_output,
                    docs_output,
                    viva_output
                )

            st.markdown("""
            <div style="margin-top:0.5rem;margin-bottom:0.5rem;">
                <span style="font-family:var(--mono);font-size:0.72rem;
                      color:var(--cyan);letter-spacing:0.1em;text-transform:uppercase;">
                ▸ Final Authenticity Report
                </span>
            </div>
            """, unsafe_allow_html=True)
            st.write(final_report)

            # ── Project Summary ───────────────────────────────────────────────
            st.markdown("""
            <div class="ct-card ct-card-green" style="margin-top:2rem;">
                <div class="section-header">
                    <div class="section-num">∑</div>
                    <div class="section-title">Project Summary</div>
                    <div class="section-tag">Structured Report</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            simple_report = build_simple_report(
                project_name,
                len(files_data),
                rule_score,
                category
            )
            st.code(simple_report, language="text")

            # ── Disclaimer ────────────────────────────────────────────────────
            st.markdown("""
            <div style="margin-top:2rem;padding:1rem 1.4rem;
                 background:rgba(245,158,11,0.06);
                 border:1px solid rgba(245,158,11,0.25);
                 border-radius:10px;
                 display:flex;align-items:flex-start;gap:12px;">
                <span style="font-size:1.1rem;margin-top:1px;">⚠️</span>
                <span style="font-family:var(--sans);font-size:0.85rem;
                      color:#fcd34d;line-height:1.65;">
                    <strong>Disclaimer:</strong> CodeTrace AI estimates AI-usage risk based on
                    heuristic and model signals. Results should be used for review support only
                    — not as final proof of authorship or academic misconduct.
                </span>
            </div>
            """, unsafe_allow_html=True)