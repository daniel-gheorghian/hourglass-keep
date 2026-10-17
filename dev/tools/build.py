import sys,re
src,out,swpath,ver=sys.argv[1:5]
s=open(src).read()
s=re.sub(r"const APP_VERSION='[^']*';","const APP_VERSION='%s';"%ver,s)
head,rest=s.split('<style>',1); style,body=rest.split('</style>',1)
extra='''<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Dawnward">
'''
boot='''
<script>
(function(){
  var note=document.getElementById('offlineNote');
  try{if(navigator.storage&&navigator.storage.persist)navigator.storage.persist();}catch(e){}
  if(!('serviceWorker' in navigator))return;
  var hadController=!!navigator.serviceWorker.controller,pending=false;
  navigator.serviceWorker.register('./sw.js').catch(function(){});
  navigator.serviceWorker.ready.then(function(){if(note)note.textContent='Saved on this device for offline play. Progress saves as you play.';});
  // A new version took over: reload now if on the title screen, otherwise as soon as the player returns to it.
  function tryReload(){var h=window.__HK;if(!h||h.mode==='title'){location.reload();return true;}return false;}
  navigator.serviceWorker.addEventListener('controllerchange',function(){if(!hadController){hadController=true;return;}if(!tryReload())pending=true;});
  setInterval(function(){if(pending&&tryReload())pending=false;},1500);
})();
</script>
'''
html='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'+head.strip()+'\n'+extra+'<style>'+style+'</style>\n</head>\n<body>\n'+body.strip()+'\n'+boot+'</body>\n</html>\n'
open(out,'w').write(html)
sw=open(swpath).read()
sw=re.sub(r"const CACHE = 'hourglass-keep-v\d+';","const CACHE = 'hourglass-keep-v%s';"%ver,sw)
open(swpath,'w').write(sw)
print('built',len(html),'bytes; cache v'+ver)
