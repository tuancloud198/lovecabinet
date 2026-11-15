from common.services import save_scoped

def save(serializer, user, scope):
    return save_scoped(serializer, user, scope)
