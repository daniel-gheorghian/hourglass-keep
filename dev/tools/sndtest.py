# sndtest.py [file] [wav=DIR]: round 50c's sound check. Loads the page, plays every cue of Snd.play (the names read from its own switch)
# through Snd.render (an OfflineAudioContext with the game's whole graph: the dry bus, the room's convolver and slap, the compressor and the
# setting's level) and checks: no exception, no NaN, a peak under 0 dBFS after the compressor (each cue alone, in a hall, and a pile-up of
# the loudest at once), every cue but 'clear' audible, and the setting's levels (Off silent, Quiet under Full). Then the live context:
# unlock, every cue played, no page error. wav=DIR writes the key cues as 16-bit WAVs (cp, die, life, clang, hurt, rewind, swready, a step
# in a hall and in a tunnel, and v90's cp/die/clang/life for comparison when hk_v90_release.html is beside this script).
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
    i = s.index("play(n){if(!this.ok())return;"); j = s.index('  wnd:null', i)
    return sorted(set(re.findall(r"case'([A-Za-z]+)'", s[i:j])))


def wav(path, L, R):
    with open(path, 'wb') as f:
        n = len(L); f.write(b'RIFF' + struct.pack('<I', 36 + n * 4) + b'WAVEfmt ' + struct.pack('<IHHIIHH', 16, 1, 2, SR, SR * 4, 4, 16) + b'data' + struct.pack('<I', n * 4))
        f.write(b''.join(struct.pack('<hh', int(max(-1, min(1, x)) * 32767), int(max(-1, min(1, y)) * 32767)) for x, y in zip(L, R)))


REND = '''async ([ns,dur,z,o])=>{const H=__HK;return await H.Snd.render(ns,dur,z,o);}'''
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
        # the live context: a key press unlocks it (a user gesture, as on the phone), every cue played, the places and the bed, sleep and wake
        pg.keyboard.press('Shift')
        live = pg.evaluate('''async (ns)=>{const H=__HK,Sn=H.Snd;Sn.unlock();await new Promise(r=>setTimeout(r,300));const st=Sn.ctx&&Sn.ctx.state;
          for(const n of ns)Sn.play(n);for(const z of ['low','room','hall','shaft','court','cross','quiet'])Sn.env(z);Sn.sleep(true);await new Promise(r=>setTimeout(r,200));const s1=Sn.ctx.state;
          Sn.sleep(false);await new Promise(r=>setTimeout(r,200));return [st,s1,Sn.ctx.state];}''', cues)
        print('live context: %s, hidden %s, shown %s' % tuple(live))
        if live[0] != 'running' or live[1] != 'suspended' or live[2] != 'running': bad.append('live context %r' % live)
        if WAV:
            os.makedirs(WAV, exist_ok=True)
            for tag, ns, dur, z in [('cp', ['cp'], 6, 'room'), ('die', ['die'], 5, 'room'), ('life', ['life'], 5, 'room'), ('clang', ['clang'], 2, 'hall'), ('hurt', ['hurt'], 2, 'room'),
                                    ('rewind', ['rewind'], 2.5, 'room'), ('swready', [['ropecreak', 0], ['swready', 0]], 2, 'hall'), ('drink', ['drink'], 3, 'room'), ('guardDie', ['guardDie'], 3, 'hall'),
                                    ('steps_hall', [['step', 0.1 + 0.24 * i] for i in range(6)], 4, 'hall'), ('steps_tunnel', [['step', 0.1 + 0.24 * i] for i in range(6)], 3, 'low'),
                                    ('steps_shaft', [['step', 0.1 + 0.24 * i] for i in range(6)], 4, 'shaft')]:
                ns = [x if isinstance(x, list) else [x, 0] for x in ns]; ns = [[x[0], x[1] + 0.25] for x in ns]  # (the compressor settles over its first 0.2 s)
                r = pg.evaluate(REND, [ns, dur + 0.25, z, {'data': True}]); wav(os.path.join(WAV, 'r50c_%s.wav' % tag), r['L'], r['R'])
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
