from playwright.sync_api import sync_playwright
import json,sys
JS=open('jumptrace.py').read().split("JS=r'''")[1].split("'''")[0]
JS=JS.replace("const log=[];","const log=[];let maxX=-1e9;").replace("if(f%4===0)log.push","maxX=Math.max(maxX,P.x-g.x);if(f%4===0)log.push").replace("return log.join(' | ');","return {maxDx:Math.round(maxX),end:P.state};")
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page()
    for f in sys.argv[1:]:
        pg.goto('file://'+f);pg.wait_for_timeout(300);out=[]
        for d in (60,70,80,90): out.append(('run@%d'%d,pg.evaluate(JS.replace('kind_d',str(d)),[170,'run'])['maxDx']))
        for d in (30,36,42): out.append(('stand@%d'%d,pg.evaluate(JS.replace('kind_d','80'),[d,'stand'])['maxDx']))
        print(f.split('/')[-1],'furthest dx past guard (>0 = got past):',out)
    b.close()
