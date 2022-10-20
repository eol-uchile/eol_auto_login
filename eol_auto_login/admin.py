from django.contrib import admin
from .models import EolAutoLogin

# Register your models here.


class EolAutoLoginAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('uuid', 'user')
    search_fields = ['uuid', 'user__username']
    ordering = ['user']


admin.site.register(EolAutoLogin, EolAutoLoginAdmin)
