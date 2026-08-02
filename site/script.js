(function(){
var KEY='sp-reading-mode';
var root=document.documentElement;
var bt=document.getElementById('mode-tech');
var bp=document.getElementById('mode-plain');
if(bt&&bp){
  var set=function(m,save){
    var plain=m==='plain';
    root.classList.toggle('plain',plain);
    bt.classList.toggle('on',!plain);
    bp.classList.toggle('on',plain);
    bt.setAttribute('aria-pressed',String(!plain));
    bp.setAttribute('aria-pressed',String(plain));
    if(save){try{localStorage.setItem(KEY,m)}catch(e){}}
  };
  bt.addEventListener('click',function(){set('tech',true)});
  bp.addEventListener('click',function(){set('plain',true)});
  var saved='tech';
  try{saved=localStorage.getItem(KEY)||'tech'}catch(e){}
  set(saved,false);
}
var button=document.getElementById('copy-command');
var command=document.getElementById('verify-command');
if(button&&command){
  button.addEventListener('click',async function(){
    try{
      await navigator.clipboard.writeText(command.textContent.trim());
      button.textContent='Copied';
      setTimeout(function(){button.textContent='Copy'},1600);
    }catch(_){button.textContent='Select text'}
  });
}
})();
