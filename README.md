# Hourglass Keep

An endless run-and-climb platformer that installs to a phone's home screen and plays offline.

## Install on a phone

1. Open the GitHub Pages address for this repo on the phone.
2. iPhone: Safari → Share → Add to Home Screen. Android: Chrome menu → Install app.
3. Open the installed app once while online. The title screen confirms when it is saved for offline play.

## Files

- `index.html` – the whole game
- `sw.js` – offline cache; bump `CACHE` when publishing a new version so phones pick it up
- `manifest.webmanifest`, `icons/` – home-screen name and icons
