"""Renders every asset in ../assets. Usage: python3 build.py [name ...]"""
import sys, os, math
from engine import *
from motifs import *
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
V, B_ = C['violet'], C['blue']
def GL(a=1): return [(.02, 1.06, .17, -.06, .34, 0, V), (.985, -.06, .86, 1.06, .3, .5, B_)] if a == 1 else [(.5, -.06, .64, 1.06, .26, .3, B_)]
def sec(eb, lines, y=88, size=34, x=60):
    it = [dict(t=eb, x=x + 2, y=y - 34, w='Medium', size=14, track=5, col=C['cyan'])]
    for i, l in enumerate(lines): it.append(dict(t=l, x=x, y=y + i * (size + 10), w='Bold', size=size, track=3))
    return it
def sc(W, H, seed, sun=(.86, .55), fig=None, peaks=(), glass=None, npart=40, **k):
    return Scene(W, H, seed=seed, sun=sun, peaks=peaks, fig=fig, glass=GL(1) if glass is None else glass, npart=npart, **k)
def trail(s, W, H, y0, y1, col=None, ph=0):
    s.add_trail(bezier((0, y0 * H), (.3 * W, y1 * H), (.7 * W, y0 * H), (W, y1 * H)), col or C['cyan'], .2, ph, 2.5)
def P(sub, name): return os.path.join(R, sub, name)

def card_glyph(o, k, x, y, t):
    s = 100; b = pulse(t, k * .2, .1)
    o.rect(x - s, y - s, x + s, y + s, C['indigo'], 110 + 100 * b, 14, C['cyan'] if b < .4 else C['gold'], 130 + 125 * b, 2)
    o.text(f"{7+k:02d}", x - s + 14, y - s + 8, 'Medium', 13, C['white'], 200, 3)
    if k == 0:   # uniconv: swapping arrows between two docs
        for dx in (-45, 45): o.rect(x + dx - 22, y - 28, x + dx + 22, y + 28, C['navy'], 255, 4, C['white'], 200, 2)
        sh = 8 * math.sin(2 * math.pi * t); o.line([(x - 18, y - 4 + sh), (x + 18, y - 4 + sh)], C['cyan'], 3); o.line([(x + 18, y + 10 - sh), (x - 18, y + 10 - sh)], C['gold'], 3)
    if k == 1:   # neet: rising bars + rank line
        for i in range(5): hh = 18 + i * 12 + 6 * math.sin(2 * math.pi * (t + i * .1)); o.rect(x - 52 + i * 22, y + 40 - hh, x - 36 + i * 22, y + 40, C['violet'], 230, 2, C['cyan'], 255, 1.5)
        o.line([(x - 50, y + 22), (x - 20, y + 4), (x + 10, y - 6), (x + 54, y - 34)], C['gold'], 3)
    if k == 2:   # event flow: 4-state flow
        for i in range(4):
            b2 = pulse(t, i / 4, .1); o.circ(x - 54 + i * 36, y, 11, C['indigo'], 255, C['gold'] if b2 > .3 else C['cyan'], 255, 2.5)
            if i < 3: o.line([(x - 42 + i * 36, y), (x - 30 + i * 36, y)], C['white'], 2, 160)
    if k == 3:   # cartfill: cart with dropping item
        o.line([(x - 52, y - 30), (x - 38, y - 30), (x - 28, y + 20), (x + 38, y + 20), (x + 48, y - 14), (x - 36, y - 14)], C['cyan'], 3)
        o.circ(x - 20, y + 36, 6, None, 255, C['white'], 255, 2); o.circ(x + 28, y + 36, 6, None, 255, C['white'], 255, 2)
        dy = (t % 1) * 44; o.rect(x - 8, y - 56 + dy, x + 12, y - 36 + dy, C['gold'], 255 * (1 - (t % 1) ** 3), 3)
    if k == 4:   # reliefchain: linked chain
        for i in range(4): b2 = pulse(t, i / 4, .1); o.rect(x - 62 + i * 32, y - 12, x - 34 + i * 32, y + 12, None, 255, 12, C['gold'] if b2 > .3 else C['cyan'], 255, 3)

def m_toolkit(o, t):
    W, H = o.W, o.H; names = ['LANGUAGES', 'FRONTEND', 'BACKEND', 'DATABASES + ORM', 'AI + EDGE', 'ENGINEERING', 'CREATIVE TOOLS']
    labels = ['LANGUAGES', 'FRONTEND', 'BACKEND', 'DATABASES + ORM', 'AI + EDGE', 'ENGINEERING + PRODUCT']
    pw, ph_ = 330, 112; gx = (W - 3 * pw) / 4
    for i in range(6):
        c, r = i % 3, i // 3; x = gx + c * (pw + gx); y = .27 * H + r * (ph_ + 26) + 6 * math.sin(2 * math.pi * (t + i * .13))
        o.rect(x, y, x + pw, y + ph_, C['indigo'], 105, 14, C['blue'], 120, 2); o.text(f"0{i+1}", x + 22, y + 18, 'Light', 38, C['violet'], 255, 2)
        o.text(labels[i], x + 22, y + 72, 'Medium', 15, C['white'], 235, 3)
        per = 2 * (pw + ph_); p = ((t + i * .17) % 1) * per
        def pp(q):
            q %= per
            if q < pw: return (x + q, y)
            if q < pw + ph_: return (x + pw, y + q - pw)
            if q < 2 * pw + ph_: return (x + pw - (q - pw - ph_), y + ph_)
            return (x, y + ph_ - (q - 2 * pw - ph_))
        for k in range(18): o.line([pp(p - k * 6), pp(p - (k + 1) * 6)], C['cyan'] if i % 2 else C['gold'], 3 * (1 - k / 18) + .5, 255 * (1 - k / 18))
    o.text('CREATIVE TOOLS  •  VIDEO EDITING  •  MOTION GRAPHICS', W / 2, .9 * H, 'Medium', 13, C['white'], 180, 4, 'c')

def m_education(o, t):
    W, H = o.W, o.H; pts = [(.5 * W, .78 * H), (.7 * W, .6 * H), (.9 * W, .38 * H)]; labs = ['SSLC', 'PUC', 'B.E.']
    o.line(pts, C['gold'], 2, 120)
    for i, (x, y) in enumerate(pts):
        a = float(smooth(np.array(t), .02 + i * .26, .16 + i * .26)) * float(1 - smooth(np.array(t), .93, 1.0)); w = 80
        for z in range(3):
            o.poly([(x - w, y + z * 4), (x, y - 30 + z * 4), (x + w, y + z * 4), (x, y + 30 + z * 4)], C['indigo'], 200 * a if z else 0, C['cyan'], 170 * a, 2)
        o.poly([(x - w, y), (x, y - 30), (x + w, y), (x, y + 30)], C['violet'], 70 * a, C['white'], 230 * a, 2)
        r = 20 + 70 * float(smooth(np.array(t), .06 + i * .26, .3 + i * .26)); o.circ(x, y, r, None, 255, C['gold'], 160 * a * (1 - r / 100), 2)
        o.text(labs[i], x, y + 42, 'Bold', 17, C['white'], 255 * a, 4, 'c')

def m_trophy(o, t):
    W, H = o.W, o.H; cx, cy = .66 * W, .5 * H; sw = (t * 1.4) % 1.4
    bowl = [(cx - 58, cy - 90), (cx + 58, cy - 90), (cx + 48, cy - 25), (cx + 14, cy + 2), (cx - 14, cy + 2), (cx - 48, cy - 25)]
    for sx in (-1, 1): o.line([(cx + sx * 56, cy - 80), (cx + sx * 86, cy - 74), (cx + sx * 80, cy - 40), (cx + sx * 44, cy - 28)], C['gold'], 6, 255)
    o.poly(bowl, C['gold'], 245, C['white'], 200, 2); o.rect(cx - 10, cy + 2, cx + 10, cy + 44, C['gold'], 245, 2); o.rect(cx - 44, cy + 44, cx + 44, cy + 66, C['gold'], 245, 4, C['white'], 180, 2)
    o.poly([(cx - 44 + 100 * (sw - .2), cy - 90), (cx - 44 + 100 * (sw - .2) + 18, cy - 90), (cx - 44 + 100 * (sw - .2) + 4, cy + 2), (cx - 44 + 100 * (sw - .2) - 14, cy + 2)], C['white'], 120 * (sw < 1.2))
    for i in range(7):
        c, r = i // 4, i % 4; x = .06 * W + c * .27 * W; y = .22 * H + r * .17 * H; w, h = .25 * W, .13 * H
        if c == 1 and r == 3: continue
        b = pulse(t, i / 7, .08); o.rect(x, y, x + w, y + h, C['indigo'], 100 + 110 * b, 10, C['gold'], 110 + 145 * b, 2)
        o.text(f"0{i+1}", x + 16, y + h / 2 - 12, 'Light', 24, C['gold'], 255); o.line([(x + 66, y + h / 2), (x + w - 22, y + h / 2)], C['white'], 2, 60 + 140 * b)
        o.circ(x + w - 22, y + h / 2, 4, C['gold'], 150 + 105 * b)

def m_git(o, t):
    W, H = o.W, o.H; rows = [.35 * H, .55 * H, .75 * H]; xs = np.linspace(.42 * W, .94 * W, 9)
    o.line([(xs[0], rows[1]), (xs[8], rows[1])], C['cyan'], 2, 140)
    for r, a, b in ((0, 1, 5), (2, 3, 7)):
        o.line([(xs[a], rows[1]), (xs[a] + 30, rows[r]), (xs[b] - 30, rows[r]), (xs[b], rows[1])], C['violet'], 2, 140)
    nodes = [(xs[i], rows[1]) for i in range(9)] + [(xs[i], rows[0]) for i in (2, 3, 4)] + [(xs[i], rows[2]) for i in (4, 5, 6)]
    for k, (x, y) in enumerate(nodes): b = pulse(t, (x - xs[0]) / (xs[8] - xs[0]) * .9, .09); o.circ(x, y, 8, C['indigo'], 255, C['gold'] if b > .4 else C['cyan'], 255, 2.5); o.circ(x, y, 3, C['white'], 120 + 135 * b)
    glow_path(o, [(xs[0], rows[1]), (xs[8], rows[1])], t, .25, C['gold'], 5)

def m_experience(o, t):
    W, H = o.W, o.H; x0, y0, x1, y1 = .44 * W, .2 * H, .95 * W, .72 * H; b = .5 + .5 * math.sin(2 * math.pi * t)
    o.rect(x0 - 8, y0 - 8, x1 + 8, y1 + 8, None, 255, 18, C['violet'], 60 + 60 * b, 2)
    o.rect(x0, y0, x1, y1, C['indigo'], 150, 14, C['cyan'], 200, 2.5)
    p = x0 - 120 + (x1 - x0 + 240) * t; cl = lambda x: max(x0 + 2, min(x1 - 2, x))
    o.poly([(cl(p), y0 + 2), (cl(p + 70), y0 + 2), (cl(p + 10), y1 - 2), (cl(p - 60), y1 - 2)], C['white'], 55)
    cx = (x0 + x1) / 2; o.text('CHIEF OPERATING OFFICER', cx, y0 + 52, 'Medium', 19, C['cyan'], 255, 5, 'c')
    o.line([(cx - 60, y0 + 92), (cx + 60, y0 + 92)], C['gold'], 2, 220)
    o.text('VOVALYX', cx, y0 + 108, 'Bold', 52, C['white'], 255, 8, 'c')
    o.text('COO  •  2026', cx, y1 - 38, 'Light', 15, C['white'], 190, 4, 'c') if False else None

JOBS = {}
def job(f): JOBS[f.__name__] = f; return f

@job
def hero():
    W, H = 1600, 500
    s = Scene(W, H, seed=7, sun=(.86, .52), peaks=[(4, .82, .40, .15), (3, .76, .2, .22)], fig=(.82, .19), npart=50,
              glass=[(.015, 1.08, .17, -.08, .3, 0, V), (.54, -.08, .665, 1.0, .3, .2, B_), (.795, -.08, .66, 1.0, .3, .55, V)])
    s.add_trail(bezier((0, 430), (400, 300), (900, 420), (1600, 250)), C['cyan'], .18, 0, 2.5)
    s.add_trail(bezier((0, 470), (500, 380), (1000, 470), (1600, 330)), C['gold'], .14, .5, 2)
    t = [dict(t='VISHESH G DEVANUR', x=200, y=115, w='Bold', size=40, track=3), dict(t='COO  •  VOVALYX', x=202, y=170, w='Regular', size=19, track=5),
         dict(t='Code  •  Create  •  Inspire', x=202, y=228, w='Light', size=20, track=3, col=C['cyan'])]
    render_asset(P('hero', 'hero-creative-developer.gif'), s, W, H, 36, texts=t, dur=80)

@job
def about():
    W, H = 1200, 400; s = sc(W, H, 11, sun=(.7, .55), peaks=[(2, .6, .12, .3)], glass=[(.02, 1.06, .17, -.06, .34, 0, V), (.9, -.06, .78, 1.06, .3, .5, B_), (.5, -.06, .6, 1.06, .22, .25, V)])
    trail(s, W, H, .85, .6); render_asset(P('sections', 'about.gif'), s, W, H, 30, texts=sec('01  —  INTRODUCTION', ['ABOUT ME'], 150, 46))

@job
def capabilities():
    W, H = 1200, 300; s = sc(W, H, 12, sun=(.5, .6), glass=GL(1)); trail(s, W, H, .85, .6)
    render_asset(P('sections', 'capabilities.gif'), s, W, H, 30, texts=sec('02  —  CAPABILITIES', ['WHAT I DO'], 100, 46))

def cap(name, seed, motif, sun):
    def f():
        W, H = 600, 340; s = sc(W, H, seed, sun=sun, npart=25, glass=GL(2)); render_asset(P('capabilities', name + '.gif'), s, W, H, 30, overlay=motif, colors=96)
    return f
JOBS['cap_product'] = cap('product-engineering', 21, m_product, (.2, .55))
JOBS['cap_stack'] = cap('full-stack-development', 22, m_layers, (.8, .5))
JOBS['cap_edge'] = cap('edge-ai', 23, lambda o, t: m_chip(o, t, 300, 170, 40, [(30, 40, 100, 62, None), (470, 40, 100, 62, None), (30, 240, 100, 62, None), (470, 240, 100, 62, None)], True), (.5, .5))
JOBS['cap_creative'] = cap('creative-technology', 24, m_creative, (.5, .45))

@job
def experience():
    W, H = 1200, 440; s = sc(W, H, 13, sun=(.2, .55), peaks=[(3, .78, .25, .25)], glass=[(.02, 1.06, .17, -.06, .3, 0, V), (.3, -.06, .38, 1.06, .2, .5, B_)])
    render_asset(P('sections', 'experience.gif'), s, W, H, 30, overlay=m_experience, texts=sec('03  —  EXPERIENCE', ['PROFESSIONAL', 'EXPERIENCE'], 140, 38))

def proj(fn, num, lines, seed, motif, sun=(.3, .55)):
    def f():
        W, H = 1200, 420; s = sc(W, H, seed, sun=sun, peaks=[(3, .2, .15, .25)]); trail(s, W, H, .85, .65)
        sz = 36 if len(max(lines, key=len)) < 16 else 30
        render_asset(P('projects', fn + '.gif'), s, W, H, 30, overlay=motif, texts=sec(f'PROJECT  {num:02d}', lines, 150 if len(lines) > 1 else 170, sz), colors=112)
    return f
def _pw(o, t): m_network(o, t, *placepro_nodes(o.W, o.H), 'person')
def _mr(o, t): m_network(o, t, *mrf_nodes(o.W, o.H), 'hex')
JOBS['p1'] = proj('no-due-portal', 1, ['NO-DUE', 'PORTAL'], 31, m_workflow)
JOBS['p2'] = proj('acadops-erp', 2, ['ACADOPS', 'ERP'], 32, m_modules)
JOBS['p3'] = proj('mitm-placepro', 3, ['MITM', 'PLACEPRO'], 33, _pw)
JOBS['p4'] = proj('mrf-platform', 4, ['MRF RESEARCH', 'ADMINISTRATION', 'PLATFORM'], 34, _mr)
JOBS['p5'] = proj('enils', 5, ['ENILS'], 35, lambda o, t: m_chip(o, t, .72 * o.W, .5 * o.H, 62, [(.46 * o.W, .66 * o.H, 110, 66, None)], True))
JOBS['p6'] = proj('disaster-management', 6, ['DISASTER', 'MANAGEMENT'], 36, m_terrain)

@job
def additional():
    W, H = 1200, 330; s = sc(W, H, 41, sun=(.5, .6), npart=30, glass=GL(2))
    render_asset(P('projects', 'additional-projects.gif'), s, W, H, 30, overlay=lambda o, t: [card_glyph(o, k, 120 + k * 240, 175, t) for k in range(5)], texts=sec('MORE  WORK', ['ADDITIONAL PROJECTS'], 42, 20, 40), colors=112)

@job
def edge_ai():
    W, H = 1200, 540; s = sc(W, H, 51, sun=(.5, .6), peaks=[(3, .5, .1, .3)], npart=60)
    dv = [(60, 120, 150, 92, 'EDGE NODE 01'), (60, 390, 150, 92, 'EDGE NODE 02'), (990, 120, 150, 92, 'EDGE NODE 03'), (990, 390, 150, 92, 'EDGE NODE 04')]
    render_asset(P('sections', 'edge-ai.gif'), s, W, H, 32, overlay=lambda o, t: m_chip(o, t, 600, 290, 86, dv, True, True), texts=sec('EDGE AI', ['LOCAL INTELLIGENCE'], 38, 28, 60), colors=112)

@job
def toolkit():
    W, H = 1200, 420; s = sc(W, H, 61, sun=(.5, .6), npart=40, glass=GL(2))
    render_asset(P('sections', 'technology-toolkit.gif'), s, W, H, 30, overlay=m_toolkit, texts=sec('TECHNOLOGY', ['TOOLKIT'], 38, 28, 60), colors=112)

@job
def education():
    W, H = 1200, 400; s = sc(W, H, 71, sun=(.88, .45), peaks=[(3, .8, .2, .3)], glass=GL(2))
    render_asset(P('sections', 'education.gif'), s, W, H, 30, overlay=m_education, texts=sec('EDUCATION', ['ACADEMIC JOURNEY'], 150, 34), colors=112, static_t=.8)

@job
def achievements():
    W, H = 1200, 420; s = sc(W, H, 81, sun=(.66, .5), npart=45, glass=GL(2))
    render_asset(P('sections', 'achievements.gif'), s, W, H, 30, overlay=m_trophy, texts=[dict(t='ACHIEVEMENTS', x=60, y=18, w='Bold', size=22, track=5)], colors=112)

@job
def github():
    W, H = 1200, 240; s = sc(W, H, 91, sun=(.2, .6), npart=30, glass=GL(2))
    render_asset(P('sections', 'github.gif'), s, W, H, 30, overlay=m_git, texts=sec('OPEN SOURCE', ['GITHUB'], 90, 40), colors=96)

@job
def contact():
    W, H = 1200, 440; s = Scene(W, H, seed=101, sun=(.7, .52), peaks=[(4, .72, .36, .16), (3, .66, .18, .22)], fig=(.72, .17), npart=45,
                               glass=[(.02, 1.06, .17, -.06, .3, 0, V), (.96, -.06, .83, 1.06, .3, .5, B_)])
    for i, ph in enumerate((0, .33, .66)): s.add_trail(bezier((0, (.9 - i * .1) * H), (.3 * W, (.5 + i * .1) * H), (.55 * W, (.7 - i * .1) * H), (.72 * W, .62 * H)), [C['cyan'], C['violet'], C['gold']][i], .2, ph, 2.5)
    t = [dict(t="LET'S BUILD", x=60, y=130, w='Bold', size=38, track=4), dict(t='SOMETHING', x=60, y=182, w='Bold', size=38, track=4), dict(t='MEANINGFUL.', x=60, y=234, w='Bold', size=38, track=4, col=C['cyan'])]
    render_asset(P('sections', 'contact.gif'), s, W, H, 32, texts=t)

if __name__ == '__main__':
    names = sys.argv[1:] or list(JOBS)
    for n in names: JOBS[n](); print('done', n, flush=True)
