import express from 'express';
import Stripe from 'stripe';
const app = express();

/**
 * 🔱 CONFIGURACIÓN DEL CLIENTE STRIPE
 * Usamos el StripeClient para todas las peticiones como estándar de oro.
 */
const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY || '';

if (!STRIPE_SECRET_KEY) {
    console.error("❌ ERROR: Falta la STRIPE_SECRET_KEY. El búnker no puede operar.");
    process.exit(1);
}

const stripeClient = new Stripe(STRIPE_SECRET_KEY);

// Comisión de la plataforma por transacción (en céntimos; 500 = 5,00 €)
const APPLICATION_FEE_AMOUNT = parseInt(process.env.APPLICATION_FEE_AMOUNT || '500', 10);

// URL base del servidor (para success_url, cancel_url y onboarding redirects)
const BASE_URL = process.env.BASE_URL || '';

app.use(express.static('public'));

// Aplicar express.json() solo a rutas que no sean /webhook (webhook necesita el body sin parsear)
app.use((req, res, next) => {
    if (req.path === '/webhook') return next();
    express.json()(req, res, next);
});

// Base de datos simulada (En producción usa PostgreSQL o similar)
const db = {
    users: {},    // mapping: userId -> stripeAccountId
    products: []  // mapping: productId -> {accountId, name, price}
};

/**
 * 🔱 1. CREACIÓN DE CUENTA CONECTADA (V2 API)
 * El "Chask" inicial: Creamos la cuenta donde el usuario recibirá sus pagos.
 */
app.post('/create-account', async (req, res) => {
    try {
        const { userId, email, name } = req.body;

        const account = await stripeClient.v2.core.accounts.create({
            display_name: name,
            contact_email: email,
            identity: {
                country: 'us',
            },
            dashboard: 'express',
            defaults: {
                responsibilities: {
                    fees_collector: 'application',
                    losses_collector: 'application',
                },
            },
            configuration: {
                recipient: {
                    capabilities: {
                        stripe_balance: {
                            stripe_transfers: {
                                requested: true,
                            },
                        },
                    },
                },
            },
        });

        db.users[userId] = account.id;

        res.json({ accountId: account.id });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

/**
 * 🔱 2. ONBOARDING (ACCOUNT LINKS V2)
 * Generamos el enlace para que el usuario complete su perfil en Stripe.
 */
app.post('/onboard-user', async (req, res) => {
    const { accountId } = req.body;

    try {
        const accountLink = await stripeClient.v2.core.accountLinks.create({
            account: accountId,
            use_case: {
                type: 'account_onboarding',
                account_onboarding: {
                    configurations: ['recipient'],
                    refresh_url: `${BASE_URL}/onboard?accountId=${accountId}`,
                    return_url: `${BASE_URL}/onboard?accountId=${accountId}`,
                },
            },
        });

        res.json({ url: accountLink.url });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

/**
 * 🔱 3. VERIFICAR STATUS (API DIRECTA)
 */
app.get('/account-status/:accountId', async (req, res) => {
    try {
        const account = await stripeClient.v2.core.accounts.retrieve(req.params.accountId, {
            include: ["configuration.recipient", "requirements"],
        });

        const readyToReceivePayments =
            account?.configuration?.recipient?.capabilities?.stripe_balance?.stripe_transfers?.status === "active";
        const requirementsStatus = account.requirements?.summary?.minimum_deadline?.status;
        const onboardingComplete =
            requirementsStatus !== "currently_due" && requirementsStatus !== "past_due";

        res.json({ onboardingComplete, readyToReceivePayments });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

/**
 * 🔱 4. CREAR PRODUCTOS (NIVEL PLATAFORMA)
 */
app.post('/create-product', async (req, res) => {
    const { name, description, price, accountId } = req.body;

    if (!price || typeof price !== 'number' || price <= 0) {
        return res.status(400).json({ error: 'El precio debe ser un número positivo.' });
    }

    try {
        const product = await stripeClient.products.create({
            name: name,
            description: description,
            default_price_data: {
                unit_amount: price * 100, // Euros a céntimos
                currency: 'eur',
            },
            metadata: { connectedAccountId: accountId }
        });

        db.products.push({
            id: product.id,
            priceId: product.default_price,
            name: name,
            price: price,
            accountId: accountId
        });

        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

/**
 * 🔱 5. PROCESAR CARGOS (DESTINATION CHARGE)
 * Monetizamos: El cliente paga, el vendedor recibe, y nosotros cobramos comisión.
 */
app.post('/create-checkout-session', async (req, res) => {
    const { priceId, connectedAccountId } = req.body;

    try {
        const session = await stripeClient.checkout.sessions.create({
            line_items: [{ price: priceId, quantity: 1 }],
            payment_intent_data: {
                application_fee_amount: APPLICATION_FEE_AMOUNT,
                transfer_data: {
                    destination: connectedAccountId,
                },
            },
            mode: 'payment',
            success_url: `${BASE_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
            cancel_url: `${BASE_URL}/cancel`,
        });

        res.json({ url: session.url });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

/**
 * 🔱 6. WEBHOOKS (THIN EVENTS V2)
 * Escuchamos cambios en los requisitos del búnker.
 */
app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    const sig = req.headers['stripe-signature'];
    const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

    try {
        const thinEvent = stripeClient.parseThinEvent(req.body, sig, webhookSecret);

        const event = await stripeClient.v2.core.events.retrieve(thinEvent.id);

        if (event.type === 'v2.core.account[requirements].updated') {
            const account = event.data.object;
            console.log(`🔱 Requisitos actualizados para cuenta: ${account.id}`);
        }

        res.json({ received: true });
    } catch (err) {
        console.error('Webhook processing error:', err.message);
        res.status(400).type('text').send('Webhook Error: verification or processing failed');
    }
});

app.listen(3000, () => console.log('🔱 TRYONYOU Búnker API activa en puerto 3000'));
