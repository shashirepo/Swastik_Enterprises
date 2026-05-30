"""
Sales Order Generator — SWASTIK ENTERPRISES
Run with:  streamlit run sales_order_streamlit.py
Requires:  pip install streamlit reportlab Pillow
"""

import io
import os
import hashlib
import random
import string
import datetime
import base64

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    Image as RLImage, SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable,
)

# ── Constants ─────────────────────────────────────────────────────────────────
COMPANY_NAME  = "SWASTIK ENTERPRISES"
COMPANY_ADDR1 = "BELWARIYA, POST - MURDAHA, DISTRICT - VARANASI, UTTAR PRADESH, INDIA, PIN-221202"
COMPANY_GSTIN = "GSTIN : 09QRFPS4600L1Z2"
COMPANY_TEL   = "Tel. : +91 9936148679 (Ravindra Singh) , +91 9506114040 (Veer Singh)"
COMPANY_EMAIL = "Email : swastikenterprises8679@gmail.com"
WARRANTY_BY   = "SWASTIK ENTERPRISES"

# Bank details — editable here or via Streamlit UI
BANK_NAME        = "Indian Overseas Bank"
BANK_BRANCH      = "Parmanandpur, Varanasi"
BANK_ACCOUNT_NO  = "346702000000466"
BANK_IFSC        = "IOBA0003467"
BANK_HOLDER      = "SWASTIK ENTERPRISES"

TERMS = [
    "Goods once sold will not be taken back.",
    "Interest @ 18% p.a. will be charged if the payment is not made within the stipulated time.",
]
CGST_RATE = 9.0
SGST_RATE = 9.0
LOGO_PATH = "logo2.jpeg"   # place logo file next to this script
QR_PATH   = "qr_code.jpeg"  # place QR code image next to this script
SIG_PATH  = "sign.jpg"       # place signature image next to this script

COMMON_UNITS = ["Pcs.", "MTR", "KG", "Set", "Pair", "Box", "Roll", "Ltr", "Nos."]

SAMPLE_ITEMS = [
    ("SOLAR STRUCTURE C CHANNEL 80*40 - PCS", "73089030", 1.0, "Pcs.", 1452.50, "GENERIC", 18.0),
    ("SOLAR APOLLO PLAIN STRUT*41*41 - PCS",  "73089030", 1.0, "Pcs.", 1120.50, "GENERIC", 18.0),
]

# ════════════════════════════════════════════════════════════════════════════════
#  AUTH
# ════════════════════════════════════════════════════════════════════════════════
def _hash(p):
    return hashlib.sha256(p.encode()).hexdigest()

def _load_users():
    defaults = {
        "admin":    {"name": "Administrator",  "password_hash": "cfad5ccaf32fb8765202858e5a6d7f6b2e88b9ca8f4d0cd433590163fd384f7e"},
        "ravindra": {"name": "Ravindra Singh", "password_hash": "6396c7fb51044fedab8e8d0278c072269fa2a8c0f8f4704ef26d1c8a5e359ff3"},
        "veer":     {"name": "Veer Singh",     "password_hash": "6396c7fb51044fedab8e8d0278c072269fa2a8c0f8f4704ef26d1c8a5e359ff3"},
    }
    try:
        users_secret = st.secrets["auth"]["users"]
        loaded = {}
        for uname, udata in users_secret.items():
            loaded[uname.strip().lower()] = {
                "name":          str(udata["name"]).strip(),
                "password_hash": str(udata["password_hash"]).strip(),
            }
        return loaded if loaded else defaults
    except Exception:
        return defaults

def check_login(username, password):
    username = username.strip().lower()
    password = password.strip()
    users = _load_users()
    user  = users.get(username)
    if user and user["password_hash"] == _hash(password):
        return True, user["name"]
    return False, ""

def show_login_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%) !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown("""
        <div style="background:white;border-radius:20px;padding:44px 40px 36px;
                    box-shadow:0 20px 60px rgba(0,0,0,.35);text-align:center;margin-top:60px">
          <div style="width:64px;height:64px;background:linear-gradient(135deg,#2563eb,#1d4ed8);
                      border-radius:16px;display:flex;align-items:center;justify-content:center;
                      font-size:28px;color:white;font-weight:700;margin:0 auto 16px">S</div>
          <div style="font-size:22px;font-weight:700;color:#1a1a2e;margin-bottom:4px">SWASTIK ENTERPRISES</div>
          <div style="font-size:13px;color:#7a7a9d;margin-bottom:28px">Sales Order Generator &nbsp;·&nbsp; Sign in to continue</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("login_error"):
            st.error("❌ Invalid username or password.")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

        if submitted:
            ok, name = check_login(username, password)
            if ok:
                st.session_state.authenticated = True
                st.session_state.user_name     = name
                st.session_state.login_error   = False
                st.rerun()
            else:
                st.session_state.login_error = True
                st.rerun()

        with st.expander("🔧 Troubleshoot login"):
            dp = st.text_input("Type password to get its hash", type="password", key="dbg")
            if dp:
                st.code(_hash(dp.strip()), language=None)
            if st.button("Show loaded users"):
                for u, d in _load_users().items():
                    st.write(f"• **{u}** → {d['name']} | hash: `{d['password_hash'][:14]}…`")

        st.markdown("<p style='text-align:center;font-size:11px;color:#aaa;margin-top:16px'>"
                    "🔒 Secured · SWASTIK ENTERPRISES © 2024</p>", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def gen_order_no():
    return "SWSENT" + "".join(random.choices(string.digits, k=3))

def num_to_words(amount):
    ones = ["","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten",
            "Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen","Seventeen","Eighteen","Nineteen"]
    tens = ["","","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]
    def two(n): return ones[n] if n<20 else (tens[n//10]+(" "+ones[n%10] if n%10 else "")).strip()
    def three(n): return (ones[n//100]+" Hundred"+(" "+two(n%100) if n%100 else "")) if n>=100 else two(n)
    rupees, paise = int(amount), round((amount-int(amount))*100)
    parts = []
    for div, label in [(10_00_00_000,"Arab"),(1_00_00_000,"Crore"),(1_00_000,"Lakh"),(1_000,"Thousand")]:
        if rupees >= div:
            parts.append(three(rupees//div)+" "+label); rupees %= div
    if rupees: parts.append(three(rupees))
    result = "Rupees "+(" ".join(parts) if parts else "Zero")
    if paise: result += f" and Paisa {two(paise)}"
    return result + " Only"

def img_to_rl(img_bytes, width_mm, height_mm):
    """Convert raw image bytes → ReportLab Image flowable."""
    from PIL import Image as PILImage
    img = PILImage.open(io.BytesIO(img_bytes)).convert("RGBA")
    bg  = PILImage.new("RGB", img.size, (255,255,255))
    bg.paste(img, mask=img.split()[3])
    out = io.BytesIO(); bg.save(out, format="PNG"); out.seek(0)
    return RLImage(out, width=width_mm*mm, height=height_mm*mm)


# ── PDF builder ───────────────────────────────────────────────────────────────
def build_pdf(party_name, party_city, order_no, order_date, items,
              qr_bytes=None, sig_bytes=None,
              bank_name=BANK_NAME, bank_branch=BANK_BRANCH,
              bank_acno=BANK_ACCOUNT_NO, bank_ifsc=BANK_IFSC,
              bank_holder=BANK_HOLDER) -> bytes:

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=12*mm, bottomMargin=12*mm)
    W = A4[0] - 30*mm
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    title_s = ps("T",  fontSize=14, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6)
    ctr_s   = ps("C",  fontSize=8,  alignment=TA_CENTER, leading=11)
    lft_s   = ps("L",  fontSize=8,  alignment=TA_LEFT,   leading=11)
    sml_s   = ps("S",  fontSize=7,  alignment=TA_LEFT,   leading=10)
    sml_b   = ps("SB", fontSize=7,  fontName="Helvetica-Bold", alignment=TA_LEFT, leading=10)
    rgt_s   = ps("R",  fontSize=8,  alignment=TA_RIGHT,  leading=11)
    bold_c  = ps("BC", fontSize=8,  fontName="Helvetica-Bold", alignment=TA_CENTER)

    story = []

    # ── Company header ───────────────────────────────────────────────────────
    try:
        logo = RLImage(LOGO_PATH, width=33*mm, height=30*mm)
    except Exception:
        logo = Paragraph("", lft_s)

    header_text = [
        Paragraph("<u>ORDER ESTIMATION</u>", bold_c),
        Paragraph(COMPANY_NAME, title_s),
        Paragraph(COMPANY_ADDR1, ctr_s),
        Paragraph(COMPANY_GSTIN, ctr_s),
        Paragraph(f"{COMPANY_TEL}<br/>{COMPANY_EMAIL}", ctr_s),
    ]
    hdr_t = Table([[logo, header_text]], colWidths=[W*.20, W*.80])
    hdr_t.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1),.9, colors.black),
        ("VALIGN",        (0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1),4),
        ("RIGHTPADDING",  (0,0),(-1,-1),4),
        ("TOPPADDING",    (0,0),(-1,-1),3),
        ("BOTTOMPADDING", (0,0),(-1,-1),3),
    ]))
    story += [hdr_t, Spacer(1,5)]

    # ── Party / Order box ────────────────────────────────────────────────────
    party_p = f"<b>Party Details :</b><br/>{party_name}<br/>{party_city}"
    order_p = f"<b>Order No. :</b> {order_no}<br/><b>Dated :</b> {order_date}"
    pt = Table([[Paragraph(party_p,lft_s), Paragraph(order_p,lft_s)]],
               colWidths=[W*.55, W*.45])
    pt.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1),.5,colors.black),
        ("LINEBEFORE",    (1,0),(1,0),  .5,colors.black),
        ("VALIGN",        (0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1),4),
        ("RIGHTPADDING",  (0,0),(-1,-1),4),
        ("TOPPADDING",    (0,0),(-1,-1),3),
        ("BOTTOMPADDING", (0,0),(-1,-1),3),
    ]))
    story += [pt, Spacer(1,2*mm),
              Paragraph("We are pleased to receive the order for the following items :", lft_s),
              Spacer(1,1*mm)]

    # ── Items table ──────────────────────────────────────────────────────────
    hdr_s = ps("H", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_CENTER, leading=10)
    hdr_ls = ps("HL", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_LEFT, leading=10)
    hdr = [
        Paragraph("S.N.",                hdr_s),
        Paragraph("Description of Goods",hdr_ls),
        Paragraph("Brand",               hdr_s),
        Paragraph("HSN/SAC<br/>Code",    hdr_s),
        Paragraph("Qty.",                hdr_s),
        Paragraph("Unit",                hdr_s),
        Paragraph("GST%",               hdr_s),
        Paragraph("Price",               hdr_s),
        Paragraph("Amount(`)",           hdr_s),
    ]
    cw = [W*.04, W*.27, W*.09, W*.09, W*.06, W*.06, W*.06, W*.11, W*.12]    
    rows = [hdr]
    subtotal = total_qty = 0.0

    # Style for wrapping text inside table cells
    wrap_s  = ps("W",  fontSize=7.5, alignment=TA_LEFT,   leading=10, wordWrap='LTR')
    wrap_c  = ps("WC", fontSize=7.5, alignment=TA_CENTER, leading=10, wordWrap='LTR')
    wrap_r  = ps("WR", fontSize=7.5, alignment=TA_RIGHT,  leading=10, wordWrap='LTR')

    for i, it in enumerate(items, 1):
        item_gst = float(it.get("gst", 18.0))
        amt = round(it["qty"] * it["price"], 2)
        subtotal  += amt
        total_qty += it["qty"]
        rows.append([
            Paragraph(str(i),                wrap_c),
            Paragraph(it["desc"],            wrap_s),
            Paragraph(it.get("brand",""),    wrap_c),
            Paragraph(it["hsn"],             wrap_c),
            Paragraph(f"{it['qty']:.2f}",    wrap_c),
            Paragraph(it["unit"],            wrap_c),
            Paragraph(f"{item_gst:.0f}%",    wrap_c),
            Paragraph(f"{it['price']:,.2f}", wrap_r),
            Paragraph(f"{amt:,.2f}",         wrap_r),
        ])

    cgst    = round(sum(it["qty"]*it["price"]*float(it.get("gst",18.0))/2/100 for it in items), 2)
    sgst    = cgst
    tax     = round(cgst + sgst, 2)
    grand   = round(subtotal + tax, 2)
    avg_gst = round(sum(it["qty"]*it["price"]*float(it.get("gst",18.0)) for it in items)
                    / max(subtotal, 1), 1) if items else 18.0

    rows += [
        ["","","","","","","","",f"{subtotal:,.2f}"],
        ["","","","","","Add : CGST","","",f"{cgst:,.2f}"],
        ["","","","","","Add : SGST","","",f"{sgst:,.2f}"],
        ["","Grand Total","","",f"{int(total_qty)} Units","","","`",f"{grand:,.2f}"],
    ]
    n = len(rows)

    it_t = Table(rows, colWidths=cw, repeatRows=1)
    it_t.setStyle(TableStyle([
        ("BOX",           (0,0),   (-1,-1),  .5,colors.black),
        ("INNERGRID",     (0,0),   (-1,n-5), .3,colors.black),
        ("LINEABOVE",     (0,n-4), (-1,n-4), .5,colors.black),
        ("LINEABOVE",     (0,n-1), (-1,n-1), .5,colors.black),
        ("BACKGROUND",    (0,0),   (-1,0),   colors.Color(.92,.92,.92)),
        ("FONTNAME",      (0,0),   (-1,0),   "Helvetica-Bold"),
        ("FONTNAME",      (0,n-1), (-1,n-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),   (-1,-1),  7.5),
        # Alignment handled by Paragraph styles inside each cell
        ("VALIGN",        (0,0),   (-1,-1),  "MIDDLE"),
        ("LEFTPADDING",   (0,0),   (-1,-1),  2),
        ("RIGHTPADDING",  (0,0),   (-1,-1),  2),
        ("TOPPADDING",    (0,0),   (-1,-1),  2),
        ("BOTTOMPADDING", (0,0),   (-1,-1),  2),
        ("SPAN", (1, n-1), (4, n-1),
    ]))
    story += [it_t, Spacer(1,2*mm)]

    # ── Tax summary ──────────────────────────────────────────────────────────
    tax_rows = [
        ["Tax Rate","Taxable Amt.","CGST Amt.","SGST Amt.","Total Tax"],
        [f"{avg_gst:.1f}%", f"{subtotal:,.2f}", f"{cgst:,.2f}", f"{sgst:,.2f}", f"{tax:,.2f}"],
    ]
    tt = Table(tax_rows, colWidths=[W*.12,W*.22,W*.22,W*.22,W*.22])
    tt.setStyle(TableStyle([
        ("FONTNAME",  (0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",  (0,0),(-1,-1),7.5),
        ("ALIGN",     (0,0),(-1,-1),"CENTER"),
        ("VALIGN",    (0,0),(-1,-1),"MIDDLE"),
        ("LINEBELOW", (0,0),(-1,0), .5,colors.black),
    ]))
    story += [tt, Spacer(1,2*mm),
              Paragraph(f"<i>{num_to_words(grand)}</i>", lft_s),
              Spacer(1,3*mm)]

    # ════════════════════════════════════════════════════════════════════════
    #  BANK DETAILS + TERMS + SIGNATURE — exactly like the image
    #  Layout:
    #  ┌─────────────────────────────┬──────────────────────────────┐
    #  │  [QR]  Bank Details:        │  Terms & Conditions:         │
    #  │        Name: ...            │  Thanks for doing business…  │
    #  │        A/c No: ...          │                              │
    #  │        IFSC: ...            │  For M/S-SWASTIK ENTERPRISES │
    #  │        Holder: ...          │                              │
    #  │                             │  [signature image]           │
    #  │                             │  Authorized Signatory        │
    #  └─────────────────────────────┴──────────────────────────────┘
    # ════════════════════════════════════════════════════════════════════════

    BANK_W = W * 0.50
    SIGN_W = W * 0.50

    # ── Left cell: QR + Bank info ────────────────────────────────────────────
    bank_title = Paragraph("<b>Bank Details:</b>", sml_b)
    bank_info  = Paragraph(
        f"Name &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <b>{bank_name}</b>, {bank_branch}<br/>"
        f"Account No. : <b>{bank_acno}</b><br/>"
        f"IFSC code &nbsp;: <b>{bank_ifsc}</b><br/>"
        f"Account holder's name : <b>{bank_holder}</b>",
        sml_s
    )

    if qr_bytes:
        try:
            qr_img = img_to_rl(qr_bytes, 22, 22)
            bank_cell = Table(
                [[qr_img, [bank_title, Spacer(1,2), bank_info]]],
                colWidths=[24*mm, BANK_W - 28*mm],
            )
            bank_cell.setStyle(TableStyle([
                ("VALIGN",        (0,0),(-1,-1),"TOP"),
                ("LEFTPADDING",   (0,0),(-1,-1),2),
                ("RIGHTPADDING",  (0,0),(-1,-1),2),
                ("TOPPADDING",    (0,0),(-1,-1),2),
                ("BOTTOMPADDING", (0,0),(-1,-1),2),
            ]))
        except Exception:
            bank_cell = [bank_title, Spacer(1,2), bank_info]
    else:
        bank_cell = [bank_title, Spacer(1,2), bank_info]

    # ── Right cell: Terms + Signature ────────────────────────────────────────
    terms_title = Paragraph("<b>Terms &amp; Conditions:</b>", sml_b)
    thanks_p    = Paragraph("Thanks for doing business with us!", sml_s)

    terms_items = []
    for j, t in enumerate(TERMS, 1):
        terms_items.append(Paragraph(f"{j}. {t}", sml_s))

    for_p = Paragraph(f"<b>For M/S-{COMPANY_NAME}:</b>", sml_s)

    if sig_bytes:
        try:
            sig_img = img_to_rl(sig_bytes, 30, 14)
        except Exception:
            sig_img = Spacer(1, 14*mm)
    else:
        sig_img = Spacer(1, 14*mm)   # blank space for wet signature

    auth_p = Paragraph("Authorized Signatory", sml_s)

    right_content = [terms_title, Spacer(1,3), thanks_p, Spacer(1,3)]
    right_content += terms_items
    right_content += [Spacer(1,4), for_p, Spacer(1,3), sig_img, auth_p]

    # ── Outer footer table ───────────────────────────────────────────────────
    footer_t = Table(
        [[bank_cell, right_content]],
        colWidths=[BANK_W, SIGN_W],
    )
    footer_t.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1),.5,colors.black),
        ("LINEBEFORE",    (1,0),(1,0),  .5,colors.black),
        ("VALIGN",        (0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1),5),
        ("RIGHTPADDING",  (0,0),(-1,-1),5),
        ("TOPPADDING",    (0,0),(-1,-1),5),
        ("BOTTOMPADDING", (0,0),(-1,-1),5),
    ]))
    story.append(footer_t)

    doc.build(story)
    return buf.getvalue()


# ════════════════════════════════════════════════════════════════════════════════
#  STREAMLIT APP
# ════════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Sales Order Generator", page_icon="🧾",
                   layout="wide", initial_sidebar_state="collapsed")

# ── Guard ─────────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    show_login_page()
    st.stop()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background:#f0f2fa;}
section.main>div{padding-top:0!important;}
.top-banner{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);color:white;
    padding:18px 28px;border-radius:14px;margin-bottom:20px;
    display:flex;align-items:center;gap:16px;}
.banner-logo{width:44px;height:44px;background:#2563eb;border-radius:10px;
    display:flex;align-items:center;justify-content:center;
    font-size:20px;font-weight:700;color:white;flex-shrink:0;}
.banner-title{font-size:18px;font-weight:600;}
.banner-sub{font-size:12px;color:rgba(255,255,255,.5);margin-top:2px;}
.banner-right{margin-left:auto;display:flex;align-items:center;gap:12px;}
.banner-user{background:rgba(255,255,255,.1);color:#cbd5e1;
    padding:5px 14px;border-radius:99px;font-size:12px;font-weight:500;}
.banner-badge{background:rgba(5,150,105,.25);color:#6ee7b7;
    padding:5px 14px;border-radius:99px;font-size:12px;font-weight:500;}
.section-card{background:white;border-radius:12px;padding:20px 24px;
    margin-bottom:16px;border:1px solid #e2e4f0;}
.section-title{font-size:13px;font-weight:600;color:#7a7a9d;letter-spacing:.8px;
    text-transform:uppercase;margin-bottom:14px;padding-bottom:10px;
    border-bottom:1px solid #f0f2fa;}
.metric-row{display:flex;gap:12px;margin-bottom:16px;}
.metric-card{flex:1;background:#f4f5fa;border-radius:10px;
    padding:14px 16px;border:1px solid #e2e4f0;}
.metric-label{font-size:11px;color:#7a7a9d;font-weight:500;
    letter-spacing:.5px;text-transform:uppercase;}
.metric-value{font-size:20px;font-weight:600;color:#1a1a2e;margin-top:4px;}
.metric-card.accent{background:#eff6ff;border-color:#bfdbfe;}
.metric-card.accent .metric-value{color:#1d4ed8;}
.bank-card{background:#f8faff;border:1.5px solid #bfdbfe;border-radius:12px;
    padding:16px 20px;margin-bottom:12px;}
.bank-row{display:flex;align-items:center;gap:10px;margin-bottom:6px;}
.bank-label{font-size:11px;color:#7a7a9d;font-weight:500;min-width:110px;}
.bank-val{font-size:13px;font-weight:600;color:#1a1a2e;}
div[data-testid="stDownloadButton"]>button{
    background:#2563eb!important;color:white!important;border:none!important;
    border-radius:10px!important;font-size:15px!important;font-weight:600!important;
    padding:12px 24px!important;width:100%;}
div[data-testid="stDownloadButton"]>button:hover{background:#1d4ed8!important;}
div[data-testid="stExpander"]{border:1px solid #e2e4f0!important;border-radius:10px!important;}
section[data-testid="stSidebar"]{background:#1a1a2e!important;}
section[data-testid="stSidebar"] *{color:rgba(255,255,255,.85)!important;}
hr{border-color:#e2e4f0;margin:16px 0;}
</style>
""", unsafe_allow_html=True)

user_display = st.session_state.get("user_name", "User")
st.markdown(f"""
<div class="top-banner">
  <div class="banner-logo">S</div>
  <div>
    <div class="banner-title">SWASTIK ENTERPRISES</div>
    <div class="banner-sub">BELWARIYA, VARANASI &nbsp;·&nbsp; GSTIN: 09QRFPS4600L1Z2</div>
  </div>
  <div class="banner-right">
    <span class="banner-user">👤 {user_display}</span>
    <span class="banner-badge">● Live</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👤 {user_display}")
    st.markdown("---")
    st.markdown(f"""
**{COMPANY_NAME}**  
{COMPANY_ADDR1}

---
**{COMPANY_GSTIN}**

📞 +91 9936148679 (Ravindra Singh)  
📞 +91 9506114040 (Veer Singh)  
✉ swastikenterprises8679@gmail.com

---
**Tax Rates**  
CGST: {CGST_RATE}% &nbsp; SGST: {SGST_RATE}%
    """)
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for k in ["authenticated","user_name","login_error","order_no","order_items",
                  "qr_bytes","sig_bytes"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── Session state init ────────────────────────────────────────────────────────
if "order_no"    not in st.session_state: st.session_state.order_no = gen_order_no()
if "order_items" not in st.session_state:
    st.session_state.order_items = [
        {"desc":d,"hsn":h,"qty":q,"unit":u,"price":p,"brand":br,"gst":g}
        for d,h,q,u,p,br,g in SAMPLE_ITEMS
    ]
if "qr_bytes" not in st.session_state:
    try:
        with open(QR_PATH, "rb") as _f:
            st.session_state.qr_bytes = _f.read()
    except Exception:
        st.session_state.qr_bytes = None

if "sig_bytes" not in st.session_state:
    try:
        with open(SIG_PATH, "rb") as _f:
            st.session_state.sig_bytes = _f.read()
    except Exception:
        st.session_state.sig_bytes = None
if "bank_name"   not in st.session_state: st.session_state.bank_name   = BANK_NAME
if "bank_branch" not in st.session_state: st.session_state.bank_branch = BANK_BRANCH
if "bank_acno"   not in st.session_state: st.session_state.bank_acno   = BANK_ACCOUNT_NO
if "bank_ifsc"   not in st.session_state: st.session_state.bank_ifsc   = BANK_IFSC
if "bank_holder" not in st.session_state: st.session_state.bank_holder = BANK_HOLDER

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([2, 1], gap="large")

# ════════════════════════════════════════
#  LEFT panel
# ════════════════════════════════════════
with left:

    # Party
    st.markdown('<div class="section-card"><div class="section-title">🏢 Party Details</div>', unsafe_allow_html=True)
    party_name = st.text_input("Party Name *", placeholder="e.g. SHASHI ENTERPRISES")
    party_city = st.text_input("City *",        placeholder="e.g. VARANASI")
    st.markdown('</div>', unsafe_allow_html=True)

    # Order
    st.markdown('<div class="section-card"><div class="section-title">📋 Order Details</div>', unsafe_allow_html=True)
    col_no, col_btn = st.columns([3,1])
    with col_no:
        order_no = st.text_input("Order Number *", value=st.session_state.order_no)
    with col_btn:
        st.write(""); st.write("")
        if st.button("↻ New", use_container_width=True):
            st.session_state.order_no = gen_order_no(); st.rerun()
    order_date     = st.date_input("Order Date *", value=datetime.date.today())
    order_date_str = order_date.strftime("%d-%m-%Y")
    st.markdown('</div>', unsafe_allow_html=True)

    # Items
    st.markdown('<div class="section-card"><div class="section-title">📦 Line Items</div>', unsafe_allow_html=True)
    st.markdown("""
<style>
.items-header{display:grid;grid-template-columns:2.8fr 1.0fr 0.9fr 0.6fr 1.0fr 0.6fr 0.7fr 0.65fr 0.35fr;
    background: #1a1a2e;border-radius: 8px;padding: 10px 12px;
    margin-bottom: 6px;
    }
    .items-header span {
    font-size: 11px;
    font-weight: 600;
    color: rgba(255,255,255,.7);
    letter-spacing: .5px;
    text-transform: uppercase;
    }
</style>
<div class="items-header">
  <span>Description</span>
  <span>Brand</span>
  <span>HSN/SAC</span>
  <span>Qty</span>
  <span>Unit</span>
  <span>GST%</span>
  <span>Price (&#8377;)</span>
  <span>Amount</span>
  <span></span>
</div>""", unsafe_allow_html=True)

    items = st.session_state.order_items
    to_delete = []

    for i, item in enumerate(items):
        c1,c2,c3,c4,c5,c6,c7,c8,c9 = st.columns([2.8,1.0,0.9,0.6,1.0,0.6,0.7,0.65,0.35])
        with c1: item["desc"]  = st.text_area("Desc",  value=item["desc"],          key=f"d{i}",  label_visibility="collapsed", placeholder="Description", height=68)
        with c2: item["brand"] = st.text_input("Brand", value=item.get("brand",""), key=f"br{i}", label_visibility="collapsed", placeholder="Brand")
        with c3: item["hsn"]   = st.text_input("HSN",   value=item["hsn"],          key=f"h{i}",  label_visibility="collapsed", placeholder="HSN")
        with c4: item["qty"]   = st.number_input("Qty",  value=float(item["qty"]),  min_value=0.0, step=1.0,  key=f"q{i}", label_visibility="collapsed", format="%.2f")
        with c5: item["unit"]  = st.selectbox("Unit", COMMON_UNITS, index=COMMON_UNITS.index(item["unit"]) if item["unit"] in COMMON_UNITS else 0, key=f"u{i}", label_visibility="collapsed")
        with c6: item["gst"]   = st.number_input("GST%", value=float(item.get("gst",18.0)), min_value=0.0, max_value=28.0, step=0.5, key=f"g{i}", label_visibility="collapsed", format="%.1f")
        with c7: item["price"] = st.number_input("Price", value=float(item["price"]), min_value=0.0, step=10.0, key=f"p{i}", label_visibility="collapsed", format="%.2f")
        with c8:
            amt = item["qty"]*item["price"]
            st.markdown(f"<div style='padding:8px 2px;font-weight:600;font-size:12px;color:#1a1a2e;text-align:right'>&#8377;{amt:,.2f}</div>", unsafe_allow_html=True)
        with c9:
            if st.button("✕", key=f"del{i}", help="Remove row"):
                to_delete.append(i)

    for idx in reversed(to_delete):
        st.session_state.order_items.pop(idx); st.rerun()

    ca, cl = st.columns(2)
    with ca:
        if st.button("＋ Add Row", use_container_width=True):
            st.session_state.order_items.append({"desc":"","hsn":"","qty":1.0,"unit":"Pcs.","price":0.0,"brand":"","gst":18.0})
            st.rerun()
    with cl:
        if st.button("Load Sample Data", use_container_width=True):
            st.session_state.order_items = [{"desc":d,"hsn":h,"qty":q,"unit":u,"price":p,"brand":br,"gst":g}
            for d,h,q,u,p,br,g in SAMPLE_ITEMS
            ]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Bank Details section ──────────────────────────────────────────────────
    st.markdown('<div class="section-card"><div class="section-title">🏦 Bank Details</div>', unsafe_allow_html=True)

    bc1, bc2 = st.columns(2)
    with bc1:
        st.session_state.bank_name   = st.text_input("Bank Name",      value=st.session_state.bank_name)
        st.session_state.bank_acno   = st.text_input("Account Number", value=st.session_state.bank_acno)
        st.session_state.bank_holder = st.text_input("Account Holder", value=st.session_state.bank_holder)
    with bc2:
        st.session_state.bank_branch = st.text_input("Branch",         value=st.session_state.bank_branch)
        st.session_state.bank_ifsc   = st.text_input("IFSC Code",      value=st.session_state.bank_ifsc)

    # QR & Signature loaded automatically from disk — show preview
    st.markdown("**QR Code & Signature** *(loaded automatically from files)*")
    uq, us = st.columns(2)
    with uq:
        if st.session_state.qr_bytes:
            st.image(st.session_state.qr_bytes, caption=f"✅ QR Code ({QR_PATH})", width=110)
        else:
            st.warning(f"⚠️ QR Code not found\nPlace `{QR_PATH}` next to the script.")
    with us:
        if st.session_state.sig_bytes:
            st.image(st.session_state.sig_bytes, caption=f"✅ Signature ({SIG_PATH})", width=130)
        else:
            st.warning(f"⚠️ Signature not found\nPlace `{SIG_PATH}` next to the script.")

    # Preview bank card
    st.markdown(f"""
    <div class="bank-card">
      <div style="font-size:13px;font-weight:700;color:#1d4ed8;margin-bottom:10px">🏦 Bank Details Preview</div>
      <div class="bank-row"><span class="bank-label">Bank Name</span><span class="bank-val">{st.session_state.bank_name}</span></div>
      <div class="bank-row"><span class="bank-label">Branch</span><span class="bank-val">{st.session_state.bank_branch}</span></div>
      <div class="bank-row"><span class="bank-label">Account No.</span><span class="bank-val">{st.session_state.bank_acno}</span></div>
      <div class="bank-row"><span class="bank-label">IFSC Code</span><span class="bank-val">{st.session_state.bank_ifsc}</span></div>
      <div class="bank-row"><span class="bank-label">Account Holder</span><span class="bank-val">{st.session_state.bank_holder}</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════
#  RIGHT panel
# ════════════════════════════════════════
with right:

    valid_items = [it for it in st.session_state.order_items if it["desc"].strip()]
    subtotal    = sum(it["qty"]*it["price"] for it in valid_items)
    cgst_amt    = round(subtotal*CGST_RATE/100, 2)
    sgst_amt    = round(subtotal*SGST_RATE/100, 2)
    grand_total = round(subtotal+cgst_amt+sgst_amt, 2)

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card"><div class="metric-label">Subtotal</div>
        <div class="metric-value">₹{subtotal:,.2f}</div></div>
      <div class="metric-card"><div class="metric-label">CGST @ {CGST_RATE}%</div>
        <div class="metric-value">₹{cgst_amt:,.2f}</div></div>
      <div class="metric-card"><div class="metric-label">SGST @ {SGST_RATE}%</div>
        <div class="metric-value">₹{sgst_amt:,.2f}</div></div>
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

    # Order preview
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
          <tr><td style="color:#7a7a9d;padding:5px 0">Items</td>
              <td style="font-weight:600;color:#1a1a2e">{len(valid_items)} item(s)</td></tr>
        </table>
        """, unsafe_allow_html=True)
    else:
        st.info("Fill in party name, city, and order number to see preview.")
    st.markdown('</div>', unsafe_allow_html=True)

    if valid_items:
        with st.expander(f"📦 {len(valid_items)} Item(s) — click to expand"):
            for i, it in enumerate(valid_items, 1):
                amt = it["qty"]*it["price"]
                st.markdown(f"**{i}. {it['desc']}**  \n"
                            f"HSN: `{it['hsn']}` | {it['qty']} {it['unit']} × ₹{it['price']:,.2f} = **₹{amt:,.2f}**")
                if i < len(valid_items):
                    st.markdown("<hr style='margin:6px 0;border-color:#f0f2fa'>", unsafe_allow_html=True)

    # QR/Sig status
    qr_ok  = "✅ Uploaded" if st.session_state.qr_bytes  else "⚠️ Not uploaded"
    sig_ok = "✅ Uploaded" if st.session_state.sig_bytes else "⚠️ Not uploaded"
    st.markdown(f"""
    <div style="background:#f4f5fa;border-radius:10px;padding:12px 16px;
                margin:12px 0;border:1px solid #e2e4f0;font-size:12px;">
      <b>PDF Footer Assets</b><br/>
      QR Code: {qr_ok} &nbsp;|&nbsp; Signature: {sig_ok}
    </div>
    """, unsafe_allow_html=True)

    # Download
    st.markdown("<hr/>", unsafe_allow_html=True)
    errors = []
    if not party_name.strip(): errors.append("Party Name is required.")
    if not party_city.strip():  errors.append("City is required.")
    if not order_no.strip():    errors.append("Order Number is required.")
    if not valid_items:         errors.append("Add at least one item with a description.")

    if errors:
        for e in errors: st.warning(e)
    else:
        pdf_bytes = build_pdf(
            party_name.strip(), party_city.strip(),
            order_no.strip(), order_date_str, valid_items,
            qr_bytes=st.session_state.qr_bytes,
            sig_bytes=st.session_state.sig_bytes,
            bank_name=st.session_state.bank_name,
            bank_branch=st.session_state.bank_branch,
            bank_acno=st.session_state.bank_acno,
            bank_ifsc=st.session_state.bank_ifsc,
            bank_holder=st.session_state.bank_holder,
        )
        st.success(f"✅ Ready — Grand Total ₹{grand_total:,.2f}")
        st.download_button(
            label="⬇  Download Sales Order PDF",
            data=pdf_bytes,
            file_name=f"SalesOrder_{order_no}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.caption(f"Saves as `SalesOrder_{order_no}.pdf`")
