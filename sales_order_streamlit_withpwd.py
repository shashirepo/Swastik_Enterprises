"""
Sales Order Generator — SWASTIK ENTERPRISES
Run with:  streamlit run sales_order_streamlit.py
Requires:  pip install streamlit reportlab Pillow streamlit-authenticator
"""

import io
import os
import hashlib
import random
import string
import datetime

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    Image, SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable,
)

# ── Constants ─────────────────────────────────────────────────────────────────
COMPANY_NAME  = "SWASTIK ENTERPRISES"
COMPANY_ADDR1 = "BELWARIYA, POST - MURDAHA, DISTRICT - VARANASI, UTTAR PRADESH, INDIA, PIN-221202"
COMPANY_GSTIN = "GSTIN : 09QRFPS4600L1Z2"
COMPANY_TEL   = "Tel. : +91 9936148679 (Ravindra Singh) , +91 9506114040 (Veer Singh)"
COMPANY_EMAIL = "Email : swastikenterprises8679@gmail.com"
WARRANTY_BY   = "SWASTIK ENTERPRISES"
BANK_DETAILS  = (
    "Bank: Indian Overseas Bank  A/c No:346702000000466, "
    "IFSC :IOBA0003467  BRANCH: PARMANANDPUR, VARANASI"
)
TERMS = [
    "Goods once sold will not be taken back.",
    "Interest @ 18% p.a. will be charged if the payment is not made within the stipulated time.",
]
CGST_RATE = 9.0
SGST_RATE = 9.0
LOGO_PATH = "logo2.jpeg"   # place logo file next to this script

COMMON_UNITS = ["Pcs.", "MTR", "KG", "Set", "Pair", "Box", "Roll", "Ltr", "Nos."]

SAMPLE_ITEMS = [
    ("SOLAR STRUCTURE C CHANNEL 80*40 - PCS", "73089030", 1.0, "Pcs.", 1452.50),
    ("SOLAR APOLLO PLAIN STRUT*41*41 - PCS",  "73089030", 1.0, "Pcs.", 1120.50),
    ("SOLAR STRUCTURE C BASE PLATE",           "73089030", 1.0, "Pcs.",   80.00),
    ("SOLAR STRUCTURE MID CLAMP",              "73089030", 1.0, "Pcs.",   25.00),
    ("SOLAR STRUCTURE END CLAMP",              "73089030", 1.0, "Pcs.",   25.00),
]


# ════════════════════════════════════════════════════════════════════════════════
#  AUTH HELPERS
#  Credentials are read from st.secrets (Streamlit Community Cloud) OR from
#  a local .streamlit/secrets.toml file during development.
#
#  secrets.toml format:
#  ─────────────────────
#  [auth.users.admin]
#  password_hash = "sha256-hex-of-password"
#  name          = "Administrator"
#
#  [auth.users.ravindra]
#  password_hash = "sha256-hex-of-password"
#  name          = "Ravindra Singh"
# ════════════════════════════════════════════════════════════════════════════════

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _load_users() -> dict:
    """
    Returns {username: {name, password_hash}} from st.secrets if available,
    otherwise falls back to built-in defaults (for first run / local dev).
    """
    try:
        users_secret = st.secrets["auth"]["users"]
        return {
            uname: {
                "name":          udata["name"],
                "password_hash": udata["password_hash"],
            }
            for uname, udata in users_secret.items()
        }
    except (KeyError, AttributeError):
        # ── Default credentials (change before deploying!) ──────────────────
        # password: swastik@2024
        # password: solar@2024
        return {
            "admin": {
                "name":          "Administrator",
                "password_hash": "cfad5ccaf32fb8765202858e5a6d7f6b2e88b9ca8f4d0cd433590163fd384f7e",
            },
            "ravindra": {
                "name":          "Ravindra Singh",
                "password_hash": "6396c7fb51044fedab8e8d0278c072269fa2a8c0f8f4704ef26d1c8a5e359ff3",
            },
        }


def check_login(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, display_name)."""
    users = _load_users()
    user  = users.get(username.strip().lower())
    if user and user["password_hash"] == _hash(password):
        return True, user["name"]
    return False, ""


def show_login_page():
    """Render a centered login card and handle submission."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%) !important; }

    /* Hide Streamlit default chrome on login page */
    #MainMenu, footer, header { visibility: hidden; }

    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    .login-card {
        background: white;
        border-radius: 20px;
        padding: 44px 40px 36px;
        width: 100%;
        max-width: 420px;
        box-shadow: 0 20px 60px rgba(0,0,0,.35);
        text-align: center;
        margin: auto;
    }
    .login-logo {
        width: 64px; height: 64px;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        border-radius: 16px;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px; color: white; font-weight: 700;
        margin: 0 auto 16px;
    }
    .login-title {
        font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px;
    }
    .login-sub {
        font-size: 13px; color: #7a7a9d; margin-bottom: 28px;
    }
    .login-error {
        background: #fef2f2; border: 1px solid #fecaca;
        color: #dc2626; border-radius: 8px;
        padding: 10px 14px; font-size: 13px; margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Centre the card using columns
    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown("""
        <div class="login-card">
          <div class="login-logo">S</div>
          <div class="login-title">SWASTIK ENTERPRISES</div>
          <div class="login-sub">Sales Order Generator &nbsp;·&nbsp; Sign in to continue</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("login_error"):
            st.error("❌ Invalid username or password. Please try again.")

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

        if submitted:
            ok, name = check_login(username, password)
            if ok:
                st.session_state.authenticated = True
                st.session_state.user_name     = name
                st.session_state.username      = username.strip().lower()
                st.session_state.login_error   = False
                st.rerun()
            else:
                st.session_state.login_error = True
                st.rerun()

        st.markdown(
            "<p style='text-align:center;font-size:11px;color:#aaa;margin-top:20px'>"
            "🔒 Secured · SWASTIK ENTERPRISES © 2024</p>",
            unsafe_allow_html=True,
        )


# ── Helpers ───────────────────────────────────────────────────────────────────
def gen_order_no():
    return "SWSENT" + "".join(random.choices(string.digits, k=3))


def num_to_words(amount: float) -> str:
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven",
            "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen",
            "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty",
            "Sixty", "Seventy", "Eighty", "Ninety"]

    def two(n):
        return ones[n] if n < 20 else (tens[n // 10] + (" " + ones[n % 10] if n % 10 else "")).strip()

    def three(n):
        return (ones[n // 100] + " Hundred" + (" " + two(n % 100) if n % 100 else "")) if n >= 100 else two(n)

    rupees, paise = int(amount), round((amount - int(amount)) * 100)
    parts = []
    for div, label in [(10_00_00_000, "Arab"), (1_00_00_000, "Crore"),
                       (1_00_000, "Lakh"), (1_000, "Thousand")]:
        if rupees >= div:
            parts.append(three(rupees // div) + " " + label)
            rupees %= div
    if rupees:
        parts.append(three(rupees))
    word = " ".join(parts) if parts else "Zero"
    result = f"Rupees {word}"
    if paise:
        result += f" and Paisa {two(paise)}"
    return result + " Only"


# ── PDF builder ───────────────────────────────────────────────────────────────
def build_pdf(party_name, party_city, order_no, order_date, items) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=12*mm, bottomMargin=12*mm,
    )
    W = A4[0] - 30*mm
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    title_s = ps("T",  fontSize=14, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6)
    ctr_s   = ps("C",  fontSize=8,  alignment=TA_CENTER, leading=11)
    lft_s   = ps("L",  fontSize=8,  alignment=TA_LEFT,   leading=11)
    sml_s   = ps("S",  fontSize=7,  alignment=TA_LEFT,   leading=10)
    bold_c  = ps("BC", fontSize=8,  fontName="Helvetica-Bold", alignment=TA_CENTER)

    story = []

    # Logo
    try:
        logo = Image(LOGO_PATH, width=33*mm, height=30*mm)
    except Exception:
        logo = ""

    header_text = [
        Paragraph("<u>ORDER ESTIMATION</u>", bold_c),
        Paragraph(COMPANY_NAME, title_s),
        Paragraph(COMPANY_ADDR1, ctr_s),
        Paragraph(COMPANY_GSTIN, ctr_s),
        Paragraph(f"{COMPANY_TEL}<br/>{COMPANY_EMAIL}", ctr_s),
    ]

    header_table = Table([[logo, header_text]], colWidths=[W * .20, W * .80])
    header_table.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), .9, colors.black),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 5))

    # Party / Order box
    party_p = f"<b>Party Details :</b><br/>{party_name}<br/>{party_city}"
    order_p = f"<b>Order No. :</b> {order_no}<br/><b>Dated :</b> {order_date}<br/>"
    pt = Table(
        [[Paragraph(party_p, lft_s), Paragraph(order_p, lft_s)]],
        colWidths=[W * .55, W * .45],
    )
    pt.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), .5, colors.black),
        ("LINEBEFORE",    (1, 0), (1,  0),  .5, colors.black),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story += [pt, Spacer(1, 2*mm),
              Paragraph("We are pleased to receive the order for the following items :", lft_s),
              Spacer(1, 1*mm)]

    # Items table
    hdr = ["S.N.", "Description of Goods", "HSN/SAC\nCode", "Qty.", "Unit", "Price", "Amount(`)"]
    cw  = [W*.05, W*.35, W*.10, W*.07, W*.07, W*.12, W*.14]
    rows = [hdr]
    subtotal = total_qty = 0.0

    for i, it in enumerate(items, 1):
        amt = round(it["qty"] * it["price"], 2)
        subtotal  += amt
        total_qty += it["qty"]
        rows.append([str(i), it["desc"], it["hsn"],
                     f"{it['qty']:.2f}", it["unit"],
                     f"{it['price']:,.2f}", f"{amt:,.2f}"])

    cgst  = round(subtotal * CGST_RATE / 100, 2)
    sgst  = round(subtotal * SGST_RATE / 100, 2)
    tax   = round(cgst + sgst, 2)
    grand = round(subtotal + tax, 2)

    rows += [
        ["", "", "", "", "", "", f"{subtotal:,.2f}"],
        ["", "", "", "", "Add : CGST", f"@ {CGST_RATE:.2f} %", f"{cgst:,.2f}"],
        ["", "", "", "", "Add : SGST", f"@ {SGST_RATE:.2f} %", f"{sgst:,.2f}"],
        ["", "Grand Total", "", f"{int(total_qty)} Units", "", "`", f"{grand:,.2f}"],
    ]
    n = len(rows)

    it_t = Table(rows, colWidths=cw, repeatRows=1)
    it_t.setStyle(TableStyle([
        ("BOX",           (0, 0),   (-1, -1),  .5, colors.black),
        ("INNERGRID",     (0, 0),   (-1, n-5), .3, colors.black),
        ("LINEABOVE",     (0, n-4), (-1, n-4), .5, colors.black),
        ("LINEABOVE",     (0, n-1), (-1, n-1), .5, colors.black),
        ("BACKGROUND",    (0, 0),   (-1, 0),   colors.Color(.92, .92, .92)),
        ("FONTNAME",      (0, 0),   (-1, 0),   "Helvetica-Bold"),
        ("FONTNAME",      (0, n-1), (-1, n-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0),   (-1, -1),  7.5),
        ("ALIGN",         (0, 0),   (-1, -1),  "CENTER"),
        ("ALIGN",         (1, 1),   (1,  n-2), "LEFT"),
        ("ALIGN",         (5, 1),   (-1, -1),  "RIGHT"),
        ("VALIGN",        (0, 0),   (-1, -1),  "MIDDLE"),
        ("LEFTPADDING",   (0, 0),   (-1, -1),  2),
        ("RIGHTPADDING",  (0, 0),   (-1, -1),  2),
        ("TOPPADDING",    (0, 0),   (-1, -1),  2),
        ("BOTTOMPADDING", (0, 0),   (-1, -1),  2),
        ("SPAN",          (1, n-1), (3,  n-1)),
    ]))
    story += [it_t, Spacer(1, 2*mm)]

    tax_rows = [
        ["Tax Rate", "Taxable Amt.", "CGST Amt.", "SGST Amt.", "Total Tax"],
        ["18%", f"{subtotal:,.2f}", f"{cgst:,.2f}", f"{sgst:,.2f}", f"{tax:,.2f}"],
    ]
    tt = Table(tax_rows, colWidths=[W*.12, W*.22, W*.22, W*.22, W*.22])
    tt.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",  (0, 0), (-1, -1), 7.5),
        ("ALIGN",     (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, 0),  .5, colors.black),
    ]))
    story += [tt, Spacer(1, 2*mm),
              Paragraph(f"<i>{num_to_words(grand)}</i>", lft_s),
              Spacer(1, 2*mm),
              HRFlowable(width=W, thickness=.5, color=colors.black),
              Spacer(1, 1*mm),
              Paragraph(f"<b>Bank Details :</b>  {BANK_DETAILS}", sml_s),
              Spacer(1, 2*mm),
              HRFlowable(width=W, thickness=.5, color=colors.black),
              Spacer(1, 1*mm)]

    terms_p = "<b>Terms &amp; Conditions</b><br/>E.&amp; O.E.<br/>"
    for j, t in enumerate(TERMS, 1):
        terms_p += f"{j}. {t}<br/>"
    sig_p = (f"Receiver's Signature :<br/><br/><br/><br/>"
             f"<b>for {COMPANY_NAME}</b><br/><br/>Authorised Signatory")
    bt = Table(
        [[Paragraph(terms_p, sml_s), Paragraph(sig_p, sml_s)]],
        colWidths=[W * .55, W * .45],
    )
    bt.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), .5, colors.black),
        ("LINEBEFORE",    (1, 0), (1,  0),  .5, colors.black),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(bt)
    doc.build(story)
    return buf.getvalue()


# ════════════════════════════════════════════════════════════════════════════════
#  STREAMLIT APP
# ════════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Sales Order Generator — SWASTIK",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Guard: show login if not authenticated ────────────────────────────────────
if not st.session_state.get("authenticated", False):
    show_login_page()
    st.stop()          # ← everything below is invisible until logged in


# ── Main app CSS (only loaded after login) ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f0f2fa; }
section.main > div { padding-top: 0 !important; }

.top-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: white; padding: 18px 28px; border-radius: 14px;
    margin-bottom: 20px; display: flex; align-items: center; gap: 16px;
}
.banner-logo {
    width: 44px; height: 44px; background: #2563eb; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 700; color: white; flex-shrink: 0;
}
.banner-title { font-size: 18px; font-weight: 600; }
.banner-sub   { font-size: 12px; color: rgba(255,255,255,.5); margin-top: 2px; }
.banner-right { margin-left: auto; display: flex; align-items: center; gap: 12px; }
.banner-user  {
    background: rgba(255,255,255,.1); color: #cbd5e1;
    padding: 5px 14px; border-radius: 99px; font-size: 12px; font-weight: 500;
}
.banner-badge {
    background: rgba(5,150,105,.25); color: #6ee7b7;
    padding: 5px 14px; border-radius: 99px; font-size: 12px; font-weight: 500;
}

.section-card {
    background: white; border-radius: 12px; padding: 20px 24px;
    margin-bottom: 16px; border: 1px solid #e2e4f0;
}
.section-title {
    font-size: 13px; font-weight: 600; color: #7a7a9d;
    letter-spacing: .8px; text-transform: uppercase;
    margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #f0f2fa;
}

.metric-row { display: flex; gap: 12px; margin-bottom: 16px; }
.metric-card {
    flex: 1; background: #f4f5fa; border-radius: 10px;
    padding: 14px 16px; border: 1px solid #e2e4f0;
}
.metric-label { font-size: 11px; color: #7a7a9d; font-weight: 500;
                letter-spacing: .5px; text-transform: uppercase; }
.metric-value { font-size: 20px; font-weight: 600; color: #1a1a2e; margin-top: 4px; }
.metric-card.accent { background: #eff6ff; border-color: #bfdbfe; }
.metric-card.accent .metric-value { color: #1d4ed8; }

.items-header {
    display: grid;
    grid-template-columns: 2.5fr 1.3fr 0.6fr 0.9fr 0.85fr 0.75fr 0.35fr;
    font-weight: bold; border-bottom: 1px solid #ccc; padding: 6px 0;
}
.items-header span { padding: 4px; }

div[data-testid="stButton"] > button { border-radius: 8px; font-weight: 500; }
div[data-testid="stDownloadButton"] > button {
    background: #2563eb !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    font-size: 15px !important; font-weight: 600 !important;
    padding: 12px 24px !important; width: 100%;
}
div[data-testid="stDownloadButton"] > button:hover { background: #1d4ed8 !important; }
div[data-testid="stInfo"],div[data-testid="stSuccess"],
div[data-testid="stWarning"],div[data-testid="stError"] { border-radius: 10px; }
div[data-testid="stExpander"] { border: 1px solid #e2e4f0 !important; border-radius: 10px !important; }
section[data-testid="stSidebar"] { background: #1a1a2e !important; }
section[data-testid="stSidebar"] * { color: rgba(255,255,255,.85) !important; }
hr { border-color: #e2e4f0; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ── Top banner (with logged-in user) ─────────────────────────────────────────
user_display = st.session_state.get("user_name", "User")
st.markdown(f"""
<div class="top-banner">
  <div class="banner-logo">S</div>
  <div>
    <div class="banner-title">SWASTIK ENTERPRISES</div>
    <div class="banner-sub">BELWARIYA, POST - MURDAHA, DISTRICT - VARANASI &nbsp;·&nbsp; GSTIN: 09QRFPS4600L1Z2</div>
  </div>
  <div class="banner-right">
    <span class="banner-user">👤 {user_display}</span>
    <span class="banner-badge">● Live Preview</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Logout button (top-right via sidebar trick)
with st.sidebar:
    st.markdown(f"### 👤 {user_display}")
    st.markdown("---")
    st.markdown(f"""
**{COMPANY_NAME}**

{COMPANY_ADDR1}

---
**{COMPANY_GSTIN}**

---
📞 +91 9936148679 (Ravindra Singh)  
📞 +91 9506114040 (Veer Singh)  
✉ swastikenterprises8679@gmail.com

---
**Bank Details**  
{BANK_DETAILS}

---
**Tax Rates**  
CGST: {CGST_RATE}%  
SGST: {SGST_RATE}%  
Total GST: {CGST_RATE + SGST_RATE}%
    """)
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for key in ["authenticated", "user_name", "username",
                    "login_error", "order_no", "order_items"]:
            st.session_state.pop(key, None)
        st.rerun()

# ── Session-state init ────────────────────────────────────────────────────────
if "order_no" not in st.session_state:
    st.session_state.order_no = gen_order_no()
if "order_items" not in st.session_state:
    st.session_state.order_items = [
        {"desc": d, "hsn": h, "qty": q, "unit": u, "price": p}
        for d, h, q, u, p in SAMPLE_ITEMS
    ]

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([1.4, 1], gap="large")

# ════════════════════════════════════════════════════════
#  LEFT — Form
# ════════════════════════════════════════════════════════
with left:

    st.markdown('<div class="section-card"><div class="section-title">🏢 Party Details</div>', unsafe_allow_html=True)
    party_name = st.text_input("Party Name *", placeholder="e.g. SHASHI ENTERPRISES")
    party_city = st.text_input("City *",        placeholder="e.g. VARANASI")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card"><div class="section-title">📋 Order Details</div>', unsafe_allow_html=True)
    col_no, col_btn = st.columns([3, 1])
    with col_no:
        order_no = st.text_input("Order Number *", value=st.session_state.order_no)
    with col_btn:
        st.write(""); st.write("")
        if st.button("↻ New", use_container_width=True):
            st.session_state.order_no = gen_order_no()
            st.rerun()
    order_date     = st.date_input("Order Date *", value=datetime.date.today())
    order_date_str = order_date.strftime("%d-%m-%Y")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card"><div class="section-title">📦 Line Items</div>', unsafe_allow_html=True)
    st.markdown("""
<style>
.items-header {
    display: grid;
    grid-template-columns: 2.5fr 1.3fr 0.6fr 0.9fr 0.85fr 0.75fr 0.35fr;
    font-weight: bold; border-bottom: 1px solid #ccc; padding: 6px 0;
}
.items-header span { padding: 4px; }
</style>
<div class="items-header">
  <span>Description</span><span>HSN/SAC</span><span>Qty</span>
  <span>Unit</span><span>Price (₹)</span><span>Amount</span><span></span>
</div>
""", unsafe_allow_html=True)

    row_list  = st.session_state.order_items
    to_delete = []

    for i, item in enumerate(row_list):
        c1, c2, c3, c4, c5, c6, c7 = st.columns([2.2, 1.3, .6, .9, .85, .75, .35])
        with c1:
            item["desc"]  = st.text_input("Desc",  value=item["desc"],  key=f"d{i}",
                                          label_visibility="collapsed", placeholder="Description")
        with c2:
            item["hsn"]   = st.text_input("HSN",   value=item["hsn"],   key=f"h{i}",
                                          label_visibility="collapsed", placeholder="HSN")
        with c3:
            item["qty"]   = st.number_input("Qty",   value=float(item["qty"]),  min_value=0.0,
                                            step=1.0, key=f"q{i}", label_visibility="collapsed", format="%.2f")
        with c4:
            item["unit"]  = st.selectbox("Unit", COMMON_UNITS,
                                         index=COMMON_UNITS.index(item["unit"]) if item["unit"] in COMMON_UNITS else 0,
                                         key=f"u{i}", label_visibility="collapsed")
        with c5:
            item["price"] = st.number_input("Price", value=float(item["price"]), min_value=0.0,
                                            step=10.0, key=f"p{i}", label_visibility="collapsed", format="%.2f")
        with c6:
            amt = item["qty"] * item["price"]
            st.markdown(f"<div style='padding:8px 4px;font-weight:600;font-size:13px;"
                        f"color:#1a1a2e;text-align:right'>₹{amt:,.2f}</div>",
                        unsafe_allow_html=True)
        with c7:
            if st.button("✕", key=f"del{i}", help="Remove row"):
                to_delete.append(i)

    for idx in reversed(to_delete):
        st.session_state.order_items.pop(idx)
        st.rerun()

    col_add, col_load = st.columns(2)
    with col_add:
        if st.button("＋ Add Row", use_container_width=True):
            st.session_state.order_items.append({"desc": "", "hsn": "", "qty": 1.0, "unit": "Pcs.", "price": 0.0})
            st.rerun()
    with col_load:
        if st.button("Load Sample Data", use_container_width=True):
            st.session_state.order_items = [
                {"desc": d, "hsn": h, "qty": q, "unit": u, "price": p}
                for d, h, q, u, p in SAMPLE_ITEMS
            ]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  RIGHT — Live summary + PDF
# ════════════════════════════════════════════════════════
with right:

    valid_items = [it for it in st.session_state.order_items if it["desc"].strip()]
    subtotal    = sum(it["qty"] * it["price"] for it in valid_items)
    cgst_amt    = round(subtotal * CGST_RATE / 100, 2)
    sgst_amt    = round(subtotal * SGST_RATE / 100, 2)
    total_tax   = round(cgst_amt + sgst_amt, 2)
    grand_total = round(subtotal + total_tax, 2)

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card">
        <div class="metric-label">Subtotal</div>
        <div class="metric-value">₹{subtotal:,.2f}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">CGST @ {CGST_RATE}%</div>
        <div class="metric-value">₹{cgst_amt:,.2f}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">SGST @ {SGST_RATE}%</div>
        <div class="metric-value">₹{sgst_amt:,.2f}</div>
      </div>
    </div>
    <div class="metric-row">
      <div class="metric-card accent" style="flex:1">
        <div class="metric-label">Grand Total (incl. GST)</div>
        <div class="metric-value" style="font-size:26px">₹{grand_total:,.2f}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"*{num_to_words(grand_total)}*")
    st.markdown("<hr/>", unsafe_allow_html=True)

    st.markdown('<div class="section-card"><div class="section-title">📄 Order Preview</div>', unsafe_allow_html=True)
    if order_no and party_name and party_city:
        st.markdown(f"""
        <table style="width:100%;font-size:13px;border-collapse:collapse">
          <tr><td style="color:#7a7a9d;padding:5px 0;width:45%">Order Number</td>
              <td style="font-weight:600;color:#1a1a2e">{order_no}</td></tr>
          <tr><td style="color:#7a7a9d;padding:5px 0">Date</td>
              <td style="font-weight:600;color:#1a1a2e">{order_date_str}</td></tr>
          <tr><td style="color:#7a7a9d;padding:5px 0">Party</td>
              <td style="font-weight:600;color:#1a1a2e">{party_name}, {party_city}</td></tr>
          <tr><td style="color:#7a7a9d;padding:5px 0">Line Items</td>
              <td style="font-weight:600;color:#1a1a2e">{len(valid_items)} item(s)</td></tr>
          <tr><td style="color:#7a7a9d;padding:5px 0">Warranty By</td>
              <td style="font-weight:600;color:#1a1a2e">{WARRANTY_BY}</td></tr>
        </table>
        """, unsafe_allow_html=True)
    else:
        st.info("Fill in party name, city, and order number to see preview.")
    st.markdown('</div>', unsafe_allow_html=True)

    if valid_items:
        with st.expander(f"📦 {len(valid_items)} Line Item(s) — Click to expand", expanded=False):
            for i, it in enumerate(valid_items, 1):
                amt = it["qty"] * it["price"]
                st.markdown(
                    f"**{i}. {it['desc']}**  \n"
                    f"HSN: `{it['hsn']}` &nbsp;|&nbsp; "
                    f"{it['qty']} {it['unit']} × ₹{it['price']:,.2f} = **₹{amt:,.2f}**"
                )
                if i < len(valid_items):
                    st.markdown("<hr style='margin:6px 0;border-color:#f0f2fa'>", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
    errors = []
    if not party_name.strip(): errors.append("Party Name is required.")
    if not party_city.strip():  errors.append("City is required.")
    if not order_no.strip():    errors.append("Order Number is required.")
    if not valid_items:         errors.append("Add at least one item with a description.")

    if errors:
        for e in errors:
            st.warning(e)
    else:
        pdf_bytes = build_pdf(
            party_name.strip(), party_city.strip(),
            order_no.strip(), order_date_str, valid_items,
        )
        st.success(f"✅ Ready to generate — Grand Total ₹{grand_total:,.2f}")
        st.download_button(
            label="⬇  Download Sales Order PDF",
            data=pdf_bytes,
            file_name=f"SalesOrder_{order_no}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.caption(f"PDF will be saved as `SalesOrder_{order_no}.pdf`")
