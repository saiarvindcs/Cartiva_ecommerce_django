# CommerceLab — Django advanced e-commerce starter

This is an expanded **source-code project** based on the original Advanced_Django_Ecommerce_System archive. It is a **production-style learning/reference project**, NOT a certified production-ready deployment.

## Run on Windows (PowerShell)

```powershell
cd advanced_ecommerce
docker compose up -d --build
docker compose exec web python manage.py check
docker compose exec web python manage.py createsuperuser
```

Then visit `http://localhost:8000/`, Swagger at `/api/docs/`, and admin at `/admin/`.

Copy `.env.example` to `.env` before starting. The development `.env` is **LOCAL DEVELOPMENT ONLY**. Change all credentials before any deployment; do not expose port 8000 to the public internet.

## Features

- Django REST Framework and JWT; registration, addresses, roles and admin
- Seller-scoped product, variant and image APIs; Django admin catalog upload
- Product browsing, search, categories, product details, cart quantity changes
- Checkout with address selection, coupons, idempotency key and stock reservation
- PostgreSQL transaction/row locking, inventory commitment on payment, expiry via Celery/Redis
- Staff-only development mock payments (success/failure) and order state transitions
- Order history, reviews, analytics endpoints, Swagger, Docker, CI/test skeleton

## Mock payments

Mock endpoints work **only** when all three conditions hold: `DJANGO_DEBUG=1`, `MOCK_PAYMENTS_ENABLED=1`, and the caller is authenticated. No real funds are transferred. The simulator checks ownership of each pending order and its payment; it is strictly a local-development tool and must be disabled in production.

- `POST /api/payments/intent/` with `{"order_id": 1}`
- `POST /api/payments/mock/simulate/` with `{"payment_id": "mock_...", "outcome": "success"}`

Checkout reserves stock for 15 minutes. Create and simulate a fresh payment before expiry. If the order expires, create a new checkout order.

## Deployment / known limitations

- This repository does **not** integrate a real payment processor. The mock gateway is intentionally unsuitable for real commerce.
- Add migrations and review them before production rollout; this source archive originated without committed initial app migrations and uses `migrate --run-syncdb` for the demo.
- Run the test suite against PostgreSQL, inspect race conditions and security controls, and configure HTTPS, secrets, CSRF origins, static/media object storage, backups, email delivery, monitoring and a real gateway before production.
- Demo JWT is stored in browser `sessionStorage`; use an HttpOnly-cookie/BFF architecture for a hardened production browser application.
- No deployed environment or actual Docker end-to-end run was verified in this artifact-generation environment.

## Cartiva improvements in this edition

- Shop sorting (newest, price ascending/descending, name) with category and search filters.
- Verified-purchase reviews publish immediately, with admin ability to hide reviews. Existing unapproved reviews are not changed automatically.
- Seller product editing, variant price/stock editing, image removal, and seller-scoped sales overview.
- Richer customer order history, details, pending-order cancellation, and payment-success confirmation page.
- Mock payment intent and simulation request bodies are documented in OpenAPI.
- Checkout already clears the cart when the pending order is created, rather than after payment. A failed mock payment remains pending until cancellation/expiry; retry and refund flows are not implemented.
- Existing Django admin controls delivery; seller shipping permissions are preserved.

### Important upgrade note

Docker Compose project name is `Cartiva_store`. If your existing environment uses a different Compose project name, **do not delete volumes** or run `docker compose down -v`: that would remove the local PostgreSQL data. Preserve your existing `.env` and Docker volumes. Run `docker compose config` to validate the Compose file before starting.

### Verification limitations

The project was statically checked for Python and embedded JavaScript syntax. A live Docker/PostgreSQL end-to-end test was not possible in the artifact build environment. Run `docker compose exec web python manage.py check`, then verify the updated storefront and payment Swagger schema locally.
