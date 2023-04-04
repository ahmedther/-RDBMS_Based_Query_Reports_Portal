from django.urls import path
import reports.views as views

urlpatterns = [
    path("", views.login_page, name="login"),  # login Page
    path("landing_page/", views.landing_page, name="landing_page"),
    path("logout/", views.logoutuser, name="logoutuser"),
    # path("base/", views.base, name="base"),  # base HTml pAge
    # KH NAV
    path("signupuser/", views.signupuser, name="signupuser"),
    path("nav/", views.nav, name="nav"),
    path("one_for_all/<str:pk>/", views.one_for_all, name="one_for_all"),
]
