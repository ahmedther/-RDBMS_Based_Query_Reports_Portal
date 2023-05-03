import pandas as pd
import os

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import FileResponse, HttpResponse

from .oracle_config import Ora
from .decorators import *
from .forms import DateForm, DateTimeForm
from .models import *
from .supports import *


# Create your views here.


@unauthenticated_user
def signupuser(request):
    facility = FacilityDropdown.objects.all().order_by("facility_name")
    context = {
        "form": UserCreationForm(),
        "facilities": facility,
    }
    if request.method == "GET":
        return render(request, "reports/signupuser.html", context)
    else:
        facility_code = input_validator(
            request=request,
            context=context,
            error_name="Facility",
            value_in_post="facility_dropdown",
        )
        first_name = input_validator(
            request=request,
            context=context,
            error_name="First Name",
            value_in_post="first_name",
        )
        last_name = input_validator(
            request=request,
            context=context,
            error_name="Last Name",
            value_in_post="last_name",
        )
        pr_number = input_validator(
            request=request,
            context=context,
            error_name="Payroll Number",
            value_in_post="pr_number",
        )
        department = input_validator(
            request=request,
            context=context,
            error_name="Department",
            value_in_post="department",
        )
        username = input_validator(
            request=request,
            context=context,
            error_name="Username",
            value_in_post="username",
        )

        if " " in username:
            context[
                "error"
            ] = "Invalid Username. Spaces are not allowed in Username field"
            return render(request, "reports/signupuser.html", context)

        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"],
                    password=request.POST["password1"],
                    first_name=first_name,
                    last_name=last_name,
                )
                user.save()
                employe_data = Employee(
                    user=User.objects.get(pk=user.id),
                    department=department,
                    pr_number=pr_number,
                    facility=FacilityDropdown.objects.get(pk=facility_code),
                )
                employe_data.save()

                context["success"] = "You Have Successfuly Signed Up"
                context[
                    "success1"
                ] = "Please enter your User ID and Password to Sign In"

                return redirect("login")

            except IntegrityError:
                context[
                    "error"
                ] = "That username has already been taken. Please choose a new username"
                return render(request, "reports/signupuser.html", context)

            # except ValueError:
            #     context["error"] = "Please Enter a Valid Username and Password"
            #     return render(request, "reports/signupuser.html", context)
        else:
            context["error"] = "Passwords did not match"
            return render(request, "reports/signupuser.html", context)


@unauthenticated_user
def login_page(request):
    if request.method == "GET":
        return render(request, "reports/login_page.html")

    else:
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )

        if user is None:
            return render(
                request,
                "reports/login_page.html",
                {
                    "form": AuthenticationForm(),
                    "error": "Username and password did not match",
                },
            )
        else:
            login(request, user)
            user_full_name = request.user.get_full_name()
            context = {"user_name": user_full_name}
            return render(request, "reports/index.html", context)


@login_required(login_url="login")
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")


@login_required(login_url="login")
def landing_page(request):
    if request.method == "GET":
        return render(
            request, "reports/index.html", {"user_name": request.user.get_full_name()}
        )


@login_required(login_url="login")
def nav(request):
    all_group_permissions = request.user.groups.all()

    report_headings = {}
    for group_permission in all_group_permissions:
        reports = QueryReports.objects.filter(report_name=group_permission)
        for report in reports:
            report_heading = report.report_heading.headings
            if report_heading not in report_headings:
                report_headings[report_heading] = []
            report_headings[report_heading].append(report)
    context = {
        "all_group_permissions": all_group_permissions,
        "user_name": request.user.get_full_name(),
        "report_headings": report_headings,
    }
    return render(request, "reports/nav.html", context)


@login_required(login_url="login")
@check_if_user_is_auth
def one_for_all(request, pk):
    try:
        report = QueryReports.objects.get(pk=pk)
        context = {
            "user_name": request.user.get_full_name(),
            "page_name": report.report_name.name.split("-")[-1],
        }
        if report.sub_sql_query:
            dropdown_options = get_dropdown_options(
                report.sub_sql_query,
                report.dropdown_option_value,
                report.dropdown_option_name1,
                report.dropdown_option_name2,
            )
            context["dropdown_options"] = dropdown_options

        if report.facility_template:
            facility = get_facility_dropdown(request)
            context["facilities"] = facility
            context["facility_template"] = "facility_template"

        if report.date_template:
            context["date_template"] = "date_template"
            context["date_form"] = DateForm()

        if report.pharmacy_iaarc:
            dropdown_options1 = get_pharmacy_IAARC()
            context["dropdown_options1"] = dropdown_options1

        if report.dropdown_options_value:
            dropdown_options2 = get_custom_dropdowns(
                report.dropdown_options_value, report.dropdown_options_name
            )
            context["dropdown_options2"] = dropdown_options2

        if report.time_template:
            context["time_template"] = "time_template"

        if report.input_tags:
            input_tags = get_input_tags(report.input_tags)
            context["input_tags"] = input_tags

        if report.textbox:
            textbox = get_input_tags(report.textbox)
            context["textbox"] = textbox

        if report.http_response:
            context["http_response"] = True

        if request.method == "GET":
            return render(request, "reports/one_for_all.html", context)
    except Exception as error:
        context["error"] = f"❌ {error} ❌"
        return render(request, "reports/one_for_all.html", context)

    try:
        if request.method == "POST":
            variables = {}
            sql_query = report.report_sql_query
            if "special_case" in sql_query:
                excel_file_path = special_case_handler(request, sql_query, context)
                if not excel_file_path:
                    context["error"] = "Sorry!!! No Data Found"
                if isinstance(excel_file_path, dict):
                    return render(request, "reports/one_for_all.html", excel_file_path)
                else:
                    return FileResponse(
                        open(excel_file_path, "rb"),
                        content_type="application/vnd.ms-excel",
                    )

            if "dropdown_options" in context:
                sql_query, variables = sql_query_formater(sql_query, request)

            if "dropdown_options1" in context:
                sql_query, variables = sql_query_formater(sql_query, request)

            if "dropdown_options2" in context:
                sql_query, variables = sql_query_formater(sql_query, request)

            if "facility_template" in context:
                try:
                    sql_query, variables = sql_query_formater(sql_query, request)

                except MultiValueDictKeyError:
                    context[
                        "error"
                    ] = "😒 Please Select a facility from the dropdown list"
                    return render(request, "reports/one_for_all.html", context)

            if "date_template" in context:
                if "time_template" in context:
                    sql_query, variables = sql_query_formater(
                        sql_query, request, type="date_time"
                    )
                else:
                    sql_query, variables = sql_query_formater(sql_query, request)

            if "input_tags" in context:
                sql_query, variables = sql_query_formater(
                    sql_query,
                    request,
                    type="input_tags",
                    other_values=report.input_tags,
                )

            if "textbox" in context:
                sql_query, variables = sql_query_formater(
                    sql_query, request, type="input_tags", other_values=report.textbox
                )

            db = Ora()
            sql_query = sql_query.format(**variables)
            data, column = db.one_for_all(sql_query)

            if not data:
                context["error"] = "Sorry!!! No Data Found"
                return render(request, "reports/one_for_all.html", context)

            if "http_response" in context:
                pd_dataframe = pd.DataFrame(data=data, columns=list(column))
                return HttpResponse(pd_dataframe.to_html())

            else:
                excel_file_path = excel_generator(
                    page_name=context["page_name"], column=column, data=data
                )
                db.close_connection()
                return FileResponse(
                    open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
                )
                # return render(request,'reports/one_for_all.html', {'stock_data':stock_data, 'user_name':request.user.get_full_name()})

    except Exception as error:
        context["error"] = f"❌ {error} ❌"
        return render(request, "reports/one_for_all.html", context)
