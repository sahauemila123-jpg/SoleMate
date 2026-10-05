def cart_count(request):
    """Adds `cart_item_count` to every template's context, so the navbar
    cart badge can show it without every view having to pass it in."""
    if request.user.is_authenticated:
        count = sum(
            item.quantity
            for item in request.user.cart_items.all()
        )
    else:
        count = 0
    return {'cart_item_count': count}
