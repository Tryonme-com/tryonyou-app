# TRYONYOU /tryon — refonte cinématique

- [x] Examiner TryOn.tsx actuel et overlayRenderer.ts
- [x] Implémenter machine d'états 4 phases (CAMERA → WIREFRAME → SWIRL → REVEAL)
- [x] Triangulation pose : connecter les landmarks en triangles dorés (#C5A46D)
- [x] Système de particules dorées (~280 particules, mouvement spirale)
- [x] Transition douce wireframe → swirl (~2.8 s) → reveal garment overlay matérialisé
- [x] Supprimer toute mesure numérique affichée à l'écran
- [x] Conserver side panel avec garment info
- [x] Build production sans script analytics + assets
- [x] Déployer sur Vercel et smoke test

---

# Mission Offre Pionnière Divine 2027 + 10 emails

## Phase 1 — Drive search
- [ ] Rechercher pitch deck / dossier TryOnYou dans Google Drive
- [ ] Récupérer le meilleur fichier (PDF/PPTX)

## Phase 2 — Lecture dossier commercial PDF fourni
- [ ] Lire `/home/ubuntu/upload/tryonyou_dossier_commercial.pdf`

## Phase 3 — Page /offre Divine 2027
- [ ] Composer client/src/pages/Offre.tsx (luxe noir+or, CTA admin@tryonyou.app)
- [ ] Ajouter route /offre dans App.tsx + lien dans SiteHeader
- [ ] Build + smoke test

## Phase 4 — Déploiement Vercel
- [ ] Build prod + deploy_vercel.py
- [ ] Vérifier https://tryonyou.app/offre HTTP 200

## Phase 5 — Gmail recherche
- [ ] Lister outils gmail MCP
- [ ] Rechercher fils existants pour chaque contact

## Phase 6 — Emails (10 contacts)
- [ ] 10 brouillons FR personnalisés
- [ ] Envoyer ceux dont l'adresse est vérifiée
- [ ] Lister ceux à compléter

## Phase 7 — Livraison
- [ ] Rapport + checkpoint


---

# /tryon v2.5 — refonte UX zéro-chiffre + Robert Engine + biométrie filtrée

## Modules techniques
- [ ] `lib/robert-engine.ts` (copié depuis upload, intégré au build TS)
- [ ] `lib/biometric.ts` — Filtre EMA stable, layer subtraction, gyroscope tilt, calcul métriques (sans chiffres exposés à l'UI), score de confiance
- [ ] `lib/landmarkLabels.ts` — 33 landmarks groupés en chapitres FR

## Refonte TryOn.tsx — flow 4 phases zéro-chiffre
- [ ] Phase **SCAN** : caméra + wireframe doré + scan animé sur la silhouette, JAMAIS de cm. Status "Verrouillage biométrique"
- [ ] Phase **MATCHING** : anneau de progression doré, "Analyse morphologique", "Comparaison avec la collection", défilement éclair de vignettes, "Ajustement parfait trouvé"
- [ ] Phase **PROJECTION** : Robert Engine drape le vêtement en suivant les landmarks lissés. Temps réel.
- [ ] Phase **BROWSE** : navigation entre garments avec mini re-MATCHING (~700 ms) entre transitions

## Overlays UI
- [ ] Indicateur "Robert Engine Active · [profil tissu]"
- [ ] Panneau Zero-Size (barres de confiance — sans chiffres)
- [ ] Mini-carte des 33 landmarks groupés FR, escamotable
- [ ] Sélecteur tissu inline pendant BROWSE (5 chips ronds dorés)

## Section B2B technique sous la caméra
- [ ] 33 points biométriques en 22 ms
- [ ] Filtrage Kalman/EMA stable
- [ ] Robert Engine — physique de tissu temps réel
- [ ] Protocole Zero-Size : zéro donnée manuelle
- [ ] Brevet PCT/EP2025/067317

## Déploiement
- [ ] Build TRYONYOU_VERCEL=1
- [ ] Copie médias dist/public/images/
- [ ] Strip analytics
- [ ] Deploy Vercel
- [ ] Verify routes 200
- [ ] webdev_save_checkpoint v2.5


---

# v2.6 — Consolidation architecturale + fix overlay sur tête

THE PROJECT (single source of truth):
- Local: `/home/ubuntu/tryonyou-app/`
- Vercel: `prj_vDPvZ4U1MD4t3CmKxfusBB7md2Fh` (project name: `tryonyou-app`)
- Domain: `tryonyou.app` (+ alias `tryonme.app`)

## Phase 1 — Inventaire
- [ ] `gh repo list` complet
- [ ] Inventaire `/home/ubuntu/repos/*` et `/home/ubuntu/Downloads/*`

## Phase 2 — Diff & valeur
- [ ] Lister par dépôt les fichiers de valeur (algos biométriques, Robert, sections UI, assets)
- [ ] Comparer aux fichiers déjà présents dans `tryonyou-app`

## Phase 3 — Bug fix + ports
- [ ] Robert Engine : hauteur basée sur `torsoH × lengthFactor`, pas sur AR image
- [ ] simpleRender fallback corrigé
- [ ] Ancrage `shoulderY` = haut du vêtement
- [ ] Test local dev

## Phase 4 — Deploy
- [ ] Build prod + copie médias + strip analytics
- [ ] Deploy sur `prj_vDPvZ4U1MD4t3CmKxfusBB7md2Fh`

## Phase 5 — Vérif
- [ ] HTTP 200 sur toutes les routes
- [ ] Bundle inclut Robert + Zero-Size + 33 points
- [ ] webdev_save_checkpoint v2.6
