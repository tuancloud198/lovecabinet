import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def drop_unaddressed(apps, schema_editor):
    # Pending code-based invitations have no recipient and cannot be carried over.
    apps.get_model('couple_invitations', 'Invitation').objects.filter(recipient__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('couple_invitations', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitation',
            name='code',
        ),
        migrations.RenameField(
            model_name='invitation',
            old_name='accepted_by',
            new_name='recipient',
        ),
        migrations.RunPython(drop_unaddressed, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='invitation',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_invitations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='invitation',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_invitations', to=settings.AUTH_USER_MODEL),
        ),
    ]
