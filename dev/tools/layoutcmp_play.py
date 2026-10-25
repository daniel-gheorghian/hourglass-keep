#!/usr/bin/env python3
# layoutcmp_play.py A.html B.html [lo hi] [seeds] [--timers]: are the two builds' floors the same? For floors lo..hi (default 1..48) and
# seeds 1..seeds (default 3), genLevel(n, seed) in each file, compared part by part: the tiles (L.base), the features (L.feat, every
# field, by value; gate timer durations left out unless --timers), the bot's path (L.path), the start and the exit (L.door), the lifts,
# forks and hurtdrops. Prints each floor that differs and in which parts, then 'layoutcmp: ok' or 'layoutcmp: FAIL n'. Run from dev/tools
# (round 38b; a later pass may merge it with layoutcmp.py).
import os, sys, json
from playwright.sync_api import sync_playwright
args = [a for a in sys.argv[1:] if not a.startswith('--')]
TIMERS = '--timers' in sys.argv
A, B = os.path.abspath(args[0]), os.path.abspath(args[1])
LO = int(args[2]) if len(args) > 2 else 1
HI = int(args[3]) if len(args) > 3 else 48
NS = int(args[4]) if len(args) > 4 else 3
JS = r'''([n,sd,timers])=>{delete window.__PZ;delete window.__FEAT;const L=__HK.genLevel(n,sd,true);
  const canon=(v)=>{const seen=new Map();let k=0;const walk=x=>{if(x===null||typeof x!=='object')return typeof x==='function'?'[fn]':x;
      if(seen.has(x))return '[ref'+seen.get(x)+']';seen.set(x,k++);if(Array.isArray(x)||ArrayBuffer.isView(x))return Array.from(x,walk);
      const o={};for(const key of Object.keys(x).sort()){if(!timers&&(key==='dur'||key==='est')&&(x.t==='gate'))continue;o[key]=walk(x[key]);}return o;};
    return JSON.stringify(walk(v));};
  const h=s=>{let a=0;for(let i=0;i<s.length;i++)a=(Math.imul(a,31)+s.charCodeAt(i))|0;return a+':'+s.length;};
  return {tiles:h(canon(Array.from(L.base))),feat:h(canon(L.feat)),path:h(canon(L.path)),start:canon(L.start),door:canon(L.door),
    lifts:h(canon(L.lifts)),forks:h(canon(L.forks||[])),hurtdrops:h(canon(L.hurtdrops||[])),cols:L.cols,rows:L.rows};}'''
def run(f, jobs):
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 844, 'height': 390}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + f); pg.wait_for_timeout(400)
        out = {j: pg.evaluate(JS, [j[0], j[1], TIMERS]) for j in jobs}
        b.close()
    return out, errs
jobs = [(n, s) for n in range(LO, HI + 1) for s in range(1, NS + 1)]
ra, ea = run(A, jobs); rb, eb = run(B, jobs)
bad = 0
for j in jobs:
    d = [k for k in ra[j] if ra[j][k] != rb[j][k]]
    if d:
        bad += 1; print('floor %d seed %d differs: %s' % (j[0], j[1], ', '.join(d)))
print('floors compared %d (%d..%d x seeds 1..%d), %s' % (len(jobs), LO, HI, NS, 'gate timers compared' if TIMERS else 'gate timers left out'))
print('page errors', ea[:2], eb[:2])
print('layoutcmp: ok' if bad == 0 and not ea and not eb else 'layoutcmp: FAIL %d' % bad)
sys.exit(0 if bad == 0 and not ea and not eb else 1)
