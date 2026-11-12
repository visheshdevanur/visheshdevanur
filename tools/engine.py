"""Cinematic scene engine used to render the portfolio GIF/PNG assets (numpy + Pillow)."""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = "/usr/share/fonts/truetype/google-fonts/"
C = dict(navy=(8,13,43), indigo=(17,27,80), blue=(66,107,255), violet=(139,108,255),
         cyan=(97,223,255), gold=(255,182,110), white=(245,247,255), graphite=(21,25,39))
_fc = {}
def font(w, s):
    k = (w, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + f"Poppins-{w}.ttf", int(s))
    return _fc[k]
def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def lerpc(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
def pulse(t, ph, w=.08):
    d = ((t - ph + .5) % 1) - .5; return math.exp(-(d / w) ** 2)

def tileable(rng, h, w, power=2.2, aniso=2.2):
    n = rng.standard_normal((h, w)); F = np.fft.fft2(n)
    fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :]
    f = np.sqrt((fx * aniso) ** 2 + fy ** 2); f[0, 0] = 1
    F = F / f ** power; F[0, 0] = 0
    r = np.real(np.fft.ifft2(F)); return (r - r.mean()) / r.std()

def fbm(rng, n, octs=6, rough=.52, f0=3):
    out = np.zeros(n); a = 1; tot = 0
    for o in range(octs):
        k = int(f0 * 2 ** o) + 1
        out += a * np.interp(np.linspace(0, k, n), np.arange(k + 1), rng.random(k + 1)); tot += a; a *= rough
    out /= tot; return (out - out.min()) / (out.max() - out.min())

def figure_sprite(h, k=4):
    S = int(h * k); w = int(S * .6); im = Image.new('RGBA', (w, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def P(pts, dx=0): return [(w / 2 + (x * S) + dx, y * S) for x, y in pts]
    shapes = [[(-.115,.165),(.115,.165),(.085,.52),(-.085,.52)],
              [(-.115,.17),(-.16,.17),(-.205,.38),(-.15,.52),(-.11,.5),(-.14,.38),(-.09,.22)],
              [(.115,.17),(.16,.17),(.215,.35),(.12,.5),(.09,.46),(.15,.34),(.09,.22)],
              [(-.085,.5),(-.005,.5),(-.015,1),(-.075,1)], [(.005,.5),(.085,.5),(.075,1),(.02,1)],
              [(-.025,.12),(.025,.12),(.03,.17),(-.03,.17)]]
    for dx, col in ((k * 1.6, (255, 190, 130, 210)), (0, (6, 9, 28, 255))):
        for p in shapes: d.polygon(P(p, dx), fill=col)
        cx, cy, r = w / 2 + dx, .075 * S, .062 * S
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    return im.resize((w // k, S // k), Image.LANCZOS)

class Scene:
    def __init__(s, W, H, seed=1, sun=(.84, .6), sunstr=1.0, peaks=(), fig=None, glass=(), npart=60,
                 bases=(.62,.70,.78,.87,.97), amps=(.30,.26,.22,.18,.10), clouds=1.0):
        s.W, s.H = W, H; rng = np.random.default_rng(seed); s.rng = rng
        s.sunx, s.suny = sun[0] * W, sun[1] * H
        Y = np.arange(H, dtype=np.float32)[:, None]; X = np.arange(W, dtype=np.float32)[None, :]
        yv = np.clip(np.arange(H) / (.72 * H), 0, 1)
        st = [(0, C['navy']), (.32, C['indigo']), (.58, (58, 54, 156)), (.8, (150, 96, 172)), (1, (255, 170, 112))]
        sky = np.stack([np.interp(yv, [a for a, _ in st], [c[i] for _, c in st]) for i in range(3)], -1).astype(np.float32)
        sky = np.repeat(sky[:, None, :], W, 1)
        dx = (X - s.sunx) / (W * .36); dy = (Y - s.suny) / (H * .36)
        g = np.exp(-(dx ** 2 + dy ** 2)) * sunstr
        core = np.exp(-(((X - s.sunx) ** 2 + (Y - s.suny) ** 2) / (H * .07) ** 2)) * sunstr
        sky += g[..., None] * np.array(C['gold'], np.float32) * .62 + core[..., None] * np.array((255, 225, 170), np.float32) * .6
        vg = np.exp(-(((X - .1 * W) / (.3 * W)) ** 2 + ((Y - .5 * H) / (.5 * H)) ** 2)) * .22
        sky += vg[..., None] * np.array(C['violet'], np.float32)
        s.sky = np.clip(sky, 0, 255)
        # clouds
        s.tw = max(160, W // 4); s.ch = int(H * .62); s.cy0 = int(H * .04)
        tex = tileable(rng, s.ch, s.tw); s.wide = np.tile(tex, (1, W // s.tw + 2))
        cx = np.arange(W)[None, :]; cyy = (np.arange(s.ch) + s.cy0)[:, None]
        sunn = np.exp(-(((cx - s.sunx) / (.42 * W)) ** 2)) * smooth(cyy, .25 * H, .62 * H)
        s.ccol = lerpc((78, 66, 170), (255, 186, 150), 0)[0] * 0 + np.stack(
            [78 + (255 - 78) * sunn, 66 + (186 - 66) * sunn, 170 + (150 - 170) * sunn], -1).astype(np.float32)
        s.cv = (smooth(cyy, .08 * H, .3 * H) * (1 - smooth(cyy, .5 * H, .66 * H) * .4)).astype(np.float32) * clouds
        # mountains
        pad = 24; n = W + 2 * pad; s.pad = pad; s.layers = []
        cols = [(92,92,204), (60,66,166), (38,46,124), (22,30,92), (11,16,52)]
        fogm = [1.0, .8, .55, .35, .2]; par = [1, 2, 4, 6, 9]
        xs = np.arange(n) - pad
        sunn1 = np.exp(-(((xs - s.sunx) / (.55 * W)) ** 2))
        for i in range(5):
            r = fbm(rng, n, 6, .5 + .02 * i, 2 + i) ** 1.25
            ridge = H * bases[i] - H * amps[i] * r
            for (li, xf, hf, wf) in peaks:
                if li == i: ridge -= H * hf * np.clip(1 - np.abs(xs - xf * W) / (wf * W), 0, 1) ** 1.35
            slope = np.convolve(np.gradient(ridge), np.ones(21) / 21, 'same')
            lit = np.clip(slope * .7, 0, 1) * sunn1 * (.45 + .1 * i)
            fog = np.array(lerpc((120, 105, 215), (255, 170, 110), .5), np.float32)[None, :] * 0 + np.stack(
                [np.interp(sunn1, [0, 1], [120, 255]), np.interp(sunn1, [0, 1], [105, 170]),
                 np.interp(sunn1, [0, 1], [215, 110])], -1).astype(np.float32)
            fog *= fogm[i]
            s.layers.append(dict(ridge=ridge.astype(np.float32), col=np.array(cols[i], np.float32), fog=fog,
                                 lit=lit.astype(np.float32), rim=(sunn1 * (.5 + .08 * i)).astype(np.float32),
                                 par=par[i] * W / 1600))
        s.fig = None
        if fig:
            s.fig = (fig[0] * W, figure_sprite(fig[1] * H))
        # glass
        s.glass = []
        for (ax, ay, bx, by, w, ph, tint) in glass:
            ax, ay, bx, by, w = ax * W, ay * H, bx * W, by * H, w * H
            L = math.hypot(bx - ax, by - ay); nx, ny = -(by - ay) / L, (bx - ax) / L
            xmin = int(max(0, min(ax, bx) - w)); xmax = int(min(W, max(ax, bx) + w))
            ymin = int(max(0, min(ay, by) - w)); ymax = int(min(H, max(ay, by) + w))
            if xmax <= xmin or ymax <= ymin: continue
            Xc = X[:, xmin:xmax]; Yc = Y[ymin:ymax]
            dist = (Xc - ax) * nx + (Yc - ay) * ny; u = ((Xc - ax) * (bx - ax) + (Yc - ay) * (by - ay)) / L ** 2
            ends = np.clip(u * L + .5, 0, 1) * np.clip((1 - u) * L + .5, 0, 1)
            m = np.clip(w / 2 - np.abs(dist) + .5, 0, 1) * ends
            e = np.exp(-((np.abs(dist) - w / 2) / 1.5) ** 2) * ends
            s.glass.append(dict(sl=(slice(ymin, ymax), slice(xmin, xmax)), u=u.astype(np.float32), v=(dist / (w / 2)).astype(np.float32),
                                m=m.astype(np.float32), e=e.astype(np.float32), ph=ph, tint=np.array(tint, np.float32)))
        # particles
        s.parts = [dict(x=rng.random() * W, y=rng.random() * H * .85, r=rng.choice([1.2, 1.8, 2.6]), ax=rng.uniform(5, 18),
                        ay=rng.uniform(5, 16), p1=rng.random(), p2=rng.random(), m=int(rng.integers(1, 3)),
                        col=[C['white'], C['cyan'], C['gold'], C['violet']][int(rng.integers(0, 4))]) for _ in range(npart)]
        s.trails = []
        yy = (Y / H - .5) * 1.4; xx = (X / W - .5) * 1.2
        s.vig = (1 - .42 * np.clip(xx ** 2 + yy ** 2, 0, 1))[..., None].astype(np.float32)
        b = np.zeros((H, W), np.float32); b[:2] = 1; b[-2:] = 1; b[:, :2] = 1; b[:, -2:] = 1; s.bm = b[..., None] * .55
    def add_trail(s, pts, col, ln=.16, ph=0., w=2.5): s.trails.append((pts, col, ln, ph, w))
    def render(s, t):
        W, H = s.W, s.H; out = s.sky.copy(); sh = int(round(s.tw * t))
        a = (np.clip((s.wide[:, sh:sh + W] - .1) / 1.5, 0, 1) ** 1.2 * .72 * s.cv)[..., None]
        sl = out[s.cy0:s.cy0 + s.ch]; sl[:] = sl * (1 - a) + s.ccol * a
        off0 = math.sin(2 * math.pi * t)
        for i, L in enumerate(s.layers):
            off = int(round(L['par'] * off0)); r = L['ridge'][s.pad + off:s.pad + off + W]
            top = max(0, int(r.min()) - 1); ys = np.arange(top, H, dtype=np.float32)[:, None]
            depth = ys - r[None, :]; m = np.clip(depth + .5, 0, 1)[..., None]
            df = (np.clip(depth / (H * .5), 0, 1) * .55)[..., None]
            fog = L['fog'][s.pad + off:s.pad + off + W][None]
            col = L['col'] * (1 - df) + fog * df
            lit = L['lit'][s.pad + off:s.pad + off + W][None]; rim = L['rim'][s.pad + off:s.pad + off + W][None]
            dd = np.clip(depth, 0, None)
            tint = lit * np.exp(-dd / 24) * .5 + rim * np.exp(-dd / 2.4) * .55
            col = col + tint[..., None] * np.array(C['gold'], np.float32)
            reg = out[top:]; reg[:] = reg * (1 - m) + np.clip(col, 0, 255) * m
        for G in s.glass:
            d = ((G['u'] - t - G['ph'] + .5) % 1) - .5; sw = np.exp(-(d / .09) ** 2)
            al = np.clip(G['m'] * (.17 + .15 * (.5 + .5 * G['v']) + .32 * sw) + G['e'] * (.4 + .6 * sw), 0, .92)[..., None]
            col = G['tint'] + (np.array(C['white'], np.float32) - G['tint']) * (.35 + .65 * sw[..., None])
            reg = out[G['sl']]; reg[:] = reg * (1 - al) + col * al
        if s.fig:
            fx, spr = s.fig; L = s.layers[-1]; off = int(round(L['par'] * off0))
            gy = int(L['ridge'][s.pad + off + int(fx)]) + 3; sa = np.asarray(spr, np.float32) / 255
            h, w = sa.shape[:2]; x0 = int(fx - w / 2) + off * 0; y0 = gy - h
            if y0 >= 0 and x0 >= 0 and x0 + w <= W:
                reg = out[y0:y0 + h, x0:x0 + w]; al = sa[..., 3:4]; reg[:] = reg * (1 - al) + sa[..., :3] * 255 * al
        # particles + trails (additive)
        lay = Image.new('RGB', (W, H)); d = ImageDraw.Draw(lay)
        for p in s.parts:
            x = p['x'] + p['ax'] * math.sin(2 * math.pi * (t * p['m'] + p['p1'])); y = p['y'] + p['ay'] * math.sin(2 * math.pi * (t + p['p2']))
            b = .45 + .55 * math.sin(2 * math.pi * (t * p['m'] + p['p1'] * 3)) ** 2; r = p['r'] * W / 1600 + .4
            d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(c * b) for c in p['col']))
        for pts, col, ln, ph, w in s.trails:
            n = len(pts); hd = int(((t + ph) % 1) * n); m_ = int(ln * n)
            for k in range(m_):
                i1 = (hd - k) % n; i0 = (hd - k - 1) % n
                if abs(i1 - i0) > 3: continue
                f = (1 - k / m_) ** 1.8; d.line([pts[i0], pts[i1]], fill=tuple(int(c * f) for c in col), width=max(1, int(w * f + .5)))
        arr = np.asarray(lay, np.float32); bl = np.asarray(lay.filter(ImageFilter.GaussianBlur(4)), np.float32)
        out += arr * .9 + bl * 1.3
        return out
    def finish(s, out):
        out *= s.vig; out[:] = out * (1 - s.bm) + np.array(C['blue'], np.float32) * s.bm
        return out

def bezier(p0, p1, p2, p3, n=120):
    t = np.linspace(0, 1, n)[:, None]; P = [np.array(p) for p in (p0, p1, p2, p3)]
    q = (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]
    return [tuple(v) for v in q]

class Ov:
    def __init__(s, W, H, k=2):
        s.W, s.H, s.k = W, H, k; s.im = Image.new('RGBA', (W * k, H * k), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def _c(s, c, a): return tuple(int(v) for v in c) + (int(max(0, min(255, a))),)
    def _p(s, pts): return [(x * s.k, y * s.k) for x, y in pts]
    def line(s, pts, col, w=2, al=255): s.d.line(s._p(pts), fill=s._c(col, al), width=max(1, int(w * s.k)), joint='curve')
    def poly(s, pts, fill=None, al=255, outline=None, oal=255, ow=1):
        P = s._p(pts)
        if fill: s.d.polygon(P, fill=s._c(fill, al))
        if outline: s.d.line(P + [P[0]], fill=s._c(outline, oal), width=max(1, int(ow * s.k)), joint='curve')
    def rect(s, x0, y0, x1, y1, fill=None, al=255, r=6, outline=None, oal=255, ow=1):
        s.d.rounded_rectangle([x0 * s.k, y0 * s.k, x1 * s.k, y1 * s.k], radius=r * s.k,
                              fill=s._c(fill, al) if fill else None, outline=s._c(outline, oal) if outline else None, width=max(1, int(ow * s.k)))
    def circ(s, x, y, r, fill=None, al=255, outline=None, oal=255, ow=1):
        s.d.ellipse([(x - r) * s.k, (y - r) * s.k, (x + r) * s.k, (y + r) * s.k],
                    fill=s._c(fill, al) if fill else None, outline=s._c(outline, oal) if outline else None, width=max(1, int(ow * s.k)))
    def text(s, txt, x, y, w, size, col, al=255, track=0, anchor='l'):
        f = font(w, size * s.k); tw = sum(f.getlength(ch) + track * s.k for ch in txt) - track * s.k
        cx = x * s.k - (tw / 2 if anchor == 'c' else 0)
        for ch in txt: s.d.text((cx, y * s.k), ch, font=f, fill=s._c(col, al)); cx += f.getlength(ch) + track * s.k
    def blend(s, out, glow=5, gs=.9):
        a = np.asarray(s.im.resize((s.W, s.H), Image.LANCZOS), np.float32) / 255; rgb = a[..., :3]; al = a[..., 3:4]
        if glow:
            pm = Image.fromarray((rgb * al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(glow)); out += np.asarray(pm, np.float32) * gs
        out[:] = out * (1 - al) + rgb * 255 * al

def path_at(pts, s):
    P = np.array(pts); seg = np.hypot(*np.diff(P, axis=0).T); cum = np.concatenate([[0], np.cumsum(seg)]); tgt = np.clip(s, 0, 1) * cum[-1]
    return (float(np.interp(tgt, cum, P[:, 0])), float(np.interp(tgt, cum, P[:, 1])))
def glow_path(o, pts, s, length, col, w=4, m=14):
    for j in range(m):
        s0, s1 = s - length * (j + 1) / m, s - length * j / m
        if s0 < 0 or s1 > 1: continue
        o.line([path_at(pts, s0), path_at(pts, s1)], col, w * (1 - j / m * .5), 255 * (1 - j / m) ** 1.5)

def text_layer(W, H, items, k=2):
    im = Image.new('RGBA', (W * k, H * k), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for it in items:
        f = font(it.get('w', 'Bold'), it['size'] * k); tr = it.get('track', 0) * k; col = it.get('col', C['white']) + (255,)
        tw = sum(f.getlength(ch) + tr for ch in it['t']) - tr; cx = it['x'] * k - (tw / 2 if it.get('anchor') == 'c' else 0)
        for ch in it['t']: d.text((cx, it['y'] * k), ch, font=f, fill=col); cx += f.getlength(ch) + tr
    return im.resize((W, H), Image.LANCZOS)

def save_gif(frames, path, dur=80, colors=128):
    n = len(frames); src = Image.fromarray(np.concatenate([frames[i] for i in (0, n // 3, 2 * n // 3)], 0))
    pal = src.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [Image.fromarray(f).quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=False, disposal=1)

def render_asset(path, scene, W, H, N=30, overlay=None, texts=(), dur=80, colors=128, static_t=.35, shimmer=True, glow=5):
    base = path.rsplit('.', 1)[0]; spr = None; shadow = None
    if texts:
        spr = np.asarray(text_layer(W, H, texts), np.float32) / 255
        a8 = Image.fromarray((spr[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
        shadow = (np.asarray(a8, np.float32) / 255)[..., None] * .55
    xs = (np.arange(W) / W)[None, :, None]
    def frame(t):
        out = scene.render(t)
        if overlay:
            o = Ov(W, H); overlay(o, t); o.blend(out, glow=glow)
        scene.finish(out)
        if spr is not None:
            out *= (1 - shadow); al = spr[..., 3:4]; rgb = spr[..., :3] * 255
            if shimmer:
                d = ((xs - t + .5) % 1) - .5; sw = np.exp(-(d / .07) ** 2) * .4
                rgb = rgb + (np.array(C['cyan'], np.float32) - rgb) * sw
            out = out * (1 - al) + rgb * al
        return np.clip(out, 0, 255).astype(np.uint8)
    frames = [frame(k / N) for k in range(N)]
    Image.fromarray(frame(static_t)).save(base + '.png', optimize=True)
    save_gif(frames, base + '.gif', dur, colors)
