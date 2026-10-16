# The regression suite in one command, spread over the machine's cores.
#   python3 suite.py quick     bot on floors 1-35 with one seed, plus the unit tests (while iterating)
#   python3 suite.py           before each commit: bot 4 seeds, forks, flag/family floors, metrics, unit tests
#   python3 suite.py release   before a release: all of that plus the fight runs and the render check
#   -j N                       number of Chromium processes (default: physical cores; more only slows a laptop down)
# The bot and render runs are split one floor (and seed) per job, so the whole suite takes about as long as its slowest
# single job instead of the sum of all of them. Each of the -j worker processes (suiteworker.py) starts ONE Chromium and runs
# its jobs in turn, every job in a fresh browser context (nothing leaks between jobs); the test scripts are the same files
# that run standalone. A job that hangs (per-job timeout) or kills its worker fails with a message, and the worker is replaced.
# Prints one line per test, the five slowest jobs, and exits 1 on a failure.
import json, os, queue, re, resource, signal, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
args = sys.argv[1:]
mode = 'quick' if 'quick' in args else 'release' if 'release' in args else 'commit'
def physical_cores():
    try: return int(subprocess.run(['sysctl', '-n', 'hw.physicalcpu'], capture_output=True, text=True).stdout.strip())
    except Exception: return max(2, (os.cpu_count() or 4) // 2)
jobs = int(args[args.index('-j') + 1]) if '-j' in args else physical_cores()
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
        'hdtest.py', 'vertscan.py', 'lifttest.py', 'featurescan.py', 'orphanscan.py', 'mazescan.py', 'glauto.py']
J += [('hinttest', ['hinttest.py', str(n), str(n)], tail_check()) for n in [1, 3, 6, 9, 10, 12, 16, 20, 24, 27, 32, 35]] # hints until learned: moves the bot uses are learned, their hints stop (floor 1 also checks the old-save migration)
J += [('grablabel', ['grablabel.py', str(n), str(n)], tail_check()) for n in [1, 3, 6, 9, 12, 16, 20, 24, 27, 32]] # the Grab button's label: scenes, fit and screenshots on floor 1; on the others the bot's Grab presses must have been announced
J += [(u[:-3], [u], tail_check()) for u in unit if os.path.exists(os.path.join(HERE, u))]
J += [('gratepeek', ['gratepeek.py', '6', '27', '6'], tail_check(r'tested [1-9]\d* bad 0 '))] # crouching on a grating shows the flask below
# longest jobs first so the tail of the run isn't one slow floor
RANK = {'featbot fight': 0, 'run2 fight': 1, 'rendersmoke': 2, 'puzzlescan': 3, 'primtest': 3, 'lifttest': 3, 'featbot': 3, 'metrics40': 4, 'featurescan': 4, 'forktest': 5, 'run2': 6}
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
    def run(self, argv):
        """-> (returncode, output); returncode -1 for a worker that died or hung."""
        try:
            if self.pr is None or self.pr.poll() is not None: self.kill(); self.start()
            timer = threading.Timer(TIMEOUT, lambda p=self.pr: os.killpg(p.pid, signal.SIGKILL)); timer.start(); t = time.time()
            try:
                self.pr.stdin.write(json.dumps({'argv': argv}) + '\n'); self.pr.stdin.flush()
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
    rc, out = w.run(a)
    if rc == -1: ok, s = False, out.strip().splitlines()[-1][:160] if out.strip() else 'exit -1'   # worker died or the job timed out
    else:
        ok, s = chk(out)          # (read even when the script exited 1, e.g. on a SLOW RUN, so the pass counts stay whole)
        if rc != 0: ok = False; s = s if isinstance(s, tuple) else (out.strip().splitlines()[-1][:160] if out.strip() else 'exit %d' % rc)
    return g, a, ok, s, time.time() - t, out

t0 = time.time(); res = []; Q = queue.Queue()
for j in J: Q.put(j)
def loop():
    w = Worker()
    try:
        while True:
            try: j = Q.get_nowait()
            except queue.Empty: return
            res.append(go(j, w))
    finally: w.stop()
ths = [threading.Thread(target=loop) for _ in range(min(jobs, len(J)))]
for t in ths: t.start()
for t in ths: t.join()
cpu_total = resource.getrusage(resource.RUSAGE_CHILDREN); cpu_total = cpu_total.ru_utime + cpu_total.ru_stime

groups = {}
for g, a, ok, s, dt, out in res: groups.setdefault(g, []).append((a, ok, s, dt, out))
allok = True
print('%-13s %-4s %7s  %s' % ('test', 'ok', 'job s', 'result'))
for g, rs in groups.items():
    ok = all(r[1] for r in rs); allok &= ok; cpu = sum(r[3] for r in rs)
    if g.startswith('featbot') or g == 'p4bot':
        tot = [r[2] for r in rs if isinstance(r[2], tuple)]
        p, n, h = (sum(x[i] for x in tot) for i in range(3))
        dmg_ok = g == 'featbot fight' or h == 0; ok &= dmg_ok; allok &= dmg_ok
        s = 'passed %d / %d, runs with damage %d' % (p, n, h)
    elif g == 'forktest':
        tot = [r[2] for r in rs if isinstance(r[2], tuple)]
        s = 'forks ok %d / %d' % (sum(x[0] for x in tot), sum(x[1] for x in tot))
    elif g.startswith('run2'):
        tot = [r[2] for r in rs if isinstance(r[2], tuple)]
        p, n, h = (sum(x[i] for x in tot) for i in range(3))
        dmg_ok = g == 'run2 fight' or h == 0; ok &= dmg_ok; allok &= dmg_ok
        s = 'passed %d / %d, runs with damage %d' % (p, n, h)
    elif g.startswith('rendersmoke'):
        s = 'floors %d, %s' % (len(rs), 'no errors' if ok else 'ERRORS')
    else:
        s = rs[0][2]
    print('%-13s %-4s %7.0f  %s' % (g, 'yes' if ok else 'NO', cpu, s))
    if not ok:
        for a, o, ss, dt, out in rs:
            if not o or g.startswith(('run2', 'featbot')) or g == 'forktest':
                fails = [l for l in out.splitlines() if l.startswith(('{', 'SLOW RUN')) or 'Error' in l][:3]
                if fails or not o: print('    ', ' '.join(a), '|', ' / '.join(x[:200] for x in fails) or ss)
slow = sorted(res, key=lambda r: -r[4])[:5]
print('slowest jobs: ' + '; '.join('%s %.0f s' % (' '.join(a), dt) for g, a, ok, s, dt, out in slow))
print('wall %.1f min with %d processes (%d jobs, cpu %.1f min); %s' % ((time.time() - t0) / 60, jobs, len(J), cpu_total / 60, 'ALL OK' if allok else 'FAILURES'))
sys.exit(0 if allok else 1)
