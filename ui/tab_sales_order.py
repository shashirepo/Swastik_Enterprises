"""
ui/tab_sales_order.py — Tab 1: Sales Order / Quotation UI
"""

import base64
import datetime

import streamlit as st

from config import COMMON_UNITS, GST_OPTIONS, QR_PATH, SAMPLE_ITEMS, SIG_PATH
from pdf.sales_order_pdf import build_pdf
from ui.styles import BANK_CARD_HTML, ITEMS_HEADER_SO
from utils import calc_gst_groups_nonzero, gen_order_no, num_to_words


def _build_summary_card(
    subtotal, total_cgst, total_sgst, total_tax,
    grand_rounded, all_grps,
    order_no, order_date_str, party_name, party_city,
    valid_items, errors,
    pdf_bytes=None,
) -> None:
    """Render the full right-panel summary card."""

    words = num_to_words(grand_rounded)

    # ── Hero grand total ──────────────────────────────────────────────────────
    hero_html = f"""
<div class="summary-card fade-up">
  <div class="summary-hero">
    <div class="summary-hero-label">Order Grand Total</div>
    <div class="summary-hero-amount">
      <span class="summary-hero-sym">₹</span>{grand_rounded:,.0f}
    </div>
    <div class="summary-hero-words">{words}</div>
  </div>

  <!-- Financial Breakdown -->
  <div class="summary-body">
    <div class="summary-row">
      <span class="summary-lbl">Subtotal (before tax)</span>
      <span class="summary-val">₹{subtotal:,.2f}</span>
    </div>
    <div class="summary-row">
      <span class="summary-lbl">Total CGST</span>
      <span class="summary-val">₹{total_cgst:,.2f}</span>
    </div>
    <div class="summary-row">
      <span class="summary-lbl">Total SGST</span>
      <span class="summary-val">₹{total_sgst:,.2f}</span>
    </div>
    <div class="summary-row">
      <span class="summary-lbl">Total Tax</span>
      <span class="summary-val">₹{total_tax:,.2f}</span>
    </div>
    <div class="summary-row grand">
      <span class="summary-lbl">Grand Total (incl. GST)</span>
      <span class="summary-val">₹{grand_rounded:,.0f}</span>
    </div>
  </div>"""

    # ── GST breakdown by rate ─────────────────────────────────────────────────
    if all_grps:
        gst_rows = ""
        for rate in sorted(all_grps.keys()):
            g    = all_grps[rate]
            half = rate / 2
            exempt = "  (0% exempt)" if rate == 0 else ""
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
            f'<div class="gst-mini-val">\u20b9{total_tax:,.2f}</div>'
            f'</div></div>'
        )

    # ── Document preview ──────────────────────────────────────────────────────
    if order_no and party_name and party_city:
        gst_groups_str = ", ".join(f"{r:.0f}%" for r in sorted(all_grps.keys())) if all_grps else "—"
        hero_html += f"""
  <div class="preview-block">
    <div class="preview-block-hdr">Document Preview</div>
    <div class="preview-row">
      <span class="preview-lbl">Order No.</span>
      <span class="preview-val">{order_no}</span>
    </div>
    <div class="preview-row">
      <span class="preview-lbl">Date</span>
      <span class="preview-val">{order_date_str}</span>
    </div>
    <div class="preview-row">
      <span class="preview-lbl">Party</span>
      <span class="preview-val">{party_name}</span>
    </div>
    <div class="preview-row">
      <span class="preview-lbl">City</span>
      <span class="preview-val">{party_city}</span>
    </div>
    <div class="preview-row">
      <span class="preview-lbl">Line Items</span>
      <span class="preview-val">{len(valid_items)} item(s)</span>
    </div>
    <div class="preview-row">
      <span class="preview-lbl">GST Slabs</span>
      <span class="preview-val">{gst_groups_str}</span>
    </div>
  </div>"""

    # ── Download section ──────────────────────────────────────────────────────
    if errors:
        err_rows = "".join(f'<div class="val-err"><span>⚠️</span>{e}</div>' for e in errors)
        hero_html += f"""
  <div class="dl-section">
    {err_rows}
  </div>"""
    elif pdf_bytes:
        fname = f"SalesOrder_{order_no}.pdf"
        b64   = base64.b64encode(pdf_bytes).decode()
        hero_html += f"""
  <div class="dl-section">
    <div class="dl-ready-badge">
      ✅ &nbsp; PDF ready — ₹{grand_rounded:,.0f}
    </div>"""
        # Close card before Streamlit download button
        hero_html += "</div></div>"
        st.markdown(hero_html, unsafe_allow_html=True)

        st.download_button(
            "⬇  Download Sales Order PDF",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
            key="so_dl_btn",
        )
        st.markdown(
            f'<a class="dl-alt" href="data:application/pdf;base64,{b64}" download="{fname}">'
            f'📎 Click here to save PDF directly</a>'
            f'<div class="dl-caption">Saves as {fname}</div>',
            unsafe_allow_html=True,
        )
        return  # already closed

    hero_html += "</div>"  # close summary-card
    st.markdown(hero_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────

def render_tab_sales_order() -> None:
    """Render the Sales Order / Quotation tab."""

    left, right = st.columns([3.5, 1], gap="small")

    # ══════════════════════════════════════════════════════════════════════════
    # LEFT — form inputs
    # ══════════════════════════════════════════════════════════════════════════
    with left:

        # ── Party Details ─────────────────────────────────────────────────────
        st.markdown('<div class="section-card"><div class="section-title">🏢 Party Details</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            party_name = st.text_input("Party Name *", placeholder="e.g. SHASHI ENTERPRISES", key="so_pname")
        with c2:
            party_city = st.text_input("City *", placeholder="e.g. VARANASI", key="so_pcity")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Order Details ─────────────────────────────────────────────────────
        st.markdown('<div class="section-card"><div class="section-title">📋 Order Details</div>', unsafe_allow_html=True)
        col_no, col_date, col_btn = st.columns([2.5, 2, 0.8])
        with col_no:
            order_no = st.text_input("Order Number *", value=st.session_state.order_no, key="so_orderno")
        with col_date:
            order_date     = st.date_input("Order Date *", value=datetime.date.today(), key="so_date")
            order_date_str = order_date.strftime("%d-%m-%Y")
        with col_btn:
            st.write(""); st.write("")
            if st.button("↻ New", use_container_width=True, key="so_new_btn", help="Generate new order number"):
                st.session_state.order_no = gen_order_no()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Line Items ────────────────────────────────────────────────────────
        st.markdown('<div class="section-card"><div class="section-title">📦 Line Items</div>', unsafe_allow_html=True)
        st.markdown(ITEMS_HEADER_SO, unsafe_allow_html=True)

        # Process any pending deletion BEFORE rendering rows
        if st.session_state.get("so_pending_delete") is not None:
            del_idx = st.session_state.so_pending_delete
            st.session_state.so_pending_delete = None
            if 0 <= del_idx < len(st.session_state.order_items):
                st.session_state.order_items.pop(del_idx)
            st.rerun()

        row_list = st.session_state.order_items

        for i, item in enumerate(row_list):
            c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2.4, 0.85, 0.80, 0.50, 0.80, 0.65, 0.80, 0.65, 0.50], gap="small")
            with c1:
                item["desc"] = st.text_area("Desc", value=item["desc"],
                                   key=f"so_d{i}", label_visibility="collapsed",
                                   placeholder="Description of goods", height=68)
            with c2:
                item["brand"] = st.text_input("Brand", value=item.get("brand", ""),
                                    key=f"so_br{i}", label_visibility="collapsed", placeholder="Brand")
            with c3:
                item["hsn"] = st.text_input("HSN", value=item["hsn"],
                                  key=f"so_h{i}", label_visibility="collapsed", placeholder="HSN")
            with c4:
                item["qty"] = st.number_input("Qty", value=float(item["qty"]),
                                  min_value=0.0, step=1.0, key=f"so_q{i}",
                                  label_visibility="collapsed", format="%.2f")
            with c5:
                item["unit"] = st.selectbox("Unit", COMMON_UNITS,
                                  index=COMMON_UNITS.index(item["unit"]) if item["unit"] in COMMON_UNITS else 0,
                                  key=f"so_u{i}", label_visibility="collapsed")
            with c6:
                gst_str = st.selectbox("GST%",
                              [f"{g:.0f}%" for g in GST_OPTIONS],
                              index=GST_OPTIONS.index(float(item.get("gst", 18.0)))
                                    if float(item.get("gst", 18.0)) in GST_OPTIONS else 3,
                              key=f"so_g{i}", label_visibility="collapsed")
                item["gst"] = float(gst_str.replace("%", ""))
            with c7:
                price_str = st.text_input("Price", value=f"{item['price']:.2f}",
                                key=f"so_p{i}", label_visibility="collapsed", placeholder="0.00")
                try:
                    item["price"] = max(0.0, float(price_str.replace(",", "").strip()))
                except (ValueError, AttributeError):
                    item["price"] = 0.0
            with c8:
                amt = item["qty"] * item["price"]
                st.markdown(f"<div class='row-amt'>₹{amt:,.2f}</div>", unsafe_allow_html=True)
            with c9:
                if st.button("✕", key=f"so_del{i}", help="Remove this row"):
                    st.session_state.so_pending_delete = i
                    st.rerun()

        ca, cl = st.columns(2)
        with ca:
            if st.button("＋  Add Row", use_container_width=True, key="so_add"):
                st.session_state.order_items.append(
                    {"desc": "", "hsn": "", "qty": 1.0, "unit": "Pcs.", "price": 0.0, "brand": "", "gst": 18.0}
                )
                st.rerun()
        with cl:
            if st.button("📥  Load Sample Data", use_container_width=True, key="so_load"):
                st.session_state.order_items = [
                    {"desc": d, "hsn": h, "qty": q, "unit": u, "price": p, "brand": br, "gst": g}
                    for d, h, q, u, p, br, g in SAMPLE_ITEMS
                ]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Bank & Assets ─────────────────────────────────────────────────────
        st.markdown('<div class="section-card"><div class="section-title">🏦 Bank & Document Assets</div>', unsafe_allow_html=True)
        uq, us = st.columns(2)
        with uq:
            if st.session_state.qr_bytes:
                st.image(st.session_state.qr_bytes, caption=f"✅ QR Code  ({QR_PATH})", width=96)
            else:
                st.info(f"Place `{QR_PATH}` next to main.py")
        with us:
            if st.session_state.sig_bytes:
                st.image(st.session_state.sig_bytes, caption=f"✅ Signature  ({SIG_PATH})", width=120)
            else:
                st.info(f"Place `{SIG_PATH}` next to main.py")
        st.markdown(BANK_CARD_HTML, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Items summary expander ─────────────────────────────────────────────
        valid_items = [it for it in st.session_state.order_items if it["desc"].strip()]
        if valid_items:
            with st.expander(f"📦  {len(valid_items)} line item(s) — click to review"):
                for i, it in enumerate(valid_items, 1):
                    amt      = it["qty"] * it["price"]
                    brand    = f" · **{it['brand']}**" if it.get("brand") else ""
                    gst_note = " *(0% exempt)*" if float(it.get("gst", 18)) == 0 else f" · GST {it.get('gst',18):.0f}%"
                    st.markdown(
                        f"**{i}. {it['desc']}**{brand}{gst_note}  \n"
                        f"HSN `{it['hsn']}` &nbsp;|&nbsp; {it['qty']:.2f} {it['unit']} × "
                        f"₹{it['price']:,.2f} = **₹{amt:,.2f}**"
                    )
                    if i < len(valid_items):
                        st.markdown("<hr style='margin:8px 0;border-color:#f1f5f9'>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # RIGHT — summary + download
    # ══════════════════════════════════════════════════════════════════════════
    with right:
        valid_items   = [it for it in st.session_state.order_items if it["desc"].strip()]
        subtotal      = sum(it["qty"] * it["price"] for it in valid_items)
        all_grps, nz  = calc_gst_groups_nonzero(valid_items)
        total_cgst    = round(sum(g["cgst"] for g in nz.values()), 2)
        total_sgst    = round(sum(g["sgst"] for g in nz.values()), 2)
        total_tax     = round(total_cgst + total_sgst, 2)
        grand_rounded = round(subtotal + total_tax)

        # Validation
        errs = []
        if not party_name.strip():  errs.append("Party Name is required.")
        if not party_city.strip():   errs.append("City is required.")
        if not order_no.strip():     errs.append("Order Number is required.")
        if not valid_items:          errs.append("Add at least one line item.")

        pdf_bytes = None
        if not errs:
            pdf_bytes = build_pdf(
                party_name.strip(), party_city.strip(),
                order_no.strip(), order_date_str, valid_items,
                qr_bytes=st.session_state.qr_bytes,
                sig_bytes=st.session_state.sig_bytes,
            )

        _build_summary_card(
            subtotal=subtotal,
            total_cgst=total_cgst,
            total_sgst=total_sgst,
            total_tax=total_tax,
            grand_rounded=grand_rounded,
            all_grps=all_grps,
            order_no=order_no,
            order_date_str=order_date_str,
            party_name=party_name,
            party_city=party_city,
            valid_items=valid_items,
            errors=errs,
            pdf_bytes=pdf_bytes,
        )
