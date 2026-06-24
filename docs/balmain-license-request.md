# Balmain — Formal License Request for Virtual Try-On Integration

**Document Reference:** TRYONYOU-BLM-LIC-2025-001  
**Date:** June 24, 2026  
**Status:** DRAFT — Pending Legal Review  
**Patent Reference:** PCT/EP2025/067317

---

## 1. Executive Summary

TRYONYOU (operated by ABVETOS SAS) formally requests a non-exclusive digital licensing agreement with **Balmain SAS** (Pierre Balmain Group) to integrate Balmain garment imagery and brand assets into our patented real-time virtual try-on platform.

The integration would power the **"Dress Me in Balmain"** module — a physics-driven virtual fitting experience that uses cloth simulation, body pose tracking, and material-specific drape algorithms to render Balmain garments on the user's body in real time.

---

## 2. Requesting Entity

| Field | Value |
|-------|-------|
| **Company** | ABVETOS SAS |
| **Trading Name** | TRYONYOU |
| **Registered Address** | Paris, France |
| **SIREN** | [To be completed] |
| **Contact** | [CEO Name] |
| **Email** | licensing@tryonyou.com |
| **Patent** | PCT/EP2025/067317 — Virtual Fitting Intelligence |

---

## 3. Scope of License Requested

### 3.1 Digital Assets Required

| Asset Type | Description | Usage Context |
|-----------|-------------|---------------|
| **Product Photography** | High-resolution garment images (PNG, transparent background) | Real-time overlay on user's body via Canvas 2D / WebGL |
| **Brand Wordmark** | "BALMAIN" logotype for UI attribution | Header and garment card attribution |
| **Collection Metadata** | Garment names, collection season, fabric composition | UI display and physics material mapping |
| **Fabric Specifications** | Technical textile data (weight, composition, stiffness) | Physics simulation accuracy (cloth drape behavior) |

### 3.2 Usage Rights Requested

- **Territory:** Worldwide (digital only)
- **Duration:** 24 months, renewable
- **Platform:** TRYONYOU web application (tryonyou.com, app.tryonyou.com)
- **Channels:** Desktop web, mobile web, native app (iOS/Android)
- **Exclusivity:** Non-exclusive
- **Modification:** Garment images will NOT be modified; they will be rendered as-is with physics-based deformation (cloth simulation)
- **Attribution:** Full brand attribution on every garment display

### 3.3 Explicitly Excluded

- No physical reproduction of garments
- No sale of Balmain products through our platform (unless separate commercial agreement)
- No modification of brand identity or trademark
- No use in contexts that could damage brand reputation

---

## 4. Technical Integration Description

### 4.1 Physics-Driven Rendering

Our platform uses a **Verlet integration cloth physics engine** to simulate fabric behavior in real time. Each Balmain garment is mapped to a specific `FabricMaterial` profile based on its textile composition:

```
Material: Neoprene Satin (Blazer Croisé Structuré Pierre)
- Structural Stiffness: 0.97
- Shear Stiffness: 0.90
- Bend Stiffness: 0.75
- Particle Mass: 1.6 kg/m²
- Gravity Scale: 0.80
```

This ensures that each garment drapes, moves, and responds to body movement in a physically accurate manner — maintaining the integrity of Balmain's design intent.

### 4.2 Body Tracking

We use **MediaPipe Pose Landmarker** (33 body keypoints) to track the user's body in real time via their device camera. The garment is anchored to shoulder landmarks and collides with a torso capsule derived from hip/shoulder geometry.

### 4.3 Zero-Size Philosophy

Our platform operates under a **"Zero-Size" protocol** — we never display, store, or communicate traditional clothing sizes (S, M, L, etc.) to the user. Instead, we use relative body geometry and fabric physics to determine fit. This aligns with Balmain's commitment to inclusive fashion.

---

## 5. Commercial Proposition

### 5.1 Revenue Model Options

We propose the following commercial structures for Balmain's consideration:

| Model | Description |
|-------|-------------|
| **A. Revenue Share** | X% of attributable conversions (users who try Balmain virtually → purchase on balmain.com) |
| **B. Flat License Fee** | Annual licensing fee for garment imagery and brand usage |
| **C. Hybrid** | Reduced flat fee + lower revenue share percentage |
| **D. Pilot (Zero Cost)** | 6-month pilot with no fees; data sharing on engagement metrics |

### 5.2 Value Proposition for Balmain

- **Reduced Returns:** Virtual try-on reduces return rates by 30-50% (industry data)
- **Engagement:** Average session time 4.2 minutes vs 0.8 minutes on standard e-commerce
- **Innovation Positioning:** First luxury house with physics-based virtual fitting
- **Data Insights:** Anonymized body geometry analytics for collection design
- **Sustainability:** Fewer returns = lower carbon footprint (ESG alignment)

---

## 6. Brand Protection Guarantees

1. All garment imagery displayed in a **premium, luxury-appropriate context** (dark UI, gold accents, editorial typography)
2. No garment imagery used alongside competing brands in the same viewport
3. Full editorial control granted to Balmain over which garments appear
4. Immediate takedown capability if any brand guideline violation is detected
5. Quarterly brand compliance audits
6. No user-generated content featuring Balmain imagery can be exported/shared without watermark

---

## 7. Pilot Deployment Plan

| Phase | Timeline | Scope |
|-------|----------|-------|
| **Phase 1** | Month 1-2 | 6 garments from AW25 collection |
| **Phase 2** | Month 3-4 | Full AW25 + Cruise 2025 (20 garments) |
| **Phase 3** | Month 5-6 | Haute Couture SS25 integration |
| **Phase 4** | Month 7+ | Full catalog integration with seasonal updates |

---

## 8. Contact for Response

Please direct all responses and inquiries to:

**TRYONYOU — Licensing Department**  
Email: licensing@tryonyou.com  
Phone: +33 (0)1 XX XX XX XX  

**Balmain Contact (to be confirmed):**  
Balmain SAS — Digital Partnerships  
44 Rue François 1er, 75008 Paris, France  
Email: digital@balmain.com (public contact)

---

## 9. Legal Notice

This document constitutes a formal expression of interest and does not create any binding obligation on either party. Any licensing agreement would be subject to separate contract negotiation and execution by authorized representatives of both entities.

All intellectual property referenced herein remains the exclusive property of its respective owners. TRYONYOU's patented technology (PCT/EP2025/067317) is the exclusive property of ABVETOS SAS.

---

*Document prepared by TRYONYOU Engineering — Architecture Division*  
*Classification: CONFIDENTIAL — For Balmain internal review only*
