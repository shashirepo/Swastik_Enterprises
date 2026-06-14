"""
ui/styles.py — Design system & global CSS for SWASTIK ENTERPRISES app
"""

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
APP_CSS = """
<style>
/* ═══ IMPORTS & TOKENS ═══════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

:root {
  /* Brand colours */
  --blue:        #2563eb;
  --blue-dark:   #1d4ed8;
  --blue-50:     #eff6ff;
  --blue-100:    #dbeafe;
  --navy:        #0f172a;
  --navy-800:    #1e293b;
  --navy-700:    #334155;
  /* Neutrals */
  --surface:     #f1f5f9;
  --surface-2:   #f8fafc;
  --card:        #ffffff;
  --border:      #e2e8f0;
  --border-2:    #cbd5e1;
  /* Text */
  --text:        #0f172a;
  --text-2:      #475569;
  --text-3:      #94a3b8;
  /* Semantic */
  --green:       #059669;
  --green-50:    #ecfdf5;
  --green-100:   #d1fae5;
  --green-200:   #a7f3d0;
  --amber:       #d97706;
  --amber-50:    #fffbeb;
  --red:         #dc2626;
  --red-50:      #fef2f2;
  --red-100:     #fee2e2;
  /* Shadows */
  --sh-xs: 0 1px 2px rgba(0,0,0,.05);
  --sh-sm: 0 1px 3px rgba(0,0,0,.10), 0 1px 2px rgba(0,0,0,.06);
  --sh-md: 0 4px 6px rgba(0,0,0,.07), 0 2px 4px rgba(0,0,0,.05);
  --sh-lg: 0 10px 25px rgba(0,0,0,.10), 0 4px 10px rgba(0,0,0,.05);
  /* Radii */
  --r-xs: 6px;  --r-sm: 8px;  --r-md: 12px;
  --r-lg: 16px; --r-xl: 20px; --r-2xl: 24px;
}

/* ═══ BASE ════════════════════════════════════════════════════════════════════ */
html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.stApp { background: var(--surface) !important; }
section.main > div { padding-top: 0 !important; }

/* Reduce default Streamlit side padding so the table uses full width */
.block-container {
  padding-left: 1rem !important;
  padding-right: 1rem !important;
  max-width: 100% !important;
}
#MainMenu, footer { visibility: hidden; }
header { visibility: visible !important; }

/* Make sidebar toggle button clearly visible */
button[kind="header"] { visibility: visible !important; opacity: 1 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

/* ═══ FORM ELEMENTS ══════════════════════════════════════════════════════════ */

/* Labels */
.stTextInput > label, .stTextArea > label, .stNumberInput > label,
.stSelectbox > label, .stDateInput > label {
  font-family: 'Inter', sans-serif !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  color: var(--text-3) !important;
  letter-spacing: .7px !important;
  text-transform: uppercase !important;
  margin-bottom: 5px !important;
}

/* Text Input */
.stTextInput > div > div > input {
  background: white !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13.5px !important;
  font-weight: 400 !important;
  padding: 10px 12px !important;
  transition: border-color .15s, box-shadow .15s !important;
}
.stTextInput > div > div > input:hover { border-color: var(--border-2) !important; }
.stTextInput > div > div > input:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px var(--blue-100) !important;
  outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-3) !important; font-size: 13px !important; }

/* Text Area */
.stTextArea > div > div > textarea {
  background: white !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13px !important;
  padding: 10px 12px !important;
  line-height: 1.55 !important;
  transition: border-color .15s, box-shadow .15s !important;
  resize: none !important;
}
.stTextArea > div > div > textarea:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px var(--blue-100) !important;
  outline: none !important;
}
.stTextArea > div > div > textarea::placeholder { color: var(--text-3) !important; }

/* Number Input */
.stNumberInput > div > div > input {
  background: white !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 10px 8px !important;
  transition: border-color .15s, box-shadow .15s !important;
  text-align: right !important;
}
.stNumberInput > div > div > input:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px var(--blue-100) !important;
}

/* Selectbox */
.stSelectbox > div[data-baseweb="select"] > div {
  background: white !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13px !important;
  transition: border-color .15s, box-shadow .15s !important;
}
.stSelectbox > div[data-baseweb="select"] > div:focus-within {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px var(--blue-100) !important;
}
.stSelectbox div[data-baseweb="select"] > div > div:first-child {
  display: flex !important;
  justify-content: center !important;
  padding-left: 2px !important;
}

/* Date Input */
.stDateInput > div > div > input {
  background: white !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13.5px !important;
  padding: 10px 12px !important;
}

/* ═══ BUTTONS ════════════════════════════════════════════════════════════════ */

.stButton > button {
  background: white !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text-2) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 9px 16px !important;
  transition: all .15s ease !important;
  letter-spacing: .1px !important;
}
/* Delete button — compact red icon */
.stButton > button[title="Remove this row"] {
  padding: 5px 6px !important;
  font-size: 12px !important;
  line-height: 1 !important;
  color: var(--red) !important;
  background: var(--red-50) !important;
  border-color: var(--red-100) !important;
  border-radius: var(--r-xs) !important;
  width: 100% !important;
  min-height: 32px !important;
  transform: none !important;
}
.stButton > button[title="Remove this row"]:hover {
  background: var(--red-100) !important;
  border-color: var(--red) !important;
  box-shadow: none !important;
  transform: none !important;
}
.stButton > button:hover {
  border-color: var(--blue) !important;
  color: var(--blue) !important;
  background: var(--blue-50) !important;
  transform: translateY(-1px) !important;
  box-shadow: var(--sh-sm) !important;
}
.stButton > button:active { transform: translateY(0) !important; box-shadow: none !important; }

/* Tighter column padding for items rows */
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
  padding-left: 2px !important;
  padding-right: 2px !important;
  min-width: 0 !important;
  overflow: hidden !important;
}

/* Download Button — Premium CTA */
div[data-testid="stDownloadButton"] > button {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: var(--r-md) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14.5px !important;
  font-weight: 700 !important;
  padding: 15px 24px !important;
  width: 100% !important;
  box-shadow: 0 4px 16px rgba(37,99,235,.40) !important;
  transition: all .2s ease !important;
  letter-spacing: .2px !important;
}
div[data-testid="stDownloadButton"] > button:hover {
  box-shadow: 0 8px 28px rgba(37,99,235,.55) !important;
  transform: translateY(-2px) !important;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
}
div[data-testid="stDownloadButton"] > button:active {
  transform: translateY(0) !important;
  box-shadow: 0 2px 8px rgba(37,99,235,.3) !important;
}

/* ═══ TABS ═══════════════════════════════════════════════════════════════════ */

.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 2px solid var(--border) !important;
  gap: 0 !important;
  padding: 0 2px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border: none !important;
  border-bottom: 3px solid transparent !important;
  border-radius: 0 !important;
  color: var(--text-2) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 14px 22px !important;
  margin-bottom: -2px !important;
  transition: all .15s ease !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--blue) !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
  color: var(--blue) !important;
  border-bottom-color: var(--blue) !important;
  font-weight: 700 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 24px !important; }

/* ═══ EXPANDER ═══════════════════════════════════════════════════════════════ */

div[data-testid="stExpander"] {
  background: white !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important;
  box-shadow: var(--sh-xs) !important;
  overflow: hidden !important;
  transition: box-shadow .15s !important;
}
div[data-testid="stExpander"]:hover { box-shadow: var(--sh-sm) !important; }
div[data-testid="stExpander"] summary {
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  color: var(--text) !important;
  padding: 14px 18px !important;
}
div[data-testid="stExpander"] summary:hover { background: var(--surface) !important; }
div[data-testid="stExpander"] > details > div { padding: 4px 16px 16px !important; }

/* ═══ ALERTS ══════════════════════════════════════════════════════════════════ */

div[data-testid="stAlert"] {
  border-radius: var(--r-md) !important;
  border-width: 1.5px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13px !important;
  font-weight: 500 !important;
}

/* ═══ SIDEBAR ═════════════════════════════════════════════════════════════════ */

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0f172a 0%, #0d1f3c 100%) !important;
  border-right: 1px solid rgba(255,255,255,.05) !important;
}
section[data-testid="stSidebar"] * { color: rgba(255,255,255,.80) !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
  color: rgba(255,255,255,.95) !important;
}
section[data-testid="stSidebar"] .stButton > button {
  background: rgba(239,68,68,.10) !important;
  border: 1.5px solid rgba(239,68,68,.30) !important;
  color: #fca5a5 !important;
  width: 100% !important;
  font-size: 13px !important;
  font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(239,68,68,.22) !important;
  border-color: rgba(239,68,68,.55) !important;
  color: #fecaca !important;
  transform: none !important;
  box-shadow: none !important;
}

/* HR */
hr { border-color: var(--border) !important; margin: 16px 0 !important; }

/* ═══════════════════════════════════════════════════════════════════════════ */
/* CUSTOM COMPONENTS                                                           */
/* ═══════════════════════════════════════════════════════════════════════════ */

/* ─── Top Banner ──────────────────────────────────────────────────────────── */
.top-banner {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #1e293b 100%);
  padding: 18px 26px;
  border-radius: var(--r-lg);
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--sh-md);
  position: relative;
  overflow: hidden;
}
.top-banner::after {
  content: '';
  position: absolute;
  top: -80px; right: 0;
  width: 320px; height: 320px;
  background: radial-gradient(circle, rgba(59,130,246,.10) 0%, transparent 65%);
  pointer-events: none;
}
.banner-icon {
  width: 46px; height: 46px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: var(--r-sm);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 800; color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(37,99,235,.5);
}
.banner-company { flex: 1; }
.banner-name { font-size: 16px; font-weight: 700; color: white; letter-spacing: .3px; }
.banner-meta { font-size: 11.5px; color: rgba(255,255,255,.42); margin-top: 3px; letter-spacing: .4px; }
.banner-user-pill {
  background: rgba(255,255,255,.08);
  color: #cbd5e1;
  padding: 6px 14px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,.12);
}

/* ─── Section Card ────────────────────────────────────────────────────────── */
.section-card {
  background: var(--card);
  border-radius: var(--r-lg);
  padding: 22px 24px;
  margin-bottom: 16px;
  border: 1px solid var(--border);
  box-shadow: var(--sh-sm);
  transition: box-shadow .2s;
}
.section-card:hover { box-shadow: var(--sh-md); }
.section-title {
  font-size: 10.5px;
  font-weight: 800;
  color: var(--text-3);
  letter-spacing: 1.2px;
  text-transform: uppercase;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1.5px solid var(--surface);
}

/* ─── Items Table Header ──────────────────────────────────────────────────── */
.items-hdr {
  display: grid;
  grid-template-columns: 2.4fr 0.85fr 0.80fr 0.50fr 0.80fr 0.65fr 0.80fr 0.65fr 0.50fr;
  column-gap: 4px;
  background: linear-gradient(135deg, #0f172a, #1e3a8a);
  border-radius: var(--r-md) var(--r-md) 0 0;
  padding: 11px 4px;
  margin-bottom: 2px;
  box-shadow: 0 2px 8px rgba(15,23,42,.2);
}
.items-hdr-inv {
  display: grid;
  grid-template-columns: 2.4fr 0.85fr 0.80fr 0.50fr 0.80fr 0.65fr 0.80fr 0.65fr 0.50fr;
  column-gap: 4px;
  background: linear-gradient(135deg, #052e16, #14532d);
  border-radius: var(--r-md) var(--r-md) 0 0;
  padding: 11px 4px;
  margin-bottom: 2px;
  box-shadow: 0 2px 8px rgba(5,46,22,.2);
}
.items-hdr span, .items-hdr-inv span {
  padding: 3px 5px;
  font-size: 9.5px;
  font-weight: 700;
  color: rgba(255,255,255,.65);
  letter-spacing: .8px;
  text-transform: uppercase;
}

/* ─── Summary Card (right panel) ──────────────────────────────────────────── */
.summary-card {
  background: var(--card);
  border-radius: var(--r-lg);
  border: 1px solid var(--border);
  box-shadow: var(--sh-sm);
  overflow: hidden;
  margin-bottom: 16px;
}
.summary-hero {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
  padding: 22px 22px 20px;
  position: relative;
  overflow: hidden;
}
.summary-hero::before {
  content: '';
  position: absolute;
  bottom: -40px; right: -30px;
  width: 140px; height: 140px;
  background: radial-gradient(circle, rgba(255,255,255,.04) 0%, transparent 70%);
}
.summary-hero-label {
  font-size: 9.5px;
  font-weight: 800;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: rgba(255,255,255,.38);
  margin-bottom: 8px;
}
.summary-hero-amount {
  font-size: 34px;
  font-weight: 800;
  color: white;
  letter-spacing: -1.5px;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}
.summary-hero-sym { font-size: 22px; font-weight: 700; opacity: .65; vertical-align: 4px; margin-right: 1px; }
.summary-hero-words { font-size: 10.5px; color: rgba(255,255,255,.35); margin-top: 10px; font-style: italic; line-height: 1.5; }

/* Summary breakdown rows */
.summary-body { padding: 0 20px 4px; }
.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 9px 0;
  border-bottom: 1px solid var(--surface);
  font-size: 13px;
}
.summary-row:last-child { border-bottom: none; }
.summary-lbl { color: var(--text-2); font-weight: 500; }
.summary-val { color: var(--text); font-weight: 600; font-variant-numeric: tabular-nums; }
.summary-row.grand {
  border-top: 2px solid var(--border-2);
  border-bottom: none;
  margin-top: 4px;
  padding-top: 13px;
}
.summary-row.grand .summary-lbl { font-weight: 700; color: var(--text); font-size: 13.5px; }
.summary-row.grand .summary-val { color: var(--blue); font-weight: 800; font-size: 16px; }

/* GST mini section inside summary card */
.gst-mini {
  margin: 4px 20px 16px;
  background: var(--green-50);
  border: 1.5px solid var(--green-100);
  border-radius: var(--r-md);
  padding: 13px 15px;
}
.gst-mini-hdr {
  font-size: 9.5px;
  font-weight: 800;
  color: var(--green);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 9px;
}
.gst-mini-row {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 12px;
  border-bottom: 1px dashed rgba(5,150,105,.2);
}
.gst-mini-row:last-child {
  border-bottom: none;
  border-top: 1.5px solid rgba(5,150,105,.25);
  padding-top: 8px;
  margin-top: 4px;
  font-weight: 700;
}
.gst-mini-lbl { color: #064e3b; font-weight: 500; }
.gst-mini-val { color: var(--green); font-weight: 600; font-variant-numeric: tabular-nums; }
.gst-mini-sub {
  font-size: 10.5px;
  color: rgba(6,78,59,.55);
  font-weight: 400;
  margin-top: 2px;
}

/* Preview table inside summary card */
.preview-block {
  margin: 0 20px;
  border-top: 1px solid var(--surface);
  padding: 14px 0 4px;
}
.preview-block-hdr {
  font-size: 9.5px;
  font-weight: 800;
  color: var(--text-3);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.preview-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid var(--surface);
  font-size: 12.5px;
}
.preview-row:last-child { border-bottom: none; }
.preview-lbl { color: var(--text-2); font-weight: 500; }
.preview-val { color: var(--text); font-weight: 600; max-width: 55%; text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Download section inside summary card */
.dl-section { padding: 16px 20px 20px; border-top: 1px solid var(--surface); }
.dl-ready-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--green-50);
  border: 1.5px solid var(--green-100);
  border-radius: var(--r-sm);
  padding: 10px 14px;
  font-size: 12.5px;
  color: #065f46;
  font-weight: 600;
  margin-bottom: 12px;
}
.dl-alt {
  display: block;
  text-align: center;
  margin-top: 10px;
  font-size: 11.5px;
  color: var(--blue);
  text-decoration: none;
  opacity: .85;
  transition: opacity .15s;
}
.dl-alt:hover { opacity: 1; text-decoration: underline; }
.dl-caption {
  text-align: center;
  font-size: 11px;
  color: var(--text-3);
  margin-top: 6px;
}

/* Validation errors */
.val-err {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: var(--red-50);
  border: 1.5px solid var(--red-100);
  border-radius: var(--r-sm);
  padding: 10px 14px;
  font-size: 12.5px;
  color: #991b1b;
  font-weight: 500;
  margin-bottom: 8px;
}

/* Bank card */
.bank-card {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border: 1.5px solid #bfdbfe;
  border-radius: var(--r-md);
  padding: 15px 18px;
  margin-top: 14px;
}
.bank-row {
  display: flex;
  gap: 10px;
  padding: 5px 0;
  align-items: center;
  border-bottom: 1px solid rgba(191,219,254,.5);
  font-size: 12.5px;
}
.bank-row:last-child { border-bottom: none; }
.bank-label { color: #3b82f6; font-weight: 700; font-size: 10px; letter-spacing: .4px; min-width: 75px; text-transform: uppercase; }
.bank-val { color: #1e3a8a; font-weight: 600; }

/* Inline row amount */
.row-amt {
  padding: 8px 2px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text);
  text-align: right;
  font-variant-numeric: tabular-nums;
}

/* Sidebar sections */
.sb-brand {
  padding: 24px 18px 18px;
  border-bottom: 1px solid rgba(255,255,255,.07);
  margin-bottom: 8px;
}
.sb-brand-icon {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: var(--r-sm);
  display: flex; align-items: center; justify-content: center;
  font-size: 17px; font-weight: 800; color: white;
  box-shadow: 0 3px 10px rgba(37,99,235,.4);
  margin-bottom: 10px;
}
.sb-brand-name { font-size: 13.5px; font-weight: 700; color: white !important; line-height: 1.3; }
.sb-brand-meta { font-size: 10.5px; color: rgba(255,255,255,.35) !important; margin-top: 2px; letter-spacing: .3px; }

.sb-section { padding: 12px 18px; }
.sb-section-label {
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: rgba(255,255,255,.28) !important;
  margin-bottom: 8px;
}
.sb-row {
  display: flex;
  gap: 8px;
  padding: 5px 0;
  font-size: 12px;
  color: rgba(255,255,255,.68) !important;
  line-height: 1.5;
  border-bottom: 1px solid rgba(255,255,255,.05);
}
.sb-row:last-child { border-bottom: none; }
.sb-icon { flex-shrink: 0; font-size: 12px; margin-top: 1px; opacity: .7; }

.sb-bank {
  margin: 4px 14px 14px;
  background: rgba(37,99,235,.1);
  border: 1px solid rgba(37,99,235,.2);
  border-radius: var(--r-md);
  padding: 12px 14px;
}
.sb-bank-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 11px;
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.sb-bank-row:last-child { border-bottom: none; }
.sb-bank-lbl { color: rgba(255,255,255,.38) !important; font-weight: 600; font-size: 9.5px; letter-spacing: .3px; text-transform: uppercase; }
.sb-bank-val { color: rgba(255,255,255,.78) !important; font-weight: 600; }

.sb-user {
  margin: 0 14px 14px;
  background: rgba(255,255,255,.05);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: var(--r-md);
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.sb-user-avatar {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; color: white;
  flex-shrink: 0;
}
.sb-user-name { font-size: 13px; font-weight: 600; color: rgba(255,255,255,.88) !important; }
.sb-user-role { font-size: 10.5px; color: rgba(255,255,255,.38) !important; margin-top: 1px; }

/* ─── Animations ───────────────────────────────────────────────────────────── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp .3s ease forwards; }
</style>
"""

# ─── Items Header HTML ─────────────────────────────────────────────────────────
ITEMS_HEADER_SO = """
<div class="items-hdr">
  <span>Description</span><span>Brand</span><span>HSN/SAC</span>
  <span>Qty</span><span>Unit</span><span>GST%</span>
  <span>Price (₹)</span><span>Amount</span><span></span>
</div>"""

ITEMS_HEADER_INV = """
<div class="items-hdr-inv">
  <span>Description</span><span>Brand</span><span>HSN/SAC</span>
  <span>Qty</span><span>Unit</span><span>GST%</span>
  <span>Price (₹)</span><span>Amount</span><span></span>
</div>"""

# ─── Bank Card HTML ─────────────────────────────────────────────────────────────
BANK_CARD_HTML = """
<div class="bank-card">
  <div class="bank-row"><span class="bank-label">Bank</span><span class="bank-val">Indian Overseas Bank</span></div>
  <div class="bank-row"><span class="bank-label">A/c No.</span><span class="bank-val">346702000000466</span></div>
  <div class="bank-row"><span class="bank-label">IFSC</span><span class="bank-val">IOBA0003467</span></div>
  <div class="bank-row"><span class="bank-label">Branch</span><span class="bank-val">Parmanandpur, Varanasi</span></div>
</div>"""


def inject_css() -> None:
    """Inject the global design-system CSS."""
    st.markdown(APP_CSS, unsafe_allow_html=True)


def render_banner(user_display: str) -> None:
    """Render the top navigation banner."""
    st.markdown(f"""
<div class="top-banner">
  <div class="banner-icon">S</div>
  <div class="banner-company">
    <div class="banner-name">SWASTIK ENTERPRISES</div>
    <div class="banner-meta">BELWARIYA, VARANASI &nbsp;·&nbsp; GSTIN: 09QRFPS4600L1Z2 &nbsp;·&nbsp; Solar Energy Solutions</div>
  </div>
  <div><span class="banner-user-pill">👤 {user_display}</span></div>
</div>""", unsafe_allow_html=True)
