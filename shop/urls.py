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
    path("login/", views.handle_login, name="Login"),
    path("signup/", views.handle_signup, name="Signup"),
    path("logout/", views.handle_logout, name="Logout"),
    path("admin/analytics/", views.admin_analytics_dashboard, name="adminAnalytics"),
]

