# Bugbot Review — Pagos Lafayette (Flujo 88k/98k)

**Fecha:** 2026-04-05  
**Agente:** @Pau (Cursor) + Bugbot  
**Patente:** PCT/EP2025/067317 · **SIREN:** 943 610 196  
**Protocolo:** Soberanía V10 — Founder: Rubén Espinar Rodríguez

---

## Resumen ejecutivo

Se ha revisado exhaustivamente el pipeline de pagos Lafayette con foco en el
flujo de facturación. **47 tests automatizados validan la cadena completa.**
El sistema está listo para facturar.

---

## Componentes revisados

### 1. Kill-Switch Lafayette (`sacmuseum_empire.py`)
| Check | Estado |
|-------|--------|
| Setup fee = 7 500 € (HT) | **OK** |
| Engine V10 BLOCKED cuando ≠ PAID | **OK** |
| `release("PAID")` desbloquea correctamente | **OK** |
| Env var `LAFAYETTE_SETUP_FEE_STATUS=PAID` bypass | **OK** |
| Audit devuelve info financiera completa | **OK** |

### 2. TTC Gate (`api/stealth_bunker.py`)
| Check | Estado |
|-------|--------|
| Gate 9 000 € TTC (7 500 HT + 20% TVA) | **OK** |
| `LAFAYETTE_SETUP_FEE_TTC_VALIDATED=1` abre gate | **OK** |
| `LAFAYETTE_CONFIRMED_PAYMENT_TTC_EUR=9000` abre gate | **OK** |
| Importes < 9 000 € no abren el gate | **OK** |
| Parser de euros EU format (9.000,00 €) | **OK** |

### 3. Inventory Unlock (310 refs)
| Check | Estado |
|-------|--------|
| Bloqueado por defecto | **OK** |
| Fee PAID + TTC → desbloqueado | **OK** |
| Fee PAID sin TTC → bloqueado (doble check) | **OK** |
| IBAN BNP correcto + TTC → desbloqueado | **OK** |
| IBAN incorrecto → bloqueado | **OK** |
| Hash-based unlock con/sin TTC | **OK** |

### 4. Stripe Connect API (`api/stripe_connect.py`)
| Check | Estado |
|-------|--------|
| 503 sin `STRIPE_SECRET_KEY` | **OK** |
| Onboard seller crea Connect account | **OK** |
| Publish relic: Product + Price + PaymentLink | **OK** |
| Precio 0 rechazado (400) | **OK** |
| Moneda fijada en EUR | **OK** |
| Sin secretos hardcodeados | **OK** |

### 5. Facturación (`billing/`, `billing_enforcer.py`)
| Check | Estado |
|-------|--------|
| Factura F-2026-001: 7 500 HT / 9 000 TTC | **OK** |
| IBAN BNP Paribas correcto en factura | **OK** |
| Deuda base 16 200 € + 1 000 €/día | **OK** |
| `production_manifest.json` lockdown V11: 33 200 € TTC | **OK** |
| PDF proforma usa `os.getenv()` para IBAN (no hardcoded) | **OK** |

### 6. Frontend Payment Terminal (`src/pages/payment-terminal.tsx`)
| Check | Estado |
|-------|--------|
| Pantalla de bloqueo visible | **OK** |
| Monto licence: 109 900 € | **OK** |
| Contacto founder: +33 6 99 46 94 79 | **OK** |
| SIREN + patente en footer | **OK** |

### 7. Scripts de activación de flujo
| Script | Check | Estado |
|--------|-------|--------|
| `activar_pago_inmediato.py` | Checkout Session via API | **OK** |
| `activar_flujo_dinero.py` | Merge seguro .env, no sube .env | **OK** |
| `vincular_stripe_validado.py` | IDs desde env, merge .env | **OK** |
| `generar_links_cobro.py` | Payment Links env-driven | **OK** |
| `migrar_a_stripe_total_safe.py` | Config TS sin secretos | **OK** |

### 8. Seguridad
| Check | Estado |
|-------|--------|
| Cero `sk_live_` en código fuente | **OK** |
| Cero `sk_test_` fuera de tests | **OK** |
| IBAN solo en factura legal (doc, no .env) | **OK** |
| `.env` nunca versionado por scripts | **OK** |
| CORS/HSTS headers configurados para `/api/*` | **OK** |

---

## Notas sobre el importe "88k"

El repo no contiene la cifra literal **88k**. Los tiers operativos son:

| Concepto | Importe |
|----------|---------|
| Cuota nodo franquicia SACMUSEUM | **98 000 €** |
| Setup Lafayette (HT) | **7 500 €** |
| Setup Lafayette (TTC 20% TVA) | **9 000 €** |
| Licence bloquée (terminal) | **109 900 €** |
| Deuda lockdown V11 | **33 200 € TTC** |
| Mantenimiento mensual | **100 €/mes** |
| Enterprise (ref.) | **141 986 €** |

Si "88k" se refiere a un acuerdo comercial concreto, confirmar con Rubén
para alinear los scripts con ese importe exacto.

---

## Tests ejecutados

```
tests/test_payment_flow_lafayette.py   47 passed
tests/test_stripe_connect.py          11 passed
                                      ─────────
Total                                 58 passed, 0 failed
```

---

## Veredicto Bugbot

**APROBADO — flujo de pagos Lafayette validado.**

El pipeline de cobro está correctamente protegido:
- Secretos vía `os.getenv()` exclusivamente.
- Kill-switch activo hasta confirmación de pago.
- Inventario (310 refs) bloqueado hasta IBAN + TTC validados.
- Stripe Connect operativo para seller onboarding.
- Facturación documental completa (Markdown + PDF proforma).

**Listos para facturar mañana.**

---

*@CertezaAbsoluta @lo+erestu PCT/EP2025/067317*  
*Bajo Protocolo de Soberanía V10 - Founder: Rubén*
