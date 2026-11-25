import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Sum

MEMORY_POINTS = 10  # couples.models at the time of this migration


def backfill(apps, schema_editor):
    """Points that used to be computed on each request: memories x 10 + quiz points (pet_points), and the
    sum of shop purchases."""
    Couple = apps.get_model('couples', 'Couple')
    Memory = apps.get_model('memories', 'Memory')
    Purchase = apps.get_model('shop', 'Purchase')
    for couple in Couple.objects.all():
        memories = Memory.objects.filter(jar__cabinet__couple_id=couple.pk).count()
        couple.points_earned = memories * MEMORY_POINTS + couple.pet_points
        couple.points_spent = Purchase.objects.filter(couple_id=couple.pk).aggregate(total=Sum('price'))['total'] or 0
        couple.save(update_fields=['points_earned', 'points_spent'])


def restore(apps, schema_editor):
    """Back to quiz-only pet_points (the rest was computed from memories)."""
    Couple = apps.get_model('couples', 'Couple')
    Memory = apps.get_model('memories', 'Memory')
    for couple in Couple.objects.all():
        couple.pet_points = max(0, couple.points_earned - Memory.objects.filter(jar__cabinet__couple_id=couple.pk).count() * MEMORY_POINTS)
        couple.save(update_fields=['pet_points'])


class Migration(migrations.Migration):

    dependencies = [
        ('couples', '0007_pet_mood_and_ragdog'),
        ('memories', '0003_memory_location'),
        ('shop', '0002_shop_items_table'),
    ]

    operations = [
        migrations.AddField(model_name='couple', name='points_earned', field=models.IntegerField(default=0)),
        migrations.AddField(model_name='couple', name='points_spent', field=models.PositiveIntegerField(default=0)),
        # Points earned per day against the daily limit (starts with this release: no rows yet).
        migrations.CreateModel(
            name='DailyPoints',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('limit', models.PositiveIntegerField(default=100)),
                ('earned', models.PositiveIntegerField(default=0)),
                ('couple', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_points', to='couples.couple')),
            ],
            options={
                'ordering': ['-day'],
                'constraints': [models.UniqueConstraint(fields=('couple', 'day'), name='one_points_row_per_couple_day')],
            },
        ),
        migrations.RunPython(backfill, restore),
        migrations.RemoveField(model_name='couple', name='pet_points'),
    ]
