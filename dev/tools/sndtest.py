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
# Must print `sndtest: ok`.
import os, re, sys, struct
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
SRC = os.path.abspath(next((x for x in a if not x.startswith('wav=')), os.path.join(HERE, '..', 'hourglass-keep.html')))
WAV = next((x[4:] for x in a if x.startswith('wav=')), None)
SR = 44100
SILENT = {'clear'}  # (round 50c: the floor's fanfare is gone on purpose)


def names(src):
    s = open(src, encoding='utf-8').read()
    i = s.index("play(n,a){if(!this.ok())return;"); j = s.index('  wnd:null', i)
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
          return {q,a,l1,b,c,far,cap:H.TELL_CAP,g0,g1};}""")
        print('voice cap: %d queued of 11, %d played out of view %s, then %d more while they ring, %d in view, %d queued past TELL_R; ambience %.2f, under a clang %.2f'
              % (cap['q'], cap['a'], cap['l1'], cap['b'], cap['c'], cap['far'], cap['g0'], cap['g1']))
        want = ['saw:%d' % d for d in (160, 220, 280, 340)][:cap['cap']]
        if cap['a'] != cap['cap'] or cap['l1'] != want or cap['b'] != 0 or cap['c'] != 1 or cap['far'] != 0: bad.append('voice cap %r' % cap)
        if not cap['g1'] < 0.7 * cap['g0']: bad.append('no duck %r' % cap)
        if live[0] != 'running' or live[1] != 'suspended' or live[2] != 'running': bad.append('live context %r' % live)
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
