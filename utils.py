"""
utils.py — Shared helper functions for SWASTIK ENTERPRISES app
"""

import io
import random
import string

from reportlab.lib.units import mm
from reportlab.platypus import Image as RLImage


# ── Number generators ─────────────────────────────────────────────────────────

def gen_order_no() -> str:
    return "SW" + "".join(random.choices(string.digits, k=3))


def gen_invoice_no() -> str:
    return "SWTK" + "".join(random.choices(string.digits, k=4))


# ── Amount in words ───────────────────────────────────────────────────────────

def num_to_words(amount: float) -> str:
    ones = [
        "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
        "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
        "Sixteen", "Seventeen", "Eighteen", "Nineteen",
    ]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def two(n: int) -> str:
        return ones[n] if n < 20 else (tens[n // 10] + (" " + ones[n % 10] if n % 10 else "")).strip()

    def three(n: int) -> str:
        return (
            ones[n // 100] + " Hundred" + (" " + two(n % 100) if n % 100 else "")
        ) if n >= 100 else two(n)

    rupees, paise = int(amount), round((amount - int(amount)) * 100)
    parts = []
    for div, label in [(10_00_00_000, "Arab"), (1_00_00_000, "Crore"), (1_00_000, "Lakh"), (1_000, "Thousand")]:
        if rupees >= div:
            parts.append(three(rupees // div) + " " + label)
            rupees %= div
    if rupees:
        parts.append(three(rupees))

    result = "Rupees " + (" ".join(parts) if parts else "Zero")
    if paise:
        result += f" and Paisa {two(paise)}"
    return result + " Only"


# ── Image helper ──────────────────────────────────────────────────────────────

def img_to_rl(img_bytes: bytes, w_mm: float, h_mm: float) -> RLImage:
    """Convert raw image bytes to a ReportLab Image with white background."""
    from PIL import Image as PILImage

    img = PILImage.open(io.BytesIO(img_bytes)).convert("RGBA")
    bg = PILImage.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    out = io.BytesIO()
    bg.save(out, format="PNG")
    out.seek(0)
    return RLImage(out, width=w_mm * mm, height=h_mm * mm)


# ── GST calculation helpers ───────────────────────────────────────────────────

def calc_gst_groups(items: list[dict]) -> dict:
    """
    Groups items by GST rate.
    Returns dict: { rate: {taxable, cgst, sgst} } — includes 0% items.
    """
    groups: dict = {}
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
    for r in groups:
        groups[r]["taxable"] = round(groups[r]["taxable"], 2)
        groups[r]["cgst"]    = round(groups[r]["cgst"],    2)
        groups[r]["sgst"]    = round(groups[r]["sgst"],    2)
    return groups


def calc_gst_groups_nonzero(items: list[dict]) -> tuple[dict, dict]:
    """
    Returns (all_groups, nonzero_groups).
    all_groups   — includes 0% rate items (for display).
    nonzero_groups — excludes 0% rate items (for tax totals).
    """
    all_groups    = calc_gst_groups(items)
    nonzero_groups = {r: g for r, g in all_groups.items() if r > 0}
    return all_groups, nonzero_groups
