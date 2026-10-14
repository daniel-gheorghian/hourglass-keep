# asc.py n seed c0 c1 : ASCII map of the floor between two columns (# wall, = floor, . air, letters: features), rows that hold any floor
from playwright.sync_api import sync_playwright
import sys
n,seed,c0,c1=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])
JS='''([n,seed,c0,c1])=>{const H=__HK,L=H.genLevel(n,seed,true),out=[];const ch={spikes:'^',loose:'l',gate:'G',plate:'P',closer:'C',chomp:'M',banner:'b',shaftfoot:'s',jgrab:'J',hurtdrop:'H',low:'t',saw:'S',stone:'o',pend:'p',vent:'v',loophole:'O',bar:'B',sanctum:'z',darter:'d',xplate:'x'};
 for(let r=0;r<L.rows;r++){let s='',any=false;for(let c=c0;c<=c1;c++){const b=L.base[r*L.cols+c],f=L.feat[r*L.cols+c];let x=b===2?'#':b===1?'=':'.';if(f)x=ch[f.t]||'?';if(b!==2)any=true;if(L.guards.some(g=>Math.floor(g.x/32)===c&&g.r===r))x='@';s+=x;}if(any)out.push(String(r).padStart(3)+' '+s);}
 return out.join('\\n');}'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    print('cols',c0,'..',c1);print(pg.evaluate(JS,[n,seed,c0,c1]));b.close()
