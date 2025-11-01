def user_roles(request):
    """Template context'e kullanıcı rollerini ekle"""
    def is_assistant(user):
        return hasattr(user, 'assistant')
    
    def is_psychologist(user):
        return hasattr(user, 'psychologist')
    
    def is_admin(user):
        return user.is_superuser
    
    return {
        'is_assistant': is_assistant,
        'is_psychologist': is_psychologist,
        'is_admin': is_admin,
    } 