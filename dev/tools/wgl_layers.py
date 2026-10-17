# wgl_layers.py [2d]: the page's visible canvases during Torchlight play (?bench, floor 2; WK=1: WebKit): each canvas's id, pixel size,
# CSS size, display, opacity and z-index, i.e. the layers the browser composites every frame
import os, sys
from playwright.sync_api import sync_playwright
import wgl_env as E
HERE = os.path.dirname(os.path.abspath(__file__))
D2 = '2d' in sys.argv[1:]
with sync_playwright() as p:
    b = E.launch(p, True); pg = b.new_page(viewport={'width': 852, 'height': 283}, device_scale_factor=2); E.setup(pg)
    pg.goto(E.url(os.path.join(HERE, '..', 'hourglass-keep.html'), '?bench' + ('=2d' if D2 else '') + '&floors=2')); pg.wait_for_timeout(5000)
    for r in pg.evaluate('''()=>[...document.querySelectorAll('canvas')].map(c=>{const s=getComputedStyle(c),q=c.getBoundingClientRect();
        return [c.id||c.className,c.width+'x'+c.height,Math.round(q.width)+'x'+Math.round(q.height),s.display,s.visibility,s.opacity,s.zIndex,s.position,c.getContext?'':''];})'''):
        print(r)
    b.close()
