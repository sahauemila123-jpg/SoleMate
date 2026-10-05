from django.db import migrations

# Prices converted from the original USD demo values to INR
# (roughly USD * 83, then rounded to a clean number). Edit freely
# in /admin/ afterwards — this just seeds a starting catalog.
PRODUCTS = [
    dict(name="AirFlex Runner", gender="Men", category="Running", price="6499.00", rating="4.8", badge="BEST SELLER",
         image="https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=700&q=85"),
    dict(name="Urban Street Sneaker", gender="Men", category="Sneakers", price="5799.00", rating="4.7", badge="NEW",
         image="https://images.unsplash.com/photo-1495555961986-6d4c1ecb7be3?auto=format&fit=crop&w=700&q=85"),
    dict(name="Classic Leather Formal", gender="Men", category="Formal", price="8299.00", rating="4.9", badge="PREMIUM",
         image="https://images.unsplash.com/photo-1614252369475-531eba835eb1?auto=format&fit=crop&w=700&q=85"),
    dict(name="Rose Fashion Sneaker", gender="Women", category="Sneakers", price="6199.00", rating="4.8", badge="TRENDING",
         image="https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=700&q=85"),
    dict(name="Elegant Women's Heels", gender="Women", category="Formal", price="7499.00", rating="4.6", badge="NEW",
         image="https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=700&q=85"),
    dict(name="Summer Comfort Sandals", gender="Women", category="Sandals", price="3699.00", rating="4.7", badge="SALE",
         image="https://images.unsplash.com/photo-1603487742131-4160ec999306?auto=format&fit=crop&w=700&q=85"),
    dict(name="Kids Color Pop Sneaker", gender="Kids", category="Sneakers", price="3299.00", rating="4.9", badge="KIDS PICK",
         image="https://images.unsplash.com/photo-1514989940723-e8e51635b782?auto=format&fit=crop&w=700&q=85"),
    dict(name="Kids Sport Runner", gender="Kids", category="Running", price="2899.00", rating="4.8", badge="NEW",
         image="https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?auto=format&fit=crop&w=700&q=85"),
    dict(name="Kids Summer Sandals", gender="Kids", category="Sandals", price="2099.00", rating="4.6", badge="SALE",
         image="https://images.unsplash.com/photo-1560089000-7433a4ebbd64?auto=format&fit=crop&w=700&q=85"),
    dict(name="Mountain Trek Boots", gender="Men", category="Boots", price="9899.00", rating="4.9", badge="PREMIUM",
         image="https://images.unsplash.com/photo-1520639888713-7851133b1ed0?auto=format&fit=crop&w=700&q=85"),
    dict(name="Women's Winter Boots", gender="Women", category="Boots", price="9099.00", rating="4.8", badge="WINTER",
         image="https://images.unsplash.com/photo-1542840410-3092f99611a3?auto=format&fit=crop&w=700&q=85"),
    dict(name="Kids School Shoes", gender="Kids", category="Formal", price="2499.00", rating="4.7", badge="SCHOOL",
         image="https://images.unsplash.com/photo-1560769629-975ec94e6a86?auto=format&fit=crop&w=700&q=85"),
]


def seed_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    if Product.objects.exists():
        # Already has data (e.g. re-run or manually added) — don't duplicate.
        return
    for item in PRODUCTS:
        Product.objects.create(**item)


def remove_seeded_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Product.objects.filter(name__in=[p['name'] for p in PRODUCTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_cartitem_order_orderitem'),
    ]

    operations = [
        migrations.RunPython(seed_products, remove_seeded_products),
    ]
