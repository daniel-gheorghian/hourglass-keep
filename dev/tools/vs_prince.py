# The prince: every pose and move, found by letting the test bot play floors and noting the first episodes of each state, then
# replaying the run frame for frame and shooting at the right moment. Strips are clean-art closeups round the prince.
from vreplay import Planner
SCANS = [(3, 1), (5, 1), (6, 1), (8, 1), (9, 1), (11, 1), (12, 1), (14, 1), (18, 1), (22, 1), (25, 1)]
FIGHT = [(6, 4106), (7, 4107), (9, 4109), (10, 4110), (12, 4112), (13, 4113), (15, 4115), (18, 4118)]
FIGHTTAGS = ('s:garde', 's:advance', 's:retreat', 's:strike', 's:parry', 's:blocked', 's:poke', 's:lowStrike', 's:hurt')
POSES = [('s:stand', 'stand', 'standing at ease'), ('s:run', 'run', 'running'), ('s:stop', 'stop', 'stopping after a run'), ('s:turn', 'turn', 'turning round'),
         ('s:step', 'tiptoe', 'careful step (Grab held)'), ('s:crouch', 'crouch', 'crouching / crawling'), ('s:jumpPrep', 'jumpprep', 'standing jump wind-up'),
         ('jk:run', 'runjump', 'running jump in the air'), ('jk:stand', 'standjump', 'standing jump in the air'), ('jk:kick', 'walljump', 'wall jump (kick off a wall)'),
         ('jk:swing', 'swingjump', 'flying off the swing bar'), ('s:swing', 'swing', 'hanging and swinging on the bar'), ('s:jumpUp', 'jumpup', 'jump-up / grab for a ledge'),
         ('s:hang', 'hang', 'hanging from a ledge'), ('s:climb', 'climb', 'climbing up onto a ledge'), ('s:climbDown', 'climbdown', 'lowering to hang from a ledge'),
         ('s:land', 'land', 'landing'), ('s:landHurt', 'landhurt', 'landing hurt after a long fall'), ('s:hurt', 'hurt', 'hit by a sword'), ('s:slide', 'slide', 'sliding down a banner'),
         ('s:wallrun', 'wallrun', 'running up a wall'), ('s:lift', 'lift', 'riding a lift'), ('s:edgeWalk', 'edgewalk', 'edging to a drop'), ('s:drink', 'drink', 'drinking a flask'),
         ('s:exit', 'exit', 'leaving through the exit door'), ('s:air', 'air', 'falling / in the air'), ('s:push', 'push', 'pushing a block'), ('s:poke', 'poke', 'crouched sword thrust at a snake'),
         ('s:lowStrike', 'lowstrike', 'low sword strike'), ('s:garde', 'garde', 'sword drawn on guard'), ('s:advance', 'advance', 'advancing with the sword'),
         ('s:retreat', 'retreat', 'retreating with the sword'), ('s:strike', 'strike', 'sword strike'), ('s:parry', 'parry', 'parrying'), ('s:blocked', 'blocked', 'blow blocked / reeling'),
         ('s:bonk', 'bonk', 'bumping a wall'), ('s:dead', 'dead', 'dead')]
STRIPS = [('run', 's:run', 6, 0, 7, 50), ('runjump', 'jk:run', 24, 14, 8, 70), ('standjump', 'jk:stand', 22, 14, 8, 70), ('climb', 's:climb', 14, 8, 7, 0),
          ('hangdrop', 's:climbDown', 6, 12, 7, 0), ('wallrun', 's:wallrun', 8, 12, 7, 0), ('slide', 's:slide', 6, 6, 6, 60), ('crouch', 's:crouch', 8, 6, 7, 60),
          ('jumpup', 's:jumpUp', 12, 14, 7, 0), ('lift', 's:lift', 6, 6, 6, 60), ('turn', 's:turn', 6, 6, 6, 0), ('edgewalk', 's:edgeWalk', 6, 6, 6, 0),
          ('drink', 's:drink', 6, 6, 6, 0), ('walljump', 'jk:kick', 14, 10, 7, 0), ('swing', 's:swing', 10, 10, 7, 0), ('push', 's:push', 6, 6, 6, 60)]


def run(rig):
    P = Planner(rig, SCANS, FIGHT)
    for tag, lab, what in POSES:
        P.shot('P-' + lab, tag, what, 'prince poses', None, 'pose-closeups', prefer_fight=True if tag in FIGHTTAGS else None)
    for name, tag, pre, post, cnt, cap in STRIPS:
        P.strip('PS-' + name, tag, 'Frame strip of the move "%s"' % name, 'prince strips', 'prince-strips', pre, post, cnt, cap)
    P.execute()
