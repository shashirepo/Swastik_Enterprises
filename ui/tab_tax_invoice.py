"""
ui/tab_tax_invoice.py — Tab 2: Tax Invoice UI
"""

import base64
import datetime

import streamlit as st

from config import COMMON_UNITS, GST_OPTIONS, QR_PATH, SAMPLE_ITEMS, SIG_PATH
from pdf.tax_invoice_pdf import build_tax_invoice_pdf
from ui.styles import BANK_CARD_HTML, ITEMS_HEADER_INV
from utils import calc_gst_groups_nonzero, gen_invoice_no, num_to_words


def _build_invoice_summary(
    inv_sub, inv_cgst, inv_sgst, inv_tax,
    inv_grand_r, inv_all_grps,
    inv_no, inv_date_str, inv_party_name, inv_party_city,
    inv_party_gstin, inv_pos,
    inv_valid, errors,
    pdf_bytes=None,
) -> None:
    """Render the full right-panel summary card for Tax Invoice."""

    words = num_to_words(inv_grand_r)

    hero_html = f"""
<div class="summary-card fade-up">
  <div class="summary-hero" style="background:linear-gradient(135deg,#052e16 0%,#14532d 100%);">
    <div class="summary-hero-label">Invoice Total</div>
    <div class="summary-hero-amount">
      <span class="summary-hero-sym">₹</span>{inv_grand_r:,.0f}
    </div>
    <div class="summary-hero-words">{words}</div>
  </div>

  <!-- Financial Breakdown -->
  <div class="summary-body">
    <div class="summary-row">
      <span class="summary-lbl">Taxable Amount</span>
      <span class="summary-val">₹{inv_sub:,.2f}</span>
    </div>
    <div class="summary-row">
      <span class="summary-lbl">Total CGST</span>
      <span class="summary-val">₹{inv_cgst:,.2f}</span>
    </div>
    <div class="summary-row">
      <span class="summary-lbl">Total SGST</span>
      <span class="summary-val">₹{inv_sgst:,.2f}</span>
    </div>
    <div class="summary-row">
      <span class="summary-lbl">Total Tax (GST)</span>
      <span class="summary-val">₹{inv_tax:,.2f}</span>
    </div>
    <div class="summary-row grand">
      <span class="summary-lbl">Invoice Total (incl. GST)</span>
      <span class="summary-val" style="color:#059669">₹{inv_grand_r:,.0f}</span>
    </div>
  </div>"""

    # GST breakdown
    if inv_all_grps:
        gst_rows = ""
        for rate in sorted(inv_all_grps.keys()):
            g       = inv_all_grps[rate]
            exempt  = "  (0% exempt)" if rate == 0 else ""
            tax_amt = round(g["cgst"] + g["sgst"], 2)
            gst_rows += (
                f'<div class="gst-mini-row">'
                f'<div class="gst-mini-lbl">GST @ {rate:.1f}%{exempt}'
                f'<div class="gst-mini-sub">Taxable: \u20b9{g["taxable"]:,.2f}</div></div>'
                f'<div class="gst-mini-val">\u20b9{tax_amt:,.2f}</div>'
                f'</div>'
            )
        hero_html += (
            '<div class="gst-mini">'
            '<div class="gst-mini-hdr">GST Breakdown by Rate</div>'
            + gst_rows +
            f'<div class="gst-mini-row">'
            f'<div class="gst-mini-lbl">Total Tax Collected</div>'
            f'<div class="gst-mini-val">\u20b9{inv_tax:,.2f}</div>'
            f'</div></div>'
        )

    # Document preview
    if inv_no and inv_party_name and inv_party_city:
        gst_str = ", ".join(f"{r:.0f}%" for r in sorted(inv_all_grps.keys())) if inv_all_grps else "—"
        gstin_row = f'<div class="preview-row"><span class="preview-lbl">Buyer GSTIN</span><span class="preview-val">{inv_party_gstin}</span></div>' if inv_party_gstin.strip() else ""
        pos_row   = f'<div class="preview-row"><span class="preview-lbl">Place of Supply</span><span class="preview-val">{inv_pos}</span></div>' if inv_pos.strip() else ""
        hero_html += f"""
  <div class="preview-block">
    <div class="preview-block-hdr">Invoice Preview</div>
    <div class="preview-row">
      <span class="preview-lbl">Invoice No.</span>
      <span class="preview-val">{inv_no}</span>
    </div>
    <div class="preview-row">
      <span class="preview-lbl">Date</span>
      <span class="preview-val">{inv_date_str}</span>
    </div>
    <div class="preview-row">
      <span class="preview-lbl">Bill To</span>
      <span class="preview-val">{inv_party_name}</span>
    </div>
    <div class="preview-row">
      <span class="preview-lbl">City</span>
      <span class="preview-val">{inv_party_city}</span>
    </div>
    {gstin_row}
    {pos_row}
    <div class="preview-row">
      <span class="preview-lbl">Line Items</span>
      <span class="preview-val">{len(inv_valid)} item(s)</span>
    </div>
    <div class="preview-row">
      <span class="preview-lbl">GST Slabs</span>
      <span class="preview-val">{gst_str}</span>
    </div>
  </div>"""

    # Download / errors
    if errors:
        err_rows = "".join(f'<div class="val-err"><span>⚠️</span>{e}</div>' for e in errors)
        hero_html += f'<div class="dl-section">{err_rows}</div>'
        hero_html += "</div>"
        st.markdown(hero_html, unsafe_allow_html=True)

    elif pdf_bytes:
        fname = f"TaxInvoice_{inv_no}.pdf"
        b64   = base64.b64encode(pdf_bytes).decode()
        hero_html += """
  <div class="dl-section">
    <div class="dl-ready-badge">✅ &nbsp; Invoice PDF ready</div>"""
        hero_html += "</div></div>"
        st.markdown(hero_html, unsafe_allow_html=True)

        st.download_button(
            "⬇  Download Tax Invoice PDF",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
            key="inv_dl_btn",
        )
        st.markdown(
            f'<a class="dl-alt" href="data:application/pdf;base64,{b64}" download="{fname}">'
            f'📎 Click here to save PDF directly</a>'
            f'<div class="dl-caption">Saves as {fname}</div>',
            unsafe_allow_html=True,
        )

    else:
        hero_html += "</div>"
        st.markdown(hero_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────

def render_tab_tax_invoice() -> None:
    """Render the Tax Invoice tab."""

    inv_left, inv_right = st.columns([3.5, 1], gap="small")

    # ══════════════════════════════════════════════════════════════════════════
    # LEFT — form inputs
    # ══════════════════════════════════════════════════════════════════════════
    with inv_left:

        # ── Buyer Details ─────────────────────────────────────────────────────
        st.markdown('<div class="section-card"><div class="section-title">🏢 Buyer Details</div>', unsafe_allow_html=True)
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            inv_party_name = st.text_input("Buyer Name *", placeholder="e.g. SHASHI ENTERPRISES", key="inv_pname")
        with r1c2:
            inv_party_city = st.text_input("City *", placeholder="e.g. VARANASI", key="inv_pcity")
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            inv_party_gstin = st.text_input("Buyer GSTIN", placeholder="09XXXXX0000X1ZX  (optional)", key="inv_pgstin")
        with r2c2:
            inv_pos = st.text_input("Place of Supply", placeholder="e.g. Uttar Pradesh", key="inv_pos")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Invoice Details ───────────────────────────────────────────────────
        st.markdown('<div class="section-card"><div class="section-title">🧾 Invoice Details</div>', unsafe_allow_html=True)
        col_no, col_date, col_btn = st.columns([2.5, 2, 0.8])
        with col_no:
            inv_no = st.text_input("Invoice Number *", value=st.session_state.inv_no, key="inv_no_input")
        with col_date:
            inv_date     = st.date_input("Invoice Date *", value=datetime.date.today(), key="inv_date")
            inv_date_str = inv_date.strftime("%d-%m-%Y")
        with col_btn:
            st.write(""); st.write("")
            if st.button("↻ New", use_container_width=True, key="inv_new_btn", help="Generate new invoice number"):
                st.session_state.inv_no = gen_invoice_no()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Line Items ────────────────────────────────────────────────────────
        st.markdown('<div class="section-card"><div class="section-title">📦 Line Items</div>', unsafe_allow_html=True)
        st.markdown(ITEMS_HEADER_INV, unsafe_allow_html=True)

        inv_row_list  = st.session_state.inv_items
        inv_to_delete = []

        for i, item in enumerate(inv_row_list):
            c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2.4, 0.85, 0.80, 0.50, 0.80, 0.65, 0.80, 0.65, 0.50], gap="small")
            with c1:
                item["desc"] = st.text_area("Desc", value=item["desc"],
                                   key=f"inv_d{i}", label_visibility="collapsed",
                                   placeholder="Description of goods", height=68)
            with c2:
                item["brand"] = st.text_input("Brand", value=item.get("brand", ""),
                                    key=f"inv_br{i}", label_visibility="collapsed", placeholder="Brand")
            with c3:
                item["hsn"] = st.text_input("HSN", value=item["hsn"],
                                  key=f"inv_h{i}", label_visibility="collapsed", placeholder="HSN")
            with c4:
                item["qty"] = st.number_input("Qty", value=float(item["qty"]),
                                  min_value=0.0, step=1.0, key=f"inv_q{i}",
                                  label_visibility="collapsed", format="%.2f")
            with c5:
                item["unit"] = st.selectbox("Unit", COMMON_UNITS,
                                  index=COMMON_UNITS.index(item["unit"]) if item["unit"] in COMMON_UNITS else 0,
                                  key=f"inv_u{i}", label_visibility="collapsed")
            with c6:
                gst_str2 = st.selectbox("GST%",
                               [f"{g:.0f}%" for g in GST_OPTIONS],
                               index=GST_OPTIONS.index(float(item.get("gst", 18.0)))
                                     if float(item.get("gst", 18.0)) in GST_OPTIONS else 3,
                               key=f"inv_g{i}", label_visibility="collapsed")
                item["gst"] = float(gst_str2.replace("%", ""))
            with c7:
                price_str = st.text_input("Price", value=f"{item['price']:.2f}",
                                key=f"inv_p{i}", label_visibility="collapsed", placeholder="0.00")
                try:
                    item["price"] = max(0.0, float(price_str.replace(",", "").strip()))
                except (ValueError, AttributeError):
                    item["price"] = 0.0
            with c8:
                amt2 = item["qty"] * item["price"]
                st.markdown(f"<div class='row-amt'>₹{amt2:,.2f}</div>", unsafe_allow_html=True)
            with c9:
                if st.button("✕", key=f"inv_del{i}", help="Remove this row"):
                    inv_to_delete.append(i)

        for idx in reversed(inv_to_delete):
            st.session_state.inv_items.pop(idx)
            st.rerun()

        ia, il = st.columns(2)
        with ia:
            if st.button("＋  Add Row", use_container_width=True, key="inv_add"):
                st.session_state.inv_items.append(
                    {"desc": "", "hsn": "", "qty": 1.0, "unit": "Pcs.", "price": 0.0, "brand": "", "gst": 18.0}
                )
                st.rerun()
        with il:
            if st.button("📥  Load Sample Data", use_container_width=True, key="inv_load"):
                st.session_state.inv_items = [
                    {"desc": d, "hsn": h, "qty": q, "unit": u, "price": p, "brand": br, "gst": g}
                    for d, h, q, u, p, br, g in SAMPLE_ITEMS
                ]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Bank & Assets ─────────────────────────────────────────────────────
        st.markdown('<div class="section-card"><div class="section-title">🏦 Bank & Document Assets</div>', unsafe_allow_html=True)
        iq, is_ = st.columns(2)
        with iq:
            if st.session_state.qr_bytes:
                st.image(st.session_state.qr_bytes, caption=f"✅ QR Code  ({QR_PATH})", width=96)
            else:
                st.info(f"Place `{QR_PATH}` next to main.py")
        with is_:
            if st.session_state.sig_bytes:
                st.image(st.session_state.sig_bytes, caption=f"✅ Signature  ({SIG_PATH})", width=120)
            else:
                st.info(f"Place `{SIG_PATH}` next to main.py")
        st.markdown(BANK_CARD_HTML, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Items expander
        inv_valid_check = [it for it in st.session_state.inv_items if it["desc"].strip()]
        if inv_valid_check:
            with st.expander(f"📦  {len(inv_valid_check)} line item(s) — click to review"):
                for i, it in enumerate(inv_valid_check, 1):
                    amt3     = it["qty"] * it["price"]
                    brand    = f" · **{it['brand']}**" if it.get("brand") else ""
                    gst_note = " *(0% exempt)*" if float(it.get("gst", 18)) == 0 else f" · GST {it.get('gst',18):.0f}%"
                    st.markdown(
                        f"**{i}. {it['desc']}**{brand}{gst_note}  \n"
                        f"HSN `{it['hsn']}` &nbsp;|&nbsp; {it['qty']:.2f} {it['unit']} × "
                        f"₹{it['price']:,.2f} = **₹{amt3:,.2f}**"
                    )
                    if i < len(inv_valid_check):
                        st.markdown("<hr style='margin:8px 0;border-color:#f1f5f9'>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # RIGHT — summary + download
    # ══════════════════════════════════════════════════════════════════════════
    with inv_right:
        inv_valid = [it for it in st.session_state.inv_items if it["desc"].strip()]
        inv_sub   = sum(it["qty"] * it["price"] for it in inv_valid)
        inv_all_grps, inv_nz = calc_gst_groups_nonzero(inv_valid)
        inv_cgst  = round(sum(g["cgst"] for g in inv_nz.values()), 2)
        inv_sgst  = round(sum(g["sgst"] for g in inv_nz.values()), 2)
        inv_tax   = round(inv_cgst + inv_sgst, 2)
        inv_grand_r = round(inv_sub + inv_tax)

        inv_errs = []
        if not inv_party_name.strip(): inv_errs.append("Buyer Name is required.")
        if not inv_party_city.strip():  inv_errs.append("City is required.")
        if not inv_no.strip():          inv_errs.append("Invoice Number is required.")
        if not inv_valid:               inv_errs.append("Add at least one line item.")

        inv_pdf = None
        if not inv_errs:
            inv_pdf = build_tax_invoice_pdf(
                inv_party_name.strip(), inv_party_city.strip(),
                inv_party_gstin.strip(), inv_pos.strip(),
                inv_no.strip(), inv_date_str, inv_valid,
                qr_bytes=st.session_state.qr_bytes,
                sig_bytes=st.session_state.sig_bytes,
            )

        _build_invoice_summary(
            inv_sub=inv_sub,
            inv_cgst=inv_cgst,
            inv_sgst=inv_sgst,
            inv_tax=inv_tax,
            inv_grand_r=inv_grand_r,
            inv_all_grps=inv_all_grps,
            inv_no=inv_no,
            inv_date_str=inv_date_str,
            inv_party_name=inv_party_name,
            inv_party_city=inv_party_city,
            inv_party_gstin=inv_party_gstin,
            inv_pos=inv_pos,
            inv_valid=inv_valid,
            errors=inv_errs,
            pdf_bytes=inv_pdf,
        )
