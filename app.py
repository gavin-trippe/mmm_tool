"""
MMM Campaign Mapper - Concept Tool
===================================
Full-feature prototype demonstrating the campaign mapping workflow.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from data_simulator import (
    generate_raw_data,
    setup_demo_client,
    list_clients,
    create_client,
    load_client_config,
    save_client_config,
    get_all_tactics,
    load_mappings,
    save_mappings,
    load_ignored,
    save_ignored,
    get_unmapped_campaigns,
    build_clean_output,
    save_export_snapshot,
    list_export_snapshots,
    load_export_snapshot,
    compare_exports,
    check_date_continuity,
    check_dependent_variables,
    list_source_configs,
    load_source_config,
    save_source_config,
    detect_new_sources,
    check_data_freshness,
    check_source_freshness,
    load_onboarding_state,
    save_onboarding_state,
    get_all_campaigns_for_onboarding,
    RAW_CAMPAIGNS,
    SIMULATED_CSV_SOURCES,
    DEFAULT_TACTICS,
    DEFAULT_DEP_VARS,
    DEFAULT_CONTEXT_VARS,
    generate_geo_data,
    aggregate_geo_for_geolift,
    get_unmatched_zips,
    normalize_zip,
    zip_to_dma,
    ZIP_DMA_LOOKUP,
)

st.set_page_config(page_title="MMM Campaign Mapper", layout="wide", initial_sidebar_state="expanded")

# -- Global SaaS CSS --
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    /* Force sidebar always open */
    section[data-testid="stSidebar"] { min-width: 280px !important; width: 280px !important; transform: none !important; }
    section[data-testid="stSidebar"] > div { width: 280px !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { background: #f8fafc; border-right: 1px solid #e2e8f0; }
    section[data-testid="stSidebar"] .stRadio label { padding: 0.5rem 1rem; border-radius: 8px; transition: all 0.2s; font-weight: 500; font-size: 0.85rem; color: #334155; }
    section[data-testid="stSidebar"] .stRadio label:hover { background: rgba(99, 102, 241, 0.1); }
    section[data-testid="stSidebar"] hr { border-color: #e2e8f0; }
    .stButton > button { background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white !important; border: none; border-radius: 8px; padding: 0.5rem 1.5rem; font-weight: 600; font-size: 0.85rem; transition: all 0.2s; box-shadow: 0 2px 4px rgba(99, 102, 241, 0.3); }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4); }
    .stDownloadButton > button { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white !important; border: none; border-radius: 8px; padding: 0.6rem 2rem; font-weight: 600; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3); }
    .stDownloadButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4); }
    .stDataFrame { border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
    .stSelectbox > div > div { border-radius: 8px; }
    .stAlert { border-radius: 10px; }
    .saas-page-header { margin-bottom: 1.5rem; }
    .saas-page-header h1 { font-size: 1.8rem; font-weight: 700; color: #0f172a; margin-bottom: 0.25rem; }
    .saas-page-header p { color: #64748b; font-size: 1rem; margin-top: 0; }
    .saas-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .saas-card-warning { border-left: 4px solid #f59e0b; background: #fffbeb; }
    .saas-card-success { border-left: 4px solid #10b981; background: #ecfdf5; }
    .saas-card-danger { border-left: 4px solid #ef4444; background: #fef2f2; }
    .saas-badge { display: inline-block; padding: 0.2rem 0.7rem; border-radius: 50px; font-size: 0.75rem; font-weight: 600; }
    .badge-green { background: #dcfce7; color: #166534; }
    .badge-red { background: #fef2f2; color: #991b1b; }
    .badge-blue { background: #eff6ff; color: #1e40af; }
    .badge-gray { background: #f1f5f9; color: #475569; }
    .badge-amber { background: #fef3c7; color: #92400e; }
    .tactic-tag { display: inline-block; background: #eff6ff; color: #3b82f6; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.8rem; font-weight: 500; margin: 0.15rem; font-family: 'SF Mono', 'Fira Code', monospace; }
    .depvar-tag { display: inline-block; background: #faf5ff; color: #7c3aed; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.8rem; font-weight: 500; margin: 0.15rem; font-family: 'SF Mono', 'Fira Code', monospace; }
    .mapping-card { background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #f59e0b; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .mapping-card .campaign-name { font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace; background: #f8fafc; padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.85rem; color: #334155; border: 1px solid #e2e8f0; }
    .mapping-card .campaign-meta { margin-top: 0.5rem; font-size: 0.8rem; color: #64748b; }
    .section-divider { height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0 20%, #e2e8f0 80%, transparent); margin: 2rem 0; border: none; }
    .feature-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; margin-bottom: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .feature-card .feature-title { font-weight: 700; font-size: 0.95rem; color: #0f172a; margin-bottom: 0.25rem; }
    .feature-card .feature-desc { font-size: 0.85rem; color: #64748b; line-height: 1.5; }
    .source-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center; }
    .source-card .source-name { font-weight: 600; color: #0f172a; font-size: 0.95rem; }
    .source-card .source-count { color: #6366f1; font-weight: 700; font-size: 1.1rem; }
    .pipeline-step { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .pipeline-step .step-title { font-weight: 700; font-size: 0.95rem; color: #0f172a; margin-bottom: 0.25rem; }
    .pipeline-step .step-desc { font-size: 0.8rem; color: #64748b; }
    .pipeline-arrow { display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: #6366f1; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# -- Helpers --
def page_header(title, subtitle=""):
    html = f'<div class="saas-page-header"><h1>{title}</h1>'
    if subtitle:
        html += f"<p>{subtitle}</p>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def section_divider():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def metric_card(label, value, accent_color="#6366f1"):
    st.markdown(f"""
    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:12px;
                padding:1.25rem; box-shadow:0 1px 3px rgba(0,0,0,0.06);
                border-top:3px solid {accent_color};">
        <div style="color:#64748b; font-size:0.75rem; font-weight:600;
                    text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.4rem;">
            {label}
        </div>
        <div style="color:#0f172a; font-size:1.5rem; font-weight:700;">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def dev_info(title, description, functions=None, data_flow=None):
    """Render a collapsible developer spec block at the top of a page."""
    fn_html = ""
    if functions:
        fn_html = '<div style="margin-top:0.75rem; padding-top:0.75rem; border-top:1px solid #e0e7ff;">'
        fn_html += '<div style="font-size:0.7rem; font-weight:700; color:#6366f1; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">Backend Functions</div>'
        for fn in functions:
            fn_html += f'<div style="font-family:monospace; font-size:0.8rem; color:#334155; padding:0.2rem 0; line-height:1.6;">{fn}</div>'
        fn_html += '</div>'
    flow_html = ""
    if data_flow:
        flow_html = '<div style="margin-top:0.75rem; padding-top:0.75rem; border-top:1px solid #e0e7ff;">'
        flow_html += '<div style="font-size:0.7rem; font-weight:700; color:#6366f1; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">Data Flow</div>'
        flow_html += f'<div style="font-size:0.8rem; color:#475569; line-height:1.6;">{data_flow}</div>'
        flow_html += '</div>'
    with st.expander("Dev Spec", expanded=False):
        st.markdown(f"""
        <div style="background:#eef2ff; border:1px solid #c7d2fe; border-radius:10px; padding:1.25rem;">
            <div style="font-weight:700; color:#312e81; font-size:0.9rem; margin-bottom:0.4rem;">{title}</div>
            <div style="font-size:0.85rem; color:#475569; line-height:1.6;">{description}</div>
            {fn_html}
            {flow_html}
        </div>
        """, unsafe_allow_html=True)


# -- Init --
setup_demo_client()


@st.cache_data
def cached_raw_data():
    return generate_raw_data(start_date="2025-10-20", n_days=111)


@st.cache_data
def cached_geo_data():
    return generate_geo_data(start_date="2025-07-01", n_days=228)


# -- Sidebar: Client selector --
st.sidebar.markdown("""
<div style="padding: 0.5rem 0 0.5rem 0; text-align: center;">
    <div style="font-size: 1.3rem; font-weight: 700; letter-spacing: -0.02em;">Campaign Mapper</div>
    <div style="font-size: 0.7rem; color: #64748b; font-weight: 500;">MMM Data Pipeline Tool</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

clients = list_clients()
if "active_client" not in st.session_state:
    st.session_state.active_client = clients[0] if clients else None

selected_client = st.sidebar.selectbox("Client", clients, key="client_select",
    index=clients.index(st.session_state.active_client) if st.session_state.active_client in clients else 0)

if selected_client != st.session_state.active_client:
    st.session_state.active_client = selected_client
    # Clear cached state
    for k in ["raw_data", "mappings", "ignored", "config"]:
        st.session_state.pop(k, None)
    st.rerun()

# New client button
with st.sidebar.expander("Add Client"):
    new_name = st.text_input("Client name", key="new_client_name")
    if st.button("Create", key="btn_create_client"):
        if new_name and new_name.strip():
            create_client(new_name.strip().lower().replace(" ", "_"))
            st.session_state.active_client = new_name.strip().lower().replace(" ", "_")
            st.rerun()

st.sidebar.markdown("---")

CLIENT = st.session_state.active_client

# Load client state
if "raw_data" not in st.session_state:
    st.session_state.raw_data = cached_raw_data()
if "config" not in st.session_state:
    st.session_state.config = load_client_config(CLIENT)
if "mappings" not in st.session_state:
    st.session_state.mappings = load_mappings(CLIENT)
if "ignored" not in st.session_state:
    st.session_state.ignored = load_ignored(CLIENT)

raw_df = st.session_state.raw_data
config = st.session_state.config
saved_mappings = st.session_state.mappings
ignored_list = st.session_state.ignored

# -- Sidebar: Nav --
view_mode = st.sidebar.selectbox("View", ["Internal", "Client Dashboard"], key="view_mode", label_visibility="collapsed")

onboarding_state = load_onboarding_state(CLIENT)
is_onboarded = onboarding_state.get("completed", False)

if view_mode == "Internal":
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Overview"

    # Nav button CSS - override default button styles inside sidebar nav
    st.markdown("""
    <style>
        div[data-testid="stSidebar"] .nav-btn button {
            background: none !important; border: none !important; box-shadow: none !important;
            color: #334155 !important; font-weight: 500 !important; font-size: 0.85rem !important;
            padding: 0.45rem 1rem !important; border-radius: 8px !important; width: 100% !important;
            text-align: left !important; transition: all 0.15s !important; margin: 0 !important;
        }
        div[data-testid="stSidebar"] .nav-btn button:hover {
            background: rgba(99, 102, 241, 0.08) !important; transform: none !important;
        }
        div[data-testid="stSidebar"] .nav-btn-active button {
            background: rgba(99, 102, 241, 0.12) !important; color: #4f46e5 !important;
            font-weight: 600 !important; box-shadow: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # -- Setup section --
    st.sidebar.markdown('<div style="font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8; padding:0.5rem 1rem 0.25rem;">Setup</div>', unsafe_allow_html=True)
    for p in ["Overview", "Sources", "Onboarding", "Raw Data"]:
        css_class = "nav-btn-active" if st.session_state.current_page == p else "nav-btn"
        st.sidebar.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.sidebar.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.current_page = p
            st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # -- Maintenance section --
    st.sidebar.markdown('<div style="font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8; padding:0.75rem 1rem 0.25rem; border-top:1px solid #e2e8f0; margin-top:0.5rem;">Maintenance</div>', unsafe_allow_html=True)
    for p in ["Data Freshness", "Campaign Mapping", "Spike Analysis", "Data Audit", "Clean Export", "Settings"]:
        css_class = "nav-btn-active" if st.session_state.current_page == p else "nav-btn"
        st.sidebar.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.sidebar.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.current_page = p
            st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # -- Incrementality Testing section --
    st.sidebar.markdown('<div style="font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8; padding:0.75rem 1rem 0.25rem; border-top:1px solid #e2e8f0; margin-top:0.5rem;">Incrementality Testing</div>', unsafe_allow_html=True)
    for p in ["Geo Lift Export"]:
        css_class = "nav-btn-active" if st.session_state.current_page == p else "nav-btn"
        st.sidebar.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.sidebar.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.current_page = p
            st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

    page = st.session_state.current_page
else:
    page = "Client Dashboard"

st.sidebar.markdown("---")

# Sidebar alerts
unmapped = get_unmapped_campaigns(raw_df, saved_mappings, ignored_list)
new_sources = detect_new_sources(CLIENT)
alert_count = len(unmapped) + len(new_sources)

if alert_count > 0:
    parts = []
    if unmapped:
        parts.append(f"{len(unmapped)} unmapped")
    if new_sources:
        parts.append(f"{len(new_sources)} new source(s)")
    st.sidebar.markdown(f"""
    <div style="background:#fef3c7; border:1px solid #fcd34d;
                border-radius:10px; padding:0.75rem 1rem; text-align:center;">
        <div style="font-size:1.3rem; font-weight:700; color:#b45309;">{alert_count}</div>
        <div style="font-size:0.75rem; color:#92400e; font-weight:500;">{" | ".join(parts)}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style="background:#ecfdf5; border:1px solid #6ee7b7;
                border-radius:10px; padding:0.75rem 1rem; text-align:center;">
        <div style="font-size:0.8rem; color:#047857; font-weight:600;">All Good</div>
    </div>
    """, unsafe_allow_html=True)

if ignored_list:
    ignored_spend = raw_df[raw_df["raw_campaign_name"].isin(ignored_list)]["daily_value"].sum()
    st.sidebar.markdown(f"""
    <div style="background:#fef2f2; border:1px solid #fca5a5;
                border-radius:10px; padding:0.5rem 1rem; text-align:center; margin-top:0.5rem;">
        <div style="font-size:0.75rem; color:#b91c1c; font-weight:500;">{len(ignored_list)} ignored (${ignored_spend:,.0f} excluded)</div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("")
st.sidebar.caption("Concept tool - simulated data")


# ==========================================================
# PAGE 1: Overview (Feature List for Developer)
# ==========================================================
if page == "Overview":

    # Hero
    st.markdown("""
    <div style="background:linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%); border:1px solid #c7d2fe;
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em; line-height:1.2;">
            MMM Campaign Mapper
        </div>
        <div style="font-size:0.95rem; color:#4338ca; margin-top:0.35rem; font-weight:500;">
            Feature specification for developer -- interactive concept prototype
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.4);"></div>
        <div style="position:absolute; bottom:-30px; right:60px; width:80px; height:80px;
                    border-radius:50%; background:rgba(255,255,255,0.25);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Overview Page",
        "Landing page that serves as a feature specification for the developer. Shows the data pipeline flow "
        "(Ingest -> Configure -> Map -> Export) and lists every feature the production tool needs to support. "
        "Also shows the simulated data sources used in this demo.",
        functions=["setup_demo_client() -- creates demo_client folder with pre-loaded config, mappings, and export snapshot",
                   "list_clients() -- scans clients/ folder for subdirectories",
                   "create_client(name) -- creates a new client folder structure"],
        data_flow="No data processing on this page. Pure informational/spec page for developer reference."
    )

    # Pipeline flow - styled steps
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1.25rem;">
        Data Pipeline Flow
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("1", "Ingest", "Raw data from APIs + CSVs flows into client folder", "#6366f1"),
        ("2", "Configure", "Map CSV columns, set tactics and dep vars", "#3b82f6"),
        ("3", "Map", "Tag campaigns to standard names, ignore unwanted", "#8b5cf6"),
        ("4", "Export", "Clean daily output with audit trail", "#10b981"),
    ]
    steps_html = '<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:1rem; margin-bottom:2rem;">'
    for num, title, desc, color in steps:
        steps_html += f"""
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden; text-align:center;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:{color};"></div>
            <div style="width:36px; height:36px; border-radius:50%; background:{color}; color:#fff;
                        display:inline-flex; align-items:center; justify-content:center;
                        font-weight:800; font-size:0.9rem; margin-bottom:0.75rem;">{num}</div>
            <div style="font-weight:700; font-size:0.95rem; color:#0f172a; margin-bottom:0.3rem;">{title}</div>
            <div style="font-size:0.8rem; color:#64748b; line-height:1.5;">{desc}</div>
        </div>"""
    steps_html += "</div>"
    st.markdown(steps_html, unsafe_allow_html=True)

    # Feature list - premium cards
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Feature List
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
        Every capability the production tool needs to support
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("Multi-Client Support", "Each client has isolated config, mappings, and exports. Switch between clients via dropdown.", "Settings", "#6366f1"),
        ("Source Auto-Detection", "When new CSV files appear in a client's data folder, the app alerts and prompts for column mapping.", "Sources", "#f59e0b"),
        ("CSV Column Mapping", "For each data source, specify which columns contain campaign name, spend amount, and date.", "Sources", "#3b82f6"),
        ("Campaign Mapping", "Tag raw campaign names to standardized tactic names. Many-to-one mapping (multiple campaigns summed into one tactic).", "Mapping", "#8b5cf6"),
        ("Campaign Ignore/Exclude", "Mark specific campaigns as ignored (e.g., international spend). Shows total excluded spend.", "Mapping", "#ef4444"),
        ("Dependent Variable Mapping", "Map raw data to dependent variables (acquisition, winbacks). Multiple dep vars supported.", "Mapping", "#7c3aed"),
        ("Tactic Name Management", "Add/remove standardized tactic names organized by channel group. Add/remove dependent variable names.", "Settings", "#10b981"),
        ("Export Window", "Set a rolling window (e.g., 27 months) so the export only includes recent data. Configurable per client.", "Settings", "#0ea5e9"),
        ("Clean Export + Snapshots", "Produces daily rows x tactic columns output for Recast. Each export saves a snapshot for auditing.", "Export", "#10b981"),
        ("Data Audit / EDA", "Compare current vs prior export: flag changed historical data, check date continuity, validate dep vars.", "Audit", "#f59e0b"),
        ("Exclude Date Support", "exclude_this_date column (TRUE/FALSE). Data must still be present. If dep var is 0 and not excluded, flagged.", "Audit", "#ef4444"),
    ]

    feat_html = ""
    for title, desc, badge, color in features:
        feat_html += f"""
        <div style="background:#fff; border:1px solid #e2e8f0; border-left:4px solid {color};
                    border-radius:12px; padding:1.25rem 1.5rem; margin-bottom:0.75rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
                <div style="font-weight:700; font-size:0.95rem; color:#0f172a;">{title}</div>
                <span style="background:#f1f5f9; color:#64748b; padding:0.15rem 0.6rem; border-radius:50px;
                             font-size:0.7rem; font-weight:600;">{badge}</span>
            </div>
            <div style="font-size:0.85rem; color:#64748b; line-height:1.5;">{desc}</div>
        </div>"""
    st.markdown(feat_html, unsafe_allow_html=True)

    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

    # Data sources
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1.25rem;">
        Data Sources in Demo
    </div>
    """, unsafe_allow_html=True)

    src_html = '<div style="display:grid; grid-template-columns:repeat(2, 1fr); gap:1rem;">'
    # API sources
    src_html += '<div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
    src_html += '<div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8; margin-bottom:1rem;">API Sources</div>'
    for ch in ["meta", "google", "tiktok"]:
        n = len(RAW_CAMPAIGNS[ch]["campaigns"])
        src_html += f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:0.6rem 0; border-bottom:1px solid #f1f5f9;">
            <span style="font-weight:600; color:#334155; font-size:0.9rem;">{ch.title()}</span>
            <span style="font-weight:700; color:#6366f1; font-size:1rem;">{n}</span>
        </div>"""
    src_html += "</div>"
    # CSV sources
    src_html += '<div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
    src_html += '<div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8; margin-bottom:1rem;">CSV Sources</div>'
    for ch in ["radio", "other", "dep_var"]:
        n = len(RAW_CAMPAIGNS[ch]["campaigns"])
        label = ch.replace("dep_var", "Dependent Variables").replace("_", " ").title()
        src_html += f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:0.6rem 0; border-bottom:1px solid #f1f5f9;">
            <span style="font-weight:600; color:#334155; font-size:0.9rem;">{label}</span>
            <span style="font-weight:700; color:#6366f1; font-size:1rem;">{n}</span>
        </div>"""
    src_html += "</div></div>"
    st.markdown(src_html, unsafe_allow_html=True)


# ==========================================================
# PAGE 2: Raw Data
# ==========================================================
elif page == "Raw Data":

    # Hero
    st.markdown("""
    <div style="background:linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border:1px solid #bfdbfe;
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">
            Raw Campaign Data
        </div>
        <div style="font-size:0.95rem; color:#1e40af; margin-top:0.35rem; font-weight:500;">
            All ingested campaign-level daily data before mapping
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.4);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Raw Data Page",
        "Shows all ingested campaign-level daily data after onboarding is complete. This is the full feed from "
        "Fivetran/BigQuery/CSVs. Users can filter by channel and source type. The campaign summary table shows "
        "mapping status for each campaign so you can verify everything is tagged correctly.",
        functions=["generate_raw_data(start_date, n_days) -- simulates daily campaign data across all channels (meta, google, tiktok, radio, other, dep_var)",
                   "get_unmapped_campaigns(raw_df, mappings, ignored) -- returns campaigns not yet mapped or ignored",
                   "RAW_CAMPAIGNS dict -- defines all simulated campaigns with channel, source type, default mappings"],
        data_flow="Fivetran pulls raw data from ad platforms into BigQuery -> Each table becomes a data source -> "
        "Raw campaign rows with columns: date, channel, source_type, raw_campaign_name, daily_value"
    )

    # Filters
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        channels = ["All"] + [c for c in RAW_CAMPAIGNS.keys()]
        channel_filter = st.selectbox("Channel", channels)
    with col2:
        source_filter = st.selectbox("Source Type", ["All", "api", "csv"])

    display_df = raw_df.copy()
    if channel_filter != "All":
        display_df = display_df[display_df["channel"] == channel_filter]
    if source_filter != "All":
        display_df = display_df[display_df["source_type"] == source_filter]

    unique_campaigns = display_df["raw_campaign_name"].nunique()
    total_value = display_df["daily_value"].sum()
    n_mapped = display_df[display_df["mapped_to"].notna()]["raw_campaign_name"].nunique()
    n_unmapped = unique_campaigns - n_mapped
    n_ignored = display_df[display_df["raw_campaign_name"].isin(ignored_list)]["raw_campaign_name"].nunique()

    # KPI strip
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:1rem; margin:1.5rem 0;">
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:#6366f1;"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Campaigns</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">{unique_campaigns}</div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:#3b82f6;"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Total Value</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">${total_value:,.0f}</div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:#10b981;"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Mapped</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">{n_mapped}</div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:#f59e0b;"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Unmapped</div>
            <div style="font-size:1.8rem; font-weight:800; color:#{'b45309' if n_unmapped > 0 else '0f172a'}; margin-top:0.25rem;">{n_unmapped}</div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:#ef4444;"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Ignored</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">{n_ignored}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Campaign summary
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1rem;">
        Campaign Summary
    </div>
    """, unsafe_allow_html=True)

    camp_sum = (
        display_df.groupby(["channel", "source_type", "raw_campaign_name", "mapped_to", "mapping_type"])
        .agg(total_value=("daily_value", "sum"), days_active=("date", "nunique"))
        .reset_index().sort_values("total_value", ascending=False)
    )
    camp_sum["status"] = camp_sum.apply(
        lambda r: "IGNORED" if r["raw_campaign_name"] in ignored_list
        else ("MAPPED" if pd.notna(r["mapped_to"]) or r["raw_campaign_name"] in saved_mappings else "UNMAPPED"), axis=1
    )

    def highlight_status(row):
        if row["status"] == "UNMAPPED":
            return ["background-color: #fef2f2; color: #991b1b;"] * len(row)
        if row["status"] == "IGNORED":
            return ["background-color: #f8fafc; color: #94a3b8;"] * len(row)
        return [""] * len(row)

    st.dataframe(camp_sum.style.apply(highlight_status, axis=1), use_container_width=True, height=400)

    with st.expander("View raw daily data"):
        st.dataframe(display_df.sort_values(["date", "channel"], ascending=[False, True]),
                      use_container_width=True, height=400)


# ==========================================================
# PAGE 3: Sources
# ==========================================================
elif page == "Sources":

    # Hero
    new_src = detect_new_sources(CLIENT)
    hero_bg = "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)" if new_src else "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)"
    hero_border = "#fcd34d" if new_src else "#6ee7b7"
    hero_sub_color = "#92400e" if new_src else "#047857"
    hero_sub = f"{len(new_src)} new source(s) detected -- configure column mappings below" if new_src else "All sources configured and active"
    st.markdown(f"""
    <div style="background:{hero_bg}; border:1px solid {hero_border};
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">
            Data Sources
        </div>
        <div style="font-size:0.95rem; color:{hero_sub_color}; margin-top:0.35rem; font-weight:500;">
            {hero_sub}
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.4);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Sources Page",
        "Each data source (BigQuery table, CSV file, API export) has different column names. This page lets the user "
        "tell the system which column is the campaign name, which is spend, and which is the date. Without this, the "
        "pipeline doesn't know how to read a new source. When a new file appears in the client data folder with no "
        "config, it shows an alert here. In production, each Fivetran connector lands a table in BigQuery -- this is "
        "where you map that table's schema to our standard format.",
        functions=["detect_new_sources(client) -- compares files in data/ folder vs saved source configs, returns unconfigured files",
                   "load_source_config(client, source_name) -- loads column mapping config for a source",
                   "save_source_config(client, source_name, config) -- saves {campaign_column, spend_column, date_column}",
                   "list_source_configs(client) -- returns all configured source names",
                   "SIMULATED_CSV_SOURCES dict -- demo sources with columns to simulate real vendor reports"],
        data_flow="New BigQuery table or CSV file appears -> Sources page detects it -> User selects which columns are "
        "campaign name, spend, and date -> Config saved to clients/{client}/source_configs/{source}.json -> "
        "Pipeline now knows how to ingest this source"
    )

    # New source alerts
    if new_src:
        for f in new_src:
            st.markdown(f"""
            <div style="background:#fff; border:1px solid #fcd34d; border-left:4px solid #f59e0b;
                        border-radius:12px; padding:1.25rem 1.5rem; margin-bottom:1rem;
                        box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-weight:700; color:#92400e; font-size:0.95rem; margin-bottom:0.5rem;">
                    New file: {f}
                </div>
            </div>
            """, unsafe_allow_html=True)
            name = f.rsplit(".", 1)[0]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                display_name = st.text_input("Display Name", value=name, key=f"src_name_{name}")
            with col2:
                camp_col = st.text_input("Campaign Column", key=f"src_camp_{name}")
            with col3:
                spend_col = st.text_input("Spend Column", key=f"src_spend_{name}")
            with col4:
                date_col = st.text_input("Date Column", key=f"src_date_{name}")
            if st.button(f"Save Config", key=f"src_save_{name}"):
                if camp_col and spend_col and date_col:
                    save_source_config(CLIENT, name, {
                        "display_name": display_name,
                        "campaign_column": camp_col,
                        "spend_column": spend_col,
                        "date_column": date_col,
                    })
                    st.rerun()
        st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

    # Configured sources
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1.25rem;">
        Configured Sources
    </div>
    """, unsafe_allow_html=True)

    configs = list_source_configs(CLIENT)
    if configs:
        cfg_html = ""
        for src_name in configs:
            src_cfg = load_source_config(CLIENT, src_name)
            if src_cfg:
                cfg_html += f"""
                <div style="background:#fff; border:1px solid #e2e8f0; border-left:4px solid #10b981;
                            border-radius:12px; padding:1.25rem 1.5rem; margin-bottom:0.75rem;
                            box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <span style="font-weight:700; color:#0f172a; font-size:0.95rem;">{src_cfg.get('display_name', src_name)}</span>
                        <span style="background:#dcfce7; color:#166534; padding:0.15rem 0.6rem; border-radius:50px;
                                     font-size:0.7rem; font-weight:600;">Active</span>
                    </div>
                    <div style="display:flex; gap:2rem; font-size:0.8rem;">
                        <div><span style="color:#94a3b8;">Campaign:</span> <span style="color:#334155; font-weight:600;">{src_cfg.get('campaign_column', '-')}</span></div>
                        <div><span style="color:#94a3b8;">Spend:</span> <span style="color:#334155; font-weight:600;">{src_cfg.get('spend_column', '-')}</span></div>
                        <div><span style="color:#94a3b8;">Date:</span> <span style="color:#334155; font-weight:600;">{src_cfg.get('date_column', '-')}</span></div>
                    </div>
                </div>"""
        st.markdown(cfg_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:2rem; text-align:center;">
            <div style="font-size:0.9rem; color:#64748b;">No source configs yet. Drop CSV files into the client's data folder to get started.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

    # All data sources with column mapping
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Source Column Mapping
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
        For each data source, select which column is the campaign name, spend value, and date
    </div>
    """, unsafe_allow_html=True)

    sim_colors = ["#6366f1", "#3b82f6", "#8b5cf6", "#0ea5e9", "#10b981", "#7c3aed", "#f97316", "#ec4899"]
    for idx, (src_name, src_info) in enumerate(SIMULATED_CSV_SOURCES.items()):
        color = sim_colors[idx % len(sim_colors)]
        all_cols = src_info["columns"]
        src_type = src_info.get("source_type", "spend")
        is_depvar_source = src_type == "dependent_variable"
        is_context_source = src_type == "context_variable"

        # Load existing config for this source
        existing_cfg = load_source_config(CLIENT, src_name) or {}
        is_configured = bool(existing_cfg)

        # Show available columns as tags
        cols_list = " ".join(f'<span style="background:#f1f5f9; color:#334155; padding:0.15rem 0.5rem; border-radius:4px; font-size:0.75rem; font-family:monospace; margin:0.1rem;">{c}</span>' for c in all_cols)
        if is_depvar_source:
            type_badge = '<span style="background:#faf5ff; color:#7c3aed; padding:0.15rem 0.6rem; border-radius:50px; font-size:0.7rem; font-weight:600;">Dep Var Source</span>'
        elif is_context_source:
            type_badge = '<span style="background:#fef3c7; color:#92400e; padding:0.15rem 0.6rem; border-radius:50px; font-size:0.7rem; font-weight:600;">Context Var Source</span>'
        else:
            type_badge = '<span style="background:#eff6ff; color:#1e40af; padding:0.15rem 0.6rem; border-radius:50px; font-size:0.7rem; font-weight:600;">Spend Source</span>'
        status_badge = '<span style="background:#dcfce7; color:#166534; padding:0.15rem 0.6rem; border-radius:50px; font-size:0.7rem; font-weight:600;">Configured</span>' if is_configured else '<span style="background:#fef3c7; color:#92400e; padding:0.15rem 0.6rem; border-radius:50px; font-size:0.7rem; font-weight:600;">Needs Config</span>'

        st.markdown(f"""
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem 1.5rem;
                    margin-bottom:0.25rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:{color};"></div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <span style="font-weight:700; color:#0f172a; font-size:0.95rem;">{src_name}</span>
                    {type_badge}
                </div>
                {status_badge}
            </div>
            <div style="margin-bottom:0.5rem;">
                <span style="font-size:0.7rem; font-weight:600; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em;">Available columns:</span>
            </div>
            <div>{cols_list}</div>
        </div>
        """, unsafe_allow_html=True)

        if is_depvar_source or is_context_source:
            # Dep var or context var source: map columns to variable names
            saved_date = existing_cfg.get("date_column", src_info["date_col"])
            date_idx = all_cols.index(saved_date) if saved_date in all_cols else 0
            default_dv_map = src_info.get("dep_var_cols", {})
            saved_dv_map = existing_cfg.get("dep_var_columns", default_dv_map)

            dc1, dc2 = st.columns([1, 3])
            with dc1:
                new_date = st.selectbox("Date Column", all_cols, index=date_idx, key=f"src_date_{src_name}")

            if is_context_source:
                st.markdown('<div style="font-size:0.8rem; font-weight:600; color:#92400e; margin-bottom:0.5rem;">Map columns to context variables:</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.8rem; font-weight:600; color:#7c3aed; margin-bottom:0.5rem;">Map columns to dependent variables:</div>', unsafe_allow_html=True)

            dep_var_names = config.get("dependent_variables", [])
            ctx_var_names = config.get("context_variables", [])
            dv_col_assignments = {}
            num_dv_cols = len(default_dv_map)
            dv_columns = st.columns(max(num_dv_cols + 1, 2) + [1])  if False else None  # placeholder

            # Show a row per potential column
            dv_source_cols = [c for c in all_cols if c != new_date]
            if is_context_source:
                col_options = ["-- skip --"] + ctx_var_names
            else:
                col_options = ["-- skip --"] + dep_var_names
            for dv_idx, dv_col in enumerate(dv_source_cols[:6]):
                dvc1, dvc2 = st.columns([1, 1])
                default_target = saved_dv_map.get(dv_col, "")
                target_idx = col_options.index(default_target) if default_target in col_options else 0
                with dvc1:
                    st.markdown(f'<span style="font-family:monospace; font-size:0.85rem; color:#334155;">{dv_col}</span>', unsafe_allow_html=True)
                with dvc2:
                    picked = st.selectbox("Maps to", col_options, index=target_idx, key=f"dv_map_{src_name}_{dv_col}", label_visibility="collapsed")
                if picked != "-- skip --":
                    dv_col_assignments[dv_col] = picked

            if st.button("Save", key=f"src_save_{src_name}", use_container_width=True):
                save_source_config(CLIENT, src_name, {
                    "display_name": src_name,
                    "source_type": src_type,
                    "date_column": new_date,
                    "dep_var_columns": dv_col_assignments,
                })
                st.rerun()
        else:
            # Spend source: campaign, spend, date columns
            saved_camp = existing_cfg.get("campaign_column", src_info["campaign_col"])
            saved_spend = existing_cfg.get("spend_column", src_info["spend_col"])
            saved_date = existing_cfg.get("date_column", src_info["date_col"])

            sc1, sc2, sc3, sc4 = st.columns([3, 3, 3, 1.5])
            with sc1:
                camp_idx = all_cols.index(saved_camp) if saved_camp in all_cols else 0
                new_camp = st.selectbox("Campaign Name", all_cols, index=camp_idx, key=f"src_camp_{src_name}")
            with sc2:
                spend_idx = all_cols.index(saved_spend) if saved_spend in all_cols else 0
                new_spend = st.selectbox("Spend / Value", all_cols, index=spend_idx, key=f"src_spend_{src_name}")
            with sc3:
                date_idx = all_cols.index(saved_date) if saved_date in all_cols else 0
                new_date = st.selectbox("Date", all_cols, index=date_idx, key=f"src_date_{src_name}")
            with sc4:
                st.markdown("")
                if st.button("Save", key=f"src_save_{src_name}", use_container_width=True):
                    save_source_config(CLIENT, src_name, {
                        "display_name": src_name,
                        "campaign_column": new_camp,
                        "spend_column": new_spend,
                        "date_column": new_date,
                    })
                    st.rerun()

        st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)


# ==========================================================
# PAGE 4: Campaign Mapping
# ==========================================================
elif page == "Campaign Mapping":

    all_tactics = get_all_tactics(config)
    dep_vars = config.get("dependent_variables", [])
    unmapped = get_unmapped_campaigns(raw_df, saved_mappings, ignored_list)

    # Hero
    hero_bg = "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)" if unmapped else "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)"
    hero_border = "#fcd34d" if unmapped else "#6ee7b7"
    hero_sub_color = "#92400e" if unmapped else "#047857"
    hero_sub = f"{len(unmapped)} campaign(s) need mapping" if unmapped else "All campaigns mapped or ignored"
    st.markdown(f"""
    <div style="background:{hero_bg}; border:1px solid {hero_border};
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">
            Campaign Mapping
        </div>
        <div style="font-size:0.95rem; color:{hero_sub_color}; margin-top:0.35rem; font-weight:500;">
            {hero_sub}
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.4);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Campaign Mapping Page (Maintenance)",
        "Post-onboarding mapping interface for incremental updates. When new campaigns appear (e.g., a new ad set "
        "launches), they show up here as unmapped. Users assign them to standardized tactic names or dependent variables. "
        "Also allows ignoring campaigns (e.g., international spend) so they are excluded from the clean export entirely.",
        functions=[
            "get_unmapped_campaigns(raw_df, saved_mappings, ignored_list) -- returns campaigns not yet mapped or ignored",
            "get_all_tactics(config) -- returns flat list of all tactic names from config",
            "save_mappings(client, mappings) -- persists campaign-to-tactic mapping dict to JSON",
            "load_mappings(client) -- loads saved mappings from JSON",
            "save_ignored(client, ignored_list) -- persists list of ignored campaign names",
            "load_ignored(client) -- loads ignored campaign list",
        ],
        data_flow="Raw campaigns -> user selects tactic or dep var -> save_mappings() writes to campaign_mappings.json. "
                   "Ignored campaigns -> save_ignored() writes to ignored_campaigns.json. "
                   "Mapping type can be 'tactic' (spend column) or 'dependent_variable' (outcome column like acquisition)."
    )

    # Unmapped campaigns
    if unmapped:
        for i, camp in enumerate(unmapped):
            camp_data = raw_df[raw_df["raw_campaign_name"] == camp["raw_campaign_name"]]
            total = camp_data["daily_value"].sum()
            days = camp_data["date"].nunique()

            st.markdown(f"""
            <div style="background:#fff; border:1px solid #e2e8f0; border-left:4px solid #f59e0b;
                        border-radius:12px; padding:1.5rem; margin-bottom:1rem;
                        box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                    <span style="font-weight:700; color:#0f172a;">Campaign {i+1}</span>
                    <div style="display:flex; gap:0.4rem;">
                        <span style="background:#eff6ff; color:#1e40af; padding:0.15rem 0.6rem; border-radius:50px;
                                     font-size:0.7rem; font-weight:600;">{camp['channel']}</span>
                        <span style="background:#f1f5f9; color:#64748b; padding:0.15rem 0.6rem; border-radius:50px;
                                     font-size:0.7rem; font-weight:600;">{camp['source_type']}</span>
                    </div>
                </div>
                <div style="font-family:'SF Mono','Fira Code','Courier New',monospace; background:#f8fafc;
                            padding:0.6rem 0.85rem; border-radius:8px; font-size:0.85rem; color:#334155;
                            border:1px solid #e2e8f0;">{camp['raw_campaign_name']}</div>
                <div style="display:flex; gap:1.5rem; margin-top:0.6rem; font-size:0.8rem; color:#64748b;">
                    <span>Total: <strong style="color:#0f172a;">${total:,.2f}</strong></span>
                    <span>Active: <strong style="color:#0f172a;">{days} days</strong></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns([1.5, 3, 1.5, 1])
            with col1:
                map_type = st.selectbox("Type", ["Spend Tactic", "Dependent Variable", "Context Variable"],
                                        key=f"type_{i}", label_visibility="collapsed")
            with col2:
                if map_type == "Spend Tactic":
                    channel_tactics = config["tactics"].get(camp["channel"], [])
                    options = channel_tactics + [t for t in all_tactics if t not in channel_tactics]
                elif map_type == "Dependent Variable":
                    options = dep_vars
                else:
                    options = config.get("context_variables", [])
                selected = st.selectbox("Target", ["-- Select --"] + options,
                                        key=f"map_{i}", label_visibility="collapsed")
            with col3:
                if st.button("Save", key=f"btn_save_{i}", use_container_width=True):
                    if selected != "-- Select --":
                        type_lookup = {"Spend Tactic": "tactic", "Dependent Variable": "dependent_variable", "Context Variable": "context_variable"}
                        m_type = type_lookup[map_type]
                        saved_mappings[camp["raw_campaign_name"]] = {"target": selected, "type": m_type}
                        save_mappings(CLIENT, saved_mappings)
                        st.session_state.mappings = saved_mappings
                        st.rerun()
            with col4:
                if st.button("Ignore", key=f"btn_ign_{i}", use_container_width=True):
                    ignored_list.append(camp["raw_campaign_name"])
                    save_ignored(CLIENT, ignored_list)
                    st.session_state.ignored = ignored_list
                    st.rerun()
    else:
        st.markdown("""
        <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:12px;
                    padding:2rem; text-align:center;">
            <div style="font-size:1.5rem; margin-bottom:0.5rem;">&#10003;</div>
            <div style="font-weight:700; color:#065f46; font-size:1.05rem;">All campaigns are mapped or ignored</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

    # Ignored campaigns section
    if ignored_list:
        ignored_spend = raw_df[raw_df["raw_campaign_name"].isin(ignored_list)]["daily_value"].sum()
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
            <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em;">
                Excluded Campaigns
            </div>
            <div style="background:#fef2f2; color:#dc2626; padding:0.3rem 0.85rem; border-radius:50px;
                        font-size:0.8rem; font-weight:700;">
                ${ignored_spend:,.0f} excluded
            </div>
        </div>
        """, unsafe_allow_html=True)

        for ig_name in ignored_list:
            ig_spend = raw_df[raw_df["raw_campaign_name"] == ig_name]["daily_value"].sum()
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;
                            padding:0.6rem 0.85rem; font-family:monospace; font-size:0.85rem; color:#64748b;
                            display:flex; justify-content:space-between; align-items:center;">
                    <span>{ig_name}</span>
                    <span style="color:#ef4444; font-weight:700;">${ig_spend:,.0f}</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Unignore", key=f"unign_{ig_name}"):
                    ignored_list.remove(ig_name)
                    save_ignored(CLIENT, ignored_list)
                    st.session_state.ignored = ignored_list
                    st.rerun()

        st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

    # Full mapping table
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1rem;">
        Complete Mapping Table
    </div>
    """, unsafe_allow_html=True)

    all_map_rows = []
    for channel, channel_data in RAW_CAMPAIGNS.items():
        for camp in channel_data["campaigns"]:
            name = camp["raw_name"]
            mapped = camp["mapped_to"]
            m_type = camp.get("type", "tactic")
            if name in saved_mappings:
                m = saved_mappings[name]
                if isinstance(m, dict):
                    mapped = m["target"]
                    m_type = m["type"]
                else:
                    mapped = m
                    m_type = "tactic"
            status = "IGNORED" if name in ignored_list else ("MAPPED" if mapped else "UNMAPPED")
            all_map_rows.append({
                "Channel": channel.replace("_", " ").title(), "Campaign": name,
                "Maps To": mapped or "--", "Type": (m_type or "--").replace("_", " ").title(), "Status": status,
            })

    mapping_df = pd.DataFrame(all_map_rows)

    def hl_map(row):
        if row["Status"] == "UNMAPPED":
            return ["background-color: #fef2f2; color: #991b1b;"] * len(row)
        if row["Status"] == "IGNORED":
            return ["background-color: #f8fafc; color: #94a3b8;"] * len(row)
        return [""] * len(row)

    st.dataframe(mapping_df.style.apply(hl_map, axis=1), use_container_width=True, height=500)


# ==========================================================
# PAGE 5: Clean Export
# ==========================================================
elif page == "Clean Export":

    all_tactics = get_all_tactics(config)
    dep_vars = config.get("dependent_variables", [])
    ctx_vars = config.get("context_variables", [])
    window = config.get("export_window_months", 27)
    unmapped = get_unmapped_campaigns(raw_df, saved_mappings, ignored_list)
    clean_df, excluded_spend = build_clean_output(raw_df, saved_mappings, ignored_list, config)
    tactic_cols = [c for c in clean_df.columns if c in all_tactics]
    depvar_cols = [c for c in clean_df.columns if c in dep_vars]
    ctxvar_cols = [c for c in clean_df.columns if c in ctx_vars]
    total_spend = clean_df[tactic_cols].sum().sum() if tactic_cols else 0

    # Hero
    st.markdown("""
    <div style="background:linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border:1px solid #6ee7b7;
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">
            Clean Export
        </div>
        <div style="font-size:0.95rem; color:#047857; margin-top:0.35rem; font-weight:500;">
            MMM-ready output -- daily spend aggregated by standardized tactic
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.4);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Clean Export Page",
        "Generates the final MMM-ready CSV output: daily rows x standardized tactic columns. "
        "Applies the export window filter (e.g., last 27 months), aggregates mapped campaigns into tactic columns, "
        "adds dependent variable columns, adds context variable columns (aggregated by mean), excludes ignored campaigns, and saves timestamped snapshots for auditing.",
        functions=[
            "build_clean_output(raw_df, saved_mappings, ignored_list, config) -- aggregates raw data into clean daily format, returns (clean_df, excluded_spend)",
            "save_export_snapshot(client, clean_df) -- saves timestamped CSV snapshot to client's exports/ folder",
            "list_export_snapshots(client) -- returns sorted list of saved snapshot filenames",
            "get_unmapped_campaigns(raw_df, saved_mappings, ignored_list) -- checks for campaigns not yet mapped",
        ],
        data_flow="Raw data -> filter by export window -> group by date -> sum spend per tactic column + dep var columns -> "
                   "exclude ignored campaigns -> clean_df. Snapshot saved on button click for Data Audit comparison."
    )

    if unmapped:
        st.markdown(f"""
        <div style="background:#fffbeb; border:1px solid #fcd34d; border-left:4px solid #f59e0b;
                    border-radius:10px; padding:0.75rem 1.25rem; margin-bottom:1.5rem;">
            <span style="color:#92400e; font-size:0.9rem; font-weight:500;">{len(unmapped)} campaign(s) still unmapped -- excluded from export</span>
        </div>
        """, unsafe_allow_html=True)

    # KPI cards
    date_min = clean_df["date"].min() if len(clean_df) else "-"
    date_max = clean_df["date"].max() if len(clean_df) else "-"
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:1rem; margin-bottom:2rem;">
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg, #6366f1, #818cf8);"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Date Range</div>
            <div style="font-size:1.1rem; font-weight:800; color:#0f172a; margin-top:0.35rem;">{date_min}</div>
            <div style="font-size:0.8rem; color:#64748b;">to {date_max}</div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg, #3b82f6, #60a5fa);"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Rows</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">{len(clean_df)}</div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg, #8b5cf6, #a78bfa);"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Window</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">{window}<span style="font-size:1rem; color:#94a3b8;"> mo</span></div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg, #10b981, #34d399);"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Total Spend</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">${total_spend:,.0f}</div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg, #ef4444, #f87171);"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Excluded</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">${excluded_spend:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Column summary strip
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:0; margin-bottom:1.5rem;
                border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; background:#fff;">
        <div style="padding:0.85rem 1.25rem; text-align:center;">
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Tactic Columns</div>
            <div style="font-size:1.1rem; font-weight:800; color:#0f172a;">{len(tactic_cols)}</div>
        </div>
        <div style="padding:0.85rem 1.25rem; text-align:center; border-left:1px solid #f1f5f9;">
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Dep Var Columns</div>
            <div style="font-size:1.1rem; font-weight:800; color:#0f172a;">{len(depvar_cols)}</div>
        </div>
        <div style="padding:0.85rem 1.25rem; text-align:center; border-left:1px solid #f1f5f9;">
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Context Var Columns</div>
            <div style="font-size:1.1rem; font-weight:800; color:#0f172a;">{len(ctxvar_cols)}</div>
        </div>
        <div style="padding:0.85rem 1.25rem; text-align:center; border-left:1px solid #f1f5f9;">
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Total Columns</div>
            <div style="font-size:1.1rem; font-weight:800; color:#0f172a;">{len(clean_df.columns)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Preview
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1rem;">
        Export Preview
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(clean_df, use_container_width=True, height=500)

    # Actions
    st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        csv_data = clean_df.to_csv(index=False)
        st.download_button("Download Clean CSV", data=csv_data,
                           file_name="mmm_clean_output.csv", mime="text/csv",
                           use_container_width=True)
    st.markdown("")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Save Snapshot (for Audit)", use_container_width=True):
            save_export_snapshot(CLIENT, clean_df)
            st.success("Snapshot saved")


# ==========================================================
# PAGE: Spike Analysis (Dependent Variables)
# ==========================================================
elif page == "Spike Analysis":

    dep_vars = config.get("dependent_variables", [])
    clean_df, _ = build_clean_output(raw_df, saved_mappings, ignored_list, config)

    # Hero
    st.markdown("""
    <div style="background:linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%); border:1px solid #fdba74;
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">
            Spike Analysis
        </div>
        <div style="font-size:0.95rem; color:#9a3412; margin-top:0.35rem; font-weight:500;">
            Identify spikes in dependent variables to inform MMM priors
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.4);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Spike Analysis Page",
        "Displays daily time series for each dependent variable (e.g., acquisition, winbacks) so the analyst can "
        "visually identify spikes. Spike dates are used to set priors in the MMM (Recast). Hover over the chart "
        "to see exact date and value. Only dependent variables are shown here -- tactic spend spikes are not relevant for priors.",
        functions=[
            "build_clean_output(raw_df, saved_mappings, ignored_list, config) -- generates the clean daily export with dep var columns",
        ],
        data_flow="Clean export (date + dep var columns) -> filter by export window -> line chart per dep var. "
                   "Analyst hovers to find spike dates, then uses those dates when configuring priors in Recast."
    )

    if not dep_vars:
        st.markdown("""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:2.5rem; text-align:center;">
            <div style="font-size:1.3rem; color:#94a3b8; margin-bottom:0.5rem;">No Dependent Variables</div>
            <div style="font-size:0.9rem; color:#64748b;">Add dependent variables in Settings first</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        depvar_cols = [c for c in clean_df.columns if c in dep_vars]

        if not depvar_cols:
            st.info("No dependent variable data in the clean export yet. Map campaigns to dep vars first.")
        else:
            chart_df = clean_df[["date"] + depvar_cols].copy()
            chart_df["date"] = pd.to_datetime(chart_df["date"])
            chart_df = chart_df.sort_values("date")

            for dv in depvar_cols:
                series = chart_df[["date", dv]].copy()
                total = series[dv].sum()
                avg = series[dv].mean()
                peak_val = series[dv].max()
                peak_date = series.loc[series[dv].idxmax(), "date"].strftime("%Y-%m-%d") if peak_val > 0 else "--"

                st.markdown(f"""
                <div style="background:#fff; border:1px solid #e2e8f0; border-left:4px solid #f97316;
                            border-radius:12px; padding:1.25rem 1.5rem; margin-bottom:0.5rem;
                            box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
                        <div style="font-weight:700; font-size:1rem; color:#0f172a;">{dv.replace('_', ' ').title()}</div>
                        <div style="display:flex; gap:1.5rem;">
                            <div style="text-align:center;">
                                <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Total</div>
                                <div style="font-size:1rem; font-weight:700; color:#0f172a;">{total:,.0f}</div>
                            </div>
                            <div style="text-align:center;">
                                <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Daily Avg</div>
                                <div style="font-size:1rem; font-weight:700; color:#0f172a;">{avg:,.1f}</div>
                            </div>
                            <div style="text-align:center;">
                                <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Peak</div>
                                <div style="font-size:1rem; font-weight:700; color:#f97316;">{peak_val:,.0f}</div>
                            </div>
                            <div style="text-align:center;">
                                <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Peak Date</div>
                                <div style="font-size:1rem; font-weight:700; color:#f97316;">{peak_date}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.line_chart(series.set_index("date"), height=280, use_container_width=True)
                st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)


# ==========================================================
# PAGE 6: Data Audit
# ==========================================================
elif page == "Data Audit":

    snapshots = list_export_snapshots(CLIENT)
    dep_vars = config.get("dependent_variables", [])
    ctx_vars = config.get("context_variables", [])

    # Hero
    st.markdown("""
    <div style="background:linear-gradient(135deg, #faf5ff 0%, #ede9fe 100%); border:1px solid #c4b5fd;
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">
            Data Audit
        </div>
        <div style="font-size:0.95rem; color:#5b21b6; margin-top:0.35rem; font-weight:500;">
            Compare exports, check data stability, validate completeness
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.4);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Data Audit Page",
        "Compare the current export against a prior snapshot to detect changes. Checks for: "
        "new dates added, historical data that changed (date + column + old vs new value), "
        "missing dates in the range (gaps), and dependent variable health (zero/null values on non-excluded dates).",
        functions=[
            "list_export_snapshots(client) -- returns sorted list of saved snapshots",
            "load_export_snapshot(client, filename) -- loads a specific snapshot CSV as DataFrame",
            "compare_exports(current_df, previous_df) -- returns new_dates, changed_cells, unchanged_count",
            "check_date_continuity(clean_df) -- returns list of missing dates in the date range",
            "check_dependent_variables(clean_df, dep_var_names) -- returns dates where dep var is 0/null and exclude != TRUE",
            "build_clean_output(raw_df, saved_mappings, ignored_list, config) -- generates current clean export for comparison",
        ],
        data_flow="User picks two snapshots (or current vs saved) -> compare_exports() diffs them cell by cell -> "
                   "check_date_continuity() finds gaps -> check_dependent_variables() validates dep var health. "
                   "exclude_this_date column: data must still exist even if excluded; if dep var is 0 and not excluded, flag it."
    )

    if len(snapshots) < 1:
        st.markdown("""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:2.5rem; text-align:center;">
            <div style="font-size:1.3rem; color:#94a3b8; margin-bottom:0.5rem;">No Snapshots Yet</div>
            <div style="font-size:0.9rem; color:#64748b;">Go to Clean Export and save a snapshot first</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        clean_df, _ = build_clean_output(raw_df, saved_mappings, ignored_list, config)
        missing_dates = check_date_continuity(clean_df)
        dv_issues = check_dependent_variables(clean_df, dep_vars)

        # Check context var presence
        ctx_in_export = [c for c in ctx_vars if c in clean_df.columns]
        ctx_missing = [c for c in ctx_vars if c not in clean_df.columns]

        # Health status strip
        checks = [
            ("Date Continuity", "0 gaps" if not missing_dates else f"{len(missing_dates)} gaps", not missing_dates),
            ("Dep Var Health", "All healthy" if not dv_issues else f"{len(dv_issues)} issues", not dv_issues),
            ("Context Vars", f"{len(ctx_in_export)}/{len(ctx_vars)} present" if ctx_vars else "None configured", not ctx_missing),
            ("Snapshots", f"{len(snapshots)} saved", True),
        ]
        strip_html = '<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:0; margin-bottom:2rem; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; background:#fff;">'
        for idx, (lbl, val, ok) in enumerate(checks):
            dot = "#10b981" if ok else "#ef4444"
            bl = "" if idx == 0 else "border-left:1px solid #f1f5f9;"
            strip_html += f"""
            <div style="padding:1rem 1.25rem; {bl}">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
                    <div style="width:8px; height:8px; border-radius:50%; background:{dot};"></div>
                    <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">{lbl}</span>
                </div>
                <div style="font-size:0.9rem; font-weight:600; color:#0f172a;">{val}</div>
            </div>"""
        strip_html += "</div>"
        st.markdown(strip_html, unsafe_allow_html=True)

        # -- Date Continuity --
        st.markdown("""
        <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1rem;">
            Date Continuity Check
        </div>
        """, unsafe_allow_html=True)
        if missing_dates:
            st.markdown(f"""
            <div style="background:#fef2f2; border:1px solid #fca5a5; border-left:4px solid #ef4444;
                        border-radius:12px; padding:1rem 1.25rem; margin-bottom:1rem;">
                <span style="font-weight:700; color:#991b1b;">{len(missing_dates)} missing date(s) detected</span>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(pd.DataFrame({"missing_date": missing_dates}), use_container_width=True)
        else:
            st.markdown("""
            <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:12px;
                        padding:1.25rem; text-align:center;">
                <span style="font-weight:700; color:#065f46;">&#10003; No missing dates -- all days continuous</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

        # -- Dep Var Health --
        st.markdown("""
        <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1rem;">
            Dependent Variable Health
        </div>
        """, unsafe_allow_html=True)
        if dv_issues:
            st.markdown(f"""
            <div style="background:#fef2f2; border:1px solid #fca5a5; border-left:4px solid #ef4444;
                        border-radius:12px; padding:1rem 1.25rem; margin-bottom:1rem;">
                <span style="font-weight:700; color:#991b1b;">{len(dv_issues)} issue(s)</span>
                <span style="color:#991b1b;"> -- dep vars should have values every non-excluded day</span>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(dv_issues), use_container_width=True, height=300)
        else:
            st.markdown("""
            <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:12px;
                        padding:1.25rem; text-align:center;">
                <span style="font-weight:700; color:#065f46;">&#10003; All dependent variables have values every day</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

        # -- Context Variable Health --
        st.markdown("""
        <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1rem;">
            Context Variable Health
        </div>
        """, unsafe_allow_html=True)
        if ctx_missing:
            st.markdown(f"""
            <div style="background:#fef2f2; border:1px solid #fca5a5; border-left:4px solid #ef4444;
                        border-radius:12px; padding:1rem 1.25rem; margin-bottom:1rem;">
                <span style="font-weight:700; color:#991b1b;">{len(ctx_missing)} context variable(s) missing from export:</span>
                <span style="color:#991b1b;"> {', '.join(ctx_missing)}</span>
            </div>
            """, unsafe_allow_html=True)
        elif not ctx_vars:
            st.markdown("""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px;
                        padding:1.25rem; text-align:center;">
                <span style="font-weight:600; color:#64748b;">No context variables configured</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            cv_summary = ""
            for cv in ctx_in_export:
                cv_mean = clean_df[cv].mean()
                cv_summary += f'<span style="background:#fef3c7; color:#92400e; padding:0.2rem 0.6rem; border-radius:6px; font-size:0.8rem; font-weight:500; font-family:monospace; margin:0.15rem;">{cv} (avg: {cv_mean:.2f})</span> '
            st.markdown(f"""
            <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:12px;
                        padding:1.25rem;">
                <div style="font-weight:700; color:#065f46; margin-bottom:0.5rem;">&#10003; All {len(ctx_in_export)} context variable(s) present in export</div>
                <div>{cv_summary}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

        # -- Export Comparison --
        st.markdown("""
        <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1rem;">
            Export Comparison
        </div>
        """, unsafe_allow_html=True)

        if len(snapshots) >= 1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px;
                            padding:0.75rem 1rem; font-size:0.85rem; color:#166534; font-weight:600;">
                    Current: Live data (generated now)
                </div>
                """, unsafe_allow_html=True)
            with col2:
                prev_file = st.selectbox("Compare against", snapshots, key="audit_prev")

            if prev_file:
                previous_df = load_export_snapshot(CLIENT, prev_file)
                results = compare_exports(clean_df, previous_df)
                n_changes = len(results["changed_cells"])

                st.markdown(f"""
                <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:1rem; margin:1.5rem 0;">
                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                                box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
                        <div style="position:absolute; top:0; left:0; right:0; height:4px; background:#10b981;"></div>
                        <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">New Dates</div>
                        <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">{len(results["new_dates"])}</div>
                    </div>
                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                                box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
                        <div style="position:absolute; top:0; left:0; right:0; height:4px; background:#3b82f6;"></div>
                        <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Historical Checked</div>
                        <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">{results["common_dates_count"]}</div>
                    </div>
                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                                box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
                        <div style="position:absolute; top:0; left:0; right:0; height:4px; background:{'#ef4444' if n_changes > 0 else '#10b981'};"></div>
                        <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Changes Found</div>
                        <div style="font-size:1.8rem; font-weight:800; color:{'#dc2626' if n_changes > 0 else '#0f172a'}; margin-top:0.25rem;">{n_changes}</div>
                    </div>
                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem;
                                box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
                        <div style="position:absolute; top:0; left:0; right:0; height:4px; background:#10b981;"></div>
                        <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#94a3b8;">Stable Days</div>
                        <div style="font-size:1.8rem; font-weight:800; color:#0f172a; margin-top:0.25rem;">{results["unchanged_count"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if results["new_dates"]:
                    st.markdown("""
                    <div style="font-size:0.95rem; font-weight:700; color:#0f172a; margin-bottom:0.75rem;">New dates added</div>
                    """, unsafe_allow_html=True)
                    new_rows = clean_df[clean_df["date"].isin(results["new_dates"])]
                    st.dataframe(new_rows, use_container_width=True, height=200)

                if results["changed_cells"]:
                    st.markdown(f"""
                    <div style="background:#fef2f2; border:1px solid #fca5a5; border-left:4px solid #ef4444;
                                border-radius:12px; padding:1rem 1.25rem; margin-top:1rem; margin-bottom:1rem;">
                        <span style="font-weight:700; color:#991b1b;">Historical data changed! {n_changes} cell(s) differ from prior export.</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame(results["changed_cells"]), use_container_width=True, height=300)
                else:
                    st.markdown("""
                    <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:12px;
                                padding:1.25rem; text-align:center; margin-top:1rem;">
                        <span style="font-weight:700; color:#065f46;">&#10003; Historical data is stable -- no changes detected</span>
                    </div>
                    """, unsafe_allow_html=True)

                if results["removed_dates"]:
                    st.warning(f"{len(results['removed_dates'])} date(s) present in prior export but missing from current (may be window change)")
        else:
            st.info("Need at least one prior snapshot to compare against.")


# ==========================================================
# PAGE 7: Settings
# ==========================================================
elif page == "Settings":

    # Hero
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); border:1px solid #cbd5e1;
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">
            Settings
        </div>
        <div style="font-size:0.95rem; color:#475569; margin-top:0.35rem; font-weight:500;">
            Configuration for {CLIENT.replace('_', ' ').title()}
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.5);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Settings Page",
        "Client-level configuration: manage standardized tactic names (organized by channel group), "
        "dependent variable names, context variable names (e.g., price, promo_flag), and the export window (rolling months). All settings persisted to config.json.",
        functions=[
            "load_client_config(client) -- loads config.json with tactics, dep vars, window, etc.",
            "save_client_config(client, config) -- saves config.json",
            "get_all_tactics(config) -- returns flat list of all tactic names across channel groups",
        ],
        data_flow="User edits tactics/dep vars/window -> save_client_config() writes to clients/{name}/config.json. "
                   "Tactic names are organized by channel group (e.g., paid_social: [meta_prospecting, meta_retargeting]). "
                   "These names appear as dropdown options in Campaign Mapping and as column headers in Clean Export."
    )

    # -- Export Window --
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1rem;">
        Export Window
    </div>
    """, unsafe_allow_html=True)
    window = st.number_input("Rolling window (months)", min_value=1, max_value=120,
                             value=config.get("export_window_months", 27), key="window_input")
    if window != config.get("export_window_months", 27):
        config["export_window_months"] = window
        save_client_config(CLIENT, config)
        st.session_state.config = config
        st.success(f"Window set to {window} months")

    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

    # -- Tactic Name Management --
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Standardized Tactic Names
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
        Master list of tactic names organized by channel group
    </div>
    """, unsafe_allow_html=True)

    tactics = config.get("tactics", DEFAULT_TACTICS)
    changed = False

    for group in list(tactics.keys()):
        group_tactics = tactics[group]
        with st.expander(f"{group.replace('_', ' ').title()} -- {len(group_tactics)} tactics", expanded=False):
            for t in group_tactics:
                tc1, tc2 = st.columns([5, 1])
                with tc1:
                    st.markdown(f'<span style="font-family:monospace; font-size:0.85rem; color:#334155;">{t}</span>', unsafe_allow_html=True)
                with tc2:
                    if st.button("x", key=f"rm_{group}_{t}"):
                        tactics[group].remove(t)
                        changed = True

    # Add new tactic
    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
    ac1, ac2, ac3 = st.columns([2, 3, 1])
    with ac1:
        add_group = st.selectbox("Channel group", list(tactics.keys()) + ["(new group)"], key="add_group")
    with ac2:
        if add_group == "(new group)":
            new_group_name = st.text_input("New group name", key="new_group_name")
            add_name = st.text_input("Tactic name", key="add_tactic_name2")
        else:
            add_name = st.text_input("Tactic name", key="add_tactic_name")
    with ac3:
        st.markdown("")
        if st.button("Add", key="btn_add_tactic"):
            if add_group == "(new group)" and new_group_name:
                group_key = new_group_name.strip().lower().replace(" ", "_")
                tactics[group_key] = [add_name.strip()]
                changed = True
            elif add_name and add_name.strip():
                if add_name.strip() not in tactics.get(add_group, []):
                    tactics.setdefault(add_group, []).append(add_name.strip())
                    changed = True

    if changed:
        config["tactics"] = tactics
        save_client_config(CLIENT, config)
        st.session_state.config = config
        st.rerun()

    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

    # -- Dependent Variable Management --
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Dependent Variables
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
        Standard names for outcome variables (acquisition, retention, etc.)
    </div>
    """, unsafe_allow_html=True)

    dep_vars = config.get("dependent_variables", DEFAULT_DEP_VARS)
    dv_changed = False

    for dv in dep_vars:
        dv1, dv2 = st.columns([5, 1])
        with dv1:
            st.markdown(f'<span style="display:inline-block; background:#faf5ff; color:#7c3aed; padding:0.3rem 0.75rem; border-radius:6px; font-size:0.85rem; font-weight:500; font-family:monospace;">{dv}</span>', unsafe_allow_html=True)
        with dv2:
            if st.button("x", key=f"rm_dv_{dv}"):
                dep_vars.remove(dv)
                dv_changed = True

    dc1, dc2 = st.columns([4, 1])
    with dc1:
        new_dv = st.text_input("New dependent variable name", key="new_dv_name")
    with dc2:
        st.markdown("")
        if st.button("Add", key="btn_add_dv"):
            if new_dv and new_dv.strip() and new_dv.strip() not in dep_vars:
                dep_vars.append(new_dv.strip())
                dv_changed = True

    if dv_changed:
        config["dependent_variables"] = dep_vars
        save_client_config(CLIENT, config)
        st.session_state.config = config
        st.rerun()

    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

    # -- Context Variable Management --
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Context Variables
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
        Variables like price, promo flags, or other non-spend/non-outcome data included in the MMM export (aggregated by mean)
    </div>
    """, unsafe_allow_html=True)

    ctx_vars = config.get("context_variables", list(DEFAULT_CONTEXT_VARS))
    cv_changed = False

    for cv in ctx_vars:
        cv1, cv2 = st.columns([5, 1])
        with cv1:
            st.markdown(f'<span style="display:inline-block; background:#fef3c7; color:#92400e; padding:0.3rem 0.75rem; border-radius:6px; font-size:0.85rem; font-weight:500; font-family:monospace;">{cv}</span>', unsafe_allow_html=True)
        with cv2:
            if st.button("x", key=f"rm_cv_{cv}"):
                ctx_vars.remove(cv)
                cv_changed = True

    cv1, cv2 = st.columns([4, 1])
    with cv1:
        new_cv = st.text_input("New context variable name", key="new_cv_name")
    with cv2:
        st.markdown("")
        if st.button("Add", key="btn_add_cv"):
            if new_cv and new_cv.strip() and new_cv.strip() not in ctx_vars:
                ctx_vars.append(new_cv.strip())
                cv_changed = True

    if cv_changed:
        config["context_variables"] = ctx_vars
        save_client_config(CLIENT, config)
        st.session_state.config = config
        st.rerun()

    st.markdown('<div style="height:2rem;"></div>', unsafe_allow_html=True)

    # Reset
    if st.button("Reset to Defaults", key="btn_reset"):
        config["tactics"] = {k: list(v) for k, v in DEFAULT_TACTICS.items()}
        config["dependent_variables"] = list(DEFAULT_DEP_VARS)
        config["context_variables"] = list(DEFAULT_CONTEXT_VARS)
        config["export_window_months"] = 27
        save_client_config(CLIENT, config)
        st.session_state.config = config
        st.rerun()


# ==========================================================
# PAGE 8: Data Freshness
# ==========================================================
elif page == "Data Freshness":

    # Hero
    freshness = check_data_freshness(raw_df, saved_mappings, ignored_list, config)
    source_fresh = check_source_freshness(raw_df)
    stale_count = sum(1 for f in freshness if f["status"] in ("stale", "no_data"))
    warn_count = sum(1 for f in freshness if f["status"] == "warning")

    if stale_count > 0:
        hero_bg = "linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)"
        hero_border = "#fca5a5"
        hero_sub = f"{stale_count} tactic(s)/variable(s) have stale or missing data"
        hero_sub_color = "#991b1b"
    elif warn_count > 0:
        hero_bg = "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)"
        hero_border = "#fcd34d"
        hero_sub = f"{warn_count} tactic(s)/variable(s) may need attention"
        hero_sub_color = "#92400e"
    else:
        hero_bg = "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)"
        hero_border = "#6ee7b7"
        hero_sub = "All data sources are current"
        hero_sub_color = "#047857"

    st.markdown(f"""
    <div style="background:{hero_bg}; border:1px solid {hero_border};
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">
            Data Freshness
        </div>
        <div style="font-size:0.95rem; color:{hero_sub_color}; margin-top:0.35rem; font-weight:500;">
            {hero_sub}
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.4);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Data Freshness Page",
        "Monitors data recency across all sources, tactics, and dependent variables. "
        "Flags stale data (no recent updates) so the team knows if a pipeline failed or a CSV was not uploaded. "
        "Critical for ensuring the MMM export does not contain trailing zeros from missing data.",
        functions=[
            "check_data_freshness(raw_df, saved_mappings, ignored_list, config) -- per tactic/dep var: latest non-zero date, days stale, status (current/warning/stale/no_data)",
            "check_source_freshness(raw_df) -- per channel/source: latest date and staleness",
        ],
        data_flow="Raw data -> group by channel/tactic -> find max date with non-zero value -> compare to today -> "
                   "classify as current (0-2 days), warning (3-5 days), or stale (6+ days). "
                   "Source-level checks run on raw channel data; tactic-level checks run on mapped data only."
    )

    # Source-level freshness
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Data Source Status
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
        Latest data date per ingestion source -- stale sources mean the pipeline needs attention
    </div>
    """, unsafe_allow_html=True)

    src_html = '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:1rem; margin-bottom:2rem;">'
    for sf in source_fresh:
        if sf["status"] == "current":
            dot = "#10b981"; bg = "#ecfdf5"; border = "#a7f3d0"; label_color = "#065f46"
        elif sf["status"] == "warning":
            dot = "#f59e0b"; bg = "#fffbeb"; border = "#fcd34d"; label_color = "#92400e"
        else:
            dot = "#ef4444"; bg = "#fef2f2"; border = "#fca5a5"; label_color = "#991b1b"
        src_html += f"""
        <div style="background:{bg}; border:1px solid {border}; border-radius:14px; padding:1.25rem;
                    position:relative; overflow:hidden;">
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                <div style="width:10px; height:10px; border-radius:50%; background:{dot};"></div>
                <span style="font-weight:700; color:#0f172a; font-size:0.9rem; text-transform:capitalize;">{sf['channel'].replace('_', ' ')}</span>
                <span style="font-size:0.7rem; color:#94a3b8; margin-left:auto;">{sf['source_type']}</span>
            </div>
            <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{sf['latest_date']}</div>
            <div style="display:flex; justify-content:space-between; margin-top:0.4rem;">
                <span style="font-size:0.75rem; color:{label_color}; font-weight:600;">{sf['days_stale']}d ago</span>
                <span style="font-size:0.75rem; color:#94a3b8;">{sf['campaign_count']} campaigns</span>
            </div>
        </div>"""
    src_html += "</div>"
    st.markdown(src_html, unsafe_allow_html=True)

    # Tactic-level freshness
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Tactic, Dep Var &amp; Context Var Freshness
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
        Last date with non-zero data for each MMM column -- if not current, the export will have zeros at the end
    </div>
    """, unsafe_allow_html=True)

    # Build HTML table
    tbl = """<div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
    <table style="width:100%; border-collapse:collapse; font-size:0.85rem;">
    <thead>
        <tr style="background:#f8fafc; border-bottom:2px solid #e2e8f0;">
            <th style="padding:0.85rem 1.25rem; text-align:left; font-weight:700; color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em;">Status</th>
            <th style="padding:0.85rem 1.25rem; text-align:left; font-weight:700; color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em;">Name</th>
            <th style="padding:0.85rem 1.25rem; text-align:left; font-weight:700; color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em;">Type</th>
            <th style="padding:0.85rem 1.25rem; text-align:left; font-weight:700; color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em;">Latest Date</th>
            <th style="padding:0.85rem 1.25rem; text-align:left; font-weight:700; color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em;">Days Stale</th>
            <th style="padding:0.85rem 1.25rem; text-align:left; font-weight:700; color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em;">Sources</th>
        </tr>
    </thead><tbody>"""

    for f in freshness:
        if f["status"] == "current":
            dot = "#10b981"; row_bg = ""; stale_txt = f["days_stale"]
        elif f["status"] == "warning":
            dot = "#f59e0b"; row_bg = "background:#fffbeb;"; stale_txt = f["days_stale"]
        elif f["status"] == "stale":
            dot = "#ef4444"; row_bg = "background:#fef2f2;"; stale_txt = f"{f['days_stale']} (!)"
        else:
            dot = "#94a3b8"; row_bg = "background:#f8fafc;"; stale_txt = "--"
        if f["type"] == "context_variable":
            type_badge_bg = "#fef3c7"; type_badge_color = "#92400e"
        elif f["type"] == "dependent_variable":
            type_badge_bg = "#faf5ff"; type_badge_color = "#7c3aed"
        else:
            type_badge_bg = "#eff6ff"; type_badge_color = "#1e40af"
        tbl += f"""<tr style="{row_bg} border-bottom:1px solid #f1f5f9;">
            <td style="padding:0.75rem 1.25rem;"><div style="width:10px; height:10px; border-radius:50%; background:{dot};"></div></td>
            <td style="padding:0.75rem 1.25rem; font-weight:600; color:#0f172a;">{f['name']}</td>
            <td style="padding:0.75rem 1.25rem;"><span style="background:{type_badge_bg}; color:{type_badge_color}; padding:0.15rem 0.5rem; border-radius:50px; font-size:0.7rem; font-weight:600;">{f['type'].replace('_',' ').title()}</span></td>
            <td style="padding:0.75rem 1.25rem; color:#334155; font-family:monospace;">{f['latest_date']}</td>
            <td style="padding:0.75rem 1.25rem; font-weight:700; color:{'#dc2626' if f['status'] in ('stale','no_data') else '#0f172a'};">{stale_txt}</td>
            <td style="padding:0.75rem 1.25rem; color:#64748b;">{f['source_campaigns']}</td>
        </tr>"""

    tbl += "</tbody></table></div>"
    st.markdown(tbl, unsafe_allow_html=True)


# ==========================================================
# PAGE 9: Onboarding (Bulk Campaign Mapping)
# ==========================================================
elif page == "Onboarding":

    all_tactics = get_all_tactics(config)
    dep_vars = config.get("dependent_variables", [])
    all_camps = get_all_campaigns_for_onboarding(raw_df, saved_mappings, ignored_list)
    onboarding_state = load_onboarding_state(CLIENT)
    is_onboarded = onboarding_state.get("completed", False)

    total = len(all_camps)
    mapped_n = sum(1 for c in all_camps if c["status"] == "mapped")
    ignored_n = sum(1 for c in all_camps if c["status"] == "ignored")
    unmapped_n = sum(1 for c in all_camps if c["status"] == "unmapped")
    pct = int((mapped_n + ignored_n) / total * 100) if total > 0 else 0

    # Hero
    if is_onboarded:
        hero_bg = "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)"
        hero_border = "#6ee7b7"
        hero_sub = "Onboarding complete -- use Campaign Mapping for incremental updates"
        hero_sub_color = "#047857"
    else:
        hero_bg = "linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)"
        hero_border = "#c7d2fe"
        hero_sub = "Map all campaigns to standardized names to get started"
        hero_sub_color = "#4338ca"

    st.markdown(f"""
    <div style="background:{hero_bg}; border:1px solid {hero_border};
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">
            Campaign Onboarding
        </div>
        <div style="font-size:0.95rem; color:{hero_sub_color}; margin-top:0.35rem; font-weight:500;">
            {hero_sub}
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.4);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Onboarding Page",
        "Bulk campaign mapping interface for initial client setup. Shows ALL campaigns across all sources "
        "with multi-select checkboxes, search/filter by name, and filter by channel. Allows mapping many campaigns "
        "at once to speed up the initial tagging process. Once all campaigns are mapped or ignored, onboarding is complete.",
        functions=[
            "get_all_campaigns_for_onboarding(raw_df, saved_mappings, ignored_list) -- returns every campaign with spend, dates, status (mapped/unmapped/ignored), current mapping",
            "save_mappings(client, mappings) -- persists updated mappings after bulk tagging",
            "save_ignored(client, ignored_list) -- persists updated ignore list after bulk ignore",
            "load_onboarding_state(client) / save_onboarding_state(client, state) -- tracks onboarding completion",
        ],
        data_flow="All raw campaigns -> display with filters (channel, status, search text) -> user selects multiple -> "
                   "applies tactic or dep var mapping in bulk -> save_mappings(). Can also bulk-ignore selected campaigns. "
                   "Progress bar shows (mapped + ignored) / total. Mark complete button saves onboarding state."
    )

    # Progress bar
    bar_color = "#10b981" if pct == 100 else "#6366f1"
    st.markdown(f"""
    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem;
                margin-bottom:2rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
        <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.75rem;">
            <div style="font-weight:800; color:#0f172a; font-size:1.1rem;">Mapping Progress</div>
            <div style="font-size:1.5rem; font-weight:800; color:{bar_color};">{pct}%</div>
        </div>
        <div style="background:#f1f5f9; border-radius:8px; height:12px; overflow:hidden; margin-bottom:0.75rem;">
            <div style="background:{bar_color}; width:{pct}%; height:100%; border-radius:8px; transition:width 0.5s ease;"></div>
        </div>
        <div style="display:flex; gap:2rem; font-size:0.8rem;">
            <span style="color:#10b981; font-weight:600;">{mapped_n} mapped</span>
            <span style="color:#94a3b8; font-weight:600;">{ignored_n} ignored</span>
            <span style="color:#f59e0b; font-weight:600;">{unmapped_n} remaining</span>
            <span style="color:#64748b;">{total} total</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mark onboarding complete
    if unmapped_n == 0 and not is_onboarded:
        if st.button("Mark Onboarding Complete", use_container_width=True, key="btn_complete_onboard"):
            save_onboarding_state(CLIENT, {"completed": True})
            st.rerun()
    elif is_onboarded:
        st.markdown("""
        <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:12px;
                    padding:1rem; text-align:center; margin-bottom:1.5rem;">
            <span style="font-weight:700; color:#065f46;">&#10003; Onboarding is complete</span>
        </div>
        """, unsafe_allow_html=True)

    # Filters
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:1rem;">
        Campaign List
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns([2, 2, 2, 4])
    with f1:
        ob_channel = st.selectbox("Channel", ["All"] + sorted(set(c["channel"] for c in all_camps)), key="ob_ch")
    with f2:
        ob_status = st.selectbox("Status", ["All", "Unmapped", "Mapped", "Ignored"], key="ob_status")
    with f3:
        ob_source = st.selectbox("Source", ["All", "api", "csv"], key="ob_source")
    with f4:
        ob_search = st.text_input("Search campaigns (contains)", key="ob_search", placeholder="e.g. demand_gen, brand, retarget...")

    # Filter campaigns
    filtered = all_camps.copy()
    if ob_channel != "All":
        filtered = [c for c in filtered if c["channel"] == ob_channel]
    if ob_status != "All":
        filtered = [c for c in filtered if c["status"] == ob_status.lower()]
    if ob_source != "All":
        filtered = [c for c in filtered if c["source_type"] == ob_source]
    if ob_search:
        search_lower = ob_search.lower()
        filtered = [c for c in filtered if search_lower in c["raw_name"].lower()]

    st.markdown(f'<div style="font-size:0.85rem; color:#64748b; margin-bottom:1rem;">Showing {len(filtered)} of {total} campaigns</div>', unsafe_allow_html=True)

    # Bulk action section
    if filtered:
        # Build campaign display with checkboxes
        st.markdown("""
        <div style="font-size:0.95rem; font-weight:700; color:#0f172a; margin-bottom:0.75rem;">
            Select campaigns and assign a mapping
        </div>
        """, unsafe_allow_html=True)

        # Mapping controls at top
        mc1, mc2, mc3, mc4 = st.columns([2, 3, 2, 1])
        with mc1:
            bulk_type = st.selectbox("Mapping Type", ["Spend Tactic", "Dependent Variable", "Context Variable"], key="ob_bulk_type")
        with mc2:
            if bulk_type == "Spend Tactic":
                bulk_target = st.selectbox("Target", ["-- Select --"] + all_tactics, key="ob_bulk_target")
            elif bulk_type == "Dependent Variable":
                bulk_target = st.selectbox("Target", ["-- Select --"] + dep_vars, key="ob_bulk_target_dv")
            else:
                ctx_vars = config.get("context_variables", [])
                bulk_target = st.selectbox("Target", ["-- Select --"] + ctx_vars, key="ob_bulk_target_cv")
        with mc3:
            if st.button("Apply to Selected", key="ob_apply", use_container_width=True):
                if bulk_target != "-- Select --":
                    selected_keys = [k for k, v in st.session_state.items() if k.startswith("ob_chk_") and v]
                    type_lookup_ob = {"Spend Tactic": "tactic", "Dependent Variable": "dependent_variable", "Context Variable": "context_variable"}
                    m_type = type_lookup_ob[bulk_type]
                    for k in selected_keys:
                        camp_name = k.replace("ob_chk_", "")
                        saved_mappings[camp_name] = {"target": bulk_target, "type": m_type}
                    if selected_keys:
                        save_mappings(CLIENT, saved_mappings)
                        st.session_state.mappings = saved_mappings
                        st.rerun()
        with mc4:
            if st.button("Ignore Sel.", key="ob_ignore", use_container_width=True):
                selected_keys = [k for k, v in st.session_state.items() if k.startswith("ob_chk_") and v]
                for k in selected_keys:
                    camp_name = k.replace("ob_chk_", "")
                    if camp_name not in ignored_list:
                        ignored_list.append(camp_name)
                if selected_keys:
                    save_ignored(CLIENT, ignored_list)
                    st.session_state.ignored = ignored_list
                    st.rerun()

        # Campaign rows with checkboxes
        for camp in filtered:
            status_dot = {"mapped": "#10b981", "ignored": "#94a3b8", "unmapped": "#f59e0b"}.get(camp["status"], "#94a3b8")
            status_bg = {"unmapped": "background:#fffbeb;", "ignored": "background:#f8fafc;"}.get(camp["status"], "")

            r1, r2 = st.columns([0.3, 5])
            with r1:
                st.checkbox("", key=f"ob_chk_{camp['raw_name']}", label_visibility="collapsed")
            with r2:
                st.markdown(f"""
                <div style="{status_bg} border:1px solid #e2e8f0; border-radius:10px; padding:0.85rem 1.1rem; margin-bottom:0.25rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <div style="width:8px; height:8px; border-radius:50%; background:{status_dot};"></div>
                            <span style="font-family:monospace; font-size:0.85rem; color:#334155; font-weight:500;">{camp['raw_name']}</span>
                        </div>
                        <div style="display:flex; gap:0.4rem;">
                            <span style="background:#f1f5f9; color:#64748b; padding:0.1rem 0.5rem; border-radius:50px; font-size:0.65rem; font-weight:600;">{camp['channel']}</span>
                            <span style="background:#f1f5f9; color:#64748b; padding:0.1rem 0.5rem; border-radius:50px; font-size:0.65rem; font-weight:600;">{camp['source_type']}</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:1.5rem; font-size:0.75rem; color:#64748b;">
                        <span>Spend: <strong style="color:#0f172a;">${camp['total_value']:,.0f}</strong></span>
                        <span>Days: <strong style="color:#0f172a;">{camp['days_active']}</strong></span>
                        <span>{camp['first_date']} to {camp['last_date']}</span>
                        <span>Maps to: <strong style="color:{'#10b981' if camp['current_mapping'] != '--' else '#f59e0b'};">{camp['current_mapping']}</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px;
                    padding:2rem; text-align:center;">
            <div style="color:#64748b;">No campaigns match your filters</div>
        </div>
        """, unsafe_allow_html=True)


# ==========================================================
# PAGE 10: Client Dashboard (Read-Only, Premium SaaS)
# ==========================================================
elif page == "Client Dashboard":

    all_tactics = get_all_tactics(config)
    dep_vars = config.get("dependent_variables", [])
    ctx_vars = config.get("context_variables", [])
    window = config.get("export_window_months", 27)
    unmapped = get_unmapped_campaigns(raw_df, saved_mappings, ignored_list)
    clean_df, excluded_spend = build_clean_output(raw_df, saved_mappings, ignored_list, config)
    tactic_cols = [c for c in clean_df.columns if c in all_tactics]
    depvar_cols = [c for c in clean_df.columns if c in dep_vars]
    ctxvar_cols = [c for c in clean_df.columns if c in ctx_vars]
    total_spend = clean_df[tactic_cols].sum().sum() if tactic_cols else 0
    total_campaigns = sum(len(ch["campaigns"]) for ch in RAW_CAMPAIGNS.values())
    mapped_count = len(saved_mappings)
    date_min = clean_df["date"].min() if len(clean_df) else "-"
    date_max = clean_df["date"].max() if len(clean_df) else "-"
    missing_dates = check_date_continuity(clean_df)
    dv_issues = check_dependent_variables(clean_df, dep_vars)
    health_ok = not unmapped and not missing_dates and not dv_issues

    # ---- Hero header with gradient ----
    health_gradient = "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)" if health_ok else "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)"
    health_border = "#10b981" if health_ok else "#f59e0b"
    health_icon = "&#10003;" if health_ok else "!"
    health_icon_bg = "#10b981" if health_ok else "#f59e0b"
    health_icon_color = "#fff"
    health_text = "All systems go -- your MMM data is complete and healthy" if health_ok else f"{len(unmapped)} unmapped campaign(s) and {len(missing_dates) + len(dv_issues)} data issue(s) need attention"
    health_text_color = "#065f46" if health_ok else "#92400e"

    st.markdown(f"""
    <div style="background:{health_gradient}; border:1px solid {health_border}; border-radius:16px;
                padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="display:flex; align-items:center; gap:1rem;">
            <div style="width:48px; height:48px; border-radius:50%; background:{health_icon_bg};
                        display:flex; align-items:center; justify-content:center;
                        font-size:1.5rem; color:{health_icon_color}; font-weight:bold; flex-shrink:0;">
                {health_icon}
            </div>
            <div>
                <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em; line-height:1.2;">
                    {CLIENT.replace('_', ' ').title()} -- MMM Data Overview
                </div>
                <div style="font-size:0.95rem; color:{health_text_color}; margin-top:0.25rem; font-weight:500;">
                    {health_text}
                </div>
            </div>
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.3);"></div>
        <div style="position:absolute; bottom:-30px; right:60px; width:80px; height:80px;
                    border-radius:50%; background:rgba(255,255,255,0.2);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Client Dashboard Page",
        "Read-only view designed for clients to visualize their MMM data health and campaign status. "
        "No controls -- just visualization. Shows health banner, KPI cards, spend breakdown by tactic, "
        "dependent variable summary, data quality checks, and tabbed campaign tables (all/mapped/unmapped/excluded).",
        functions=[
            "build_clean_output(raw_df, saved_mappings, ignored_list, config) -- generates clean export for KPI calculations",
            "get_unmapped_campaigns(raw_df, saved_mappings, ignored_list) -- counts unmapped campaigns for health check",
            "check_date_continuity(clean_df) -- checks for date gaps in the export",
            "check_dependent_variables(clean_df, dep_vars) -- validates dep var health",
        ],
        data_flow="All internal data -> read-only aggregation -> display as KPIs, charts, and tables. "
                   "Health banner turns green when: no unmapped campaigns, no date gaps, no dep var issues. "
                   "Client sees total spend, mapping coverage, data window, excluded spend, and quality status."
    )

    # ---- KPI row ----
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:1rem; margin-bottom:2rem;">
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px;
                        background:linear-gradient(90deg, #6366f1, #818cf8);"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;
                        color:#94a3b8; margin-bottom:0.5rem;">Total Media Spend</div>
            <div style="font-size:2rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">${total_spend:,.0f}</div>
            <div style="font-size:0.8rem; color:#64748b; margin-top:0.25rem;">{date_min} to {date_max}</div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px;
                        background:linear-gradient(90deg, #10b981, #34d399);"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;
                        color:#94a3b8; margin-bottom:0.5rem;">Campaigns Mapped</div>
            <div style="font-size:2rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">{mapped_count}<span style="font-size:1rem; color:#94a3b8; font-weight:500;">/{total_campaigns}</span></div>
            <div style="font-size:0.8rem; color:#64748b; margin-top:0.25rem;">{len(tactic_cols)} tactics + {len(depvar_cols)} dep vars + {len(ctxvar_cols)} context</div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px;
                        background:linear-gradient(90deg, #3b82f6, #60a5fa);"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;
                        color:#94a3b8; margin-bottom:0.5rem;">Data Window</div>
            <div style="font-size:2rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">{len(clean_df)} <span style="font-size:1rem; color:#94a3b8; font-weight:500;">days</span></div>
            <div style="font-size:0.8rem; color:#64748b; margin-top:0.25rem;">Rolling {window}-month window</div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px;
                        background:linear-gradient(90deg, #ef4444, #f87171);"></div>
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;
                        color:#94a3b8; margin-bottom:0.5rem;">Excluded Spend</div>
            <div style="font-size:2rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">${excluded_spend:,.0f}</div>
            <div style="font-size:0.8rem; color:#64748b; margin-top:0.25rem;">{len(ignored_list)} campaign(s) excluded</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Data quality strip ----
    ctx_in_export = [c for c in ctx_vars if c in clean_df.columns]
    dq_items = []
    dq_items.append(("Date Continuity", "0 gaps" if not missing_dates else f"{len(missing_dates)} gaps", not missing_dates))
    dq_items.append(("Dep Var Health", "All healthy" if not dv_issues else f"{len(dv_issues)} issues", not dv_issues))
    dq_items.append(("Context Vars", f"{len(ctx_in_export)}/{len(ctx_vars)} in export" if ctx_vars else "N/A", len(ctx_in_export) == len(ctx_vars)))
    dq_items.append(("Campaign Coverage", "100%" if not unmapped else f"{mapped_count}/{total_campaigns}", not unmapped))
    dq_items.append(("Excluded Data", f"{len(ignored_list)} intentional" if ignored_list else "None", True))

    dq_html = '<div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:0; margin-bottom:2rem; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; background:#fff;">'
    for idx, (dq_label, dq_value, dq_ok) in enumerate(dq_items):
        dot_color = "#10b981" if dq_ok else "#ef4444"
        border_left = "" if idx == 0 else "border-left:1px solid #f1f5f9;"
        dq_html += f"""
        <div style="padding:1rem 1.25rem; {border_left}">
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
                <div style="width:8px; height:8px; border-radius:50%; background:{dot_color};"></div>
                <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">{dq_label}</span>
            </div>
            <div style="font-size:0.9rem; font-weight:600; color:#0f172a;">{dq_value}</div>
        </div>"""
    dq_html += "</div>"
    st.markdown(dq_html, unsafe_allow_html=True)

    # ---- Spend by tactic (horizontal bars via HTML) ----
    spend_header_c1, spend_header_c2 = st.columns([3, 1])
    with spend_header_c1:
        st.markdown("""
        <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
            Media Spend Breakdown
        </div>
        <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:0.5rem;">
            Total spend per tactic going into Recast
        </div>
        """, unsafe_allow_html=True)
    with spend_header_c2:
        spend_window = st.selectbox("Date Range", ["Last 30 Days", "Last 60 Days", "Last 90 Days", "Last 365 Days", "All Time"],
                                    key="client_spend_window", label_visibility="collapsed")

    spend_days_map = {"Last 30 Days": 30, "Last 60 Days": 60, "Last 90 Days": 90, "Last 365 Days": 365, "All Time": None}
    spend_days = spend_days_map[spend_window]
    if spend_days and len(clean_df) > 0:
        max_date = pd.to_datetime(clean_df["date"]).max()
        cutoff = max_date - pd.Timedelta(days=spend_days)
        spend_df = clean_df[pd.to_datetime(clean_df["date"]) > cutoff]
    else:
        spend_df = clean_df

    if tactic_cols:
        tactic_totals = spend_df[tactic_cols].sum().sort_values(ascending=False)
        max_val = tactic_totals.max() if tactic_totals.max() > 0 else 1
        colors = ["#6366f1", "#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899",
                  "#14b8a6", "#f97316", "#06b6d4", "#84cc16", "#a855f7", "#ef4444",
                  "#0ea5e9", "#eab308", "#d946ef", "#22c55e", "#64748b", "#e11d48"]

        # Build campaign-to-tactic lookup for drill-down
        tactic_campaigns = {}
        for camp_name, m in saved_mappings.items():
            if isinstance(m, dict) and m.get("type") == "tactic":
                target = m.get("target")
            elif isinstance(m, str):
                target = m
            else:
                continue
            if target not in tactic_campaigns:
                tactic_campaigns[target] = []
            camp_val = raw_df[raw_df["raw_campaign_name"] == camp_name]
            if spend_days and len(camp_val) > 0:
                camp_val = camp_val[pd.to_datetime(camp_val["date"]) > (pd.to_datetime(raw_df["date"]).max() - pd.Timedelta(days=spend_days))]
            tactic_campaigns[target].append({"name": camp_name, "spend": camp_val["daily_value"].sum()})

        for ch, ch_data in RAW_CAMPAIGNS.items():
            for camp in ch_data["campaigns"]:
                raw_name = camp["raw_name"]
                mapped_to = camp.get("mapped_to")
                camp_type = camp.get("type", "tactic")
                if mapped_to and camp_type == "tactic" and raw_name not in saved_mappings:
                    if mapped_to not in tactic_campaigns:
                        tactic_campaigns[mapped_to] = []
                    if not any(c["name"] == raw_name for c in tactic_campaigns[mapped_to]):
                        camp_val = raw_df[raw_df["raw_campaign_name"] == raw_name]
                        if spend_days and len(camp_val) > 0:
                            camp_val = camp_val[pd.to_datetime(camp_val["date"]) > (pd.to_datetime(raw_df["date"]).max() - pd.Timedelta(days=spend_days))]
                        tactic_campaigns[mapped_to].append({"name": raw_name, "spend": camp_val["daily_value"].sum()})

        # Render bars with expandable campaign detail
        bars_html = '<div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
        for i, (tname, tval) in enumerate(tactic_totals.items()):
            pct = (tval / max_val) * 100
            color = colors[i % len(colors)]
            camp_count = len(tactic_campaigns.get(tname, []))
            bars_html += f"""
            <div style="margin-bottom:{'1rem' if i < len(tactic_totals) - 1 else '0'};">
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.35rem;">
                    <div style="font-size:0.85rem; font-weight:600; color:#334155;">{tname}</div>
                    <div style="display:flex; align-items:baseline; gap:0.75rem;">
                        <span style="font-size:0.7rem; color:#94a3b8;">{camp_count} source(s)</span>
                        <span style="font-size:0.95rem; font-weight:700; color:#0f172a; font-variant-numeric:tabular-nums;">${tval:,.0f}</span>
                    </div>
                </div>
                <div style="background:#f1f5f9; border-radius:6px; height:10px; overflow:hidden;">
                    <div style="background:{color}; width:{pct:.1f}%; height:100%; border-radius:6px;
                                transition:width 0.6s ease;"></div>
                </div>
            </div>"""
        bars_html += "</div>"
        st.markdown(bars_html, unsafe_allow_html=True)

        # Drill-down expander per tactic
        for i, (tname, tval) in enumerate(tactic_totals.items()):
            camps = tactic_campaigns.get(tname, [])
            if not camps:
                continue
            camps_sorted = sorted(camps, key=lambda x: x["spend"], reverse=True)
            color = colors[i % len(colors)]
            with st.expander(f"{tname} -- {len(camps_sorted)} campaign(s)"):
                camp_max_val = camps_sorted[0]["spend"] if camps_sorted[0]["spend"] > 0 else 1
                rows_html = ""
                for c in camps_sorted:
                    c_pct = (c["spend"] / camp_max_val) * 100 if camp_max_val > 0 else 0
                    rows_html += f"""
                    <div style="margin-bottom:0.75rem;">
                        <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.25rem;">
                            <div style="font-size:0.8rem; color:#475569; font-family:monospace; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:70%;">{c['name']}</div>
                            <div style="font-size:0.85rem; font-weight:700; color:#0f172a;">${c['spend']:,.0f}</div>
                        </div>
                        <div style="background:#f1f5f9; border-radius:4px; height:6px; overflow:hidden;">
                            <div style="background:{color}; opacity:0.6; width:{c_pct:.1f}%; height:100%; border-radius:4px;"></div>
                        </div>
                    </div>"""
                st.markdown(rows_html, unsafe_allow_html=True)
    else:
        st.info("No tactic data available yet.")

    st.markdown('<div style="height:2rem;"></div>', unsafe_allow_html=True)

    # ---- Dependent Variables summary ----
    if depvar_cols:
        dv_header_c1, dv_header_c2 = st.columns([3, 1])
        with dv_header_c1:
            st.markdown("""
            <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
                Dependent Variables (Outcomes)
            </div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:0.5rem;">
                KPIs being modeled -- acquisition, retention, etc.
            </div>
            """, unsafe_allow_html=True)
        with dv_header_c2:
            dv_window = st.selectbox("Date Range", ["Last 30 Days", "Last 60 Days", "Last 90 Days", "Last 365 Days", "All Time"],
                                     key="client_dv_window", label_visibility="collapsed")

        dv_days_map = {"Last 30 Days": 30, "Last 60 Days": 60, "Last 90 Days": 90, "Last 365 Days": 365, "All Time": None}
        dv_days = dv_days_map[dv_window]
        if dv_days and len(clean_df) > 0:
            dv_max_date = pd.to_datetime(clean_df["date"]).max()
            dv_cutoff = dv_max_date - pd.Timedelta(days=dv_days)
            dv_df = clean_df[pd.to_datetime(clean_df["date"]) > dv_cutoff]
        else:
            dv_df = clean_df

        dv_cards_html = '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:1rem;">'
        dv_colors = ["#7c3aed", "#a855f7", "#c084fc", "#d8b4fe"]
        for i, dv in enumerate(depvar_cols):
            dv_total = dv_df[dv].sum()
            avg_daily = dv_df[dv].mean()
            zero_days = int((dv_df[dv] == 0).sum())
            color = dv_colors[i % len(dv_colors)]
            dv_cards_html += f"""
            <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem;
                        box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
                <div style="position:absolute; top:0; left:0; right:0; height:4px; background:{color};"></div>
                <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;
                            color:#94a3b8; margin-bottom:0.75rem;">{dv}</div>
                <div style="font-size:1.8rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">{dv_total:,.0f}</div>
                <div style="display:flex; gap:1.5rem; margin-top:0.75rem;">
                    <div>
                        <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase;">Avg/Day</div>
                        <div style="font-size:0.9rem; font-weight:600; color:#334155;">{avg_daily:,.1f}</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase;">Zero Days</div>
                        <div style="font-size:0.9rem; font-weight:600; color:{'#ef4444' if zero_days > 0 else '#10b981'};">{zero_days}</div>
                    </div>
                </div>
            </div>"""
        dv_cards_html += "</div>"
        st.markdown(dv_cards_html, unsafe_allow_html=True)

        st.markdown('<div style="height:2rem;"></div>', unsafe_allow_html=True)

    # ---- Context Variables summary ----
    if ctxvar_cols:
        st.markdown("""
        <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
            Context Variables
        </div>
        <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">
            Non-spend, non-outcome variables included in the MMM (aggregated by mean)
        </div>
        """, unsafe_allow_html=True)

        cv_cards_html = '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:1rem;">'
        cv_colors = ["#f59e0b", "#d97706", "#b45309", "#92400e"]
        for i, cv in enumerate(ctxvar_cols):
            cv_mean = clean_df[cv].mean()
            cv_min = clean_df[cv].min()
            cv_max = clean_df[cv].max()
            color = cv_colors[i % len(cv_colors)]
            cv_cards_html += f"""
            <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:1.5rem;
                        box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; overflow:hidden;">
                <div style="position:absolute; top:0; left:0; right:0; height:4px; background:{color};"></div>
                <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;
                            color:#94a3b8; margin-bottom:0.75rem;">{cv}</div>
                <div style="font-size:1.8rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">{cv_mean:,.2f}</div>
                <div style="font-size:0.65rem; color:#94a3b8; margin-top:0.25rem;">Daily Average</div>
                <div style="display:flex; gap:1.5rem; margin-top:0.75rem;">
                    <div>
                        <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase;">Min</div>
                        <div style="font-size:0.9rem; font-weight:600; color:#334155;">{cv_min:,.2f}</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase;">Max</div>
                        <div style="font-size:0.9rem; font-weight:600; color:#334155;">{cv_max:,.2f}</div>
                    </div>
                </div>
            </div>"""
        cv_cards_html += "</div>"
        st.markdown(cv_cards_html, unsafe_allow_html=True)

        st.markdown('<div style="height:2rem;"></div>', unsafe_allow_html=True)

    # ---- Dependent Variable Spike Analysis ----
    if depvar_cols:
        st.markdown("""
        <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
            Dependent Variable Trends
        </div>
        <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
            Daily time series -- hover to identify spike dates for MMM priors
        </div>
        """, unsafe_allow_html=True)

        chart_src = clean_df[["date"] + depvar_cols].copy()
        chart_src["date"] = pd.to_datetime(chart_src["date"])
        chart_src = chart_src.sort_values("date")

        for dv in depvar_cols:
            series = chart_src[["date", dv]].copy()
            peak_val = series[dv].max()
            peak_date = series.loc[series[dv].idxmax(), "date"].strftime("%Y-%m-%d") if peak_val > 0 else "--"

            st.markdown(f"""
            <div style="background:#fff; border:1px solid #e2e8f0; border-left:4px solid #f97316;
                        border-radius:12px; padding:1rem 1.25rem; margin-bottom:0.5rem;
                        box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#0f172a;">{dv.replace('_', ' ').title()}</span>
                    <span style="font-size:0.8rem; color:#94a3b8;">Peak: <span style="color:#f97316; font-weight:700;">{peak_val:,.0f}</span> on {peak_date}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.line_chart(series.set_index("date"), height=250, use_container_width=True)
            st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

        st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

    # ---- Context Variable Trends ----
    if ctxvar_cols:
        st.markdown("""
        <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
            Context Variable Trends
        </div>
        <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
            Daily time series for non-spend, non-outcome variables (aggregated by mean)
        </div>
        """, unsafe_allow_html=True)

        cv_chart_src = clean_df[["date"] + ctxvar_cols].copy()
        cv_chart_src["date"] = pd.to_datetime(cv_chart_src["date"])
        cv_chart_src = cv_chart_src.sort_values("date")

        for cv in ctxvar_cols:
            cv_series = cv_chart_src[["date", cv]].copy()
            cv_avg = cv_series[cv].mean()
            cv_min_val = cv_series[cv].min()
            cv_max_val = cv_series[cv].max()

            st.markdown(f"""
            <div style="background:#fff; border:1px solid #e2e8f0; border-left:4px solid #f59e0b;
                        border-radius:12px; padding:1rem 1.25rem; margin-bottom:0.5rem;
                        box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#0f172a;">{cv.replace('_', ' ').title()}</span>
                    <span style="font-size:0.8rem; color:#94a3b8;">Avg: <span style="color:#f59e0b; font-weight:700;">{cv_avg:,.2f}</span> &nbsp; Min: {cv_min_val:,.2f} &nbsp; Max: {cv_max_val:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.line_chart(cv_series.set_index("date"), height=250, use_container_width=True)
            st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

        st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

    # ---- Campaign mapping table ----
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Campaign Mapping Detail
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
        How every raw campaign rolls up into the MMM
    </div>
    """, unsafe_allow_html=True)

    mapped_rows = []
    for channel, channel_data in RAW_CAMPAIGNS.items():
        for camp in channel_data["campaigns"]:
            name = camp["raw_name"]
            m_target = camp["mapped_to"]
            m_type = camp.get("type", "tactic")
            if name in saved_mappings:
                m = saved_mappings[name]
                if isinstance(m, dict):
                    m_target = m["target"]
                    m_type = m["type"]
                else:
                    m_target = m
            camp_val = raw_df[raw_df["raw_campaign_name"] == name]["daily_value"].sum()
            if name in ignored_list:
                status = "Excluded"
            elif m_target:
                status = "Mapped"
            else:
                status = "Unmapped"
            mapped_rows.append({
                "Channel": channel.replace("_", " ").title(),
                "Raw Campaign": name,
                "Maps To": m_target or "--",
                "Type": m_type.replace("_", " ").title() if m_target else "--",
                "Total Value": round(camp_val, 2),
                "Status": status,
            })

    mapped_display = pd.DataFrame(mapped_rows)

    # Filters
    filt_c1, filt_c2, filt_c3 = st.columns([2, 2, 1])
    with filt_c1:
        channels_available = sorted(mapped_display["Channel"].unique().tolist())
        filter_channel = st.multiselect("Filter by Channel", channels_available, default=channels_available, key="client_map_channel")
    with filt_c2:
        targets_available = sorted([t for t in mapped_display["Maps To"].unique().tolist() if t != "--"])
        filter_target = st.multiselect("Filter by Tactic / Dep Var / Context Var", targets_available, default=[], key="client_map_target",
                                       placeholder="All targets")
    with filt_c3:
        filter_search = st.text_input("Search", key="client_map_search", placeholder="Campaign name...")

    filtered_display = mapped_display[mapped_display["Channel"].isin(filter_channel)] if filter_channel else mapped_display
    if filter_target:
        filtered_display = filtered_display[filtered_display["Maps To"].isin(filter_target)]
    if filter_search:
        filtered_display = filtered_display[filtered_display["Raw Campaign"].str.contains(filter_search, case=False, na=False)]

    tab_all, tab_mapped, tab_unmapped, tab_excluded = st.tabs(["All Campaigns", "Mapped", "Unmapped", "Excluded"])
    with tab_all:
        def style_status(row):
            if row["Status"] == "Excluded":
                return ["background:#f8fafc; color:#94a3b8;"] * len(row)
            if row["Status"] == "Unmapped":
                return ["background:#fef2f2;"] * len(row)
            return [""] * len(row)
        display = filtered_display.copy()
        display["Total Value"] = display["Total Value"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(display.style.apply(style_status, axis=1), use_container_width=True, hide_index=True, height=420)

    with tab_mapped:
        m_df = filtered_display[filtered_display["Status"] == "Mapped"].copy()
        m_df["Total Value"] = m_df["Total Value"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(m_df, use_container_width=True, hide_index=True, height=420)

    with tab_unmapped:
        u_df = filtered_display[filtered_display["Status"] == "Unmapped"].copy()
        if len(u_df):
            u_df["Total Value"] = u_df["Total Value"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(u_df, use_container_width=True, hide_index=True, height=300)
        else:
            st.markdown("""
            <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:12px;
                        padding:2rem; text-align:center;">
                <div style="font-size:1.5rem; margin-bottom:0.5rem;">&#10003;</div>
                <div style="font-weight:700; color:#065f46;">All campaigns are mapped</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_excluded:
        e_df = filtered_display[filtered_display["Status"] == "Excluded"].copy()
        if len(e_df):
            e_df["Total Value"] = e_df["Total Value"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(e_df, use_container_width=True, hide_index=True, height=300)
            total_exc = mapped_display[mapped_display["Status"] == "Excluded"]["Total Value"].sum()
            st.markdown(f"""
            <div style="text-align:right; padding:0.75rem 1rem; background:#fef2f2; border-radius:10px; margin-top:0.5rem;">
                <span style="font-size:0.85rem; color:#64748b;">Total excluded spend:</span>
                <span style="font-size:1.1rem; font-weight:800; color:#dc2626; margin-left:0.5rem;">${total_exc:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px;
                        padding:2rem; text-align:center;">
                <div style="font-weight:600; color:#64748b;">No campaigns excluded</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

    # ---- Footer with branding ----
    st.markdown(f"""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:1.25rem 2rem;
                display:flex; justify-content:space-between; align-items:center; margin-top:1rem;">
        <div>
            <span style="font-size:0.8rem; font-weight:700; color:#334155;">MMM Campaign Mapper</span>
            <span style="font-size:0.8rem; color:#94a3b8; margin-left:0.5rem;">|</span>
            <span style="font-size:0.8rem; color:#94a3b8; margin-left:0.5rem;">{CLIENT.replace('_',' ').title()}</span>
        </div>
        <div style="font-size:0.75rem; color:#94a3b8;">
            {len(clean_df)} days of data -- {len(tactic_cols)} tactics -- {len(depvar_cols)} outcomes -- {window}mo window
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================================
# PAGE 11: Geo Lift Export (Incrementality Testing)
# ==========================================================
elif page == "Geo Lift Export":

    geo_df = cached_geo_data()

    # Hero
    st.markdown("""
    <div style="background:linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); border:1px solid #e879f9;
                border-radius:16px; padding:2rem 2.5rem; margin-bottom:2rem; position:relative; overflow:hidden;">
        <div style="font-size:1.6rem; font-weight:800; color:#0f172a; letter-spacing:-0.03em;">
            Incrementality Testing
        </div>
        <div style="font-size:0.95rem; color:#86198f; margin-top:0.35rem; font-weight:500;">
            Geo data export for Meta GeoLift -- aggregated by DMA or State
        </div>
        <div style="position:absolute; top:-20px; right:-20px; width:120px; height:120px;
                    border-radius:50%; background:rgba(255,255,255,0.4);"></div>
    </div>
    """, unsafe_allow_html=True)

    dev_info(
        "Geo Lift Export Page (Incrementality Testing)",
        "Generates geo-aggregated acquisition data formatted for Meta's GeoLift R package. "
        "Acquisition data comes from Shopify orders (order_date, billing_address_zip, acquisition flag). "
        "ZIP is normalized to 5 digits, then mapped to DMA region and state via a ZIP-to-DMA lookup table. "
        "User picks aggregation level (DMA, State, or ZIP) and date range, then exports CSV. "
        "Unmatched ZIPs (no DMA found) are flagged so they can be manually added to the lookup. "
        "In production, the ZIP-to-DMA lookup should be stored in a database table and kept up to date. "
        "This demo uses an embedded lookup of ~90 ZIPs across 25+ DMAs.",
        functions=[
            "generate_geo_data(start_date, n_days) -- simulates Shopify order-level data: order_date, billing_address_zip, state, dma_code, dma_name, acquisition",
            "aggregate_geo_for_geolift(geo_df, location_level) -- aggregates orders to GeoLift format (zeros removed)",
            "normalize_zip(zip_code) -- strips ZIP+4 to 5 digits (e.g., '34293-8821' -> '34293')",
            "zip_to_dma(zip5) -- looks up (state, dma_code, dma_name) for a 5-digit ZIP",
            "get_unmatched_zips(geo_df) -- finds orders with no DMA match, returns summary + counts",
            "ZIP_DMA_LOOKUP dict -- in production: database table. User can add missing ZIPs via UI.",
        ],
        data_flow="Shopify orders table (order_date, billing_address_zip, acquisition) -> normalize_zip() strips to 5 digits -> "
                   "zip_to_dma() maps to DMA code/name and state -> aggregate_geo_for_geolift() groups by date + location, removes zeros -> "
                   "export CSV in GeoLift format. Feed into GeoLift R package. "
                   "Source: acquisition = Shopify order conversion flag (1 = new customer acquisition, 0 = no acquisition)."
    )

    # -- ZIP File Upload Tool --
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Upload ZIP Code File
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
        Upload a CSV with ZIP code data and download a DMA-matched output ready for GeoLift
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload CSV file (must contain a ZIP code column)",
        type=["csv"],
        key="geo_upload",
    )

    if uploaded_file is not None:
        try:
            upload_df = pd.read_csv(uploaded_file, dtype=str)
        except Exception as e:
            st.error(f"Could not read file: {e}")
            upload_df = None

        if upload_df is not None and len(upload_df) > 0:
            # Let user pick which column is the ZIP
            up1, up2 = st.columns([2, 2])
            with up1:
                zip_col = st.selectbox("Which column contains ZIP codes?", upload_df.columns.tolist(), key="upload_zip_col")
            with up2:
                value_col_options = ["-- row count (1 per row) --"] + [c for c in upload_df.columns if c != zip_col]
                value_col = st.selectbox("Which column is the Y value (optional)?", value_col_options, key="upload_val_col")

            # Normalize ZIPs and look up DMA
            upload_df["_zip5"] = upload_df[zip_col].apply(normalize_zip)
            dma_states = []
            dma_codes = []
            dma_names = []
            for z in upload_df["_zip5"]:
                result = zip_to_dma(z)
                if result:
                    dma_states.append(result[0])
                    dma_codes.append(result[1])
                    dma_names.append(result[2])
                else:
                    dma_states.append(None)
                    dma_codes.append(None)
                    dma_names.append(None)

            upload_df["zip5"] = upload_df["_zip5"]
            upload_df["state"] = dma_states
            upload_df["dma_code"] = dma_codes
            upload_df["dma_name"] = dma_names
            upload_df = upload_df.drop(columns=["_zip5"])

            matched = upload_df["dma_name"].notna().sum()
            unmatched = upload_df["dma_name"].isna().sum()
            match_pct = matched / len(upload_df) * 100 if len(upload_df) > 0 else 0

            # Stats
            m_color = "#10b981" if match_pct >= 95 else ("#f59e0b" if match_pct >= 80 else "#ef4444")
            st.markdown(f"""
            <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:1rem; margin:1rem 0;">
                <div style="background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:1.25rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Total Rows</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#0f172a;">{len(upload_df):,}</div>
                </div>
                <div style="background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:1.25rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Matched to DMA</div>
                    <div style="font-size:1.6rem; font-weight:800; color:{m_color};">{matched:,}</div>
                </div>
                <div style="background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:1.25rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Unmatched</div>
                    <div style="font-size:1.6rem; font-weight:800; color:{'#ef4444' if unmatched > 0 else '#10b981'};">{unmatched:,}</div>
                </div>
                <div style="background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:1.25rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#94a3b8;">Match Rate</div>
                    <div style="font-size:1.6rem; font-weight:800; color:{m_color};">{match_pct:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Preview
            st.dataframe(upload_df.head(50), use_container_width=True, height=280)

            # Build GeoLift-format output (grouped by dma_name + date if date col exists)
            matched_df = upload_df[upload_df["dma_name"].notna()].copy()

            if value_col == "-- row count (1 per row) --":
                matched_df["Y"] = 1
            else:
                matched_df["Y"] = pd.to_numeric(matched_df[value_col], errors="coerce").fillna(0)

            dl1, dl2 = st.columns(2)
            with dl1:
                full_csv = upload_df.to_csv(index=False)
                st.download_button(
                    label="Download Full Matched CSV (all rows + DMA columns)",
                    data=full_csv,
                    file_name="zip_dma_matched.csv",
                    mime="text/csv",
                    key="dl_upload_full",
                    use_container_width=True,
                )
            with dl2:
                geolift_out = matched_df[["dma_name", "Y"]].groupby("dma_name", as_index=False)["Y"].sum()
                geolift_out = geolift_out.rename(columns={"dma_name": "location"})
                geolift_out = geolift_out[geolift_out["Y"] > 0].sort_values("location")
                geolift_csv = geolift_out.to_csv(index=False)
                st.download_button(
                    label="Download GeoLift Format (location, Y)",
                    data=geolift_csv,
                    file_name="zip_to_dma_geolift.csv",
                    mime="text/csv",
                    key="dl_upload_geolift",
                    use_container_width=True,
                )

            if unmatched > 0:
                unmatched_zips_df = upload_df[upload_df["dma_name"].isna()][[zip_col, "zip5"]].drop_duplicates()
                st.markdown(f"""
                <div style="background:#fef2f2; border:1px solid #fca5a5; border-left:4px solid #ef4444;
                            border-radius:10px; padding:0.85rem 1.25rem; margin-top:0.75rem;">
                    <span style="font-weight:700; color:#991b1b;">{unmatched:,} row(s) had no DMA match</span>
                    <span style="color:#991b1b; font-size:0.85rem;"> -- excluded from GeoLift output. Use the Add ZIP Mapping section below to resolve.</span>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(unmatched_zips_df, use_container_width=True, height=180)

    section_divider()

    # KPI row
    total_orders = len(geo_df)
    total_acquisitions = int(geo_df["acquisition"].sum())
    unique_zips = geo_df["billing_address_zip"].nunique()
    unique_dmas = geo_df["dma_name"].nunique()
    unique_states = geo_df["state"].nunique()
    date_min = geo_df["order_date"].min()
    date_max = geo_df["order_date"].max()
    n_days_data = geo_df["order_date"].nunique()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Total Orders", f"{total_orders:,}", "#a855f7")
    with c2:
        metric_card("Acquisitions", f"{total_acquisitions:,}", "#6366f1")
    with c3:
        metric_card("Unique DMAs", str(unique_dmas), "#3b82f6")
    with c4:
        metric_card("Unique States", str(unique_states), "#0ea5e9")
    with c5:
        metric_card("Days of Data", str(n_days_data), "#10b981")

    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

    # -- Raw order data preview (like the BigQuery screenshot) --
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Raw Order Data
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">
        Simulated BigQuery output -- each row is one order with ZIP, DMA, and acquisition flag
    </div>
    """, unsafe_allow_html=True)

    preview_df = geo_df[["order_date", "billing_address_zip", "state", "dma_code", "dma_name", "acquisition"]].copy()
    st.dataframe(preview_df.head(50), use_container_width=True, height=300)

    section_divider()

    # -- Export configuration --
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        GeoLift Export
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.25rem;">
        Configure and download data formatted for Meta GeoLift (date, location, Y)
    </div>
    """, unsafe_allow_html=True)

    cfg1, cfg2 = st.columns(2)
    with cfg1:
        location_level = st.selectbox("Location Granularity", ["DMA", "State", "ZIP Code"], key="geo_loc_level")
    with cfg2:
        date_range = st.date_input(
            "Date Range",
            value=(pd.Timestamp(date_min), pd.Timestamp(date_max)),
            min_value=pd.Timestamp(date_min),
            max_value=pd.Timestamp(date_max),
            key="geo_date_range",
        )

    # Filter by date range (handle single-date selection gracefully)
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        d_start, d_end = date_range
        filtered_geo = geo_df[
            (geo_df["order_date"] >= str(d_start)) & (geo_df["order_date"] <= str(d_end))
        ].copy()
    else:
        filtered_geo = geo_df.copy()

    if len(filtered_geo) == 0:
        st.warning("No data in selected date range.")
        st.stop()

    loc_map = {"DMA": "dma", "State": "state", "ZIP Code": "zip"}
    loc_key = loc_map[location_level]
    geolift_df = aggregate_geo_for_geolift(filtered_geo, location_level=loc_key)

    # Stats about the export
    loc_col_name = "dma_name" if loc_key == "dma" else "location"
    n_locations = geolift_df[loc_col_name].nunique()
    n_dates = geolift_df["date"].nunique()
    total_y = int(geolift_df["Y"].sum())

    st.markdown(f"""
    <div style="background:#faf5ff; border:1px solid #e9d5ff; border-radius:12px; padding:1.25rem; margin-bottom:1.5rem;">
        <div style="display:flex; gap:2rem; flex-wrap:wrap;">
            <div>
                <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#7c3aed;">Locations</span>
                <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{n_locations}</div>
            </div>
            <div>
                <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#7c3aed;">Days</span>
                <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{n_dates}</div>
            </div>
            <div>
                <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#7c3aed;">Total Y (Acquisitions)</span>
                <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{total_y:,}</div>
            </div>
            <div>
                <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#7c3aed;">Rows</span>
                <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{len(geolift_df):,}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Show the GeoLift formatted data
    col_tags = ""
    for col in geolift_df.columns:
        col_tags += f'<span style="font-family:monospace; background:#f1f5f9; padding:0.1rem 0.4rem; border-radius:4px; margin-right:0.3rem;">{col}</span> '

    st.markdown(f"""
    <div style="font-size:0.95rem; font-weight:700; color:#0f172a; margin-bottom:0.5rem;">
        GeoLift Format Preview
    </div>
    <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:0.75rem;">
        Columns: {col_tags} -- zero-Y rows removed, ready for GeoDataRead() in R
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(geolift_df, use_container_width=True, height=400)

    # Download button
    csv_data = geolift_df.to_csv(index=False)
    st.download_button(
        label=f"Download GeoLift CSV ({location_level})",
        data=csv_data,
        file_name=f"geolift_{loc_key}_{date_min}_{date_max}.csv",
        mime="text/csv",
        key="download_geolift",
    )

    section_divider()

    # -- DMA reference table --
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        ZIP to DMA Reference
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">
        Mapping used to convert 5-digit ZIP codes to DMA regions and states
    </div>
    """, unsafe_allow_html=True)

    ref_rows = []
    for z, (st_code, dma_c, dma_n) in sorted(ZIP_DMA_LOOKUP.items()):
        ref_rows.append({"zip_code": z, "state": st_code, "dma_code": dma_c, "dma_name": dma_n})
    ref_df = pd.DataFrame(ref_rows)
    st.dataframe(ref_df, use_container_width=True, height=300)

    section_divider()

    # -- Unmatched ZIPs section --
    unmatched_summary, total_unmatched, total_orders = get_unmatched_zips(geo_df)
    unmatched_pct = (total_unmatched / total_orders * 100) if total_orders > 0 else 0

    if total_unmatched > 0:
        border_color = "#ef4444" if unmatched_pct > 5 else "#f59e0b"
        bg_color = "#fef2f2" if unmatched_pct > 5 else "#fffbeb"
        text_color = "#991b1b" if unmatched_pct > 5 else "#92400e"
        label_color = "#b91c1c" if unmatched_pct > 5 else "#b45309"

        st.markdown(f"""
        <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
            Unmatched ZIP Codes
        </div>
        <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">
            Orders with ZIP codes not found in the DMA lookup -- these are excluded from DMA/State exports
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:{bg_color}; border:1px solid {border_color}; border-left:4px solid {border_color};
                    border-radius:12px; padding:1.25rem; margin-bottom:1.5rem;">
            <div style="display:flex; gap:2.5rem; flex-wrap:wrap; align-items:center;">
                <div>
                    <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:{label_color};">Unmatched Orders</span>
                    <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{total_unmatched:,}</div>
                </div>
                <div>
                    <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:{label_color};">% of Total</span>
                    <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{unmatched_pct:.1f}%</div>
                </div>
                <div>
                    <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:{label_color};">Unique ZIPs</span>
                    <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{len(unmatched_summary)}</div>
                </div>
                <div>
                    <span style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:{label_color};">Lost Acquisitions</span>
                    <div style="font-size:1.3rem; font-weight:800; color:#0f172a;">{int(unmatched_summary["acquisition_count"].sum()):,}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Build styled table of unmatched ZIPs
        table_rows = ""
        for _, row in unmatched_summary.iterrows():
            table_rows += f"""
            <tr>
                <td style="padding:0.6rem 1rem; font-family:monospace; font-weight:600; color:#334155;">{row['billing_address_zip']}</td>
                <td style="padding:0.6rem 1rem; text-align:right; color:#0f172a; font-weight:600;">{int(row['order_count']):,}</td>
                <td style="padding:0.6rem 1rem; text-align:right; color:#6366f1; font-weight:600;">{int(row['acquisition_count']):,}</td>
                <td style="padding:0.6rem 1rem;">
                    <span style="background:#fef2f2; color:#991b1b; padding:0.15rem 0.6rem; border-radius:50px;
                                 font-size:0.75rem; font-weight:600;">No DMA Match</span>
                </td>
            </tr>"""

        st.markdown(f"""
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.06);">
            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background:#f8fafc; border-bottom:2px solid #e2e8f0;">
                        <th style="padding:0.75rem 1rem; text-align:left; font-size:0.75rem; font-weight:700;
                                   text-transform:uppercase; letter-spacing:0.05em; color:#64748b;">ZIP Code</th>
                        <th style="padding:0.75rem 1rem; text-align:right; font-size:0.75rem; font-weight:700;
                                   text-transform:uppercase; letter-spacing:0.05em; color:#64748b;">Orders</th>
                        <th style="padding:0.75rem 1rem; text-align:right; font-size:0.75rem; font-weight:700;
                                   text-transform:uppercase; letter-spacing:0.05em; color:#64748b;">Acquisitions</th>
                        <th style="padding:0.75rem 1rem; text-align:left; font-size:0.75rem; font-weight:700;
                                   text-transform:uppercase; letter-spacing:0.05em; color:#64748b;">Status</th>
                    </tr>
                </thead>
                <tbody>{table_rows}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:1rem 1.25rem; margin-top:1rem;">
            <div style="font-weight:700; color:#1e40af; font-size:0.85rem; margin-bottom:0.4rem;">How to resolve unmatched ZIPs</div>
            <ul style="margin:0; padding-left:1.25rem; font-size:0.8rem; color:#334155; line-height:1.8;">
                <li>Add missing ZIPs to the <span style="font-family:monospace; background:#dbeafe; padding:0.1rem 0.3rem; border-radius:3px;">ZIP_DMA_LOOKUP</span> reference table</li>
                <li>In production: use a complete ZIP-to-DMA dataset (e.g., USPS crosswalk or Nielsen DMA boundaries)</li>
                <li>ZIPs like 96xxx (Hawaii), 995xx-998xx (Alaska), 009xx (Puerto Rico) often lack DMA coverage</li>
                <li>Consider mapping these to a catch-all "Other" DMA or excluding them intentionally</li>
                <li>Download unmatched list below to investigate and add to lookup</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Download unmatched ZIPs
        unmatched_csv = unmatched_summary.to_csv(index=False)
        st.download_button(
            label="Download Unmatched ZIPs CSV",
            data=unmatched_csv,
            file_name="unmatched_zips.csv",
            mime="text/csv",
            key="download_unmatched_zips",
        )
    else:
        st.markdown("""
        <div style="background:#ecfdf5; border:1px solid #6ee7b7; border-left:4px solid #10b981;
                    border-radius:12px; padding:1.25rem; margin-top:0.5rem;">
            <div style="font-weight:700; color:#065f46; font-size:0.95rem;">All ZIP codes matched</div>
            <div style="font-size:0.85rem; color:#047857; margin-top:0.25rem;">
                Every order ZIP in the dataset has a valid DMA mapping. No data is being lost.
            </div>
        </div>
        """, unsafe_allow_html=True)

    section_divider()

    # -- Manual ZIP-to-DMA entry --
    st.markdown("""
    <div style="font-size:1.1rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em; margin-bottom:0.25rem;">
        Add ZIP to DMA Mapping
    </div>
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">
        Manually add missing ZIP codes to the lookup. In production this saves to a database table.
    </div>
    """, unsafe_allow_html=True)

    add_c1, add_c2, add_c3, add_c4 = st.columns([1, 1, 2, 1])
    with add_c1:
        new_zip = st.text_input("ZIP Code (5-digit)", max_chars=5, key="add_zip", placeholder="e.g. 96701")
    with add_c2:
        new_dma_code = st.text_input("DMA Code", max_chars=4, key="add_dma_code", placeholder="e.g. 744")
    with add_c3:
        new_dma_name = st.text_input("DMA Name", key="add_dma_name", placeholder="e.g. HONOLULU")
    with add_c4:
        st.markdown('<div style="height:1.65rem;"></div>', unsafe_allow_html=True)
        add_clicked = st.button("Add Mapping", key="btn_add_zip", use_container_width=True)

    if "custom_zip_mappings" not in st.session_state:
        st.session_state.custom_zip_mappings = []

    if add_clicked:
        errors = []
        zip_val = (new_zip or "").strip()
        code_val = (new_dma_code or "").strip()
        name_val = (new_dma_name or "").strip().upper()
        if not zip_val or len(zip_val) != 5 or not zip_val.isdigit():
            errors.append("ZIP must be exactly 5 digits")
        if not code_val or not code_val.isdigit():
            errors.append("DMA Code must be a number")
        if not name_val:
            errors.append("DMA Name is required")

        if errors:
            st.error(" | ".join(errors))
        else:
            st.session_state.custom_zip_mappings.append({
                "zip_code": zip_val, "dma_code": int(code_val), "dma_name": name_val
            })
            st.success(f"Mapping added: {zip_val} -> {code_val} ({name_val}). In production this writes to the ZIP-to-DMA database table.")

    if st.session_state.custom_zip_mappings:
        st.markdown("""
        <div style="font-size:0.9rem; font-weight:700; color:#0f172a; margin-top:1rem; margin-bottom:0.5rem;">
            Pending Additions (this session)
        </div>
        """, unsafe_allow_html=True)
        rows_html = ""
        for m in st.session_state.custom_zip_mappings:
            rows_html += f"""
            <tr>
                <td style="padding:0.5rem 1rem; font-family:monospace; font-weight:600;">{m['zip_code']}</td>
                <td style="padding:0.5rem 1rem; font-weight:600; color:#6366f1;">{m['dma_code']}</td>
                <td style="padding:0.5rem 1rem; color:#334155;">{m['dma_name']}</td>
                <td style="padding:0.5rem 1rem;"><span class="badge-amber" style="display:inline-block; padding:0.15rem 0.6rem; border-radius:50px; font-size:0.7rem; font-weight:600; background:#fef3c7; color:#92400e;">Pending Save</span></td>
            </tr>"""
        st.markdown(f"""
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.06);">
            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background:#f8fafc; border-bottom:2px solid #e2e8f0;">
                        <th style="padding:0.6rem 1rem; text-align:left; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#64748b;">ZIP</th>
                        <th style="padding:0.6rem 1rem; text-align:left; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#64748b;">DMA Code</th>
                        <th style="padding:0.6rem 1rem; text-align:left; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#64748b;">DMA Name</th>
                        <th style="padding:0.6rem 1rem; text-align:left; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#64748b;">Status</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)
