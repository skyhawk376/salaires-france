#!/usr/bin/env python3
"""Générateur statique : data/insee.json + data/adzuna.json -> site HTML multi-pages."""
import json,os,re,unicodedata,html,datetime
H=os.path.dirname(os.path.abspath(__file__))
BASE='https://skyhawk376.github.io/salaires-france/'
OUTD=os.environ.get('SITE_OUT',os.path.join(H,'dist'))
INSEE=json.load(open(os.path.join(H,'data/insee.json')))
ADZ=json.load(open(os.path.join(H,'data/adzuna.json')))
CAT={'2':"Chefs d'entreprise salariés",'3':'Cadres','4':'Professions intermédiaires','5':'Employés','6':'Ouvriers'}
# correspondance requête Adzuna -> codes PCS INSEE
MAP={'développeur':['388A','478A'],'infirmier':['431F'],'comptable':['543B','461D'],'commercial':['374D','463D'],'cuisinier':['636D'],
'aide-soignant':['526A'],'chauffeur poids lourd':['641A'],'électricien':['633A'],'plombier':['632F'],'vendeur':['554E','553C'],
'ingénieur':['388A','382A','384A'],'serveur':['561B'],'maçon':['632A'],'agent de sécurité':['534A'],'secrétaire':['542A'],
'data analyst':['372A'],'mécanicien':['634C'],'pharmacien':['344D'],'avocat':['312A']}
adz_by={}
for r in ADZ['rows']:
    for c in MAP.get(r[0],[]): adz_by[c]=r
def slug(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:80]
for x in INSEE: x['s']=slug(x['c']+' '+x['l']); x['l']=x['l'].strip()
eur=lambda n:(f"{n:,}".replace(',','\u202f')+' €') if n else 'secret stat.'
e=html.escape
ALLM=sorted(x['m'] for x in INSEE)
def rank(m): return sum(1 for v in ALLM if v>m)+1
FAV='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1d4ed8"/><text x="32" y="44" font-size="34" text-anchor="middle" fill="#fff" font-family="Arial" font-weight="700">€</text></svg>'
def page(path,title,desc,body,depth=0):
    p='../'*depth
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:locale" content="fr_FR"><meta name="twitter:card" content="summary">
<link rel="icon" href="{p}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{p}style.css"></head><body>
<header class="top"><div class="wrap nav"><a class="brand" href="{p}index.html"><span class="logo">€</span> Salaires France</a><nav><a href="{p}index.html">Accueil</a><a href="{p}classement.html">Classement</a><a href="{p}comparer.html">Comparer</a><a href="{p}offres.html">Offres en cours</a><a href="{p}methode.html">Méthode &amp; sources</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Données officielles : INSEE, base Tous salariés 2024 (salaire net mensuel moyen EQTP, secteur privé, publication annuelle). Offres en cours : API Adzuna, échantillon de test. Site indépendant, non affilié à l'INSEE ni à Adzuna. <a href="{p}methode.html">Méthode &amp; sources</a></div></footer>
<script>window.ROOT="{p}";</script><script src="{p}app.js" defer></script></body></html>'''
def bars(rows,depth=0):
    mx=max(r['m'] for r in rows)
    return '<ol class="bars">'+''.join(f'<li><a href="{"../"*depth}metier/{r["s"]}.html"><span class="bl">{e(r["l"])}</span><span class="bt"><span class="bf" style="width:{r["m"]/mx*100:.1f}%"></span></span><span class="bv">{eur(r["m"])}</span></a></li>' for r in rows)+'</ol>'
def badge(kind): return '<span class="badge off">Officiel · INSEE 2024 · annuel</span>' if kind=='o' else '<span class="badge live">En direct · offres Adzuna · échantillon test</span>'
out={}
srt=sorted(INSEE,key=lambda x:-x['m'])
cats=''.join(f'<button class="chip" data-cat="{k}">{e(v)}</button>' for k,v in CAT.items())
med=sorted(x['m'] for x in INSEE)[len(INSEE)//2]
out['index.html']=page('index.html','Salaires de tous les métiers en France (INSEE 2024 + offres en cours)',f'Salaire net mensuel moyen de {len(INSEE)} métiers en France d’après l’INSEE, et salaires des offres d’emploi en cours.',f'''
<section class="hero"><h1>Combien gagne-t-on dans chaque métier en France&nbsp;?</h1><p>Le salaire net mensuel moyen de <b>{len(INSEE)} professions</b> selon les dernières données officielles de l’INSEE (2024), complété par les salaires affichés dans les offres d’emploi en cours.</p>
<div class="search"><input id="q" type="search" placeholder="Rechercher un métier : infirmier, développeur, boulanger…" autocomplete="off" aria-label="Rechercher un métier"><ul id="sugg" class="sugg"></ul></div>
<div class="kpis"><div><b>{len(INSEE)}</b><span>métiers</span></div><div><b>{eur(med)}</b><span>salaire médian des métiers</span></div><div><b>{len(ADZ["rows"])}</b><span>métiers avec offres en direct</span></div></div></section>
<p class="note">{badge('o')} Les chiffres officiels sont mis à jour une fois par an : ce n’est pas du temps réel. {badge('l')} Relevé du {e(ADZ["ts"])}.</p>
<div class="grid2"><section class="card"><h2>Les 10 métiers les mieux payés</h2>{bars(srt[:10])}</section><section class="card"><h2>Les 10 métiers les moins payés</h2>{bars(srt[-10:][::-1])}</section></div>
<section class="card"><h2>Par catégorie</h2><div class="chips">{cats}</div><p class="muted">Cliquez une catégorie pour ouvrir le classement filtré.</p></section>''')
out['classement.html']=page('classement.html','Classement des salaires par métier en France','Classement filtrable et triable des salaires nets moyens de 361 métiers (INSEE 2024).',f'''
<h1>Classement des salaires</h1><p class="note">{badge('o')} Salaire net mensuel moyen en équivalent temps plein, secteur privé, 2024.</p>
<div class="filters"><input id="fq" type="search" placeholder="Filtrer par métier ou code PCS"><select id="fc"><option value="">Toutes catégories</option>{''.join(f'<option value="{k}">{e(v)}</option>' for k,v in CAT.items())}</select>
<select id="fs"><option value="desc">Salaire décroissant</option><option value="asc">Salaire croissant</option><option value="eff">Effectif</option><option value="az">A → Z</option></select></div>
<p id="count" class="muted"></p><div class="tablewrap"><table id="tbl"><thead><tr><th>#</th><th>Métier</th><th>Catégorie</th><th class="r">Net moyen</th><th class="r">Femmes</th><th class="r">Hommes</th><th class="r">Effectif</th></tr></thead><tbody></tbody></table></div>''')
out['comparer.html']=page('comparer.html','Comparer les salaires de deux métiers','Comparez le salaire net moyen, l’écart femmes-hommes et l’effectif de deux métiers.',f'''
<h1>Comparer deux métiers</h1><p class="note">{badge('o')}</p><div class="filters"><select id="ca"></select><select id="cb"></select></div><div id="cmp" class="grid2"></div>''')
arows=''.join(f'<tr><td>{e(r[0])}</td><td class="r">{r[1]:,}</td><td class="r">{r[2]}</td><td class="r"><b>{eur(r[6])}</b></td><td class="r">{eur(r[3])}</td><td class="r">{eur(r[4])} – {eur(r[5])}</td></tr>'.replace(',','\u202f') for r in ADZ['rows'])
out['offres.html']=page('offres.html','Salaires des offres d’emploi en cours (Adzuna)','Salaire brut médian affiché dans les offres d’emploi en ligne pour 20 métiers courants.',f'''
<h1>Salaires des offres en cours</h1><p class="note">{badge('l')} Relevé du {e(ADZ["ts"])}.</p>
<div class="warn"><b>Échantillon de test, à lire avec prudence.</b> Le compte Adzuna est en mode test : seules les 50 premières annonces par métier sont lues. Certaines médianes reposent sur très peu d’annonces, et des offres d’alternance à salaire fixe peuvent tirer les valeurs vers le bas. Les salaires estimés par Adzuna sont exclus. Montants bruts (avant cotisations), non comparables directement aux montants nets INSEE.</div>
<div class="tablewrap"><table><thead><tr><th>Recherche</th><th class="r">Offres en ligne</th><th class="r">Avec salaire</th><th class="r">Médiane brut/mois</th><th class="r">Médiane brut/an</th><th class="r">Min – max /an</th></tr></thead><tbody>{arows}</tbody></table></div>''')
out['methode.html']=page('methode.html','Méthode et sources','Sources, définitions et limites des données de salaires.',f'''
<h1>Méthode &amp; sources</h1><div class="prose">
<h2>Pas de temps réel pour les salaires officiels</h2><p>Aucune source publique ne publie en continu les salaires de tous les métiers. Les données officielles sont annuelles ; ce site affiche la dernière année disponible (2024) et la mettra à jour à chaque nouvelle publication.</p>
<h2>Données officielles : INSEE</h2><ul><li>Source : INSEE, base Tous salariés, millésime 2024, jeu <code>DS_DERA_PRIVE_ANNUEL</code>.</li><li>Mesure : salaire <b>net</b> mensuel <b>moyen</b> en équivalent temps plein (EQTP). La médiane n’est pas publiée à ce niveau de détail.</li><li>Nomenclature : PCS-ESE, 4 caractères ({len(INSEE)} professions).</li><li>Champ : salariés du secteur privé en France ; hors agriculture, particuliers employeurs et métiers surtout publics (ex. professeurs des écoles).</li><li>« secret stat. » : valeur non diffusée par l’INSEE (effectif trop faible).</li></ul>
<h2>Offres en cours : Adzuna</h2><ul><li>Source : API Adzuna (agrégateur d’offres d’emploi), offres en ligne en France.</li><li>Mesure : point milieu de la fourchette affichée, converti en brut annuel ; salaires estimés par Adzuna exclus, offres d’alternance exclues des recherches.</li><li>Limite : compte de test (50 annonces par métier). Une formule payante (environ 8 £/mois, 500 appels/jour) permettrait un relevé quotidien complet.</li><li>Correspondance avec les métiers INSEE établie à la main ; elle est indicative.</li></ul>
<h2>Liens</h2><ul><li><a href="https://www.data.gouv.fr/datasets/salaires-dans-le-secteur-prive-par-categorie-socioprofessionnelle-detaillee">data.gouv.fr – Salaires dans le secteur privé par catégorie socioprofessionnelle détaillée</a></li><li><a href="https://www.insee.fr/fr/statistiques/2021266">INSEE – Salaires dans le secteur privé en 2024</a></li><li><a href="https://www.insee.fr/fr/statistiques/2407703">INSEE – Dispersion des salaires par catégorie</a></li><li><a href="https://developer.adzuna.com">Adzuna – API</a></li></ul>
<p class="muted">Code et données : <a href="https://github.com/skyhawk376/salaires-france">github.com/skyhawk376/salaires-france</a>. Généré le {datetime.date.today().strftime('%d/%m/%Y')}.</p></div>''')
for x in INSEE:
    a=adz_by.get(x['c']); same=[y for y in srt if y['c'][:2]==x['c'][:2] and y['c']!=x['c']][:6]
    gap=f'<p>Écart femmes/hommes : <b>{round((x["h"]-x["f"])/x["h"]*100)} %</b> en défaveur des {"femmes" if x["h"]>x["f"] else "hommes"}.</p>' if x['f'] and x['h'] and x['h']!=x['f'] else ''
    live=f'''<section class="card"><h2>Offres d’emploi en cours</h2><p>{badge('l')}</p><div class="kpis"><div><b>{eur(a[6])}</b><span>médiane brut/mois</span></div><div><b>{a[2]}</b><span>annonces avec salaire lues</span></div><div><b>{a[1]:,}</b><span>offres en ligne (« {e(a[0])} »)</span></div></div><p class="muted">Relevé du {e(ADZ["ts"])}. Fourchette {eur(a[4])} – {eur(a[5])} brut/an. Échantillon de test : <a href="../offres.html">voir les limites</a>.</p></section>'''.replace(',','\u202f') if a else ''
    out[f'metier/{x["s"]}.html']=page(f'metier/{x["s"]}.html',f'Salaire {x["l"]} : {eur(x["m"])} net/mois (INSEE 2024)',f'Salaire net mensuel moyen des {x["l"]} en France : {eur(x["m"])} en équivalent temps plein (INSEE 2024).',f'''
<p class="crumbs"><a href="../index.html">Accueil</a> › <a href="../classement.html?cat={x["c"][0]}">{e(CAT.get(x["c"][0],""))}</a></p><h1>{e(x["l"])}</h1><p class="muted">Code PCS {x["c"]} · {e(CAT.get(x["c"][0],""))}</p>
<section class="card"><h2>Salaire officiel</h2><p>{badge('o')}</p><div class="kpis"><div><b>{eur(x["m"])}</b><span>net mensuel moyen</span></div><div><b>{eur(x["f"])}</b><span>femmes</span></div><div><b>{eur(x["h"])}</b><span>hommes</span></div><div><b>{x["e"]:,}</b><span>salariés (EQTP)</span></div></div>{gap}<p class="muted">Rang {rank(x["m"])} sur {len(INSEE)} métiers. Moyenne en équivalent temps plein, secteur privé.</p></section>{live}
<section class="card"><h2>Métiers proches</h2>{bars(same,1) if same else ''}</section><p><a class="btn" href="../comparer.html?a={x["c"]}">Comparer ce métier</a></p>'''.replace(f'{x["e"]:,}',f'{x["e"]:,}'.replace(',','\u202f')),1)
os.makedirs(os.path.join(OUTD,'metier'),exist_ok=True)
for k,v in out.items(): open(os.path.join(OUTD,k),'w').write(v)
open(os.path.join(OUTD,'favicon.svg'),'w').write(FAV)
idx=[[x['c'],x['l'],x['m'],x['f'],x['h'],x['e'],x['s']] for x in INSEE]
open(os.path.join(OUTD,'data.json'),'w').write(json.dumps(idx,ensure_ascii=False,separators=(',',':')))
for f in ('style.css','app.js'): open(os.path.join(OUTD,f),'w').write(open(os.path.join(H,'assets',f)).read())
today=datetime.date.today().isoformat()
open(os.path.join(OUTD,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE}{k}</loc><lastmod>{today}</lastmod></url>' for k in out)+'</urlset>')
open(os.path.join(OUTD,'robots.txt'),'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
open(os.path.join(OUTD,'.nojekyll'),'w').write('')
print(len(out),'pages')
