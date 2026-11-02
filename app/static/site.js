(function(){
var d=document.documentElement,t=null;
try{t=localStorage.getItem('dg-theme')}catch(e){}
if(t!=='light'&&t!=='dark')t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
d.setAttribute('data-theme',t);
var L=[['/','Home','home'],['/check','Check an order','check'],['/how-it-works','How it works','how'],['/dataset','Dataset','dataset'],['/results','Results','results'],['/about','About','about']];
var LOGO='<svg width="34" height="34" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="var(--primary)"/><path d="M16 6l8 3v6c0 5-3.4 8.6-8 10-4.6-1.4-8-5-8-10V9z" fill="var(--on-primary)"/></svg>';
document.addEventListener('DOMContentLoaded',function(){
var page=document.body.getAttribute('data-page');
var h=document.createElement('header');h.className='top';
h.innerHTML='<div class="wrap bar"><a class="brand" href="/">'+LOGO+'DelayGuard</a>'+
'<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>'+
'<nav id="nav" aria-label="Main">'+L.map(function(x){return '<a href="'+x[0]+'"'+(x[2]===page?' aria-current="page"':'')+'>'+x[1]+'</a>'}).join('')+'</nav>'+
'<button class="icon-btn" id="themeBtn" type="button" aria-label="Switch theme"><svg class="i-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg><svg class="i-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button></div>';
document.body.insertBefore(h,document.body.firstChild);
var f=document.createElement('footer');f.className='foot';
f.innerHTML='<div class="wrap"><p>DelayGuard is a decision aid, not a guarantee. It estimates risk from order details known at order time.</p><div><a href="/docs">API docs</a><a href="https://github.com/Yashvigohel/delayguard">GitHub</a><a href="https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis">Dataset on Kaggle</a></div></div>';
document.body.appendChild(f);
var tb=document.getElementById('themeBtn');
function lab(){var k=d.getAttribute('data-theme')==='dark';tb.setAttribute('aria-label',k?'Switch to light theme':'Switch to dark theme')}
tb.addEventListener('click',function(){var n=d.getAttribute('data-theme')==='dark'?'light':'dark';d.setAttribute('data-theme',n);try{localStorage.setItem('dg-theme',n)}catch(e){}lab()});lab();
var mb=h.querySelector('.menu-btn'),nav=document.getElementById('nav');
mb.addEventListener('click',function(){var o=nav.classList.toggle('open');mb.setAttribute('aria-expanded',o?'true':'false')});
setTimeout(function(){document.querySelectorAll('.bars').forEach(function(b){b.classList.add('go')})},150);
});
})();
