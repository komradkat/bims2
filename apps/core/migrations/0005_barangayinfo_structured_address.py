from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_barangayinfo_captain_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='barangayinfo',
            name='address',
        ),
        migrations.AddField(
            model_name='barangayinfo',
            name='street',
            field=models.CharField(blank=True, help_text='Street / Purok / Sitio', max_length=200),
        ),
        migrations.AddField(
            model_name='barangayinfo',
            name='city_municipality',
            field=models.CharField(default='', help_text='City or Municipality', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='barangayinfo',
            name='province',
            field=models.CharField(default='', help_text='Province', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='barangayinfo',
            name='region',
            field=models.CharField(blank=True, help_text='Region', max_length=100),
        ),
        migrations.AddField(
            model_name='barangayinfo',
            name='zip_code',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
