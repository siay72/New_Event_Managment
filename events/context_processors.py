# events/context_processors.py
def user_roles(request):
    user = request.user
    return {
        'is_organizer': user.groups.filter(name='Organizer').exists(),
        'is_admin': user.is_superuser,
    }