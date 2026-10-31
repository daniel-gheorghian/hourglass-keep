# sndtest.py [file] [wav=DIR]: round 50c's sound check. Loads the page, plays every cue of Snd.play (the names read from its own switch)
# through Snd.render (an OfflineAudioContext with the game's whole graph: the dry bus, the room's convolver and slap, the compressor and the
# setting's level) and checks: no exception, no NaN, a peak under 0 dBFS after the compressor (each cue alone, in a hall, and a pile-up of
# the loudest at once), every cue but 'clear' audible, and the setting's levels (Off silent, Quiet under Full). Then the live context:
# unlock, every cue played, no page error. wav=DIR writes the key cues as 16-bit WAVs (cp, die, life, clang, hurt, rewind, swready, a step
# in a hall and in a tunnel, and v90's cp/die/clang/life for comparison when hk_v90_release.html is beside this script).
# Round 50d adds: every footfall cue (step, land, landh, gstep, gland) on every surface of SND_SURF (no NaN, under 0 dBFS, audible, the
# surfaces told apart by their sound), footSurf on the floor's own tiles; the traps heard off screen (Snd.tell): the falloff with distance
# and storeys, the voice cap (at most TELL_CAP out of view at once, the nearest first; in view always; none past TELL_R); every theme's
# ambience over the air bed rendered 12 s (no NaN, quiet: a peak under 0.3 and an rms under 0.02); the ambience ducked under an event.
# wav=DIR also writes r50d_steps_surfaces.wav, r50d_guard_offscreen.wav, r50d_saw_offscreen.wav and r50d_amb_<look>.wav (nun, meroe,
# foggara, west: 15 s standing in a hall by a lamp).
# Round 50e adds: the gate cue's openings and closings (gopen, gdoor, lopen, gshut, gthud, lshut) by their length, the great door's boom
# louder than its rise, the summoned lift's rumble without a gap, gopen's falloff placed (far left quieter, two storeys up muffled), the
# ambience ducked under a far gate; wav=DIR writes r50e_*.wav (gate near, far left, two up, closing far, a closer's slam, the door near and
# far, a lift summoned, a lift's mouth).
# Round 50h adds: a long noise plays its whole length (N(3 s) still sounding at 2.5 s: the looped buffer); the captain's drum (Snd.duel fed
# a timeline as duelState gives it): the heartbeat's tempo calm and tense (64 and 74 bpm by its 'dum' strokes), the first four softer, the
# last stroke once on the fight's end and nothing after it, a stop (null) silent within 0.4 s, a new fight (a rewind's key) softly again;
# duelState on floor 10's captain: engaged in garde, held while his reinforcement is still to drop and through it (capR), the last stroke
# only when the last of them falls, stopped by the prince's death and by a pause; the title's piece (Snd.title): the whole piece, then its
# tail, Quiet under Full, Off silent, left: faded within 1.5 s; live: a fresh page's first key press starts it on the title, a floor stops
# it and frees its strings, Quit to the title plays it again from its start. wav=DIR also writes r50h_title.wav (41 s), r50h_title_left.wav
# (left at 12 s) and r50h_duel_drum.wav (the timeline above).
# Must print `sndtest: ok`.
import os, re, sys, struct, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if not x.startswith('wav=')), os.path.join(HERE, '..', 'hourglass-keep.html')))
WAV = next((x[4:] for x in a if x.startswith('wav=')), None)
SR = 44100
SILENT = {'clear'}  # (round 50c: the floor's fanfare is gone on purpose)


def names(src):
    s = open(src, encoding='utf-8').read()
    i = s.index("play(n,a){if(!this.ok())return;"); j = min(k for k in (s.find('  wnd:null', i), s.find('  drum(kind,v,b,N,T)', i)) if k > 0)  # (round 50h: the drum's and the title's kinds are not cues)
    return sorted(set(re.findall(r"case'([A-Za-z]+)'", s[i:j])))


def wav(path, L, R):
    with open(path, 'wb') as f:
        n = len(L); f.write(b'RIFF' + struct.pack('<I', 36 + n * 4) + b'WAVEfmt ' + struct.pack('<IHHIIHH', 16, 1, 2, SR, SR * 4, 4, 16) + b'data' + struct.pack('<I', n * 4))
        f.write(b''.join(struct.pack('<hh', int(max(-1, min(1, x)) * 32767), int(max(-1, min(1, y)) * 32767)) for x, y in zip(L, R)))


REND = '''async ([ns,dur,z,o])=>{const H=__HK;return await H.Snd.render(ns,dur,z,o);}'''
FEET = ['step', 'land', 'landh', 'gstep', 'gland']
LOOKS4 = ['nun', 'meroe', 'foggara', 'west']


def feat(L, R):
    """a footfall's crude signature: rms, zero-crossing rate (brightness) and the time to fall 30 dB under its peak (its ring)"""
    n = len(L); m = [abs(a) + abs(b) for a, b in zip(L, R)]; pk = max(m) or 1e-9; i0 = m.index(pk)
    end = i0
    for i in range(i0, n):
        if m[i] > pk * 0.0316: end = i
    zc = sum(1 for i in range(1, n) if (L[i - 1] < 0) != (L[i] < 0) and m[i] > pk * 0.01)
    return (sum(x * x for x in L) / n) ** 0.5, zc / max(1, end - i0 + 1), (end - i0) / SR
# v90's Snd had no render: its cues are copied out of the page's own source into an offline context (comparison WAVs only)
OLD = r'''async ([n,dur])=>{const c=new OfflineAudioContext(2,Math.ceil(44100*dur),44100),S0=__HK.Snd,keep={ctx:S0.ctx,master:S0.master,nb:S0.nb};
  const sv=__HK.S.set.sound;__HK.S.set.sound=true;S0.ctx=c;S0.master=c.createGain();S0.master.gain.value=0.5;S0.master.connect(c.destination);
  const len=Math.floor(44100*0.8),b=c.createBuffer(1,len,44100),dd=b.getChannelData(0);for(let i=0;i<len;i++)dd[i]=Math.random()*2-1;S0.nb=b;
  const ok=S0.ok;S0.ok=()=>true;try{S0.play(n);const r=await c.startRendering();return {L:Array.from(r.getChannelData(0)),R:Array.from(r.getChannelData(1))};}
  finally{S0.ok=ok;Object.assign(S0,keep);__HK.S.set.sound=sv;}}'''

if __name__ == '__main__':
    cues = names(SRC); bad = []; errs = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + SRC); pg.wait_for_timeout(600)
        pg.evaluate("()=>{window.__HKfreeze=true;__HK.load(7,1,false);__HK.S.set.sound=true;__HK.S.set.sndQ=false;}")
        loud = {}
        for n in cues:
            dur = 6 if n in ('cp', 'die', 'life', 'rockfall', 'storm', 'breeze') else 3
            for z in ('hall', 'low'):
                r = pg.evaluate(REND, [[[n, 0.3]], dur + 0.3, z, {}])
                if r['nan']: bad.append('%s %s: %d NaN' % (n, z, r['nan']))
                if r['peak'] >= 1.0: bad.append('%s %s: peak %.3f (0 dBFS or over)' % (n, z, r['peak']))
                if n not in SILENT and r['peak'] < 1e-4: bad.append('%s %s: silent' % (n, z))
                if z == 'hall': loud[n] = r['peak']
        top = sorted(loud, key=lambda k: -loud[k])[:8]
        r = pg.evaluate(REND, [[[n, 0.3] for n in top], 5.3, 'shaft', {}])
        if r['peak'] >= 1.0 or r['nan']: bad.append('pile-up %s: peak %.3f nan %d' % (','.join(top), r['peak'], r['nan']))
        print('loudest cues (hall, peak): ' + ', '.join('%s %.2f' % (k, loud[k]) for k in top) + '; all at once %.2f' % r['peak'])
        lv = {l: pg.evaluate(REND, [[['thud', 0.3], ['step', 0.3], ['clang', 0.3]], 2, 'room', {'level': l}])['peak'] for l in ('off', 'quiet', 'full')}
        print('levels (peak of thud+step+clang): off %.4f quiet %.3f full %.3f' % (lv['off'], lv['quiet'], lv['full']))
        if lv['off'] > 0 or not (0 < lv['quiet'] < lv['full'] * 0.7): bad.append('levels %r' % lv)
        # (round 50d) the footfalls on every surface
        surf = pg.evaluate("()=>Object.keys(__HK.SND_SURF)")
        sig = {}
        for n in FEET:
            for sf in surf:
                r = pg.evaluate(REND, [[[n, 0.3, sf]], 1.6, 'room', {'data': n == 'step'}])
                if r['nan']: bad.append('%s %s: %d NaN' % (n, sf, r['nan']))
                if r['peak'] >= 1.0: bad.append('%s %s: peak %.3f' % (n, sf, r['peak']))
                if r['peak'] < 1e-4: bad.append('%s %s: silent' % (n, sf))
                if n == 'step': sig[sf] = feat(r['L'], r['R'])
        r = pg.evaluate(REND, [[[n, 0.3, sf] for n in ('landh', 'gland') for sf in surf], 2.5, 'shaft', {}])
        if r['peak'] >= 1.0 or r['nan']: bad.append('every landing at once: peak %.3f nan %d' % (r['peak'], r['nan']))
        print('steps by surface (rms x1000, crossings a sample, ring ms): ' + ', '.join('%s %.2f/%.3f/%d' % (k, v[0] * 1000, v[1], v[2] * 1000) for k, v in sig.items()))
        same = []
        ks = list(sig)
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                u, w = sig[ks[i]], sig[ks[j]]
                if all(abs(x - y) <= 0.06 * max(abs(x), abs(y), 1e-9) for x, y in zip(u, w)): same.append(ks[i] + '=' + ks[j])
        if same: bad.append('surfaces not told apart: ' + ', '.join(same))
        fs = pg.evaluate("""()=>{const H=__HK,L=H.L,out={};for(let r=0;r<L.rows;r++)for(let c=0;c<L.cols;c++){if(L.base[r*L.cols+c]!==1)continue;
          const k=H.footSurf(c*32+16,(r+1)*64-4,false);out[k]=(out[k]||0)+1;}return [out,L.theme.style];}""")
        print('footSurf on floor 7\'s floor tiles: %r (style %s)' % tuple(fs))
        if any(k not in surf for k in fs[0]) or fs[1] not in fs[0]: bad.append('footSurf %r' % (fs,))
        # (round 50d) a trap heard off screen: quieter and more muffled with distance, and through the storeys
        # (rms over both channels: the panner keeps the power; the mean of three renders, the noise's start is random)
        rm = lambda dx, dy, vw: sum(pg.evaluate(REND, [[['saw', 0.3, '', dx, dy, 'tell']], 1.2, 'room', {'vw': vw}])['rms'] for _ in range(3)) / 3
        pk = [rm(dx, 20, 1 if dx else 999) for dx in (0, 150, 300, 450, 600)]
        up = rm(150, 20 - 128, 1)
        print('saw heard (rms x1e4) at 0 (in view), 150, 300, 450, 600 px: %s; 150 px two storeys up %.2f' % (' '.join('%.2f' % (x * 1e4) for x in pk), up * 1e4))
        if any(pk[i + 1] > pk[i] * 1.05 for i in range(4)) or pk[4] > pk[0] * 0.3 or up > pk[1] * 0.8: bad.append('tell falloff %r up %.4f' % (pk, up))
        # (round 50d) every theme's ambience: quiet, no NaN
        looks = pg.evaluate("()=>__HK.THEMES.map(t=>t.look)")
        for lk in looks:
            r = pg.evaluate(REND, [[], 12, 'hall', {'bed': True, 'amb': {'look': lk}}])
            if r['nan'] or r['peak'] >= 0.3 or r['rms'] >= 0.02 or r['peak'] < 1e-4: bad.append('ambience %s: peak %.3f rms %.4f nan %d' % (lk, r['peak'], r['rms'], r['nan']))
            print('ambience %-8s peak %.3f rms %.4f' % (lk, r['peak'], r['rms']))
        # (round 50e) the gate cue: each opening's length (to 40 dB under its peak), the great door's boom at its top (2.22 s) louder than its
        # rise, a lift summoned (lsummon every LIFT_SS 0.45 s, overlapping: no gap over 40 dB down between them), and the falloff placed (far
        # off screen left quieter, two storeys up more muffled: less of the first difference)
        def env(r, t0):
            m = [abs(x) + abs(y) for x, y in zip(r['L'], r['R'])]; pk = max(m) or 1e-9; last = 0
            for i, v in enumerate(m):
                if v > pk * 0.01: last = i
            return m, pk, last / SR - t0
        ln = {}
        for n, lo_, hi_ in (('gopen', 1.9, 3.2), ('gdoor', 3.0, 4.8), ('lopen', 1.0, 2.1), ('gshut', 0.25, 1.4), ('gthud', 0.4, 2.1), ('lshut', 0.4, 2.2)):  # (the reverb's tail and the noise's random start move these by +-0.15 s)
            r = pg.evaluate(REND, [[[n, 0.3]], 5.5, 'room', {'data': True}]); m, pk, L_ = env(r, 0.3); ln[n] = L_
            if not lo_ <= L_ <= hi_: bad.append('%s lasts %.2f s, wanted %.1f-%.1f' % (n, L_, lo_, hi_))
            if n == 'gdoor':
                w = lambda a0, a1: max(m[int((0.3 + a0) * SR):int((0.3 + a1) * SR)])
                boom, rise = w(2.18, 2.6), w(0.8, 2.0)
                if not boom > rise * 1.5: bad.append('gdoor boom %.3f over its rise %.3f' % (boom, rise))
        r = pg.evaluate(REND, [[['lsummon', 0.3 + 0.45 * i] for i in range(6)], 3.5, 'shaft', {'data': True}]); m = [abs(x) + abs(y) for x, y in zip(r['L'], r['R'])]
        pk = max(m); gap = min(max(m[int(t * SR):int((t + 0.05) * SR)]) for t in [0.45 + 0.05 * i for i in range(46)]) / pk
        if gap < 0.01: bad.append('lsummon has a gap: %.4f of its peak' % gap)
        def zc(r):  # brightness: the rms of the first difference over the rms (more high frequencies, higher)
            L0 = r['L']; a = sum(x * x for x in L0) or 1e-12
            return 1000 * (sum((L0[i] - L0[i - 1]) ** 2 for i in range(1, len(L0))) / a) ** 0.5
        near = pg.evaluate(REND, [[['gopen', 0.3, '', 40, 0, 'at']], 3.2, 'room', {'data': True}]); far = pg.evaluate(REND, [[['gopen', 0.3, '', -900, 0, 'at']], 3.2, 'room', {'data': True}])
        up2 = pg.evaluate(REND, [[['gopen', 0.3, '', 0, -128, 'at']], 3.2, 'room', {'data': True}])
        print('gate cue lengths (s): ' + ', '.join('%s %.2f' % (k, v) for k, v in ln.items()) + '; lsummon\'s quietest 50 ms %.3f of its peak; gopen rms x1e4 near %.2f, 900 px left %.2f, two storeys up %.2f (brightness x1000 near %.1f, two up %.1f)'
              % (gap, near['rms'] * 1e4, far['rms'] * 1e4, up2['rms'] * 1e4, zc(near), zc(up2)))
        if not far['rms'] < near['rms'] * 0.7 or not zc(up2) < zc(near): bad.append('gopen falloff near %.5f far %.5f up %.5f' % (near['rms'], far['rms'], up2['rms']))
        # (round 50h) a long noise sounds its whole length (rms x1e4 of each 0.25 s; the buffer loops)
        nz = pg.evaluate("""async()=>{const Sn=__HK.Snd,pl=Sn.play;Sn.play=function(){this.noise(3,{vol:0.1,f:1000,att:0.05});};let r;
          try{r=await Sn.render(['x'],3.5,'cross',{data:true,level:'full'});}finally{Sn.play=pl;}const w=11025,o=[];for(let i=0;i+w<=r.L.length;i+=w){let q=0;for(let j=i;j<i+w;j++)q+=r.L[j]*r.L[j];o.push(Math.sqrt(q/w)*1e4);}return o;}""")
        print('N(3 s) rms x1e4 by 0.25 s: ' + ' '.join('%.1f' % v for v in nz))
        if not (nz[4] > nz[1] * 0.08 and nz[8] > nz[1] * 0.005): bad.append('a long noise is cut: %r' % [round(v, 1) for v in nz])
        # (round 50h) the drum: a timeline (60 Hz) calm 0-12 s, tense (k 1) 12-22 s, the last foe down at 22 s; its strokes recorded by kind
        DUEL = """async([tl,dur,data])=>{const H=__HK,Sn=H.Snd,dr=Sn.drum,log=[];Sn.drum=function(k,v,b,N,T){log.push([k,v]);let t0=1e9;dr.call(this,k,v,b,(d,o)=>{N(d,o);t0=Math.min(t0,o.at||0);},(f,d,o)=>{T(f,d,o);t0=Math.min(t0,o.at||0);});log[log.length-1].push(t0);};
          let r;try{r=await Sn.render([],dur,'room',{duel:tl,data,level:'full'});}finally{Sn.drum=dr;}const out={peak:r.peak,nan:r.nan,log};
          if(data){const w=4410,o=[];for(let i=0;i+w<=r.L.length;i+=w){let q=0;for(let j=i;j<i+w;j++)q+=r.L[j]*r.L[j];o.push(Math.sqrt(q/w));}out.env=o;out.L=r.L;out.R=r.R;}return out;}"""
        tl = [[i / 60, {'key': 1, 'on': i < 22 * 60, 'fin': 1 if 22 * 60 <= i < 22 * 60 + 3 else 0, 'k': 1 if i >= 12 * 60 else 0}] for i in range(28 * 60)]
        d = pg.evaluate(DUEL, [tl, 28, bool(WAV)])
        dums = [e for e in d['log'] if e[0] == 'dum']; tt = lambda e: e[2]
        def bpm(a, b):  # the median interval between strokes (a doubled stroke's half intervals left out by the median)
            ts = sorted(tt(e) for e in dums if a <= tt(e) < b); iv = sorted(ts[i + 1] - ts[i] for i in range(len(ts) - 1)); return 60 / iv[len(iv) // 2]
        fins = [e for e in d['log'] if e[0] == 'fin']; late = [e for e in d['log'] if e[0] != 'fin' and tt(e) > 23.0]
        calm, tense = bpm(3, 12), bpm(15, 22)
        print('drum: %d strokes (%s), calm %.1f bpm, tense %.1f bpm, first four %s, last stroke %s, after it %d; peak %.3f'
              % (len(d['log']), ','.join('%s %d' % (k, sum(1 for e in d['log'] if e[0] == k)) for k in ('dum', 'dub', 'tek', 'fin')), calm, tense,
                 ' '.join('%.2f' % e[1] for e in dums[:5]), ' '.join('%.2f s' % tt(e) for e in fins), len(late), d['peak']))
        if not (62 <= calm <= 66 and 71 <= tense <= 76): bad.append('drum tempo %.1f %.1f' % (calm, tense))
        if not (dums[0][1] < dums[1][1] < dums[2][1] < dums[3][1] and dums[0][1] < 0.6): bad.append('drum entrance %r' % dums[:5])
        if len(fins) != 1 or not 22.3 < tt(fins[0]) < 22.6 or late: bad.append('drum last stroke %r, after %d' % (fins, len(late)))
        if d['nan'] or d['peak'] >= 1.0: bad.append('drum peak %.3f nan %d' % (d['peak'], d['nan']))
        # stopped (null) at 6 s: silent within 0.4 s; a rewind (a new key) at 8 s: in again softly
        tl2 = [[i / 60, None if 6 * 60 <= i < 7 * 60 else {'key': 1 if i < 6 * 60 else 2, 'on': True, 'fin': 0, 'k': 0}] for i in range(11 * 60)]
        d2 = pg.evaluate(DUEL, [tl2, 11, True]); e2 = d2['env']
        st = max(e2[66:70]) / max(e2[20:58]); re = [e for e in d2['log'] if e[0] == 'dum' and tt(e) > 7]
        print('drum stopped: rms 6.6-7.0 s (the room tail of the strokes before) %.4f of the beating; after the rewind %d dums, the first %.2f' % (st, len(re), re[0][1] if re else -1))
        if st > 0.1 or not re or re[0][1] > 0.6 or any(6.5 < tt(e) < 7 for e in d2['log']): bad.append('drum stop %.4f / restart %r' % (st, re[:2]))
        # duelState on a captain floor: floor 10 (its captain is a veteran's match from floor 6 on, with a reinforcement)
        ds = pg.evaluate("""()=>{const H=__HK,Sn=H.Snd,D=Sn.dl,o={};H.load(10,700970,false);const G=H.G,c=G.find(g=>g.cap),P=H.P;if(!c)return {none:1};
          const st=()=>{const s=H.duelState(1/60);if(!s){D.nt=-1;return s;}if(s.key!==D.key){D.nt=-1;D.key=s.key;}D.nt=(s.fin||!s.on)?-1:1;return {on:!!s.on,fin:s.fin|0,k:s.k||0};};
          o.idle=st();c.state='garde';o.garde=st();c.alive=false;H.PGQ.push({at:H.gameTime+0.9,src:c});o.pend=st();o.pend2=st();
          H.PGQ.length=0;const v=Object.assign({},c,{cap:false,capR:1,alive:true,state:'garde',hp:1});G.push(v);o.reinf=st();o.tense=st().k;
          H.P.hp=1;o.both=st().k;H.P.hp=H.S.maxHp;v.alive=false;o.fin=st();o.after=st();
          D.nt=-1;D.key=null;H.load(10,700970,false);const c2=H.G.find(g=>g.cap);c2.state='garde';o.again=st();H.P.state='dead';o.dead=st();H.P.state='stand';
          H.mode='paused';o.paused=st();H.mode='play';D.nt=-1;D.key=null;return o;}""")
        print('duelState floor 10: %s' % json.dumps(ds))
        okd = (not ds.get('none') and not ds['idle']['on'] and ds['garde']['on'] and ds['pend']['on'] and not ds['pend']['fin'] and ds['pend2']['on'] and ds['reinf']['on']
               and abs(ds['tense'] - 0.6) < 1e-9 and ds['both'] == 1 and ds['fin']['fin'] == 1 and not ds['after']['fin'] and ds['again']['on'] and not ds['dead']['on'] and ds['paused'] is None)
        if not okd: bad.append('duelState %r' % ds)
        # the title's piece: 41 s (the piece, then its tail), Quiet and Off, and left at 12 s
        TIT = """async([dur,shown,lv,data])=>{const H=__HK;H.S.set.sound=true;const r=await H.Snd.render([],dur,'quiet',{title:shown,data,level:lv});const out={peak:r.peak,rms:r.rms,nan:r.nan};
          if(data){const w=11025,o=[];for(let i=0;i+w<=r.L.length;i+=w){let q=0;for(let j=i;j<i+w;j++)q+=r.L[j]*r.L[j]+r.R[j]*r.R[j];o.push(Math.sqrt(q/(2*w)));}out.env=o;out.L=r.L;out.R=r.R;}return out;}"""
        ti = pg.evaluate(TIT, [41, 41, 'full', True]); E = ti['env']; m = lambda a, b: (sum(x * x for x in E[a * 4:b * 4]) / ((b - a) * 4)) ** 0.5
        piece, after, tailpk = m(3, 25), m(29, 33), max(E[33 * 4:37 * 4])
        tq = pg.evaluate(TIT, [12, 12, 'quiet', False]); tf = pg.evaluate(TIT, [12, 12, 'full', False]); to = pg.evaluate(TIT, [12, 12, 'off', False])
        tL = pg.evaluate(TIT, [20, 12, 'full', True]); EL = tL['env']; left = max(EL[int(13.5 * 4):]) / max(EL[5 * 4:12 * 4])
        print('title: peak %.3f, rms 3-25 s %.4f, 29-33 s %.5f, the tail stroke 33-37 s %.4f; Quiet %.4f Full %.4f Off %.5f (rms); left at 12 s: %.4f of its level after 13.5 s'
              % (ti['peak'], piece, after, tailpk, tq['rms'], tf['rms'], to['rms'], left))
        if ti['nan'] or ti['peak'] >= 1.0 or not after < piece * 0.15 or not tailpk > after * 2: bad.append('title piece %r' % [ti['peak'], piece, after, tailpk])
        if to['peak'] > 0 or not 0 < tq['rms'] < tf['rms'] * 0.5: bad.append('title levels %r' % [tq['rms'], tf['rms'], to['rms']])
        if left > 0.05: bad.append('title not faded when left: %.4f' % left)
        # the live context: a key press unlocks it (a user gesture, as on the phone), every cue played, the places and the bed, sleep and wake
        pg.keyboard.press('Shift')
        live = pg.evaluate('''async (ns)=>{const H=__HK,Sn=H.Snd;Sn.unlock();await new Promise(r=>setTimeout(r,300));const st=Sn.ctx&&Sn.ctx.state;
          for(const n of ns)Sn.play(n);for(const z of ['low','room','hall','shaft','court','cross','quiet'])Sn.env(z);Sn.sleep(true);await new Promise(r=>setTimeout(r,200));const s1=Sn.ctx.state;
          Sn.sleep(false);await new Promise(r=>setTimeout(r,200));return [st,s1,Sn.ctx.state];}''', cues)
        print('live context: %s, hidden %s, shown %s' % tuple(live))
        # (round 50d) the voice cap and the ambience's duck, on the live context
        cap = pg.evaluate("""async ()=>{const H=__HK,Sn=H.Snd,P=H.P;Sn.tvE.fill(0);Sn.tqN=0;Sn.tlog=[];const ds=[700,160,580,220,460,400,340,280,520,640,900];
          for(const d of ds)Sn.tell('saw',P.x+d,P.y-30,false);const q=Sn.tqN,a=Sn.flush(),l1=Sn.tlog.slice();Sn.tlog=[];
          Sn.tell('saw',P.x+300,P.y-30,false);const b=Sn.flush();Sn.tell('saw',P.x+30,P.y-30,true);const c=Sn.flush();Sn.tell('saw',P.x+5000,P.y-30,false);const far=Sn.tqN;Sn.flush();
          Sn.tlog=null;await new Promise(r=>setTimeout(r,3000));const g0=Sn.aB.gain.value;Sn.play('clang');await new Promise(r=>setTimeout(r,120));const g1=Sn.aB.gain.value;
          await new Promise(r=>setTimeout(r,3000));const g2=Sn.aB.gain.value;Sn.playAt('gopen',P.x-600,P.y-30);await new Promise(r=>setTimeout(r,120));const g3=Sn.aB.gain.value; // (round 50e: a gate heard far off ducks it too)
          return {q,a,l1,b,c,far,cap:H.TELL_CAP,g0,g1,g2,g3};}""")
        print('voice cap: %d queued of 11, %d played out of view %s, then %d more while they ring, %d in view, %d queued past TELL_R; ambience %.2f, under a clang %.2f'
              % (cap['q'], cap['a'], cap['l1'], cap['b'], cap['c'], cap['far'], cap['g0'], cap['g1']))
        want = ['saw:%d' % d for d in (160, 220, 280, 340)][:cap['cap']]
        if cap['a'] != cap['cap'] or cap['l1'] != want or cap['b'] != 0 or cap['c'] != 1 or cap['far'] != 0: bad.append('voice cap %r' % cap)
        if not cap['g1'] < 0.7 * cap['g0']: bad.append('no duck %r' % cap)
        if not cap['g3'] < 0.7 * cap['g2']: bad.append('no duck under a gate %r' % cap)
        print('ambience under a far gate: %.2f of %.2f' % (cap['g3'], cap['g2']))
        if live[0] != 'running' or live[1] != 'suspended' or live[2] != 'running': bad.append('live context %r' % live)
        # (round 50h) the title, live: a fresh page shows it; the first key press wakes the sound and the piece starts; a floor stops it and lets
        # its strings go; Quit to the title plays it again from its start
        pg.goto('file://' + SRC); pg.wait_for_timeout(600)
        t0 = pg.evaluate("()=>[__HK.mode,!!__HK.Snd.ctx]")
        pg.keyboard.press('Shift'); pg.wait_for_timeout(900)
        t1 = pg.evaluate("()=>{const Sn=__HK.Snd;return [__HK.mode,Sn.ctx&&Sn.ctx.state,Sn.tl.t0>=0,!!Sn.tB,Sn.tl.i,!!Sn.tk];}")
        pg.evaluate("()=>{__HK.S.set.sound=true;__HK.load(10,700970,false);}"); pg.wait_for_timeout(400)
        t2 = pg.evaluate("()=>{const Sn=__HK.Snd;return [__HK.mode,Sn.tl.t0,!!Sn.tB,!!Sn.tk];}")
        pg.evaluate("()=>__HK.goTitle()"); pg.wait_for_timeout(700)
        t3 = pg.evaluate("()=>{const Sn=__HK.Snd;return [__HK.mode,Sn.tl.t0>=0,!!Sn.tB,Sn.tl.i,!!Sn.tk];}")
        print('title live: loaded %r, after a key %r, on a floor %r, back on the title %r' % (t0, t1, t2, t3))
        if t0 != ['title', False] or t1[:4] != ['title', 'running', True, True] or not t1[4] > 0 or t2[1:] != [-1, False, False] or t3[:3] != ['title', True, True] or not 0 < t3[3] < 12:
            bad.append('title live %r %r %r %r' % (t0, t1, t2, t3))
        if WAV:
            os.makedirs(WAV, exist_ok=True)
            for tag, ns, dur, z in [('cp', ['cp'], 6, 'room'), ('die', ['die'], 5, 'room'), ('life', ['life'], 5, 'room'), ('clang', ['clang'], 2, 'hall'), ('hurt', ['hurt'], 2, 'room'),
                                    ('rewind', ['rewind'], 2.5, 'room'), ('swready', [['ropecreak', 0], ['swready', 0]], 2, 'hall'), ('drink', ['drink'], 3, 'room'), ('guardDie', ['guardDie'], 3, 'hall'),
                                    ('steps_hall', [['step', 0.1 + 0.24 * i] for i in range(6)], 4, 'hall'), ('steps_tunnel', [['step', 0.1 + 0.24 * i] for i in range(6)], 3, 'low'),
                                    ('steps_shaft', [['step', 0.1 + 0.24 * i] for i in range(6)], 4, 'shaft')]:
                ns = [x if isinstance(x, list) else [x, 0] for x in ns]; ns = [[x[0], x[1] + 0.25] for x in ns]  # (the compressor settles over its first 0.2 s)
                r = pg.evaluate(REND, [ns, dur + 0.25, z, {'data': True}]); wav(os.path.join(WAV, 'r50c_%s.wav' % tag), r['L'], r['R'])
            # (round 50d) a strip of footfalls on each surface: four steps, a landing and a heavy one
            surf = pg.evaluate("()=>Object.keys(__HK.SND_SURF)"); ns = []; t = 0.3
            for sf in surf:
                for i in range(4): ns.append(['step', t + 0.26 * i, sf])
                ns.append(['land', t + 1.25, sf]); ns.append(['landh', t + 1.9, sf]); t += 2.9
            r = pg.evaluate(REND, [ns, t + 0.5, 'room', {'data': True}]); wav(os.path.join(WAV, 'r50d_steps_surfaces.wav'), r['L'], r['R'])
            print('r50d_steps_surfaces.wav: ' + ', '.join('%s %.1f s' % (sf, 0.3 + 2.9 * i) for i, sf in enumerate(surf)))
            # a guard heard before he is seen: he walks toward an idle guard 700 px ahead (in view under 240 px), who shifts his weight now and
            # then, draws at 100 px and advances two steps
            ns = [['step', 0.3 + 0.27 * i, 'palace'] for i in range(23)]
            for tt in (0.5, 1.6, 2.4, 3.9, 4.6, 5.6): ns.append(['gshift', tt, '', 700 - 100 * tt, -20, 'tell'])
            ns += [['draw', 6.2, '', 85, 0, 'tell'], ['gstep', 6.7, 'palace', 75, 0, 'tell'], ['gstep', 7.2, 'palace', 62, 0, 'tell']]
            r = pg.evaluate(REND, [ns, 8.5, 'hall', {'data': True, 'vw': 240, 'bed': True}]); wav(os.path.join(WAV, 'r50d_guard_offscreen.wav'), r['L'], r['R'])
            # a saw heard off screen, then coming into view: he walks toward it from 650 px
            ns = [['step', 0.3 + 0.27 * i, 'dungeon'] for i in range(26)] + [['saw', 0.25 * i, '', 650 - 85 * 0.25 * i, 20, 'tell'] for i in range(1, 29)]
            r = pg.evaluate(REND, [ns, 7.8, 'room', {'data': True, 'vw': 240, 'bed': True}]); wav(os.path.join(WAV, 'r50d_saw_offscreen.wav'), r['L'], r['R'])
            # 15 s of four themes' ambience, standing in a hall by a lamp (a floor of that theme, its first lamp that burns)
            for lk in LOOKS4:
                n = pg.evaluate("(lk)=>{for(let n=1;n<200;n++)if(__HK.themeOf(n).look===lk)return n;return 1;}", lk)
                pg.evaluate("""(n)=>{const H=__HK;H.load(n,1,false);const L=H.L,P=H.P,t=L.torches.find(t=>!t.broken)||L.torches[0];if(t){P.x=t.c*32+16+50;P.y=(t.r+1)*64-4;}}""", n)
                r = pg.evaluate(REND, [[], 15.3, 'hall', {'data': True, 'bed': True, 'amb': {'look': lk}}]); wav(os.path.join(WAV, 'r50d_amb_%s.wav' % lk), r['L'], r['R'])
                print('r50d_amb_%s.wav: floor %d, peak %.3f, rms %.4f' % (lk, n, r['peak'], r['rms']))
            # (round 50e) the gate cue for the owner: a gate opening near, far off screen left, two storeys up; a closing grind far; the exit's great
            # door near and far; a lift summoned from the plate to boarding (k 2: 1.18 s coming, the arrival, its slab opening, the ride's
            # rattle) and a lift's mouth opening; each over the hall's air bed
            for tag, ns, dur, z in [('gate_near', [['gopen', 0.3, '', 50, 0, 'at']], 3.4, 'room'), ('gate_far_left', [['gopen', 0.3, '', -700, 0, 'at']], 3.4, 'room'),
                                    ('gate_two_up', [['gopen', 0.3, '', 60, -128, 'at']], 3.4, 'room'),
                                    ('closing_far', [['gshut', 0.3, '', 520, 0, 'at'], ['gthud', 0.68, '', 520, 0, 'at']], 2.4, 'room'),
                                    ('closer_slam', [['gshut', 0.3, 'slam', 40, 0, 'at'], ['gthud', 0.55, 'slam', 40, 0, 'at']], 2.0, 'room'),
                                    ('door_near', [['gdoor', 0.3, '', 60, 0, 'at']], 4.8, 'hall'), ('door_far', [['gdoor', 0.3, '', 900, 0, 'at']], 4.8, 'hall'),
                                    ('lift_summoned', [['plate', 0.3]] + [['lsummon', 0.32 + 0.45 * i, '', 30, -60 + 23 * i, 'at'] for i in range(3)] + [['larrive', 1.5, '', 30, 0, 'at'], ['lopen', 1.5, '', 20, 0, 'at']]
                                     + [['gate', 2.3 + 0.42 * i] for i in range(4)], 4.5, 'shaft'),
                                    ('lift_mouth', [['lopen', 0.3, '', 40, 0, 'at']], 2.2, 'room')]:
                r = pg.evaluate(REND, [ns, dur, z, {'data': True, 'bed': True}]); wav(os.path.join(WAV, 'r50e_%s.wav' % tag), r['L'], r['R'])
            wav(os.path.join(WAV, 'r50h_title.wav'), ti['L'], ti['R']); wav(os.path.join(WAV, 'r50h_title_left.wav'), tL['L'], tL['R']); wav(os.path.join(WAV, 'r50h_duel_drum.wav'), d['L'], d['R'])
            old = os.path.join(HERE, 'hk_v90_release.html')
            if os.path.exists(old):
                pg.goto('file://' + old); pg.wait_for_timeout(600); pg.evaluate("()=>{window.__HKfreeze=true;__HK.load(7,1,false);}")
                for n, dur in (('cp', 2), ('die', 2), ('life', 2), ('clang', 1.5), ('hurt', 1), ('rewind', 2), ('swready', 1.5)):
                    r = pg.evaluate(OLD, [n, dur]); wav(os.path.join(WAV, 'r50c_v90_%s.wav' % n), r['L'], r['R'])
            print('wrote WAVs to', WAV)
        b.close()
    if errs: bad.append('page errors: ' + '; '.join(errs[:3]))
    print('%d cues' % len(cues))
    for x in bad: print('FAIL', x)
    print('sndtest: ok' if not bad else 'sndtest: FAIL')
    sys.exit(1 if bad else 0)
