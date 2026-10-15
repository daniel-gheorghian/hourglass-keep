# Slow-run guard for the bot scripts. A run that costs too much per game frame fails the test, naming the floor and seed, so a
# regression like the v41 particle leak (fight runs up to 50x slower) shows up as a failure and not as a long wait.
#   g = SlowGuard('run2'); r = g.run(pg, JS, args, 'floor 5 seed 3')   # like pg.evaluate, but timed; r['frames'] is the cost base
#   ...; sys.exit(g.finish(ok))                                         # prints the slow runs, returns the exit code
# Cost is the CPU time of the page's main thread (Chrome's ThreadTime, read over CDP), per game frame, so a busy machine does not
# make a healthy run look slow; if CDP is not available it falls back to wall time. Budget: HK_MS_PER_FRAME (default MS_FRAME,
# averaged over the run, bot included) and HK_RUN_WALL (default WALL_S seconds of wall time for a single run, a loose cap for a
# run that hangs or crawls); environment overrides win. The defaults leave 4x or more headroom over the slowest healthy run.
import os, time
MS_FRAME = 0.3   # healthy bot runs cost 0.02 to 0.1 ms/frame; the v41 particle leak made fight runs up to 50x slower
WALL_S = 300     # healthy single runs take under 30 s even on a loaded machine (rendersmoke, which renders on top, has its own budgets)
class SlowGuard:
    def __init__(self, name, ms=None, wall=None):
        self.name = name; self.slow = []; self.runs = 0; self.frames = 0; self.secs = 0.0; self.worst = (0.0, '')
        self.msf = float(os.environ.get('HK_MS_PER_FRAME', ms or MS_FRAME)); self.wall = float(os.environ.get('HK_RUN_WALL', wall or WALL_S))
    def note(self, label, secs, frames, cpu=None):
        cpu = secs if cpu is None else cpu
        self.runs += 1; self.frames += frames or 0; self.secs += cpu
        per = 1000 * cpu / frames if frames else 0
        if per > self.worst[0]: self.worst = (per, label)
        if (frames and per > self.msf) or secs > self.wall:
            self.slow.append('SLOW RUN %s %s: %.2f ms/frame over %s frames, %.1f s cpu, %.1f s wall (budget %.2f ms/frame, %.0f s wall)' % (self.name, label, per, frames, cpu, secs, self.msf, self.wall))
    def run(self, pg, js, arg, label, frames=lambda r: r.get('frames') if isinstance(r, dict) else None):
        t = time.time(); c0 = self.cpu(pg); r = pg.evaluate(js, arg); dt = time.time() - t; c1 = self.cpu(pg)
        self.note(label, dt, frames(r), c1 - c0 if c0 is not None and c1 is not None else dt); return r
    def cpu(self, pg):
        try:
            if not hasattr(pg, '_hk_cdp'):
                pg._hk_cdp = pg.context.new_cdp_session(pg); pg._hk_cdp.send('Performance.enable')
            return next(m['value'] for m in pg._hk_cdp.send('Performance.getMetrics')['metrics'] if m['name'] == 'ThreadTime')
        except Exception: return None
    def finish(self, ok=True):
        print('slowest run: %.2f ms/frame (%s), mean %.2f ms/frame over %d runs' % (self.worst[0], self.worst[1], 1000 * self.secs / max(1, self.frames), self.runs))
        for s in self.slow[:10]: print(s)
        return 0 if ok and not self.slow else 1
