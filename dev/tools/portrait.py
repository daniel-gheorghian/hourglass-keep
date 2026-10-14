from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/hourglass-keep.html'); pg.wait_for_timeout(800)
    pg.screenshot(path='portrait_prompt.png')
    # rotate while playing: the game pauses
    pg.set_viewport_size({'width':844,'height':390}); pg.wait_for_timeout(300)
    pg.evaluate("__HK.startLevel(5,-1)"); pg.wait_for_timeout(300)
    m1=pg.evaluate("__HK.mode")
    pg.set_viewport_size({'width':390,'height':844}); pg.wait_for_timeout(400)
    m2=pg.evaluate("__HK.mode")
    vis=pg.evaluate("getComputedStyle(document.getElementById('rotate')).display")
    pg.set_viewport_size({'width':844,'height':390}); pg.wait_for_timeout(400)
    vis2=pg.evaluate("getComputedStyle(document.getElementById('rotate')).display")
    pg.screenshot(path='landscape_after.png')
    print('mode before',m1,'after turning upright',m2,'prompt',vis,'back to landscape prompt',vis2,errs[:3]); b.close()
im=Image.open('portrait_prompt.png'); im.resize((im.width//2,im.height//2)).save('portrait_prompt_s.png')
