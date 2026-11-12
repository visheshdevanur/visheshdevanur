import math, numpy as np
from engine import *

def m_workflow(o, t):
    W, H = o.W, o.H; x0, x1, cy, am = .42 * W, .95 * W, .55 * H, .14 * H
    xs = np.linspace(x0, x1, 80); ys = cy + am * np.sin((xs - x0) / (x1 - x0) * 2 * math.pi * .9 + .5)
    path = list(zip(xs, ys)); o.line(path, C['blue'], 5, 70); o.line(path, C['cyan'], 1.5, 160)
    for i, ix in enumerate([0, 20, 40, 60, 79]):
        x, y = path[ix]; b = pulse(t, ix / 79, .09)
        o.rect(x - 40, y - 78, x + 40, y + 34, C['indigo'], 90 + 110 * b, 10, C['cyan'] if b < .5 else C['gold'], 120 + 135 * b, 2)
        o.text(f"0{i+1}", x, y - 66, 'Medium', 13, C['white'], 150 + 100 * b, 2, 'c')
        for k in range(3): o.line([(x - 22, y - 40 + k * 12), (x + 22 - k * 8, y - 40 + k * 12)], C['white'], 2, 70 + 120 * b)
        o.circ(x, y, 8, C['white'] if b > .3 else C['cyan'], 255, C['violet'], 255, 2)
    glow_path(o, path, t, .22, C['gold'], 5)

def m_modules(o, t):
    W, H = o.W, o.H; cx, cy = .7 * W, .52 * H
    mods = [(cx + math.cos(a) * .27 * W, cy + math.sin(a) * .36 * H) for a in [i * math.pi / 4 + math.pi / 8 for i in range(8)]]
    for i, (x, y) in enumerate(mods):
        b = pulse(t, i / 8, .07); o.line([(cx, cy), (x, y)], C['violet'], 1.5, 70 + 150 * b)
    d = 44 + 3 * math.sin(2 * math.pi * t)
    o.poly([(cx, cy - d), (cx + d * 1.4, cy), (cx, cy + d), (cx - d * 1.4, cy)], C['indigo'], 200, C['cyan'], 255, 2)
    o.poly([(cx, cy - d * .5), (cx + d * .7, cy), (cx, cy + d * .5), (cx - d * .7, cy)], C['blue'], 200, C['white'], 200, 1.5)
    for i, (x, y) in enumerate(mods):
        b = pulse(t, i / 8, .07)
        o.rect(x - 40, y - 26, x + 40, y + 26, C['indigo'], 100 + 120 * b, 8, C['cyan'] if b < .4 else C['gold'], 130 + 125 * b, 2)
        for k in range(3): o.line([(x - 24, y - 12 + k * 12), (x + 24 - k * 10, y - 12 + k * 12)], C['white'], 2, 80 + 150 * b)

def m_network(o, t, nodes, edges, shape='dot', hub=None):
    for k, (a, b_) in enumerate(edges):
        A, B = nodes[a], nodes[b_]; o.line([A, B], C['violet'], 1.5, 85)
        s = (t + k * .137) % 1; px, py = A[0] + (B[0] - A[0]) * s, A[1] + (B[1] - A[1]) * s
        o.line([(A[0] + (B[0] - A[0]) * max(0, s - .18), A[1] + (B[1] - A[1]) * max(0, s - .18)), (px, py)], C['cyan'], 3, 230); o.circ(px, py, 3.5, C['white'])
    for k, (x, y) in enumerate(nodes):
        b = .5 + .5 * math.sin(2 * math.pi * (t + k * .11)) ** 2
        if shape == 'person' and k % 2 == 0:
            o.circ(x, y - 12, 8, C['indigo'], 255, C['cyan'], 120 + 130 * b, 2); o.poly([(x - 16, y + 12), (x - 10, y - 1), (x + 10, y - 1), (x + 16, y + 12)], C['indigo'], 255, C['cyan'], 120 + 130 * b, 2)
        elif shape == 'hex':
            o.poly([(x + 16 * math.cos(a * math.pi / 3), y + 16 * math.sin(a * math.pi / 3)) for a in range(6)], C['indigo'], 230, C['cyan'] if k % 3 else C['gold'], 120 + 135 * b, 2); o.circ(x, y, 3, C['white'], 120 + 130 * b)
        else:
            o.circ(x, y, 9, C['indigo'], 255, C['gold'], 120 + 135 * b, 2); o.circ(x, y, 3.5, C['white'], 150 + 100 * b)

def placepro_nodes(W, H):
    hub = (.74 * W, .52 * H); nodes = [hub]; edges = []
    for i in range(5): a = math.pi * (.65 + i * .175); nodes.append((hub[0] - .22 * W * (-math.cos(a)) * -1 - 0, hub[1] + math.sin(a) * .34 * H)); 
    nodes = [hub] + [(.5 * W + i * .0 * W, (.22 + i * .14) * H) for i in range(5)] + [(.93 * W, (.25 + i * .25) * H) for i in range(3)]
    edges = [(0, i) for i in range(1, 9)] + [(1, 2), (2, 3), (3, 4), (4, 5)]
    return nodes, edges
def mrf_nodes(W, H):
    nodes = []; 
    for r in range(5):
        for c in range(6): nodes.append((.47 * W + c * .09 * W + (r % 2) * .045 * W, (.18 + r * .16) * H))
    edges = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if math.dist(nodes[i], nodes[j]) < .105 * W and (i * 7 + j * 3) % 3: edges.append((i, j))
    return nodes, edges

def board(o, x, y, w, h, b, label=None):
    o.rect(x, y, x + w, y + h, C['graphite'], 245, 8, C['cyan'], 110 + 140 * b, 2)
    o.rect(x + w * .38, y + h * .3, x + w * .62, y + h * .62, C['indigo'], 255, 3, C['gold'], 120 + 130 * b, 2)
    for k in range(10): o.circ(x + w * .1 + k * w * .08, y + 7, 1.8, C['gold'], 200); o.circ(x + w * .1 + k * w * .08, y + 15, 1.8, C['gold'], 200)
    o.rect(x + w - 14, y + h * .72, x + w, y + h - 6, C['white'], 120, 2); o.rect(x + w - 14, y + h * .3, x + w, y + h * .55, C['white'], 120, 2)
    if label: o.text(label, x + w / 2, y + h + 5, 'Medium', 11, C['white'], 170, 1.5, 'c')

def m_chip(o, t, cx, cy, s=64, devices=(), neural=True, labels=False):
    W, H = o.W, o.H
    if neural:
        cols = [[(cx + (c - 1.5) * s * 3.2, cy + (r - 2) * s * .95) for r in range(5)] for c in range(4)]
        for c in range(3):
            for i, a in enumerate(cols[c]):
                for j, b in enumerate(cols[c + 1]):
                    if (i + j + c) % 2 == 0: o.line([a, b], C['violet'], 1, 38)
        for k, (c, i) in enumerate([(c, i) for c in range(4) for i in range(5)]): o.circ(*cols[c][i], 3, C['violet'], 60 + 110 * pulse(t, (c * .2 + i * .04), .1))
    for i, (x, y, w, h, lab) in enumerate(devices):
        dx, dy = x + w / 2, y + h / 2; tr = [(cx, cy), (cx + (dx - cx) * .5, cy), (cx + (dx - cx) * .5, dy), (dx, dy)]
        o.line(tr, C['blue'], 4, 70); o.line(tr, C['cyan'], 1.2, 150); ph = i / max(1, len(devices))
        s_ = (t + ph) % 1; glow_path(o, tr, s_ if s_ < 1 else 1, .3, C['gold'], 4)
        board(o, x, y, w, h, pulse(t, ph + .12, .12), lab if labels else None)
    o.rect(cx - s, cy - s, cx + s, cy + s, C['graphite'], 255, 10, C['cyan'], 255, 2.5)
    for k in range(-3, 4):
        for sd in range(4):
            p = k * s / 3.6
            a = [(cx + p, cy - s - 11, cx + p, cy - s), (cx + p, cy + s, cx + p, cy + s + 11), (cx - s - 11, cy + p, cx - s, cy + p), (cx + s, cy + p, cx + s + 11, cy + p)][sd]
            o.line([(a[0], a[1]), (a[2], a[3])], C['gold'], 2.5, 200)
    for r in range(3):
        for c in range(3):
            b = pulse(t, ((r * 3 + c) / 9), .12); q = s * .36
            o.rect(cx - s * .78 + c * q * 1.4, cy - s * .78 + r * q * 1.4, cx - s * .78 + c * q * 1.4 + q * 1.1, cy - s * .78 + r * q * 1.4 + q * 1.1, C['indigo'], 150 + 100 * b, 3, C['violet'] if b < .4 else C['cyan'], 150 + 105 * b, 1.5)
    o.circ(cx, cy, 4 + 3 * math.sin(2 * math.pi * t), C['white'], 200)

def m_terrain(o, t):
    W, H = o.W, o.H; n = 15; cx, cy, cw, chh = .72 * W, .38 * H, .047 * W, .028 * H
    rng = np.random.default_rng(5); hz = np.zeros((n, n))
    for _ in range(4):
        px, py, a = rng.uniform(2, n - 2, 2).tolist() + [rng.uniform(25, 60)]; X, Y = np.meshgrid(range(n), range(n)); hz += a * np.exp(-((X - px) ** 2 + (Y - py) ** 2) / 8)
    P = lambda i, j: (cx + (i - j) * cw, cy + (i + j) * chh - hz[j, i] * .3)
    top = [[P(i, j) for i in range(n)] for j in range(n)]
    for j in range(n):
        o.line(top[j], C['blue'], 1.3, 150)
    for i in range(n): o.line([top[j][i] for j in range(n)], C['violet'], 1.3, 150)
    for j in range(0, n - 1):
        for i in range(0, n - 1):
            if (i + j) % 3 == 0: o.poly([top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]], C['indigo'], 80)
    pts = [(1, 12), (3, 9), (5, 8), (7, 5), (10, 4), (12, 1)]; route = [P(i, j) for i, j in pts]
    o.line(route, C['gold'], 4, 90); o.line(route, C['white'], 1.5, 200); glow_path(o, route, t, .3, C['gold'], 5)
    for k, p in enumerate(route): b = pulse(t, k / len(route), .12); o.circ(p[0], p[1], 5 + 4 * b, C['gold'], 200 + 55 * b, C['white'], 255, 1.5)

def iso(cx, cy, x, y, z, c=34): return (cx + (x - y) * c, cy + (x + y) * c * .5 - z * c * 1.05)
def cube(o, cx, cy, gx, gy, gz, al, c=34, glow=0):
    p = lambda x, y, z: iso(cx, cy, x, y, z, c)
    top = [p(gx, gy, gz + 1), p(gx + 1, gy, gz + 1), p(gx + 1, gy + 1, gz + 1), p(gx, gy + 1, gz + 1)]
    lf = [p(gx, gy + 1, gz + 1), p(gx + 1, gy + 1, gz + 1), p(gx + 1, gy + 1, gz), p(gx, gy + 1, gz)]
    rt = [p(gx + 1, gy, gz + 1), p(gx + 1, gy + 1, gz + 1), p(gx + 1, gy + 1, gz), p(gx + 1, gy, gz)]
    ec = lerpc(C['cyan'], C['gold'], glow)
    o.poly(lf, C['indigo'], al * .85, ec, al * .8, 1.5); o.poly(rt, C['navy'], al * .85, ec, al * .8, 1.5); o.poly(top, lerpc(C['violet'], C['white'], glow * .8), al * .9, ec, al, 1.5)

def m_product(o, t):
    W, H = o.W, o.H; cx, cy = .5 * W, .42 * H; cubes = []
    for z, lay in enumerate([[(x, y) for x in range(3) for y in range(3)], [(x, y) for x in range(2) for y in range(2)], [(0, 0)]]):
        cubes += [(x + (.5 if z == 1 else 0) * 0, y, z) for x, y in lay]
    cubes.sort(key=lambda c: (c[2], c[0] + c[1])); n = len(cubes); gl = 1 - smooth(np.array(t), .78, .9)
    for i, (x, y, z) in enumerate(cubes):
        p = float(smooth(np.array(t), .04 + i * .04, .12 + i * .04 + .05)); drop = (1 - p) ** 2 * 3.2
        fade = float(1 - smooth(np.array(t), .9, 1.0)); a = 255 * p * fade
        if a > 4: cube(o, cx, cy, x, y, z + drop, a, 36, glow=float(pulse(t, .2 + i * .045, .06)) * .9)

def m_layers(o, t):
    W, H = o.W, o.H; cx = .5 * W; names = ['FRONTEND', 'BACKEND', 'APIS', 'DATABASE']
    for i in range(4):
        y = .22 * H + i * .17 * H + 5 * math.sin(2 * math.pi * (t + i * .15)); b = pulse(t, (.15 + i * .2) % 1, .1); w = .2 * W
        P = [(cx - w, y), (cx, y - .06 * H), (cx + w, y), (cx, y + .06 * H)]
        o.poly(P, C['indigo'], 120 + 100 * b, C['cyan'] if b < .4 else C['gold'], 170 + 85 * b, 2)
        for k in range(4): o.line([(cx - w * .5 + k * w * .25, y + .01 * H), (cx - w * .1 + k * w * .25, y - .02 * H)], C['white'], 2, 60 + 130 * b)
        o.text(names[i], cx + w + 18, y - 9, 'Medium', 13, C['white'], 190, 3)
    for sx in (-1, 1):
        o.line([(cx + sx * .2 * W, .22 * H), (cx + sx * .2 * W, .22 * H + 3 * .17 * H)], C['violet'], 1.5, 90)
    glow_path(o, [(cx, .12 * H), (cx, .88 * H)], (t * 1.0), .25, C['gold'], 5)

def m_creative(o, t):
    W, H = o.W, o.H; bob = 7 * math.sin(2 * math.pi * t); f = font('Bold', 230 * o.k); cx, cy = .5 * W, .5 * H + bob
    for d in range(22, 0, -1):
        col = lerpc(C['violet'], C['blue'], 1 - d / 22); o.text('C', cx - 70 - d * .8, cy - 170 + d * .8, 'Bold', 230, col, 60 + 3 * (22 - d), 0)
    o.text('C', cx - 70, cy - 170, 'Bold', 230, C['white'], 235, 0)
    for k, (rx, ph, col) in enumerate([(130, 0, C['cyan']), (170, .33, C['gold']), (210, .66, C['violet'])]):
        a = 2 * math.pi * (t + ph); pts = [(cx + rx * math.cos(a + q * .1), cy + 28 * math.sin(a + q * .1) * 1.0 + (q - 31) * 1.0) for q in range(0, 63)]
        o.line(pts, col, 2, 140)
    for k in range(3):
        x = cx + 150 * math.cos(2 * math.pi * (t + k / 3)); y = cy + 30 * math.sin(2 * math.pi * (t + k / 3)); o.circ(x, y, 5, C['white'], 240)
