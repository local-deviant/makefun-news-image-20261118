#!/usr/bin/env python3
"""Render the front page of THE WORLD TODAY for Wednesday, 18 November 2026.

Self-contained: only Pillow + the bundled fonts in fonts/ (SIL OFL).
No network, no clock, no randomness. Renders at 3x and downsamples with
LANCZOS, so running it twice writes byte-identical PNGs.

Layout (broadsheet front page, 1024x1024):
  folio line / nameplate / double rule / sub-masthead
  lead: kicker, 2-line headline, dek, framed skyline illustration, body
  three-column story row (Kerch / Gulf / Alaska) with spot illustrations
  three-column brief row (Cyclone / Ebola / Dow-Nvidia)
  "Also today" strip / footer
"""
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
FONT_DIR = BASE / "fonts"

W = H = 1024
SS = 3  # supersample factor (deterministic; no grain, no random)

# ---- palette: newsprint cream + warm ink + one brick-red accent ----
PAPER = (245, 240, 225)
PANEL = (238, 232, 214)
SKY = (236, 220, 182)
WATER = (203, 196, 176)
INK = (26, 23, 18)
SOFT = (74, 68, 58)
RED = (163, 30, 34)

M = 36            # side margin
CW = W - 2 * M    # content width = 952

FONTS = {
    "gloock": {"regular": "Gloock-Regular.ttf"},
    "lora": {"regular": "Lora-Regular.ttf", "bold": "Lora-Bold.ttf",
             "italic": "Lora-Italic.ttf"},
    "crimson": {"italic": "CrimsonPro-Italic.ttf"},
    "sans": {"regular": "InstrumentSans-Regular.ttf",
             "bold": "InstrumentSans-Bold.ttf"},
    "mono": {"regular": "DMMono-Regular.ttf"},
}


def font(role, size, weight="regular"):
    path = FONT_DIR / FONTS[role][weight]
    return ImageFont.truetype(str(path), int(round(size * SS)))


def s(v):
    """Final px -> supersampled px."""
    return int(round(v * SS))


# ---- canvas ---------------------------------------------------------
img = Image.new("RGB", (W * SS, H * SS), PAPER)
dr = ImageDraw.Draw(img)


def rect(x0, y0, x1, y1, fill):
    dr.rectangle([s(x0), s(y0), s(x1), s(y1)], fill=fill)


def hline(x0, x1, y, w, fill=INK):
    rect(x0, y - w / 2, x1, y + w / 2, fill)


def vline(x, y0, y1, w, fill=INK):
    rect(x - w / 2, y0, x + w / 2, y1, fill)


def line(x0, y0, x1, y1, w, fill=INK):
    dr.line([s(x0), s(y0), s(x1), s(y1)], fill=fill, width=max(1, s(w)))


def poly(points, fill):
    dr.polygon([(s(x), s(y)) for x, y in points], fill=fill)


def disk(cx, cy, r, fill):
    dr.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=fill)


def outline(x0, y0, x1, y1, w, fill=INK):
    rect(x0, y0, x1, y0 + w, fill)
    rect(x0, y1 - w, x1, y1, fill)
    rect(x0, y0, x0 + w, y1, fill)
    rect(x1 - w, y0, x1, y1, fill)


# ---- text -----------------------------------------------------------
def tw(text, f):
    return dr.textlength(text, font=f) / SS


def fit_size(text, target_px, role, weight="regular", lo=8, hi=200):
    """Largest final-px size so text fits within target_px."""
    lo_i, hi_i = lo, hi
    while lo_i < hi_i:
        mid = (lo_i + hi_i + 1) // 2
        if tw(text, font(role, mid, weight)) <= target_px:
            lo_i = mid
        else:
            hi_i = mid - 1
    return lo_i


def wrap(text, f, max_px):
    """Greedy word wrap into lines fitting max_px."""
    lines, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        if tw(test, f) <= max_px or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(x, y_baseline, txt, f, fill=INK, align="left"):
    """Draw one line; y is the baseline in final px."""
    w = tw(txt, f)
    if align == "center":
        x = x - w / 2
    elif align == "right":
        x = x - w
    dr.text((s(x), s(y_baseline)), txt, font=f, fill=fill, anchor="ls")
    return w


def tracked(x, y_baseline, txt, f, fill=INK, tracking=0.0, align="left"):
    """Draw one line with letter-spacing (tracking in final px per gap)."""
    widths = [dr.textlength(c, font=f) / SS for c in txt]
    total = sum(widths) + tracking * max(0, len(txt) - 1)
    if align == "center":
        x = x - total / 2
    elif align == "right":
        x = x - total
    xx = x
    for c, w in zip(txt, widths):
        dr.text((s(xx), s(y_baseline)), c, font=f, fill=fill, anchor="ls")
        xx += w + tracking
    return total


def block(x, y_baseline, txt, f, max_px, lh, fill=INK):
    """Wrap + draw stacked lines; honours explicit "\n" breaks.
    Returns baseline of the last line and the line count."""
    lines = []
    for part in txt.split("\n"):
        lines.extend(wrap(part, f, max_px))
    for i, ln in enumerate(lines):
        text(x, y_baseline + i * lh, ln, f, fill=fill)
    return y_baseline + (len(lines) - 1) * lh, len(lines)


# =====================================================================
# 1. Folio line
# =====================================================================
f_folio = font("mono", 12.5)
tracked(M, 30, "WEDNESDAY, 18 NOVEMBER 2026", f_folio, fill=INK, tracking=1.0)
tracked(W - M, 30, "No. 322  —  PRICE $2.50", f_folio, fill=INK, tracking=1.0,
        align="right")
hline(M, W - M, 40, 1.5)

# =====================================================================
# 2. Nameplate
# =====================================================================
name_size = fit_size("THE WORLD TODAY", CW, "gloock")
f_name = font("gloock", name_size)
asc, _desc = f_name.getmetrics()
asc = asc / SS
name_base = 46 + asc
text(W / 2, name_base, "THE WORLD TODAY", f_name, fill=INK, align="center")
hline(M, W - M, name_base + 12, 3)
hline(M, W - M, name_base + 18, 1)

# =====================================================================
# 3. Sub-masthead
# =====================================================================
f_sub = font("mono", 12)
sub_base = name_base + 34
tracked(W / 2, sub_base, "INTERNATIONAL EDITION", f_sub, fill=SOFT,
        tracking=2.5, align="center")

# =====================================================================
# 4. Lead story — kicker, headline, dek
# =====================================================================
f_kick = font("sans", 17, "bold")
kick_base = sub_base + 28
tracked(M, kick_base, "SUMMIT IN SHENZHEN", f_kick, fill=RED, tracking=2.5)

head_size = min(56, fit_size("Xi greets Trump in Shenzhen", CW, "gloock"))
f_head = font("gloock", head_size)
lh_head = head_size * 1.12
h1_base = kick_base + 50
text(M, h1_base, "Xi greets Trump in Shenzhen", f_head, fill=INK)
text(M, h1_base + lh_head, "ahead of three-way summit", f_head, fill=INK)

f_dek = font("lora", 19, "italic")
dek = ("Chinese and Russian leaders meet a day before Thursday's talks;\n"
       "the U.S.–China tariff truce runs to 10 January 2027.")
dek_last, _ = block(M, h1_base + lh_head + 28, dek, f_dek, CW, 24, fill=SOFT)

# =====================================================================
# 5. Lead illustration — Shenzhen skyline (flat, original drawing)
# =====================================================================
ix0, ix1 = M, W - M
iy0 = dek_last + 14
iy1 = iy0 + 104
rect(ix0, iy0, ix1, iy1, SKY)
# sun — in a clear gap between towers on the right
disk(ix1 - 110, iy0 + 34, 22, RED)
# plane silhouette, upper left, clear of the towers
px, py = ix0 + 64, iy0 + 24
poly([(px - 30, py), (px - 7, py - 6), (px + 30, py - 2), (px + 34, py + 2),
      (px + 5, py + 6), (px - 16, py + 10), (px - 21, py + 5)], INK)
line(px - 46, py + 13, px - 64, py + 15, 1.5, fill=INK)
line(px - 40, py + 19, px - 56, py + 21, 1.5, fill=INK)
# towers (x_frac, width, height_frac) — bottoms sit above the water band
water_h = 16
base_y = iy1 - water_h
towers = [(0.02, 0.06, 0.52), (0.09, 0.05, 0.72), (0.15, 0.08, 0.44),
          (0.24, 0.05, 0.82), (0.30, 0.07, 0.58), (0.38, 0.05, 0.92),
          (0.44, 0.08, 0.48), (0.53, 0.05, 0.68), (0.59, 0.07, 0.40),
          (0.67, 0.05, 0.78), (0.73, 0.07, 0.52), (0.81, 0.05, 0.62),
          (0.95, 0.03, 0.66)]
pw = ix1 - ix0
for fx, fw, fh in towers:
    tx0 = ix0 + fx * pw
    tx1 = tx0 + fw * pw
    th = fh * (iy1 - iy0 - water_h)
    rect(tx0, base_y - th, tx1, base_y, INK)
    # windows: small paper dots, every other floor
    rows = int(th // 14)
    cols = max(1, int((tx1 - tx0) // 12))
    for r in range(rows):
        if r % 2:
            continue
        for c in range(cols):
            wx = tx0 + 5 + c * 12
            wy = base_y - th + 7 + r * 14
            if wx + 3 < tx1 - 2 and wy + 4 < base_y - 3:
                rect(wx, wy, wx + 3, wy + 4, PAPER)
# tallest tower: tapered crown
cx = ix0 + 0.405 * pw
poly([(cx - 14, base_y - 0.92 * (iy1 - iy0 - water_h)),
      (cx + 14, base_y - 0.92 * (iy1 - iy0 - water_h)),
      (cx + 6, base_y - 0.92 * (iy1 - iy0 - water_h) - 14),
      (cx - 6, base_y - 0.92 * (iy1 - iy0 - water_h) - 14)], INK)
# water band + harbour lines
rect(ix0, iy1 - water_h, ix1, iy1, WATER)
for i, wy in enumerate([iy1 - 12, iy1 - 7, iy1 - 3]):
    line(ix0 + 10 + i * 30, wy, ix1 - 10 - i * 22, wy, 1, fill=INK)
outline(ix0, iy0, ix1, iy1, 1.5)

# caption
f_cap = font("crimson", 12.5, "italic")
cap_base = iy1 + 18
text(M, cap_base,
     "Shenzhen, where the leaders met on the tarmac before Thursday's "
     "three-way summit.", f_cap, fill=SOFT)

# =====================================================================
# 6. Lead body (two lines)
# =====================================================================
f_body = font("lora", 15.5)
body = ("Xi Jinping greeted Donald Trump on the tarmac in Shenzhen on "
        "Wednesday, a day before the three leaders sit down together — "
        "capping a week of shuttle diplomacy with the tariff truce intact "
        "until 10 January 2027.")
body_last, n_body = block(M, cap_base + 24, body, f_body, CW, 20, fill=INK)
assert n_body <= 3, f"lead body wrapped to {n_body} lines"

# =====================================================================
# 7. Heavy rule, then three-column story row
# =====================================================================
hline(M, W - M, body_last + 16, 3)

COLW = 304
GUT = 20
COLX = [M, M + COLW + GUT, M + 2 * (COLW + GUT)]  # 36, 360, 684

f_colkick = font("sans", 12, "bold")
f_colhead = font("lora", 24, "bold")
f_coldek = font("lora", 14)

rowA_kick = body_last + 38
stories_A = [
    ("UKRAINE",
     ["Kerch bridge span", "falls into strait"],
     "Ukraine hits the crossing to occupied Crimea for a second day; part "
     "of the road deck collapses into the strait, Kyiv says.",
     "bridge"),
    ("THE GULF",
     ["U.S. jets hit Guard", "site on Qeshm Island"],
     "U.S. jets hit a Revolutionary Guard missile site on Qeshm Island "
     "after Iranian drones targeted forces in Bahrain and Kuwait; a ship "
     "was hit near Hormuz.",
     "gulf"),
    ("MIDTERMS",
     ["Peltola takes Alaska;", "Senate goes 56–44"],
     "Democrat Mary Peltola unseats Republican Dan Sullivan in the last "
     "midterm race to be called; Democrats take the Senate 56–44, a net "
     "gain of nine seats.",
     "ballot"),
]


def spot_bridge(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, PANEL)
    mid = (x0 + x1) / 2
    # deck, left and right, with the middle span dropped
    line(x0 + 6, y0 + 14, mid - 34, y0 + 14, 2.5, fill=INK)
    line(mid + 34, y0 + 14, x1 - 6, y0 + 14, 2.5, fill=INK)
    # fallen span, tilted down into the water
    poly([(mid - 34, y0 + 12), (mid + 30, y0 + 12), (mid + 38, y0 + 20),
          (mid - 26, y0 + 20)], INK)
    rect(mid + 8, y0 + 20, mid + 16, y0 + 28, RED)
    # arch over the left deck (kept inside the panel)
    dr.arc([s(x0 + 18), s(y0 + 2), s(mid - 10), s(y0 + 26)], 180, 360,
           fill=INK, width=s(2))
    # support posts
    vline(x0 + 30, y0 + 14, y0 + 30, 2)
    vline(x1 - 30, y0 + 14, y0 + 30, 2)
    # water
    for wy in (y1 - 10, y1 - 5):
        line(x0 + 8, wy, x1 - 8, wy, 1, fill=INK)


def spot_gulf(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, PANEL)
    # jet, upper left (slim delta)
    jx, jy = x0 + 62, y0 + 13
    poly([(jx - 34, jy), (jx - 8, jy - 6), (jx + 32, jy - 2),
          (jx + 36, jy + 1), (jx + 2, jy + 5), (jx - 18, jy + 8)], INK)
    line(jx - 44, jy + 8, jx - 60, jy + 10, 1.5, fill=INK)
    # island with missile site, right
    ix = x1 - 92
    poly([(ix, y1 - 4), (ix + 18, y1 - 22), (ix + 74, y1 - 22),
          (ix + 92, y1 - 4)], INK)
    vline(ix + 46, y1 - 34, y1 - 22, 2.5)
    disk(ix + 46, y1 - 37, 3.5, RED)
    # waves
    for wy in (y1 - 10, y1 - 5):
        line(x0 + 8, wy, ix - 6, wy, 1, fill=INK)


def spot_ballot(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, PANEL)
    bx0, bx1 = x0 + 96, x0 + 208
    by0, by1 = y0 + 16, y1 - 6
    # ballot paper, half in the slot
    poly([(bx0 + 34, by0 - 12), (bx0 + 78, by0 - 12), (bx0 + 72, by0 + 4),
          (bx0 + 28, by0 + 4)], (252, 248, 238))
    outline(bx0 + 34, by0 - 12, bx0 + 78, by0 + 4, 1)
    # box
    rect(bx0, by0, bx1, by1, INK)
    rect(bx0 + 14, by0 + 3, bx1 - 14, by0 + 6, PAPER)
    # red check above the box
    line(bx0 + 118, by0 - 8, bx0 + 132, by0 + 4, 3, fill=RED)
    line(bx0 + 132, by0 + 4, bx0 + 158, by0 - 16, 3, fill=RED)


SPOTS = {"bridge": spot_bridge, "gulf": spot_gulf, "ballot": spot_ballot}

for (kicker, head_lines, dek_txt, kind), cx in zip(stories_A, COLX):
    tracked(cx, rowA_kick, kicker, f_colkick, fill=RED, tracking=2.0)
    hb = rowA_kick + 30
    for i, ln in enumerate(head_lines):
        assert tw(ln, f_colhead) <= COLW, f"headline too wide: {ln}"
        text(cx, hb + i * 28, ln, f_colhead, fill=INK)
    iy0a = hb + 28 + 12
    iy1a = iy0a + 44
    SPOTS[kind](cx, iy0a, cx + COLW, iy1a)
    dek_last_a, n_a = block(cx, iy1a + 20, dek_txt, f_coldek, COLW, 18,
                            fill=INK)
    assert n_a <= 4, f"Row A dek wrapped to {n_a} lines"

rowA_rule = iy1a + 20 + 3 * 18 + 14
hline(M, W - M, rowA_rule, 1)

# =====================================================================
# 8. Three-column brief row
# =====================================================================
rowB_kick = rowA_rule + 20
f_bkick = font("mono", 11.5)
f_bhead = font("lora", 21, "bold")
f_bdek = font("lora", 13.5)

stories_B = [
    ("INDIA",
     ["Cyclone Akvan", "nears India"],
     "Landfall is forecast on the Andhra Pradesh coast on Friday, with "
     "winds of 120–130 km/h gusting to 145 km/h."),
    ("CONGO",
     ["Ebola tops 11,000", "cases in Congo"],
     "The U.N. says more than 5,400 people have died; nearly three in "
     "four infected children under five do not survive."),
    ("MARKETS",
     ["Dow down 849;", "Nvidia beats"],
     "The Dow shed 849 points ahead of Nvidia's results; the chipmaker "
     "then reported $115.8bn in quarterly revenue, beating forecasts."),
]

for (kicker, head_lines, dek_txt), cx in zip(stories_B, COLX):
    tracked(cx, rowB_kick, kicker, f_bkick, fill=RED, tracking=1.5)
    hb = rowB_kick + 28
    for i, ln in enumerate(head_lines):
        assert tw(ln, f_bhead) <= COLW, f"brief headline too wide: {ln}"
        text(cx, hb + i * 25, ln, f_bhead, fill=INK)
    dek_last_b, n_b = block(cx, hb + 25 + 24, dek_txt, f_bdek, COLW, 17,
                            fill=INK)
    assert n_b <= 3, f"Row B dek wrapped to {n_b} lines"

rowB_rule = hb + 25 + 24 + 2 * 17 + 16
hline(M, W - M, rowB_rule, 1)

# =====================================================================
# 9. "Also today" strip
# =====================================================================
f_label = font("mono", 13)
f_also = font("lora", 13)
label = "ALSO TODAY — "
label_w = tw(label, f_label)
also_txt = ("Russian military plane crashes in Siberia, killing 19. "
            "U.S. loses measles-free status after 26 years. Knesset elects "
            "Matan Kahana speaker. Board of Peace faults Israel and Hamas "
            "over the Gaza truce.")
# first line shares its width with the label; the rest run full width
first_lines = wrap(also_txt, f_also, CW - label_w)
rest = " ".join(first_lines[1:])
also_lines = [first_lines[0]]
if rest:
    also_lines += wrap(rest, f_also, CW)
also_base = rowB_rule + 20
text(M, also_base, label, f_label, fill=RED)
text(M + label_w, also_base, also_lines[0], f_also, fill=INK)
for i, ln in enumerate(also_lines[1:], start=1):
    text(M, also_base + i * 17, ln, f_also, fill=INK)
also_last = also_base + (len(also_lines) - 1) * 17

# =====================================================================
# 10. Footer
# =====================================================================
hline(M, W - M, also_last + 14, 1.5)
f_foot = font("mono", 11)
foot_base = also_last + 30
assert foot_base <= 1008, f"footer too low: {foot_base}"
text(M, foot_base, "ILLUSTRATIONS ARE ORIGINAL DRAWINGS, NOT PHOTOGRAPHS.",
     f_foot, fill=SOFT)
text(W - M, foot_base, "PAGE 1", f_foot, fill=SOFT, align="right")

# =====================================================================
# Save (deterministic: no grain, no randomness anywhere)
# =====================================================================
out = img.resize((W, H), Image.LANCZOS).convert("RGB")
out_path = sys.argv[1] if len(sys.argv) > 1 else str(BASE / "entry.png")
out.save(out_path, format="PNG")
print(f"saved {out_path} {out.size} {out.mode}")
print(f"nameplate size={name_size} headline size={head_size} "
      f"footer baseline={foot_base}")
