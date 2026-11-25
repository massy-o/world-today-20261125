#!/usr/bin/env python3
"""THE WORLD TODAY -- Wednesday 25 November 2026.

Renders a one-page newspaper front page (1024x1024 PNG) summing up the
day's world news: six story cards, a ten-figure numbers strip and a
thirty-item briefs column set.  Pure Python 3 standard library only:
the PNG encoder and the 5x7 pixel typeface below are both written for
this entry.  No network access.  Output is deterministic -- two runs
produce byte-identical files.

Writes /output/entry.png (falls back to ./entry.png if /output is not
writable).
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- PNG sink

def _chunk(tag, payload):
    body = tag + payload
    return (struct.pack(">I", len(payload)) + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))


def encode_png(rgb, w, h):
    """Encode an RGB bytearray as a PNG file (filter 0 rows, zlib)."""
    stride = w * 3
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ------------------------------------------------------------------- canvas

class Canvas:
    """A flat RGB framebuffer with rectangle fills."""

    def __init__(self, w, h, colour):
        self.w = w
        self.h = h
        self.px = bytearray(colour) * (w * h)

    def fill(self, x, y, rw, rh, colour):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + rw), min(self.h, y + rh)
        if x0 >= x1 or y0 >= y1:
            return
        row = bytes(colour) * (x1 - x0)
        n = len(row)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + n] = row

    def outline(self, x, y, rw, rh, colour, t=2):
        self.fill(x, y, rw, t, colour)
        self.fill(x, y + rh - t, rw, t, colour)
        self.fill(x, y, t, rh, colour)
        self.fill(x + rw - t, y, t, rh, colour)


# ------------------------------------------------------- 5x7 pixel typeface
# Every glyph is seven rows of five pixels, '#' for ink and '.' for blank.
# The set covers the characters used by the page copy below.

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
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
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
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
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
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"),
    "$": ("..#..", ".####", "#....", ".###.", "....#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "\u2022": (".....", ".....", ".##..", ".##..", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
}

ADV = 6  # glyph advance in font units: 5 px of glyph + 1 px of air


def text_width(s, scale):
    """Pixel width of a string at the given integer scale."""
    if not s:
        return 0
    return len(s) * ADV * scale - scale


def draw_text(cv, x, y, s, scale, colour):
    """Draw string s with its top-left corner at (x, y)."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for r, row in enumerate(glyph):
            for c, cell in enumerate(row):
                if cell == "#":
                    cv.fill(cx + c * scale, y + r * scale, scale, scale, colour)
        cx += ADV * scale
    return cx - scale


def draw_centered(cv, cx, y, s, scale, colour):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, colour)


def wrap(s, max_chars):
    """Greedy word wrap: split s into lines of at most max_chars."""
    lines, cur = [], ""
    for word in s.split(" "):
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


# ------------------------------------------------------------------- colours

PAPER = (243, 238, 226)
INK = (22, 24, 28)
RED = (178, 30, 38)
WHITE = (250, 250, 248)
GOLD = (232, 164, 52)
GREY = (74, 76, 82)

TEAL = (14, 122, 114)
CRIMSON = (185, 28, 28)
BLUE = (29, 78, 158)
OCHRE = (178, 124, 10)
PURPLE = (116, 48, 168)
GREEN = (30, 138, 76)

MX = 24            # page side margin
CW = W - 2 * MX    # content width, 976

# --------------------------------------------------------------------- copy
# All facts are drawn from the day's wire reports (AP, AFP, Reuters,
# SCMP, Dow Jones wires) for Wednesday 25 November 2026.

# (kicker, kicker colour, headline, body, footer)
CARDS = [
    ("MARKETS", TEAL,
     "NVIDIA SLIDES 6% RALLY ENDS",
     "NASDAQ -1.5%, S&P -0.5% AS RALLY OVER HUANG'S RETURN FIZZLES.",
     "37% BELOW OCTOBER HIGH"),
    ("CHINA", CRIMSON,
     "CHINA PROBES SHANGHAI PARTY CHIEF",
     "CHINA PROBES POLITBURO MEMBER AND SHANGHAI PARTY CHIEF CHEN JINING.",
     "POLITBURO MEMBER PROBED"),
    ("UKRAINE", BLUE,
     "KYIV STRIKES 14 KILLED",
     "RUSSIAN STRIKES ON UKRAINE'S KYIV REGION KILL AT LEAST 14 PEOPLE.",
     "KYIV REGION TARGETED"),
    ("SAUDI", OCHRE,
     "RIYADH TOWER HIT TWICE",
     "RIYADH CONDEMNS A TERROR ATTACK AFTER THE PIF TOWER IS HIT AGAIN.",
     "SECOND HIT IN A WEEK"),
    ("UN REPORT", PURPLE,
     "FIVE WOMEN KILLED EVERY HOUR",
     "A UN REPORT FINDS FIVE WOMEN KILLED EACH HOUR BY RELATIVES IN 2025.",
     "UN DAY TO END VIOLENCE"),
    ("LANDMINES", GREEN,
     "LANDMINES 7,000 HIT 5-YR HIGH",
     "LANDMINE CASUALTIES HIT A FIVE-YEAR HIGH OF 7,000 IN A YEAR.",
     "MYANMAR, SYRIA TOP LIST"),
]

# Ten figures of the day, three lines.
STRIP = [
    "$237BN VENEZUELA DEBT \u2022 7,000 MINE CASUALTIES \u2022 14 KILLED AT KYIV",
    "25 HOSTAGES IN COLOMBIA \u2022 NVIDIA -6% \u2022 NASDAQ -1.5% \u2022 S&P 500 -0.5%",
    "CONFIDENCE 103.3 \u2022 $100M SHEIN DEAL \u2022 81.5M US TRAVELLERS",
]

# Thirty briefs, laid out column by column (8 / 8 / 7 / 7).
BRIEF_COLS = [
    ["US JURY CONVICTS HUAWEI OF THEFT",
     "SOLDIER ZHAO SOLD INTEL TO CHINA",
     "US TARIFF PROBE: 16 PARTNERS",
     "CHINA EASES US CURBS TO JAN",
     "RUSSIAN JETS ENTER KOREA AIR ZONE",
     "NATO EYES NUCLEAR SATELLITE CLAIM",
     "NORTH KOREA WARNS SWISS OFFICE",
     "US ENVOY DOUBTS $3.8BN ISRAEL AID"],
    ["FLYDUBAI CLEARED FOR TEL AVIV",
     "GERMANS OPPOSE UKRAINE WEAPONS",
     "GIULIANI GETS MEDAL OF FREEDOM",
     "TRUMP PARDONS HOLIDAY TURKEYS",
     "GOMEZ RESIGNS IN ETHICS CASE",
     "DEMOCRATS TURN TO 2028 RACE",
     "CDC CHIEF FACES STAFF DOUBTS",
     "FORT HOOD BID FAILS ON HASAN"],
    ["US HOME PRICES STEADY IN SEPT",
     "OIL REBOUNDS ON SHIPPING RISKS",
     "MICROSOFT CODE RED AFTER OUTAGE",
     "COBALT RUSH BEATS CONGO BAN",
     "SHEIN PAYS $100M IN FTC CASE",
     "BAHRAIN: IRAN HIT CIVILIAN SITE",
     "HAMAS CHIEF KILLED IN GAZA"],
    ["PUNJAB: BJP-SAD ALLIANCE FOR 2027",
     "NEPAL PM WINS 15,000 CRORE AID",
     "INDIA FACTORY PMI 9-MONTH HIGH",
     "SENSEX +500, NIFTY TOPS 25,400",
     "CALIFORNIA FACES EXTREME FLOODS",
     "ENGLAND BEAT AUSTRALIA IN T20",
     "12 CORAL SPECIES REVIVED"],
]

# ------------------------------------------------------------------- layout

def draw_card(cv, x, y, w, h, kicker, colour, headline, body, footer):
    cv.outline(x, y, w, h, INK, 2)
    cv.fill(x, y, w, 24, colour)
    draw_text(cv, x + 10, y + 5, kicker, 2, WHITE)
    ty = y + 33
    for line in wrap(headline, 12):
        draw_text(cv, x + 11, ty, line, 4, INK)
        ty += 33
    by = y + 138
    for line in wrap(body, 24):
        draw_text(cv, x + 11, by, line, 2, GREY)
        by += 16
    cv.fill(x + 11, y + h - 22, w - 22, 2, colour)
    draw_text(cv, x + 11, y + h - 17, footer, 2, INK)


def render():
    cv = Canvas(W, H, PAPER)

    # Masthead and dateline bar
    draw_centered(cv, W // 2, 14, "THE WORLD TODAY", 9, INK)
    cv.fill(MX, 88, CW, 5, INK)
    cv.fill(MX, 97, CW, 2, INK)
    cv.fill(MX, 106, CW, 38, RED)
    draw_centered(cv, W // 2, 114,
                  "WEDNESDAY 25 NOVEMBER 2026 \u2022 THE DAY ON ONE PAGE",
                  3, WHITE)
    draw_centered(cv, W // 2, 152,
                  "MARKETS WOBBLE, GEOPOLITICS FLARE AND HUMAN COSTS RISE",
                  2, INK)
    cv.fill(MX, 172, CW, 2, INK)

    # Six story cards, two rows of three
    card_w, card_h = 317, 208
    xs = [MX, MX + card_w + 12, MX + 2 * (card_w + 12)]
    for i, (kicker, colour, head, body, foot) in enumerate(CARDS):
        cx = xs[i % 3]
        cy = 182 + (i // 3) * (card_h + 10)
        draw_card(cv, cx, cy, card_w, card_h, kicker, colour, head, body, foot)

    # Numbers strip
    sy = 620
    cv.fill(MX, sy, CW, 72, INK)
    for j, line in enumerate(STRIP):
        draw_centered(cv, W // 2, sy + 9 + j * 21, line, 2,
                      GOLD if j == 1 else WHITE)

    # Briefs header
    draw_text(cv, MX, 706, "IN BRIEF", 3, RED)
    draw_text(cv, MX + text_width("IN BRIEF ", 3), 706,
              "- THIRTY MORE FACTS FROM WEDNESDAY", 3, INK)
    cv.fill(MX, 736, CW, 2, INK)

    # Briefs in four columns
    col_x = [MX, 272, 520, 768]
    for c, briefs in enumerate(BRIEF_COLS):
        for r, brief in enumerate(briefs):
            yy = 748 + r * 30
            cv.fill(col_x[c], yy + 4, 6, 6, RED)
            for k, line in enumerate(wrap(brief, 18)):
                draw_text(cv, col_x[c] + 13, yy + k * 15, line, 2, INK)

    # Footer credit
    draw_centered(cv, W // 2, 996,
                  "THE WORLD TODAY \u2022 COMPILED FROM THE DAY'S WIRE REPORTS"
                  " \u2022 PAGE 1 OF 1",
                  2, GREY)
    return cv


def main():
    data = encode_png(render().px, W, H)
    try:
        os.makedirs("/output", exist_ok=True)
        path = "/output/entry.png"
    except OSError:
        path = os.path.join(os.getcwd(), "entry.png")
    try:
        with open(path, "wb") as fh:
            fh.write(data)
    except OSError:
        path = os.path.join(os.getcwd(), "entry.png")
        with open(path, "wb") as fh:
            fh.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
