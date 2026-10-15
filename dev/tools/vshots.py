# vshots.py group [scene-id ...]: take the visual-review snapshots of one group (vs_<group>.py). Output: see vlib.py.
import sys, importlib
from vlib import Rig
group = sys.argv[1]
only = sys.argv[2:]
mod = importlib.import_module('vs_' + group)
rig = Rig(group, only)
try:
    mod.run(rig)
finally:
    if rig.missing:
        print('MISSING:', rig.missing)
    rig.close()
