from django.urls import path

from advertisements.views import (
    ADSCreateView,
    ADSDeleteView,
    ADSDetailView,
    ADSListView,
    ADSStatisticsView,
    ADSUpdateView,
)

app_name = "advertisements"

urlpatterns: list[path] = [
    path("", ADSListView.as_view(), name="list"),
    path("<int:pk>/", ADSDetailView.as_view(), name="detail"),
    path("create/", ADSCreateView.as_view(), name="create"),
    path("<int:pk>/update/", ADSUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ADSDeleteView.as_view(), name="delete"),
    path("statistic/", ADSStatisticsView.as_view(), name="statistic"),
]
