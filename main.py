#!/usr/bin/env python3
"""
THE WORLD TODAY - Wednesday 25 November 2026 on one page.

A self-contained front-page renderer for the make.fun news-image-20261125
entry. Pure Python 3 standard library: the PNG encoder, the 5x7 pixel
typeface, the dotted world map, the drawn card art and the whole layout
are all implemented in this file. No network, no third-party code, and
the output is deterministic (same bytes on every run).

Layout, top to bottom:
  masthead / date bar / deck
  world map panel with story pins + dateline sweep strip
  six story cards, each with drawn art, a source tag, body and angle line
  the day in numbers (ten figures)
  in brief, grouped by region
  footer
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
PAPER = (233, 226, 205)      # warm newsprint
PAPER_DARK = (219, 210, 182)  # shaded paper for art strips
INK = (32, 30, 27)           # near-black ink
FAINT = (96, 90, 78)         # grey-brown for secondary text
RED = (176, 32, 42)          # masthead bar red
WHITE = (245, 242, 232)
WATER = (203, 214, 222)      # map water tint
LAND = (54, 68, 86)          # map dot slate
PIN = (196, 30, 40)          # map pin red
DARK = (24, 23, 26)          # numbers strip background
GOLD = (216, 164, 60)
TEAL = (0, 108, 98)
BLUE = (30, 70, 158)
BROWN = (168, 118, 18)
PURPLE = (108, 48, 148)
GREEN = (28, 124, 66)


# ---------------------------------------------------------------------------
# Minimal PNG writer (encoder written for this project)
# ---------------------------------------------------------------------------
def _png_chunk(tag, payload):
    chunk = struct.pack(">I", len(payload)) + tag + payload
    chunk += struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
    return chunk


def encode_png(width, height, rgb):
    """rgb: bytearray of width*height*3. Returns the PNG file bytes."""
    stride = width * 3
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0 (None) on every scanline
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _png_chunk(b"IHDR", ihdr)
            + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _png_chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# Canvas: a flat RGB buffer plus rectangle / line / circle helpers
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def frame(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line, stamped with a t x t brush."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set_px(xx, yy, color)

    def save(self, path):
        with open(path, "wb") as fh:
            fh.write(encode_png(self.w, self.h, self.px))


# ---------------------------------------------------------------------------
# 5x7 pixel typeface, drawn by hand for this project.
# Each glyph is 7 rows of 5 pixels; '#' is ink, '.' is empty.
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
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
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.###"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "*": (".....", ".....", "..#..", ".###.", "..#..", ".....", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
}

CELL_W = 6   # 5 px glyph + 1 px gap, in font units
CELL_H = 7   # glyph height in font units


def text_w(s, scale):
    """Pixel width of a string at the given integer scale."""
    if not s:
        return 0
    return len(s) * CELL_W * scale - scale


def draw_text(cv, x, y, s, scale, color):
    """Draw string s with its top-left at (x, y). Returns the end x."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == "#":
                    cv.rect(cx + col_i * scale, y + row_i * scale,
                            scale, scale, color)
        cx += CELL_W * scale
    return cx


def draw_centered(cv, cx, y, s, scale, color):
    return draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def draw_right(cv, rx, y, s, scale, color):
    return draw_text(cv, rx - text_w(s, scale), y, s, scale, color)


def wrap_text(s, max_chars):
    """Greedy word wrap to lines of at most max_chars characters."""
    lines = []
    cur = ""
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


# ---------------------------------------------------------------------------
# Dotted world map. The landmass grid below is typed by hand as string
# rows: 24 rows x 100 columns, '#' is land, '.' is water. It is a coarse
# equirectangular sketch (longitude -180..180, latitude +78..-58).
# Each row is written as ten 10-character groups so the columns can be
# counted in tens while authoring.
# ---------------------------------------------------------------------------
MAP_ROWS = [
    # cols 0-9    10-19       20-29       30-39       40-49       50-59       60-69       70-79       80-89       90-99
    ".........." "#####....." "#####....." "........##" "######...." ".........." "..#######." "...#######" "....######" "#...######",
    "..#######." "..########" "##########" "#......###" "#####....." "...#####.." "##########" "##########" "##########" "##########",
    "...#######" "...#######" "##########" "####....##" "####..##.." "..#######." "##########" "##########" "##########" "##########",
    "....######" ".....#####" "##########" "######...." "###......#" "#..#######" "##########" "##########" "##########" "########..",
    ".....###.." "......####" "##########" "#######..." "........##" "##########" "##########" "##########" "##########" "#######...",
    ".........." ".......###" "##########" "######...." ".......###" "##########" "..#...####" "##########" "##########" "####......",
    ".........." "........##" "##########" "####......" "........##" "##########" "..#..#####" "##########" "##########" "##........",
    ".........." ".......###" "##########" "###......." "......####" "##########" "##########" "##########" "######...#" "#.........",
    ".........." "........##" "##########" "#........." ".....#####" "##########" "##########" "##########" "########.." "..........",
    ".........." ".........#" "########.." ".........." ".....#####" "##########" "######...#" "##########" "....##...." "..........",
    ".........." ".........." "#######..." ".........." "......####" "##########" "##........" "####..####" ".........." "..........",
    ".........." ".........." "..####...." ".........." ".......###" "##########" "#........." "###...####" ".........." "..........",
    ".........." ".........." "........##" "#######..." "........##" "##########" ".........." "....###.##" "##........" "..........",
    ".........." ".........." ".........#" "#########." ".........#" "#########." ".........." "...#######" "######...." "..........",
    ".........." ".........." ".........#" "##########" ".........." "########.." ".........." "....######" "#######..." "..........",
    ".........." ".........." ".........." "##########" ".........." "########.." ".........." "......####" "##########" "#.........",
    ".........." ".........." ".........." "#########." ".........." ".######..." ".........." ".........." ".#########" "##........",
    ".........." ".........." ".........." ".########." ".........." ".######..." "##........" ".........." ".#########" "###.......",
    ".........." ".........." ".........." ".#######.." ".........." ".#####...." "##........" ".........." "..########" "###.......",
    ".........." ".........." ".........." ".######..." ".........." "..###....." ".........." ".........." "...#######" "##........",
    ".........." ".........." ".........." ".#####...." ".........." ".........." ".........." ".........." "....######" "......###.",
    ".........." ".........." ".........." ".####....." ".........." ".........." ".........." ".........." ".........." ".....###..",
    ".........." ".........." ".........." ".###......" ".........." ".........." ".........." ".........." ".........." "..........",
    ".........." ".........." ".........." ".##......." ".........." ".........." ".........." ".........." ".........." "..........",
]

MAP_X0 = 30          # left edge of the map area inside the panel
MAP_Y0 = 153         # top edge of the map area
MAP_W = 964          # map area width in px
MAP_H = 96           # map area height in px
MAP_COLS = 100
MAP_NROWS = 24


def _map_xy(lon, lat):
    """Project longitude/latitude to a pixel point on the map."""
    x = MAP_X0 + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y0 + (78.0 - lat) / 136.0 * MAP_H
    return int(x), int(y)


# Story pins: (label, longitude, latitude, label side)
PINS = [
    ("NEW YORK", -74.0, 40.7, "L"),
    ("BOGOTA", -74.1, 4.6, "R"),
    ("LONDON", -0.1, 51.5, "L"),
    ("KYIV", 30.5, 50.4, "R"),
    ("GAZA", 34.3, 31.5, "B"),
    ("RIYADH", 46.7, 24.6, "R"),
    ("DELHI", 77.2, 28.6, "B"),
    ("MYANMAR", 95.8, 21.9, "R"),
    ("BEIJING", 116.4, 39.9, "L"),
    ("SEOUL", 127.0, 37.6, "R"),
]

# Dateline sweep: the day's story cities ordered west to east.
DATELINE = "BOGOTA * NEW YORK * LONDON * KYIV * GAZA * RIYADH * DELHI * BEIJING * SEOUL"


def draw_map(cv):
    """Fill the water, stamp the land dots, then plot pins and labels."""
    cv.rect(MAP_X0 - 6, MAP_Y0 - 2, MAP_W + 12, MAP_H + 4, WATER)
    cell_w = MAP_W / MAP_COLS
    cell_h = MAP_H / MAP_NROWS
    for r, row in enumerate(MAP_ROWS):
        for c, bit in enumerate(row[:MAP_COLS]):
            if bit == "#":
                dx = int(MAP_X0 + c * cell_w + cell_w / 2)
                dy = int(MAP_Y0 + r * cell_h + cell_h / 2)
                cv.rect(dx - 2, dy - 1, 5, 3, LAND)
    for label, lon, lat, side in PINS:
        px, py = _map_xy(lon, lat)
        cv.circle(px, py, 5, PIN)
        cv.circle(px, py, 2, WHITE)
        lw = text_w(label, 1)
        if side == "L":
            lx = px - 9 - lw
            ly = py - 3
        elif side == "B":
            lx = px - lw // 2
            ly = py + 8
        else:
            lx = px + 9
            ly = py - 3
        # paper-water halo so the label never fights the dots
        cv.rect(lx - 2, ly - 1, lw + 4, 9, WATER)
        draw_text(cv, lx, ly, label, 1, INK)


# ---------------------------------------------------------------------------
# Drawn card art: small flat silhouette scenes, drawn with the canvas
# primitives above. Each motif fills a 19 px tall strip inside its card.
# ---------------------------------------------------------------------------
def art_chart(cv, x, y, w, h, c):
    """A rally that rolls over: jagged line rising, then sliding."""
    base = y + h - 3
    cv.rect(x + 6, base, w - 12, 1, c)
    pts = [(0.03, 0.50), (0.18, 0.22), (0.33, 0.38), (0.48, 0.24),
           (0.63, 0.52), (0.78, 0.70), (0.93, 0.86), (0.99, 0.94)]
    pp = [(int(x + fx * w), int(y + fy * (h - 4))) for fx, fy in pts]
    for (x1, y1), (x2, y2) in zip(pp, pp[1:]):
        cv.line(x1, y1, x2, y2, c, 2)
    cv.circle(pp[-1][0], pp[-1][1], 3, RED)


def art_building(cv, x, y, w, h, c):
    """A state hall: pitched roof, beam, columns, side wings."""
    cx = x + w // 2
    base = y + h - 2
    cv.line(cx - 40, y + 5, cx, y + 1, c, 2)
    cv.line(cx, y + 1, cx + 40, y + 5, c, 2)
    cv.rect(cx - 40, y + 6, 81, 3, c)
    for i in range(-3, 4):
        cv.rect(cx + i * 11 - 2, y + 10, 4, base - (y + 10), c)
    cv.rect(cx - 44, base - 1, 89, 2, c)
    cv.rect(x + 14, base - 6, 34, 6, c)
    cv.rect(x + w - 48, base - 6, 34, 6, c)


def art_domes(cv, x, y, w, h, c):
    """A domed skyline: towers of varied height, each capped by a dome."""
    base = y + h - 2
    cv.rect(x + 4, base, w - 8, 2, c)
    for fx, th in [(0.10, 7), (0.30, 10), (0.52, 8), (0.74, 11), (0.90, 6)]:
        tx = int(x + fx * w)
        cv.rect(tx - 4, base - th, 8, th, c)
        cv.circle(tx, base - th - 1, 3, c)


def art_tower(cv, x, y, w, h, c):
    """A landmark tower with an arch cut out, flanked by low blocks."""
    cx = x + w // 2
    base = y + h - 2
    cv.rect(x + 6, base, w - 12, 2, c)
    cv.rect(cx - 70, base - 6, 30, 6, c)
    cv.rect(cx + 40, base - 8, 30, 8, c)
    cv.rect(cx - 9, base - 10, 18, 10, c)
    cv.rect(cx - 6, base - 14, 12, 4, c)
    cv.rect(cx - 2, base - 17, 4, 3, c)
    cv.rect(cx - 3, base - 9, 6, 5, PAPER_DARK)
    cv.circle(cx, base - 9, 3, PAPER_DARK)


def art_candles(cv, x, y, w, h, c):
    """Five candles for the five women killed each hour."""
    base = y + h - 2
    cv.rect(x + 8, base, w - 16, 2, c)
    for i, ch in enumerate([7, 10, 8, 11, 6]):
        cxp = int(x + (0.14 + 0.18 * i) * w)
        cv.rect(cxp - 2, base - ch, 5, ch, c)
        cv.circle(cxp, base - ch - 3, 2, RED)


def art_warning(cv, x, y, w, h, c):
    """A warning triangle over a mined field."""
    base = y + h - 2
    cv.rect(x + 6, base, w - 12, 2, c)
    cv.line(x + 40, y + 1, x + 24, base - 2, c, 2)
    cv.line(x + 40, y + 1, x + 56, base - 2, c, 2)
    cv.line(x + 24, base - 2, x + 56, base - 2, c, 2)
    cv.rect(x + 39, y + 8, 2, 5, c)
    cv.rect(x + 39, y + 14, 2, 2, c)
    for fx in (0.45, 0.60, 0.75, 0.88):
        mx = int(x + fx * w)
        cv.rect(mx - 3, base - 4, 7, 2, c)
        cv.rect(mx - 1, base - 6, 3, 2, c)


ARTS = {
    "chart": art_chart,
    "building": art_building,
    "domes": art_domes,
    "tower": art_tower,
    "candles": art_candles,
    "warning": art_warning,
}

# ---------------------------------------------------------------------------
# Content. Every fact below comes from the day's candidate pool
# (AP / AFP / Reuters / SCMP / Dow Jones wire reports of 24-25 Nov 2026).
# ---------------------------------------------------------------------------
CARDS = [
    # category, source tag, accent, art, headline lines, body, angle line
    ("MARKETS", "REUTERS", TEAL, "chart",
     ("NVIDIA SLIDES 6%,", "RALLY FIZZLES"),
     "RALLY OVER HUANG RETURN DIES. NASDAQ -1.5%.",
     "STILL 37% BELOW OCT HIGH"),
    ("CHINA", "AP", RED, "building",
     ("CHINA PROBES", "SHANGHAI CHIEF"),
     "BEIJING PROBES POLITBURO MEMBER CHEN JINING.",
     "RARE PURGE AT THE TOP"),
    ("UKRAINE", "UKR OFFICIALS", BLUE, "domes",
     ("KYIV STRIKES", "KILL 14"),
     "RUSSIAN STRIKES HIT KYIV REGION, KILL 14.",
     "CAPITAL REGION TARGETED"),
    ("SAUDI", "SCMP", BROWN, "tower",
     ("RIYADH TOWER", "HIT TWICE"),
     "SAUDI CONDEMNS TERROR ATTACK ON THE PIF TOWER.",
     "SECOND HIT IN ONE WEEK"),
    ("UN REPORT", "UN", PURPLE, "candles",
     ("FIVE WOMEN", "KILLED HOURLY"),
     "FIVE WOMEN KILLED EACH HOUR BY KIN, UN FINDS.",
     "25 NOV: ANTI-VIOLENCE DAY"),
    ("LANDMINES", "GLOBAL REPORT", GREEN, "warning",
     ("LANDMINES HIT", "5-YEAR HIGH"),
     "CASUALTIES REACH 7,000; MYANMAR, SYRIA TOP LIST.",
     "WORST TOLL IN FIVE YEARS"),
]

# The day in numbers: (figure, caption lines, colour)
NUMBERS = [
    ("$237BN", ("VENEZUELA DEBT",), GOLD),
    ("7,000", ("MINE CASUALTIES",), WHITE),
    ("14", ("KILLED AT KYIV",), (238, 120, 120)),
    ("25", ("HOSTAGES IN", "COLOMBIA"), WHITE),
    ("-6%", ("NVIDIA",), GOLD),
    ("-1.5%", ("NASDAQ",), WHITE),
    ("-0.5%", ("S&P 500",), GOLD),
    ("103.3", ("CONFIDENCE",), WHITE),
    ("$100M", ("SHEIN DEAL",), GOLD),
    ("81.5M", ("US TRAVELLERS",), WHITE),
]

# In brief, grouped by region. Columns render top to bottom; the last
# column carries two region blocks (Middle East & Africa, then World).
BRIEF_COLUMNS = [
    [("EUROPE", TEAL, [
        "NATO ANSWERS NUKE-SAT REPORTS",
        "GERMANS OPPOSE MORE UKRAINE ARMS",
        "GERMAN BUSINESS MOOD RISES - IFO",
        "PELICOT SLAMS PUBLISHER PROMO",
        "2 HELD IN WILLIAM HOME BREAK-IN",
        "POTANIN IN UK DIVORCE TRIAL",
        "DANISH COURT BACKS EVICTIONS",
        "ENGLAND LEVEL T20 VS AUSTRALIA",
    ])],
    [("ASIA-PACIFIC", RED, [
        "RUSSIAN JETS ENTER SK ADIZ",
        "N KOREA MAY SHUT SWISS OFFICE",
        "CHINA EASES US CURBS TO JAN",
        "PUNJAB: BJP-SAD ALLIANCE 2027",
        "NEPAL PM GETS 15,000CR AID",
        "INDIA PMI HITS 9-MONTH HIGH",
        "SENSEX +500, NIFTY TOPS 25,400",
        "AMAZON PLANS $7BN INDIA PUSH",
        "MALAYSIA SENDS MYANMAR HOME",
        "INDIA WOMEN FACE CHINA HOCKEY",
    ])],
    [("AMERICAS", BLUE, [
        "JURY CONVICTS HUAWEI OF THEFT",
        "SOLDIER ZHAO SOLD INTEL",
        "TARIFF PROBE: 16 PARTNERS",
        "GIULIANI GETS MEDAL OF FREEDOM",
        "TRUMP PARDONS HOLIDAY TURKEYS",
        "GOMEZ RESIGNS IN ETHICS CASE",
        "DEMOCRATS EYE 2028 RACE",
        "FORT HOOD BID FAILS ON HASAN",
        "GUNMEN HOLD 25 IN COLOMBIA",
        "CALIFORNIA FACES EXTREME FLOODS",
    ])],
    [("MIDDLE EAST + AFRICA", BROWN, [
        "BAHRAIN: IRAN HIT CIVILIAN SITE",
        "HAMAS SECURITY CHIEF KILLED",
        "US ENVOY DOUBTS $3.8BN AID",
        "FLYDUBAI CLEARED FOR TEL AVIV",
        "COBALT RUSH BEATS CONGO BAN",
        "OIL REBOUNDS ON SHIPPING RISKS",
    ]),
     ("WORLD", PURPLE, [
        "12 CORAL SPECIES REVIVED",
        "RARE ASTEROID ECLIPSE CAUGHT",
    ])],
]


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------
def draw_card(cv, x, y, card):
    cat, src, accent, art, headline, body, angle = card
    w, h = 325, 148
    cv.frame(x, y, w, h, INK, 2)
    cv.rect(x, y, w, 20, accent)
    draw_text(cv, x + 8, y + 3, cat, 2, WHITE)
    draw_right(cv, x + w - 8, y + 3, src, 2, WHITE)
    cv.rect(x + 2, y + 21, w - 4, 19, PAPER_DARK)
    ARTS[art](cv, x + 2, y + 21, w - 4, 19, accent)
    draw_text(cv, x + 8, y + 45, headline[0], 3, INK)
    draw_text(cv, x + 8, y + 68, headline[1], 3, INK)
    for i, ln in enumerate(wrap_text(body, 25)):
        draw_text(cv, x + 8, y + 94 + i * 15, ln, 2, INK)
    cv.rect(x + 8, y + 128, w - 16, 1, accent)
    draw_text(cv, x + 8, y + 132, angle, 2, accent)


def draw_page(cv):
    # Masthead
    draw_centered(cv, 512, 8, "THE WORLD TODAY", 7, INK)
    cv.rect(16, 62, 992, 3, INK)
    cv.rect(16, 68, 992, 1, INK)
    # Date bar
    cv.rect(16, 72, 992, 26, RED)
    draw_centered(cv, 512, 74, "WEDNESDAY 25 NOVEMBER 2026 - THE DAY ON ONE PAGE",
                  3, WHITE)
    # Deck
    draw_centered(cv, 512, 104,
                  "MARKETS WOBBLE, GEOPOLITICS FLARE AND HUMAN COSTS RISE",
                  2, FAINT)
    # Map panel
    cv.frame(16, 124, 992, 152, INK, 2)
    draw_text(cv, 28, 132, "THE DAY ON THE MAP", 2, RED)
    draw_right(cv, 996, 132, "DATELINE SWEEP WEST TO EAST - WED 25 NOV", 2, INK)
    cv.rect(24, 150, 976, 1, INK)
    draw_map(cv)
    cv.rect(24, 255, 976, 1, INK)
    draw_centered(cv, 512, 259, DATELINE, 2, INK)
    # Story cards: two rows of three
    for i, card in enumerate(CARDS):
        draw_card(cv, 16 + (i % 3) * 333, 284 + (i // 3) * 156, card)
    # The day in numbers
    cv.rect(16, 596, 992, 38, DARK)
    for i, (fig, caps, color) in enumerate(NUMBERS):
        ccx = 16 + i * 99 + 49
        draw_centered(cv, ccx, 601, fig, 2, color)
        for j, cap in enumerate(caps):
            draw_centered(cv, ccx, 618 + j * 8, cap, 1, WHITE)
    # In brief, by region
    draw_text(cv, 16, 642, "IN BRIEF", 3, RED)
    draw_text(cv, 171, 646, "- THIRTY-SIX MORE FACTS, GROUPED BY REGION", 2, INK)
    cv.rect(16, 668, 992, 2, INK)
    for ci, blocks in enumerate(BRIEF_COLUMNS):
        cx = 16 + ci * 250
        by = 676
        for name, accent, briefs in blocks:
            cv.rect(cx, by, 240, 18, accent)
            draw_text(cv, cx + 6, by + 2, name, 2, WHITE)
            draw_right(cv, cx + 234, by + 2, str(len(briefs)), 2, WHITE)
            by += 26
            for brief in briefs:
                cv.rect(cx + 1, by + 4, 5, 5, RED)
                for li, ln in enumerate(wrap_text(brief, 19)):
                    draw_text(cv, cx + 12, by + li * 15, ln, 2, INK)
                by += 29
            by += 8
    # Footer
    cv.rect(16, 995, 992, 1, FAINT)
    draw_centered(cv, 512, 1000,
                  "THE WORLD TODAY - COMPILED FROM THE DAY'S WIRE REPORTS - PAGE 1 OF 1",
                  2, FAINT)


def main():
    cv = Canvas(W, H, PAPER)
    draw_page(cv)
    try:
        os.makedirs("/output", exist_ok=True)
        cv.save("/output/entry.png")
        print("wrote /output/entry.png")
    except OSError:
        cv.save("./entry.png")
        print("wrote ./entry.png")


if __name__ == "__main__":
    main()
