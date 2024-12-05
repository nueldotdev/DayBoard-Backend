from django.contrib import admin
from . import models

# Register your models here.
# admin.site.register('Admins', admin.ModelAdmin)
admin.site.register(models.User)
admin.site.register(models.Board)
admin.site.register(models.List)
admin.site.register(models.Card)