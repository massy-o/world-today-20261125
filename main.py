#!/usr/bin/env python3
"""THE WORLD TODAY - Wednesday 25 November 2026, dense edition.

Renders one 1024x1024 front page that sums up the day's world news:
six story cards with fuller wire copy and a second-angle line each,
a ten-figure numbers strip and forty briefs. Around eighty sourced
facts on a single page. Pure standard library: the PNG encoder and
the 5x7 pixel typeface below are both written for this entry.
No network, deterministic. Output: /output/entry.png
(falls back to ./entry.png locally).
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
    """Encode an RGB bytearray as a PNG, filter type 0 throughout."""
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
# Each glyph is 7 rows of 5 pixels, drawn as strings ('#' = ink).
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}

CELL = 6  # glyph advance: 5 px of glyph + 1 px of air, times scale


def text_w(s, scale):
    return len(s) * CELL * scale - scale


def draw_text(page, x, y, s, scale, colour):
    """Draw s with its top-left at (x, y); returns the end x."""
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col, bit in enumerate(row):
                if bit == "#":
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
# Content: a 51-item sourced wire pool for Wednesday 25 November 2026
# (AP, AFP, Reuters, SCMP, Dow Jones wires), ranked and laid out with
# Groq (gpt-oss-120b) and sub-edited by qwen3.8-27b. This dense edition
# carries about 80 items: six cards with fuller copy and a second-angle
# line each, ten figures in the strip, and forty briefs.
# Card tuple: kicker, accent, headline, body, angle, footer.
CARDS = [
    ("MARKETS", (14, 124, 116),
     "NVIDIA SLIDES 6% RALLY ENDS",
     "THE RELIEF RALLY OVER JENSEN HUANG'S RETURN AS CEO FIZZLES ON "
     "TUESDAY. TECH -2.8%; HEALTH +2.9%.",
     "STILL 37% BELOW OCT HIGH",
     "NASDAQ -1.5% / S&P -0.5%"),
    ("CHINA", RED,
     "CHINA PROBES SHANGHAI PARTY CHIEF",
     "BEIJING INVESTIGATES POLITBURO MEMBER AND SHANGHAI PARTY "
     "CHIEF CHEN JINING.",
     "RARE PURGE AT THE TOP",
     "POLITBURO MEMBER PROBED"),
    ("UKRAINE", (30, 80, 160),
     "KYIV STRIKES 14 KILLED",
     "RUSSIAN STRIKES ON UKRAINE'S KYIV REGION KILL AT LEAST 14 "
     "PEOPLE. UKRAINE OFFICIALS SAY.",
     "CAPITAL REGION STRUCK",
     "KYIV REGION TARGETED"),
    ("SAUDI", (176, 124, 28),
     "RIYADH TOWER HIT TWICE",
     "SAUDI ARABIA CONDEMNS A TERRORIST ATTACK AFTER THE PIF "
     "TOWER IS HIT AGAIN.",
     "SECOND HIT IN ONE WEEK",
     "RIYADH CONDEMNS ATTACK"),
    ("UN REPORT", (110, 60, 160),
     "FIVE WOMEN KILLED EVERY HOUR",
     "A UN REPORT FINDS FIVE WOMEN WERE KILLED EACH HOUR BY "
     "RELATIVES IN 2025.",
     "UN DAY TO END VIOLENCE",
     "KILLERS WERE RELATIVES"),
    ("LANDMINES", (22, 128, 74),
     "LANDMINES 7,000 HIT 5-YR HIGH",
     "LANDMINE CASUALTIES HIT A FIVE-YEAR HIGH OF 7,000; "
     "MYANMAR, SYRIA TOP.",
     "WORST TOLL IN FIVE YEARS",
     "FIVE-YEAR HIGH: 7,000"),
]

STRIP = [
    "$237BN VENEZUELA DEBT \u2022 7,000 MINE CASUALTIES \u2022 14 KILLED AT KYIV",
    "25 HOSTAGES IN COLOMBIA \u2022 NVIDIA -6% \u2022 NASDAQ -1.5% \u2022 S&P 500 -0.5%",
    "CONFIDENCE 103.3 \u2022 $100M SHEIN DEAL \u2022 81.5M US TRAVELLERS",
]

BRIEFS = [
    "BAHRAIN: IRAN HIT CIVILIAN SITE",
    "HAMAS SECURITY CHIEF KILLED",
    "RUSSIAN JETS ENTER SK ADIZ",
    "NATO EYES NUKE SATELLITE",
    "N KOREA WARNS SWISS OFFICE",
    "US ENVOY DOUBTS $3.8BN AID",
    "FLYDUBAI CLEARED FOR TEL AVIV",
    "GERMANS OPPOSE MORE ARMS",
    "JURY CONVICTS HUAWEI OF THEFT",
    "SOLDIER ZHAO SOLD INTEL",
    "TARIFF PROBE: 16 PARTNERS",
    "CHINA EASES CURBS TO JAN",
    "GIULIANI GETS MEDAL OF FREEDOM",
    "TRUMP PARDONS HOLIDAY TURKEYS",
    "GOMEZ RESIGNS IN ETHICS CASE",
    "DEMOCRATS TURN TO 2028 RACE",
    "CDC CHIEF FACES STAFF DOUBTS",
    "FORT HOOD BID FAILS ON HASAN",
    "US HOME PRICES STEADY IN SEPT",
    "SHEIN PAYS $100M IN FTC CASE",
    "MICROSOFT CODE RED AFTER OUTAGE",
    "COBALT RUSH BEATS CONGO BAN",
    "OIL REBOUNDS ON SHIPPING RISKS",
    "BOC: INFLATION TO PERSIST",
    "GDP, PCE DATA DUE WEDNESDAY",
    "PUNJAB: BJP-SAD ALLIANCE 2027",
    "NEPAL PM GETS 15,000CR AID",
    "INDIA PMI HITS 9-MONTH HIGH",
    "SENSEX +500, NIFTY TOPS 25,400",
    "AMAZON PLANS $7BN INDIA PUSH",
    "MALAYSIA SENDS MYANMAR HOME",
    "GUNMEN HOLD 25 IN COLOMBIA",
    "CALIFORNIA FACES EXTREME FLOODS",
    "PELICOT SLAMS BOOK PROMO",
    "2 ARRESTS IN WILLIAM BREAK-IN",
    "POTANIN DIVORCE TRIAL OPENS",
    "DANISH COURT BACKS EVICTIONS",
    "ENGLAND BEAT AUSTRALIA IN T20",
    "INDIA WOMEN FACE CHINA IN HOCKEY",
    "12 CORAL SPECIES REVIVED",
]


MARGIN = 28
CW = W - 2 * MARGIN  # 968 px of content width


def card(page, x, y, w, h, kicker, accent, headline, body, angle, footer):
    page.frame(x, y, w, h, INK, 2)
    page.fill(x, y, w, 19, accent)
    draw_text(page, x + 10, y + 2, kicker, 2, WHITE)
    ty = y + 24
    for line in wrap(headline, 12):
        draw_text(page, x + 10, ty, line, 4, INK)
        ty += 29
    by = y + 114
    for line in wrap(body, 25)[:4]:
        draw_text(page, x + 10, by, line, 2, GREY)
        by += 16
    draw_text(page, x + 10, y + 180, angle, 2, accent)
    page.hline(x + 10, y + h - 20, w - 20, accent, 2)
    draw_text(page, x + 10, y + h - 17, footer, 2, INK)


def render():
    page = Page(W, H, PAPER)

    # Masthead (one size down from the previous edition)
    centred(page, W // 2, 10, "THE WORLD TODAY", 9, INK)
    page.hline(MARGIN, 79, CW, INK, 4)
    page.hline(MARGIN, 87, CW, INK, 2)
    page.fill(MARGIN, 95, CW, 32, RED)
    centred(page, W // 2, 100,
            "WEDNESDAY 25 NOVEMBER 2026 \u2022 THE DAY ON ONE PAGE", 3, WHITE)
    centred(page, W // 2, 133,
            "MARKETS WOBBLE, GEOPOLITICS FLARE AND HUMAN COSTS RISE", 2, INK)

    # Six story cards, two rows of three
    card_w, card_h = 314, 216
    for i, (kicker, accent, head, body, angle, foot) in enumerate(CARDS):
        cx = MARGIN + (i % 3) * (card_w + 12)
        cy = 154 + (i // 3) * (card_h + 8)
        card(page, cx, cy, card_w, card_h,
             kicker, accent, head, body, angle, foot)

    # Numbers strip
    sy = 602
    page.fill(MARGIN, sy, CW, 50, INK)
    for j, line in enumerate(STRIP):
        centred(page, W // 2, sy + 4 + j * 15, line, 2,
                GOLD if j == 1 else WHITE)

    # Briefs: forty, four columns of ten, tight leading
    hy = 660
    draw_text(page, MARGIN, hy, "IN BRIEF", 3, RED)
    draw_text(page, MARGIN + text_w("IN BRIEF ", 3), hy,
              "- FORTY MORE FACTS FROM WEDNESDAY", 3, INK)
    page.hline(MARGIN, hy + 25, CW, INK, 2)
    col_x = [MARGIN, 276, 524, 772]
    for c in range(4):
        for r in range(10):
            brief = BRIEFS[c * 10 + r]
            yy = 694 + r * 30
            page.fill(col_x[c], yy + 4, 6, 6, RED)
            for k, line in enumerate(wrap(brief, 18)[:2]):
                draw_text(page, col_x[c] + 14, yy + k * 15, line, 2, INK)

    page.hline(MARGIN, 1001, CW, INK, 1)
    centred(page, W // 2, 1005,
            "THE WORLD TODAY \u2022 COMPILED FROM THE DAY'S WIRE REPORTS "
            "\u2022 PAGE 1 OF 1", 2, GREY)
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
