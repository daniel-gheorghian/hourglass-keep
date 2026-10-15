# fx5_ctl.py: the touch controls fade (class ctlThin) while something that matters lies under them, and the prince sits in the clear
import sys
from vlib import Rig
rig = Rig('fx5ctl', [])
pred = "return V.dynSpot(L,'saw',null,5)"
for n, seed in ((8, 9500), (20, 9507)):
    r = rig.find(n, seed, pred, 80, False)
    if not r: print('none', n); continue
    rig.place(r['spot']); rig.settle(90)
    for i in range(4): rig.ev('()=>{__HK.tick(30);return 1}')
    thin = rig.ev("()=>document.getElementById('app').classList.contains('ctlThin')")
    rig.render('torch')
    open('/private/tmp/claude-501/-Users-dan-Documents-Projects-hourglass-keep/67efd09d-09a7-4add-94ea-fd5ae3e82aad/scratchpad/fx_5/after/shots/CTL-saw-%d.png' % n, 'wb').write(rig.png())
    print('floor', n, 'thin', thin)
rig.close()
