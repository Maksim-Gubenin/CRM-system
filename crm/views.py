from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from advertisements.models import Advertisement
from customers.models import Customer
from leads.models import Lead
from products.models import Product


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    Render the main dashboard page with statistical overview.

    This view displays key metrics including counts of products, advertisements,
    leads, and customers. The view requires user authentication.

    Args:
        request: HttpRequest object containing metadata about the request

    Returns:
        HttpResponse: Rendered dashboard template with statistics context
    """

    context: dict[str, int] = {
        "products_count": Product.objects.count(),
        "advertisements_count": Advertisement.objects.count(),
        "leads_count": Lead.objects.count(),
        "customers_count": Customer.objects.count(),
    }

    return render(request, "index.html", context)
