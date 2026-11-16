from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('couples', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='couple',
            name='pet_type',
            field=models.CharField(choices=[('dog', 'Cún'), ('cat', 'Mèo'), ('capybara', 'Capybara')], default='dog', max_length=20),
        ),
    ]
