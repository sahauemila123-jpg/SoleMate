from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_seed_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.URLField(blank=True, help_text='A link to an image already online (optional if you upload a photo below).'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_file',
            field=models.ImageField(blank=True, help_text='Upload a photo from your computer.', null=True, upload_to='products/'),
        ),
    ]
