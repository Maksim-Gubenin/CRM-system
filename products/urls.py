from django.urls import path

from products.views import (
    ProductsCreateView,
    ProductsDeleteView,
    ProductsDetailView,
    ProductsListView,
    ProductsUpdateView,
)

app_name = "products"

urlpatterns = [
    path("", ProductsListView.as_view(), name="list"),
    path("<int:pk>/", ProductsDetailView.as_view(), name="detail"),
    path("create/", ProductsCreateView.as_view(), name="create"),
    path("<int:pk>/update/", ProductsUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ProductsDeleteView.as_view(), name="delete"),
]
