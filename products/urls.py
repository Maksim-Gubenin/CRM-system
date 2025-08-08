from django.urls import path

from products.views import ProductsListView

app_name = "products"

urlpatterns = [
    path("<int:pk>/", ProductsListView.as_view(), name="detail"),
]
