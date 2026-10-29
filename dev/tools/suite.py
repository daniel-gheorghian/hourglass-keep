# The regression suite in one command, spread over the machine's cores.
#   python3 suite.py quick     bot on floors 1-35 with one seed, plus the unit tests (while iterating)
#   python3 suite.py           before each commit: bot 4 seeds, forks, flag/family floors, metrics, unit tests
#   python3 suite.py release   before a release: all of that plus the fight runs and the render check
#   -j N                       number of Chromium processes (default: physical cores; more only slows a laptop down)
#   --suite play,gen,render    only these suites, run in this order (comma list; default all, play, gen, render). The tier chooses
#                              the jobs, the suite picks among them: play (the bot and play checks), gen (generator and layout scans),
#                              render (drawing checks); see SUITES
#   --stop-on-fail             after a suite fails, skip the suites still to run (default: carry on, so every suite reports)
#   --only REGEX               only the jobs whose group and argv ("run2 run2.py 5 5 1 x 700000") match REGEX (re.search)
#   --resume FILE|DIR          skip the jobs already in a journal: a previous run dir, or a journal file (also HK_SUITE_JOURNAL)
# The bot and render runs are split one floor (and seed) per job, so the whole suite takes about as long as its slowest
# single job instead of the sum of all of them. Each of the -j worker processes (suiteworker.py) starts ONE Chromium and runs
# its jobs in turn, every job in a fresh browser context (nothing leaks between jobs); the test scripts are the same files
# that run standalone. A job that hangs (per-job timeout) or kills its worker fails with a message, and the worker is replaced.
# Several suites in one run go one after another (the order of --suite, else play, gen, render): each has the whole pool of
# workers and the GPU slots, finishes, writes and prints its summary, then the next starts (--stop-on-fail: none after a failure).
# Every run writes a run dir, suite_logs/<YYYYmmdd-HHMMSS>-<tier>[-<suites>]/ (gitignored), as it goes:
#   progress.log            a line as each job starts and finishes ([done/total], suite, ok/FAIL, argv, seconds, summary);
#                           the finish lines go to stdout too (tail -f either)
#   jobs/<suite>/<job>.log  each job's whole output, written when it finishes
#   journal.jsonl           every finished job (what --resume reads)
#   summary-<suite>.txt     a suite's verdict, its wall time and table, written (and printed) as the suite finishes
#   summary.txt             at the end: every suite's block, the five slowest jobs, and the last line ALL OK or FAILURES (exit 1)
import collections, json, os, queue, re, resource, signal, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
OPT, pos, it = {}, [], iter(sys.argv[1:])
for x in it:
    if x in ('-j', '--suite', '--only', '--resume'): OPT[x] = next(it, '')
    elif x == '--stop-on-fail': OPT[x] = True
    else: pos.append(x)
mode = 'quick' if 'quick' in pos else 'release' if 'release' in pos else 'commit'
def physical_cores():
    try: return int(subprocess.run(['sysctl', '-n', 'hw.physicalcpu'], capture_output=True, text=True).stdout.strip())
    except Exception: return max(2, (os.cpu_count() or 4) // 2)
jobs = int(OPT['-j']) if '-j' in OPT else physical_cores()
FLOORS = range(1, 36) # (the owner plays past floor 30: the bot and render runs go to 35)

# (group, argv, check(stdout) -> (ok, summary)); groups with several jobs are merged into one line.
def run2_check(out):
    m = re.search(r'passed (\d+) / (\d+).*runs with damage (\d+)', out)
    return (bool(m) and m[1] == m[2], (int(m[1]), int(m[2]), int(m[3])) if m else None)  # every run must pass
def render_check(out):
    bad = re.findall(r"\(\d+, (?!True)\w+", out) or ("errors []" not in out)
    return (not bad, out.strip().splitlines()[-1][:120] if out.strip() else '')
def tail_check(pat=None, n=2):
    def f(out):
        lines = out.strip().splitlines()
        ok = bool(re.search(pat, out)) if pat else not re.search(r'FAILURES [1-9]', out) # (the unit scripts end with 'FAILURES n')
        return (ok, ' | '.join(l.strip()[:110] for l in lines[-n:]))
    return f

J = []
seeds = 1 if mode == 'quick' else 4
def r2(n, s, fight=''): return ['run2.py', str(n), str(n), '1'] + (['fight'] if fight else ['x']) + [str(700000 + s * 13)] # one floor, seed s (run2's seed is base+n*97+s*13)
J += [('run2', r2(n, s), run2_check) for n in FLOORS for s in range(seeds)]
if mode == 'release':
    J += [('run2 fight', r2(n, s, 1), run2_check) for n in FLOORS for s in range(2)]
    J += [('rendersmoke', ['rendersmoke.py', str(n), str(n), 'both'], render_check) for n in FLOORS] # one play per floor, rendered in Classic and in Torchlight (the WebGL pass)
if mode != 'quick':
    J += [('metrics40', ['metrics40.py'], tail_check(r'FLAGS', 1))]
def fork_check(out):
    m = re.search(r'forks ok (\d+) / (\d+)', out)
    return (bool(m) and m[1] == m[2], (int(m[1]), int(m[2]), 0) if m else None)
J += [('guardscan', ['guardscan.py', str(n), str(n + 4), '4'], tail_check(r'guardscan OK')) for n in range(1, 36, 5)] # guards and snakes keep to their own budgets and meaningful spots
J += [('forktest', ['forktest.py', str(n), str(n), '2'], fork_check) for n in range(6, 28)]
def feat_check(out):
    m = re.search(r'TOTAL passed (\d+) / (\d+) with damage (\d+)', out)
    return (bool(m) and m[1] == m[2], (int(m[1]), int(m[2]), int(m[3])) if m else None)
J += [('featbot', ['featbot.py', '2', '-', 'all', str(n)], feat_check) for n in [4, 6, 9, 13, 18, 24, 27]]
def p4_check(out):
    m = re.search(r'P4 gates (\d+) runs passed (\d+) / (\d+) with damage (\d+)', out)
    return (bool(m) and m[2] == m[3] and m[4] == '0', (int(m[2]), int(m[3]), int(m[4])) if m else None)
J += [('p4bot', ['p4bot.py', str(n), str(n), '3'], p4_check) for n in range(6, 28)] # the timed remote plates (P4), timers without an extra factor
if mode == 'release':
    J += [('featbot fight', ['featbot.py', '3', 'fight', 'flags', str(n), 'flag:' + w], feat_check) for n in [9, 18, 24, 25, 27] for w in ['tower', 'rotten', 'barracks', 'longway', 'maze']] # one flag on one floor per job
unit = ['forkscan.py', 'respawnplates.py', 'puzzlescan.py', 'slabresume.py', 'primtest.py',
        'hdtest.py', 'vertscan.py', 'lifttest.py', 'featurescan.py', 'orphanscan.py', 'mazescan.py', 'glauto.py', 'metaltest.py', 'rewindrooms.py']
J += [('hinttest', ['hinttest.py', str(n), str(n)], tail_check()) for n in [1, 3, 6, 9, 10, 12, 16, 20, 24, 27, 32, 35]] # hints until learned: moves the bot uses are learned, their hints stop (floor 1 also checks the old-save migration)
J += [('grablabel', ['grablabel.py', str(n), str(n)], tail_check()) for n in [1, 3, 6, 9, 12, 16, 20, 24, 27, 32]] # the Grab button's label: scenes, fit and screenshots on floor 1; on the others the bot's Grab presses must have been announced
J += [(u[:-3], [u], tail_check()) for u in unit if os.path.exists(os.path.join(HERE, u))]
J += [('swingtest', ['swingtest.py', str(n), str(n + 2)], tail_check()) for n in [6, 12, 20]] # the swing bar is a trapeze: rest, one-way hold, pumping, the run-in catch, releases, rewind
J += [('stormfair', ['stormfair.py', str(n), str(n + 1)], tail_check()) for n in [6, 9, 13, 17, 21, 25]] # the dark's front reads where it kills, Classic and Torchlight, every theme (round 29: the rip on every row, the jackal on his)
J += [('liftkick', ['liftkick.py'], tail_check(r'ALL OK'))] # no wall plant or kick in a lift's shaft; kick shafts still climb
J += [('liftscan', ['liftscan.py', str(n), str(n + 5), '3', 'both'], tail_check(r'ALL OK')) for n in range(3, 61, 6)] # no part of a lift or its rider over a wall's front, a low ceiling or a grating in front of it (Classic and Torchlight)
J += [('lowceil', ['lowceil.py'], tail_check(r'ALL OK'))] # under a ceiling at his height a jump is the low leap and never goes through the stone
J += [('wellcorr', ['wellcorr.py', str(n), str(n + 11)], tail_check(r'wellcorr: ok')) for n in range(1, 49, 12)] # (round 30) no sand well stands in a corridor: every well's pit is walled on both sides down to its floor
if mode != 'quick':
    J += [('cpscan', ['cpscan.py', str(n), str(n + 11)], tail_check(r'cpscan: ok')) for n in range(1, 49, 12)] # (round 37c) no pixel of the water clock (the checkpoint) over a wall's front face, a step or a low ceiling beside it (both modes)
# (round 36a) the Crossing between themes: every theme starts and ends, pad, skip, save untouched, never under the bot, both modes;
# (round 36b) quick: Classic, one theme per setting (about 2 min); otherwise every theme, Classic and Torchlight as two jobs (Torchlight heavy)
if mode == 'quick': J += [('crossscan', ['crossscan.py', 'quick'], tail_check(r'crossscan: ok'))]
else: J += [('crossscan', ['crossscan.py', 'classic'], tail_check(r'crossscan: ok')), ('crossscan torch', ['crossscan.py', 'torch'], tail_check(r'crossscan: ok'))]
J += [('gratepeek', ['gratepeek.py', '6', '27', '6'], tail_check(r'tested [1-9]\d* bad 0 '))] # crouching on a grating shows the flask below
# (round 38c) checks that ran only by hand until the reference docs listed them (each guards a rule in CLAUDE.md; a few seconds to a minute each)
J += [('r38b_tests', ['r38b_tests.py'], tail_check(r'r38b: ok'))] # round 38b's play faults, one check each (roof block and P.inv, hurtdrop lip, banner rewind, sand lift hint and top, recruit colour, timed gates' waits)
J += [('sawceil', ['sawceil.py'], tail_check(r'sawceil: ok'))] # a saw under a ceiling at his height became spikes, tiptoed; the bot plays each such floor
J += [('lampscan', ['lampscan.py'], tail_check(r'(?m)^ok$'))] # (round 19) every lamp keeps clear
J += [('slabscan', ['slabscan.py'], tail_check(r'slabscan: ok'))] # (round 25d) a slab always slides up into stone
J += [('sandshaft', ['sandshaft.py'], tail_check(r'sandshaft: ok'))] # (round 26e) every sand lift stands in a shaft
J += [('wellscan', ['wellscan.py'], tail_check(r'(?m)^ok$'))] # (round 21b) the sand wells' slope, volume, break timing and rewind
J += [('hillscan', ['hillscan.py', str(n), str(n + 11)], tail_check(r'hillscan: ok')) for n in range(1, 49, 12)] # (round 43) heaps and drifts only on a run's plain floor, off timed stretches and the chase, at least one a floor from floor 3
if mode != 'quick': # (round 47a) no jump (but the low leap) lands on or past a hill's foot or leaves the floor on one, none crosses one faster than its pace, no crawl onto one; four jobs
    J += [('hilljump', ['hilljump.py', str(lo), str(hi)], tail_check(r'hilljump: ok')) for lo, hi in ((3, 14), (15, 26), (27, 38), (39, 48))]
J += [('windscan', ['windscan.py', str(n), str(n + 11)], tail_check(r'windscan: ok')) for n in range(1, 49, 12)] # (round 44) the wind only on a run's plain floor, clear of every jump, off timed stretches and the chase; a gust pushes him back but never off it
J += [('courtscan', ['courtscan.py', str(n), str(n + 11)], tail_check(r'courtscan: ok')) for n in range(1, 49, 12)] # (round 45) courts on headroom under stone, 7-8 a floor from 3, never two in view, kinds by theme, every court pit a pool, nothing of the wall left; a fall into a pool drowns at its surface
# (round 47b) one horizon per storey: a window, an open arch or breach and a court on one storey place every layer of the view at the same screen y,
# and the court's own art stands on the windows' horizon (to 0.5 px; analytic, no picture); two jobs
J += [('viewscan', ['viewscan.py', str(lo), str(hi)], tail_check(r'viewscan: ok')) for lo, hi in ((3, 24), (25, 48))]
if os.path.exists(os.path.join(HERE, 'hk_v69_release.html')): # (its baseline is kept locally, not in git)
    J += [('figscan', ['figscan.py'], tail_check(r'figscan: ok'))] # (round 23) the body's poses: held hands, crown, soles, the keyed jumps and steps
if mode == 'release':
    J += [('shadowscan', ['shadowscan.py', str(n), str(n + 5)], tail_check(r'shadowscan: ok')) for n in range(1, 49, 6)] # (round 38a) no figure's lamp shadow on what stands before the back wall (Torchlight)
def art_check(out): # doorscan / openscan print counts per kind and mode: every count of bad must be 0, and no page errors
    ok = 'errors []' in out and not re.search(r'(torch|classic) [1-9]\d*( of|,| \()', out)
    return (ok, ' | '.join(l.strip()[:60] for l in out.strip().splitlines()[-2:]))
if mode == 'release': # (the art-over-openings scans of rounds 15, 16c and 35c, both modes; all twelve themes over floors 1-48)
    J += [('doorscan', ['doorscan.py', str(n), str(n + 11)], art_check) for n in range(1, 49, 12)]
    J += [('openscan', ['openscan.py', str(n), str(n + 11)], art_check) for n in range(1, 49, 12)]
    J += [('tilescan', ['tilescan.py', str(n), str(n + 11), 'views=2'], tail_check(r'tilescan: ok')) for n in range(1, 49, 12)]
    # (round 46a) no staircases in the sky beams (rules S1-S7, dev/docs/rendering.md): every theme at every hour and the forced cases, both modes,
    # GLP.rs 1, .75, .5 and Battery saver; split by the cases' floors into four GPU jobs of about 10 cases (1.5 to 2 min each here)
    J += [('beamjag', ['beamjag.py', str(lo), str(hi)], tail_check(r'beamjag: ok')) for lo, hi in ((1, 24), (25, 60), (61, 110), (111, 180))]
    # (round 46b) heaps and drifts are opaque solids (layers.md R5-R7): their drawn pixels unchanged with the back wall's art flattened, the beams,
    # the lamp shadow or the relief off, both modes; floors 3-48 x 2 seeds in four GPU jobs
    J += [('heapscan', ['heapscan.py', str(n), str(min(48, n + 11))], tail_check(r'heapscan: ok')) for n in range(3, 49, 12)]
    # (round 46c) the other solids are opaque too (layers.md R5-R7): pushed blocks, fallen roof blocks, jambs, lifts, the sky clock; four GPU jobs
    J += [('solidscan', ['solidscan.py', str(n), str(n + 11)], tail_check(r'solidscan: ok')) for n in range(1, 49, 12)]
    # (round 46c) the contour rule (rendering.md "Contours"): no prop's edge a fixed near-black ink; Classic, in software, four light jobs
    J += [('contourscan', ['contourscan.py', str(n), str(n + 11)], tail_check(r'contourscan: ok')) for n in range(1, 49, 12)]
    # (round 47b) the court's layers move at their true depths: each alone, panned, every band at its f to 0.01, the theme's view in its bays no
    # nearer than the far side; every theme and hour (Classic, software), three light jobs by floor range
    J += [('panscan', ['panscan.py', str(lo), str(hi)], tail_check(r'panscan: ok')) for lo, hi in ((3, 60), (61, 120), (121, 180))]
# Suites: every group belongs to exactly one (a group with none stops the run here, before anything starts: add it below)
SUITES = {
    'play': ('run2', 'run2 fight', 'featbot', 'featbot fight', 'p4bot', 'forktest', 'hinttest', 'grablabel', 'swingtest', 'liftkick',
             'lowceil', 'r38b_tests', 'sawceil', 'hilljump', 'primtest', 'hdtest', 'lifttest', 'respawnplates', 'slabresume', 'gratepeek'), # the bot and play checks
    'gen': ('metrics40', 'guardscan', 'forkscan', 'puzzlescan', 'vertscan', 'featurescan', 'orphanscan', 'mazescan', 'wellcorr', 'lampscan',
            'slabscan', 'sandshaft', 'wellscan', 'hillscan', 'windscan', 'courtscan'), # generator and layout scans (the tiles, no picture)
    'render': ('rendersmoke', 'liftscan', 'crossscan', 'crossscan torch', 'cpscan', 'shadowscan', 'doorscan', 'openscan', 'tilescan', 'beamjag',
               'heapscan', 'solidscan', 'contourscan', 'viewscan', 'panscan', 'stormfair', 'glauto', 'metaltest', 'rewindrooms', 'figscan')} # drawing checks (pixels, poses, the WebGL path)
SUITE_OF = {g: su for su, gs in SUITES.items() for g in gs}
assert len(SUITE_OF) == sum(len(gs) for gs in SUITES.values()), 'a group is in two suites'
miss = sorted({j[0] for j in J} - set(SUITE_OF))
if miss: sys.exit('suite.py: group(s) %s belong to no suite: add each to one of SUITES' % ', '.join(miss))
WANT = OPT['--suite'].split(',') if OPT.get('--suite') else list(SUITES)
if set(WANT) - set(SUITES): sys.exit('suite.py: unknown suite(s) %s (have %s)' % (', '.join(sorted(set(WANT) - set(SUITES))), ', '.join(SUITES)))
WANT = list(dict.fromkeys(WANT))   # (in the order given; each once)
ONLY = OPT.get('--only')
J = [j for j in J if SUITE_OF[j[0]] in WANT and (not ONLY or re.search(ONLY, j[0] + ' ' + ' '.join(j[1])))]
WANT = [su for su in WANT if any(SUITE_OF[j[0]] == su for j in J)]   # (a suite --only left empty is not reported)
if not J: sys.exit('suite.py: no %s jobs in suite(s) %s%s' % (mode, ','.join(WANT), ' matching --only %r' % ONLY if ONLY else ''))
# longest jobs first so the tail of the run isn't one slow floor
RANK = {'liftscan': 0, 'crossscan torch': 0, 'shadowscan': 1, 'crossscan': 2, 'featbot fight': 0, 'run2 fight': 1, 'rendersmoke': 2, 'puzzlescan': 3, 'primtest': 3, 'lifttest': 3, 'featbot': 3, 'metrics40': 4, 'featurescan': 4, 'forktest': 5, 'run2': 6}
def floor_of(a): return max([int(x) for x in a[1:] if x.isdigit() and int(x) < 100] or [0]) # (the run2 seed base is not a floor)
J.sort(key=lambda j: (RANK.get(j[0], 7), -floor_of(j[1])))
TIMEOUT = 1500 # seconds a single job may take (the slowest healthy ones take under 5 min); a job over it fails and its worker is replaced

# each worker runs in its own process group (with its Chromium), so stopping the suite (Ctrl-C, kill) also stops everything
LIVE = set()
def stop_all(*_):
    for pr in list(LIVE):
        try: os.killpg(pr.pid, signal.SIGTERM)
        except Exception: pass
    os._exit(130)
signal.signal(signal.SIGTERM, stop_all); signal.signal(signal.SIGINT, stop_all)

class Worker:
    """One suiteworker.py process with its Chromium; started on first use and again after it hung or died."""
    def __init__(self): self.pr = None
    def start(self):
        self.pr = subprocess.Popen([PY, os.path.join(HERE, 'suiteworker.py')], cwd=HERE, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, start_new_session=True)
        LIVE.add(self.pr); self.err = []
        threading.Thread(target=lambda p=self.pr, e=self.err: e.extend(p.stderr), daemon=True).start() # (drained so a chatty worker can't block)
        if not self.pr.stdout.readline(): raise RuntimeError('worker did not start: ' + ''.join(self.err)[-300:])
    def kill(self):
        if self.pr:
            try: os.killpg(self.pr.pid, signal.SIGKILL)
            except Exception: pass
            try: self.pr.wait(10)
            except Exception: pass
            LIVE.discard(self.pr); self.pr = None
    def stop(self):
        if self.pr:
            try: self.pr.stdin.close(); self.pr.wait(30)
            except Exception: pass
            self.kill()
    def run(self, argv, gpu=False):
        """-> (returncode, output); returncode -1 for a worker that died or hung."""
        try:
            if self.pr is None or self.pr.poll() is not None: self.kill(); self.start()
            timer = threading.Timer(TIMEOUT, lambda p=self.pr: os.killpg(p.pid, signal.SIGKILL)); timer.start(); t = time.time()
            try:
                self.pr.stdin.write(json.dumps({'argv': argv, 'gpu': gpu}) + '\n'); self.pr.stdin.flush()
                line = self.pr.stdout.readline()
            finally: timer.cancel()
            if line:
                r = json.loads(line); return r['rc'], r['out']
            why = 'timed out after %d s' % TIMEOUT if time.time() - t >= TIMEOUT - 1 else 'worker (Chromium) died'
            time.sleep(0.2); msg = '%s: %s %s' % (why, ' '.join(argv), ''.join(self.err)[-300:])
            self.kill(); return -1, msg
        except Exception as e:
            self.kill(); return -1, 'worker failed: %r' % e

def go(j, w):
    g, a, chk = j; t = time.time()
    rc, out = w.run(a, g in HEAVY)   # (the jobs that draw Torchlight run in the worker's GPU browser: suiteworker.py)
    if rc == -1: ok, s = False, out.strip().splitlines()[-1][:160] if out.strip() else 'exit -1'   # worker died or the job timed out
    else:
        ok, s = chk(out)          # (read even when the script exited 1, e.g. on a SLOW RUN, so the pass counts stay whole)
        if rc != 0: ok = False; s = s if isinstance(s, tuple) else (out.strip().splitlines()[-1][:160] if out.strip() else 'exit %d' % rc)
    return g, a, ok, s, time.time() - t, out

# Jobs that draw Torchlight run in each worker's GPU browser (WebGL through ANGLE on Metal, suiteworker.py; HK_SUITE_GPU=0: on the
# CPU in SwiftShader, as before) and at most GPU_JOBS at a time; the other workers take light jobs meanwhile. On the GPU (8-core i9,
# Radeon Pro 5500M, idle): liftscan.py 15 20 83 s against 495 s in software, shadowscan.py 13 18 127 s against 533 s; eight
# shadowscans at once took 285 s each and 4.9 min in all, four at a time 150 s each and 5.2 min, at 40% less CPU, so 4. (In
# software, v67: 1 rendersmoke alone 53 s, 4 at once 137 s each, 8 at once 300 s each.) Only these: a GPU-drawn 2D canvas is not
# bit-exact between two redraws on the Radeon (rewindrooms finds 13 values off), so the light jobs stay in software.
HEAVY = ('rendersmoke', 'liftscan', 'crossscan torch', 'cpscan', 'shadowscan', 'doorscan', 'openscan', 'tilescan', 'beamjag', 'heapscan', 'solidscan')
GPU_JOBS = int(os.environ.get('HK_GPU_JOBS', '4'))
t0 = time.time(); res = []; QL = queue.Queue(); QH = queue.Queue(); GPU = threading.Semaphore(GPU_JOBS)
# The run dir (see the top). --resume FILE (or HK_SUITE_JOURNAL): every finished job is appended to FILE as one JSON line, and a run
# started with the same FILE skips the jobs it already holds and reports them with the rest (a machine that restarts mid-run loses only
# the jobs in flight); --resume DIR carries on in that run dir with its journal.jsonl. Without either, the journal is the new run dir's.
R = OPT.get('--resume') or os.environ.get('HK_SUITE_JOURNAL')
if R and os.path.isdir(R): RUN = os.path.abspath(R); JOURNAL = os.path.join(RUN, 'journal.jsonl')
else:
    RUN = os.path.join(HERE, 'suite_logs', time.strftime('%Y%m%d-%H%M%S') + '-' + mode + ('-' + '-'.join(WANT) if OPT.get('--suite') else ''))
    JOURNAL = R or os.path.join(RUN, 'journal.jsonl')
os.makedirs(RUN, exist_ok=True)
def jlog(g, a): # jobs/<suite>/<argv with the script's .py dropped and anything odd made _>.log
    return os.path.join(RUN, 'jobs', SUITE_OF.get(g, 'other'), re.sub(r'[^\w.+-]+', '_', ' '.join(a).replace('.py', '', 1)) + '.log')
def rel(p): return os.path.relpath(p, HERE)
def short(s): return (('passed %d / %d, damage %d' % s) if isinstance(s, tuple) else str(s))[:140]
def write_job(r):
    g, a, ok, s, dt, out = r; p = jlog(g, a); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f: f.write('# %s | %s | %.1f s | %s\n%s' % (' '.join(a), 'ok' if ok else 'FAIL', dt, short(s), out))
PLOCK = threading.RLock(); PF = open(os.path.join(RUN, 'progress.log'), 'a')
def plog(line, echo=False): # progress.log (and stdout) at once, one writer at a time
    s = '%s %6.0fs %s' % (time.strftime('%H:%M:%S'), time.time() - t0, line)
    with PLOCK:
        PF.write(s + '\n'); PF.flush()
        if echo: print(s, flush=True)
KEEP = {json.dumps(j[1]) for j in J}; done = set()
if os.path.exists(JOURNAL):
    for l in open(JOURNAL):
        try: r = json.loads(l)
        except Exception: continue
        k = json.dumps(r['a'])
        if k not in KEEP or k in done: continue   # (a job of another tier, suite or --only; or one already read)
        s = tuple(r['s']) if isinstance(r['s'], list) else r['s']
        res.append((r['g'], r['a'], r['ok'], s, r['dt'], r['out'])); done.add(k)
        if not os.path.exists(jlog(r['g'], r['a'])): write_job(res[-1])
NTOT = len(J); NDONE = [len(done)]
LEFT_ALL = collections.Counter(SUITE_OF[j[0]] for j in J)
SUT = {}      # suite -> [start, finish] of its turn in this run
SKIP = []     # suites --stop-on-fail left out
print('run dir %s' % RUN, flush=True)
plog('suite.py %s, %d jobs (%s), %d processes%s%s' % (mode, NTOT, ', '.join('%s %d' % (su, sum(SUITE_OF[j[0]] == su for j in J)) for su in WANT), jobs,
     ', --only %r' % ONLY if ONLY else '', ', resumed %d finished jobs from %s' % (len(done), JOURNAL) if done else ''), True)
def take():
    """-> (job, holds_gpu) or (None, False) when both queues are empty."""
    while True:
        if not QH.empty() and GPU.acquire(blocking=False):
            try: return QH.get_nowait(), True
            except queue.Empty: GPU.release()
        try: return QL.get_nowait(), False
        except queue.Empty: pass
        if QH.empty(): return None, False
        if GPU.acquire(timeout=1):     # only heavy jobs are left: wait for a slot
            try: return QH.get_nowait(), True
            except queue.Empty: GPU.release()

def block(su):
    """-> (ok, lines): a suite's header and its per-group table (featbot/p4bot/run2 totals and damage, forks, rendersmoke floors),
    each failing job with its key lines and its log."""
    rs_ = [r for r in res if SUITE_OF.get(r[0]) == su]; groups = {}; sok = True; L = []
    for g, a, ok, s, dt, out in rs_: groups.setdefault(g, []).append((a, ok, s, dt, out))
    for g, rs in groups.items():
        ok = all(r[1] for r in rs); cpu = sum(r[3] for r in rs)
        if g.startswith('featbot') or g == 'p4bot':
            tot = [r[2] for r in rs if isinstance(r[2], tuple)]
            p, n, h = (sum(x[i] for x in tot) for i in range(3))
            ok &= g == 'featbot fight' or h == 0
            s = 'passed %d / %d, runs with damage %d' % (p, n, h)
        elif g == 'forktest':
            tot = [r[2] for r in rs if isinstance(r[2], tuple)]
            s = 'forks ok %d / %d' % (sum(x[0] for x in tot), sum(x[1] for x in tot))
        elif g.startswith('run2'):
            tot = [r[2] for r in rs if isinstance(r[2], tuple)]
            p, n, h = (sum(x[i] for x in tot) for i in range(3))
            ok &= g == 'run2 fight' or h == 0
            s = 'passed %d / %d, runs with damage %d' % (p, n, h)
        elif g.startswith('rendersmoke'):
            s = 'floors %d, %s' % (len(rs), 'no errors' if ok else 'ERRORS')
        else:
            s = rs[0][2]
        sok &= ok
        L.append('%-15s %-4s %7.0f  %s' % (g, 'yes' if ok else 'NO', cpu, s))
        if not ok:
            for a, o, ss, dt, out in rs:
                if not o or g.startswith(('run2', 'featbot')) or g == 'forktest':
                    fails = [l for l in out.splitlines() if l.startswith(('{', 'SLOW RUN')) or 'Error' in l][:3]
                    if fails or not o: L.append('    %s | %s\n      log %s' % (' '.join(a), ' / '.join(x[:200] for x in fails) or short(ss), rel(jlog(g, a))))
    w = SUT.get(su); wall = (w[1] - w[0]) if w and w[1] else 0; nj = sum(SUITE_OF[j[0]] == su for j in J)
    if su in SKIP:
        return False, ['== %s: SKIPPED (--stop-on-fail after %s failed), %d jobs not run' % (su, SKIP_BY[0], nj - len(rs_))]
    nres = sum(1 for r in rs_ if json.dumps(r[1]) in done)
    head = '== %s: %s, %d jobs%s, wall %.1f min, job time %.1f min%s' % (su, 'OK' if sok else 'FAILURES', len(rs_),
           ' (%d resumed)' % nres if nres else '', wall / 60, sum(r[4] for r in rs_) / 60, '' if len(rs_) == nj else ' (INCOMPLETE)')
    if len(rs_) < nj: sok = False   # (a job that never reported is not a pass)
    return sok, [head, '%-15s %-4s %7s  %s' % ('test', 'ok', 'job s', 'result')] + L
WROTE = set()
def suite_done(su): # summary-<suite>.txt and stdout, as a suite finishes -> its verdict
    with PLOCK:
        ok, L = block(su)
        if su in WROTE: return ok
        WROTE.add(su)
        with open(os.path.join(RUN, 'summary-%s.txt' % su), 'w') as f: f.write('\n'.join(L) + '\n')
        plog('suite %s done: %s (%s)' % (su, 'OK' if ok else 'SKIPPED' if su in SKIP else 'FAILURES', rel(os.path.join(RUN, 'summary-%s.txt' % su))))
        print('\n'.join(L) + '\n', flush=True)
        return ok

def loop():
    w = Worker()
    try:
        while True:
            j, gpu = take()
            if j is None: return
            su = SUITE_OF[j[0]]
            plog('[%*d/%d] %-6s start %s' % (len(str(NTOT)), NDONE[0], NTOT, su, ' '.join(j[1])))
            try:
                r = go(j, w); res.append(r); write_job(r)
                with JLOCK, open(JOURNAL, 'a') as f: f.write(json.dumps({'g': r[0], 'a': r[1], 'ok': r[2], 's': r[3], 'dt': r[4], 'out': r[5]}) + '\n')
                with PLOCK:
                    NDONE[0] += 1
                    plog('[%*d/%d] %-6s %-4s %s  %.0f s | %s' % (len(str(NTOT)), NDONE[0], NTOT, su, 'ok' if r[2] else 'FAIL', ' '.join(r[1]), r[4], short(r[3])), True)
            finally:
                if gpu: GPU.release()
    finally: w.stop()
JLOCK = threading.Lock(); SKIP_BY = ['']
for su in WANT: # one suite after another, each with the whole pool (a worker and its Chromium per thread, stopped at the suite's end)
    if SKIP_BY[0]: SKIP.append(su); suite_done(su); continue
    todo = [j for j in J if SUITE_OF[j[0]] == su and json.dumps(j[1]) not in done]
    SUT[su] = [time.time(), 0]
    plog('suite %s start: %d jobs%s' % (su, len(todo), ', %d resumed' % (LEFT_ALL[su] - len(todo)) if LEFT_ALL[su] > len(todo) else ''), True)
    for j in todo: (QH if j[0] in HEAVY else QL).put(j)
    ths = [threading.Thread(target=loop) for _ in range(min(jobs, len(todo)))]
    for t in ths: t.start()
    for t in ths: t.join()
    SUT[su][1] = time.time()
    if not suite_done(su) and OPT.get('--stop-on-fail'): SKIP_BY[0] = su
cpu_total = resource.getrusage(resource.RUSAGE_CHILDREN); cpu_total = cpu_total.ru_utime + cpu_total.ru_stime

allok = True; S = []
for su in WANT:
    ok, L = block(su); allok &= ok; S += L + ['']
slow = sorted(res, key=lambda r: -r[4])[:5]
S.append('slowest jobs: ' + '; '.join('%s %.0f s' % (' '.join(a), dt) for g, a, ok, s, dt, out in slow))
S.append('run dir %s' % RUN)
S.append('wall %.1f min with %d processes (%d jobs, cpu %.1f min); %s' % ((time.time() - t0) / 60, jobs, NTOT, cpu_total / 60, 'ALL OK' if allok else 'FAILURES'))
with open(os.path.join(RUN, 'summary.txt'), 'w') as f: f.write('\n'.join(S) + '\n')
plog('finished: %s (%s)' % ('ALL OK' if allok else 'FAILURES', rel(os.path.join(RUN, 'summary.txt'))))
print('==== summary (%s)\n' % rel(os.path.join(RUN, 'summary.txt')) + '\n'.join(S), flush=True)
sys.exit(0 if allok else 1)
