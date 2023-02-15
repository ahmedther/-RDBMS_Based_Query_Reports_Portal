import platform
import pandas as pd

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import FileResponse, HttpResponse
from reports.indore_oracle_config import Ora
from .decorators import unauthenticated_user, allowed_users
from .forms import DateForm, DateTimeForm
from .models import IAACR, FacilityDropdown, Employee
from .supports import (
    date_formater,
    excel_generator,
    excel_generator_tpa,
    input_validator,
)


@login_required(login_url="login")
def indore_nav(request):
    all_group_permissions = request.user.groups.values()
    context = {}
    for group_permission in all_group_permissions:
        context.update({group_permission["page_permission"]: group_permission["name"]})
    context.update({"user_name": request.user.get_full_name()})
    return render(request, "reports/indore_nav.html", context)


@login_required(login_url="login")
@allowed_users("Indore Finance - Revenue Report")
def indore_revenue_report(request):
    dropdown_options = [
        {
            "option_value": "REVENUE_DATA_IN",
            "option_name": "Revenue Data [0]",
        },
        {
            "option_value": "REVENUE_DATA_IN1",
            "option_name": "Revenue Data 1",
        },
        {
            "option_value": "REVENUE_DATA_IN2",
            "option_name": "Revenue Data 2",
        },
    ]
    context = {
        "user_name": request.user.get_full_name(),
        "page_name": "Indore Revenue Report",
        "dropdown_options": dropdown_options,
    }

    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        try:
            revenue_data = request.POST["dropdown_options"]
        except:
            context["error"] = "Please Select The Dropdown Field"
            return render(request, "reports/one_for_all.html", context)
        db = Ora()
        indore_revenue_report, column_name = db.get_indore_revenue_report(revenue_data)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=indore_revenue_report,
            column=column_name,
        )

        if not indore_revenue_report:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'indore_revenue_report':indore_revenue_report, 'user_name':request.user.username,'date_form' : DateForm(),'facilities' : facility})


# Indore Miscellaneous
# Indore Billing


@login_required(login_url="login")
@allowed_users(
    "Indore Miscellaneous Reports - Indore Billing - Discharge Billing Report Without Date Range Indore"
)
def discharge_billing_report_without_date_range_indore(request):
    context = {
        "user_name": request.user.get_full_name(),
        "page_name": "Discharge Billing Report Without Date Range Indore",
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        db = Ora()
        (
            discharge_billing_report_without_date_range_indore_value,
            column_name,
        ) = db.get_discharge_billing_report_without_date_range_indore()
        # excel_file_path = excel_generator(page_name="Discharge Billing Report Without Date Range", data=discharge_billing_report_without_date_range_indore_value, column=column_name,      )

        if not discharge_billing_report_without_date_range_indore_value:
            context["error"] = "Sorry!!! No Data Found"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        else:
            pd_dataframe = pd.DataFrame(
                data=discharge_billing_report_without_date_range_indore_value,
                columns=list(column_name),
            )
            pd_dataframe["DIS_ADV_DATE_TIME"] = pd.to_datetime(
                pd_dataframe["DIS_ADV_DATE_TIME"], format="%d-%b-%Y %H:%M:%S"
            ).dt.strftime("%d-%b-%Y %H:%M:%S")

            return HttpResponse(pd_dataframe.to_html())
            # return FileResponse(
            #     open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            # )
            # return render(request,'reports/one_for_all.html', {'discharge_billing_report_without_date_range_indore_value':discharge_billing_report_without_date_range_indore_value, 'user_name':request.user.get_full_name()})
