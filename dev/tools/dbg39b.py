from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(300)
    print(pg.evaluate(r'''()=>{const L=__HK.load(27,702645,true);return JSON.stringify(L.detours.filter(d=>d.double));}'''))
    b.close()
