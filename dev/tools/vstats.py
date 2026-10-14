from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///Users/dan/Documents/Projects/hourglass-keep/dev/hourglass-keep.html'); pg.wait_for_timeout(300)
    r=pg.evaluate('''()=>{const H=__HK,out={};for(const n of [2,5,9,14,20,26]){const acc=[];for(let s=0;s<6;s++){const L=H.genLevel(n,3000+s*17,true);
        const segs=L.segs.filter(q=>q.k!=='secret'&&q.k!=='detour'&&q.k!=='double');let rmin=99,rmax=-1,bandCh=0,rowCh=0,vert=0,longest=0,cur=0,lastBand=-1,startBand=-1,curStart=0;
        const band=r=>Math.floor(r/3);
        for(const q of L.segs){rmin=Math.min(rmin,q.r0,q.r1);rmax=Math.max(rmax,q.r0,q.r1);if(q.r1!==q.r0){rowCh++;vert+=Math.abs(q.r1-q.r0);}
          const bb=band(q.r1);if(lastBand<0){lastBand=bb;curStart=q.c0;}if(bb!==lastBand){longest=Math.max(longest,q.c1-curStart);curStart=q.c1;bandCh++;lastBand=bb;}}
        longest=Math.max(longest,L.cols-curStart);
        // share of the main path's length per room band
        const share={};for(const q of L.segs){const bb=band(q.r1);share[bb]=(share[bb]||0)+(q.c1-q.c0);}
        const kinds={};for(const q of L.segs)if(q.r1!==q.r0)kinds[q.k]=(kinds[q.k]||0)+1;
        acc.push({cols:L.cols,rows:L.rows,roomsW:L.roomsW,roomsH:L.roomsH,rowRange:[rmin,rmax],rowChanges:rowCh,vertRows:vert,bandChanges:bandCh,longestInBandRooms:+(longest/10).toFixed(1),share,kinds});}
        out[n]=acc;}return out;}''')
    for n,acc in r.items():
        a=acc
        print(n, 'roomsW',a[0]['roomsW'],'roomsH',a[0]['roomsH'],'rows',a[0]['rows'])
        for x in a[:3]: print('   ',x['rowRange'],'rowCh',x['rowChanges'],'vert',x['vertRows'],'bandCh',x['bandChanges'],'longestBand(rooms)',x['longestInBandRooms'],x['kinds'])
    b.close()
