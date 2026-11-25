#!/usr/bin/env python3
"""Generates the "Cún Khố Rách" pet art (the poor ragged dog, "khố rách áo ôm") for Love Cabinet.

Outputs (default: the folder this script lives in):
  body-1.svg .. body-3.svg   one body per growth stage, without the head
  head-<mood>.svg            the full head per mood (neutral = the sketch's deadpan face, happy/shy/excited),
                             one shared viewBox; also used on its own as the small mood icon
  index.js                   imports + the anchor (position/size) of the head on each body, for PetArt.vue

Usage: python3 gen.py [out_dir]
"""
import math, os, sys

MOODS = ['neutral', 'happy', 'shy', 'excited']
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

OUT = '#3a2a20'
FUR = '#E3C48E'
FUR_SH = '#D2AF74'
EAR = '#DDB97C'
EAR_SH = '#C99F62'
MUZZLE = '#8C7B68'
MUZZLE_SH = '#7A6A58'
NOSE = '#4A3A2E'
MOUTH = '#6E2A26'
TONGUE = '#F08C92'
BLUSH = '#F49A90'
BLUSH_LINE = '#E0675E'
SPARK = '#F6C431'
RAG = '#A3A8AD'
RAG_SH = '#848A8F'
RAG_HI = '#B8BCC0'
TEAR = '#5E6368'
PATCH_D = '#6F6A66'
PATCH_L = '#A08C78'
STITCH = '#EDE4D6'
GRASS = '#C9E39A'
GRASS_SH = '#B4D67F'
BLADE = '#8FC25A'

SW = 6  # outline width in head-local units


def f(x):
    return ('%.1f' % x).rstrip('0').rstrip('.')


def pts(points):
    return ' '.join(f'{f(x)},{f(y)}' for x, y in points)


def sym(top, segs):
    """Closed path symmetric about x=0: `segs` are the cubic segments ((c1),(c2),(p)) of the right half,
    running from `top` (on the axis) down to a point on the axis; the left half is their mirror image."""
    d = f'M{f(top[0])},{f(top[1])}'
    for c1, c2, p in segs:
        d += f' C{pts([c1, c2, p])}'
    starts = [top] + [s[2] for s in segs[:-1]]
    for (c1, c2, _), p0 in zip(reversed(segs), reversed(starts)):
        d += f' C{pts([(-c2[0], c2[1]), (-c1[0], c1[1]), (-p0[0], p0[1])])}'
    return d + ' Z'


# ---------- head (head-local units, centre of the face at 0,0) ----------
# Wide and a little flat on top, wider than tall; shaggy fur tufts around the cheeks and under the chin
# (they spill over the rag's collar). Right half from the crown down to the chin, mirrored for the left.
SHAG_R = [(106, 10), (113, 22), (103, 27), (107, 39), (95, 42), (97, 54), (83, 55), (83, 67),
          (67, 65), (63, 77), (47, 73), (41, 85), (25, 79), (14, 89), (0, 83)]


def head_path():
    d = 'M0,-74 C44,-76 82,-74 98,-56 C110,-42 110,-14 106,12'
    d += ' L' + pts(SHAG_R[1:])
    left = [(-x, y) for x, y in reversed(SHAG_R[:-1])]
    d += ' L' + pts(left)
    d += ' C-110,-14 -110,-42 -98,-56 C-82,-74 -44,-76 0,-74 Z'
    return d


HEAD_D = head_path()
MUZZLE_D = sym((0, 20), [((27, 20), (41, 28), (41, 40)), ((41, 52), (25, 60), (0, 60))])


def ear(s):
    """Small ear folded forward over the top corner (s=-1: viewer left), lying close against the head."""
    d = (f'M{f(-34*s)},-75 C{f(-70*s)},-82 {f(-106*s)},-72 {f(-117*s)},-48 '
         f'C{f(-124*s)},-26 {f(-122*s)},6 {f(-113*s)},18 C{f(-106*s)},26 {f(-93*s)},24 {f(-89*s)},10 '
         f'C{f(-84*s)},-6 {f(-86*s)},-30 {f(-78*s)},-48 C{f(-70*s)},-62 {f(-56*s)},-70 {f(-34*s)},-75 Z')
    shade = (f'M{f(-102*s)},-62 C{f(-112*s)},-44 {f(-112*s)},-14 {f(-106*s)},4 '
             f'C{f(-100*s)},8 {f(-96*s)},-2 {f(-96*s)},-16 C{f(-96*s)},-36 {f(-90*s)},-52 {f(-78*s)},-64 Z')
    return (f'<path d="{d}" fill="{EAR}"/>'
            f'<path d="{shade}" fill="{EAR_SH}" opacity="0.55"/>'
            f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')


def sparks(x, y, s=1, scale=0.6):
    """Three little yellow dashes fanning out; s=-1 mirrors them to the left side."""
    return (f'<g transform="translate({f(x)} {f(y)}) scale({f(s*scale)} {f(scale)})" stroke="{SPARK}" stroke-width="8" fill="none">'
            f'<path d="M-6,-6 L-10,-28"/><path d="M10,0 L28,-14"/><path d="M16,20 L38,18"/></g>')


def eyes(mood):
    """The sketch's small dark ovals (outer ends a little higher, set wide apart), per mood."""
    out = []
    for ex, rot in ((-40, 16), (40, -16)):
        tr = f'transform="rotate({rot} {ex} -14)"'
        if mood == 'happy':      # closed, ^^
            out.append(f'<path d="M{ex-12},-10 Q{ex},-25 {ex+12},-10" {tr} stroke="{OUT}" stroke-width="6" fill="none"/>')
        elif mood == 'excited':  # bigger, sparkling
            out.append(f'<ellipse cx="{ex}" cy="-14" rx="15" ry="13.5" {tr} fill="{OUT}"/>'
                       f'<circle cx="{ex+5}" cy="-19" r="5" fill="#fff"/>'
                       f'<circle cx="{ex-6}" cy="-9" r="2.4" fill="#fff"/>')
        elif mood == 'shy':      # glancing aside (to the viewer's left)
            out.append(f'<ellipse cx="{ex}" cy="-14" rx="12" ry="8.5" {tr} fill="#fff" stroke="{OUT}" stroke-width="3.5"/>'
                       f'<ellipse cx="{ex-5}" cy="-13" rx="6" ry="6.5" fill="{OUT}"/>')
        else:
            out.append(f'<ellipse cx="{ex}" cy="-14" rx="10" ry="7" {tr} fill="{OUT}"/>')
    return ''.join(out)


def mouth(mood):
    if mood == 'happy':
        return f'<path d="M-28,42 C-15,57 15,57 28,42" stroke="{OUT}" stroke-width="4" fill="none"/>'
    if mood == 'shy':
        return f'<path d="M-10,47 Q-5,42 0,47 Q5,52 10,47" stroke="{OUT}" stroke-width="3.6" fill="none"/>'
    if mood == 'excited':
        d = 'M-13,41 C-13,37 13,37 13,41 C13,51 7,57 0,57 C-7,57 -13,51 -13,41 Z'
        return (f'<clipPath id="mo"><path d="{d}"/></clipPath>'
                f'<path d="{d}" fill="{MOUTH}"/>'
                f'<ellipse cx="0" cy="57" rx="9" ry="7" fill="{TONGUE}" clip-path="url(#mo)"/>'
                f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="3.6"/>')
    return f'<path d="M-24,45 C-12,52 12,52 24,45" stroke="{OUT}" stroke-width="3.6" fill="none"/>'


def head(mood='neutral'):
    """The sketch's face: small slanted dot eyes set wide, a wide grey-brown muzzle low on the face with
    a nose blob on top and a thin smiling mouth line (neutral is the sketch's deadpan look). Only the
    expression changes between moods."""
    p = []
    p.append(f'<clipPath id="hc"><path d="{HEAD_D}"/></clipPath>')
    p.append(f'<path d="{HEAD_D}" fill="{FUR}"/>')
    p.append('<g clip-path="url(#hc)">')
    p.append(f'<path d="M-130,40 C-80,70 -40,74 0,74 C40,74 80,70 130,40 L130,110 L-130,110 Z" fill="{FUR_SH}" opacity="0.6"/>')
    # a few scruffy fur strokes on the cheeks
    p.append(f'<path d="M-86,24 L-74,34 M-80,40 L-66,46 M86,24 L74,34 M80,40 L66,46" stroke="{FUR_SH}" stroke-width="4"/>')
    p.append('</g>')
    p.append(f'<path d="{HEAD_D}" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    p.append(ear(1))
    p.append(ear(-1))
    if mood == 'shy':
        p.append(f'<ellipse cx="-64" cy="22" rx="17" ry="10" fill="{BLUSH}" opacity="0.85"/>'
                 f'<ellipse cx="64" cy="22" rx="17" ry="10" fill="{BLUSH}" opacity="0.85"/>'
                 f'<path d="M-74,28 L-69,16 M-64,28 L-59,16 M-54,28 L-49,16 M54,28 L59,16 M64,28 L69,16 M74,28 L79,16" '
                 f'stroke="{BLUSH_LINE}" stroke-width="3"/>')
    elif mood in ('happy', 'excited'):
        p.append(f'<ellipse cx="-64" cy="22" rx="14" ry="8" fill="{BLUSH}" opacity="0.55"/>'
                 f'<ellipse cx="64" cy="22" rx="14" ry="8" fill="{BLUSH}" opacity="0.55"/>')
    p.append(eyes(mood))
    if mood == 'shy':
        p.append(f'<path d="M70,-52 C64,-42 64,-34 70,-34 C76,-34 76,-42 70,-52 Z" fill="#BFE3F5" stroke="{OUT}" stroke-width="3.2"/>')
    # the muzzle: wide, low on the face, nose blob at its top centre, the mouth across it
    p.append(f'<clipPath id="mz"><path d="{MUZZLE_D}"/></clipPath>')
    p.append(f'<path d="{MUZZLE_D}" fill="{MUZZLE}"/>')
    p.append(f'<path d="M-60,50 C-30,64 30,64 60,50 L60,76 L-60,70 Z" fill="{MUZZLE_SH}" opacity="0.55" clip-path="url(#mz)"/>')
    p.append(f'<path d="{MUZZLE_D}" fill="none" stroke="{OUT}" stroke-width="4.5"/>')
    p.append(mouth(mood))
    p.append(f'<path d="M-11,26 C-11,19 11,19 11,26 C11,32 5,35 0,35 C-5,35 -11,32 -11,26 Z" fill="{NOSE}"/>')
    p.append(f'<ellipse cx="-4" cy="24" rx="3" ry="1.8" fill="#fff" opacity="0.35"/>')
    if mood in ('happy', 'excited'):
        p.append(sparks(126, -80) + sparks(-126, -80, -1))
    return ''.join(p)


def svg(vb, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'
            f'<g stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>\n')


HEAD_VB = (-152, -100, 304, 198)   # x, y, w, h in head-local units; symmetric so the face is centred,
                                    # with room for the sparks at the top corners


def head_svg(mood):
    return svg(' '.join(str(v) for v in HEAD_VB), head(mood))


# ---------- bodies ----------
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


def patch(x, y, w, h, rot, fill):
    """A square patch sewn on, with a stitched border."""
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)})">'
            f'<rect x="{f(-w/2)}" y="{f(-h/2)}" width="{f(w)}" height="{f(h)}" rx="3" fill="{fill}" stroke="{OUT}" stroke-width="4"/>'
            f'<rect x="{f(-w/2+5)}" y="{f(-h/2+5)}" width="{f(w-10)}" height="{f(h-10)}" rx="1.5" fill="none" '
            f'stroke="{STITCH}" stroke-width="2.4" stroke-dasharray="4 4" opacity="0.85"/></g>')


def scratch(x, y, s=1.0):
    """Two little tear marks."""
    return (f'<path d="M{f(x)},{f(y)} l{f(-7*s)},{f(14*s)} M{f(x+9*s)},{f(y+2*s)} l{f(-7*s)},{f(14*s)}" '
            f'stroke="{TEAR}" stroke-width="3.6" fill="none"/>')


def zig(x0, x1, y, amp, n, jitter):
    """Ragged edge from x0 to x1 around height y: n teeth, `jitter` = per-point extra drop."""
    out = []
    for i in range(2 * n + 1):
        x = x0 + (x1 - x0) * i / (2 * n)
        dy = (amp if i % 2 else 0) + jitter[i % len(jitter)]
        out.append((x, y + dy))
    return out


# Stage geometry, in head-local units with the head at 0,0 scale 1 (the head covers the neck down to y~70).
#  hw: half body width (fur)   yb: soles   foot: (x, rx, ry)
#  shirt: shoulder (shx, shy), sleeve outer edge at its hem (so, sl), armpit at the sleeve hem (si),
#         half width at the belly (sh), hem height (hem)   ab: bottom of the paws
STAGE = {
    # baby: a round little puppy lost in a rag that's far too big (hangs to the feet, sleeves over the paws)
    1: dict(hw=72, yb=186, foot=(30, 24, 13), shx=86, shy=96, so=118, sl=152, si=82, sh=98, hem=158, ab=0, k=0.72, n=6),
    2: dict(hw=98, yb=250, foot=(40, 30, 16), shx=84, shy=92, so=128, sl=152, si=88, sh=104, hem=198, ab=204, k=0.86, n=7),
    3: dict(hw=116, yb=296, foot=(46, 34, 17), shx=98, shy=96, so=146, sl=170, si=104, sh=122, hem=232, ab=232, k=1.0, n=8),
}


def standing(st):
    g = STAGE[st]
    hw, yb, k = g['hw'], g['yb'], g['k']
    fx, frx, fry = g['foot']
    shx, shy, so, sl, si, sh, hem, ab = (g[n] for n in ('shx', 'shy', 'so', 'sl', 'si', 'sh', 'hem', 'ab'))
    baby = st == 1
    gy = yb + 10
    p = []
    p.append(grass(0, gy, max(hw, sh) + 34, 17, [(-max(hw, sh) - 26, gy + 4, 0.85), (max(hw, sh) + 8, gy + 2, 0.95), (max(hw, sh) - 6, gy + 12, 0.6)]))
    # feet
    for s in (-1, 1):
        cx = s * fx
        p.append(f'<ellipse cx="{f(cx)}" cy="{f(yb)}" rx="{frx}" ry="{fry}" fill="{FUR}" stroke="{OUT}" stroke-width="{SW}"/>')
        p.append(f'<path d="M{f(cx-7)},{f(yb+fry)} L{f(cx-7)},{f(yb+fry-8)} M{f(cx+7)},{f(yb+fry)} L{f(cx+7)},{f(yb+fry-8)}" stroke="{OUT}" stroke-width="3.5"/>')
    # chubby body: a pear from the neck down to just above the soles
    h = yb - 6 - 40
    body = sym((0, 44), [((28, 44), (52, 50), (58, 74)),
                         ((66, 90), (hw * 1.02, 40 + h * 0.28), (hw * 1.03, 40 + h * 0.55)),
                         ((hw * 1.04, 40 + h * 0.85), (hw * 0.6, yb - 4), (0, yb - 4))])
    p.append(f'<clipPath id="bc"><path d="{body}"/></clipPath>')
    p.append(f'<path d="{body}" fill="{FUR}"/>')
    p.append(f'<path d="M-200,{f(yb-30)} C-60,{f(yb-10)} 60,{f(yb-10)} 200,{f(yb-30)} L200,400 L-200,400 Z" fill="{FUR_SH}" opacity="0.55" clip-path="url(#bc)"/>')
    p.append(f'<path d="{body}" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    # stubby arms hanging a little outwards, the paws poking out of the sleeves
    for s in ((-1, 1) if ab else ()):
        it, ot = s * (shx - 14 * k), s * (shx + 6 * k)          # top (hidden in the sleeve)
        ib, ob = s * (si + 2 * k), s * (so - 2 * k)              # at the sleeve hem
        pw = abs(ob - ib)
        d = (f'M{f(it)},{f(shy+10)} L{f(ot)},{f(shy+6)} L{f(ob)},{f(sl)} '
             f'C{f(ob+s*2)},{f(ab-8)} {f(ob-s*pw*0.25)},{f(ab)} {f((ib+ob)/2)},{f(ab)} '
             f'C{f(ib+s*pw*0.2)},{f(ab)} {f(ib-s*2)},{f(ab-8)} {f(ib)},{f(sl)} Z')
        p.append(f'<path d="{d}" fill="{FUR}" stroke="{OUT}" stroke-width="{SW}"/>')
        px = (ib + ob) / 2
        p.append(f'<path d="M{f(px-5)},{f(ab)} L{f(px-5)},{f(ab-7)} M{f(px+5)},{f(ab)} L{f(px+5)},{f(ab-7)}" stroke="{OUT}" stroke-width="3.2"/>')
    # the rag shirt: one piece with a ragged collar, sleeves and hem
    collar = [(-64, 66), (-52, 82), (-40, 72), (-28, 90), (-14, 78), (0, 92), (14, 78), (28, 90), (40, 72), (52, 82), (64, 66)]
    sw_ = so - si
    sleeve_r = [(so, sl), (so - sw_ * 0.22, sl + 14 * k), (so - sw_ * 0.4, sl + 3), (so - sw_ * 0.62, sl + 17 * k),
                (so - sw_ * 0.8, sl + 4), (si, sl + 12 * k)]
    hem_pts = zig(sh * 0.95, -sh * 0.95, hem, 18 * max(k, 0.85), g['n'], [0, 3, -2, 5, 1, -3, 4])
    d = f'M{pts(collar[-1:])}'
    d += f' C{pts([(shx * 0.85, 64), (shx, shy - 14), (shx, shy)])}'
    d += f' C{pts([(shx + (so - shx) * 0.5, shy + 18), (so, sl - (sl - shy) * 0.45), (so, sl)])}'
    d += ' L' + pts(sleeve_r[1:])
    d += f' C{pts([(si + (sh - si) * 0.6, sl + 30 * k), (sh, hem - 40 * k), (sh * 0.95, hem)])}'
    d += ' L' + pts(hem_pts[1:])
    sleeve_l = [(-x, y + (3 if i % 2 else 0)) for i, (x, y) in enumerate(reversed(sleeve_r))]
    d += f' C{pts([(-sh, hem - 40 * k), (-si - (sh - si) * 0.6, sl + 30 * k), sleeve_l[0]])}'
    d += ' L' + pts(sleeve_l[1:])
    d += f' C{pts([(-so, sl - (sl - shy) * 0.45), (-shx - (so - shx) * 0.5, shy + 18), (-shx, shy)])}'
    d += f' C{pts([(-shx, shy - 14), (-shx * 0.85, 64), collar[0]])}'
    d += ' L' + pts(collar[1:]) + ' Z'
    p.append(f'<clipPath id="sc"><path d="{d}"/></clipPath>')
    p.append(f'<path d="{d}" fill="{RAG}"/>')
    p.append('<g clip-path="url(#sc)">')
    # light from the top-left: darker on the right and along the hem
    p.append(f'<path d="M{f(sh*0.45)},40 C{f(sh*0.85)},{f(shy+40)} {f(sh*0.8)},{f(hem-30)} {f(sh*0.35)},{f(hem+30)} L300,{f(hem+30)} L300,40 Z" fill="{RAG_SH}" opacity="0.45"/>')
    p.append(f'<path d="M-300,{f(hem-4)} C-100,{f(hem-22)} 100,{f(hem-22)} 300,{f(hem-4)} L300,{f(hem+40)} L-300,{f(hem+40)} Z" fill="{RAG_SH}" opacity="0.45"/>')
    p.append(f'<path d="M{f(-sh*0.5)},{f(shy+22)} C{f(-sh*0.6)},{f(shy+50)} {f(-sh*0.6)},{f(sl)} {f(-sh*0.52)},{f(sl+22*k)}" stroke="{RAG_HI}" stroke-width="7" fill="none"/>')
    # seams where the sleeves meet the body, from the armpit up into the shoulder
    for s in (-1, 1):
        p.append(f'<path d="M{f(s*(shx-6))},{f(shy+4)} C{f(s*(shx-8))},{f(shy+30)} {f(s*(si-4))},{f(sl-24)} {f(s*si)},{f(sl+4)}" '
                 f'stroke="{OUT}" stroke-width="4.5" fill="none"/>')
    p.append('</g>')
    p.append(f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="{SW}"/>')
    # wear and tear: scratch marks and sewn-on patches
    p.append(scratch(-sh * 0.36, shy + 26 * k, k))
    p.append(scratch(sh * 0.08, hem - 46 * k, k * 0.9))
    p.append(patch(sh * 0.5, shy + 22 * k, 30 * k + 4, 28 * k + 4, 38, PATCH_D))
    p.append(patch(-sh * 0.5, hem - 30 * k, 36 * k + 4, 32 * k + 4, 10, PATCH_L if not baby else PATCH_D))
    if not baby:
        p.append(patch(sh * 0.42, hem - 34 * k, 26 * k + 4, 24 * k + 4, -14, PATCH_L))
    else:
        p.append(patch(so - sw_ * 0.5, sl - 22, 22, 20, -12, PATCH_L))
    gx = max(hw, sh) + 34
    return ''.join(p), (gx, gy + 17)


STAGE_HEAD = {1: (0, 0, 1.0), 2: (0, 0, 1.04), 3: (0, 0, 1.08)}   # translate(x y) scale(s) of the head


def body_vb(st):
    """Tight viewBox around the body, the grass and the (scaled) head image."""
    _, (gx, gb) = standing(st)
    hs = STAGE_HEAD[st][2]
    x0 = min(HEAD_VB[0] * hs, -gx - 4)
    w = max((HEAD_VB[0] + HEAD_VB[2]) * hs, gx + 4) - x0
    y0 = HEAD_VB[1] * hs
    x0, y0 = math.floor(x0), math.floor(y0)
    return (x0, y0, math.ceil(w), math.ceil(gb + 3 - y0))


STAGES = {st: body_vb(st) for st in (1, 2, 3)}


def anchor(stage):
    """Head image box on the body image, in % of the body image (x/y = top-left, w = width)."""
    bx, by, bw, bh = STAGES[stage]
    hx, hy, hs = STAGE_HEAD[stage]
    vx, vy, vw, vh = HEAD_VB
    return {
        'x': round((hx + vx * hs - bx) / bw * 100, 2),
        'y': round((hy + vy * hs - by) / bh * 100, 2),
        'w': round(vw * hs / bw * 100, 2),
        'r': 0,
    }


INDEX_JS = """// The ragged dog pet (Cún Khố Rách): a body per growth stage (no head) + a head per mood, put together by PetArt.vue.
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


if __name__ == '__main__':
    for st, vb in STAGES.items():
        write(f'body-{st}.svg', svg(' '.join(f(v) for v in vb), standing(st)[0]))
    for mood in MOODS:
        write(f'head-{mood}.svg', head_svg(mood))
    anchors = ', '.join('{ x: %s, y: %s, w: %s, r: %s }' % tuple(('%.2f' % anchor(st)[c]).rstrip('0').rstrip('.') for c in 'xywr') for st in STAGES)
    body_sizes = ', '.join(f'[{f(vb[2])}, {f(vb[3])}]' for vb in STAGES.values())
    write('index.js', INDEX_JS.replace('ANCHORS', anchors).replace('BODYSIZES', body_sizes)
          .replace('HEADSIZE', f'[{HEAD_VB[2]}, {HEAD_VB[3]}]'))
    print('ok', anchors, body_sizes)
