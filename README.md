# SoleMate — Django Integration

Your shoe store template as a full Django project: login system,
database-backed cart (add/update/delete), order placement, category
pages, price filtering, and search — all priced in ₹ (INR).

## What's new in this version

- **AI chat box** — a 💬 button in the bottom-left corner on every page opens
  a chat assistant (powered by Google's Gemini API) that can answer
  questions about sizing, shipping, returns, and the store in general.
  The API key is already configured in `settings.py` — swap it for your
  own if you want to use a different Gemini account, and move it into
  an environment variable before deploying anywhere public.
- **20 products** in the starter catalog now (was 12).
- **Product detail pages** — clicking a product's photo or name opens
  its own page (`/product/<id>/`) with the full price, rating,
  category, and delivery/return info, plus Add to Cart and Buy Now.
- **Buy Now** — a direct checkout path that skips the cart entirely.
  Available on both the product cards and the product detail page.
  It doesn't touch anything already in your cart.
- **Address manager** — a 📍 icon next to your name in the navbar
  (when logged in) opens a small page to save your name, phone, and
  delivery address. One address per account, editable anytime.
- **Checkout with Razorpay (test mode)** — the cart's "Proceed to
  Checkout" button now leads to a real checkout page with a
  **"Pay with Razorpay"** button. It uses Razorpay's official test
  environment (test keys are already configured in
  `solemate/settings.py`), so you can run a full payment flow —
  including Razorpay's own popup — with **zero real money involved**.
  Use test card `4111 1111 1111 1111`, any future expiry date, any
  CVV, to simulate a successful payment (shown right on the checkout
  page too). The payment signature is verified server-side before an
  order is ever created, so it isn't just a fake front-end animation —
  it's a real (sandboxed) payment flow.
  - ⚠️ The test keys in `settings.py` are fine for development, but
    move them into environment variables before deploying anywhere
    public, and never commit real (`rzp_live_...`) keys to a repo.
- **Upload product photos in the admin** — Products now have an actual
  file-upload field (`image_file`), not just a pasted URL. In
  `/admin/` → Products → open or add a product, and you'll see an
  "Image file" upload button plus a live preview. Uploaded photos are
  saved to a `media/` folder and served automatically in development.
  (The original `image` URL field still works too, e.g. for the seeded
  starter catalog — uploaded files just take priority when both are set.)
- **Dedicated category pages** — every gender (`/category/Men/`,
  `/category/Women/`, `/category/Kids/`) and every product category
  (`/category/Sneakers/`, `/category/Running/`, `/category/Formal/`,
  `/category/Sandals/`, `/category/Boots/`) now has its own real,
  shareable URL, server-rendered from the database — not just a
  JS toggle on one page.
- **Price filtering** — a Min Price / Max Price field on the shop
  section filters products server-side, and works together with a
  category page (e.g. `/category/Men/?min_price=3000&max_price=8000`).
- **Search** — the search box now queries the database directly
  (`?q=...`), and combines with category + price filters at the same
  time.
- **Products now live in the database** (`store/models.py` → `Product`),
  seeded automatically by a migration (12 starter shoes, prices in ₹).
  Manage them anytime at `/admin/`.
- **Cart is server-side and per-user** (`CartItem` model) — persists
  across reloads/logins. From `/cart/` you can increase/decrease
  quantity, remove an item, and see a live total.
- **Orders**: "Place Order" on the cart page creates an `Order` +
  `OrderItem` records (a permanent snapshot, so it stays accurate even
  if a product's price changes later), clears the cart, and shows a
  confirmation page. Past orders are listed at `/orders/` ("My Orders"
  in the navbar once logged in).
- **Currency is ₹** throughout.

Adding to cart, viewing the cart, and placing orders all require being
logged in (you'll be redirected to `/login/` if not).

## Run it

```bash
cd solemate_project
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

**If you're upgrading an existing copy of this project**: replace your
`store/` folder and `solemate/settings.py` with the new ones here, keep
your existing `db.sqlite3` if you want to keep your users, then run
`python manage.py migrate` again — it only adds new tables/data, it
won't touch your existing users or superuser account.

Visit:
- `http://127.0.0.1:8000/` — storefront, all products
- `http://127.0.0.1:8000/category/Men/` — example category page
- `http://127.0.0.1:8000/cart/` — cart (requires login)
- `http://127.0.0.1:8000/orders/` — order history (requires login)
- `http://127.0.0.1:8000/admin/` — manage products, users, and orders

## Notes / next steps

- **SECRET_KEY** in `settings.py` is a placeholder — replace it before
  deploying.
- **Prices**: seeded catalog uses INR values converted from the
  original USD demo prices (~×83, rounded). Edit anytime in
  `/admin/` → Products.
- **Payment gateway**: "Place Order" currently just records the order
  in your database — it doesn't charge anyone. Wire up Razorpay,
  Stripe, or another gateway before accepting real payments.
- **Wishlist heart button** is still just a visual toggle (not saved).

"# solemate" 
