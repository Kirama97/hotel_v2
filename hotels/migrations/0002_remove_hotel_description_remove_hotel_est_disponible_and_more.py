import cloudinary.models
import django.core.validators
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotel',
            name='description',
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='est_disponible',
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='etoiles',
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='nombre_chambres',
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='pays',
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='ville',
        ),
        migrations.AddField(
            model_name='hotel',
            name='devise',
            field=models.CharField(choices=[('F XOF', 'F XOF — Franc CFA'), ('EUR', 'EUR — Euro'), ('USD', 'USD — Dollar américain'), ('GBP', 'GBP — Livre sterling')], default='F XOF', max_length=10, verbose_name='Devise'),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='email_contact',
            field=models.EmailField(max_length=254, verbose_name='E-mail'),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='Photo'),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='prix_par_nuit',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Prix par nuit'),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='telephone',
            field=models.CharField(max_length=20, verbose_name='Numéro de téléphone'),
        ),
        migrations.AlterField(
            model_name='hotel',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
