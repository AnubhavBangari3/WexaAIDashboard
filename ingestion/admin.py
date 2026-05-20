from django.contrib import admin
from . models import APIKey,Event,CSVUpload

# Register your models here.
admin.site.register(APIKey)
admin.site.register(Event)
admin.site.register(CSVUpload)