from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('couple_invitations', '0003_invite_by_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='declined_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
