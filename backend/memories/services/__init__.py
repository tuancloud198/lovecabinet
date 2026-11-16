from common.services import save_scoped
from memories.models import Reaction

def save_memory(serializer, user):
    return save_scoped(serializer, user, 'jar__cabinet__couple')
def add_comment(serializer, memory, user):
    return serializer.save(memory=memory, author=user)
def toggle_reaction(memory, user):
    reaction, created = Reaction.objects.get_or_create(memory=memory, author=user)
    if not created:
        reaction.delete()
    return created
