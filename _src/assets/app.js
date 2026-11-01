(function(){const R=window.ROOT||'';const CAT={'2':"Chefs d'entreprise salariés",'3':'Cadres','4':'Professions intermédiaires','5':'Employés','6':'Ouvriers'};
const eur=n=>n?n.toLocaleString('fr-FR')+' €':'secret stat.';const norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));const url=r=>R+'metier/'+r[6]+'.html';
let D=null;const load=()=>D?Promise.resolve(D):fetch(R+'data.json').then(r=>r.json()).then(d=>(D=d));
const P=new URLSearchParams(location.search);
const q=document.getElementById('q');if(q){const ul=document.getElementById('sugg');let sel=-1,res=[];
 const draw=()=>{const s=norm(q.value.trim());if(!s){ul.style.display='none';return}load().then(d=>{const w=s.split(/\s+/);res=d.filter(r=>{const t=norm(r[1]+' '+r[0]);return w.every(x=>t.includes(x))}).slice(0,12);sel=-1;
  ul.innerHTML=res.length?res.map((r,i)=>`<li><a href="${url(r)}"><span>${esc(r[1])}</span><b>${eur(r[2])}</b></a></li>`).join(''):'<li><a href="'+R+'classement.html">Aucun résultat, voir le classement</a></li>';ul.style.display='block'})};
 q.addEventListener('input',draw);q.addEventListener('keydown',e=>{const li=ul.querySelectorAll('li');if(e.key==='ArrowDown'){sel=Math.min(sel+1,li.length-1)}else if(e.key==='ArrowUp'){sel=Math.max(sel-1,0)}else if(e.key==='Enter'){if(res[sel<0?0:sel])location.href=url(res[sel<0?0:sel]);return}else return;e.preventDefault();li.forEach((l,i)=>l.classList.toggle('on',i===sel))});
 document.addEventListener('click',e=>{if(!e.target.closest('.search'))ul.style.display='none'})}
document.querySelectorAll('.chip[data-cat]').forEach(b=>b.addEventListener('click',()=>location.href=R+'classement.html?cat='+b.dataset.cat));
const tb=document.querySelector('#tbl tbody');if(tb){const fq=document.getElementById('fq'),fc=document.getElementById('fc'),fs=document.getElementById('fs');if(P.get('cat'))fc.value=P.get('cat');if(P.get('q'))fq.value=P.get('q');
 const run=()=>load().then(d=>{const s=norm(fq.value.trim());let r=d.filter(x=>(!fc.value||x[0][0]===fc.value)&&(!s||norm(x[1]+' '+x[0]).includes(s)));const k=fs.value;
  r.sort(k==='asc'?(a,b)=>a[2]-b[2]:k==='eff'?(a,b)=>b[5]-a[5]:k==='az'?(a,b)=>a[1].localeCompare(b[1],'fr'):(a,b)=>b[2]-a[2]);
  document.getElementById('count').textContent=r.length+' métiers';tb.innerHTML=r.map((x,i)=>`<tr><td>${i+1}</td><td><a href="${url(x)}">${esc(x[1])}</a></td><td>${CAT[x[0][0]]||''}</td><td class="r"><b>${eur(x[2])}</b></td><td class="r">${eur(x[3])}</td><td class="r">${eur(x[4])}</td><td class="r">${x[5].toLocaleString('fr-FR')}</td></tr>`).join('')});
 [fq,fc,fs].forEach(el=>el.addEventListener('input',run));run()}
const ca=document.getElementById('ca');if(ca){const cb=document.getElementById('cb');load().then(d=>{const s=[...d].sort((a,b)=>a[1].localeCompare(b[1],'fr'));const o=s.map(r=>`<option value="${r[0]}">${esc(r[1])}</option>`).join('');ca.innerHTML=o;cb.innerHTML=o;
 ca.value=P.get('a')||'388A';cb.value=P.get('b')||'431F';const mx=Math.max(...d.map(r=>r[2]));
 const card=r=>`<section class="card"><h2><a href="${url(r)}">${esc(r[1])}</a></h2><div class="kpis"><div><b>${eur(r[2])}</b><span>net moyen</span></div><div><b>${eur(r[3])}</b><span>femmes</span></div><div><b>${eur(r[4])}</b><span>hommes</span></div><div><b>${r[5].toLocaleString('fr-FR')}</b><span>salariés</span></div></div></section>`;
 const run=()=>{const a=d.find(r=>r[0]===ca.value),b=d.find(r=>r[0]===cb.value);const diff=a[2]-b[2];document.getElementById('cmp').innerHTML=card(a)+card(b)+`<section class="card" style="grid-column:1/-1"><h2>Écart</h2><p><b>${esc(diff>=0?a[1]:b[1])}</b> gagne en moyenne <b>${eur(Math.abs(diff))}</b> net de plus par mois (${Math.round(Math.abs(diff)/Math.min(a[2],b[2])*100)} %).</p></section>`;history.replaceState(null,'','?a='+a[0]+'&b='+b[0])};
 ca.onchange=cb.onchange=run;run()})}
})();
