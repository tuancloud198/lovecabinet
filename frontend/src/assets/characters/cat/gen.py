#!/usr/bin/env python3
"""Generates the cat pet art for Love Cabinet.

Outputs (default: the folder this script lives in):
  body-1.svg .. body-3.svg   one body per growth stage, without the head
  head-<mood>.svg            the full head per mood (neutral/happy/shy/excited), one shared viewBox;
                             also used on its own as the small mood icon
  index.js                   imports + the anchor (position/size) of the head on each body, for PetArt.vue

Usage: python3 gen.py [out_dir]
"""
import os, sys

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
MOODS = ['neutral', 'happy', 'shy', 'excited']

OUT = '#3a2a20'
FUR = '#F4AC63'
FUR_SH = '#E6914A'
STRIPE = '#D9773A'
CREAM = '#FFF4E4'
CREAM_SH = '#F3DCC0'
EAR_IN = '#F7B9B0'
NOSE = '#E77F78'
BLUSH = '#F49A90'
BOW = '#D9564C'
BOW_SH = '#B9473E'
BOW_HI = '#FBE5DD'
SPARK = '#F6C431'
MOUTH = '#7A2E2A'
TONGUE = '#F08C92'
GRASS = '#C9E39A'
GRASS_SH = '#B4D67F'
BLADE = '#8FC25A'

SW = 6  # outline width in head-local units

def f(x):
    return ('%.1f' % x).rstrip('0').rstrip('.')


def ear(side, pid):
    s = side
    outer = (f'M{f(-100*s)},-18 C{f(-104*s)},-62 {f(-100*s)},-100 {f(-90*s)},-118 '
             f'C{f(-84*s)},-126 {f(-74*s)},-124 {f(-64*s)},-116 C{f(-52*s)},-106 {f(-40*s)},-92 {f(-28*s)},-76 Z')
    inner = (f'M{f(-88*s)},-36 C{f(-92*s)},-66 {f(-88*s)},-92 {f(-82*s)},-104 '
             f'C{f(-72*s)},-100 {f(-58*s)},-86 {f(-46*s)},-72 Z')
    tuft = f'M{f(-82*s)},-66 L{f(-72*s)},-80 M{f(-78*s)},-54 L{f(-64*s)},-66'
    return (f'<path d="{outer}" fill="{FUR}" stroke="{OUT}" stroke-width="{SW}"/>'
            f'<path d="{inner}" fill="{EAR_IN}"/>'
            f'<path d="{tuft}" stroke="{CREAM}" stroke-width="3.5" fill="none"/>')


HEAD_D = ('M0,-80 C58,-80 102,-54 105,-8 C106,14 101,28 95,38 L110,48 L92,54 L102,64 L82,64 '
          'C62,80 32,86 0,86 C-32,86 -62,80 -82,64 L-102,64 L-92,54 L-110,48 L-95,38 '
          'C-101,28 -106,14 -105,-8 C-102,-54 -58,-80 0,-80 Z')

MUZZLE_D = ('M-46,40 C-50,20 -30,6 -12,12 C-6,14 -2,16 0,16 C2,16 6,14 12,12 '
            'C30,6 50,20 46,40 C42,62 22,74 0,74 C-22,74 -42,62 -46,40 Z')


def bow(x, y, rot, scale=1.0):
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(scale)})">'
            f'<path d="M-4,8 L-16,30 L-7,27 L-3,34 L2,10 Z M4,8 L14,30 L5,28 L1,34 Z" fill="{BOW_SH}" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M-6,-3 C-22,-26 -48,-24 -46,0 C-44,22 -20,18 -6,5 Z" fill="{BOW}" stroke="{OUT}" stroke-width="{SW}"/>'
            f'<path d="M6,-3 C22,-26 48,-24 46,0 C44,22 20,18 6,5 Z" fill="{BOW}" stroke="{OUT}" stroke-width="{SW}"/>'
            f'<path d="M-14,-4 C-24,-12 -34,-10 -36,-2 M14,-4 C24,-12 34,-10 36,-2" stroke="{BOW_SH}" stroke-width="4" fill="none"/>'
            f'<path d="M-36,-12 C-32,-16 -27,-16 -24,-14" stroke="{BOW_HI}" stroke-width="4" fill="none"/>'
            f'<rect x="-10" y="-10" width="20" height="20" rx="8" fill="{BOW_SH}" stroke="{OUT}" stroke-width="{SW}"/>'
            f'</g>')


def sparks(x, y, scale=1.0):
    return (f'<g transform="translate({f(x)} {f(y)}) scale({f(scale)})" stroke="{SPARK}" stroke-width="8" fill="none">'
            f'<path d="M-6,-6 L-12,-28"/><path d="M12,2 L30,-14"/><path d="M18,22 L40,18"/></g>')


def eye(mood, ex, ey, cid):
    if mood == 'happy':
        return f'<path d="M{f(ex-17)},{f(ey+6)} Q{f(ex)},{f(ey-16)} {f(ex+17)},{f(ey+6)}" stroke="{OUT}" stroke-width="7" fill="none"/>'
    if mood == 'excited':
        return (f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="20" ry="23" fill="{OUT}"/>'
                f'<circle cx="{f(ex+6)}" cy="{f(ey-9)}" r="7.5" fill="#fff"/>'
                f'<circle cx="{f(ex-7)}" cy="{f(ey+9)}" r="3.8" fill="#fff"/>'
                f'<path d="M{f(ex+8)},{f(ey+4)} l2,5 l5,2 l-5,2 l-2,5 l-2,-5 l-5,-2 l5,-2 Z" fill="#fff"/>')
    # neutral (half-lidded), shy (looking aside)
    rx, ry = 21, 18
    if mood == 'shy':
        px, py, lid = ex - 9, ey + 5, ey - 7
    else:
        px, py, lid = ex + 3, ey + 6, ey - 1
    return (f'<clipPath id="{cid}"><ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{rx}" ry="{ry}"/></clipPath>'
            f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{rx}" ry="{ry}" fill="#fff"/>'
            f'<g clip-path="url(#{cid})">'
            f'<circle cx="{f(px)}" cy="{f(py)}" r="9.5" fill="{OUT}"/>'
            f'<circle cx="{f(px+3)}" cy="{f(py-3)}" r="3" fill="#fff"/>'
            f'<rect x="{f(ex-rx-2)}" y="{f(ey-ry-2)}" width="{2*rx+4}" height="{f(lid-(ey-ry-2))}" fill="{FUR}"/>'
            f'</g>'
            f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{rx}" ry="{ry}" fill="none" stroke="{OUT}" stroke-width="5"/>'
            f'<path d="M{f(ex-rx-2)},{f(lid+1)} Q{f(ex)},{f(lid-3)} {f(ex+rx+2)},{f(lid+1)}" stroke="{OUT}" stroke-width="6.5" fill="none"/>')


def mouth(mood, blep):
    w = f'M-17,31 Q-8,40 0,31 Q8,40 17,31'
    if mood == 'neutral':
        s = ''
        if blep:
            s += f'<path d="M-6,34 L-6,42 Q0,50 6,42 L6,34 Z" fill="{TONGUE}" stroke="{OUT}" stroke-width="4"/>'
        return s + f'<path d="M0,22 L0,31 {w}" stroke="{OUT}" stroke-width="5" fill="none"/>'
    if mood == 'shy':
        return f'<path d="M0,22 L0,30 M-11,33 Q-6,37 0,32 Q6,37 11,33" stroke="{OUT}" stroke-width="4.5" fill="none"/>'
    if mood == 'happy':
        return (f'<clipPath id="mh"><path d="M-17,31 Q-8,38 0,31 Q8,38 17,31 Q15,58 0,60 Q-15,58 -17,31 Z"/></clipPath>'
                f'<path d="M-17,31 Q-8,38 0,31 Q8,38 17,31 Q15,58 0,60 Q-15,58 -17,31 Z" fill="{MOUTH}"/>'
                f'<ellipse cx="0" cy="58" rx="13" ry="11" fill="{TONGUE}" clip-path="url(#mh)"/>'
                f'<path d="M-17,31 Q-8,38 0,31 Q8,38 17,31 Q15,58 0,60 Q-15,58 -17,31 Z" fill="none" stroke="{OUT}" stroke-width="5"/>'
                f'<path d="M0,22 L0,31" stroke="{OUT}" stroke-width="5"/>')
    if mood == 'excited':
        d = 'M-22,30 Q-10,38 0,31 Q10,38 22,30 Q22,68 0,70 Q-22,68 -22,30 Z'
        return (f'<clipPath id="mx"><path d="{d}"/></clipPath>'
                f'<path d="{d}" fill="{MOUTH}"/>'
                f'<ellipse cx="0" cy="68" rx="16" ry="13" fill="{TONGUE}" clip-path="url(#mx)"/>'
                f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="5"/>'
                f'<path d="M0,22 L0,31" stroke="{OUT}" stroke-width="5"/>')
    return ''


def head(mood='neutral', blep=False, fluffy=False):
    p = []
    p.append(ear(1, 'l'))
    p.append(ear(-1, 'r'))
    p.append(f'<clipPath id="hc"><path d="{HEAD_D}"/></clipPath>')
    p.append(f'<path d="{HEAD_D}" fill="{FUR}"/>')
    p.append('<g clip-path="url(#hc)">')
    # soft shading along the bottom/sides
    p.append(f'<path d="M-120,40 C-90,70 -40,84 0,84 C40,84 90,70 120,40 L120,100 L-120,100 Z" fill="{FUR_SH}" opacity="0.55"/>')
    # forehead tabby stripes
    p.append(f'<path d="M-22,-82 L-16,-56 L-10,-82 Z M-6,-84 L0,-50 L6,-84 Z M10,-82 L16,-56 L22,-82 Z" fill="{STRIPE}"/>')
    # cheek stripes
    p.append(f'<path d="M-112,-6 L-84,0 L-112,8 Z M-112,14 L-88,18 L-112,26 Z M112,-6 L84,0 L112,8 Z M112,14 L88,18 L112,26 Z" fill="{STRIPE}"/>')
    # cream muzzle
    p.append(f'<path d="{MUZZLE_D}" fill="{CREAM}"/>')
    p.append('</g>')
    p.append(f'<path d="{HEAD_D}" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    # blush
    if mood == 'shy':
        p.append(f'<ellipse cx="-62" cy="26" rx="22" ry="12" fill="{BLUSH}" opacity="0.85"/>'
                 f'<ellipse cx="62" cy="26" rx="22" ry="12" fill="{BLUSH}" opacity="0.85"/>'
                 f'<path d="M-74,32 L-68,20 M-63,32 L-57,20 M-52,32 L-46,20 M52,32 L58,20 M63,32 L69,20 M74,32 L80,20" stroke="{BOW}" stroke-width="3.5"/>')
    else:
        p.append(f'<ellipse cx="-64" cy="26" rx="17" ry="10" fill="{BLUSH}" opacity="0.7"/>'
                 f'<ellipse cx="64" cy="26" rx="17" ry="10" fill="{BLUSH}" opacity="0.7"/>')
    # eyes
    p.append(eye(mood, -40, -10, 'el'))
    p.append(eye(mood, 40, -10, 'er'))
    if mood == 'shy':
        # tiny sweat drop
        p.append(f'<path d="M84,-46 C78,-36 78,-28 84,-28 C90,-28 90,-36 84,-46 Z" fill="#BFE3F5" stroke="{OUT}" stroke-width="3.5"/>')
    # mouth then nose
    p.append(mouth(mood, blep))
    p.append(f'<path d="M-11,12 Q0,8 11,12 Q8,22 0,24 Q-8,22 -11,12 Z" fill="{NOSE}" stroke="{OUT}" stroke-width="4.5"/>')
    p.append(f'<ellipse cx="-3" cy="14" rx="3" ry="1.8" fill="#fff" opacity="0.8"/>')
    # whiskers
    p.append(f'<path d="M-82,30 L-124,22 M-80,40 L-122,44 M82,30 L124,22 M80,40 L122,44" stroke="{OUT}" stroke-width="3.5" fill="none"/>')
    # bow on the viewer-left ear
    p.append(bow(-66, -82, -22))
    return ''.join(p)


def grass(cx, cy, rx, ry, tufts):
    g = (f'<path d="M{f(cx-rx)},{f(cy)} C{f(cx-rx)},{f(cy-ry)} {f(cx-rx*0.4)},{f(cy-ry*1.1)} {f(cx)},{f(cy-ry)} '
         f'C{f(cx+rx*0.5)},{f(cy-ry*1.15)} {f(cx+rx)},{f(cy-ry*0.9)} {f(cx+rx)},{f(cy)} '
         f'C{f(cx+rx)},{f(cy+ry*0.9)} {f(cx+rx*0.4)},{f(cy+ry)} {f(cx)},{f(cy+ry)} '
         f'C{f(cx-rx*0.5)},{f(cy+ry)} {f(cx-rx)},{f(cy+ry*0.8)} {f(cx-rx)},{f(cy)} Z" fill="{GRASS}"/>'
         f'<path d="M{f(cx-rx*0.8)},{f(cy+ry*0.35)} C{f(cx-rx*0.3)},{f(cy+ry*0.85)} {f(cx+rx*0.4)},{f(cy+ry*0.85)} {f(cx+rx*0.85)},{f(cy+ry*0.3)}" '
         f'stroke="{GRASS_SH}" stroke-width="{f(ry*0.5)}" fill="none" opacity="0.8"/>')
    for (x, y, s) in tufts:
        g += (f'<g transform="translate({f(x)} {f(y)}) scale({f(s)})" stroke="{BLADE}" stroke-width="7" fill="none">'
              f'<path d="M0,0 Q-2,-14 -10,-24"/><path d="M6,0 Q8,-18 6,-32"/><path d="M12,0 Q16,-12 24,-18"/></g>')
    return g


def tail(d, w):
    return (f'<path d="{d}" stroke="{OUT}" stroke-width="{f(w+2*SW)}" fill="none"/>'
            f'<path d="{d}" stroke="{FUR}" stroke-width="{f(w)}" fill="none"/>'
            f'<path d="{d}" stroke="{STRIPE}" stroke-width="{f(w)}" fill="none" stroke-linecap="butt" stroke-dasharray="9 20" stroke-dashoffset="-14"/>')


def svg(vb, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'
            f'<g stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>\n')


# ---------- heads ----------
HEAD_VB = (-136, -132, 314, 226)   # x, y, w, h in head-local units


def head_svg(mood):
    b = head(mood, blep=(mood == 'neutral'))
    if mood in ('happy', 'excited'):
        b += sparks(128, -96)
    return svg(' '.join(str(v) for v in HEAD_VB), b)


# ---------- shared bits for the full-body poses ----------
def front_legs(cx, w, gap, yt, yb, gy, ry=13):
    """Two identical forelegs mirrored about x=cx, cream chest showing between them."""
    p = []
    p.append(f'<rect x="{f(cx-gap/2-3)}" y="{f(yt)}" width="{f(gap+6)}" height="{f(yb-yt-4)}" fill="{CREAM}"/>')
    for side in (-1, 1):
        inner = cx + side * gap / 2
        outer = cx + side * (gap / 2 + w)
        x0, x1 = min(inner, outer), max(inner, outer)
        d = (f'M{f(x0)},{f(yt)} L{f(x0)},{f(yb-10)} Q{f(x0)},{f(yb)} {f(x0+10)},{f(yb)} '
             f'L{f(x1-10)},{f(yb)} Q{f(x1)},{f(yb)} {f(x1)},{f(yb-10)} L{f(x1)},{f(yt)} Z')
        p.append(f'<path d="{d}" fill="{FUR}"/>')
        # stripes start at the outer edge and point inwards (mirrored)
        sy = yb - (yb - yt) * 0.42
        p.append(f'<path d="M{f(outer)},{f(sy)} L{f(outer-side*12)},{f(sy)} M{f(outer)},{f(sy+14)} L{f(outer-side*9)},{f(sy+14)}" '
                 f'stroke="{STRIPE}" stroke-width="6" stroke-linecap="butt"/>')
        # outline without the top edge, so the leg flows out of the chest
        p.append(f'<path d="{d[:-2]}" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    for side in (-1, 1):
        pc = cx + side * (gap / 2 + w / 2)
        p.append(f'<ellipse cx="{f(pc)}" cy="{f(gy)}" rx="{f(w/2+3)}" ry="{ry}" fill="{CREAM}" stroke="{OUT}" stroke-width="{SW}"/>')
        p.append(f'<path d="M{f(pc-7)},{f(gy+ry)} L{f(pc-7)},{f(gy+ry-8)} M{f(pc+7)},{f(gy+ry)} L{f(pc+7)},{f(gy+ry-8)}" stroke="{OUT}" stroke-width="3.5"/>')
    return ''.join(p)


# ---------- stage 2/3: sitting ----------
# where the head sits on each body: translate(x y) scale(s) of the head-local coordinates
STAGE_HEAD = {1: (-10, -26, 1.0), 2: (-14, -16, 0.88), 3: (-16, -18, 0.84)}


def sitting(stage):
    fl = stage == 3
    hx, hy, hs = STAGE_HEAD[stage]
    cx = hx                     # centre line of head / chest / front legs
    w, gap = (40, 22) if fl else (36, 20)
    gy = 190
    p = []
    p.append(grass(46, gy + 4, 210 if fl else 192, 22, [(-150, gy + 6, 0.9), (176, gy + 4, 1.0), (214, gy + 12, 0.7)]))
    if fl:
        p.append(tail('M126,180 C196,184 226,132 212,92 C204,68 208,48 230,44', 34))
        body = ('M-60,40 C-74,70 -74,98 -68,114 L-56,190 L150,190 C184,188 192,146 176,106 '
                'C170,92 168,84 160,80 C150,62 140,58 132,56 C116,42 104,40 96,36 C84,32 70,32 50,32 Z')
    else:
        p.append(tail('M120,180 C180,184 208,140 198,100 C192,76 196,58 216,54', 26))
        body = ('M-56,42 C-66,70 -64,96 -54,112 L-44,190 L140,190 C172,188 180,146 166,112 '
                'C150,72 100,40 50,38 Z')
    p.append(f'<clipPath id="bc"><path d="{body}"/></clipPath>')
    p.append(f'<path d="{body}" fill="{FUR}"/>')
    p.append('<g clip-path="url(#bc)">')
    p.append(f'<path d="M20,192 C30,146 74,120 116,120 C160,120 190,150 190,192 Z" fill="{FUR_SH}" opacity="0.5"/>')
    p.append(f'<path d="M88,40 L80,70 L102,46 Z M120,56 L104,84 L130,66 Z M148,80 L126,102 L156,94 Z" fill="{STRIPE}"/>')
    p.append('</g>')
    p.append(f'<path d="{body}" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    if fl:
        p.append(f'<path d="M44,190 C38,134 86,104 130,110 C166,116 182,150 176,182" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    else:
        p.append(f'<path d="M42,190 C36,138 80,110 120,116 C152,120 168,150 162,180" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    p.append(f'<path d="M94,148 L114,138 M102,166 L122,158" stroke="{STRIPE}" stroke-width="8"/>')
    # hind paw
    p.append(f'<ellipse cx="76" cy="{gy}" rx="30" ry="12" fill="{CREAM}" stroke="{OUT}" stroke-width="{SW}"/>')
    # front legs, symmetric about the head centre
    p.append(front_legs(cx, w, gap, 100 if fl else 92, gy - 2, gy - 2))
    # chest bib (symmetric) covering the tops of the legs
    if fl:
        offs = [(-56, 112), (-45, 124), (-34, 114), (-23, 130), (-11, 118), (0, 138),
                (11, 118), (23, 130), (34, 114), (45, 124), (56, 112)]
        zz = ' '.join(f'L{f(cx+dx)},{dy}' for dx, dy in offs)
        p.append(f'<path d="M{f(cx-50)},52 C{f(cx-58)},86 {f(cx-58)},104 {f(cx-56)},112 {zz} '
                 f'C{f(cx+58)},104 {f(cx+58)},86 {f(cx+50)},52 Z" fill="{CREAM}" clip-path="url(#bc)"/>')
        p.append(f'<path d="M{zz[1:]}" fill="none" stroke="{OUT}" stroke-width="4" clip-path="url(#bc)"/>')
    else:
        hw, yb = 42, 132
        p.append(f'<path d="M{f(cx-hw)},56 C{f(cx-hw-4)},104 {f(cx-hw+16)},{yb} {f(cx)},{yb} '
                 f'C{f(cx+hw-16)},{yb} {f(cx+hw+4)},104 {f(cx+hw)},56 Z" fill="{CREAM}"/>')
        p.append(f'<path d="M{f(cx-34)},116 C{f(cx-26)},128 {f(cx-14)},{yb} {f(cx)},{yb} '
                 f'C{f(cx+14)},{yb} {f(cx+26)},128 {f(cx+34)},116" fill="none" stroke="{OUT}" stroke-width="4"/>')
    return ''.join(p)


# ---------- stage 1: lying kitten ----------
def lying():
    p = []
    p.append(grass(50, 122, 190, 18, [(-128, 124, 0.8), (196, 122, 0.9)]))
    body = 'M40,8 C112,-6 184,22 188,78 C190,108 174,124 150,124 L16,124 Z'
    p.append(f'<clipPath id="bc"><path d="{body}"/></clipPath>')
    p.append(f'<path d="{body}" fill="{FUR}"/>')
    p.append('<g clip-path="url(#bc)">')
    p.append(f'<path d="M60,124 C70,84 110,66 150,70 C190,74 210,100 210,124 Z" fill="{FUR_SH}" opacity="0.5"/>')
    p.append(f'<path d="M116,-2 L108,26 L130,4 Z M150,12 L134,38 L162,24 Z M174,38 L152,56 L182,54 Z" fill="{STRIPE}"/>')
    p.append('</g>')
    p.append(f'<path d="{body}" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    p.append(f'<path d="M90,124 C90,96 116,80 144,84 C168,88 180,104 178,120" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    p.append(tail('M180,92 C210,100 208,122 182,124 C156,126 132,124 112,122', 18))
    # forelegs stretched forward under the lifted head (centre x=-10), paws on the ground
    p.append(front_legs(-10, 44, 24, 30, 110, 112, ry=14))
    return ''.join(p)


STAGES = {
    1: ((-176, -160, 404, 308), lying),
    2: ((-152, -134, 396, 358), lambda: sitting(2)),
    3: ((-170, -140, 430, 372), lambda: sitting(3)),
}


def anchor(stage):
    """Head image box on the body image, in % of the body image (x/y = top-left, w = width)."""
    bx, by, bw, bh = STAGES[stage][0]
    hx, hy, hs = STAGE_HEAD[stage]
    vx, vy, vw, vh = HEAD_VB
    return {
        'x': round((hx + vx * hs - bx) / bw * 100, 2),
        'y': round((hy + vy * hs - by) / bh * 100, 2),
        'w': round(vw * hs / bw * 100, 2),
        'r': 0,
    }


INDEX_JS = """// The cat pet: a body per growth stage (no head) + a head per mood, put together by PetArt.vue.
import body1 from './body-1.svg'
import body2 from './body-2.svg'
import body3 from './body-3.svg'
import neutral from './head-neutral.svg'
import happy from './head-happy.svg'
import shy from './head-shy.svg'
import excited from './head-excited.svg'
export default {
  bodies: [body1, body2, body3],
  heads: { neutral, happy, shy, excited },
  // Where the head goes on each body, as % of the body image: x/y = top-left of the head image, w = its width
  // (height follows the head's aspect ratio), r = rotation in degrees around the head's centre.
  anchors: [ANCHORS],
  // Image sizes (viewBox width/height), so PetArt can lay both out in one SVG.
  bodySizes: [BODYSIZES],
  headSize: HEADSIZE,
}
"""


def write(name, text):
    with open(os.path.join(OUT_DIR, name), 'w') as fh:
        fh.write(text)


for st, (vb, fn) in STAGES.items():
    write(f'body-{st}.svg', svg(' '.join(str(v) for v in vb), fn()))
for mood in MOODS:
    write(f'head-{mood}.svg', head_svg(mood))
anchors = ', '.join('{ x: %(x)s, y: %(y)s, w: %(w)s, r: %(r)s }' % anchor(st) for st in STAGES)
body_sizes = ', '.join(f'[{vb[2]}, {vb[3]}]' for vb, _ in STAGES.values())
write('index.js', INDEX_JS.replace('ANCHORS', anchors).replace('BODYSIZES', body_sizes).replace('HEADSIZE', f'[{HEAD_VB[2]}, {HEAD_VB[3]}]'))
print('ok', anchors)
