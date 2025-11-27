from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "calories", "protein", "fat", "carbs", "fiber")
    search_fields = ("name",)
    list_filter = ("category",)
    ordering = ("category", "name")

