# jb-drf-billing Roadmap (Plan Completo Consolidado)

Roadmap operativo basado en `PLAN.md`, con estados de avance reales.

## Leyenda de estado

- ✅ `LISTO`
- 🟡 `PROGRESO`
- ⚪ `NO INICIADO`
- ⛔ `BLOQUEADO` (cuando aplique)

## Alcance del roadmap

Este roadmap cubre el **plan completo**:
- Backend reusable `jb-drf-billing` (patrón `jb-drf-auth`)
- Integración backend en `finzenio-api`
- `jb-expo-dev-kit` + `finzenio-app`
- `jb-react-web-dev-kit` + `mentalysis-frontend`
- Expansión futura: `payments` (cobros directos) + `invoicing` (fiscal)

## Resumen ejecutivo

| Área | Estado | Nota |
|---|---:|---|
| Fase 0 - Diseño consolidado | ✅ | Plan completo consolidado y corregido (abstract models + settings + adapters + integraciones) |
| Fase 1 - Core `jb-drf-billing` | ✅ | Scaffold reusable funcional con endpoints base, models abstractos, config/checks |
| Fase 2 - Integración `finzenio-api` (base) | ✅ | App local `billing`, modelos concretos, admin, migración inicial, URLs, settings |
| Fase 3 - RevenueCat backend (base funcional) | 🟡 | Sync/webhook/idempotencia básica implementados; falta endurecer y pruebas reales |
| Fase 4 - Stripe backend | ⚪ | Stubs existen, implementación real pendiente |
| Fase 5 - Comercial avanzado (sin fiscal) | ⚪ | No iniciado |
| Fase 6 - `payments` (cobros directos) | ⚪ | No iniciado (solo diseñado conceptualmente) |
| Fase 7 - `invoicing` fiscal | ⚪ | No iniciado |
| Expo DevKit + FinZenio app | ⚪ | No iniciado |
| Web DevKit + Mentalysis frontend | ⚪ | No iniciado |

---

## Repos / rutas involucradas

| Componente | Ruta | Estado |
|---|---|---:|
| `jb-drf-billing` | `/Users/joel_barron/Developer/personal/my-libs/python/jb-drf-billing` | ✅ |
| `finzenio-api` | `/Users/joel_barron/Developer/usbix/finzenio/finzenio-api` | 🟡 |
| `jb-expo-dev-kit` | `/Users/joel_barron/Developer/personal/my-libs/npm/jb-expo-dev-kit` | ⚪ |
| `finzenio-app` | `/Users/joel_barron/Developer/usbix/finzenio/finzenio-app` | ⚪ |
| `jb-react-web-dev-kit` | `/Users/joel_barron/Developer/personal/my-libs/npm/jb-react-web-dev-kit` | ⚪ |
| `mentalysis-frontend` | `/Users/joel_barron/Developer/usbix/mentalysis/mentalysis-frontend` | ⚪ |

---

## Decisiones de arquitectura (baseline del plan)

| Decisión | Valor | Estado |
|---|---|---:|
| Nombre de librería | `jb-drf-billing` | ✅ |
| Patrón backend | Tipo `jb-drf-auth` (modelos abstractos + migraciones locales + settings) | ✅ |
| Scope v1 | Suscripciones + entitlements | ✅ |
| Scope futuro | `payments` (cobros directos) + `invoicing` (fiscal) | ✅ |
| Titularidad de cobro | `User` | ✅ |
| Scope de entitlements | `HYBRID` (`USER` / `PROFILE`) | ✅ |
| Mobile provider strategy | RevenueCat-first híbrido | ✅ |
| Web checkout | Stripe | ✅ |
| Fiscal v1 | Fuera de alcance | ✅ |
| Personalización | config + hooks + signals + overrides puntuales | ✅ |

---

## Fase 0 - Diseño / Arquitectura (Consolidado)

### Objetivo
Dejar la arquitectura completa definida antes de implementación profunda.

### Estado
✅ `LISTO`

### Entregables (planificados y consolidados)

| Entregable | Estado | Nota |
|---|---:|---|
| Arquitectura híbrida RevenueCat + Stripe | ✅ | Definida |
| Patrón `jb-drf-auth` para billing | ✅ | Definido y aplicado en implementación inicial |
| Modelo `HYBRID` (`USER`/`PROFILE`) | ✅ | Definido |
| Estrategia multi-producto por `app_slug` | ✅ | Definida |
| Límite de alcance (sin lógica de negocio de reservas en la librería) | ✅ | Definido |
| Ruta de expansión `payments` / `invoicing` | ✅ | Definida |

---

## Fase 1 - Core Backend Reusable `jb-drf-billing` (sin providers reales completos)

### Objetivo
Tener la base reusable y configurable lista para integrarse en proyectos.

### Estado
✅ `LISTO` (base)

### 1.1 Estructura del package

| Item | Estado | Nota |
|---|---:|---|
| `pyproject.toml` | ✅ | Creado |
| `README.md` | ✅ | Base |
| `apps.py` | ✅ | AppConfig + `checks` en `ready()` |
| `conf.py` | ✅ | Defaults + getters + providers config |
| `checks.py` | ✅ | Validaciones base de config |
| `signals.py` | ✅ | Señales base |
| `permissions.py` | ✅ | Permission base autenticada |
| `exceptions.py` / `utils.py` | ✅ | Base |

### 1.2 Dominio abstracto (modelos)

| Modelo abstracto | Estado | Nota |
|---|---:|---|
| `AbstractBillingApp` | ✅ | Multi-producto por `app_slug` |
| `AbstractBillingCustomer` | ✅ | `provider_customer_ids` JSON |
| `AbstractPlan` | ✅ | Por app |
| `AbstractPlanPrice` | ✅ | Incluye mappings Stripe/RevenueCat |
| `AbstractSubscription` | ✅ | Estado consolidado interno |
| `AbstractEntitlement` | ✅ | Feature reusable |
| `AbstractPlanEntitlement` | ✅ | Relación plan-feature |
| `AbstractEntitlementGrant` | ✅ | Scope `USER`/`PROFILE` |
| `AbstractBillingEvent` | ✅ | Idempotencia/auditoría |
| `AbstractCheckoutIntent` | ✅ | Preparado para Stripe/web |

### 1.3 API reusable (base)

| Endpoint / Grupo | Estado | Nota |
|---|---:|---|
| `GET /billing/catalog` | ✅ | Funcional (DB/settings provider base) |
| `GET /billing/status` | ✅ | Funcional base |
| `GET /billing/entitlements` | ✅ | Funcional base |
| `POST /billing/access/check` | ✅ | Funcional base |
| `POST /billing/mobile/sync` | ✅ | Conectado a RevenueCat adapter (Fase 3) |
| `POST /billing/mobile/restore/ack` | ✅ | Ack base |
| `POST /billing/web/checkout-session` | ✅ | Stub |
| `POST /billing/web/portal-session` | ✅ | Stub |
| `POST /billing/web/change-plan` | ✅ | Stub |
| `POST /billing/webhooks/revenuecat` | ✅ | Conectado a RevenueCat adapter (Fase 3) |
| `POST /billing/webhooks/stripe` | ✅ | Stub |

### 1.4 Servicios / extensibilidad

| Componente | Estado | Nota |
|---|---:|---|
| Catalog providers (`DB`, `SETTINGS`) | ✅ | Base funcional |
| Access policy base | ✅ | `USER/PROFILE` ownership básico |
| Feature visibility policy base | ✅ | Base |
| Entitlement resolver | ✅ | Resolución efectiva base |
| Reemplazo de grants por suscripción | ✅ | Base funcional (Fase 3) |
| Hooks configurables (settings keys) | ✅ | Definidos en config |
| Señales billing_* | ✅ | Definidas |

### 1.5 Testing del package

| Prueba | Estado | Nota |
|---|---:|---|
| `test_conf` | ✅ | Pasa |
| `test_checks` | ✅ | Pasa |
| `test_urls` | ✅ | Pasa |
| Tests de dominio reales con modelos concretos | ⚪ | Pendiente |
| Tests RevenueCat adapter/webhooks | ⚪ | Pendiente |
| Tests Stripe adapter/webhooks | ⚪ | Pendiente |

### 1.6 Artefactos repo / DX

| Item | Estado | Nota |
|---|---:|---|
| Repo Git inicializado | ✅ | Commit inicial hecho |
| `.gitignore` | ✅ | Python/Django + caches + IDE + `PLAN.md` |
| `roadmap.md` | ✅ | Este documento |

---

## Fase 2 - Integración Backend Inicial en `finzenio-api`

### Objetivo
Validar el patrón abstracto + migraciones locales + wiring real del proyecto.

### Estado
✅ `LISTO` (base), con pendientes de catálogo y migración legacy

### 2.1 App local `api/billing`

| Item | Estado | Nota |
|---|---:|---|
| `api/billing/apps.py` | ✅ | Creado |
| `api/billing/models.py` | ✅ | Modelos concretos extienden abstractos |
| `api/billing/admin.py` | ✅ | Admin básico |
| `api/billing/migrations/0001_initial.py` | ✅ | Generada |

### 2.2 Integración en settings / urls

| Item | Estado | Nota |
|---|---:|---|
| `jb_drf_billing` en `INSTALLED_APPS` | ✅ | Integrado |
| `api.billing` en `LOCAL_APPS` | ✅ | Integrado |
| `JB_DRF_BILLING` en settings | ✅ | Base configurada |
| `path("billing/", include(...))` | ✅ | Integrado en API |

### 2.3 Validación técnica realizada

| Validación | Estado | Nota |
|---|---:|---|
| `makemigrations billing` | ✅ | Generada (con `--skip-checks` por checks de auth) |
| `django.setup()` e imports billing | ✅ | OK |
| `manage.py check` limpio | ⛔ | Bloqueado por checks existentes de `jb_drf_auth` (social CLIENT_IDS faltantes) |

### 2.4 Pendientes de Fase 2

| Pendiente | Estado | Nota |
|---|---:|---|
| Seed de catálogo FinZenio (`BillingApp`, `Plan`, `PlanPrice`, `Entitlement`, `PlanEntitlement`) | ⚪ | Pendiente |
| Migración de compatibilidad `authentication.User.stripe_customer_id` -> `BillingCustomer.provider_customer_ids["stripe"]` | ⚪ | Pendiente |
| Cleanup/remoción campo legacy `stripe_customer_id` (fase posterior) | ⚪ | Pendiente |

---

## Fase 3 - RevenueCat Backend (Mobile)

### Objetivo
Soportar flujo backend para mobile: sync + webhook + estado consolidado + grants.

### Estado
🟡 `PROGRESO` (base funcional implementada, falta endurecer)

### 3.1 RevenueCat adapter / sync / webhook

| Item | Estado | Nota |
|---|---:|---|
| `RevenueCatAdapter` base real | ✅ | Implementado |
| `build_app_user_id` / parse `app_user_id` | ✅ | Formato `app_slug:user:{id}` |
| Sync por API `/v1/subscribers/{app_user_id}` | ✅ | Implementado |
| Parse de subscriber subscriptions | ✅ | Implementado |
| Mapeo `product_id -> PlanPrice.revenuecat_product_id` | ✅ | Implementado |
| Upsert `Subscription` (`REVENUECAT`) | ✅ | Implementado |
| Recalculo de `EntitlementGrant` desde `PlanEntitlement` | ✅ | Implementado |
| `POST /billing/mobile/sync` conectado | ✅ | Implementado |
| `POST /billing/webhooks/revenuecat` conectado | ✅ | Implementado |
| Idempotencia vía `BillingEvent` | ✅ | Implementado (create-or-ignore por `provider,event_id`) |

### 3.2 Verificación de webhook / seguridad

| Item | Estado | Nota |
|---|---:|---|
| Validación simple por header secret configurable | ✅ | Implementada (`authorization` por default) |
| Verificación de firma robusta / múltiples estrategias | 🟡 | Pendiente de endurecimiento |
| Rotación de secrets / múltiples secretos | ⚪ | Pendiente |

### 3.3 Manejo de estado / edge cases RevenueCat

| Item | Estado | Nota |
|---|---:|---|
| Estado activo/expirado/canceled inferido base | ✅ | Implementado |
| Detección avanzada de grace period / past_due / pause | 🟡 | Parcial; pendiente mapear eventos/fields completos |
| Eventos fuera de orden | 🟡 | Idempotencia está; reconciliación avanzada pendiente |
| Reconciliación periódica | ⚪ | Pendiente |
| Support assignment de grants por `PROFILE` (metadata) | ⚪ | Pendiente |

### 3.4 Testing / QA backend de Fase 3

| Item | Estado | Nota |
|---|---:|---|
| Smoke tests de import/compilación | ✅ | OK |
| Tests unitarios del adapter RevenueCat | ⚪ | Pendiente |
| Fixtures reales de RevenueCat webhooks | ⚪ | Pendiente |
| Pruebas de duplicados / reintentos | ⚪ | Pendiente |
| Pruebas de eventos fuera de orden | ⚪ | Pendiente |

### 3.5 Bloqueos actuales conocidos

| Bloqueo | Estado | Nota |
|---|---:|---|
| `manage.py check` limpio en `finzenio-api` | ⛔ | Bloqueado por checks existentes de `jb_drf_auth` (social CLIENT_IDS faltantes) |
| E2E local en SQLite del proyecto | ⛔ | Una migración SQL previa del proyecto falla en SQLite (ajeno a billing) |

---

## Fase 4 - Stripe Backend (Web)

### Objetivo
Implementar checkout/portal/webhooks Stripe y consolidación backend.

### Estado
⚪ `NO INICIADO`

### 4.1 Adapter Stripe

| Item | Estado | Nota |
|---|---:|---|
| `StripeBillingAdapter` real | ⚪ | Stub existe |
| Crear checkout session | ⚪ | Pendiente |
| Crear portal session | ⚪ | Pendiente |
| Sync customer/subscription | ⚪ | Pendiente |
| Mapeo `stripe_price_id -> PlanPrice` | ⚪ | Pendiente |

### 4.2 Endpoints web

| Endpoint | Estado | Nota |
|---|---:|---|
| `POST /billing/web/checkout-session` | ⚪ | Stub |
| `POST /billing/web/portal-session` | ⚪ | Stub |
| `POST /billing/web/change-plan` | ⚪ | Stub |

### 4.3 Webhooks Stripe

| Item | Estado | Nota |
|---|---:|---|
| `POST /billing/webhooks/stripe` procesamiento real | ⚪ | Stub |
| Verificación de firma | ⚪ | Pendiente |
| Idempotencia con `BillingEvent` | ⚪ | Pendiente |
| Reordenamiento de eventos | ⚪ | Pendiente |

---

## Fase 5 - Comercial Avanzado (sin fiscal)

### Objetivo
Cubrir capacidades comerciales de suscripción sin entrar a facturación fiscal.

### Estado
⚪ `NO INICIADO`

| Capacidad | Estado | Nota |
|---|---:|---|
| Trials | ⚪ | |
| Promos / cupones | ⚪ | |
| Upgrades / downgrades + prorrateo | ⚪ | |
| `cancel_at_period_end` UX/backend completo | ⚪ | |
| Grace period handling UX/state | ⚪ | |
| Reactivación | ⚪ | |
| Historial de eventos/estado para UI | ⚪ | |
| Multi-moneda básica MXN/USD | ⚪ | |
| Flags de compliance por región/plataforma en catálogo | 🟡 | Base hardcoded existe; falta diseño final configurable |

---

## Fase 6 - `payments` (Cobros directos) - Futuro

### Objetivo
Agregar cobros directos (one-time) sin mezclar lógica de negocio de reservas/citas.

### Estado
⚪ `NO INICIADO`

| Item | Estado | Nota |
|---|---:|---|
| Diseño módulo `jb_drf_billing.payments` | ⚪ | |
| `PaymentProviderAdapter` base | ⚪ | |
| Charges / payment intents / captures / refunds | ⚪ | |
| Webhooks de pagos directos | ⚪ | |
| Auditoría / conciliación básica | ⚪ | |
| Integración con dominios externos (solo vía metadata/refs) | ⚪ | Sin meter modelos de reservas en la librería |

---

## Fase 7 - `invoicing` Fiscal - Futuro

### Objetivo
Facturación fiscal (ej. CFDI) y conciliación fiscal/contable.

### Estado
⚪ `NO INICIADO`

| Item | Estado | Nota |
|---|---:|---|
| Captura de datos fiscales | ⚪ | |
| Integración proveedor fiscal | ⚪ | |
| Emisión CFDI / tax invoices | ⚪ | |
| Reconciliación fiscal/contable | ⚪ | |
| Descarga/consulta de comprobantes | ⚪ | |

---

## Frontend y Proyectos Integradores (parte del plan completo)

## Fase F1 - `jb-expo-dev-kit` (`subscriptions`)

### Estado
⚪ `NO INICIADO`

| Item | Estado | Nota |
|---|---:|---|
| Nuevo módulo `@joelbarron/expo-dev-kit/subscriptions` | ⚪ | |
| `JBSubscriptionsProvider` | ⚪ | |
| `useJBSubscriptions()` | ⚪ | |
| `useJBEntitlements()` | ⚪ | |
| `useJBPurchasePlan()` | ⚪ | |
| `useJBRestorePurchases()` | ⚪ | |
| `useJBPaywall()` | ⚪ | |
| `JBPremiumFeatureGuard` | ⚪ | |
| `JBPaywallScreen` | ⚪ | |
| `syncBillingStatus()` | ⚪ | |
| `JBAppConfig.subscriptions` (types + validation) | ⚪ | |

## Fase F2 - `finzenio-app` integración mobile

### Estado
⚪ `NO INICIADO`

| Item | Estado | Nota |
|---|---:|---|
| Config `subscriptions` en `global-config.ts` | ⚪ | |
| Wiring provider en root layout | ⚪ | |
| Feature gating premium modules | ⚪ | |
| Pantalla/flujo premium-paywall usando DevKit | ⚪ | |
| Sync post-purchase / restore | ⚪ | |

## Fase W1 - `jb-react-web-dev-kit` (`billing`)

### Estado
⚪ `NO INICIADO`

| Item | Estado | Nota |
|---|---:|---|
| Nuevo módulo `@joelbarron/react-web-dev-kit/billing` | ⚪ | |
| `JBBillingProvider` | ⚪ | |
| `useJBBillingStatus()` | ⚪ | |
| `useJBCheckout()` | ⚪ | |
| `useJBManageSubscription()` | ⚪ | |
| `JBPricingTable` | ⚪ | |
| `JBPlanCard` | ⚪ | |
| `JBSubscriptionBadge` | ⚪ | |
| `JBPremiumGuard` | ⚪ | |
| `JBAppConfig.subscriptions` (web types + validation) | ⚪ | |

## Fase W2 - `mentalysis-frontend` integración web

### Estado
⚪ `NO INICIADO`

| Item | Estado | Nota |
|---|---:|---|
| Config `subscriptions` | ⚪ | |
| Wiring `JBBillingProvider` | ⚪ | |
| Pantalla real de pricing/billing (no mock) | ⚪ | |
| Checkout/portal Stripe vía backend | ⚪ | |
| Feature guards por plan | ⚪ | |

---

## Endpoints del plan (matriz de estado)

| Endpoint | Fase | Estado | Nota |
|---|---:|---:|---|
| `GET /billing/catalog` | 1 | ✅ | Base funcional |
| `GET /billing/status` | 1 | ✅ | Base funcional |
| `GET /billing/entitlements` | 1 | ✅ | Base funcional |
| `POST /billing/access/check` | 1 | ✅ | Base funcional |
| `POST /billing/mobile/sync` | 3 | ✅ | RevenueCat sync base |
| `POST /billing/mobile/restore/ack` | 1/3 | ✅ | Ack base |
| `POST /billing/web/checkout-session` | 4 | ⚪ | Stub |
| `POST /billing/web/portal-session` | 4 | ⚪ | Stub |
| `POST /billing/web/change-plan` | 4 | ⚪ | Stub |
| `POST /billing/webhooks/revenuecat` | 3 | ✅ | RevenueCat webhook base |
| `POST /billing/webhooks/stripe` | 4 | ⚪ | Stub |

---

## Testing / QA (matriz del plan completo)

## Backend (`jb-drf-billing` + integraciones)

| Escenario | Estado | Nota |
|---|---:|---|
| Tests de config/checks/urls del package | ✅ | Pasando |
| Tests unitarios de grants `USER`/`PROFILE` | ⚪ | Pendiente |
| Tests de precedencia/expiración de grants | ⚪ | Pendiente |
| Tests multi-app isolation | ⚪ | Pendiente |
| Tests RevenueCat adapter (fixtures reales) | ⚪ | Pendiente |
| Tests idempotencia webhook RevenueCat | ⚪ | Pendiente |
| Tests Stripe adapter/webhooks | ⚪ | Pendiente |
| API tests `/catalog`, `/status`, `/access/check` con modelos concretos | ⚪ | Pendiente |
| API tests `/web/checkout-session`, `/webhooks/stripe` | ⚪ | Pendiente |
| Migración legacy `stripe_customer_id` test | ⚪ | Pendiente |

## Frontend / cross-platform

| Escenario | Estado | Nota |
|---|---:|---|
| Compra mobile -> acceso web | ⚪ | Pendiente |
| Compra web -> acceso mobile | ⚪ | Pendiente |
| Restore purchases mobile | ⚪ | Pendiente |
| Gating por `PROFILE` | ⚪ | Pendiente |
| Compliance flags por plataforma/país | ⚪ | Pendiente |
| Webhooks fuera de orden -> estado final correcto | ⚪ | Pendiente |

---

## Riesgos y mitigaciones (estado actual)

| Riesgo | Mitigación del plan | Estado |
|---|---|---:|
| Cambios de compliance móvil | Flags por plataforma/país en catálogo; no hardcode en frontend | 🟡 |
| Drift entre provider y backend | Webhooks + sync endpoint + reconciliación | 🟡 |
| Vendor lock-in RevenueCat | Modelo interno + adapters desacoplados | ✅ |
| Inflar v1 con “completo comercial” | Fases 3/4/5 separadas | ✅ |
| Acoplar billing a auth | `jb-drf-billing` separado con patrón tipo `jb-drf-auth` | ✅ |

---

## Notas operativas actuales

- ✅ Repo `jb-drf-billing` inicializado con commit inicial.
- ✅ `PLAN.md` está ignorado en `.gitignore` (documento local de referencia).
- 🟡 RevenueCat backend está funcional en base, pero falta endurecer mapping/fixtures/eventos reales.
- ⛔ `manage.py check` en `finzenio-api` no está limpio por checks existentes de `jb_drf_auth` (social providers), no por billing.
- ⛔ Prueba E2E local con SQLite del proyecto puede fallar por migraciones SQL previas del proyecto (ajenas a billing).

---

## Próximos pasos recomendados (orden)

| Prioridad | Paso | Estado |
|---:|---|---:|
| 1 | Seed catálogo FinZenio + migración legacy `stripe_customer_id` | ⚪ |
| 2 | Endurecer Fase 3 RevenueCat (fixtures reales + tests + firma webhook) | 🟡 |
| 3 | Implementar Fase 4 backend Stripe | ⚪ |
| 4 | `jb-expo-dev-kit/subscriptions` + `finzenio-app` | ⚪ |
| 5 | `jb-react-web-dev-kit/billing` + `mentalysis-frontend` | ⚪ |
