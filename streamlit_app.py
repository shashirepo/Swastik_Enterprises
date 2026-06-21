"""
main.py — Entry point for SWASTIK ENTERPRISES Sales Order Generator
Run with:  streamlit run main.py
Requires:  pip install streamlit reportlab Pillow
"""

import streamlit as st
import uuid

from auth import show_login_page
from config import BANK_DETAILS, COMPANY_ADDR1, COMPANY_GSTIN, COMPANY_NAME, QR_PATH, SAMPLE_ITEMS, SIG_PATH
from ui.styles import inject_css, render_banner
from ui.tab_sales_order import render_tab_sales_order
from ui.tab_tax_invoice import render_tab_tax_invoice
from utils import gen_invoice_no, gen_order_no

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Swastik Enterprises — Invoice Portal",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    import base64
    if "session" in st.query_params:
        try:
            decoded = base64.b64decode(st.query_params["session"]).decode()
            if decoded.startswith("auth:"):
                st.session_state.authenticated = True
                st.session_state.user_name = decoded.split(":", 1)[1]
        except Exception:
            pass

if not st.session_state.get("authenticated", False):
    show_login_page()
    st.stop()

# ── Inject design-system CSS ──────────────────────────────────────────────────
inject_css()

user_display = st.session_state.get("user_name", "User")
user_initial = user_display[0].upper() if user_display else "U"

# ── Top Banner ────────────────────────────────────────────────────────────────
render_banner(user_display)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand block
    st.markdown(f"""
<div class="sb-brand">
  <div class="sb-brand-icon">S</div>
  <div class="sb-brand-name">SWASTIK ENTERPRISES</div>
  <div class="sb-brand-meta">Solar Energy Solutions · Varanasi</div>
</div>""", unsafe_allow_html=True)

    # Logged-in user
    st.markdown(f"""
<div class="sb-user">
  <div class="sb-user-avatar">{user_initial}</div>
  <div>
    <div class="sb-user-name">{user_display}</div>
    <div class="sb-user-role">Authorised User</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Contact info
    st.markdown("""
<div class="sb-section">
  <div class="sb-section-label">Contact</div>
  <div class="sb-row"><span class="sb-icon">📞</span> +91 9936148679 — Ravindra Singh</div>
  <div class="sb-row"><span class="sb-icon">📞</span> +91 9506114040 — Veer Singh</div>
  <div class="sb-row"><span class="sb-icon">✉️</span> swastikenterprises8679@gmail.com</div>
  <div class="sb-row"><span class="sb-icon">📍</span> Belwariya, Murdaha, Varanasi — 221202</div>
</div>""", unsafe_allow_html=True)

    # GSTIN
    st.markdown("""
<div class="sb-section">
  <div class="sb-section-label">GST Registration</div>
  <div class="sb-row"><span class="sb-icon">🏛️</span> GSTIN: 09QRFPS4600L1Z2</div>
  <div class="sb-row"><span class="sb-icon">📊</span> GST Slabs: 0% · 5% · 12% · 18% · 28%</div>
</div>""", unsafe_allow_html=True)

    # Bank details
    st.markdown("""
<div class="sb-bank">
  <div style="font-size:9.5px;font-weight:800;letter-spacing:1px;text-transform:uppercase;
              color:rgba(255,255,255,.35);margin-bottom:10px;">Bank Details</div>
  <div class="sb-bank-row">
    <span class="sb-bank-lbl">Bank</span>
    <span class="sb-bank-val">Indian Overseas Bank</span>
  </div>
  <div class="sb-bank-row">
    <span class="sb-bank-lbl">A/c No.</span>
    <span class="sb-bank-val">346702000000466</span>
  </div>
  <div class="sb-bank-row">
    <span class="sb-bank-lbl">IFSC</span>
    <span class="sb-bank-val">IOBA0003467</span>
  </div>
  <div class="sb-bank-row">
    <span class="sb-bank-lbl">Branch</span>
    <span class="sb-bank-val">Parmanandpur, Varanasi</span>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if st.button("🚪  Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            st.session_state.pop(k, None)
        if "session" in st.query_params:
            del st.query_params["session"]
        st.rerun()

    st.markdown("""
<div style="padding:16px 18px 0;font-size:10.5px;color:rgba(255,255,255,.2);text-align:center;line-height:1.6">
  Swastik Enterprises © 2025<br>Invoice Portal v2.0
</div>""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
def _init(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

_init("order_no",    gen_order_no())
_init("order_items", [
    {"_id": uuid.uuid4().hex, "desc": d, "hsn": h, "qty": q, "unit": u, "price": p, "brand": br, "gst": g}
    for d, h, q, u, p, br, g in SAMPLE_ITEMS
])
_init("inv_no",    gen_invoice_no())
_init("inv_items", [
    {"_id": uuid.uuid4().hex, "desc": d, "hsn": h, "qty": q, "unit": u, "price": p, "brand": br, "gst": g}
    for d, h, q, u, p, br, g in SAMPLE_ITEMS
])

for asset_key, path in [("qr_bytes", QR_PATH), ("sig_bytes", SIG_PATH)]:
    if asset_key not in st.session_state:
        try:
            with open(path, "rb") as f:
                st.session_state[asset_key] = f.read()
        except Exception:
            st.session_state[asset_key] = None

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📋  Sales Order / Quotation", "🧾  Tax Invoice"])

with tab1:
    render_tab_sales_order()

with tab2:
    render_tab_tax_invoice()
