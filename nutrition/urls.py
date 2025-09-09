from django.urls import path

from .views import calculator_view, search_products


urlpatterns = [
    path("", calculator_view, name="nutrition_calculator"),
    path("api/search-products/", search_products, name="search_products"),
]

