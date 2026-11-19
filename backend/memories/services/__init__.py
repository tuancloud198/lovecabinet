from django.db import transaction
from common.services import save_scoped
from memories.models import Reaction

def save_memory(serializer, user):
    old_jar = serializer.instance.jar_id if serializer.instance else None
    staged = serializer.validated_data.pop('staged_photos', [])
    with transaction.atomic():  # the memory only exists if all its staged photos attach
        memory = save_scoped(serializer, user, 'jar__cabinet__couple')
        if staged:
            from photos.services import attach_staged
            attach_staged(memory, staged)
    if old_jar and memory.jar_id != old_jar:
        from photos.services import relocate_photos
        relocate_photos(memory)
    return memory
def add_comment(serializer, memory, user):
    return serializer.save(memory=memory, author=user)
def toggle_reaction(memory, user):
    reaction, created = Reaction.objects.get_or_create(memory=memory, author=user)
    if not created:
        reaction.delete()
    return created
