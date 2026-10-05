import json
from decimal import Decimal, InvalidOperation

import razorpay
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST

from .models import Address, CartItem, Order, OrderItem, Product

# The category "chips" shown on every product listing page. Each one
# matches either the gender or the category field on Product.
CATEGORY_CHIPS = ['Men', 'Women', 'Kids', 'Sneakers', 'Running', 'Formal', 'Sandals', 'Boots']


def _parse_price(value):
    """Turns a query-string price into a Decimal, or None if it's blank/invalid."""
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def product_list(request, category_value=None):
    """Renders the storefront. With no category_value, shows everything.
    With one (e.g. 'Men' or 'Sneakers'), shows only matching products —
    this is what gives each category its own real, shareable URL.

    On top of that, ?q=, ?min_price= and ?max_price= in the query
    string narrow the results further (works on both the all-products
    page and any category page).
    """
    products = Product.objects.all()

    if category_value:
        products = products.filter(
            Q(gender__iexact=category_value) | Q(category__iexact=category_value)
        )

    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(name__icontains=search_query)

    min_price_raw = request.GET.get('min_price', '').strip()
    max_price_raw = request.GET.get('max_price', '').strip()
    min_price = _parse_price(min_price_raw)
    max_price = _parse_price(max_price_raw)

    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)

    products = products.order_by('id')

    context = {
        'products': products,
        'category_chips': CATEGORY_CHIPS,
        'current_category': category_value,
        'search_query': search_query,
        'min_price': min_price_raw,
        'max_price': max_price_raw,
        'has_active_filters': bool(category_value or search_query or min_price_raw or max_price_raw),
    }
    return render(request, 'store/home.html', context)


def product_detail(request, product_id):
    """A single product's own page — full details, price, and both
    'Add to Cart' and 'Buy Now' options."""
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})


class SoleMateLoginView(LoginView):
    """Custom login view so we can use our own themed template instead
    of Django's default bare-bones one."""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class SignUpView(View):
    """Simple signup page using Django's built-in UserCreationForm,
    styled to match the rest of the site."""
    template_name = 'registration/signup.html'

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}. You can log in now.')
            return redirect('login')
        return render(request, self.template_name, {'form': form})


# ---------------------------------------------------------------------
# CART
# ---------------------------------------------------------------------

@login_required
def cart_view(request):
    items = (
        CartItem.objects
        .filter(user=request.user)
        .select_related('product')
        .order_by('added_at')
    )
    total = sum((item.subtotal for item in items), Decimal('0.00'))
    return render(request, 'store/cart.html', {'items': items, 'total': total})


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f'Added "{product.name}" to your cart.')
    return redirect(request.META.get('HTTP_REFERER') or 'home')


@login_required
@require_POST
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    action = request.POST.get('action')

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
            messages.success(request, f'Removed "{item.product.name}" from your cart.')
            return redirect('cart')
        item.save()
    else:
        # Manual quantity entry from a number input.
        try:
            quantity = int(request.POST.get('quantity', item.quantity))
        except ValueError:
            quantity = item.quantity
        if quantity <= 0:
            item.delete()
            messages.success(request, f'Removed "{item.product.name}" from your cart.')
            return redirect('cart')
        item.quantity = quantity
        item.save()

    return redirect('cart')


@login_required
@require_POST
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    name = item.product.name
    item.delete()
    messages.success(request, f'Removed "{name}" from your cart.')
    return redirect('cart')


# ---------------------------------------------------------------------
# CHECKOUT & PAYMENT (Razorpay, test mode)
# ---------------------------------------------------------------------

def _get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def _resolve_checkout_lines(request):
    """Figures out what's being paid for: either a single product from
    a 'Buy Now' click (passed as buy_now_product_id/buy_now_qty in the
    request), or everything currently in the user's cart. Returns
    (lines, total, is_buy_now) where each line is
    {'product', 'quantity', 'subtotal'} — a shape both the cart and a
    single Buy Now purchase can share."""
    buy_now_product_id = request.POST.get('buy_now_product_id') or request.GET.get('buy_now_product_id')

    if buy_now_product_id:
        product = get_object_or_404(Product, id=buy_now_product_id)
        raw_qty = request.POST.get('buy_now_qty') or request.GET.get('buy_now_qty') or 1
        try:
            quantity = max(1, int(raw_qty))
        except (TypeError, ValueError):
            quantity = 1
        subtotal = product.price * quantity
        return [{'product': product, 'quantity': quantity, 'subtotal': subtotal}], subtotal, True

    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    lines = [{'product': item.product, 'quantity': item.quantity, 'subtotal': item.subtotal} for item in cart_items]
    total = sum((line['subtotal'] for line in lines), Decimal('0.00'))
    return lines, total, False


@login_required
def checkout_view(request):
    """The checkout summary page — shows either the cart or a single
    'Buy Now' product, with a 'Pay with Razorpay' button."""
    lines, total, is_buy_now = _resolve_checkout_lines(request)

    if not lines:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    return render(request, 'store/checkout.html', {
        'lines': lines,
        'total': total,
        'is_buy_now': is_buy_now,
        'buy_now_product_id': request.GET.get('buy_now_product_id', ''),
        'buy_now_qty': request.GET.get('buy_now_qty', '1'),
    })


@login_required
@require_POST
def create_razorpay_order(request):
    """AJAX endpoint: creates a Razorpay order for the checkout total
    (cart or Buy Now) and hands back what the frontend needs to open
    the Razorpay Checkout popup. No local Order row is created yet —
    that only happens once the payment is verified below."""
    lines, total, is_buy_now = _resolve_checkout_lines(request)

    if not lines:
        return JsonResponse({'error': 'Nothing to pay for.'}, status=400)

    amount_paise = int(total * 100)  # Razorpay wants the amount in paise

    client = _get_razorpay_client()
    try:
        razorpay_order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': 1,
        })
    except Exception as exc:
        return JsonResponse({'error': f'Could not start payment: {exc}'}, status=502)

    return JsonResponse({
        'razorpay_order_id': razorpay_order['id'],
        'amount': amount_paise,
        'currency': 'INR',
        'key_id': settings.RAZORPAY_KEY_ID,
        'name': 'SoleMate',
        'description': f'{len(lines)} item(s)',
        'prefill_email': request.user.email or '',
        'prefill_name': request.user.username,
    })


@login_required
@require_POST
def verify_razorpay_payment(request):
    """AJAX endpoint the frontend calls after Razorpay's popup reports
    success. Verifies the payment signature server-side (so a forged
    'success' from the browser alone can't create a fake paid order),
    then creates the real Order + OrderItem rows. A cart checkout also
    clears the cart; a Buy Now purchase leaves the cart untouched."""
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')

    if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
        return JsonResponse({'error': 'Missing payment details.'}, status=400)

    client = _get_razorpay_client()
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'error': 'Payment verification failed.'}, status=400)

    lines, total, is_buy_now = _resolve_checkout_lines(request)
    if not lines:
        # Extremely unlikely (cart emptied in another tab mid-payment),
        # but handle it rather than create an order with no items.
        return JsonResponse({'error': 'Nothing to pay for.'}, status=400)

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            total=total,
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            payment_status='paid',
        )

        for line in lines:
            OrderItem.objects.create(
                order=order,
                product=line['product'],
                product_name=line['product'].name,
                price=line['product'].price,
                quantity=line['quantity'],
            )

        if not is_buy_now:
            CartItem.objects.filter(user=request.user).delete()

    return JsonResponse({'redirect_url': reverse('order_success', args=[order.id])})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
def address_view(request):
    """A small 'manage your address' page — one shipping address per
    user, linked from the navbar next to the login/logout area."""
    address, _created = Address.objects.get_or_create(
        user=request.user,
        defaults={'full_name': request.user.username, 'phone': '', 'address_line1': '', 'city': '', 'state': '', 'pincode': ''},
    )

    if request.method == 'POST':
        address.full_name = request.POST.get('full_name', '').strip()
        address.phone = request.POST.get('phone', '').strip()
        address.address_line1 = request.POST.get('address_line1', '').strip()
        address.address_line2 = request.POST.get('address_line2', '').strip()
        address.city = request.POST.get('city', '').strip()
        address.state = request.POST.get('state', '').strip()
        address.pincode = request.POST.get('pincode', '').strip()
        address.save()
        messages.success(request, 'Address saved.')
        return redirect('address')

    return render(request, 'store/address.html', {'address': address})


# ---------------------------------------------------------------------
# AI CHAT BOX (Gemini)
# ---------------------------------------------------------------------

GEMINI_SYSTEM_PROMPT = (
    "You are the friendly customer support assistant for SoleMate, an online "
    "shoe store. Help visitors with questions about products, sizing, shipping "
    "(free delivery on orders over ₹4,000), returns (30-day return policy), "
    "their cart, and orders. Keep replies short (2-4 sentences) and friendly. "
    "Prices on the site are in Indian Rupees (₹). If you don't know something "
    "specific to this store (like exact stock or a specific order's status), "
    "say so honestly instead of making it up, and suggest contacting support."
)


@require_POST
def chat_api(request):
    """AJAX endpoint for the site-wide AI chat widget. Not login-gated —
    anonymous visitors can use it too, like a normal support chat."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    user_message = (data.get('message') or '').strip()
    history = data.get('history') or []

    if not user_message:
        return JsonResponse({'error': 'Message is empty.'}, status=400)
    if not settings.GEMINI_API_KEY:
        return JsonResponse({'error': 'Chat is not configured yet.'}, status=503)

    contents = []
    for turn in history[-10:]:
        role = 'user' if turn.get('role') == 'user' else 'model'
        text = (turn.get('text') or '')[:2000]
        if text:
            contents.append({'role': role, 'parts': [{'text': text}]})
    contents.append({'role': 'user', 'parts': [{'text': user_message[:2000]}]})

    url = f'https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent'
    payload = {
        'contents': contents,
        'system_instruction': {'parts': [{'text': GEMINI_SYSTEM_PROMPT}]},
                'generationConfig': {'maxOutputTokens': 1000},
    }

    try:
        response = requests.post(
            url,
            headers={'x-goog-api-key': settings.GEMINI_API_KEY, 'Content-Type': 'application/json'},
            json=payload,
            timeout=20,
        )
        if not response.ok:
            print("GEMINI ERROR:", response.status_code, response.text)
            return JsonResponse({'error': "Sorry, I couldn't reach the assistant right now. Please try again in a moment."}, status=502)
        result = response.json()
        reply = result['candidates'][0]['content']['parts'][0]['text']
    except requests.exceptions.RequestException as exc:
        print("GEMINI NETWORK ERROR:", repr(exc))
        return JsonResponse({'error': "Sorry, I couldn't reach the assistant right now. Please try again in a moment."}, status=502)
    except (KeyError, IndexError):
        print("GEMINI BAD RESPONSE:", response.text)
        return JsonResponse({'error': "Sorry, I couldn't understand that. Could you rephrase?"}, status=502)

    return JsonResponse({'reply': reply})