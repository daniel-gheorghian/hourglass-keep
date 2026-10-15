# vlib.py: the rig behind the visual-review snapshots (vshots.py, vs_*.py, vsheets.py).
# One Chromium page at the iPhone landscape size (844x390, device scale 3), the game's touch controls and HUD in view.
# Output goes to $VREVIEW_OUT (default: the review folder in the scratchpad): shots/, strips/, sheets/, parts/<group>.json
# (one manifest fragment per group; vsheets.py joins them into manifest.json and manifest.md).
from playwright.sync_api import sync_playwright
import os, sys, json, base64, io, time
HERE = os.path.dirname(os.path.abspath(__file__))
HTML = 'file://' + os.path.abspath(os.path.join(HERE, '..', 'hourglass-keep.html'))
OUT = os.environ.get('VREVIEW_OUT', '/private/tmp/claude-501/-Users-dan-Documents-Projects-hourglass-keep/67efd09d-09a7-4add-94ea-fd5ae3e82aad/scratchpad/vreview')
for d in ('shots', 'strips', 'sheets', 'parts', 'cache'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
MODES = ('torch', 'classic')


class Rig:
    def __init__(self, group, only=None):
        self.group = group
        self.only = set(only or [])
        self.pw = sync_playwright().start()
        self.br = self.pw.chromium.launch()
        self.ctx = self.br.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=3, has_touch=True, is_mobile=True)
        self.pg = None
        self.errs = []
        self.keepbanner = False
        self.entries = []
        part = os.path.join(OUT, 'parts', group + '.json')
        self.prev = json.load(open(part)) if os.path.exists(part) else []
        self.fresh()

    # ---------- page
    def fresh(self, init=True, clean=False, viewport=None):
        if self.pg:
            self.pg.close()
        if clean or viewport:
            self.ctx.close()
            self.ctx = self.br.new_context(viewport=viewport or {'width': 844, 'height': 390}, device_scale_factor=3, has_touch=True, is_mobile=True)
        pg = self.pg = self.ctx.new_page()
        pg.on('pageerror', lambda e: self.errs.append(str(e)))
        pg.add_init_script('try{localStorage.clear()}catch(e){}')
        pg.goto(HTML)
        pg.wait_for_timeout(500)
        pg.add_script_tag(path=os.path.join(HERE, 'bot.js'))
        pg.add_script_tag(path=os.path.join(HERE, 'vlib.js'))
        if init:
            pg.evaluate('V.init()')
        pg.evaluate('document.fonts.ready.then(()=>1)')
        return pg

    def ev(self, js, arg=None):
        return self.pg.evaluate(js, arg) if arg is not None else self.pg.evaluate(js)

    def close(self):
        self.save()
        self.br.close()
        self.pw.stop()
        if self.errs:
            print('PAGE ERRORS', len(self.errs), self.errs[:3])

    # ---------- manifest
    def want(self, sid):
        return not self.only or sid in self.only or any(sid.startswith(o + '-') for o in self.only)

    def add(self, **e):
        self.entries = [x for x in self.entries if x['id'] != e['id']] + [e]

    def save(self):
        keep = [x for x in self.prev if x['id'] not in {y['id'] for y in self.entries}]
        # an entry from an earlier run of this group stays unless this run redid it
        if self.only:
            data = keep + self.entries
        else:
            data = self.entries
        json.dump(data, open(os.path.join(OUT, 'parts', self.group + '.json'), 'w'), indent=1)

    # ---------- scenes
    def load(self, n, seed, guards=False):
        self.ev('([n,s,g])=>{V.load(n,s,{guards:g});return 1}', [n, seed, guards])

    def find(self, n, seed0, pred, tries=40, guards=False):
        """Search seeds seed0.. of floor n for the first level where pred(L,V,H) (JS body) returns a spot; the level stays loaded."""
        return self.ev('([n,s0,t,p,g])=>V.find(n,s0,t,p,{guards:g})', [n, seed0, tries, pred, guards])

    def place(self, spot, **o):
        self.ev('([s,o])=>{V.place(s.x,s.r,s.face||1,o);return 1}', [spot, o])

    def settle(self, ticks=90, **o):
        self.ev('([k,o,c])=>{V.hold(k,o);if(c)V.clean();return 1}', [ticks, o, not self.keepbanner])

    def render(self, mode):
        self.ev('([m,c])=>{V.light(m);if(c)V.clean();V.R();return 1}', [mode, not self.keepbanner])

    def meta(self):
        return self.ev('V.meta()')

    def png(self, clip=None):
        return self.pg.screenshot(clip=clip) if clip else self.pg.screenshot()

    def shot(self, sid, what, topic, sheet, repro, modes=MODES, clip=None, closeup=False, note='', fname=None, label=None, folder='shots'):
        """Screenshot the current scene in each lighting mode; one manifest entry per image."""
        out = []
        for m in modes:
            self.render(m)
            meta = self.meta()
            iid = '%s-%s' % (sid, m)
            fn = os.path.join(folder, (fname or sid) + '-%s.png' % m)
            data = self.png(clip)
            open(os.path.join(OUT, fn), 'wb').write(data)
            self.add(id=iid, file=fn, topic=topic, sheet=sheet, what=what + (' ' + note if note else ''), repro=repro, closeup=closeup,
                     label=label or sid, kind='shot', **meta)
            out.append(iid)
        return out

    # ---------- bot scans / replays
    def scan(self, n, seed, fight=False, want=None, limit=60 * 600):
        key = '%d_%d_%d.json' % (n, seed, 1 if fight else 0)
        p = os.path.join(OUT, 'cache', key)
        if os.path.exists(p) and not want:
            return json.load(open(p))
        self.fresh()
        t = time.time()
        r = self.ev('([n,s,f,l,w])=>V.scan(n,s,f,l,w)', [n, seed, fight, limit, want or []])
        r['secs'] = round(time.time() - t, 1)
        if not want:
            json.dump(r, open(p, 'w'))
        return r

    def replay_to(self, n, seed, fight, rec, frame):
        self.fresh()
        self.ev('([n,s,f,r])=>V.replayInit(n,s,f,r)', [n, seed, fight, rec])
        self.ev('k=>{V.rstep(k);return 1}', frame)

    def step(self, k):
        self.ev('k=>{V.rstep(k);return 1}', k)

    def compose_strip(self, imgs, caps, path, title=None, height=None):
        from PIL import Image, ImageDraw, ImageFont
        n = len(imgs)
        cw = 2400 // n
        ims = [Image.open(io.BytesIO(b)).convert('RGB') for b in imgs]
        ch = int(ims[0].height * cw / ims[0].width)
        bar = 34
        top = 34 if title else 0
        sheet = Image.new('RGB', (cw * n, ch + bar + top), (18, 14, 24))
        d = ImageDraw.Draw(sheet)
        f = font(22)
        if title:
            d.text((8, 6), title, fill=(232, 196, 127), font=f)
        for i, (im, cap) in enumerate(zip(ims, caps)):
            sheet.paste(im.resize((cw, ch), Image.LANCZOS), (i * cw, top))
            d.text((i * cw + 8, top + ch + 5), cap, fill=(240, 240, 240), font=f)
            if i:
                d.line([(i * cw, top), (i * cw, top + ch + bar)], fill=(60, 50, 70), width=2)
        sheet.save(path)


_fonts = {}


def font(sz):
    from PIL import ImageFont
    if sz in _fonts:
        return _fonts[sz]
    for p in ('/System/Library/Fonts/Menlo.ttc', '/System/Library/Fonts/Helvetica.ttc', '/Library/Fonts/Arial.ttf'):
        try:
            _fonts[sz] = ImageFont.truetype(p, sz)
            return _fonts[sz]
        except Exception:
            pass
    _fonts[sz] = ImageFont.load_default()
    return _fonts[sz]


def _scene(self, sid, n, seed0, pred, what, topic, sheet, ticks=90, tries=40, js=None, js2=None, modes=MODES, clip=None, guards=False,
           note='', closeup=False, inv=True, label=None):
    """Find a level whose pred(L,V,H) gives a spot, put the prince there, settle, and shoot it in each lighting mode.
    js/js2 (optional, called with the spot) run after placing / after settling, to force a state."""
    if not self.want(sid):
        return None
    ns = n if isinstance(n, (list, tuple)) else [n]
    r = None
    for n in ns:
        r = self.find(n, seed0, pred, tries, guards)
        if r:
            break
    if not r:
        print('NOT FOUND', sid)
        self.missing.append(sid)
        return None
    spot = r['spot']
    self.place(spot, inv=inv) if inv else self.place(spot, inv=False)
    if js:
        self.ev('(s)=>{' + js + ';return 1}', spot)
    self.settle(ticks, inv=inv)
    if js2:
        self.ev('(s)=>{' + js2 + ';return 1}', spot)
    cl = None
    self.render('torch')
    if clip == 'prince':
        cl = self.ev('V.princeBox()')
    elif isinstance(clip, (list, tuple)):
        cl = self.ev('([a,b,c,d])=>V.box(...[0,1,2,3].map(i=>[a,b,c,d][i]))', clip)
    elif isinstance(clip, str) and clip.startswith('js:'):
        cl = self.ev('(s)=>' + clip[3:], spot)
    repro = 'cd dev/tools && python3 vshots.py %s %s' % (self.group, sid)
    ids = self.shot(sid, what, topic, sheet, repro, modes=modes, clip=cl, closeup=closeup or bool(cl), note=note, label=label)
    print('ok', sid, 'floor', n, 'seed', r['seed'])
    return r


Rig.scene = _scene
Rig.missing = []


def _strip(self, sid, what, topic, sheet, frames, light='torch', meta=None):
    """frames: [(png bytes, caption)]. One wide strip image (clean-art closeups, captions burned in)."""
    fn = os.path.join('strips', sid + '.png')
    self.compose_strip([f[0] for f in frames], [f[1] for f in frames], os.path.join(OUT, fn))
    m = dict(meta or {})
    self.add(id=sid, file=fn, topic=topic, sheet=sheet, what=what, repro='cd dev/tools && python3 vshots.py %s %s' % (self.group, sid),
             closeup=True, label=sid, kind='strip', light=light, **m)


def _fbox(self, spot, pre=80, post=112, up=120, down=10):
    return self.ev('([s,a,b,u,d])=>V.box(s.c*32-a,(s.r+1)*64-u,s.c*32+b,(s.r+1)*64+d)', [spot, pre, post, up, down])


def _timestrip(self, sid, n, seed0, pred, what, topic, sheet, nfr=7, span=None, tries=40, guards=False, clipf=None, light='torch', t_state='stand', pre=None, inv=True):
    """A trap through time: nfr frames spread over `span` seconds (default: one period of the found trap), clipped round the feature."""
    if not self.want(sid):
        return
    r = self.find(n, seed0, pred, tries, guards)
    if not r:
        print('NOT FOUND', sid); self.missing.append(sid); return
    sp = r['spot']
    self.place(sp, inv=inv)
    if pre:
        self.ev('(s)=>{' + pre + ';return 1}', sp)
    self.settle(60, inv=inv)
    self.render(light)
    box = self.ev('(s)=>' + clipf, sp) if clipf else _fbox(self, sp)
    per = span if span else (self.ev('(s)=>{const o=V.dynAt(s);return o&&o.f.per||2}', sp))
    ticks = max(1, int(round(per * 60 / nfr)))
    fr = []
    for i in range(nfr):
        self.render(light)
        fr.append((self.png(box), 't=%.2fs' % (i * ticks / 60)))
        self.settle(ticks, inv=inv)
    meta = self.meta()
    _strip(self, sid, what, topic, sheet, fr, light, dict(floor=meta['floor'], seed=meta['seed'], theme=meta['theme'], style=meta['style'], state=meta['state']))
    print('ok strip', sid, n, r['seed'])


def _statestrip(self, sid, n, seed0, pred, what, topic, sheet, states, tries=40, guards=False, clipf=None, light='torch', place=True, ticks=60, inv=True):
    """The same spot in several forced states: states = [(caption, js with s = the spot)]; clipped round the feature."""
    if not self.want(sid):
        return
    r = self.find(n, seed0, pred, tries, guards)
    if not r:
        print('NOT FOUND', sid); self.missing.append(sid); return
    sp = r['spot']
    self.place(sp, inv=inv)
    self.settle(ticks, inv=inv)
    self.render(light)
    box = self.ev('(s)=>' + clipf, sp) if clipf else _fbox(self, sp)
    fr = []
    for cap, js in states:
        self.ev('(s)=>{' + js + ';return 1}', sp)
        self.render(light)
        fr.append((self.png(box), cap))
    meta = self.meta()
    _strip(self, sid, what, topic, sheet, fr, light, dict(floor=meta['floor'], seed=meta['seed'], theme=meta['theme'], style=meta['style'], state=meta['state']))
    print('ok strip', sid, n, r['seed'])


Rig.strip = _strip
Rig.timestrip = _timestrip
Rig.statestrip = _statestrip


def _pass(self, n, seed, fight, rec, caps):
    """One replay of a recorded bot run on a fresh page, capturing at ascending frames.
    caps: [{frame, clip: None|'prince'|[hw,up,down], modes: (..), out: list to append (png, mode, meta) to}]"""
    caps = sorted(caps, key=lambda c: c['frame'])
    self.replay_to(n, seed, fight, rec, 0)
    cur = 0
    for c in caps:
        if c['frame'] > cur:
            self.step(c['frame'] - cur)
            cur = c['frame']
        for m in c['modes']:
            self.render(m)
            cl = None
            if c.get('clip'):
                a = c['clip'] if isinstance(c['clip'], (list, tuple)) else (80, 95, 25)
                cl = self.ev('([a,b,d])=>V.princeBox(a,b,d)', list(a))
            c['out'].append((self.png(cl), m, self.meta()))


Rig.replay_pass = _pass


def _eventstrip(self, sid, what, topic, sheet, n, seed0, pred, setup, event, pre, post, cnt, guards=False, inv=False, crop=(60, 85, 20), tries=60, maxt=900, full_after=None, hp=None):
    """Play a forced scenario twice on fresh pages: first to find the tick T when `event` (JS over H) comes true, then again,
    capturing cnt frames between T-pre and T+post. setup (JS, s = spot) typically holds a key. Returns T or None."""
    if not self.want(sid):
        return None
    self.fresh()
    r = self.find(n, seed0, pred, tries, guards)
    if not r:
        print('NOT FOUND', sid); self.missing.append(sid); return None
    seed, sp = r['seed'], r['spot']

    def start():
        self.fresh()
        self.ev('([n,s,g])=>{V.load(n,s,{guards:g});return 1}', [n, seed, guards])
        self.place(sp, inv=inv)
        if hp:
            self.ev('h=>{H.P.hp=h;return 1}', hp)
        self.ev('(s)=>{' + setup + ';return 1}', sp)
    start()
    T = self.ev('([ev,m])=>{window.__evf=new Function("H","return ("+ev+")");for(let t=0;t<m;t++){H.tick(1);if(window.__evf(H))return t;}return -1}', [event, maxt])
    if T < 0:
        print('EVENT NEVER', sid); self.missing.append(sid + ' (event never happened)'); return None
    start()
    t0 = max(0, T - pre)
    self.ev('([ev,k])=>{window.__evf=new Function("H","return ("+ev+")");for(let t=0;t<k;t++){H.tick(1);window.__evf(H);}return 1}', [event, t0])
    frames = []
    per = max(1, int(round((pre + post) / max(1, cnt - 1))))
    cur = t0
    for i in range(cnt):
        self.render('torch')
        cl = self.ev('([a,b,c])=>V.princeBox(a,b,c)', list(crop))
        frames.append((self.png(cl), '%+.2fs' % ((cur - T) / 60)))
        self.ev('k=>{for(let t=0;t<k;t++){H.tick(1);window.__evf(H);}return 1}', per)
        cur += per
    meta = self.meta()
    _strip(self, sid, what + ' (floor %d seed %d; forced scenario, event at tick %d; clean-art closeup).' % (n, seed, T), topic, sheet, frames, 'torch',
           dict(floor=meta['floor'], seed=meta['seed'], theme=meta['theme'], style=meta['style'], state=meta['state']))
    if full_after is not None:
        self.ev('k=>{H.tick(k);return 1}', full_after)
        shots = self.shot(sid + '-full', what + ' (full view a little later).', topic, None, 'cd dev/tools && python3 vshots.py %s %s' % (self.group, sid), modes=('torch',))
    print('ok event strip', sid, 'T', T)
    return T


Rig.eventstrip = _eventstrip


def _strip_wrap(self, sid, what, topic, sheet, frames, meta, light='torch'):
    _strip(self, sid, what, topic, sheet, frames, light, dict(floor=meta['floor'], seed=meta['seed'], theme=meta['theme'], style=meta['style'], state=meta['state']))


Rig._strip_wrap = _strip_wrap
