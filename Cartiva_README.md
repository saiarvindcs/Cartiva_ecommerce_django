# Cartiva— CommerceLab V2 visual redesign

This is a visual redesign of the supplied CommerceLab V2 source, retaining the original Django apps, DRF APIs, migrations, Celery tasks, PostgreSQL and Redis configuration. It is **not** a newly verified end-to-end production app.

## Windows PowerShell quick start

1. Extract this ZIP into a **new** folder.
2. Open PowerShell in `advanced_ecommerce`.
3. Run `Copy-Item .env.example .env` and edit the new `.env` secrets.
4. Run `docker compose up -d --build`.
5. Open `http://localhost:8000/` and API docs at `http://localhost:8000/api/docs/`.
6. Run `docker compose ps` and `docker compose logs web --tail 100` if needed.

The Compose project name is `velora_store`, so its PostgreSQL named volume is separate from your existing CommerceLab V2 volume. Existing users/products/orders will **not** automatically appear in Cartiva. If the old project's Docker volume remains, do not delete it until deciding how to migrate data.

## Scope

Included: brand rename in storefront templates, redesigned responsive header with account dropdown and sign out, editorial home hero, ivory/champagne/gold/espresso/charcoal CSS theme, styled catalog/product/cart/checkout/auth/seller pages, footer. Existing routes and backend behavior retained.

Not included or claimed: real payment gateway, shipping integrations, complete feature verification, new profile/wishlist pages, new database content, or deployment hardening.
