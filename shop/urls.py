from django.urls import path
from . import views

urlpatterns = [
    path("",views.index ,name="ShopHome"),
    path("about/",views.about ,name="About Us"),
    path("contact/",views.contact ,name="Contact Us"),
    path("tracker/",views.tracker ,name="Tracking status"),
    path("search/",views.search ,name="Search"),
    path("products/<int:myid>", views.productview, name="View Product"),
    path("checkout/",views.checkout ,name="Check Out"),
    path("handlerequest/",views.handlerequest ,name="HandleRequest"),
]   

