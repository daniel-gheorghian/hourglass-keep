from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate(r'''()=>{const L=__HK.genLevel(6,502,true);const out=[];for(const ins of L.path.filter(a=>a.a==='walljump')){const c=ins.from;let r=-1;
        for(let rr=0;rr<L.rows;rr++){const f=L.feat[rr*L.cols+c];if(f&&f.t==='shaftfoot')r=rr;}
        const cell=(cc,rr)=>(rr<0||rr>=L.rows)?'#':['.','=','#'][L.base[rr*L.cols+cc]];
        const m=[];for(let rr=Math.max(0,r-ins.k-2);rr<=Math.min(L.rows-1,r+1);rr++){let row='';for(let cc=c-4;cc<=c+6;cc++)row+=cell(cc,rr);m.push((rr===r?'>':' ')+row);}
        out.push(JSON.stringify(ins)+' foot row '+r+'\n'+m.join('\n'));}return out.join('\n\n');}'''))
    b.close()
