"""
Sales Order Generator — SWASTIK ENTERPRISES
Run with:  streamlit run sales_order_streamlit.py
Requires:  pip install streamlit reportlab Pillow
"""

import io, hashlib, random, string, datetime
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
BANK_DETAILS  = "Bank: Indian Overseas Bank  A/c No:346702000000466, IFSC :IOBA0003467  BRANCH: PARMANANDPUR, VARANASI"
TERMS = [
    "Goods once sold will not be taken back.",
    "Interest @ 18% p.a. will be charged if the payment is not made within the stipulated time.",
]

LOGO_PATH = "logo2.jpeg"
QR_PATH   = "qr_code.jpeg"
SIG_PATH  = "sign.jpg"

# Available GST rates (matching GRS Solar style: 5% and 18% are most common)
GST_OPTIONS   = [0.0, 5.0, 12.0, 18.0, 28.0]
COMMON_UNITS  = ["Pcs.", "MTR", "KG", "Set", "Pair", "Bag", "Box", "Roll", "Ltr", "Nos.", "Mtr"]

SAMPLE_ITEMS = [
    ("SOLAR PANEL 650WP BIFACIAL",                   "85414300", 6.0,  "Pcs.", 20000.00, "NDCR",    5.0),
    ("INVERTER 10KW ON GRID",                        "85044010", 1.0,  "Pcs.", 44500.00, "MICROTEK", 18.0),
    ("SOLAR STRUCTURE (MEDIUM 3FT X 5FT)",           "73089030", 1.0,  "Set",  13500.00, "GENERIC",  18.0),
    ("ANCHOR FASTENER M10",                          "73181500", 20.0, "Pcs.",    15.00, "GENERIC",  18.0),
    ("CHEMICAL BAG 15KG",                            "25081010", 1.0,  "Bag",    175.00, "GENERIC",  18.0),
    ("ACDB 1IN 1OUT",                                "85371000", 1.0,  "Pcs.",  1550.00, "GENERIC",  18.0),
    ("DCDB BOX",                                     "85371000", 1.0,  "Pcs.",  1550.00, "GENERIC",  18.0),
    ("MC4 CONNECTOR PAIR",                           "85366990", 25.0, "Pcs.",    30.00, "GENERIC",  18.0),
    ("4MM DC CABLE BLACK/RED",                       "85441990", 50.0, "MTR",     40.00, "POLYCAB",  18.0),
    ("SERVICE CHARGE",                               "9954",     1.0,  "Nos.",  3308.67, "",          18.0),
]

# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════
def _hash(p): return hashlib.sha256(p.encode()).hexdigest()

def _load_users():
    defaults = {
        "admin":    {"name": "Administrator",  "password_hash": "cfad5ccaf32fb8765202858e5a6d7f6b2e88b9ca8f4d0cd433590163fd384f7e"},
        "ravindra": {"name": "Ravindra Singh", "password_hash": "6396c7fb51044fedab8e8d0278c072269fa2a8c0f8f4704ef26d1c8a5e359ff3"},
        "veer":     {"name": "Veer Singh",     "password_hash": "6396c7fb51044fedab8e8d0278c072269fa2a8c0f8f4704ef26d1c8a5e359ff3"},
    }
    try:
        us = st.secrets["auth"]["users"]
        loaded = {u.strip().lower(): {"name": str(d["name"]).strip(),
                  "password_hash": str(d["password_hash"]).strip()} for u,d in us.items()}
        return loaded if loaded else defaults
    except Exception:
        return defaults

def check_login(username, password):
    u, p = username.strip().lower(), password.strip()
    user = _load_users().get(u)
    return (True, user["name"]) if user and user["password_hash"] == _hash(p) else (False, "")

def show_login_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
    html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
    .stApp{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%)!important;}
    #MainMenu,footer,header{visibility:hidden;}
    </style>""", unsafe_allow_html=True)
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
        </div>""", unsafe_allow_html=True)
        if st.session_state.get("login_error"): st.error("❌ Invalid username or password.")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)
        if submitted:
            ok, name = check_login(username, password)
            if ok:
                st.session_state.authenticated = True
                st.session_state.user_name = name
                st.session_state.login_error = False
                st.rerun()
            else:
                st.session_state.login_error = True; st.rerun()
        with st.expander("🔧 Troubleshoot login"):
            dp = st.text_input("Type password to get hash", type="password", key="dbg")
            if dp: st.code(_hash(dp.strip()), language=None)
            if st.button("Show loaded users"):
                for u, d in _load_users().items():
                    st.write(f"• **{u}** → {d['name']} | hash: `{d['password_hash'][:14]}…`")
        st.markdown("<p style='text-align:center;font-size:11px;color:#aaa;margin-top:16px'>"
                    "🔒 Secured · SWASTIK ENTERPRISES © 2024</p>", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def gen_order_no(): return "SWSENT" + "".join(random.choices(string.digits, k=3))

def num_to_words(amount):
    ones=["","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten",
          "Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen","Seventeen","Eighteen","Nineteen"]
    tens=["","","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]
    def two(n): return ones[n] if n<20 else (tens[n//10]+(" "+ones[n%10] if n%10 else "")).strip()
    def three(n): return (ones[n//100]+" Hundred"+(" "+two(n%100) if n%100 else "")) if n>=100 else two(n)
    rupees,paise=int(amount),round((amount-int(amount))*100)
    parts=[]
    for div,label in [(10_00_00_000,"Arab"),(1_00_00_000,"Crore"),(1_00_000,"Lakh"),(1_000,"Thousand")]:
        if rupees>=div: parts.append(three(rupees//div)+" "+label); rupees%=div
    if rupees: parts.append(three(rupees))
    result="Rupees "+(" ".join(parts) if parts else "Zero")
    if paise: result+=f" and Paisa {two(paise)}"
    return result+" Only"

def img_to_rl(img_bytes, w_mm, h_mm):
    from PIL import Image as PILImage
    img=PILImage.open(io.BytesIO(img_bytes)).convert("RGBA")
    bg=PILImage.new("RGB",img.size,(255,255,255)); bg.paste(img,mask=img.split()[3])
    out=io.BytesIO(); bg.save(out,format="PNG"); out.seek(0)
    return RLImage(out, width=w_mm*mm, height=h_mm*mm)

def calc_gst_groups(items):
    """
    Returns dict: { gst_rate_float: {"taxable": x, "cgst": y, "sgst": z} }
    Groups items by their GST rate and sums up.
    Mirrors GRS Solar PDF: each GST rate gets its own row in tax summary.
    """
    groups = {}
    for it in items:
        rate = float(it.get("gst", 18.0))
        amt  = round(it["qty"] * it["price"], 2)
        if rate not in groups:
            groups[rate] = {"taxable": 0.0, "cgst": 0.0, "sgst": 0.0}
        cgst = round(amt * rate / 2 / 100, 2)
        sgst = round(amt * rate / 2 / 100, 2)
        groups[rate]["taxable"] += amt
        groups[rate]["cgst"]    += cgst
        groups[rate]["sgst"]    += sgst
    # round final values
    for r in groups:
        groups[r]["taxable"] = round(groups[r]["taxable"], 2)
        groups[r]["cgst"]    = round(groups[r]["cgst"],    2)
        groups[r]["sgst"]    = round(groups[r]["sgst"],    2)
    return groups

# ══════════════════════════════════════════════════════════════════════════════
#  PDF BUILDER
# ══════════════════════════════════════════════════════════════════════════════
def build_pdf(party_name, party_city, order_no, order_date, items,
              qr_bytes=None, sig_bytes=None) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=12*mm, bottomMargin=12*mm)
    W = A4[0] - 30*mm
    base = getSampleStyleSheet()

    def ps(name, **kw): return ParagraphStyle(name, parent=base["Normal"], **kw)

    title_s = ps("T",   fontSize=14, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    ctr_s   = ps("C",   fontSize=8,  alignment=TA_CENTER, leading=11)
    lft_s   = ps("L",   fontSize=8,  alignment=TA_LEFT,   leading=11)
    sml_s   = ps("S",   fontSize=7,  alignment=TA_LEFT,   leading=10)
    sml_b   = ps("SB",  fontSize=7,  fontName="Helvetica-Bold", alignment=TA_LEFT,   leading=10)
    rgt_s   = ps("R",   fontSize=8,  alignment=TA_RIGHT,  leading=11)
    bold_c  = ps("BC",  fontSize=8,  fontName="Helvetica-Bold", alignment=TA_CENTER)
    hdr_s   = ps("H",   fontSize=7.5,fontName="Helvetica-Bold", alignment=TA_CENTER, leading=10)
    hdr_ls  = ps("HL",  fontSize=7.5,fontName="Helvetica-Bold", alignment=TA_LEFT,   leading=10)
    wrap_s  = ps("WS",  fontSize=7.5,alignment=TA_LEFT,   leading=10, wordWrap="LTR")
    wrap_c  = ps("WC",  fontSize=7.5,alignment=TA_CENTER, leading=10, wordWrap="LTR")
    wrap_r  = ps("WR",  fontSize=7.5,alignment=TA_RIGHT,  leading=10, wordWrap="LTR")
    italic_s= ps("IT",  fontSize=8,  alignment=TA_LEFT,   leading=11)

    story = []

    # ── Header ───────────────────────────────────────────────────────────────
    try:    logo = RLImage(LOGO_PATH, width=33*mm, height=30*mm)
    except: logo = Paragraph("", lft_s)

    hdr_txt = [
        Paragraph("<u>ORDER ESTIMATION</u>", bold_c),
        Paragraph(COMPANY_NAME, title_s),
        Paragraph(COMPANY_ADDR1, ctr_s),
        Paragraph(COMPANY_GSTIN, ctr_s),
        Paragraph(f"{COMPANY_TEL}<br/>{COMPANY_EMAIL}", ctr_s),
    ]
    ht = Table([[logo, hdr_txt]], colWidths=[W*.20, W*.80])
    ht.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),.9,colors.black),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    story += [ht, Spacer(1,5)]

    # ── Party / Order box ────────────────────────────────────────────────────
    pp = f"<b>Party Details :</b><br/>{party_name}<br/>{party_city}"
    op = f"<b>Order No. :</b> {order_no}<br/><b>Dated :</b> {order_date}"
    pt = Table([[Paragraph(pp,lft_s), Paragraph(op,lft_s)]], colWidths=[W*.55,W*.45])
    pt.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),.5,colors.black),("LINEBEFORE",(1,0),(1,0),.5,colors.black),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    story += [pt, Spacer(1,2*mm),
              Paragraph("We are pleased to receive the order for the following items :", lft_s),
              Spacer(1,1*mm)]

    # ── Items table (9 columns with Brand + GST%) ────────────────────────────
    hdr_row = [
        Paragraph("S.N.",                hdr_s),
        Paragraph("Description of Goods",hdr_ls),
        Paragraph("Brand",               hdr_s),
        Paragraph("HSN/SAC<br/>Code",    hdr_s),
        Paragraph("Qty.",                hdr_s),
        Paragraph("Unit",                hdr_s),
        Paragraph("GST%",               hdr_s),
        Paragraph("Rate",                hdr_s),
        Paragraph("Amount",              hdr_s),
    ]
    cw = [W*.04, W*.27, W*.09, W*.09, W*.06, W*.06, W*.06, W*.11, W*.12]

    rows = [hdr_row]
    subtotal = total_qty = 0.0

    for i, it in enumerate(items, 1):
        item_gst = float(it.get("gst", 18.0))
        amt = round(it["qty"] * it["price"], 2)
        subtotal  += amt
        total_qty += it["qty"]
        rows.append([
            Paragraph(str(i),                   wrap_c),
            Paragraph(it["desc"],               wrap_s),
            Paragraph(it.get("brand",""),       wrap_c),
            Paragraph(it["hsn"],                wrap_c),
            Paragraph(f"{it['qty']:.2f}",       wrap_c),
            Paragraph(it["unit"],               wrap_c),
            Paragraph(f"{item_gst:.1f}%",       wrap_c),
            Paragraph(f"{it['price']:,.2f}",    wrap_r),
            Paragraph(f"{amt:,.2f}",            wrap_r),
        ])

    # ── GST calculation: grouped by rate (GRS Solar style) ──────────────────
    gst_groups = calc_gst_groups(items)
    total_cgst = round(sum(g["cgst"] for g in gst_groups.values()), 2)
    total_sgst = round(sum(g["sgst"] for g in gst_groups.values()), 2)
    total_tax  = round(total_cgst + total_sgst, 2)
    grand      = round(subtotal + total_tax, 2)

    # Subtotal row
    rows.append(["","","","","","","","", f"{subtotal:,.2f}"])

    # One CGST row + one SGST row per GST rate group
    # Compact GST rows (no extra height)
    for rate in sorted(gst_groups.keys()):
        g    = gst_groups[rate]
        half = rate / 2
    
        rows.append([
            "", "", "", "", "",
            Paragraph(f"CGST@{half:.1f}%", wrap_r),
            "", "",
            Paragraph(f"{g['cgst']:,.2f}", wrap_r)
        ])
    
        rows.append([
            "", "", "", "", "",
            Paragraph(f"SGST@{half:.1f}%", wrap_r),
            "", "",
            Paragraph(f"{g['sgst']:,.2f}", wrap_r)
        ])

    # Round off
    round_off = round(round(grand) - grand, 2)
    if round_off != 0:
        rows.append(["","","","","",
                     Paragraph("Round Off", wrap_s),
                     "","", f"{round_off:,.2f}"])
    grand_rounded = round(grand + round_off)

    # Grand total row
    rows.append(["",
                 Paragraph("<b>Grand Total</b>", wrap_s),
                 "","",
                 f"{int(total_qty)} Units",
                 "","","",
                 Paragraph(f"<b>{grand_rounded:,.2f}</b>", wrap_r)])

    n = len(rows)
    # number of trailing summary rows (cgst+sgst per group + roundoff + grandtotal)
    n_tail = sum(2 for _ in gst_groups) + (1 if round_off else 0) + 2  # +subtotal +grand

    it_t = Table(rows, colWidths=cw, repeatRows=1)
    it_t.setStyle(TableStyle([
        ("BOX",           (0,0),     (-1,-1),      .5, colors.black),
        ("INNERGRID",     (0,0),     (-1, n-n_tail),.3, colors.black),
        ("LINEABOVE",     (0, n-n_tail), (-1, n-n_tail), .5, colors.black),
        ("LINEABOVE",     (0, n-1),  (-1, n-1),    .8, colors.black),
        ("BACKGROUND",    (0,0),     (-1,0),       colors.Color(.92,.92,.92)),
        ("BACKGROUND",    (0,n-1),   (-1,n-1),     colors.Color(.88,.92,.98)),
        ("FONTNAME",      (0,0),     (-1,0),       "Helvetica-Bold"),
        ("FONTNAME",      (0,n-1),   (-1,n-1),     "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),     (-1,-1),      7.5),
        ("ALIGN",         (0,0),     (-1,-1),      "CENTER"),
        ("ALIGN",         (5,n-n_tail),(5,n-2),    "RIGHT"),
        ("ALIGN",         (8,1),     (8,-1),       "RIGHT"),
        ("VALIGN",        (0,0),     (-1,-1),      "MIDDLE"),
        ("LEFTPADDING",   (0,0),     (-1,-1),      2),
        ("RIGHTPADDING",  (0,0),     (-1,-1),      2),
        ("TOPPADDING",    (0,0),     (-1,-1),      2),
        ("BOTTOMPADDING", (0,0),     (-1,-1),      2),
        ("SPAN",          (1,n-1),   (4,n-1)),
    ]))
    story += [it_t, Spacer(1,2*mm)]

    # ── Tax summary table (GRS Solar style: one row per GST rate) ────────────
    tax_hdr = [
        Paragraph("Tax Rate",    hdr_s),
        Paragraph("Taxable Amt.",hdr_s),
        Paragraph("CGST Amt.",   hdr_s),
        Paragraph("SGST Amt.",   hdr_s),
        Paragraph("Total Tax",   hdr_s),
    ]
    tax_rows_data = [tax_hdr]
    for rate in sorted(gst_groups.keys()):
        g = gst_groups[rate]
        tax_rows_data.append([
            Paragraph(f"{rate:.1f}%",            wrap_c),
            Paragraph(f"{g['taxable']:,.2f}",    wrap_r),
            Paragraph(f"{g['cgst']:,.2f}",       wrap_r),
            Paragraph(f"{g['sgst']:,.2f}",       wrap_r),
            Paragraph(f"{g['cgst']+g['sgst']:,.2f}", wrap_r),
        ])
    # Total row
    tax_rows_data.append([
        Paragraph("<b>Total</b>",           hdr_s),
        Paragraph(f"<b>{subtotal:,.2f}</b>",wrap_r),
        Paragraph(f"<b>{total_cgst:,.2f}</b>",wrap_r),
        Paragraph(f"<b>{total_sgst:,.2f}</b>",wrap_r),
        Paragraph(f"<b>{total_tax:,.2f}</b>",wrap_r),
    ])
    nt = len(tax_rows_data)
    tt = Table(tax_rows_data, colWidths=[W*.12, W*.22, W*.22, W*.22, W*.22])
    tt.setStyle(TableStyle([
        ("BOX",       (0,0),   (-1,-1),  .5, colors.black),
        ("INNERGRID", (0,0),   (-1,-1),  .3, colors.black),
        ("BACKGROUND",(0,0),   (-1,0),   colors.Color(.92,.92,.92)),
        ("BACKGROUND",(0,nt-1),(-1,nt-1),colors.Color(.88,.92,.98)),
        ("FONTNAME",  (0,0),   (-1,0),   "Helvetica-Bold"),
        ("FONTSIZE",  (0,0),   (-1,-1),  7.5),
        ("VALIGN",    (0,0),   (-1,-1),  "MIDDLE"),
        ("LEFTPADDING",  (0,0),(-1,-1),  2),
        ("RIGHTPADDING", (0,0),(-1,-1),  2),
        ("TOPPADDING",   (0,0),(-1,-1),  2),
        ("BOTTOMPADDING",(0,0),(-1,-1),  2),
    ]))
    story += [tt, Spacer(1,2*mm)]

    # ── Amount in words ──────────────────────────────────────────────────────
    story.append(Paragraph(f"<i>{num_to_words(grand_rounded)}</i>", lft_s))
    story.append(Spacer(1,3*mm))

    # ── Bank + Terms + Signature footer ──────────────────────────────────────
    BANK_W = W * 0.50

    bank_title = Paragraph("<b>Bank Details:</b>", sml_b)
    bdet       = BANK_DETAILS
    bank_info  = Paragraph(
        f"Bank : <b>Indian Overseas Bank</b><br/>"
        f"A/c No. : <b>346702000000466</b><br/>"
        f"IFSC : <b>IOBA0003467</b><br/>"
        f"Branch : <b>PARMANANDPUR, VARANASI</b>", sml_s)

    if qr_bytes:
        try:
            qr_img    = img_to_rl(qr_bytes, 22, 22)
            bank_cell = Table([[qr_img,[bank_title,Spacer(1,2),bank_info]]],
                              colWidths=[24*mm, BANK_W-28*mm])
            bank_cell.setStyle(TableStyle([
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2),
                ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]))
        except Exception: bank_cell=[bank_title,Spacer(1,2),bank_info]
    else: bank_cell=[bank_title,Spacer(1,2),bank_info]

    terms_title = Paragraph("<b>Terms &amp; Conditions:</b>", sml_b)
    thanks_p    = Paragraph("Thanks for doing business with us!", sml_s)
    terms_items = [Paragraph(f"{j}. {t}", sml_s) for j,t in enumerate(TERMS,1)]
    for_p       = Paragraph(f"<b>For M/S-{COMPANY_NAME}:</b>", sml_s)
    if sig_bytes:
        try:    sig_img = img_to_rl(sig_bytes, 30, 14)
        except: sig_img = Spacer(1,14*mm)
    else: sig_img = Spacer(1,14*mm)
    auth_p = Paragraph("Authorized Signatory", sml_s)

    right_content  = [terms_title,Spacer(1,3),thanks_p,Spacer(1,3)]+terms_items
    right_content += [Spacer(1,4),for_p,Spacer(1,3),sig_img,auth_p]

    footer_t = Table([[bank_cell,right_content]], colWidths=[BANK_W,BANK_W])
    footer_t.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),.5,colors.black),
        ("LINEBEFORE",(1,0),(1,0),.5,colors.black),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story.append(footer_t)

    doc.build(story)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
#  STREAMLIT APP
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Sales Order Generator", page_icon="🧾",
                   layout="wide", initial_sidebar_state="collapsed")

if not st.session_state.get("authenticated", False):
    show_login_page(); st.stop()

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
.section-card{background:white;border-radius:12px;padding:20px 24px;
    margin-bottom:16px;border:1px solid #e2e4f0;}
.section-title{font-size:13px;font-weight:600;color:#7a7a9d;letter-spacing:.8px;
    text-transform:uppercase;margin-bottom:14px;padding-bottom:10px;
    border-bottom:1px solid #f0f2fa;}
.metric-row{display:flex;gap:12px;margin-bottom:16px;}
.metric-card{flex:1;background:#f4f5fa;border-radius:10px;padding:14px 16px;border:1px solid #e2e4f0;}
.metric-label{font-size:11px;color:#7a7a9d;font-weight:500;letter-spacing:.5px;text-transform:uppercase;}
.metric-value{font-size:20px;font-weight:600;color:#1a1a2e;margin-top:4px;}
.metric-card.accent{background:#eff6ff;border-color:#bfdbfe;}
.metric-card.accent .metric-value{color:#1d4ed8;}
/* GST breakdown cards */
.gst-breakdown{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;
    padding:12px 16px;margin-bottom:10px;font-size:12px;}
.gst-row{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dashed #d1fae5;}
.gst-row:last-child{border-bottom:none;font-weight:700;}
.gst-label{color:#166534;} .gst-val{color:#15803d;font-weight:600;}
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

user_display = st.session_state.get("user_name","User")
st.markdown(f"""
<div class="top-banner">
  <div class="banner-logo">S</div>
  <div>
    <div class="banner-title">SWASTIK ENTERPRISES</div>
    <div class="banner-sub">BELWARIYA, VARANASI &nbsp;·&nbsp; GSTIN: 09QRFPS4600L1Z2</div>
  </div>
  <div class="banner-right"><span class="banner-user">👤 {user_display}</span></div>
</div>""", unsafe_allow_html=True)

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
**Bank Details**  
{BANK_DETAILS}

---
**GST Rates Supported**  
0%, 5%, 12%, 18%, 28%  
*(per item — auto grouped in PDF)*
    """)
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()): st.session_state.pop(k,None)
        st.rerun()

# ── Session state ─────────────────────────────────────────────────────────────
def _init(k,v):
    if k not in st.session_state: st.session_state[k]=v

_init("order_no", gen_order_no())
_init("order_items", [{"desc":d,"hsn":h,"qty":q,"unit":u,"price":p,"brand":br,"gst":g}
                       for d,h,q,u,p,br,g in SAMPLE_ITEMS])

for asset_key, path in [("qr_bytes",QR_PATH),("sig_bytes",SIG_PATH)]:
    if asset_key not in st.session_state:
        try:
            with open(path,"rb") as f: st.session_state[asset_key]=f.read()
        except: st.session_state[asset_key]=None

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([1.5, 1], gap="large")

# ════════════════════════════════════
# LEFT panel
# ════════════════════════════════════
with left:

    # Party
    st.markdown('<div class="section-card"><div class="section-title">🏢 Party Details</div>', unsafe_allow_html=True)
    party_name = st.text_input("Party Name *", placeholder="e.g. SHASHI ENTERPRISES")
    party_city = st.text_input("City *",        placeholder="e.g. VARANASI")
    st.markdown('</div>', unsafe_allow_html=True)

    # Order
    st.markdown('<div class="section-card"><div class="section-title">📋 Order Details</div>', unsafe_allow_html=True)
    col_no, col_btn = st.columns([3,1])
    with col_no: order_no = st.text_input("Order Number *", value=st.session_state.order_no)
    with col_btn:
        st.write(""); st.write("")
        if st.button("↻ New", use_container_width=True):
            st.session_state.order_no=gen_order_no(); st.rerun()
    order_date     = st.date_input("Order Date *", value=datetime.date.today())
    order_date_str = order_date.strftime("%d-%m-%Y")
    st.markdown('</div>', unsafe_allow_html=True)

    # Items
    st.markdown('<div class="section-card"><div class="section-title">📦 Line Items</div>', unsafe_allow_html=True)

    st.markdown("""
<style>
.ih{display:grid;
    grid-template-columns:2.6fr 0.9fr 0.85fr 0.55fr 0.95fr 0.7fr 0.65fr 0.6fr 0.35fr;
    background:#1a1a2e;border-radius:8px;padding:8px 4px;margin-bottom:4px;}
.ih span{padding:3px 5px;font-size:10.5px;font-weight:600;
    color:rgba(255,255,255,.8);letter-spacing:.3px;text-transform:uppercase;}
</style>
<div class="ih">
  <span>Description</span><span>Brand</span><span>HSN/SAC</span>
  <span>Qty</span><span>Unit</span><span>GST%</span>
  <span>Price&nbsp;(&#8377;)</span><span>Amount</span><span></span>
</div>""", unsafe_allow_html=True)

    row_list  = st.session_state.order_items
    to_delete = []

    for i, item in enumerate(row_list):
        c1,c2,c3,c4,c5,c6,c7,c8,c9 = st.columns([2.6,0.9,0.85,0.55,0.95,0.7,0.65,0.6,0.35])
        with c1: item["desc"]  = st.text_area("Desc",  value=item["desc"],
                                    key=f"d{i}", label_visibility="collapsed",
                                    placeholder="Description", height=68)
        with c2: item["brand"] = st.text_input("Brand", value=item.get("brand",""),
                                    key=f"br{i}", label_visibility="collapsed",
                                    placeholder="Brand")
        with c3: item["hsn"]   = st.text_input("HSN",   value=item["hsn"],
                                    key=f"h{i}", label_visibility="collapsed",
                                    placeholder="HSN")
        with c4: item["qty"]   = st.number_input("Qty", value=float(item["qty"]),
                                    min_value=0.0, step=1.0,
                                    key=f"q{i}", label_visibility="collapsed", format="%.2f")
        with c5: item["unit"]  = st.selectbox("Unit", COMMON_UNITS,
                                    index=COMMON_UNITS.index(item["unit"])
                                          if item["unit"] in COMMON_UNITS else 0,
                                    key=f"u{i}", label_visibility="collapsed")
        with c6: item["gst"]   = st.selectbox("GST%",
                                    [f"{g:.0f}%" for g in GST_OPTIONS],
                                    index=GST_OPTIONS.index(float(item.get("gst",18.0)))
                                          if float(item.get("gst",18.0)) in GST_OPTIONS else 3,
                                    key=f"g{i}", label_visibility="collapsed")
        # parse back from string
        item["gst"] = float(item["gst"].replace("%",""))
        with c7: item["price"] = st.number_input("Price", value=float(item["price"]),
                                    min_value=0.0, step=10.0,
                                    key=f"p{i}", label_visibility="collapsed", format="%.2f")
        with c8:
            amt = item["qty"]*item["price"]
            st.markdown(f"<div style='padding:8px 2px;font-weight:600;font-size:11px;"
                        f"color:#1a1a2e;text-align:right'>&#8377;{amt:,.2f}</div>",
                        unsafe_allow_html=True)
        with c9:
            if st.button("✕", key=f"del{i}", help="Remove"): to_delete.append(i)

    for idx in reversed(to_delete):
        st.session_state.order_items.pop(idx); st.rerun()

    ca, cl = st.columns(2)
    with ca:
        if st.button("＋ Add Row", use_container_width=True):
            st.session_state.order_items.append(
                {"desc":"","hsn":"","qty":1.0,"unit":"Pcs.","price":0.0,"brand":"","gst":18.0})
            st.rerun()
    with cl:
        if st.button("Load Sample Data", use_container_width=True):
            st.session_state.order_items = [
                {"desc":d,"hsn":h,"qty":q,"unit":u,"price":p,"brand":br,"gst":g}
                for d,h,q,u,p,br,g in SAMPLE_ITEMS]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Bank details
    st.markdown('<div class="section-card"><div class="section-title">🏦 Bank Details</div>', unsafe_allow_html=True)
    uq, us = st.columns(2)
    with uq:
        if st.session_state.qr_bytes:  st.image(st.session_state.qr_bytes,  caption=f"✅ QR ({QR_PATH})",  width=100)
        else: st.warning(f"Place `{QR_PATH}` next to script")
    with us:
        if st.session_state.sig_bytes: st.image(st.session_state.sig_bytes, caption=f"✅ Sig ({SIG_PATH})", width=120)
        else: st.warning(f"Place `{SIG_PATH}` next to script")
    st.markdown(f"""
    <div class="bank-card">
      <div class="bank-row"><span class="bank-label">Bank</span><span class="bank-val">Indian Overseas Bank</span></div>
      <div class="bank-row"><span class="bank-label">A/c No.</span><span class="bank-val">346702000000466</span></div>
      <div class="bank-row"><span class="bank-label">IFSC</span><span class="bank-val">IOBA0003467</span></div>
      <div class="bank-row"><span class="bank-label">Branch</span><span class="bank-val">Parmanandpur, Varanasi</span></div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════
# RIGHT panel
# ════════════════════════════════════
with right:
    valid_items = [it for it in st.session_state.order_items if it["desc"].strip()]

    # ── Live totals ───────────────────────────────────────────────────────────
    subtotal = sum(it["qty"]*it["price"] for it in valid_items)
    gst_grps = calc_gst_groups(valid_items)
    total_cgst = round(sum(g["cgst"] for g in gst_grps.values()), 2)
    total_sgst = round(sum(g["sgst"] for g in gst_grps.values()), 2)
    total_tax  = round(total_cgst+total_sgst, 2)
    grand_total= round(subtotal+total_tax, 2)
    grand_rounded = round(grand_total)

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card">
        <div class="metric-label">Subtotal</div>
        <div class="metric-value">&#8377;{subtotal:,.2f}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Total CGST</div>
        <div class="metric-value">&#8377;{total_cgst:,.2f}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Total SGST</div>
        <div class="metric-value">&#8377;{total_sgst:,.2f}</div>
      </div>
    </div>
    <div class="metric-row">
      <div class="metric-card accent" style="flex:1">
        <div class="metric-label">Grand Total (incl. GST)</div>
        <div class="metric-value" style="font-size:26px">&#8377;{grand_rounded:,.2f}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"*{num_to_words(grand_rounded)}*")
    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── GST breakdown (GRS Solar style) ──────────────────────────────────────
    if gst_grps:
        st.markdown('<div class="section-card"><div class="section-title">🧮 GST Breakdown (Auto)</div>', unsafe_allow_html=True)
        breakdown_html = '<div class="gst-breakdown">'
        for rate in sorted(gst_grps.keys()):
            g    = gst_grps[rate]
            half = rate/2
            ttax = round(g["cgst"]+g["sgst"],2)
            breakdown_html += f"""
            <div class="gst-row">
              <span class="gst-label">CGST @ {half:.1f}% &nbsp;(on &#8377;{g['taxable']:,.2f})</span>
              <span class="gst-val">&#8377;{g['cgst']:,.2f}</span>
            </div>
            <div class="gst-row">
              <span class="gst-label">SGST @ {half:.1f}% &nbsp;(on &#8377;{g['taxable']:,.2f})</span>
              <span class="gst-val">&#8377;{g['sgst']:,.2f}</span>
            </div>"""
        breakdown_html += f"""
            <div class="gst-row">
              <span class="gst-label">&#8209;&#8209;&#8209; Total Tax</span>
              <span class="gst-val">&#8377;{total_tax:,.2f}</span>
            </div>
        </div>"""
        st.markdown(breakdown_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Order preview ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-card"><div class="section-title">📄 Order Preview</div>', unsafe_allow_html=True)
    if order_no and party_name and party_city:
        st.markdown(f"""
        <table style="width:100%;font-size:13px;border-collapse:collapse">
          <tr><td style="color:#7a7a9d;padding:5px 0;width:45%">Order No.</td>
              <td style="font-weight:600;color:#1a1a2e">{order_no}</td></tr>
          <tr><td style="color:#7a7a9d;padding:5px 0">Date</td>
              <td style="font-weight:600;color:#1a1a2e">{order_date_str}</td></tr>
          <tr><td style="color:#7a7a9d;padding:5px 0">Party</td>
              <td style="font-weight:600;color:#1a1a2e">{party_name}, {party_city}</td></tr>
          <tr><td style="color:#7a7a9d;padding:5px 0">Items</td>
              <td style="font-weight:600;color:#1a1a2e">{len(valid_items)} item(s)</td></tr>
          <tr><td style="color:#7a7a9d;padding:5px 0">GST Groups</td>
              <td style="font-weight:600;color:#059669">{", ".join(f"{r:.0f}%" for r in sorted(gst_grps.keys()))}</td></tr>
        </table>""", unsafe_allow_html=True)
    else:
        st.info("Fill in party name, city, and order number to see preview.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Items expander ────────────────────────────────────────────────────────
    if valid_items:
        with st.expander(f"📦 {len(valid_items)} Item(s) — click to expand"):
            for i,it in enumerate(valid_items,1):
                amt   = it["qty"]*it["price"]
                brand = f" | **{it.get('brand','')}**" if it.get("brand") else ""
                st.markdown(f"**{i}. {it['desc']}**{brand} | GST:{it.get('gst',18):.0f}%  \n"
                            f"HSN:`{it['hsn']}` | {it['qty']} {it['unit']} × ₹{it['price']:,.2f} = **₹{amt:,.2f}**")
                if i<len(valid_items): st.markdown("<hr style='margin:6px 0;border-color:#f0f2fa'>",unsafe_allow_html=True)

    # ── Download ──────────────────────────────────────────────────────────────
    st.markdown("<hr/>", unsafe_allow_html=True)
    errs=[]
    if not party_name.strip(): errs.append("Party Name is required.")
    if not party_city.strip():  errs.append("City is required.")
    if not order_no.strip():    errs.append("Order Number is required.")
    if not valid_items:         errs.append("Add at least one item with a description.")
    if errs:
        for e in errs: st.warning(e)
    else:
        pdf = build_pdf(
            party_name.strip(), party_city.strip(),
            order_no.strip(), order_date_str, valid_items,
            qr_bytes=st.session_state.qr_bytes,
            sig_bytes=st.session_state.sig_bytes)
        st.success(f"✅ Ready — Grand Total ₹{grand_rounded:,.2f}")
        st.download_button("⬇  Download Sales Order PDF", data=pdf,
            file_name=f"SalesOrder_{order_no}.pdf",
            mime="application/pdf", use_container_width=True)
        st.caption(f"Saves as `SalesOrder_{order_no}.pdf`")
