from django.db import migrations

MORE_PRODUCTS = [
    dict(name="Cloud Walk Sneaker", gender="Men", category="Sneakers", price="5499.00", rating="4.7", badge="COMFORT",
         image="https://images.unsplash.com/photo-1595341888016-a392ef81b7de?auto=format&fit=crop&w=700&q=85"),
    dict(name="Street Runner Pro", gender="Men", category="Running", price="7299.00", rating="4.8", badge="NEW",
         image="https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=700&q=85"),
    dict(name="Executive Oxford", gender="Men", category="Formal", price="8999.00", rating="4.9", badge="PREMIUM",
         image="https://images.unsplash.com/photo-1478186957726-70bcd53e2caf?auto=format&fit=crop&w=700&q=85"),
    dict(name="Pastel Fashion Sneaker", gender="Women", category="Sneakers", price="5999.00", rating="4.7", badge="TRENDING",
         image="https://images.unsplash.com/photo-1465453869711-7e174808ace9?auto=format&fit=crop&w=700&q=85"),
    dict(name="Strappy Block Heels", gender="Women", category="Formal", price="6799.00", rating="4.5", badge="",
         image="https://images.unsplash.com/photo-1543508282-6319a3e2621f?auto=format&fit=crop&w=700&q=85"),
    dict(name="Everyday Flat Sandals", gender="Women", category="Sandals", price="3299.00", rating="4.6", badge="SALE",
         image="https://images.unsplash.com/photo-1519744792095-2f2205e87b6f?auto=format&fit=crop&w=700&q=85"),
    dict(name="Kids Light-Up Sneaker", gender="Kids", category="Sneakers", price="3599.00", rating="4.9", badge="KIDS PICK",
         image="https://images.unsplash.com/photo-1528701800489-20be9c1a4c5f?auto=format&fit=crop&w=700&q=85"),
    dict(name="Kids Rainy Day Boots", gender="Kids", category="Boots", price="2799.00", rating="4.6", badge="NEW",
         image="https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=700&q=85"),
]


def add_more_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    for item in MORE_PRODUCTS:
        Product.objects.get_or_create(name=item['name'], defaults=item)


def remove_more_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Product.objects.filter(name__in=[p['name'] for p in MORE_PRODUCTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_address'),
    ]

    operations = [
        migrations.RunPython(add_more_products, remove_more_products),
    ]
