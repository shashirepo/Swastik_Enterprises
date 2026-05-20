"""
Trus India Enterprises — Sales Management App
  Tab 1: Sales Order / Estimation Generator
  Tab 2: Tax Invoice (Bill) Generator
Run:  streamlit run sales_order_streamlit.py
Req:  pip install streamlit reportlab Pillow
"""

import io, os, hashlib, random, string, datetime, base64
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
COMPANY_NAME  = "Trus India Enterprises"
COMPANY_ADDR1 = "O-529, GAUR CITY CENTRE, GREATER NOIDA (W)-201306, RGD. 454G NYAY KHAND-1, INDIRAPURAM GHAZIABAD (UP), BRANCH OFFICE: S 8/220-2, KHAJURI, PANDEYPUR, VARANASI-221002"
COMPANY_GSTIN = "GSTIN : 09AMAPV9671N1Z1"
COMPANY_TEL   = "Tel. : +91 9711193903"
COMPANY_EMAIL = "Email : trusindia@gmail.com"

BANK_NAME       = "Indian Overseas Bank"
BANK_BRANCH     = "Parmanandpur, Varanasi"
BANK_ACCOUNT_NO = "346702000000466"
BANK_IFSC       = "IOBA0003467"
BANK_HOLDER     = "Trus India Enterprises"

CGST_RATE = 9.0
SGST_RATE = 9.0
LOGO_PATH = "logo2.jpeg"
QR_PATH   = "qr_code.jpeg"
SIG_PATH  = "sign.jpg"

COMMON_UNITS = ["Pcs.", "MTR", "KG", "Set", "Pair", "Box", "Roll", "Ltr", "Nos."]

TERMS_ORDER = [
    "Goods once sold will not be taken back.",
    "Interest @ 18% p.a. will be charged if the payment is not made within the stipulated time.",
]
TERMS_BILL = [
    "All disputes subject to Varanasi jurisdiction only.",
    "Payment due within 30 days of invoice date.",
    "Goods once sold will not be taken back.",
]
PAYMENT_MODES = ["Cash", "UPI", "Bank Transfer", "Cheque", "NEFT/RTGS", "Other"]

SAMPLE_ITEMS = [
    ("SOLAR STRUCTURE C CHANNEL 80*40 - PCS", "73089030", 1.0, "Pcs.", 1452.50),
    ("SOLAR APOLLO PLAIN STRUT*41*41 - PCS",  "73089030", 1.0, "Pcs.", 1120.50),
    ("SOLAR STRUCTURE C BASE PLATE",          "73089030", 1.0, "Pcs.",   80.00),
    ("SOLAR STRUCTURE MID CLAMP",             "73089030", 1.0, "Pcs.",   25.00),
    ("SOLAR STRUCTURE END CLAMP",             "73089030", 1.0, "Pcs.",   25.00),
]

# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════
def _hash(p): return hashlib.sha256(p.encode()).hexdigest()

def _load_users():
    defaults = {
        "admin":    {"name":"Administrator",  "password_hash":"cfad5ccaf32fb8765202858e5a6d7f6b2e88b9ca8f4d0cd433590163fd384f7e"},
        "ravindra": {"name":"Ravindra Singh", "password_hash":"6396c7fb51044fedab8e8d0278c072269fa2a8c0f8f4704ef26d1c8a5e359ff3"},
        "veer":     {"name":"Veer Singh",     "password_hash":"6396c7fb51044fedab8e8d0278c072269fa2a8c0f8f4704ef26d1c8a5e359ff3"},
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
    users = _load_users()
    usr = users.get(u)
    return (True, usr["name"]) if usr and usr["password_hash"] == _hash(p) else (False, "")

def show_login_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
    html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
    .stApp{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%)!important;}
    #MainMenu,footer,header{visibility:hidden;}
    </style>""", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,1.5,1])
    with mid:
        st.markdown("""
        <div style="background:white;border-radius:20px;padding:44px 40px 36px;
                    box-shadow:0 20px 60px rgba(0,0,0,.35);text-align:center;margin-top:60px">
          <div style="width:64px;height:64px;background:linear-gradient(135deg,#2563eb,#1d4ed8);
                      border-radius:16px;display:flex;align-items:center;justify-content:center;
                      font-size:28px;color:white;font-weight:700;margin:0 auto 16px">S</div>
          <div style="font-size:22px;font-weight:700;color:#1a1a2e;margin-bottom:4px">Trus India Enterprises</div>
          <div style="font-size:13px;color:#7a7a9d;margin-bottom:28px">Sales Management &nbsp;·&nbsp; Sign in to continue</div>
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
                    "🔒 Secured · Trus India Enterprises © 2024</p>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def gen_order_no():  return "SWSENT" + "".join(random.choices(string.digits, k=3))
def gen_invoice_no(): return "SWSINV" + "".join(random.choices(string.digits, k=3))

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

def img_to_rl(img_bytes, width_mm, height_mm):
    from PIL import Image as PILImage
    img=PILImage.open(io.BytesIO(img_bytes)).convert("RGBA")
    bg=PILImage.new("RGB",img.size,(255,255,255)); bg.paste(img,mask=img.split()[3])
    out=io.BytesIO(); bg.save(out,format="PNG"); out.seek(0)
    return RLImage(out, width=width_mm*mm, height=height_mm*mm)

def _make_ps(base):
    def ps(name,**kw): return ParagraphStyle(name,parent=base["Normal"],**kw)
    return ps

def _common_footer(story, W, ps, qr_bytes, sig_bytes,
                   bank_name, bank_branch, bank_acno, bank_ifsc, bank_holder,
                   terms, for_label):
    """Shared bank + terms + signature footer used by both PDFs."""
    sml_s = ps("FS",  fontSize=7, alignment=TA_LEFT,  leading=10)
    sml_b = ps("FSB", fontSize=7, fontName="Helvetica-Bold", alignment=TA_LEFT, leading=10)

    bank_title = Paragraph("<b>Bank Details:</b>", sml_b)
    bank_info  = Paragraph(
        f"Name &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <b>{bank_name}</b>, {bank_branch}<br/>"
        f"Account No. : <b>{bank_acno}</b><br/>"
        f"IFSC code &nbsp;: <b>{bank_ifsc}</b><br/>"
        f"Account holder : <b>{bank_holder}</b>", sml_s)

    BANK_W = W*0.50
    if qr_bytes:
        try:
            qr_img = img_to_rl(qr_bytes, 22, 22)
            bank_cell = Table([[qr_img,[bank_title,Spacer(1,2),bank_info]]],
                              colWidths=[24*mm, BANK_W-28*mm])
            bank_cell.setStyle(TableStyle([
                ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),2),
                ("RIGHTPADDING",(0,0),(-1,-1),2),("TOPPADDING",(0,0),(-1,-1),2),
                ("BOTTOMPADDING",(0,0),(-1,-1),2)]))
        except Exception: bank_cell=[bank_title,Spacer(1,2),bank_info]
    else: bank_cell=[bank_title,Spacer(1,2),bank_info]

    terms_title = Paragraph("<b>Terms &amp; Conditions:</b>", sml_b)
    thanks_p    = Paragraph("Thanks for doing business with us!", sml_s)
    terms_items = [Paragraph(f"{j}. {t}", sml_s) for j,t in enumerate(terms,1)]
    for_p       = Paragraph(f"<b>{for_label}</b>", sml_s)
    if sig_bytes:
        try: sig_img = img_to_rl(sig_bytes, 30, 14)
        except Exception: sig_img = Spacer(1,14*mm)
    else: sig_img = Spacer(1,14*mm)
    auth_p = Paragraph("Authorized Signatory", sml_s)

    right_content = [terms_title,Spacer(1,3),thanks_p,Spacer(1,3)]+terms_items
    right_content += [Spacer(1,4),for_p,Spacer(1,3),sig_img,auth_p]

    footer_t = Table([[bank_cell,right_content]], colWidths=[BANK_W,BANK_W])
    footer_t.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),.5,colors.black),
        ("LINEBEFORE",(1,0),(1,0),.5,colors.black),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    story.append(footer_t)

# ══════════════════════════════════════════════════════════════════════════════
#  PDF 1 — SALES ORDER / ESTIMATION
# ══════════════════════════════════════════════════════════════════════════════
def build_order_pdf(party_name, party_city, order_no, order_date, items,
                    qr_bytes=None, sig_bytes=None,
                    bank_name=BANK_NAME, bank_branch=BANK_BRANCH,
                    bank_acno=BANK_ACCOUNT_NO, bank_ifsc=BANK_IFSC,
                    bank_holder=BANK_HOLDER) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=12*mm, bottomMargin=12*mm)
    W   = A4[0]-30*mm
    ps  = _make_ps(getSampleStyleSheet())

    title_s = ps("OT", fontSize=14, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6)
    ctr_s   = ps("OC", fontSize=8,  alignment=TA_CENTER, leading=11)
    lft_s   = ps("OL", fontSize=8,  alignment=TA_LEFT,   leading=11)
    bold_c  = ps("OBC",fontSize=8,  fontName="Helvetica-Bold", alignment=TA_CENTER)
    hdr_s   = ps("OH", fontSize=7.5,fontName="Helvetica-Bold", alignment=TA_CENTER, leading=10)
    hdr_ls  = ps("OHL",fontSize=7.5,fontName="Helvetica-Bold", alignment=TA_LEFT,   leading=10)
    wrap_s  = ps("OW", fontSize=7.5,alignment=TA_LEFT,   leading=10, wordWrap="LTR")
    wrap_c  = ps("OWC",fontSize=7.5,alignment=TA_CENTER, leading=10, wordWrap="LTR")
    wrap_r  = ps("OWR",fontSize=7.5,alignment=TA_RIGHT,  leading=10, wordWrap="LTR")

    story = []

    # Header
    try: logo = RLImage(LOGO_PATH, width=33*mm, height=30*mm)
    except: logo = Paragraph("", lft_s)
    hdr_txt = [Paragraph("<u>ORDER ESTIMATION</u>",bold_c),
               Paragraph(COMPANY_NAME,title_s),
               Paragraph(COMPANY_ADDR1,ctr_s),
               Paragraph(COMPANY_GSTIN,ctr_s),
               Paragraph(f"{COMPANY_TEL}<br/>{COMPANY_EMAIL}",ctr_s)]
    ht = Table([[logo,hdr_txt]], colWidths=[W*.20,W*.80])
    ht.setStyle(TableStyle([("BOX",(0,0),(-1,-1),.9,colors.black),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    story += [ht, Spacer(1,5)]

    # Party/Order box
    pp = f"<b>Party Details :</b><br/>{party_name}<br/>{party_city}"
    op = f"<b>Order No. :</b> {order_no}<br/><b>Dated :</b> {order_date}"
    pt = Table([[Paragraph(pp,lft_s),Paragraph(op,lft_s)]], colWidths=[W*.55,W*.45])
    pt.setStyle(TableStyle([("BOX",(0,0),(-1,-1),.5,colors.black),
        ("LINEBEFORE",(1,0),(1,0),.5,colors.black),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    story += [pt, Spacer(1,2*mm),
              Paragraph("We are pleased to receive the order for the following items :", lft_s),
              Spacer(1,1*mm)]

    # Items table
    hdr_row = [Paragraph("S.N.",hdr_s),Paragraph("Description of Goods",hdr_ls),
               Paragraph("HSN/SAC<br/>Code",hdr_s),Paragraph("Qty.",hdr_s),
               Paragraph("Unit",hdr_s),Paragraph("Price",hdr_s),Paragraph("Amount(`)",hdr_s)]
    cw = [W*.05,W*.37,W*.10,W*.07,W*.07,W*.12,W*.12]
    rows = [hdr_row]; subtotal = total_qty = 0.0
    for i,it in enumerate(items,1):
        amt=round(it["qty"]*it["price"],2); subtotal+=amt; total_qty+=it["qty"]
        rows.append([Paragraph(str(i),wrap_c),Paragraph(it["desc"],wrap_s),
                     Paragraph(it["hsn"],wrap_c),Paragraph(f"{it['qty']:.2f}",wrap_c),
                     Paragraph(it["unit"],wrap_c),Paragraph(f"{it['price']:,.2f}",wrap_r),
                     Paragraph(f"{amt:,.2f}",wrap_r)])
    cgst=round(subtotal*CGST_RATE/100,2); sgst=round(subtotal*SGST_RATE/100,2)
    tax=round(cgst+sgst,2); grand=round(subtotal+tax,2)
    rows += [["","","","","","",f"{subtotal:,.2f}"],
             ["","","","","Add : CGST",f"@ {CGST_RATE:.2f} %",f"{cgst:,.2f}"],
             ["","","","","Add : SGST",f"@ {SGST_RATE:.2f} %",f"{sgst:,.2f}"],
             ["","Grand Total","",f"{int(total_qty)} Units","","`",f"{grand:,.2f}"]]
    n=len(rows)
    it_t=Table(rows,colWidths=cw,repeatRows=1)
    it_t.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),.5,colors.black),
        ("INNERGRID",(0,0),(-1,n-5),.3,colors.black),
        ("LINEABOVE",(0,n-4),(-1,n-4),.5,colors.black),
        ("LINEABOVE",(0,n-1),(-1,n-1),.5,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.Color(.92,.92,.92)),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTNAME",(0,n-1),(-1,n-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),7.5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2),
        ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
        ("SPAN",(1,n-1),(3,n-1))]))
    story += [it_t,Spacer(1,2*mm)]

    # Tax summary
    tr=[["Tax Rate","Taxable Amt.","CGST Amt.","SGST Amt.","Total Tax"],
        ["18%",f"{subtotal:,.2f}",f"{cgst:,.2f}",f"{sgst:,.2f}",f"{tax:,.2f}"]]
    tt=Table(tr,colWidths=[W*.12,W*.22,W*.22,W*.22,W*.22])
    tt.setStyle(TableStyle([("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),7.5),("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LINEBELOW",(0,0),(-1,0),.5,colors.black)]))
    story += [tt,Spacer(1,2*mm),
              Paragraph(f"<i>{num_to_words(grand)}</i>",
                        ps("OAW",fontSize=8,alignment=TA_LEFT,leading=11)),
              Spacer(1,3*mm)]

    _common_footer(story,W,ps,qr_bytes,sig_bytes,bank_name,bank_branch,
                   bank_acno,bank_ifsc,bank_holder,TERMS_ORDER,
                   f"For M/S-{COMPANY_NAME}:")
    doc.build(story)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
#  PDF 2 — TAX INVOICE / BILL
# ══════════════════════════════════════════════════════════════════════════════
def build_invoice_pdf(party_name, party_city, party_gstin, party_phone,
                      invoice_no, invoice_date, due_date, payment_mode,
                      items, qr_bytes=None, sig_bytes=None,
                      bank_name=BANK_NAME, bank_branch=BANK_BRANCH,
                      bank_acno=BANK_ACCOUNT_NO, bank_ifsc=BANK_IFSC,
                      bank_holder=BANK_HOLDER) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=12*mm, bottomMargin=12*mm)
    W   = A4[0]-30*mm
    ps  = _make_ps(getSampleStyleSheet())

    title_s  = ps("IT", fontSize=14, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    ctr_s    = ps("IC", fontSize=8,  alignment=TA_CENTER, leading=11)
    lft_s    = ps("IL", fontSize=8,  alignment=TA_LEFT,   leading=11)
    rgt_s    = ps("IR", fontSize=8,  alignment=TA_RIGHT,  leading=11)
    bold_c   = ps("IBC",fontSize=8,  fontName="Helvetica-Bold", alignment=TA_CENTER)
    bold_l   = ps("IBL",fontSize=8,  fontName="Helvetica-Bold", alignment=TA_LEFT)
    hdr_s    = ps("IH", fontSize=7.5,fontName="Helvetica-Bold", alignment=TA_CENTER, leading=10)
    hdr_ls   = ps("IHL",fontSize=7.5,fontName="Helvetica-Bold", alignment=TA_LEFT,   leading=10)
    wrap_s   = ps("IW", fontSize=7.5,alignment=TA_LEFT,   leading=10, wordWrap="LTR")
    wrap_c   = ps("IWC",fontSize=7.5,alignment=TA_CENTER, leading=10, wordWrap="LTR")
    wrap_r   = ps("IWR",fontSize=7.5,alignment=TA_RIGHT,  leading=10, wordWrap="LTR")
    inv_title= ps("INV",fontSize=16, fontName="Helvetica-Bold", alignment=TA_CENTER,
                  textColor=colors.HexColor("#1d4ed8"), spaceAfter=2)

    story = []

    # Header — logo left, company centre, TAX INVOICE label right
    try: logo = RLImage(LOGO_PATH, width=33*mm, height=30*mm)
    except: logo = Paragraph("", lft_s)

    company_cell = [Paragraph(COMPANY_NAME,title_s),
                    Paragraph(COMPANY_ADDR1,ctr_s),
                    Paragraph(COMPANY_GSTIN,ctr_s),
                    Paragraph(f"{COMPANY_TEL}<br/>{COMPANY_EMAIL}",ctr_s)]
    invoice_label= [Paragraph("TAX INVOICE",inv_title),
                    Paragraph(f"<b>Invoice No:</b> {invoice_no}",rgt_s),
                    Paragraph(f"<b>Date:</b> {invoice_date}",rgt_s),
                    Paragraph(f"<b>Due Date:</b> {due_date}",rgt_s)]

    ht = Table([[logo, company_cell, invoice_label]],
               colWidths=[W*.18, W*.50, W*.32])
    ht.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),.9,colors.black),
        ("LINEBEFORE",(1,0),(1,0),.5,colors.black),
        ("LINEBEFORE",(2,0),(2,0),.5,colors.black),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(2,0),(2,0),"RIGHT"),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story += [ht, Spacer(1,4)]

    # Bill To / Invoice Details box
    bill_to = (f"<b>Bill To:</b><br/>"
               f"<b>{party_name}</b><br/>"
               f"{party_city}<br/>"
               f"GSTIN: {party_gstin or 'N/A'}<br/>"
               f"Phone: {party_phone or 'N/A'}")
    inv_det = (f"<b>Payment Mode:</b> {payment_mode}<br/>"
               f"<b>Bank:</b> {bank_name}<br/>"
               f"<b>A/c No:</b> {bank_acno}<br/>"
               f"<b>IFSC:</b> {bank_ifsc}")
    bt = Table([[Paragraph(bill_to,lft_s), Paragraph(inv_det,lft_s)]],
               colWidths=[W*.55, W*.45])
    bt.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),.5,colors.black),
        ("LINEBEFORE",(1,0),(1,0),.5,colors.black),
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f0f4ff")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story += [bt, Spacer(1,2*mm)]

    # Items table
    hdr_row=[Paragraph("S.N.",hdr_s),Paragraph("Description of Goods/Services",hdr_ls),
             Paragraph("HSN/SAC",hdr_s),Paragraph("Qty.",hdr_s),
             Paragraph("Unit",hdr_s),Paragraph("Rate (₹)",hdr_s),
             Paragraph("CGST\n9%",hdr_s),Paragraph("SGST\n9%",hdr_s),
             Paragraph("Amount (₹)",hdr_s)]
    cw=[W*.04,W*.30,W*.08,W*.06,W*.06,W*.10,W*.08,W*.08,W*.10]
    rows=[hdr_row]; subtotal=total_qty=0.0
    for i,it in enumerate(items,1):
        base_amt=round(it["qty"]*it["price"],2)
        cgst_cell=round(base_amt*CGST_RATE/100,2)
        sgst_cell=round(base_amt*SGST_RATE/100,2)
        total_cell=round(base_amt+cgst_cell+sgst_cell,2)
        subtotal+=base_amt; total_qty+=it["qty"]
        rows.append([Paragraph(str(i),wrap_c),Paragraph(it["desc"],wrap_s),
                     Paragraph(it["hsn"],wrap_c),Paragraph(f"{it['qty']:.2f}",wrap_c),
                     Paragraph(it["unit"],wrap_c),Paragraph(f"{it['price']:,.2f}",wrap_r),
                     Paragraph(f"{cgst_cell:,.2f}",wrap_r),Paragraph(f"{sgst_cell:,.2f}",wrap_r),
                     Paragraph(f"{total_cell:,.2f}",wrap_r)])

    cgst_total=round(subtotal*CGST_RATE/100,2)
    sgst_total=round(subtotal*SGST_RATE/100,2)
    tax_total =round(cgst_total+sgst_total,2)
    grand     =round(subtotal+tax_total,2)

    rows.append(["","",Paragraph("<b>Totals</b>",hdr_s),"","","",
                 Paragraph(f"<b>{cgst_total:,.2f}</b>",wrap_r),
                 Paragraph(f"<b>{sgst_total:,.2f}</b>",wrap_r),
                 Paragraph(f"<b>{grand:,.2f}</b>",wrap_r)])
    n=len(rows)
    it_t=Table(rows,colWidths=cw,repeatRows=1)
    it_t.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),.5,colors.black),
        ("INNERGRID",(0,0),(-1,n-2),.3,colors.black),
        ("LINEABOVE",(0,n-1),(-1,n-1),.8,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BACKGROUND",(0,n-1),(-1,n-1),colors.HexColor("#eff6ff")),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTNAME",(0,n-1),(-1,n-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),7.5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2),
        ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]))
    story += [it_t, Spacer(1,2*mm)]

    # Summary box (right-aligned)
    sum_rows=[
        ["Subtotal (excl. GST)",        f"₹ {subtotal:,.2f}"],
        [f"CGST @ {CGST_RATE}%",        f"₹ {cgst_total:,.2f}"],
        [f"SGST @ {SGST_RATE}%",        f"₹ {sgst_total:,.2f}"],
        ["Total Tax",                   f"₹ {tax_total:,.2f}"],
        ["GRAND TOTAL",                 f"₹ {grand:,.2f}"],
    ]
    sum_t=Table(sum_rows, colWidths=[W*.25,W*.15],
                hAlign="RIGHT")
    sum_t.setStyle(TableStyle([
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("ALIGN",(0,0),(0,-1),"RIGHT"),("ALIGN",(1,0),(1,-1),"RIGHT"),
        ("FONTNAME",(0,4),(1,4),"Helvetica-Bold"),
        ("BACKGROUND",(0,4),(1,4),colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR",(0,4),(1,4),colors.white),
        ("LINEABOVE",(0,4),(1,4),.8,colors.black),
        ("LINEBELOW",(0,4),(1,4),.8,colors.black),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("ROWBACKGROUNDS",(0,0),(-1,3),[colors.white,colors.HexColor("#f0f4ff")])]))
    story += [sum_t, Spacer(1,2*mm),
              Paragraph(f"<i>{num_to_words(grand)}</i>",
                        ps("IAMW",fontSize=8,alignment=TA_LEFT,leading=11)),
              Spacer(1,3*mm)]

    _common_footer(story,W,ps,qr_bytes,sig_bytes,bank_name,bank_branch,
                   bank_acno,bank_ifsc,bank_holder,TERMS_BILL,
                   f"For {COMPANY_NAME}:")
    doc.build(story)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def render_items_ui(key_prefix, items_key):
    """Render the line-items editor. Returns list of valid items."""
    st.markdown("""
<style>
.items-header{display:grid;
    grid-template-columns:3.5fr 1.1fr 0.6fr 1.2fr 0.85fr 0.75fr 0.35fr;
    font-weight:bold;border-bottom:1px solid #ccc;padding:6px 0;}
.items-header span{padding:4px;}
</style>
<div class="items-header">
  <span>Description</span><span>HSN/SAC</span><span>Qty</span>
  <span>Unit</span><span>Price (₹)</span><span>Amount</span><span></span>
</div>""", unsafe_allow_html=True)

    row_list  = st.session_state[items_key]
    to_delete = []
    for i, item in enumerate(row_list):
        c1,c2,c3,c4,c5,c6,c7 = st.columns([3.5,1.1,.6,1.2,.85,.75,.35])
        with c1: item["desc"]  = st.text_area("Desc", value=item["desc"],
                                    key=f"{key_prefix}_d{i}",
                                    label_visibility="collapsed",
                                    placeholder="Description", height=68)
        with c2: item["hsn"]   = st.text_input("HSN", value=item["hsn"],
                                    key=f"{key_prefix}_h{i}",
                                    label_visibility="collapsed", placeholder="HSN")
        with c3: item["qty"]   = st.number_input("Qty", value=float(item["qty"]),
                                    min_value=0.0, step=1.0,
                                    key=f"{key_prefix}_q{i}",
                                    label_visibility="collapsed", format="%.2f")
        with c4: item["unit"]  = st.selectbox("Unit", COMMON_UNITS,
                                    index=COMMON_UNITS.index(item["unit"])
                                          if item["unit"] in COMMON_UNITS else 0,
                                    key=f"{key_prefix}_u{i}",
                                    label_visibility="collapsed")
        with c5: item["price"] = st.number_input("Price", value=float(item["price"]),
                                    min_value=0.0, step=10.0,
                                    key=f"{key_prefix}_p{i}",
                                    label_visibility="collapsed", format="%.2f")
        with c6:
            amt = item["qty"]*item["price"]
            st.markdown(f"<div style='padding:8px 4px;font-weight:600;font-size:13px;"
                        f"color:#1a1a2e;text-align:right'>₹{amt:,.2f}</div>",
                        unsafe_allow_html=True)
        with c7:
            if st.button("✕", key=f"{key_prefix}_del{i}", help="Remove"):
                to_delete.append(i)

    for idx in reversed(to_delete):
        st.session_state[items_key].pop(idx); st.rerun()

    ca, cl = st.columns(2)
    with ca:
        if st.button("＋ Add Row", key=f"{key_prefix}_add", use_container_width=True):
            st.session_state[items_key].append(
                {"desc":"","hsn":"","qty":1.0,"unit":"Pcs.","price":0.0}); st.rerun()
    with cl:
        if st.button("Load Sample Data", key=f"{key_prefix}_sample", use_container_width=True):
            st.session_state[items_key] = [
                {"desc":d,"hsn":h,"qty":q,"unit":u,"price":p}
                for d,h,q,u,p in SAMPLE_ITEMS]; st.rerun()

    return [it for it in st.session_state[items_key] if it["desc"].strip()]


def render_metrics(valid_items):
    subtotal    = sum(it["qty"]*it["price"] for it in valid_items)
    cgst_amt    = round(subtotal*CGST_RATE/100,2)
    sgst_amt    = round(subtotal*SGST_RATE/100,2)
    grand_total = round(subtotal+cgst_amt+sgst_amt,2)
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
    </div>""", unsafe_allow_html=True)
    st.markdown(f"*{num_to_words(grand_total)}*")
    return subtotal, cgst_amt, sgst_amt, grand_total


# ══════════════════════════════════════════════════════════════════════════════
#  STREAMLIT APP
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Trus India Enterprises", page_icon="🧾",
                   layout="wide", initial_sidebar_state="collapsed")

if not st.session_state.get("authenticated", False):
    show_login_page(); st.stop()

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background:#f0f2fa;}
section.main>div{padding-top:0!important;}
.top-banner{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);color:white;
    padding:18px 28px;border-radius:14px;margin-bottom:4px;
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
/* Tab styling */
button[data-baseweb="tab"]{font-size:14px!important;font-weight:600!important;padding:12px 28px!important;}
div[data-baseweb="tab-list"]{background:#f0f2fa!important;border-radius:12px!important;
    padding:4px!important;margin-bottom:16px!important;}
button[data-baseweb="tab"][aria-selected="true"]{
    background:white!important;border-radius:10px!important;
    box-shadow:0 2px 8px rgba(0,0,0,.08)!important;color:#2563eb!important;}
</style>
""", unsafe_allow_html=True)

user_display = st.session_state.get("user_name","User")
st.markdown(f"""
<div class="top-banner">
  <div class="banner-logo">S</div>
  <div>
    <div class="banner-title">Trus India Enterprises</div>
    <div class="banner-sub">O-529, GAUR CITY CENTRE, GREATER NOIDA (W)-201306, RGD. 454G NYAY KHAND-1, INDIRAPURAM GHAZIABAD (UP) &nbsp;·&nbsp; GSTIN: 09AMAPV9671N1Z1</div>
  </div>
  <div class="banner-right">
    <span class="banner-user">👤 {user_display}</span>
  </div>
</div>""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {user_display}")
    st.markdown("---")
    st.markdown(f"""
**{COMPANY_NAME}**  
{COMPANY_ADDR1}

---
**{COMPANY_GSTIN}**

📞 +91 9711193903 
✉ trusindia@gmail.com

---
**Bank:** {BANK_NAME}  
**A/c:** {BANK_ACCOUNT_NO}  
**IFSC:** {BANK_IFSC}

---
**Tax:** CGST {CGST_RATE}% + SGST {SGST_RATE}%
    """)
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()): st.session_state.pop(k, None)
        st.rerun()

# Session state
def _init(key, val):
    if key not in st.session_state: st.session_state[key] = val

_init("order_no",    gen_order_no())
_init("invoice_no",  gen_invoice_no())
_init("order_items", [{"desc":d,"hsn":h,"qty":q,"unit":u,"price":p} for d,h,q,u,p in SAMPLE_ITEMS])
_init("bill_items",  [{"desc":d,"hsn":h,"qty":q,"unit":u,"price":p} for d,h,q,u,p in SAMPLE_ITEMS])
_init("bank_name",   BANK_NAME)
_init("bank_branch", BANK_BRANCH)
_init("bank_acno",   BANK_ACCOUNT_NO)
_init("bank_ifsc",   BANK_IFSC)
_init("bank_holder", BANK_HOLDER)

for asset_key, path in [("qr_bytes", QR_PATH), ("sig_bytes", SIG_PATH)]:
    if asset_key not in st.session_state:
        try:
            with open(path,"rb") as f: st.session_state[asset_key]=f.read()
        except: st.session_state[asset_key]=None

# ══════════════════════════════════
#  TWO TABS
# ══════════════════════════════════
tab1, tab2 = st.tabs(["📋  Sales Order / Estimation", "🧾  Tax Invoice / Bill"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — SALES ORDER
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    left, right = st.columns([1.4,1], gap="large")

    with left:
        # Party
        st.markdown('<div class="section-card"><div class="section-title">🏢 Party Details</div>', unsafe_allow_html=True)
        o_party_name = st.text_input("Party Name *", placeholder="e.g. SHASHI ENTERPRISES", key="o_pname")
        o_party_city = st.text_input("City *", placeholder="e.g. VARANASI", key="o_pcity")
        st.markdown('</div>', unsafe_allow_html=True)

        # Order details
        st.markdown('<div class="section-card"><div class="section-title">📋 Order Details</div>', unsafe_allow_html=True)
        col_no, col_btn = st.columns([3,1])
        with col_no:
            o_order_no = st.text_input("Order Number *", value=st.session_state.order_no, key="o_ono")
        with col_btn:
            st.write(""); st.write("")
            if st.button("↻ New", key="o_newno", use_container_width=True):
                st.session_state.order_no = gen_order_no(); st.rerun()
        o_order_date     = st.date_input("Order Date *", value=datetime.date.today(), key="o_date")
        o_order_date_str = o_order_date.strftime("%d-%m-%Y")
        st.markdown('</div>', unsafe_allow_html=True)

        # Items
        st.markdown('<div class="section-card"><div class="section-title">📦 Line Items</div>', unsafe_allow_html=True)
        o_valid_items = render_items_ui("o", "order_items")
        st.markdown('</div>', unsafe_allow_html=True)

        # Bank details
        st.markdown('<div class="section-card"><div class="section-title">🏦 Bank Details</div>', unsafe_allow_html=True)
        bc1, bc2 = st.columns(2)
        with bc1:
            st.session_state.bank_name   = st.text_input("Bank Name",      value=st.session_state.bank_name,   key="o_bname")
            st.session_state.bank_acno   = st.text_input("Account Number", value=st.session_state.bank_acno,   key="o_bacno")
            st.session_state.bank_holder = st.text_input("Account Holder", value=st.session_state.bank_holder, key="o_bholder")
        with bc2:
            st.session_state.bank_branch = st.text_input("Branch",    value=st.session_state.bank_branch, key="o_bbranch")
            st.session_state.bank_ifsc   = st.text_input("IFSC Code", value=st.session_state.bank_ifsc,   key="o_bifsc")
        uq, us = st.columns(2)
        with uq:
            if st.session_state.qr_bytes:  st.image(st.session_state.qr_bytes,  caption=f"✅ QR ({QR_PATH})",  width=100)
            else: st.warning(f"Place `{QR_PATH}` next to script")
        with us:
            if st.session_state.sig_bytes: st.image(st.session_state.sig_bytes, caption=f"✅ Sig ({SIG_PATH})", width=120)
            else: st.warning(f"Place `{SIG_PATH}` next to script")
        st.markdown(f"""
        <div class="bank-card">
          <div style="font-size:13px;font-weight:700;color:#1d4ed8;margin-bottom:8px">🏦 Bank Preview</div>
          <div class="bank-row"><span class="bank-label">Bank</span><span class="bank-val">{st.session_state.bank_name}</span></div>
          <div class="bank-row"><span class="bank-label">Branch</span><span class="bank-val">{st.session_state.bank_branch}</span></div>
          <div class="bank-row"><span class="bank-label">Account No.</span><span class="bank-val">{st.session_state.bank_acno}</span></div>
          <div class="bank-row"><span class="bank-label">IFSC</span><span class="bank-val">{st.session_state.bank_ifsc}</span></div>
          <div class="bank-row"><span class="bank-label">Holder</span><span class="bank-val">{st.session_state.bank_holder}</span></div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        subtotal, cgst_amt, sgst_amt, grand_total = render_metrics(o_valid_items)
        st.markdown("<hr/>", unsafe_allow_html=True)

        st.markdown('<div class="section-card"><div class="section-title">📄 Order Preview</div>', unsafe_allow_html=True)
        if o_order_no and o_party_name and o_party_city:
            st.markdown(f"""
            <table style="width:100%;font-size:13px;border-collapse:collapse">
              <tr><td style="color:#7a7a9d;padding:5px 0;width:45%">Order No.</td>
                  <td style="font-weight:600;color:#1a1a2e">{o_order_no}</td></tr>
              <tr><td style="color:#7a7a9d;padding:5px 0">Date</td>
                  <td style="font-weight:600;color:#1a1a2e">{o_order_date_str}</td></tr>
              <tr><td style="color:#7a7a9d;padding:5px 0">Party</td>
                  <td style="font-weight:600;color:#1a1a2e">{o_party_name}, {o_party_city}</td></tr>
              <tr><td style="color:#7a7a9d;padding:5px 0">Items</td>
                  <td style="font-weight:600;color:#1a1a2e">{len(o_valid_items)} item(s)</td></tr>
            </table>""", unsafe_allow_html=True)
        else:
            st.info("Fill in party name, city and order number.")
        st.markdown('</div>', unsafe_allow_html=True)

        if o_valid_items:
            with st.expander(f"📦 {len(o_valid_items)} Item(s)"):
                for i,it in enumerate(o_valid_items,1):
                    amt=it["qty"]*it["price"]
                    st.markdown(f"**{i}. {it['desc']}**  \n"
                                f"HSN:`{it['hsn']}` | {it['qty']} {it['unit']} × ₹{it['price']:,.2f} = **₹{amt:,.2f}**")
                    if i<len(o_valid_items): st.markdown("<hr style='margin:6px 0;border-color:#f0f2fa'>",unsafe_allow_html=True)

        st.markdown("<hr/>", unsafe_allow_html=True)
        errs=[]
        if not o_party_name.strip(): errs.append("Party Name is required.")
        if not o_party_city.strip():  errs.append("City is required.")
        if not o_order_no.strip():    errs.append("Order Number is required.")
        if not o_valid_items:         errs.append("Add at least one item.")
        if errs:
            for e in errs: st.warning(e)
        else:
            pdf=build_order_pdf(
                o_party_name.strip(), o_party_city.strip(),
                o_order_no.strip(), o_order_date_str, o_valid_items,
                qr_bytes=st.session_state.qr_bytes,
                sig_bytes=st.session_state.sig_bytes,
                bank_name=st.session_state.bank_name,
                bank_branch=st.session_state.bank_branch,
                bank_acno=st.session_state.bank_acno,
                bank_ifsc=st.session_state.bank_ifsc,
                bank_holder=st.session_state.bank_holder)
            st.success(f"✅ Ready — Grand Total ₹{grand_total:,.2f}")
            st.download_button("⬇  Download Sales Order PDF", data=pdf,
                file_name=f"SalesOrder_{o_order_no}.pdf",
                mime="application/pdf", use_container_width=True)
            st.caption(f"Saves as `SalesOrder_{o_order_no}.pdf`")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — TAX INVOICE / BILL
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    left2, right2 = st.columns([1.4,1], gap="large")

    with left2:
        # Customer details
        st.markdown('<div class="section-card"><div class="section-title">👤 Customer Details</div>', unsafe_allow_html=True)
        b_party_name  = st.text_input("Customer Name *",  placeholder="e.g. RAMESH KUMAR",         key="b_pname")
        b_party_city  = st.text_input("City / Address *", placeholder="e.g. VARANASI, UP",          key="b_pcity")
        bc1, bc2 = st.columns(2)
        with bc1: b_party_gstin = st.text_input("Customer GSTIN", placeholder="Optional", key="b_gstin")
        with bc2: b_party_phone = st.text_input("Phone Number",   placeholder="+91 XXXXXXXXXX", key="b_phone")
        st.markdown('</div>', unsafe_allow_html=True)

        # Invoice details
        st.markdown('<div class="section-card"><div class="section-title">🧾 Invoice Details</div>', unsafe_allow_html=True)
        col_inv, col_btn2 = st.columns([3,1])
        with col_inv:
            b_invoice_no = st.text_input("Invoice Number *", value=st.session_state.invoice_no, key="b_invno")
        with col_btn2:
            st.write(""); st.write("")
            if st.button("↻ New", key="b_newno", use_container_width=True):
                st.session_state.invoice_no = gen_invoice_no(); st.rerun()
        ic1, ic2, ic3 = st.columns(3)
        with ic1: b_inv_date  = st.date_input("Invoice Date *",  value=datetime.date.today(),               key="b_idate")
        with ic2: b_due_date  = st.date_input("Due Date",        value=datetime.date.today()+datetime.timedelta(days=30), key="b_ddate")
        with ic3: b_pay_mode  = st.selectbox("Payment Mode",     PAYMENT_MODES, key="b_paymode")
        b_inv_date_str = b_inv_date.strftime("%d-%m-%Y")
        b_due_date_str = b_due_date.strftime("%d-%m-%Y")
        st.markdown('</div>', unsafe_allow_html=True)

        # Items
        st.markdown('<div class="section-card"><div class="section-title">📦 Line Items</div>', unsafe_allow_html=True)
        b_valid_items = render_items_ui("b", "bill_items")
        st.markdown('</div>', unsafe_allow_html=True)

        # Bank (shared, read-only display)
        st.markdown(f"""
        <div class="section-card">
          <div class="section-title">🏦 Bank Details</div>
          <div class="bank-card" style="margin-bottom:0">
            <div class="bank-row"><span class="bank-label">Bank</span><span class="bank-val">{st.session_state.bank_name}</span></div>
            <div class="bank-row"><span class="bank-label">Branch</span><span class="bank-val">{st.session_state.bank_branch}</span></div>
            <div class="bank-row"><span class="bank-label">Account No.</span><span class="bank-val">{st.session_state.bank_acno}</span></div>
            <div class="bank-row"><span class="bank-label">IFSC</span><span class="bank-val">{st.session_state.bank_ifsc}</span></div>
            <div class="bank-row"><span class="bank-label">Holder</span><span class="bank-val">{st.session_state.bank_holder}</span></div>
          </div>
          <p style="font-size:11px;color:#7a7a9d;margin-top:8px">
          ✏️ Edit bank details in the <b>Sales Order tab</b> — shared across both tabs.</p>
        </div>""", unsafe_allow_html=True)

    with right2:
        subtotal2, cgst2, sgst2, grand2 = render_metrics(b_valid_items)
        st.markdown("<hr/>", unsafe_allow_html=True)

        st.markdown('<div class="section-card"><div class="section-title">🧾 Invoice Preview</div>', unsafe_allow_html=True)
        if b_invoice_no and b_party_name and b_party_city:
            st.markdown(f"""
            <table style="width:100%;font-size:13px;border-collapse:collapse">
              <tr><td style="color:#7a7a9d;padding:5px 0;width:45%">Invoice No.</td>
                  <td style="font-weight:600;color:#1d4ed8">{b_invoice_no}</td></tr>
              <tr><td style="color:#7a7a9d;padding:5px 0">Invoice Date</td>
                  <td style="font-weight:600;color:#1a1a2e">{b_inv_date_str}</td></tr>
              <tr><td style="color:#7a7a9d;padding:5px 0">Due Date</td>
                  <td style="font-weight:600;color:#1a1a2e">{b_due_date_str}</td></tr>
              <tr><td style="color:#7a7a9d;padding:5px 0">Customer</td>
                  <td style="font-weight:600;color:#1a1a2e">{b_party_name}</td></tr>
              <tr><td style="color:#7a7a9d;padding:5px 0">City</td>
                  <td style="font-weight:600;color:#1a1a2e">{b_party_city}</td></tr>
              <tr><td style="color:#7a7a9d;padding:5px 0">Payment Mode</td>
                  <td style="font-weight:600;color:#059669">{b_pay_mode}</td></tr>
              <tr><td style="color:#7a7a9d;padding:5px 0">Items</td>
                  <td style="font-weight:600;color:#1a1a2e">{len(b_valid_items)} item(s)</td></tr>
            </table>""", unsafe_allow_html=True)
        else:
            st.info("Fill in customer name, city and invoice number.")
        st.markdown('</div>', unsafe_allow_html=True)

        if b_valid_items:
            with st.expander(f"📦 {len(b_valid_items)} Item(s) — with GST breakdown"):
                for i,it in enumerate(b_valid_items,1):
                    base=round(it["qty"]*it["price"],2)
                    cgst_c=round(base*CGST_RATE/100,2)
                    total_c=round(base+cgst_c*2,2)
                    st.markdown(f"**{i}. {it['desc']}**  \n"
                                f"{it['qty']} {it['unit']} × ₹{it['price']:,.2f} = "
                                f"₹{base:,.2f} + GST ₹{cgst_c*2:,.2f} = **₹{total_c:,.2f}**")
                    if i<len(b_valid_items): st.markdown("<hr style='margin:6px 0;border-color:#f0f2fa'>",unsafe_allow_html=True)

        st.markdown("<hr/>", unsafe_allow_html=True)
        errs2=[]
        if not b_party_name.strip(): errs2.append("Customer Name is required.")
        if not b_party_city.strip():  errs2.append("City is required.")
        if not b_invoice_no.strip():  errs2.append("Invoice Number is required.")
        if not b_valid_items:         errs2.append("Add at least one item.")
        if errs2:
            for e in errs2: st.warning(e)
        else:
            pdf2=build_invoice_pdf(
                b_party_name.strip(), b_party_city.strip(),
                b_party_gstin.strip(), b_party_phone.strip(),
                b_invoice_no.strip(), b_inv_date_str, b_due_date_str,
                b_pay_mode, b_valid_items,
                qr_bytes=st.session_state.qr_bytes,
                sig_bytes=st.session_state.sig_bytes,
                bank_name=st.session_state.bank_name,
                bank_branch=st.session_state.bank_branch,
                bank_acno=st.session_state.bank_acno,
                bank_ifsc=st.session_state.bank_ifsc,
                bank_holder=st.session_state.bank_holder)
            st.success(f"✅ Ready — Grand Total ₹{grand2:,.2f}")
            st.download_button("⬇  Download Tax Invoice PDF", data=pdf2,
                file_name=f"Invoice_{b_invoice_no}.pdf",
                mime="application/pdf", use_container_width=True)
            st.caption(f"Saves as `Invoice_{b_invoice_no}.pdf`")
