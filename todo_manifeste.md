# Intégration manifeste TRYONYOU x Galeries Lafayette

## Nouvelle page
- [ ] `/manifeste` — page éditoriale longue (5 chapitres du document)

## Nouvelles sections home (à insérer après Solution)
- [ ] **ZeroSizeProtocol** — concept "Bien Divina" + scénario Gemelas + Privacy Firewall
- [ ] **AbvetosArchitecture** — table des 4 modules (PAU, ABVET, CAP, FTT) + Agente 70
- [ ] **ForteresseIP** — brevet PCT/EP2025/067317 + 8 super-claims + 8 marques + valorisation 120-400 M€
- [ ] **Roadmap** — 2026 / 2027-2028

## Mises à jour code
- [ ] Ajouter palette manifeste dans `index.css` (--manifeste-anthracite, --manifeste-or, --manifeste-beige)
- [ ] Ajouter route `/manifeste` dans App.tsx
- [ ] Ajouter lien "Manifeste" dans SiteHeader
- [ ] Insérer les 4 nouvelles sections dans Home.tsx (entre Solution et Technology)

## Déploiement
- [ ] Build production (TRYONYOU_VERCEL=1)
- [ ] Restore images, clean debug folder, strip analytics
- [ ] Deploy via scripts/deploy_vercel.py
- [ ] Smoke test toutes routes (/, /tryon, /catalogue, /investors, /footscan, /offre, /manifeste)
- [ ] Checkpoint final
