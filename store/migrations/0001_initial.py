from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('gender', models.CharField(choices=[('Men', 'Men'), ('Women', 'Women'), ('Kids', 'Kids')], max_length=10)),
                ('category', models.CharField(max_length=60)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('rating', models.DecimalField(decimal_places=1, default=5.0, max_digits=2)),
                ('badge', models.CharField(blank=True, max_length=40)),
                ('image', models.URLField(blank=True)),
            ],
        ),
    ]
