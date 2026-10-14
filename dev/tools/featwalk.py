# featwalk.py: in play (floor seeds from the game's seed) flags come about one floor in nine, never on two floors in a row,
# and no floor repeats the featured move / puzzle / obstacle family of the floor before it. Run from dev/tools.
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate('''()=>{const H=__HK;let fl=0,tot=0,adj=0,rep=0,pairs=0,deter=0;
      for(let g=1;g<=400;g++){H.setGameSeed(g*7919);let prev=null;for(let n=4;n<=27;n++){const F=H.featFor(n,H.levelSeed(n)),G=H.featFor(n,H.levelSeed(n));if(JSON.stringify(F)!==JSON.stringify(G))deter++;
        tot++;if(F.flag)fl++;if(prev){if(F.flag&&prev.flag)adj++;for(const k of ['move','puzzle','obstacle']){pairs++;if(F[k]&&F[k]===prev[k])rep++;}}prev=F;}}
      return JSON.stringify({floors:tot,flagged:fl,rate:fl/tot,adjacentFlags:adj,repeatedFamilies:rep,pairs,nondeterministic:deter});}'''))
    print(errs[:3]); b.close()
