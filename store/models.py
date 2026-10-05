from django.conf import settings
from django.db import models


class Product(models.Model):
    """The shoe catalog. Used to live as a JS array in home.html —
    now server-rendered from here so the cart/orders can reference
    real product rows."""

    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Kids', 'Kids'),
    ]

    name = models.CharField(max_length=120)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    category = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    badge = models.CharField(max_length=40, blank=True)

    # Original field — a pasted link to an image already hosted online.
    # Kept so the seeded starter catalog (which uses Unsplash links)
    # keeps working.
    image = models.URLField(blank=True, help_text="A link to an image already online (optional if you upload a photo below).")

    # New field — an actual photo file uploaded from your computer via
    # the admin. Takes priority over `image` when both are set.
    image_file = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Upload a photo from your computer.")

    def __str__(self):
        return self.name

    @property
    def display_image(self):
        """The image to actually show: an uploaded file if there is
        one, otherwise the pasted URL."""
        if self.image_file:
            return self.image_file.url
        return self.image


class CartItem(models.Model):
    """One row per (user, product) in a user's active cart."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.user.username})"

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """A placed order. Items are copied into OrderItem at checkout time
    so the order stays accurate even if a Product's price changes later."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Razorpay payment tracking. An Order row is only created once a
    # payment has actually been verified as successful (see
    # views.verify_razorpay_payment), so payment_status is always
    # 'paid' in practice — the field exists for admin visibility and
    # in case a "pay later" option gets added down the line.
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=20, default='paid')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} — {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=120)  # snapshot, survives product deletion
    price = models.DecimalField(max_digits=8, decimal_places=2)  # price at time of purchase
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class Address(models.Model):
    """One shipping address per user, managed from a small "My Address"
    page linked near the login/logout area in the navbar."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='address',
    )
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.full_name}'s address ({self.user.username})"
