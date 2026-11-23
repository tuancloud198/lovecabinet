from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('couples', '0004_more_pet_types')]
    operations = [
        migrations.RenameField('couple', 'anniversary', 'dating_since'),
        migrations.AddField('couple', 'met_on', models.DateField(blank=True, null=True)),
    ]
