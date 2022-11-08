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
    # Pharmacy Based permissions
    indore_pharmacy_permission = request.user.groups.filter(name="Indore Pharmacy")
    batchwise_stock_report_permission = request.user.groups.filter(
        name="Pharmacy - Batch Wise Stock Report"
    )
    # Finance Base permissions
    indore_finance_permission = request.user.groups.filter(name="Indore Finance")
    collection_report_permission = request.user.groups.filter(
        name="Finance - Collection Report"
    )
    indore_revenue_report_permission = request.user.groups.filter(
        name="Indore Finance - Revenue Report"
    )
    context = {
        # Pharmacy Base permissions
        "indore_pharmacy_permission": indore_pharmacy_permission,
        "batchwise_stock_report_permission": batchwise_stock_report_permission,
        # Finance Permissions
        "indore_finance_permission": indore_finance_permission,
        "collection_report_permission": collection_report_permission,
        "indore_revenue_report_permission": indore_revenue_report_permission,
    }

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
        "user_name": request.user.username,
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
