from playwright.sync_api import sync_playwright
import json,collections
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(400)
    cdp=pg.context.new_cdp_session(pg); cdp.send('Profiler.enable'); cdp.send('Profiler.setSamplingInterval',{'interval':100})
    pg.evaluate("()=>{window.__Ls=[];for(let s=0;s<12;s++){window.__Ls.push(__HK.load(19,1000+s,true));}}")
    cdp.send('Profiler.start')
    pg.evaluate("()=>{for(let s=0;s<12;s++){__HK.load(19,1000+s,true);__HK.L.breaches=null;__HK.breaches();}}")
    prof=cdp.send('Profiler.stop')['profile']
    nodes={n['id']:n for n in prof['nodes']}; self=collections.Counter()
    for sid in prof['samples']: self[nodes[sid]['callFrame']['functionName'] or '(anon)']+=1
    tot=sum(self.values())
    for k,v in self.most_common(15): print(f'{k:30s} {v/tot*100:5.1f}%')
    b.close()
