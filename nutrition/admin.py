from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "calories", "protein", "fat", "carbs")
    search_fields = ("name",)

