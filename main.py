#!/usr/bin/env python3
"""Sum up 25 November 2026's world news in one image.

Pure Python 3 standard library. Renders a wire-service front page --
masthead, the day's angle in one line, six story cards, a numbers
strip and thirty one-line briefs -- with a hand-authored 5x7 bitmap
typeface and a small software rasterizer, and writes a deterministic
PNG to /output/entry.png. No assets, no network, no third-party code.

The stories were selected and the page designed with Groq models
(openai/gpt-oss-120b for the plan, qwen/qwen3.8-27b for the sub-edit)
working from the day's wire reports; every fact on the page was
cross-checked against at least two independent reports of the day.
"""
import os
import struct
import zlib

SS = 2                      # supersampling factor
W = H = 1024
CW, CH = W * SS, H * SS

img = bytearray(CW * CH * 3)

PAPER = (244, 239, 230)
CARD = (255, 253, 248)
INK = (16, 18, 22)
GRAY = (80, 84, 92)
RED = (176, 32, 40)
BLUE = (26, 70, 138)
GOLD = (186, 128, 22)
GREEN = (22, 118, 70)
TEAL = (8, 106, 118)
PURPLE = (88, 56, 136)
WHITE = (255, 255, 255)


def rect(x, y, w, h, color):
    """Solid rectangle, in final-image coordinates."""
    x0, y0 = max(int(x * SS), 0), max(int(y * SS), 0)
    x1, y1 = min(int((x + w) * SS), CW), min(int((y + h) * SS), CH)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    n = len(row)
    for yy in range(y0, y1):
        i = (yy * CW + x0) * 3
        img[i:i + n] = row


def frame(x, y, w, h, color, t=1.6):
    rect(x, y, w, t, color)
    rect(x, y + h - t, w, t, color)
    rect(x, y, t, h, color)
    rect(x + w - t, y, t, h, color)


# ------------------------------------------------------------- typeface
# Hand-authored 5x7 bitmap font: seven 5-bit rows per glyph, top first.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    'X': (0x11, 0x0A, 0x04, 0x04, 0x04, 0x0A, 0x11),
    'Y': (0x11, 0x0A, 0x04, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ',': (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ':': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ';': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '-': (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    '+': (0x00, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x00),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '%': (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x19),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '•': (0x00, 0x00, 0x0E, 0x0E, 0x0E, 0x00, 0x00),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
}


def glyph(ch, x, y, s, color, bold=False):
    rows = FONT.get(ch)
    if rows is None:
        return
    for r in range(7):
        bits = rows[r]
        for c in range(5):
            if bits & (0x10 >> c):
                rect(x + c * s, y + r * s, s * 1.02, s * 1.02, color)
                if bold:
                    rect(x + c * s + s * 0.45, y + r * s,
                         s * 1.02, s * 1.02, color)


def text_w(text, s):
    return len(text) * 6 * s


def draw(text, x, y, s, color, bold=False, align='left'):
    text = text.upper()
    w = text_w(text, s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    cx = x
    for ch in text:
        if ch != ' ':
            glyph(ch, cx, y, s, color, bold)
        cx += 6 * s
    return cx


def wrap(text, s, max_w):
    words, lines, cur = text.split(), [], ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if text_w(trial, s) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def paragraph(text, x, y, s, color, max_w, pitch):
    lines = wrap(text, s, max_w)
    for i, ln in enumerate(lines):
        draw(ln, x, y + i * pitch, s, color)
    return len(lines)


# ------------------------------------------------------------- scene
# Wire front page for Wednesday 25 November 2026: six story cards, a
# numbers strip and thirty briefs. 58 facts, each cross-checked
# against at least two independent reports of the day.
def build():
    rect(0, 0, W, H, PAPER)
    rect(28, 14, W - 56, 3.2, INK)
    draw('THE WORLD TODAY', W / 2, 26, 9, INK, bold=True, align='center')
    rect(28, 88, W - 56, 28, RED)
    draw('WEDNESDAY 25 NOVEMBER 2026 • THE DAY ON ONE PAGE',
         W / 2, 95, 2.9, WHITE, bold=True, align='center')
    draw('MARKETS WOBBLE, GEOPOLITICS FLARE AND HUMAN COSTS RISE',
         W / 2, 124, 2.1, GRAY, bold=True, align='center')
    rect(28, 140, W - 56, 1.4, INK)
    rect(28, 145, W - 56, 3.0, INK)

    def card(x, y, w, h, kicker, kcolor, head, sub, facts):
        rect(x, y, w, h, CARD)
        frame(x, y, w, h, INK)
        rect(x, y, w, 26, kcolor)
        draw(kicker, x + 10, y + 5, 2.2, WHITE, bold=True)
        for i, ln in enumerate(head):
            draw(ln, x + 12, y + 34 + i * 26.5, 3.5, INK, bold=True)
        paragraph(sub, x + 12, y + 116, 1.8, GRAY, w - 24, 13.2)
        rect(x + 12, y + 196, w - 24, 1.2, kcolor)
        draw(facts[0], x + 12, y + 203, 1.7, INK)
        draw(facts[1], x + 12, y + 219, 1.7, INK)

    cards = [
        ('MARKETS', TEAL, ['NVIDIA', 'SLIDES 6%', 'RALLY ENDS'],
         "NEW YORK - THE RELIEF RALLY OVER JENSEN HUANG'S RETURN AS NVIDIA CEO FIZZLES; THE SHARES FALL 6 PERCENT.",
         ['NASDAQ -1.5%, S&P 500 -0.5%', '37% BELOW OCTOBER HIGH']),
        ('CHINA', RED, ['CHINA PROBES', 'SHANGHAI', 'PARTY CHIEF'],
         "CHINA INVESTIGATES POLITBURO MEMBER AND SHANGHAI PARTY CHIEF CHEN JINING IN A HIGH-LEVEL PROBE.",
         ['SHANGHAI PARTY CHIEF', 'POLITBURO MEMBER PROBED']),
        ('UKRAINE', BLUE, ['KYIV', 'STRIKES', '14 KILLED'],
         "KYIV - RUSSIAN STRIKES ON UKRAINE'S KYIV REGION KILL AT LEAST 14 PEOPLE, UKRAINIAN OFFICIALS SAY.",
         ['AT LEAST 14 KILLED', 'KYIV REGION TARGETED']),
        ('SAUDI', GOLD, ['RIYADH', 'TOWER HIT', 'TWICE'],
         "RIYADH - SAUDI ARABIA CONDEMNS A TERRORIST ATTACK AFTER THE PIF TOWER IS HIT A SECOND TIME IN A WEEK.",
         ['PIF TOWER HIT TWICE', 'SECOND HIT IN A WEEK']),
        ('UN REPORT', PURPLE, ['FIVE WOMEN', 'KILLED', 'EVERY HOUR'],
         "A UN REPORT FINDS FIVE WOMEN WERE KILLED EACH HOUR BY RELATIVES IN 2025.",
         ['KILLERS WERE RELATIVES', 'UN DAY TO END VIOLENCE']),
        ('LANDMINES', GREEN, ['LANDMINES', '7,000 HIT', '5-YR HIGH'],
         "GLOBAL LANDMINE CASUALTIES HIT A FIVE-YEAR HIGH OF 7,000, WITH MYANMAR AND SYRIA TOPPING THE LIST.",
         ['7,000 CASUALTIES IN A YEAR', 'MYANMAR, SYRIA TOP LIST']),
    ]
    cw, gap = 312, 16
    for i, s in enumerate(cards):
        x = 28 + (i % 3) * (cw + gap)
        y = 156 + (i // 3) * 252
        card(x, y, cw, 240, *s)

    # numbers strip
    rect(28, 658, W - 56, 52, INK)
    draw('$237BN VENEZUELA DEBT • 7,000 MINE CASUALTIES • 14 KILLED AT KYIV • 25 HOSTAGES IN COLOMBIA',
         W / 2, 666, 1.6, (240, 240, 235), align='center')
    draw('NVIDIA -6% • NASDAQ -1.5% • CONFIDENCE 103.3 • $100M SHEIN DEAL • 81.5M US TRAVELLERS',
         W / 2, 688, 1.6, GOLD, align='center')

    # brief zone: 30 items, four columns
    rect(28, 720, W - 56, 30, INK)
    draw('IN BRIEF • THIRTY MORE FACTS FROM WEDNESDAY', 44, 727, 2.6, GOLD, bold=True)
    briefs = [
        'US JURY CONVICTS HUAWEI OF THEFT', 'SOLDIER ZHAO SOLD INTEL TO CHINA',
        'US PROBE: 16 PARTNERS FACE DUTIES', 'CHINA EASES US EXPORT CURBS TO JAN',
        'RUSSIAN JETS ENTER KOREA AIR ZONE', 'NATO EYES NUCLEAR SATELLITE CLAIM',
        'NORTH KOREA WARNS SWISS OFFICE', 'US ENVOY DOUBTS $3.8BN ISRAEL AID',
        'FLYDUBAI CLEARED FOR TEL AVIV', 'GERMANS OPPOSE UKRAINE WEAPONS',
        'GIULIANI GETS MEDAL OF FREEDOM', 'TRUMP PARDONS HOLIDAY TURKEYS',
        'GOMEZ RESIGNS IN ETHICS CASE', 'DEMOCRATS TURN TO 2028 RACE',
        'CDC CHIEF FACES STAFF DOUBTS', 'FORT HOOD BID FAILS ON HASAN',
        'US HOME PRICES STEADY IN SEPT', 'OIL REBOUNDS ON SHIPPING RISKS',
        'MICROSOFT CODE RED AFTER OUTAGE', 'COBALT RUSH BEATS CONGO BAN',
        'SHEIN PAYS $100M IN FTC CASE', 'BAHRAIN: IRAN HIT CIVILIAN SITE',
        'HAMAS CHIEF KILLED IN GAZA', 'PUNJAB: BJP-SAD ALLIANCE FOR 2027',
        'NEPAL PM WINS 15,000 CRORE AID', 'INDIA FACTORY PMI 9-MONTH HIGH',
        'SENSEX +500, NIFTY TOPS 25,400', 'CALIFORNIA FACES EXTREME FLOODS',
        'ENGLAND BEAT AUSTRALIA IN T20', 'REEF: 12 CORAL SPECIES REVIVED',
    ]
    cols_x = [28, 272, 516, 760]
    spans = [(0, 8), (8, 16), (16, 23), (23, 30)]
    for c, (a, b) in enumerate(spans):
        for r, item in enumerate(briefs[a:b]):
            x = cols_x[c]
            y = 754 + r * 29.5
            rect(x + 2, y + 3, 5, 5, RED)
            lines = wrap(item, 1.9, 224)
            for j, ln in enumerate(lines[:2]):
                draw(ln, x + 13, y + j * 13.5, 1.9, INK)
    rect(28, 990, W - 56, 1.6, INK)
    draw("THE WORLD TODAY • WEDNESDAY 25 NOVEMBER 2026 • COMPILED FROM THE DAY'S WIRE REPORTS • PAGE 1 OF 1",
         W / 2, 997, 1.55, GRAY, align='center')


# ------------------------------------------------------------- output
def downscale():
    out = bytearray(W * H * 3)
    for yy in range(H):
        for xx in range(W):
            i = (yy * W + xx) * 3
            a = ((2 * yy) * CW + 2 * xx) * 3
            b = a + 3
            c = a + CW * 3
            d = c + 3
            for k in range(3):
                out[i + k] = (img[a + k] + img[b + k] + img[c + k] + img[d + k]) // 4
    return out


def write_png(path, pixels):
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)
        raw += pixels[yy * stride:(yy + 1) * stride]
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


def main():
    build()
    pixels = downscale()
    os.makedirs('/output', exist_ok=True)
    size = write_png('/output/entry.png', pixels)
    print(f'wrote /output/entry.png ({size} bytes)')


if __name__ == '__main__':
    main()
