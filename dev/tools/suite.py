# The regression suite in one command, spread over the machine's cores.
#   python3 suite.py quick     bot on floors 1-27 with one seed, plus the unit tests (while iterating)
#   python3 suite.py           before each commit: bot 4 seeds, forks, flag/family floors, metrics, unit tests
#   python3 suite.py release   before a release: all of that plus the fight runs and the render check
#   -j N                       number of Chromium processes (default: physical cores; more only slows a laptop down)
# The bot and render runs are split one floor per job (each job its own Chromium), so the whole suite takes about
# as long as its slowest single test instead of the sum of all of them. Prints one line per test and exits 1 on a failure.
import os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
args = sys.argv[1:]
mode = 'quick' if 'quick' in args else 'release' if 'release' in args else 'commit'
def physical_cores():
    try: return int(subprocess.run(['sysctl', '-n', 'hw.physicalcpu'], capture_output=True, text=True).stdout.strip())
    except Exception: return max(2, (os.cpu_count() or 4) // 2)
jobs = int(args[args.index('-j') + 1]) if '-j' in args else physical_cores()
FLOORS = range(1, 28)

# (group, argv, check(stdout) -> (ok, summary)); groups with several jobs are merged into one line.
def run2_check(out):
    m = re.search(r'passed (\d+) / (\d+).*runs with damage (\d+)', out)
    return (bool(m), (int(m[1]), int(m[2]), int(m[3])) if m else None)
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
J += [('run2', ['run2.py', str(n), str(n), str(seeds)], run2_check) for n in FLOORS]
if mode == 'release':
    J += [('run2 fight', ['run2.py', str(n), str(n), '2', 'fight'], run2_check) for n in FLOORS]
    J += [('rendersmoke', ['rendersmoke.py', str(n), str(n)], render_check) for n in FLOORS]
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
    J += [('featbot fight', ['featbot.py', '3', 'fight', 'flags', str(n)], feat_check) for n in [9, 18, 24, 25, 27]]
unit = ['forkscan.py', 'respawnplates.py', 'puzzlescan.py', 'slabresume.py', 'primtest.py',
        'hdtest.py', 'vertscan.py', 'lifttest.py', 'featurescan.py', 'orphanscan.py', 'mazescan.py']
J += [(u[:-3], [u], tail_check()) for u in unit if os.path.exists(os.path.join(HERE, u))]
# longest jobs first so the tail of the run isn't one slow floor
RANK = {'featbot fight': 0, 'run2 fight': 1, 'rendersmoke': 2, 'featbot': 3, 'metrics40': 4, 'featurescan': 4, 'forktest': 5, 'run2': 6}
def floor_of(a): return max([int(x) for x in a[1:] if x.isdigit()] or [0])
J.sort(key=lambda j: (RANK.get(j[0], 7), -floor_of(j[1])))

def go(j):
    g, a, chk = j; t = time.time()
    p = subprocess.run([PY] + a, cwd=HERE, capture_output=True, text=True)
    out = p.stdout + p.stderr
    ok, s = chk(out) if p.returncode == 0 else (False, out.strip().splitlines()[-1][:160] if out.strip() else 'exit %d' % p.returncode)
    return g, a, ok, s, time.time() - t, out

t0 = time.time(); res = []
with ThreadPoolExecutor(jobs) as ex:
    for r in ex.map(go, J): res.append(r)

groups = {}
for g, a, ok, s, dt, out in res: groups.setdefault(g, []).append((a, ok, s, dt, out))
allok = True
print('%-13s %-4s %7s  %s' % ('test', 'ok', 'cpu s', 'result'))
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
    elif g == 'rendersmoke':
        s = 'floors %d, %s' % (len(rs), 'no errors' if ok else 'ERRORS')
    else:
        s = rs[0][2]
    print('%-13s %-4s %7.0f  %s' % (g, 'yes' if ok else 'NO', cpu, s))
    if not ok:
        for a, o, ss, dt, out in rs:
            if not o or g.startswith(('run2', 'featbot')) or g == 'forktest':
                fails = [l for l in out.splitlines() if l.startswith('{') or 'Error' in l][:3]
                if fails or not o: print('    ', ' '.join(a), '|', ' / '.join(x[:200] for x in fails) or ss)
print('wall %.1f min with %d processes; %s' % ((time.time() - t0) / 60, jobs, 'ALL OK' if allok else 'FAILURES'))
sys.exit(0 if allok else 1)
