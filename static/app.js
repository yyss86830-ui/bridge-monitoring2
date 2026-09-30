(function(){
  const root=document.documentElement;
  const toggle=document.getElementById('themeToggle');
  function setTheme(theme){root.dataset.theme=theme;try{localStorage.setItem('bridge-theme',theme)}catch(e){}; if(window.bridgeCharts){window.bridgeCharts.forEach(c=>{c.options.plugins.legend.labels.color=getComputedStyle(root).getPropertyValue('--ink');c.options.scales?.y?.ticks&&(c.options.scales.y.ticks.color=getComputedStyle(root).getPropertyValue('--muted'));c.update()})}}
  if(toggle){toggle.addEventListener('click',()=>setTheme(root.dataset.theme==='dark'?'light':'dark'))}
  document.querySelectorAll('[data-count]').forEach(el=>{const target=Number(el.dataset.count)||0;let n=0;const step=Math.max(1,Math.ceil(target/18));const timer=setInterval(()=>{n=Math.min(target,n+step);el.textContent=n;if(n>=target)clearInterval(timer)},35)});
  window.bridgeCharts=[];
  const css=()=>getComputedStyle(root);
  const main=document.getElementById('mainChart');
  if(main && window.stats){window.bridgeCharts.push(new Chart(main,{type:'doughnut',data:{labels:['Хорошее','Требует внимания','Критическое'],datasets:[{data:[window.stats.good,window.stats.warning,window.stats.critical],backgroundColor:['#16a34a','#f59e0b','#ef4444'],borderWidth:0,hoverOffset:8}]},options:{responsive:true,maintainAspectRatio:false,cutout:'68%',plugins:{legend:{position:'bottom',labels:{color:css().getPropertyValue('--ink'),padding:18,usePointStyle:true}}}}}))}
  const ac=document.getElementById('analyticsChart');
  if(ac && window.analyticsData){const map={'Хорошее':0,'Требует внимания':0,'Критическое':0};window.analyticsData.forEach(x=>{if(map[x.condition]!==undefined)map[x.condition]=Number(x.n)||0});window.bridgeCharts.push(new Chart(ac,{type:'bar',data:{labels:Object.keys(map),datasets:[{label:'Количество объектов',data:Object.values(map),backgroundColor:['#16a34a','#f59e0b','#ef4444'],borderRadius:10,borderSkipped:false}]},options:{responsive:true,maintainAspectRatio:false,scales:{x:{grid:{display:false},ticks:{color:css().getPropertyValue('--muted')}},y:{beginAtZero:true,ticks:{precision:0,color:css().getPropertyValue('--muted')},grid:{color:css().getPropertyValue('--line')}}},plugins:{legend:{display:false},tooltip:{displayColors:false}}}}))}
  document.querySelectorAll('[data-ripple]').forEach(el=>el.addEventListener('click',function(e){const r=document.createElement('span');r.className='ripple';const rect=this.getBoundingClientRect();r.style.left=(e.clientX-rect.left)+'px';r.style.top=(e.clientY-rect.top)+'px';this.appendChild(r);setTimeout(()=>r.remove(),600)}));
})();
function copyText(t){navigator.clipboard?.writeText(t).then(()=>toast('Координаты скопированы'))}
function toast(msg){let x=document.createElement('div');x.className='toast';x.textContent=msg;document.body.appendChild(x);setTimeout(()=>x.classList.add('show'),10);setTimeout(()=>{x.classList.remove('show');setTimeout(()=>x.remove(),250)},2200)}
