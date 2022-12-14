from django.contrib import admin

from main.models import CheckfrontStatus, Product, Venue

# Register your models here.
admin.site.register(Product)
admin.site.register(Venue)
admin.site.register(CheckfrontStatus)
