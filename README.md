# Salaires France
Site statique : salaires de 361 métiers (INSEE, base Tous salariés 2024, net mensuel moyen EQTP) + salaires des offres d'emploi en cours (API Adzuna, échantillon de test).
Site : https://skyhawk376.github.io/salaires-france/

- `_src/build_site.py` génère toutes les pages (`SITE_OUT=.. python3 build_site.py` depuis `_src`).
- `_src/refresh_adzuna.py` relève les offres Adzuna (clés via secrets `ADZUNA_APP_ID` / `ADZUNA_APP_KEY`, jamais dans le site).
- `_src/refresh.yml` (à déplacer dans `.github/workflows/`, le jeton utilisé pour publier n’avait pas le droit `workflow`) : déclenchement **manuel** uniquement (compte test limité à 25 appels). Avec la formule payante, décommenter le bloc `schedule` pour un relevé quotidien.
