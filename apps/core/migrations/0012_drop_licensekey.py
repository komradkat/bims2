from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_barangayinfo_logo_base64_barangayinfo_logo_mimetype'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LicenseKey',
        ),
    ]
