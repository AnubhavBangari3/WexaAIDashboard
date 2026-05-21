from django.contrib import admin
from . models import Dashboard,SavedQuery,Widget
# Register your models here.

admin.site.register(Dashboard)
admin.site.register(SavedQuery)
admin.site.register(Widget)
