#!/usr/bin/env python3
"""THE WORLD TODAY - Wednesday 25 November 2026.

Renders one 1024x1024 front page that sums up the day's world news:
six story cards, a ten-figure numbers strip and thirty briefs.
Pure standard library: the PNG encoder and the 5x7 pixel typeface
below are both written for this entry. No network, deterministic.
Output: /output/entry.png (falls back to ./entry.png locally).
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (242, 237, 227)
INK = (20, 24, 29)
RED = (179, 32, 44)
GOLD = (233, 164, 60)
GREY = (92, 96, 102)
WHITE = (250, 248, 243)


# ---------------------------------------------------------------- PNG sink
def png_bytes(rgb, w, h):
    """Encode an RGB bytearray as a PNG with no filtering fuss."""
    def chunk(tag, payload):
        body = tag + payload
        return (struct.pack(">I", len(payload)) + body
                + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    stride = w * 3
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


class Page:
    """A flat RGB canvas with block-fill helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def fill(self, x, y, rw, rh, colour):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + rw), min(self.h, y + rh)
        if x0 >= x1 or y0 >= y1:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + len(row)] = row

    def hline(self, x, y, rw, colour, thick=1):
        self.fill(x, y, rw, thick, colour)

    def frame(self, x, y, rw, rh, colour, thick=2):
        self.fill(x, y, rw, thick, colour)
        self.fill(x, y + rh - thick, rw, thick, colour)
        self.fill(x, y, thick, rh, colour)
        self.fill(x + rw - thick, y, thick, rh, colour)


# ------------------------------------------------- 5x7 pixel typeface ----
# Each glyph: 7 rows of 5 bits, bit 16 is the leftmost pixel.
FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (28, 18, 17, 17, 17, 18, 28),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 17, 25, 21, 19, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10),
    "X": (17, 10, 4, 4, 4, 10, 17),
    "Y": (17, 10, 4, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "-": (0, 0, 0, 31, 0, 0, 0),
    "'": (4, 4, 8, 0, 0, 0, 0),
    "$": (4, 15, 20, 14, 5, 30, 4),
    "%": (25, 26, 2, 4, 8, 11, 19),
    "+": (0, 4, 4, 31, 4, 4, 0),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 6, 4, 0, 4),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "\u2022": (0, 0, 12, 12, 0, 0, 0),
}

CELL = 6  # glyph advance is 6 units: 5 px of glyph + 1 px of air


def text_w(s, scale):
    return len(s) * CELL * scale - scale


def draw_text(page, x, y, s, scale, colour):
    """Draw s with its top-left at (x, y); returns the end x."""
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row_i, bits in enumerate(glyph):
            for col in range(5):
                if bits & (16 >> col):
                    page.fill(cx + col * scale, y + row_i * scale,
                              scale, scale, colour)
        cx += CELL * scale
    return cx - scale


def centred(page, cx, y, s, scale, colour):
    draw_text(page, cx - text_w(s, scale) // 2, y, s, scale, colour)


def wrap(s, max_chars):
    """Greedy word wrap to lines of at most max_chars characters."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------- the news ----
# Content plan: 51 sourced wire items for Wednesday 25 November 2026 were
# ranked and laid out with Groq (gpt-oss-120b), then sub-edited by
# qwen3.8-27b. Six stories carry the page; ten figures run in the strip;
# thirty more facts close it. 58 items in all.
CARDS = [
    ("MARKETS", (15, 118, 110),
     "NVIDIA SLIDES 6% RALLY ENDS",
     "NEW YORK - THE RELIEF RALLY OVER JENSEN HUANG'S RETURN FIZZLES.",
     "NASDAQ -1.5% / S&P -0.5%"),
    ("CHINA", RED,
     "CHINA PROBES SHANGHAI PARTY CHIEF",
     "CHINA PROBES POLITBURO MEMBER AND SHANGHAI CHIEF CHEN JINING.",
     "POLITBURO MEMBER PROBED"),
    ("UKRAINE", (30, 80, 160),
     "KYIV STRIKES 14 KILLED",
     "KYIV - RUSSIAN STRIKES ON THE KYIV REGION KILL AT LEAST 14 PEOPLE.",
     "KYIV REGION TARGETED"),
    ("SAUDI", (176, 124, 28),
     "RIYADH TOWER HIT TWICE",
     "RIYADH CONDEMNS A TERROR ATTACK AFTER THE PIF TOWER IS HIT AGAIN.",
     "SECOND HIT IN A WEEK"),
    ("UN REPORT", (110, 60, 160),
     "FIVE WOMEN KILLED EVERY HOUR",
     "A UN REPORT FINDS FIVE WOMEN KILLED EACH HOUR BY RELATIVES IN 2025.",
     "UN DAY TO END VIOLENCE"),
    ("LANDMINES", (22, 128, 74),
     "LANDMINES 7,000 HIT 5-YR HIGH",
     "LANDMINE CASUALTIES HIT A FIVE-YEAR HIGH OF 7,000 IN A YEAR.",
     "MYANMAR, SYRIA TOP LIST"),
]

STRIP = [
    "$237BN VENEZUELA DEBT \u2022 7,000 MINE CASUALTIES \u2022 14 KILLED AT KYIV",
    "25 HOSTAGES IN COLOMBIA \u2022 NVIDIA -6% \u2022 NASDAQ -1.5% \u2022 S&P 500 -0.5%",
    "CONFIDENCE 103.3 \u2022 $100M SHEIN DEAL \u2022 81.5M US TRAVELLERS",
]

BRIEFS = [
    "US JURY CONVICTS HUAWEI OF THEFT",
    "SOLDIER ZHAO SOLD INTEL TO CHINA",
    "US TARIFF PROBE: 16 PARTNERS",
    "CHINA EASES US CURBS TO JAN",
    "RUSSIAN JETS ENTER KOREA AIR ZONE",
    "NATO EYES NUCLEAR SATELLITE CLAIM",
    "NORTH KOREA WARNS SWISS OFFICE",
    "US ENVOY DOUBTS $3.8BN ISRAEL AID",
    "FLYDUBAI CLEARED FOR TEL AVIV",
    "GERMANS OPPOSE UKRAINE WEAPONS",
    "GIULIANI GETS MEDAL OF FREEDOM",
    "TRUMP PARDONS HOLIDAY TURKEYS",
    "GOMEZ RESIGNS IN ETHICS CASE",
    "DEMOCRATS TURN TO 2028 RACE",
    "CDC CHIEF FACES STAFF DOUBTS",
    "FORT HOOD BID FAILS ON HASAN",
    "US HOME PRICES STEADY IN SEPT",
    "OIL REBOUNDS ON SHIPPING RISKS",
    "MICROSOFT CODE RED AFTER OUTAGE",
    "COBALT RUSH BEATS CONGO BAN",
    "SHEIN PAYS $100M IN FTC CASE",
    "BAHRAIN: IRAN HIT CIVILIAN SITE",
    "HAMAS CHIEF KILLED IN GAZA",
    "PUNJAB: BJP-SAD ALLIANCE FOR 2027",
    "NEPAL PM WINS 15,000 CRORE AID",
    "INDIA FACTORY PMI 9-MONTH HIGH",
    "SENSEX +500, NIFTY TOPS 25,400",
    "CALIFORNIA FACES EXTREME FLOODS",
    "ENGLAND BEAT AUSTRALIA IN T20",
    "12 CORAL SPECIES REVIVED",
]

MARGIN = 28
CW = W - 2 * MARGIN  # 968 px of content width


def card(page, x, y, w, h, kicker, colour, headline, body, footer):
    page.frame(x, y, w, h, INK, 2)
    page.fill(x, y, w, 24, colour)
    draw_text(page, x + 10, y + 5, kicker, 2, WHITE)
    ty = y + 34
    for line in wrap(headline, 12):
        draw_text(page, x + 10, ty, line, 4, INK)
        ty += 33
    by = y + 138
    for line in wrap(body, 24)[:3]:
        draw_text(page, x + 10, by, line, 2, GREY)
        by += 17
    page.hline(x + 10, y + h - 24, w - 20, colour, 2)
    draw_text(page, x + 10, y + h - 18, footer, 2, INK)


def render():
    page = Page(W, H, PAPER)

    # Masthead
    centred(page, W // 2, 14, "THE WORLD TODAY", 9, INK)
    page.hline(MARGIN, 86, CW, INK, 4)
    page.hline(MARGIN, 94, CW, INK, 1)
    page.fill(MARGIN, 102, CW, 32, RED)
    centred(page, W // 2, 107, "WEDNESDAY 25 NOVEMBER 2026 \u2022 THE DAY ON ONE PAGE",
            3, WHITE)
    centred(page, W // 2, 142,
            "MARKETS WOBBLE, GEOPOLITICS FLARE AND HUMAN COSTS RISE", 2, INK)
    page.hline(MARGIN, 162, CW, INK, 1)

    # Six story cards, two rows of three
    card_w, card_h, gap = 314, 216, 12
    for i, (kicker, colour, head, body, foot) in enumerate(CARDS):
        cx = MARGIN + (i % 3) * (card_w + gap)
        cy = 170 + (i // 3) * (card_h + 10)
        card(page, cx, cy, card_w, card_h, kicker, colour, head, body, foot)

    # Numbers strip
    sy = 624
    page.fill(MARGIN, sy, CW, 80, INK)
    for j, line in enumerate(STRIP):
        centred(page, W // 2, sy + 8 + j * 24, line, 2,
                GOLD if j == 1 else WHITE)

    # Briefs
    by0 = 712
    draw_text(page, MARGIN, by0, "IN BRIEF", 3, RED)
    draw_text(page, MARGIN + text_w("IN BRIEF ", 3), by0,
              "- THIRTY MORE FACTS FROM WEDNESDAY", 3, INK)
    page.hline(MARGIN, by0 + 26, CW, INK, 2)
    col_x = [MARGIN, 274, 520, 766]
    per_col = [8, 8, 7, 7]
    idx = 0
    for c, count in enumerate(per_col):
        for r in range(count):
            yy = 748 + r * 30
            page.fill(col_x[c], yy + 4, 6, 6, RED)
            lines = wrap(BRIEFS[idx], 18)
            for k, line in enumerate(lines[:2]):
                draw_text(page, col_x[c] + 12, yy + k * 15, line, 2, INK)
            idx += 1
    centred(page, W // 2, 994,
            "THE WORLD TODAY \u2022 COMPILED FROM THE DAY'S WIRE REPORTS \u2022 PAGE 1 OF 1",
            2, GREY)
    page.hline(MARGIN, 1014, CW, INK, 1)
    return page


def main():
    data = png_bytes(render().px, W, H)
    try:
        os.makedirs("/output", exist_ok=True)
        path = "/output/entry.png"
        with open(path, "wb") as fh:
            fh.write(data)
    except OSError:
        path = os.path.join(os.getcwd(), "entry.png")
        with open(path, "wb") as fh:
            fh.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
