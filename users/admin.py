from django.contrib import admin
from django.contrib.auth import get_user_model
from events.models import Event,Category
User = get_user_model()
# Register your models here.
admin.site.register(Event)
admin.site.register(Category)
admin.site.register(User)

