from django.shortcuts import redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from reports.models import QueryReports


def unauthenticated_user(login_page):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("landing_page")
        else:
            return login_page(request, *args, **kwargs)

    return wrapper_func


def check_if_user_is_auth(view_func):
    def wrapper_func(request, pk, *args, **kwargs):
        try:
            report = QueryReports.objects.get(pk=pk)
            groups = request.user.groups.filter(name=report.report_name)

        except QueryReports.DoesNotExist:
            return render(
                request,
                "reports/index.html",
                {
                    "error": "The requested report does not exist.",
                    "user_name": request.user.username,
                },
            )

        if not groups.exists():
            return render(
                request,
                "reports/index.html",
                {
                    "error": "You are not authorized to access this report. Please contact your administrator.",
                    "user_name": request.user.username,
                },
            )

        return view_func(request, pk, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            try:
                groups = request.user.groups.get(name=allowed_roles)

            except Group.DoesNotExist:
                return render(
                    request,
                    "reports/index.html",
                    {
                        "error": "You Are Not Authorized To Access This Page. Please Contact Your Administrator.",
                        "user_name": request.user.username,
                    },
                )

            if groups:
                return view_func(request, *args, **kwargs)

        return wrapper_func

    return decorator


# def user_specific_webpage(view_func):
#     def wrapper_func(request, *args,**kwargs):

#         groups = request.user.groups.all()
#         for group in groups:
#             print(group)

#     return wrapper_func
