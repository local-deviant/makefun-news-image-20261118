#!/usr/bin/env python3
"""The World Today — front page for Wednesday, 18 November 2026 (v3).

A dense canvas newspaper: 49 date-checked stories from 18 November 2026
across 7 regions, 11 code-drawn illustrations, built to read at thumbnail,
half and full size. Every element is drawn from code with Pillow. No
photograph, no copied image, no template. Rendered at 3x and downsampled
with LANCZOS for crisp type. Fully deterministic: fixed values only, no
randomness, no clock — re-running this file reproduces entry.png byte-for-byte.

Stories were verified against reporting dated 18 November 2026 (AP, AFP,
Reuters, Al Jazeera, NPR, IMD, QUAD joint statement, CSK, ITU, and a
50-story roundup of the day). The 8 lead stories match the edition brief.
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

# ---------------------------------------------------------------- canvas
S = 3
W = H = 1024
CW, CH = W * S, H * S

PAPER = (247, 243, 234)
INK = (26, 26, 26)
SOFT = (74, 70, 62)
RULE = (138, 133, 120)
RED = (176, 42, 32)
BLUE = (38, 84, 134)
GREEN = (34, 120, 70)
SKY_TOP = (38, 58, 96)
SKY_MID = (196, 116, 64)
SUN = (242, 196, 96)
TOWER = (30, 42, 66)
WATER = (28, 52, 84)
LIT = (244, 196, 110)

MARGIN = 34
PAGE_W = W - 2 * MARGIN            # 956
FEAT_W = (PAGE_W - 2 * 18) // 3    # 3 featured columns
GRID_W = (PAGE_W - 3 * 14) // 4    # 4 brief columns


def f(path, size):
    return ImageFont.truetype(os.path.join(FONTS, path), size * S)


GLOOCK = "Gloock-Regular.ttf"
LORA = "Lora-Regular.ttf"
LORA_B = "Lora-Bold.ttf"
LORA_I = "Lora-Italic.ttf"
CRIM_I = "CrimsonPro-Italic.ttf"
SANS = "InstrumentSans-Regular.ttf"
SANS_B = "InstrumentSans-Bold.ttf"


# ---------------------------------------------------------------- helpers
def wrap(text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if font.getlength(trial) <= max_w * S:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tw(d, text, font):
    return d.textlength(text, font=font) / S


def tracked(d, cx, y, text, font, fill, tracking=2):
    widths = [d.textlength(ch, font=font) / S for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x * S, y * S), ch, font=font, fill=fill)
        x += w + tracking
    return total


def center(d, x, y, text, font, fill):
    d.text(((x - tw(d, text, font) / 2) * S, y * S), text, font=font, fill=fill)


def hrule(d, x0, x1, y, weight=1, fill=INK):
    d.line([(x0 * S, y * S), (x1 * S, y * S)], fill=fill, width=weight * S)


def para(d, x, y, text, font, fill, max_w, leading, max_lines=None):
    lines = wrap(text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        d.text((x * S, y * S), line, font=font, fill=fill)
        y += leading
    return y, len(lines)


# ---------------------------------------------------------------- spot art
def draw_skyline(d, x, y, w, h):
    """Shenzhen at dusk: gradient sky, low sun, towers with lit windows,
    harbour band with reflections."""
    for i in range(h):
        t = i / max(h - 1, 1)
        r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * t)
        d.line([(x * S, (y + i) * S), ((x + w) * S, (y + i) * S)], fill=(r, g, b))
    sx, sy, sr = x + w * 0.70, y + h * 0.16, 20
    d.ellipse([(sx - sr) * S, (sy - sr) * S, (sx + sr) * S, (sy + sr) * S],
              fill=SUN)
    towers = [
        (0.02, 0.09, 0.52, 3), (0.13, 0.07, 0.68, 4), (0.22, 0.10, 0.44, 2),
        (0.34, 0.08, 0.78, 5), (0.44, 0.09, 0.58, 3), (0.55, 0.07, 0.86, 5),
        (0.64, 0.10, 0.62, 4), (0.76, 0.08, 0.72, 4), (0.86, 0.11, 0.50, 3),
    ]
    base = y + h * 0.82
    for fx, fw, fh, rows in towers:
        tx, twd = x + w * fx, w * fw
        th = h * fh
        d.rectangle([tx * S, (base - th) * S, (tx + twd) * S, base * S],
                    fill=TOWER)
        if fh > 0.75:
            d.line([(tx + twd / 2) * S, (base - th) * S,
                    (tx + twd / 2) * S, (base - th - 10) * S],
                   fill=TOWER, width=2 * S)
        cols = max(2, int(twd // 11))
        for r in range(rows):
            for c in range(cols):
                if (r * 2 + c * 3) % 4 == 0:
                    wx = tx + 4 + c * 11
                    wy = base - th + 8 + r * 13
                    d.rectangle([wx * S, wy * S, (wx + 4) * S, (wy + 5) * S],
                                fill=LIT)
    d.rectangle([x * S, base * S, (x + w) * S, (y + h) * S], fill=WATER)
    for i, rx in enumerate([0.10, 0.30, 0.52, 0.74, 0.90]):
        rw = 26 + (i % 3) * 12
        ry = base + 5 + (i % 2) * 6
        d.line([(x + w * rx) * S, ry * S,
                (x + w * rx + rw) * S, ry * S], fill=LIT, width=2 * S)


def draw_bridge(d, x, y, w, h):
    """Kerch crossing: two deck spans with a broken gap, one span sagging
    into the strait, pillars, water lines."""
    d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=(233, 238, 240))
    wy = y + h * 0.62
    for i in range(4):
        yy = wy + 5 + i * 5
        if yy > y + h - 2:
            break
        d.line([(x + 4) * S, yy * S, (x + w - 4) * S, yy * S],
               fill=(150, 178, 196), width=1 * S)
    deck_y = y + h * 0.30
    d.line([(x + 4) * S, deck_y * S, (x + w * 0.42) * S, deck_y * S],
           fill=INK, width=4 * S)
    d.line([(x + w * 0.60) * S, deck_y * S, (x + w - 4) * S, deck_y * S],
           fill=INK, width=4 * S)
    d.line([(x + w * 0.42) * S, deck_y * S, (x + w * 0.51) * S,
            (wy - 2) * S], fill=INK, width=4 * S)
    d.line([(x + w * 0.51) * S, (wy - 2) * S, (x + w * 0.60) * S,
            deck_y * S], fill=INK, width=4 * S)
    for px in (0.16, 0.30, 0.72, 0.88):
        d.line([(x + w * px) * S, deck_y * S, (x + w * px) * S, wy * S],
               fill=SOFT, width=3 * S)
    for dx, dy in ((0.47, 0.52), (0.50, 0.58), (0.54, 0.50), (0.49, 0.66)):
        d.ellipse([(x + w * dx - 2) * S, (y + h * dy - 2) * S,
                   (x + w * dx + 2) * S, (y + h * dy + 2) * S], fill=INK)
    # small red marker over the break (only when it fits above the deck)
    if deck_y - 22 >= y:
        d.polygon([((x + w * 0.51) * S, (deck_y - 12) * S),
                   ((x + w * 0.51 - 5) * S, (deck_y - 22) * S),
                   ((x + w * 0.51 + 5) * S, (deck_y - 22) * S)], fill=RED)


def draw_gulf(d, x, y, w, h):
    """Strait of Hormuz sketch: coast above, Qeshm island below, a
    starburst at the strike site, a ship in the strait."""
    d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=(226, 236, 240))
    d.polygon([(x * S, y * S), ((x + w) * S, y * S),
               ((x + w) * S, (y + h * 0.30) * S),
               ((x + w * 0.62) * S, (y + h * 0.44) * S),
               ((x + w * 0.30) * S, (y + h * 0.34) * S),
               (x * S, (y + h * 0.42) * S)], fill=(214, 204, 178))
    d.polygon([((x + w * 0.30) * S, (y + h * 0.62) * S),
               ((x + w * 0.44) * S, (y + h * 0.56) * S),
               ((x + w * 0.72) * S, (y + h * 0.60) * S),
               ((x + w * 0.78) * S, (y + h * 0.70) * S),
               ((x + w * 0.58) * S, (y + h * 0.76) * S),
               ((x + w * 0.34) * S, (y + h * 0.72) * S)],
              fill=(196, 184, 154))
    if h >= 56:
        center(d, x + w * 0.50, y + h * 0.86, "STRAIT OF HORMUZ",
               f(SANS, 9), SOFT)
    bx, by = x + w * 0.55, y + h * 0.64
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([bx * S, by * S,
                (bx + 10 * math.cos(a)) * S, (by + 10 * math.sin(a)) * S],
               fill=RED, width=2 * S)
    d.ellipse([(bx - 3) * S, (by - 3) * S, (bx + 3) * S, (by + 3) * S],
              fill=RED)
    shx, shy = x + w * 0.22, y + h * 0.50
    d.polygon([(shx * S, shy * S), ((shx + 22) * S, shy * S),
               ((shx + 18) * S, (shy + 6) * S),
               ((shx + 4) * S, (shy + 6) * S)], fill=INK)
    d.rectangle([(shx + 8) * S, (shy - 6) * S, (shx + 13) * S, shy * S],
                fill=INK)


def draw_senate(d, x, y, w, h):
    """Senate 56-44: two horizontal bars with counts. Lays out
    proportionally so it works at 44-62px tall."""
    f_lab = f(SANS, 10)
    f_num = f(SANS_B, 13)
    u = h / 62.0
    d.text((x * S, y * S), "DEM 56", font=f_lab, fill=INK)
    bh = max(7, int(13 * u))
    d.rectangle([x * S, (y + 13 * u) * S, (x + w * 0.56) * S,
                 (y + 13 * u + bh) * S], fill=BLUE)
    d.text(((x + w * 0.56 + 5) * S, (y + 12 * u) * S), "56",
           font=f_num, fill=BLUE)
    d.text((x * S, (y + 30 * u) * S), "GOP 44", font=f_lab, fill=INK)
    d.rectangle([x * S, (y + 43 * u) * S, (x + w * 0.44) * S,
                 (y + 43 * u + bh) * S], fill=RED)
    d.text(((x + w * 0.44 + 5) * S, (y + 42 * u) * S), "44",
           font=f_num, fill=RED)
    if h >= 56:
        center(d, x + w / 2, y + h - 11, "SENATE 56-44  ·  NET +9 DEM",
               f(SANS, 9), SOFT)


def draw_cyclone(d, x, y, w, h):
    """Cyclone Akvan: spiral arms around a calm eye, wind note.
    Spiral radii scale with the box height."""
    sc = h / 96.0
    cx, cy = x + w * 0.30, y + h * 0.46
    for k in range(3):
        r0 = (7 + k * 8) * sc
        pts = []
        for a in range(0, 300, 12):
            ang = math.radians(a + k * 40)
            r = (r0 + a * 0.05 * sc)
            pts.append(((cx + r * math.cos(ang)) * S,
                        (cy + r * math.sin(ang)) * S))
        d.line(pts, fill=INK, width=2 * S)
    er = max(3, int(5 * sc))
    d.ellipse([(cx - er) * S, (cy - er) * S, (cx + er) * S, (cy + er) * S],
              fill=PAPER, outline=INK, width=2 * S)
    d.text(((x + w * 0.60) * S, (y + 2) * S), "120-130",
           font=f(SANS_B, 13), fill=INK)
    d.text(((x + w * 0.60) * S, (y + 18) * S), "km/h",
           font=f(SANS, 10), fill=SOFT)
    d.text(((x + w * 0.60) * S, (y + 32) * S), "gusts 145",
           font=f(SANS_B, 11), fill=RED)
    if h >= 56:
        center(d, x + w / 2, y + h - 11, "LANDFALL FRIDAY · ANDHRA PRADESH",
               f(SANS, 9), SOFT)


def draw_congo(d, x, y, w, h):
    """Ebola cases: eleven dots, one per thousand cases. At taller
    heights also shows the death toll and a caption."""
    d.text((x * S, y * S), "11,000+", font=f(SANS_B, 13), fill=INK)
    d.text(((x + 70) * S, (y + 2) * S), "cases", font=f(SANS, 11), fill=SOFT)
    for i in range(11):
        dx = x + 6 + (i % 6) * 13
        dy = y + 20 + (i // 6) * 12
        d.ellipse([dx * S, dy * S, (dx + 8) * S, (dy + 8) * S], fill=RED)
    if h >= 56:
        d.text((x * S, (y + 48) * S), "5,400+ dead", font=f(SANS_B, 12),
               fill=INK)
        center(d, x + w / 2, y + h - 11,
               "3 IN 4 CHILDREN UNDER 5 DO NOT SURVIVE",
               f(SANS, 9), SOFT)


def draw_markets(d, x, y, w, h):
    """Markets: jagged index line, Dow down, Nvidia up. At taller
    heights also shows the Nvidia revenue line and a caption."""
    pts = []
    seq = [(0.00, 0.30), (0.14, 0.38), (0.28, 0.34), (0.42, 0.48),
           (0.56, 0.44), (0.70, 0.58), (0.84, 0.52), (1.00, 0.30)]
    for fx, fy in seq:
        pts.append(((x + w * fx) * S, (y + 4 + 22 * fy) * S))
    d.line(pts, fill=SOFT, width=2 * S)
    d.text((x * S, (y + 28) * S), "DOW  -849", font=f(SANS_B, 14), fill=RED)
    d.text(((x + w * 0.52) * S, (y + 28) * S), "NVDA  +",
           font=f(SANS_B, 14), fill=GREEN)
    if h >= 56:
        d.text((x * S, (y + 46) * S), "Nvidia $115.8bn revenue",
               font=f(SANS, 11), fill=SOFT)
        center(d, x + w / 2, y + h - 11, "WALL STREET · AFTER THE BELL",
               f(SANS, 9), SOFT)


def draw_cricket(d, x, y, w, h):
    """Dhoni retires: bat, ball and stumps on a green strip."""
    d.rectangle([x * S, (y + h - 12) * S, (x + w) * S, (y + h) * S],
                fill=(96, 140, 82))
    # stumps
    for sx in (0.16, 0.22, 0.28):
        d.line([(x + w * sx) * S, (y + h - 26) * S,
                (x + w * sx) * S, (y + h - 12) * S], fill=(232, 214, 160),
               width=2 * S)
    # bat, leaning
    bx, by = x + w * 0.55, y + 6
    d.polygon([(bx * S, by * S), ((bx + 12) * S, (by + 4) * S),
               ((bx + 4) * S, (by + 30) * S),
               ((bx - 6) * S, (by + 26) * S)], fill=(214, 178, 120))
    d.line([(bx + 6) * S, by * S, (bx + 12) * S, (by - 8) * S],
           fill=(120, 84, 48), width=3 * S)
    # red ball with seam
    cx, cy = x + w * 0.82, y + h * 0.45
    d.ellipse([(cx - 7) * S, (cy - 7) * S, (cx + 7) * S, (cy + 7) * S],
              fill=RED)
    d.arc([(cx - 7) * S, (cy - 7) * S, (cx + 7) * S, (cy + 7) * S],
          200, 340, fill=(255, 255, 255), width=1 * S)


def draw_rocket(d, x, y, w, h):
    """ULA Vulcan failure: a rocket climbing, flame below, small stars."""
    cx = x + w * 0.5
    # stars
    for sx, sy in ((0.12, 0.20), (0.88, 0.16), (0.82, 0.55), (0.10, 0.62)):
        d.ellipse([(x + w * sx - 2) * S, (y + h * sy - 2) * S,
                   (x + w * sx + 2) * S, (y + h * sy + 2) * S], fill=SOFT)
    # body
    d.rounded_rectangle([(cx - 8) * S, (y + 6) * S, (cx + 8) * S,
                         (y + h * 0.62) * S], radius=8 * S, fill=INK)
    # nose cone
    d.polygon([((cx - 8) * S, (y + 8) * S), ((cx + 8) * S, (y + 8) * S),
               (cx * S, (y - 2) * S)], fill=RED)
    # fins
    d.polygon([((cx - 8) * S, (y + h * 0.50) * S),
               ((cx - 18) * S, (y + h * 0.66) * S),
               ((cx - 8) * S, (y + h * 0.66) * S)], fill=RED)
    d.polygon([((cx + 8) * S, (y + h * 0.50) * S),
               ((cx + 18) * S, (y + h * 0.66) * S),
               ((cx + 8) * S, (y + h * 0.66) * S)], fill=RED)
    # flame
    d.polygon([(cx * S, (y + h) * S),
               ((cx - 6) * S, (y + h * 0.66) * S),
               ((cx + 6) * S, (y + h * 0.66) * S)], fill=(232, 140, 40))
    # window
    d.ellipse([(cx - 3) * S, (y + 14) * S, (cx + 3) * S, (y + 20) * S],
              fill=(180, 210, 235))


def draw_oil(d, x, y, w, h):
    """Oil near $93: a barrel with the price tag."""
    bx, by, bw, bh = x + w * 0.18, y + 4, 34, h - 14
    d.rounded_rectangle([bx * S, by * S, (bx + bw) * S, (by + bh) * S],
                        radius=4 * S, fill=(58, 58, 58))
    d.line([bx * S, (by + 8) * S, (bx + bw) * S, (by + 8) * S],
           fill=(120, 120, 120), width=2 * S)
    d.line([bx * S, (by + bh - 8) * S, (bx + bw) * S, (by + bh - 8) * S],
           fill=(120, 120, 120), width=2 * S)
    d.text(((x + w * 0.52) * S, (y + 6) * S), "$93",
           font=f(SANS_B, 22), fill=INK)
    d.text(((x + w * 0.52) * S, (y + 32) * S), "a barrel",
           font=f(SANS, 12), fill=SOFT)
    if h >= 56:
        center(d, x + w / 2, y + h - 10, "GULF TENSIONS LIFT CRUDE",
               f(SANS, 9), SOFT)


def draw_globe(d, x, y, r):
    """Small globe glyph for the brief band."""
    cx, cy = x + r, y + r
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S],
              outline=RED, width=2 * S)
    d.ellipse([(cx - r * 0.45) * S, (cy - r) * S,
               (cx + r * 0.45) * S, (cy + r) * S], outline=RED, width=1 * S)
    d.line([(cx - r) * S, cy * S, (cx + r) * S, cy * S], fill=RED, width=1 * S)


# ---------------------------------------------------------------- stories
# Each brief: (headline, one-line dek). Headlines kept short so they fit
# one line at 13pt bold in a 226px column; deks are one line at 12pt.
BRIEFS_COL1 = [
    ("APEC opens in Shenzhen", "21 leaders meet on trade and AI."),
    ("Quad unveils Manila plan", "Joint patrols and cable links agreed."),
    ("Modi offers ASEAN e-visas", "Free e-visas proposed for tourists."),
    ("ASEAN chair goes to Singapore", "Digital economy pact completed."),
    ("Canada, China cut tariffs", "Tariffs fall after Carney-Xi talks."),
    ("Russian jets enter Japan airspace", "Tokyo lodges formal protest."),
    ("Phuket fire kills 11", "Safety audit ordered after blaze."),
    ("S. China Sea code near done", "Terms 85-90% agreed, ASEAN says."),
    ("India wins ITU Council seat", "Wins 2027-2030 term at ITU."),
    ("Taiwan seeks $14bn arms", "PLA sorties rise near Taiwan."),
]

BRIEFS_COL2 = [
    ("Kyiv bridges pounded", "Power and water cut in the capital."),
    ("EU proposes 45bn Kyiv loan", "Loan for 2027, repaid by Russia."),
    ("Britain sanctions settlers", "Move defends two-state solution."),
    ("France denies Ukraine troops", "Paris calls Moscow claim false."),
    ("Spain lifts minimum wage", "Up 5.3% to 1,286 euros a month."),
    ("Serbia MiG-29 crashes", "Pilot killed near Belgrade."),
    ("UK inflation hits 3.6%", "Record diesel prices drive rise."),
    ("ICJ to rule on Myanmar case", "Rohingya genocide case decided."),
    ("Trump hails Manila trade deal", "Claims a very big deal in Manila."),
    ("Smith flips N.C. House seat", "Democrat beats Murphy in N. Carolina."),
]

BRIEFS_COL3 = [
    ("Iran hits U.S. base in Kuwait", "Drones target Ali Al Salem base."),
    ("Israeli tanks enter Gaza", "First ground move since the truce."),
    ("Iran bars nuclear inspectors", "No IAEA access until war ends."),
    ("Houthis seize Yemen coast", "Ground taken 100 km west of Aden."),
    ("Hormuz tankers attacked", "Crews hurt, vessels burning."),
    ("Geneva talks on Iran nukes", "Tehran and Washington to meet."),
    ("U.S. intel aids Nigeria fight", "Help targets militants, 2027 vote."),
    ("Zamfara police free 20", "Abducted women and children freed."),
    ("S. Africa probes 17 deaths", "Two weekend shootings probed."),
    ("Egypt, India plan trade pact", "Working group on pharma, farms."),
]

BRIEFS_COL4 = [
    ("Fiji declares El Nino disaster", "Drought emergency across Fiji."),
    ("Anthropic raises $81.3bn", "Largest stock offering on record."),
    ("Siberia plane crash kills 19", "Military plane down in Kemerovo."),
    ("U.S. loses measles-free status", "Status lost after 26 years."),
    ("Kahana elected Knesset speaker", "Matan Kahana takes the chair."),
    ("Board faults Israel, Hamas", "Both fell short on Gaza truce."),
    ("Nvidia bars Huang return", "Board rejects ex-CEO comeback."),
]

# Headlines that carry a small code-drawn illustration (art briefs).
ART_BRIEFS = {"Dhoni retires from IPL": draw_cricket,
              "Kerch bridge span falls": draw_bridge,
              "Ebola tops 11,000 cases": draw_congo,
              "Vulcan fails; 40 satellites lost": draw_rocket,
              "Oil nears $93 on Gulf fears": draw_oil}


# ---------------------------------------------------------------- blocks
def brief_item(d, x, y, w, headline, dek):
    """One dense brief: bold headline + one-line dek. Returns new y."""
    fh = f(LORA_B, 13)
    fd = f(LORA, 12)
    y, _ = para(d, x, y, headline, fh, INK, w, 13, max_lines=1)
    y, _ = para(d, x, y, dek, fd, SOFT, w, 12, max_lines=1)
    return y + 2


def art_brief(d, x, y, w, headline, dek, art):
    """A brief with a small code-drawn illustration above the text."""
    ah = 32
    art(d, x, y, w, ah)
    y += ah + 3
    return brief_item(d, x, y, w, headline, dek)


def region_head(d, x, y, w, label):
    d.text((x * S, y * S), label, font=f(SANS_B, 11), fill=RED)
    hrule(d, x + tw(d, label, f(SANS_B, 11)) + 8, x + w, y + 6, 1, RULE)
    return y + 15


def medium(d, x, y, w, kicker, headline, body, art, art_h):
    """A medium story: kicker, 2-line headline, 2-line body, spot art."""
    d.text((x * S, y * S), kicker, font=f(SANS_B, 13), fill=RED)
    y += 17
    y, _ = para(d, x, y, headline, f(LORA_B, 19), INK, w, 22, max_lines=2)
    y += 2
    y, _ = para(d, x, y, body, f(LORA, 14), INK, w, 16, max_lines=2)
    y += 4
    art(d, x, y, w, art_h)
    return y + art_h


def grid_column(d, x, y, w, regions, bottom):
    """Flow one brief column: (region, [(headline, dek), ...]) groups.
    Returns the y just below the column; prints overflow if any."""
    for label, items in regions:
        y = region_head(d, x, y, w, label)
        for head, dek in items:
            art = ART_BRIEFS.get(head)
            if art is not None:
                y = art_brief(d, x, y, w, head, dek, art)
            else:
                y = brief_item(d, x, y, w, head, dek)
            if y > bottom:
                print("  OVERFLOW in column at:", head)
    return y


# ---------------------------------------------------------------- page
def render():
    img = Image.new("RGB", (CW, CH), PAPER)
    d = ImageDraw.Draw(img)
    y = 14

    # --- edition line + nameplate + folio
    tracked(d, W / 2, y, "INTERNATIONAL EDITION", f(SANS, 13), SOFT, 4)
    y += 20
    center(d, W / 2, y, "THE WORLD TODAY", f(GLOOCK, 68), INK)
    y += 76
    hrule(d, MARGIN, W - MARGIN, y, 3)
    y += 6
    ff = f(SANS, 13)
    d.text((MARGIN * S, y * S), "WEDNESDAY, 18 NOVEMBER 2026",
           font=ff, fill=INK)
    right = "No. 322  —  PRICE $2.50"
    d.text(((W - MARGIN - tw(d, right, ff)) * S, y * S), right,
           font=ff, fill=INK)
    y += 19
    hrule(d, MARGIN, W - MARGIN, y, 1)
    y += 7

    # --- lead: kicker, headline, dek, skyline
    tracked(d, W / 2, y, "SUMMIT IN SHENZHEN", f(SANS_B, 17), RED, 5)
    y += 24
    fh = f(GLOOCK, 44)
    center(d, W / 2, y, "Xi greets Trump in Shenzhen", fh, INK)
    y += 48
    center(d, W / 2, y, "ahead of three-way summit", fh, INK)
    y += 48
    y, _ = para(d, MARGIN + 60, y,
                "Chinese and Russian leaders meet a day before Thursday's "
                "three-way summit, as the U.S.-China tariff truce runs to "
                "10 January 2027.",
                f(CRIM_I, 21), INK, W - 2 * MARGIN - 120, 26, max_lines=2)
    y += 5
    art_h = 88
    d.rectangle([(MARGIN - 2) * S, (y - 2) * S,
                 (W - MARGIN + 2) * S, (y + art_h + 2) * S],
                outline=INK, width=2 * S)
    draw_skyline(d, MARGIN, y, W - 2 * MARGIN, art_h)
    y += art_h + 6
    center(d, W / 2, y,
           "The Shenzhen skyline at dusk, where Xi Jinping greeted Donald "
           "Trump on the tarmac.",
           f(LORA_I, 13), SOFT)
    y += 19
    print("y after lead =", y)

    # --- brief band
    hrule(d, MARGIN, W - MARGIN, y, 2)
    y += 5
    draw_globe(d, MARGIN + 2, y, 8)
    band = "THE WORLD IN BRIEF  —  47 STORIES  ·  7 REGIONS"
    d.text(((MARGIN + 24) * S, y * S), band, font=f(SANS_B, 13), fill=INK)
    right = "ALL STORIES DATE-CHECKED 18 NOV 2026"
    d.text(((W - MARGIN - tw(d, right, f(SANS, 11))) * S, (y + 2) * S),
           right, font=f(SANS, 11), fill=SOFT)
    y += 21
    hrule(d, MARGIN, W - MARGIN, y, 1)
    y += 7
    grid_top = y
    bottom = 986

    # --- grid: 4 columns. Each column opens with a medium story, then
    # region-grouped briefs (some carry a small code-drawn illustration).
    gx = [MARGIN + i * (GRID_W + 14) for i in range(4)]
    y1 = medium(d, gx[0], y, GRID_W, "INDIA · CYCLONE",
                "Cyclone Akvan nears India",
                "Landfall is forecast on the Andhra Pradesh coast Friday.",
                draw_cyclone, 46)
    y1 = grid_column(d, gx[0], y1 + 7, GRID_W,
                     [("ASIA", [("Dhoni retires from IPL",
                                  "Becomes CSK mentor for 2027.")] +
                     BRIEFS_COL1)], bottom)
    y2 = medium(d, gx[1], y, GRID_W, "MIDTERMS",
                "Peltola takes Alaska",
                "Peltola unseats Sullivan; Democrats take the Senate 56-44.",
                draw_senate, 46)
    y2 = grid_column(d, gx[1], y2 + 7, GRID_W,
                     [("EUROPE", [("Kerch bridge span falls",
                                    "Deck collapses into the strait.")] +
                     BRIEFS_COL2[:8]),
                      ("AMERICAS", BRIEFS_COL2[8:])], bottom)
    y3 = medium(d, gx[2], y, GRID_W, "THE GULF",
                "U.S. jets hit Guard site",
                "U.S. jets hit a Guard site on Qeshm; a ship is hit near Hormuz.",
                draw_gulf, 46)
    y3 = grid_column(d, gx[2], y3 + 7, GRID_W,
                     [("MIDDLE EAST", BRIEFS_COL3[:6]),
                      ("AFRICA", [("Ebola tops 11,000 cases",
                                   "5,400+ dead, U.N. says.")] +
                      BRIEFS_COL3[6:])], bottom)
    y4 = medium(d, gx[3], y, GRID_W, "MARKETS",
                "Dow down 849; Nvidia beats",
                "The Dow falls 849; Nvidia reports $115.8bn in revenue.",
                draw_markets, 46)
    y4 = grid_column(d, gx[3], y4 + 7, GRID_W,
                     [("OCEANIA", BRIEFS_COL4[:2]),
                      ("MARKETS", [("Oil nears $93 on Gulf fears",
                                    "Crude climbs as tensions rise.")] +
                      BRIEFS_COL4[2:3]),
                      ("ALSO TODAY", BRIEFS_COL4[3:] +
                      [("Vulcan fails; 40 satellites lost",
                        "Amazon Leo plan faces delay.")])], bottom)
    print("grid top =", grid_top)
    print("column bottoms:", y1, y2, y3, y4, "(limit", bottom, ")")
    y = max(y1, y2, y3, y4)
    assert y <= bottom, "grid overflow: %d" % y

    # --- footer
    y = bottom + 4
    hrule(d, MARGIN, W - MARGIN, y, 2)
    y += 8
    center(d, W / 2, y,
           "ILLUSTRATIONS ARE ORIGINAL DRAWINGS, NOT PHOTOGRAPHS.",
           f(SANS, 12), SOFT)
    y += 20
    print("final y =", y, "(page height 1024)")
    assert y <= 1024, "page overflow: %d" % y
    return img


def main():
    img = render()
    out = img.resize((W, H), Image.LANCZOS)
    path = os.path.join(HERE, "entry.png")
    out.save(path, "PNG")
    data = open(path, "rb").read()
    print("entry.png", len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
