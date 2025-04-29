# 💳 Stripe Payment Integration (Django + Stripe API)

Ce projet permet l'intégration complète de **Stripe** dans une application Django avec deux méthodes de paiement :

- **Stripe Elements (PaymentIntent)** – intégration front-end personnalisée via Stripe Elements.
- **Stripe Checkout (Checkout Session)** – interface Stripe prête à l'emploi.

---

## ⚙️ Configuration

1. **Cloner le projet**

   ```bash
   git clone https://github.com/AnicetJonhia/payment.git
   cd payment
   ```

2. **Environnement**

   Copie le fichier `.env.example` :

   ```bash
   cp .env.example .env
   ```

   Puis renseigne tes clés dans `.env` :

   ```env
   STRIPE_SECRET_KEY=sk_test_51...        # Clé secrète Stripe
   STRIPE_WEBHOOK_SECRET=whsec_...        # Clé du webhook Stripe
   PUBLIC_API_URL=http://localhost:8000   # URL backend
   PUBLIC_CLIENT_URL=http://localhost:3000 # URL frontend
   ```

3. **Installer les dépendances**

   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Démarrage

### Backend (Django)

```bash
python manage.py migrate
python manage.py runserver 8000
```

### Frontend (Next.js)

```bash
npm install
# ou yarn

# Lancer sur le port 3000
PORT=3000 npm run dev
```

---

## 📦 API Endpoints

### 🔹 Créer une Checkout Session (Stripe Checkout)

```
POST /api/payment/create-checkout-session/
```

**Payload**
```json
{
  "product_name": "Nom produit",
  "amount": 1000,
  "quantity": 2
}
```

**Réponse**
```json
{
  "id": "cs_test_...",
  "url": "https://checkout.stripe.com/..."
}
```

---

### 🔹 Créer un PaymentIntent (Stripe Elements)

```
POST /api/payment/create-payment-intent/
```

**Payload**
```json
{
  "product_name": "Produit test",
  "amount": 500,
  "quantity": 1
}
```

**Réponse**
```json
{
  "clientSecret": "pi_..._secret_...",
  "order_id": 25
}
```

---

### 🔹 Stripe Webhook

```
POST /api/payment/webhook/
```

Stripe enverra les événements ici, notamment `checkout.session.completed` pour marquer une commande comme payée.

Pour tester en local :
```bash
stripe listen --forward-to localhost:8000/api/payment/webhook/
```

Une fois la commande lancée, tu verras dans la console une ligne du type :
```bash
> Ready! Your webhook signing secret is whsec_...
```
Copie la valeur whsec_... et reporte-la dans ton fichier .env sous la clé STRIPE_WEBHOOK_SECRET.

---

### 🔹 Pages de retour

- **Succès :** `GET /api/payment/success/`  
- **Annulation :** `GET /api/payment/cancel/`

---

### 🔹 Rembourser une commande

```
POST /api/payment/refund/<order_id>/
```

**Réponse**
```json
{
  "message": "Commande remboursée.",
  "refund": { ... }
}
```

---

## 🧱 Modèle `Order`

Le modèle `Order` contient :

- `product_name`: nom du produit
- `amount`: montant unitaire en cents
- `quantity`: quantité commandée
- `stripe_checkout_session_id`: ID de session ou PaymentIntent
- `paid` (booléen)
- `refunded` (booléen)

---

## 📌 Notes

- `amount` est exprimé en **cents** (ex. : `500` = 5.00 USD)
- En production, adapte les URLs de `success_url` et `cancel_url` aux domaines réels
- Stripe Webhooks assure la confirmation serveur des paiements

---

## 🔐 Sécurité

- **Ne jamais committer** `.env` contenant vos clés Stripe.
- Ajoutez `.env` dans votre `.gitignore`.

---

## 📄 Licence

Projet sous licence MIT – libre d'utilisation et modification.

