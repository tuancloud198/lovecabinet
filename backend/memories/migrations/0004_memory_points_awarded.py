from django.db import migrations, models


class Migration(migrations.Migration):
    """Points each memory earned. Memories from before the daily limit all earned the full 10, so they get 10
    (deleting one takes back what it gave); new memories record what the limit allowed."""

    dependencies = [('memories', '0003_memory_location')]

    operations = [
        migrations.AddField(model_name='memory', name='points_awarded', field=models.PositiveSmallIntegerField(default=10), preserve_default=False),
        migrations.AlterField(model_name='memory', name='points_awarded', field=models.PositiveSmallIntegerField(default=0)),
    ]
