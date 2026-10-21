#!/usr/bin/env python3
"""Generates the TiRobotix SVG illustrations (hero blueprint, urban scene, agricultural scene)."""
import math
import os
import random
import sys

OUT = sys.argv[1]

ACCENT = "#FF7A1A"
VISOR = "#7BE7FF"
JOINT = "#1B232D"
HAND = "#26303C"
OL = 'stroke="#0A0F19" stroke-opacity=".28" stroke-width="1"'
MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace"


def sin(d):
    return math.sin(math.radians(d))


def cos(d):
    return math.cos(math.radians(d))


# ---------------------------------------------------------------- side robot

def robot_defs(p):
    return f'''
    <linearGradient id="{p}shell" x1="1" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#C2CBD7"/>
    </linearGradient>
    <linearGradient id="{p}far" x1="1" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#A7B2C0"/><stop offset="1" stop-color="#7A8696"/>
    </linearGradient>
    <linearGradient id="{p}dark" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#34404F"/><stop offset="1" stop-color="#18202A"/>
    </linearGradient>'''


def joint(cx, cy, r, w=1.6):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{JOINT}" stroke="{ACCENT}" stroke-width="{w}"/>'


def arm(fill, a1, a2):
    return f'''
  <g transform="translate(0,-92) rotate({-a1:.1f})">
    <rect x="-6.5" y="6" width="13" height="48" rx="6.5" fill="{fill}" {OL}/>
    <g transform="translate(0,56) rotate({-a2:.1f})">
      <rect x="-5.5" y="5" width="11" height="42" rx="5.5" fill="{fill}" {OL}/>
      <rect x="-7" y="46" width="14" height="17" rx="6" fill="{HAND}"/>
    </g>
    {joint(0, 56, 7.5)}
  </g>
  {joint(0, -92, 10, 1.8)}'''


def leg(fill, t, k, sole):
    return f'''
  <g transform="translate(0,6) rotate({-t:.1f})">
    <rect x="-8" y="6" width="16" height="56" rx="8" fill="{fill}" {OL}/>
    <g transform="translate(0,66) rotate({k:.1f})">
      <rect x="-7" y="5" width="14" height="56" rx="7" fill="{fill}" {OL}/>
      <g transform="translate(0,66) rotate({t - k:.1f})">
        <rect x="-12" y="3" width="34" height="10" rx="4" fill="{sole}"/>
        <rect x="-10" y="0" width="26" height="7" rx="3" fill="{fill}" {OL}/>
        {joint(0, 0, 5.5, 1.4)}
      </g>
    </g>
    {joint(0, 66, 8.5)}
  </g>
  {joint(0, 6, 10.5, 1.8)}'''


def foot_bottom(t, k):
    knee_y = 6 + 66 * cos(t)
    ankle_y = knee_y + 66 * cos(t - k)
    return ankle_y + 13


def hand_pos(a1, a2):
    ex, ey = 56 * sin(a1), -92 + 56 * cos(a1)
    return ex + 54 * sin(a1 + a2), ey + 54 * cos(a1 + a2)


def crate(kind, hx, hy):
    x0, y0, w, h = hx - 36, hy - 22, 62, 34
    if kind == "parcel":
        return f'''
  <g>
    <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="2" fill="#C8955A" {OL}/>
    <rect x="{x0}" y="{y0}" width="{w}" height="6" fill="#B07E47"/>
    <rect x="{x0 + w / 2 - 4}" y="{y0}" width="8" height="{h}" fill="#E2BE86" opacity=".8"/>
    <rect x="{x0 + 6}" y="{y0 + 14}" width="16" height="10" rx="1" fill="#F4F1EA"/>
    <path d="M{x0 + 8},{y0 + 17} h12 M{x0 + 8},{y0 + 20} h8" stroke="#8A8F98" stroke-width="1"/>
  </g>'''
    produce = []
    rnd = random.Random(7)
    for i in range(9):
        px = x0 + 6 + i * (w - 12) / 8 + rnd.uniform(-1.5, 1.5)
        py = y0 - 2 + rnd.uniform(-3, 2)
        col = ["#E2432F", "#F07A2A", "#D93A2B", "#E8562E"][i % 4]
        produce.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.6" fill="{col}"/>'
                       f'<circle cx="{px - 1.8:.1f}" cy="{py - 2:.1f}" r="1.6" fill="#fff" opacity=".45"/>')
        if i % 3 == 1:
            produce.append(f'<ellipse cx="{px + 2:.1f}" cy="{py - 6:.1f}" rx="5" ry="2" fill="#4E9A35" '
                           f'transform="rotate(-25 {px + 2:.1f} {py - 6:.1f})"/>')
    slats = "".join(
        f'<rect x="{x0}" y="{y0 + 2 + j * 11}" width="{w}" height="9" rx="1.5" fill="#B47A43" {OL}/>'
        for j in range(3))
    return f'''
  <g>
    {''.join(produce)}
    <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="2" fill="#8E5D2F"/>
    {slats}
    <rect x="{x0 + 2}" y="{y0}" width="5" height="{h}" fill="#9D6836"/>
    <rect x="{x0 + w - 7}" y="{y0}" width="5" height="{h}" fill="#9D6836"/>
  </g>'''


def side_robot(p, cx, ground, s, near_arm, far_arm, near_leg, far_leg, carry=None, flip=False):
    low = max(foot_bottom(*near_leg), foot_bottom(*far_leg))
    shell, far, dark = f"url(#{p}shell)", f"url(#{p}far)", f"url(#{p}dark)"
    sx = -s if flip else s
    body = f'''
  <rect x="-37" y="-106" width="17" height="62" rx="5" fill="{dark}" {OL}/>
  <circle cx="-28.5" cy="-96" r="1.8" fill="#3DDC97"/>
  <circle cx="-28.5" cy="-89" r="1.8" fill="#3DDC97"/>
  <circle cx="-28.5" cy="-82" r="1.8" fill="{ACCENT}"/>
  <rect x="-17" y="-10" width="34" height="24" rx="9" fill="{shell}" {OL}/>
  <rect x="-12" y="-27" width="24" height="19" rx="5" fill="{dark}"/>
  <path d="M-16,-22 L16,-22 L24,-76 Q27,-104 6,-112 L-14,-112 Q-28,-104 -24,-76 Z" fill="{shell}" {OL}/>
  <path d="M-19,-46 L19,-46" stroke="#9AA6B4" stroke-width="1"/>
  <rect x="12" y="-97" width="10" height="3.5" rx="1.75" fill="{ACCENT}"/>
  <rect x="-6" y="-127" width="12" height="18" rx="3" fill="{dark}"/>
  <rect x="-19" y="-163" width="40" height="40" rx="13" fill="{shell}" {OL}/>
  <rect x="5" y="-153" width="18" height="14" rx="6" fill="#0E1620"/>
  <rect x="10" y="-148.5" width="11" height="4" rx="2" fill="{VISOR}"/>
  {joint(-5, -143, 6, 1.4)}'''
    held = crate(carry, *hand_pos(*near_arm)) if carry else ""
    return f'''
<g transform="translate({cx:.1f},{ground - low * s:.1f}) scale({sx},{s})">
  {arm(far, *far_arm)}
  {leg(far, *far_leg, "#141A22")}
  {body}
  {leg(shell, *near_leg, HAND)}
  {held}
  {arm(shell, *near_arm)}
</g>'''


def ground_shadow(cx, ground, rx, op=0.35):
    return f'<ellipse cx="{cx}" cy="{ground + 1}" rx="{rx}" ry="{rx * 0.14:.1f}" fill="#000" opacity="{op}"/>'


def svg(w, h, defs, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">
<title id="t">{title}</title>
<defs>{defs}
</defs>
{body}
</svg>
'''


# ---------------------------------------------------------------- urban scene

def person(x, ground, h, color, op=1.0):
    s = h / 172
    return f'''
<g transform="translate({x},{ground}) scale({s:.3f})" fill="{color}" opacity="{op}">
  <circle cx="0" cy="-160" r="11"/>
  <path d="M-15,-145 Q0,-151 15,-145 L18,-80 L-18,-80 Z"/>
  <rect x="-23" y="-142" width="8" height="58" rx="4"/>
  <rect x="15" y="-142" width="8" height="58" rx="4"/>
  <rect x="-14" y="-84" width="12" height="84" rx="5"/>
  <rect x="2" y="-84" width="12" height="84" rx="5"/>
</g>'''


def detection(x, y, w, h, label):
    return f'''
<g fill="none" stroke="{ACCENT}" stroke-width="1.4">
  <path d="M{x},{y + 10} v-10 h10 M{x + w - 10},{y} h10 v10 M{x + w},{y + h - 10} v10 h-10 M{x + 10},{y + h} h-10 v-10"/>
</g>
<g>
  <rect x="{x}" y="{y - 17}" width="{len(label) * 6.2 + 10:.0f}" height="14" rx="2" fill="{ACCENT}"/>
  <text x="{x + 5}" y="{y - 7}" font-family="{MONO}" font-size="9" font-weight="600" fill="#0A0E13" letter-spacing=".6">{label}</text>
</g>'''


def building(x, base, w, h, fill, rnd, win_on="#FFD08A", win_off="#283152", density=0.45, cols=None):
    parts = [f'<rect x="{x}" y="{base - h}" width="{w}" height="{h}" fill="{fill}"/>']
    cols = cols or max(2, int(w // 16))
    gap_x = w / cols
    rows = int((h - 20) // 18)
    for r in range(rows):
        for c in range(cols):
            wx = x + c * gap_x + gap_x * 0.28
            wy = base - h + 14 + r * 18
            lit = rnd.random() < density
            parts.append(f'<rect x="{wx:.1f}" y="{wy}" width="{gap_x * 0.44:.1f}" height="9" '
                         f'fill="{win_on if lit else win_off}" opacity="{0.9 if lit else 0.8}"/>')
    return "".join(parts)


def urban():
    rnd = random.Random(42)
    W, H = 800, 520
    defs = robot_defs("u") + f'''
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0E1730"/><stop offset=".55" stop-color="#2C3B66"/>
      <stop offset=".82" stop-color="#C9707A"/><stop offset="1" stop-color="#F59A5A"/>
    </linearGradient>
    <radialGradient id="sun" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="#FFD9A0" stop-opacity=".95"/><stop offset=".35" stop-color="#FFB27A" stop-opacity=".55"/>
      <stop offset="1" stop-color="#FF8A5B" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="cone" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFE3B0" stop-opacity=".45"/><stop offset="1" stop-color="#FFE3B0" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="road" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1A2033"/><stop offset="1" stop-color="#0D111C"/>
    </linearGradient>
    <linearGradient id="walk" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3A4260"/><stop offset="1" stop-color="#262D44"/>
    </linearGradient>'''
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
         f'<circle cx="560" cy="330" r="190" fill="url(#sun)"/>',
         '<circle cx="560" cy="330" r="46" fill="#FFD3A0" opacity=".9"/>']
    # stars
    for _ in range(40):
        b.append(f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, 150):.0f}" '
                 f'r="{rnd.uniform(.5, 1.3):.1f}" fill="#fff" opacity="{rnd.uniform(.2, .7):.2f}"/>')
    # far skyline
    x = -10
    while x < W:
        w = rnd.randint(30, 70)
        h = rnd.randint(70, 190)
        b.append(f'<rect x="{x}" y="{360 - h}" width="{w}" height="{h}" fill="#43497A" opacity=".75"/>')
        if rnd.random() < 0.25:
            b.append(f'<rect x="{x + w / 2 - 1}" y="{360 - h - 24}" width="2" height="24" fill="#43497A" opacity=".75"/>'
                     f'<circle cx="{x + w / 2}" cy="{360 - h - 24}" r="2" fill="#FF6A5B"/>')
        x += w + rnd.randint(-6, 4)
    # mid skyline
    x = -20
    while x < W:
        w = rnd.randint(50, 100)
        h = rnd.randint(90, 200)
        b.append(building(x, 395, w, h, "#232B4A", rnd, density=0.3))
        x += w + rnd.randint(4, 30)
    # near buildings
    b.append(building(-10, 395, 150, 330, "#141A2E", rnd, density=0.5, cols=6))
    b.append(building(680, 395, 140, 300, "#141A2E", rnd, density=0.5, cols=6))
    b.append('<rect x="-10" y="60" width="150" height="8" fill="#1E2640"/><rect x="680" y="90" width="140" height="8" fill="#1E2640"/>')
    # street
    b.append(f'<rect x="0" y="392" width="{W}" height="48" fill="url(#walk)"/>')
    b.append(f'<rect x="0" y="392" width="{W}" height="3" fill="#525C80"/>')
    for i in range(0, W, 64):
        b.append(f'<rect x="{i}" y="395" width="1.5" height="45" fill="#20263B"/>')
    b.append(f'<rect x="0" y="440" width="{W}" height="6" fill="#4A5372"/>')
    b.append(f'<rect x="0" y="446" width="{W}" height="{H - 446}" fill="url(#road)"/>')
    for i in range(7):
        b.append(f'<rect x="{520 + i * 34}" y="452" width="20" height="{H - 452}" fill="#E8EAF2" opacity=".55"/>')
    for i in range(0, 500, 70):
        b.append(f'<rect x="{i}" y="484" width="38" height="4" fill="#F2C14E" opacity=".75"/>')
    # street lamps
    for lx in (175, 720):
        b.append(f'''
<polygon points="{lx + 22},232 {lx - 30},440 {lx + 92},440" fill="url(#cone)"/>
<rect x="{lx - 2.5}" y="222" width="5" height="218" fill="#0B0F1C"/>
<path d="M{lx},226 q2,-12 22,-10" stroke="#0B0F1C" stroke-width="4" fill="none"/>
<rect x="{lx + 12}" y="214" width="22" height="7" rx="3" fill="#0B0F1C"/>
<rect x="{lx + 14}" y="220" width="18" height="3" rx="1.5" fill="#FFE8B8"/>''')
    # traffic light
    b.append('''
<rect x="612" y="280" width="5" height="160" fill="#0B0F1C"/>
<rect x="604" y="276" width="21" height="44" rx="4" fill="#0B0F1C"/>
<circle cx="614.5" cy="288" r="5" fill="#3A1A1A"/>
<circle cx="614.5" cy="306" r="5" fill="#2EE59D"/>
<circle cx="614.5" cy="306" r="11" fill="#2EE59D" opacity=".2"/>''')
    # tree
    b.append('''
<rect x="64" y="330" width="6" height="110" fill="#0B0F1C"/>
<circle cx="67" cy="318" r="36" fill="#162034"/><circle cx="42" cy="334" r="24" fill="#162034"/>
<circle cx="92" cy="332" r="26" fill="#162034"/>
<rect x="46" y="420" width="42" height="20" rx="2" fill="#0F1424"/>''')
    # people in the background
    for px, pg, ph, conf in ((462, 434, 200, "0.97"), (548, 428, 188, "0.94")):
        b.append(person(px, pg, ph, "#0C1122", 0.96))
        b.append(detection(px - 34, pg - ph - 8, 68, ph + 12, f"PERSON {conf}"))
    # robot path
    b.append(f'<path d="M318,437 C 340,437 360,437 400,437" stroke="{ACCENT}" stroke-width="2" '
             f'stroke-dasharray="2 7" stroke-linecap="round" fill="none" opacity=".9"/>')
    b.append(f'<path d="M400,432 l8,5 l-8,5" stroke="{ACCENT}" stroke-width="2" fill="none" stroke-linecap="round"/>')
    # robots
    b.append(ground_shadow(250, 437, 52))
    b.append(side_robot("u", 246, 437, 0.72, (12, 70), (16, 66), (22, 12), (-14, 34), carry="parcel"))
    # HUD tag
    b.append(f'''
<g font-family="{MONO}" font-size="9.5" letter-spacing=".8">
  <rect x="24" y="24" width="194" height="44" rx="4" fill="#0A0E13" opacity=".72"/>
  <circle cx="38" cy="38" r="3.5" fill="#2EE59D"/>
  <text x="48" y="41" fill="#E6EDF3">URBAN NAV · ACTIVE</text>
  <text x="34" y="58" fill="#8A99A8">PEDESTRIAN-AWARE ROUTING</text>
</g>''')
    return svg(W, H, defs, "\n".join(b), "Humanoid robot carrying a parcel along a city sidewalk at dusk")


# ---------------------------------------------------------------- agricultural scene

def plant_symbol(pid, fruit, rnd):
    leaves = []
    for ang, ln in ((-70, 14), (-35, 16), (0, 15), (35, 16), (70, 14), (-15, 11), (20, 11)):
        lx, ly = ln * 0.55 * sin(ang), -8 - ln * 0.55 * abs(cos(ang))
        col = rnd.choice(["#3E7E2B", "#4C9234", "#357227", "#5AA33C"])
        leaves.append(f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="{ln / 2:.1f}" ry="3.6" fill="{col}" '
                      f'transform="rotate({ang - 90} {lx:.1f} {ly:.1f})"/>')
    fr = ""
    if fruit:
        for fx, fy in ((-5, -6), (4, -4), (0, -11)):
            fr += f'<circle cx="{fx}" cy="{fy}" r="2.8" fill="#E2432F"/>'
    return f'<symbol id="{pid}" overflow="visible">{"".join(leaves)}{fr}</symbol>'


def agri():
    rnd = random.Random(11)
    W, H = 800, 520
    VPX, VPY, HOR = 400, 252, 292
    defs = robot_defs("a") + robot_defs("b") + f'''
    <linearGradient id="asky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#6FB6E4"/><stop offset=".6" stop-color="#BFE2F1"/>
      <stop offset="1" stop-color="#FCE7BC"/>
    </linearGradient>
    <radialGradient id="asun" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="#FFF6D8"/><stop offset=".25" stop-color="#FFE9A8" stop-opacity=".8"/>
      <stop offset="1" stop-color="#FFE9A8" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="haze" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F6EDD0" stop-opacity=".75"/><stop offset="1" stop-color="#F6EDD0" stop-opacity="0"/>
    </linearGradient>
    {''.join(plant_symbol(f"p{i}", i >= 3, rnd) for i in range(5))}
    <clipPath id="field"><rect x="0" y="{HOR}" width="{W}" height="{H - HOR}"/></clipPath>'''
    b = [f'<rect width="{W}" height="{H}" fill="url(#asky)"/>',
         '<circle cx="640" cy="110" r="130" fill="url(#asun)"/>',
         '<circle cx="640" cy="110" r="30" fill="#FFF4CF"/>']
    for cx, cy, s in ((150, 90, 1.0), (430, 60, 0.8), (300, 150, 0.6)):
        b.append(f'<g fill="#fff" opacity=".8" transform="translate({cx},{cy}) scale({s})">'
                 '<ellipse cx="0" cy="0" rx="46" ry="14"/><ellipse cx="-18" cy="-10" rx="22" ry="14"/>'
                 '<ellipse cx="14" cy="-14" rx="26" ry="17"/></g>')
    # hills
    b.append(f'<path d="M0,250 C120,205 230,215 340,240 C450,262 560,200 680,215 C740,222 780,235 {W},240 L{W},{HOR + 4} L0,{HOR + 4} Z" fill="#A9CC93"/>')
    b.append(f'<path d="M0,272 C140,248 260,262 380,270 C520,280 620,250 {W},262 L{W},{HOR + 4} L0,{HOR + 4} Z" fill="#86B872"/>')
    # polytunnel greenhouses
    for gx in (70, 150, 230):
        b.append(f'''<g transform="translate({gx},282)">
  <path d="M0,0 v-14 a36,26 0 0 1 72,0 v14 Z" fill="#EEF5F6" opacity=".95"/>
  <path d="M12,-28 v28 M24,-36 v36 M36,-38 v38 M48,-36 v36 M60,-28 v28" stroke="#BFD3D8" stroke-width="1.2"/>
  <path d="M0,-14 a36,26 0 0 1 72,0" fill="none" stroke="#C9DCE0" stroke-width="1.5"/></g>''')
    # tree line
    for tx in range(470, 800, 22):
        r = rnd.uniform(9, 14)
        b.append(f'<circle cx="{tx}" cy="{279 - r * 0.6:.1f}" r="{r:.1f}" fill="#4F8A45"/>')
    # wind turbine
    b.append('''<g transform="translate(560,170)" stroke="#F4F7F8" stroke-linecap="round">
  <path d="M0,0 V108" stroke-width="3"/>
  <path d="M0,0 L0,-36 M0,0 L31,18 M0,0 L-31,18" stroke-width="2.4"/>
  <circle r="3" fill="#F4F7F8" stroke="none"/></g>''')
    # field with perspective rows
    b.append(f'<rect x="0" y="{HOR}" width="{W}" height="{H - HOR}" fill="#7A5B37"/>')
    rows = []
    span = 64
    for i in range(-16, 17):
        x0 = VPX + i * span
        x1 = x0 + span * 0.55
        rows.append(f'<polygon points="{VPX},{VPY} {x0},{H} {x1:.1f},{H}" fill="#5E8F36"/>')
    b.append(f'<g clip-path="url(#field)">{"".join(rows)}</g>')
    # plants along rows, back to front
    plants = []
    for i in range(-16, 17):
        cxb = VPX + i * span + span * 0.275
        y = HOR + 8
        while y < H + 10:
            f = (y - VPY) / (H - VPY)
            x = VPX + (cxb - VPX) * f
            if -20 < x < W + 20:
                plants.append((y, x, f * 1.35, rnd.randrange(5) if rnd.random() < 0.35 else rnd.randrange(3)))
            y += 5 + f * 26
    plants.sort()
    b.append("".join(f'<use href="#p{v}" transform="translate({x:.1f},{y:.1f}) scale({s:.2f})"/>'
                     for y, x, s, v in plants))
    b.append(f'<rect x="0" y="{HOR}" width="{W}" height="60" fill="url(#haze)"/>')
    # robots
    b.append(ground_shadow(560, 352, 16, .25))
    b.append(side_robot("b", 560, 352, 0.3, (38, 8), (12, 18), (6, 4), (-4, 4)))
    b.append(detection(574, 330, 30, 26, "RIPE · PICK"))
    b.append(ground_shadow(300, 478, 64, .32))
    b.append(side_robot("a", 296, 478, 0.88, (12, 70), (16, 66), (18, 10), (-12, 30), carry="produce"))
    b.append(f'''
<g font-family="{MONO}" font-size="9.5" letter-spacing=".8">
  <rect x="24" y="24" width="194" height="44" rx="4" fill="#0A0E13" opacity=".72"/>
  <circle cx="38" cy="38" r="3.5" fill="#2EE59D"/>
  <text x="48" y="41" fill="#E6EDF3">FIELD OPS · HARVEST</text>
  <text x="34" y="58" fill="#8A99A8">TERRAIN-ADAPTIVE GAIT</text>
</g>''')
    return svg(W, H, defs, "\n".join(b), "Humanoid robots harvesting tomatoes in crop rows on a farm")


# ---------------------------------------------------------------- hero blueprint (front view)

def front_robot():
    st = 'fill="#0F1924" stroke="#8FA6BF" stroke-width="1.1"'

    def j(x, y, r):
        return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#0A0F14" stroke="{ACCENT}" stroke-width="1.6"/>'
                f'<circle cx="{x}" cy="{y}" r="{r * 0.35:.1f}" fill="{ACCENT}"/>')

    def arm_(side):
        sx, ang = side * 52, side * -8
        return f'''
  <g transform="translate({sx},80) rotate({ang})">
    <rect x="-7" y="8" width="14" height="58" rx="7" {st}/>
    <rect x="-6" y="80" width="12" height="54" rx="6" {st}/>
    <rect x="-8" y="137" width="16" height="22" rx="7" {st}/>
    {j(0, 72, 9)}
  </g>
  {j(sx, 80, 12)}'''

    def leg_(side):
        hx = side * 17
        return f'''
  <rect x="{hx - 8}" y="210" width="16" height="72" rx="8" {st}/>
  <rect x="{hx - 7}" y="300" width="14" height="74" rx="7" {st}/>
  <rect x="{hx - 15 + side * 4}" y="386" width="30" height="12" rx="5" {st}/>
  {j(hx, 290, 10)}{j(hx, 380, 6)}{j(hx, 200, 11)}'''

    return f'''
  {arm_(-1)}{arm_(1)}
  {leg_(-1)}{leg_(1)}
  <rect x="-28" y="168" width="56" height="26" rx="9" {st}/>
  <rect x="-20" y="156" width="40" height="14" rx="4" {st}/>
  <path d="M-44,70 Q0,60 44,70 L34,158 Q0,166 -34,158 Z" {st}/>
  <path d="M-30,136 Q0,142 30,136" fill="none" stroke="#8FA6BF" stroke-width=".8" opacity=".6"/>
  <rect x="-16" y="86" width="32" height="26" rx="5" fill="#0A0F14" stroke="{ACCENT}" stroke-width="1.2"/>
  <path d="M-9,99 h4 l3,-6 l4,12 l3,-6 h4" fill="none" stroke="{ACCENT}" stroke-width="1.4" stroke-linejoin="round"/>
  <circle cx="0" cy="124" r="4" fill="#2EE59D"/>
  <rect x="-7" y="52" width="14" height="14" rx="3" {st}/>
  <rect x="-24" y="0" width="48" height="52" rx="16" {st}/>
  <rect x="-17" y="18" width="34" height="13" rx="6.5" fill="#05080C" stroke="#8FA6BF" stroke-width=".8"/>
  <rect class="visor" x="-13" y="22.5" width="26" height="4" rx="2" fill="{VISOR}" filter="url(#glow)"/>'''


def hero():
    W, H = 560, 640
    S, OX, OY = 1.22, 280, 58

    def P(x, y):
        return OX + S * x, OY + S * y

    callouts = [
        # (side, label, sub, point(x,y) in robot coords, label y)
        (1, "VISION + COMPUTE", "STEREO DEPTH · AI", (17, 25), 72),
        (-1, "SHOULDER ACTUATOR", "3 DOF · BACKDRIVABLE", (-52, 80), 140),
        (1, "SAFETY CONTROLLER", "E-STOP · TORQUE LIMIT", (16, 99), 176),
        (-1, "ELBOW JOINT", "CYCLOIDAL REDUCER", (-62, 151), 238),
        (1, "HIP JOINT", "3 DOF · ABS. ENCODER", (17, 200), 296),
        (-1, "KNEE ACTUATOR", "HIGH-TORQUE MODULE", (-17, 290), 400),
        (1, "BLDC MOTOR", "FOC DRIVER · CAN-BUS", (17, 290), 420),
        (-1, "FOOT SENSORS", "FORCE / TORQUE", (-17, 392), 532),
    ]
    c = []
    for i, (side, label, sub, pt, ly) in enumerate(callouts, 1):
        px, py = P(*pt)
        edge = 392 if side == 1 else 168
        knee_x = edge - side * 14
        anchor = "start" if side == 1 else "end"
        tx = edge + side * 8
        c.append(f'''
  <g class="callout">
    <polyline points="{px:.1f},{py:.1f} {knee_x:.1f},{ly} {edge},{ly}" fill="none" stroke="#5B7088" stroke-width="1"/>
    <circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{ACCENT}"/>
    <circle cx="{px:.1f}" cy="{py:.1f}" r="7" fill="none" stroke="{ACCENT}" stroke-opacity=".45"/>
    <text x="{tx}" y="{ly - 3}" text-anchor="{anchor}" font-size="10.5" fill="#E6EDF3" letter-spacing=".9"><tspan fill="{ACCENT}">{i:02d} </tspan>{label}</text>
    <text x="{tx}" y="{ly + 11}" text-anchor="{anchor}" font-size="8.5" fill="#6F849B" letter-spacing=".8">{sub}</text>
  </g>''')
    defs = f'''
    <pattern id="g1" width="16" height="16" patternUnits="userSpaceOnUse">
      <path d="M16,0 H0 V16" fill="none" stroke="#FFFFFF" stroke-opacity=".045"/>
    </pattern>
    <pattern id="g2" width="80" height="80" patternUnits="userSpaceOnUse">
      <path d="M80,0 H0 V80" fill="none" stroke="#FFFFFF" stroke-opacity=".08"/>
    </pattern>
    <radialGradient id="fade" cx=".5" cy=".45" r=".6">
      <stop offset="0" stop-color="#fff"/><stop offset=".75" stop-color="#fff"/><stop offset="1" stop-color="#000"/>
    </radialGradient>
    <mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
    <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="1" stop-color="{ACCENT}" stop-opacity=".22"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-200%" width="200%" height="500%">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .scan {{ animation: scan 6s cubic-bezier(.45,0,.55,1) infinite; }}
      .visor {{ animation: pulse 3s ease-in-out infinite; }}
      @keyframes scan {{ 0% {{ transform: translateY(0); opacity: 0; }} 10% {{ opacity: 1; }} 90% {{ opacity: 1; }} 100% {{ transform: translateY(500px); opacity: 0; }} }}
      @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .55; }} }}
      @media (prefers-reduced-motion: reduce) {{ .scan, .visor {{ animation: none; }} .scan {{ opacity: 0; }} }}
    </style>'''
    body = f'''
<g mask="url(#m)"><rect width="{W}" height="{H}" fill="url(#g1)"/><rect width="{W}" height="{H}" fill="url(#g2)"/></g>
<path d="M{OX},24 V{H - 30}" stroke="#5B7088" stroke-width=".8" stroke-dasharray="6 4 1 4" opacity=".7"/>
<g transform="translate({OX},{OY}) scale({S})">{front_robot()}
</g>
<rect class="scan" x="{OX - 110}" y="{OY - 30}" width="220" height="30" fill="url(#scan)"/>
<g font-family="{MONO}">{"".join(c)}
  <text x="20" y="22" font-size="9" fill="#6F849B" letter-spacing="1.2">FIG. 01 — HUMANOID REFERENCE ARCHITECTURE</text>
  <g transform="translate({W - 220},{H - 40})">
    <rect width="200" height="28" fill="none" stroke="#5B7088" stroke-width=".8"/>
    <path d="M148,0 V28" stroke="#5B7088" stroke-width=".8"/>
    <text x="10" y="18" font-size="9" fill="#AFC0D2" letter-spacing="1.2">TIROBOTIX · HUMANOID</text>
    <text x="158" y="18" font-size="9" fill="{ACCENT}" letter-spacing="1.2">REV A</text>
  </g>
</g>'''
    return svg(W, H, defs, body, "Technical illustration of a humanoid robot with its joints, motors and safety systems labelled")


os.makedirs(OUT, exist_ok=True)
for name, fn in (("urban.svg", urban), ("agriculture.svg", agri), ("hero-blueprint.svg", hero)):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(fn())
    print("wrote", name)
