from django.db import migrations, models
import users.models


def backfill_tags(apps, schema_editor):
    User = apps.get_model('users', 'User')
    used = set()
    for user in User.objects.filter(tag__isnull=True).only('pk'):
        tag = users.models.generate_tag()
        while tag in used or User.objects.filter(tag=tag).exists():
            tag = users.models.generate_tag()
        used.add(tag)
        User.objects.filter(pk=user.pk).update(tag=tag)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tag',
            field=models.CharField(editable=False, max_length=9, null=True),
        ),
        migrations.RunPython(backfill_tags, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='user',
            name='tag',
            field=models.CharField(default=users.models.generate_tag, editable=False, max_length=9, unique=True),
        ),
    ]
