"""
pdf/tax_invoice_pdf.py — Builds the GST Tax Invoice PDF
"""

import io

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as RLImage, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

from config import (
    COMPANY_ADDR1, COMPANY_EMAIL, COMPANY_GSTIN, COMPANY_NAME,
    COMPANY_TEL, LOGO_PATH, TERMS,
)
from utils import calc_gst_groups_nonzero, img_to_rl, num_to_words


def build_tax_invoice_pdf(
    party_name: str,
    party_city: str,
    party_gstin: str,
    place_of_supply: str,
    inv_no: str,
    inv_date: str,
    items: list[dict],
    qr_bytes: bytes | None = None,
    sig_bytes: bytes | None = None,
) -> bytes:
    """Generates a proper GST Tax Invoice PDF for Swastik Enterprises."""

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=10 * mm, bottomMargin=10 * mm,
    )
    W    = A4[0] - 30 * mm
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    title_s = ps("IT",  fontSize=14, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    ctr_s   = ps("IC",  fontSize=8,  alignment=TA_CENTER, leading=11)
    lft_s   = ps("IL",  fontSize=8,  alignment=TA_LEFT,   leading=11)
    sml_s   = ps("IS",  fontSize=7,  alignment=TA_LEFT,   leading=10)
    sml_b   = ps("ISB", fontSize=7,  fontName="Helvetica-Bold", alignment=TA_LEFT, leading=10)
    bold_c  = ps("IBC", fontSize=9,  fontName="Helvetica-Bold", alignment=TA_CENTER)
    hdr_s   = ps("IH",  fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_CENTER, leading=10)
    hdr_ls  = ps("IHL", fontSize=7.5, fontName="Helvetica-Bold", alignment=TA_LEFT,   leading=10)
    wrap_s  = ps("IWS", fontSize=7.5, alignment=TA_LEFT,   leading=10, wordWrap="LTR")
    wrap_c  = ps("IWC", fontSize=7.5, alignment=TA_CENTER, leading=10, wordWrap="LTR")
    wrap_r  = ps("IWR", fontSize=7.5, alignment=TA_RIGHT,  leading=10, wordWrap="LTR")
    gst_amt = ps("IGA", fontSize=7,  alignment=TA_RIGHT,  leading=8,  wordWrap="LTR")

    story = []

    # ── "Original for Recipient" label ────────────────────────────────────────
    orig_label = Table(
        [[Paragraph("ORIGINAL FOR RECIPIENT", ps(
            "OFR", fontSize=8, fontName="Helvetica-Bold",
            alignment=TA_RIGHT, textColor=colors.Color(.3, .3, .3),
        ))]],
        colWidths=[W],
    )
    orig_label.setStyle(TableStyle([
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
    ]))
    story.append(orig_label)

    # ── Header ──────────────────────────────────────────────────────────────────
    try:    logo = RLImage(LOGO_PATH, width=33 * mm, height=30 * mm)
    except: logo = Paragraph("", lft_s)

    hdr_txt = [
        Paragraph("<u>TAX INVOICE</u>", bold_c),
        Paragraph(COMPANY_NAME, title_s),
        Paragraph(COMPANY_ADDR1, ctr_s),
        Paragraph(COMPANY_GSTIN, ctr_s),
        Paragraph(f"{COMPANY_TEL}<br/>{COMPANY_EMAIL}", ctr_s),
    ]
    ht = Table([[logo, hdr_txt]], colWidths=[W * .20, W * .80])
    ht.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), .9, colors.black),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
    ]))
    story += [ht, Spacer(1, 3)]

    # ── Buyer + Invoice details ────────────────────────────────────────────────
    buyer_gstin_line = f"<b>GSTIN :</b> {party_gstin}" if party_gstin.strip() else ""
    pos_line         = f"<b>Place of Supply :</b> {place_of_supply}" if place_of_supply.strip() else ""
    buyer_lines      = ["<b>Bill To :</b>", party_name, party_city]
    if buyer_gstin_line: buyer_lines.append(buyer_gstin_line)
    if pos_line:         buyer_lines.append(pos_line)

    buyer_p = "<br/>".join(buyer_lines)
    inv_p   = (
        f"<b>Invoice No. :</b> {inv_no}<br/>"
        f"<b>Invoice Date :</b> {inv_date}<br/>"
        "<b>Supply Type :</b> Intra-State"
    )

    pt = Table([[Paragraph(buyer_p, lft_s), Paragraph(inv_p, lft_s)]], colWidths=[W * .55, W * .45])
    pt.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), .5, colors.black),
        ("LINEBEFORE",   (1, 0), (1,  0),  .5, colors.black),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
    ]))
    story += [pt, Spacer(1, 2 * mm)]

    # ── Items table (10 cols) ─────────────────────────────────────────────────
    cw = [W * .04, W * .24, W * .08, W * .08, W * .05, W * .05, W * .12, W * .10, W * .10, W * .14]

    hdr_row = [
        Paragraph("S.N.",                  hdr_s),
        Paragraph("Description of Goods",  hdr_ls),
        Paragraph("Brand",                 hdr_s),
        Paragraph("HSN/SAC",               hdr_s),
        Paragraph("Qty.",                  hdr_s),
        Paragraph("Unit",                  hdr_s),
        Paragraph("Taxable<br/>Amount",    hdr_s),
        Paragraph("CGST<br/>Amt.",         hdr_s),
        Paragraph("SGST<br/>Amt.",         hdr_s),
        Paragraph("Total<br/>Amount",      hdr_s),
    ]

    rows           = [hdr_row]
    subtotal       = total_qty = 0.0
    total_cgst_pdf = total_sgst_pdf = 0.0

    for i, it in enumerate(items, 1):
        rate    = float(it.get("gst", 18.0))
        taxable = round(it["qty"] * it["price"], 2)
        cgst    = round(taxable * rate / 2 / 100, 2) if rate > 0 else 0.0
        sgst    = round(taxable * rate / 2 / 100, 2) if rate > 0 else 0.0
        total   = round(taxable + cgst + sgst, 2)
        subtotal       += taxable
        total_qty      += it["qty"]
        total_cgst_pdf += cgst
        total_sgst_pdf += sgst
        # Convert newlines to <br/> for multi-line descriptions
        desc_text = it["desc"].replace("\n", "<br/>")
        rows.append([
            Paragraph(str(i),                   wrap_c),
            Paragraph(desc_text,                wrap_s),
            Paragraph(it.get("brand", ""),      wrap_c),
            Paragraph(it["hsn"],                wrap_c),
            Paragraph(f"{it['qty']:.2f}",       wrap_c),
            Paragraph(it["unit"],               wrap_c),
            Paragraph(f"{taxable:,.2f}",        wrap_r),
            Paragraph(f"{cgst:,.2f}",           wrap_r),
            Paragraph(f"{sgst:,.2f}",           wrap_r),
            Paragraph(f"{total:,.2f}",          wrap_r),
        ])

    subtotal       = round(subtotal, 2)
    total_cgst_pdf = round(total_cgst_pdf, 2)
    total_sgst_pdf = round(total_sgst_pdf, 2)
    total_tax_pdf  = round(total_cgst_pdf + total_sgst_pdf, 2)
    grand          = round(subtotal + total_tax_pdf, 2)
    round_off      = round(round(grand) - grand, 2)
    grand_rounded  = int(round(grand + round_off))
    first_tail_idx = len(rows)

    # Sub-total row
    sub_row    = [""] * 10
    sub_row[1] = Paragraph("<b>Sub-Total</b>", wrap_s)
    sub_row[6] = Paragraph(f"<b>{subtotal:,.2f}</b>",        wrap_r)
    sub_row[7] = Paragraph(f"<b>{total_cgst_pdf:,.2f}</b>",  wrap_r)
    sub_row[8] = Paragraph(f"<b>{total_sgst_pdf:,.2f}</b>",  wrap_r)
    sub_row[9] = Paragraph(f"<b>{(subtotal + total_tax_pdf):,.2f}</b>", wrap_r)
    rows.append(sub_row)

    # Round off
    if round_off != 0:
        ro_row    = [""] * 10
        ro_row[1] = Paragraph("Round Off", wrap_s)
        ro_row[9] = Paragraph(f"{round_off:+,.2f}", gst_amt)
        rows.append(ro_row)

    # Grand total
    gt_row    = [""] * 10
    gt_row[1] = Paragraph("<b>Grand Total (With GST)</b>", wrap_s)
    gt_row[9] = Paragraph(f"<b>{grand_rounded:,.2f}</b>",  wrap_r)
    rows.append(gt_row)

    n = len(rows)

    inv_t = Table(rows, colWidths=cw, repeatRows=1)
    inv_t.setStyle(TableStyle([
        ("BOX",          (0, 0),    (-1, -1),                .5, colors.black),
        ("INNERGRID",    (0, 0),    (-1, first_tail_idx),    .3, colors.black),
        ("LINEABOVE",    (0, first_tail_idx), (-1, first_tail_idx), .5, colors.black),
        ("LINEABOVE",    (0, n - 1),(-1, n - 1),             .8, colors.black),
        ("BACKGROUND",   (0, 0),    (-1, 0),                 colors.Color(.92, .92, .92)),
        ("BACKGROUND",   (0, first_tail_idx), (-1, first_tail_idx), colors.Color(.96, .96, .96)),
        ("BACKGROUND",   (0, n - 1),(-1, n - 1),             colors.Color(.88, .92, .98)),
        ("FONTNAME",     (0, 0),    (-1, 0),                 "Helvetica-Bold"),
        ("FONTNAME",     (0, n - 1),(-1, n - 1),             "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0),    (-1, -1),                7.5),
        ("ALIGN",        (0, 0),    (-1, -1),                "CENTER"),
        ("ALIGN",        (1, 1),    (1, first_tail_idx - 1), "LEFT"),
        ("ALIGN",        (1, first_tail_idx), (1, n - 1),    "LEFT"),
        ("ALIGN",        (6, 1),    (-1, -1),                "RIGHT"),
        ("VALIGN",       (0, 0),    (-1, -1),                "MIDDLE"),
        ("LEFTPADDING",  (0, 0),    (-1, -1),                2),
        ("RIGHTPADDING", (0, 0),    (-1, -1),                2),
        ("TOPPADDING",   (0, 0),    (-1, -1),                1),
        ("BOTTOMPADDING",(0, 0),    (-1, -1),                1),
        ("SPAN",         (1, n - 1),(5, n - 1)),
    ]))
    story += [inv_t, Spacer(1, 2 * mm)]

    # ── GST summary table ─────────────────────────────────────────────────────
    all_groups, _ = calc_gst_groups_nonzero(items)
    tax_hdr = [
        Paragraph("GST Rate",     hdr_s),
        Paragraph("Taxable Amt.", hdr_s),
        Paragraph("CGST Amt.",    hdr_s),
        Paragraph("SGST Amt.",    hdr_s),
        Paragraph("Total Tax",    hdr_s),
    ]
    tax_data = [tax_hdr]

    for rate in sorted(all_groups.keys()):
        g    = all_groups[rate]
        ttax = round(g["cgst"] + g["sgst"], 2)
        tax_data.append([
            Paragraph(f"{rate:.1f}%",         wrap_c),
            Paragraph(f"{g['taxable']:,.2f}", wrap_r),
            Paragraph(f"{g['cgst']:,.2f}",    wrap_r),
            Paragraph(f"{g['sgst']:,.2f}",    wrap_r),
            Paragraph(f"{ttax:,.2f}",         wrap_r),
        ])

    tax_sub = round(sum(g["taxable"] for g in all_groups.values()), 2)
    tax_data.append([
        Paragraph("<b>Total</b>",                  hdr_s),
        Paragraph(f"<b>{tax_sub:,.2f}</b>",        wrap_r),
        Paragraph(f"<b>{total_cgst_pdf:,.2f}</b>", wrap_r),
        Paragraph(f"<b>{total_sgst_pdf:,.2f}</b>", wrap_r),
        Paragraph(f"<b>{total_tax_pdf:,.2f}</b>",  wrap_r),
    ])
    nt = len(tax_data)

    tt = Table(tax_data, colWidths=[W * .12, W * .22, W * .22, W * .22, W * .22])
    tt.setStyle(TableStyle([
        ("BOX",          (0, 0),    (-1, -1),   .5, colors.black),
        ("INNERGRID",    (0, 0),    (-1, -1),   .3, colors.black),
        ("BACKGROUND",   (0, 0),    (-1, 0),    colors.Color(.92, .92, .92)),
        ("BACKGROUND",   (0, nt-1), (-1, nt-1), colors.Color(.88, .92, .98)),
        ("FONTNAME",     (0, 0),    (-1, 0),    "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0),    (-1, -1),   7.5),
        ("ALIGN",        (0, 0),    (-1, -1),   "CENTER"),
        ("ALIGN",        (1, 1),    (-1, -1),   "RIGHT"),
        ("VALIGN",       (0, 0),    (-1, -1),   "MIDDLE"),
        ("LEFTPADDING",  (0, 0),    (-1, -1),   2),
        ("RIGHTPADDING", (0, 0),    (-1, -1),   2),
        ("TOPPADDING",   (0, 0),    (-1, -1),   2),
        ("BOTTOMPADDING",(0, 0),    (-1, -1),   2),
    ]))
    story += [tt, Spacer(1, 2 * mm)]

    # ── Amount in words ───────────────────────────────────────���───────────────────
    story.append(Paragraph(f"<i>{num_to_words(grand_rounded)}</i>", lft_s))
    story.append(Spacer(1, 3 * mm))

    # ── Bank + Terms + Signature footer ───────────────────────────────────────────
    BANK_W     = W * 0.50
    bank_title = Paragraph("<b>Bank Details:</b>", sml_b)
    bank_info  = Paragraph(
        "Bank : <b>Indian Overseas Bank</b><br/>"
        "A/c No. : <b>346702000000466</b><br/>"
        "IFSC : <b>IOBA0003467</b><br/>"
        "Branch : <b>PARMANANDPUR, VARANASI</b>",
        sml_s,
    )

    if qr_bytes:
        try:
            qr_img    = img_to_rl(qr_bytes, 22, 22)
            bank_cell = Table(
                [[qr_img, [bank_title, Spacer(1, 2), bank_info]]],
                colWidths=[24 * mm, BANK_W - 28 * mm],
            )
            bank_cell.setStyle(TableStyle([
                ("VALIGN",       (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING",   (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 2),
            ]))
        except Exception:
            bank_cell = [bank_title, Spacer(1, 2), bank_info]
    else:
        bank_cell = [bank_title, Spacer(1, 2), bank_info]

    terms_title   = Paragraph("<b>Terms &amp; Conditions:</b>", sml_b)
    thanks_p      = Paragraph("Thanks for doing business with us!", sml_s)
    terms_items   = [Paragraph(f"{j}. {t}", sml_s) for j, t in enumerate(TERMS, 1)]
    for_p         = Paragraph(f"<b>For M/S-{COMPANY_NAME}:</b>", sml_s)
    declaration   = Paragraph(
        "<i>I/We hereby certify that food/goods mentioned in this invoice are"
        " warranted to be of the nature and quality which they purport to be.</i>",
        sml_s,
    )

    if sig_bytes:
        try:    sig_img = img_to_rl(sig_bytes, 30, 14)
        except: sig_img = Spacer(1, 14 * mm)
    else:
        sig_img = Spacer(1, 14 * mm)

    auth_p        = Paragraph("Authorized Signatory", sml_s)
    right_content = [terms_title, Spacer(1, 3), thanks_p, Spacer(1, 3)] + terms_items
    right_content += [Spacer(1, 4), declaration, Spacer(1, 4), for_p, Spacer(1, 3), sig_img, auth_p]

    footer_t = Table([[bank_cell, right_content]], colWidths=[BANK_W, BANK_W])
    footer_t.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), .5, colors.black),
        ("LINEBEFORE",   (1, 0), (1,  0),  .5, colors.black),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    story.append(footer_t)

    doc.build(story)
    return buf.getvalue()
