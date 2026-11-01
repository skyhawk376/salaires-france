#!/usr/bin/env python3
"""Salaires des offres en cours via l'API Adzuna (France). Budget d'appels contrôlé.
Usage: python3 refresh_adzuna.py [--budget N] [--reuse metier=fichier.json]
Identifiants lus dans .env (ADZUNA_APP_ID, ADZUNA_APP_KEY). Compteur cumulé : calls_used.txt.
Sortie : adzuna.json + lignes `const ADZ...` / `const ADZ_TS...` à coller dans la Page (EditCanvas)."""
import os,sys,json,statistics,datetime,urllib.request,urllib.parse
H=os.path.dirname(os.path.abspath(__file__))
env={k:os.environ[k] for k in ('ADZUNA_APP_ID','ADZUNA_APP_KEY') if k in os.environ}
if not env and os.path.exists(os.path.join(H,'.env')): env=dict(l.strip().split('=',1) for l in open(os.path.join(H,'.env')) if '=' in l)
OUT=os.environ.get('ADZUNA_OUT',os.path.join(H,'adzuna.json'))
METIERS=["développeur","infirmier","comptable","commercial","cuisinier","aide-soignant","chauffeur poids lourd","électricien","plombier","vendeur","enseignant","ingénieur","serveur","maçon","agent de sécurité","secrétaire","data analyst","mécanicien","pharmacien","avocat"]
args=sys.argv[1:]; budget=int(args[args.index('--budget')+1]) if '--budget' in args else 20
reuse=dict(a.split('=',1) for a in args if '=' in a and not a.startswith('--'))
CF=os.path.join(H,'calls_used.txt'); used=int(open(CF).read()) if os.path.exists(CF) else 0
calls=0
def annual(v):
    if v<100: return v*151.67*12      # horaire
    if v<10000: return v*12           # mensuel
    return v                          # annuel
out=[]
for m in METIERS:
    if m in reuse: d=json.load(open(os.path.join(H,reuse[m])))
    else:
        if calls>=budget: print('budget atteint, arrêt avant',m,file=sys.stderr); break
        q=urllib.parse.urlencode({'app_id':env['ADZUNA_APP_ID'],'app_key':env['ADZUNA_APP_KEY'],'what':m,'results_per_page':50,'what_exclude':'alternance apprenti apprentissage','content-type':'application/json'})
        calls+=1; open(CF,'w').write(str(used+calls))
        d=json.load(urllib.request.urlopen('https://api.adzuna.com/v1/api/jobs/fr/search/1?'+q))
    r=d.get('results',[]); vals=[]; pred=0
    for x in r:
        if x.get('salary_min') is None: continue
        if str(x.get('salary_is_predicted'))=='1': pred+=1; continue
        a=annual((x['salary_min']+(x.get('salary_max') or x['salary_min']))/2)
        if 12000<=a<=300000: vals.append(a)
    if vals:
        md=statistics.median(vals)
        out.append([m,d.get('count',0),len(vals),round(md),round(min(vals)),round(max(vals)),round(md/12),pred])
ts=datetime.datetime.now().astimezone().strftime('%d/%m/%Y %H:%M (heure de Paris)')
json.dump({'ts':ts,'rows':out},open(OUT,'w'),ensure_ascii=False)
print('appels ce run:',calls,'| cumul:',used+calls,file=sys.stderr)
print('const ADZ: [string, number, number, number, number, number, number, number][] = '+json.dumps(sorted(out,key=lambda x:-x[3]),ensure_ascii=False,separators=(',',':'))+';')
print('const ADZ_TS = '+json.dumps(ts)+';')
