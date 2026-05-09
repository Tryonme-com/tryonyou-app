# TRYONYOU — Trois directions de design

## Direction 1 — « Maison Couture Nocturne » (probabilité 0.07)

**Mouvement** : Néo-couture parisienne contemporaine, inspirée des dossiers de presse Saint Laurent, Balmain Couture, et Hermès Editorial. Référence : la rigueur typographique d'un magazine *L'Officiel* croisée avec la sobriété d'un site Bottega Veneta.

**Principes fondamentaux** :
1. **Souveraineté du noir** : le noir profond (#0A0807) n'est pas un fond, c'est une matière — un drapé. Tout texte respire dans cette obscurité.
2. **L'or comme signature** : #C9A84C utilisé avec parcimonie chirurgicale — uniquement pour les ancres, les CTA, et les fines hairlines qui découpent les sections.
3. **Asymétrie éditoriale** : aucune section ne reproduit la grille d'une autre. Headlines décalés, légendes en marge, numérotation romaine pour les étapes.
4. **Pas de centrisme paresseux** : chaque section utilise une grille 12-col distincte avec décalage volontaire.

**Philosophie de couleur** : Noir absolu → graphite #1A1614 → or pâle #C9A84C → blanc cassé #F5EFE0 (pour les textes longs). Aucun gradient violet/rose. Aucune saturation tropicale.

**Paradigme de layout** : Sections en plein écran avec déplacement latéral interne (un titre à gauche colonne 1-4, contenu à droite 7-12). Le hero lui-même utilise un split-screen : une moitié vidéo / image, l'autre moitié typographie monumentale.

**Éléments signature** :
- Fines lignes horizontales en or (1px, opacity 0.4) qui tracent le rythme éditorial
- Numérotation en chiffres romains (I, II, III) pour les étapes — esthétique des défilés
- Petites capitales (font-variant: small-caps) pour les eyebrows de section

**Philosophie d'interaction** : Les transitions sont des fondus longs (700-900ms) avec courbes de Bézier inspirées du drapé tissu. Les boutons révèlent leur fond or en glissant depuis la gauche au hover. Aucun rebond, aucun bounce.

**Animation** :
- Apparition : `opacity 0→1` + `translateY(40px → 0)` sur scroll, durée 800ms, ease `cubic-bezier(0.16, 1, 0.3, 1)`
- Hero typo : caractères un par un en fade (stagger 30ms)
- Lignes-or : `scaleX 0→1` depuis la gauche
- Démo avatar : reveal progressif du wireframe en or sur le webcam feed

**Système typographique** :
- Display : **Playfair Display** 700/900 italic pour les hero titles (size: clamp(48px, 7vw, 96px), letter-spacing: -0.02em)
- Subtitle : **Playfair Display** 400 italic
- Body : **Inter** 400/500 (size: 17px sur desktop, 15px mobile, line-height: 1.7)
- Eyebrow : **Inter** 600 small-caps, letter-spacing: 0.18em, taille 11-12px en or
- Nombres / metrics : **Playfair Display** 600

---

## Direction 2 — « Atelier Industriel Or » (probabilité 0.06)

Néo-bauhaus appliqué au luxe — inspiration Off-White typographique avec discipline japonaise. Cadres techniques visibles, monospace ponctuel, brutalité maîtrisée.

**Principes** : grilles techniques apparentes, contrastes durs noir/blanc/or, chiffres en monospace, grandes capitales sans serif géant.

**Couleurs** : noir #000, blanc pur #FFF, or industriel #C9A84C, gris technique #2B2B2B.

**Layout** : grille 12-col stricte avec gutters visibles (lignes verticales 0.5px), tags techniques en monospace dans les coins (ex. "[002 / SOLUTION]"), encadrés rectangulaires.

**Typo** : Space Grotesk display + JetBrains Mono pour les métadonnées + Inter body. Beaucoup d'uppercase.

Trop technique pour des dirigeants Sézane/Sandro qui recherchent l'élégance feutrée du couture.

---

## Direction 3 — « Salon Privé Vénitien » (probabilité 0.04)

Inspiration palazzo italien, marbre, velours, dorures — esprit Brioni / Loro Piana. Beaucoup de textures riches (grain papier, bruit), beiges chauds, or rougeoyant.

**Couleurs** : ivoire #F2EAD8, ocre #B89968, bordeaux profond #4A1B1B, or chaud #D4AF37.

**Layout** : très centré, presque liturgique, ornements dorés.

Trop traditionaliste, manque l'aspect tech/biométrique requis par TRYONYOU. Trop de centrisme — exclu par le brief.

---

## Direction sélectionnée : **Maison Couture Nocturne** (Direction 1)

Cette direction satisfait simultanément :
- L'aspect **luxe parisien** attendu par les dirigeants Sézane/Sandro
- La **modernité tech** de la démo biométrique (l'or-sur-noir évoque l'overlay biométrique du Gemelo Digital)
- La contrainte **fond sombre + accent or #C9A84C**
- Les **typos Playfair Display + Inter** imposées
- L'évitement de l'IA-slop (asymétrie, italiques, hairlines, chiffres romains)
