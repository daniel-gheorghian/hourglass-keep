# One suite.py worker: starts Chromium once, then runs test scripts sent to it (one JSON line per job on stdin) and answers
# with one JSON line each ({"rc", "out"}). The test scripts are NOT changed: each is run with runpy under its own sys.argv and
# its output captured, and playwright's sync_playwright is replaced by a stand-in whose chromium.launch() hands back the shared
# browser, so a script's `b.new_page()` / `b.new_context()` opens a fresh browser CONTEXT (own localStorage, own cache) and its
# `b.close()` closes only the contexts it opened. A context per job is what keeps the jobs isolated; the Chromium is reused.
# If a job leaves the browser dead, the next job starts a new one. A hung job is killed from outside by suite.py (the whole
# process group), which then starts a new worker. Run by suite.py; not meant to be started by hand.
import contextlib, io, json, os, runpy, sys, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPLY = sys.stdout            # the protocol channel; jobs get their own captured stdout
sys.path.insert(0, HERE)
os.chdir(HERE)

import playwright.sync_api as sa
_real = sa.sync_playwright().start()
_browser = [None]
def browser():
    b = _browser[0]
    if b is None or not b.is_connected(): _browser[0] = b = _real.chromium.launch()
    return b

class BrowserProxy:
    """What a script sees as `b = p.chromium.launch()`: new_page/new_context make a fresh context in the shared browser."""
    def __init__(self, ctxs): self._ctxs = ctxs
    def new_context(self, **kw):
        c = browser().new_context(**kw); self._ctxs.append(c); return c
    def new_page(self, **kw): return self.new_context(**kw).new_page()
    def close(self): self._close_contexts()
    def _close_contexts(self):
        while self._ctxs:
            try: self._ctxs.pop().close()
            except Exception: pass
    def __getattr__(self, k): return getattr(browser(), k)

class Chromium:
    def __init__(self, ctxs): self._ctxs = ctxs
    def launch(self, **kw):
        assert not kw, 'shared browser: launch() options are not supported (%r)' % kw
        return BrowserProxy(self._ctxs)

class PW:
    def __init__(self, ctxs): self.chromium = Chromium(ctxs)
    def __enter__(self): return self
    def __exit__(self, *a): return False

def run(job):
    ctxs = []
    sa.sync_playwright = lambda: PW(ctxs)
    argv = job['argv']; out = io.StringIO(); rc = 0
    old = sys.argv; sys.argv = [os.path.join(HERE, argv[0])] + argv[1:]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try: runpy.run_path(sys.argv[0], run_name='__main__')
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
                if isinstance(e.code, str): print(e.code)
            except BaseException:
                rc = 1; traceback.print_exc()
    finally:
        sys.argv = old
        BrowserProxy(ctxs)._close_contexts()      # whatever the script left open
    return {'rc': rc, 'out': out.getvalue()}

if __name__ == '__main__':
    browser()
    REPLY.write(json.dumps({'ready': True}) + '\n'); REPLY.flush()
    for line in sys.stdin:
        if not line.strip(): continue
        r = run(json.loads(line))
        REPLY.write(json.dumps(r) + '\n'); REPLY.flush()
    try: _browser[0] and _browser[0].close()
    except Exception: pass
    _real.stop()
