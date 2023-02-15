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

from .rh_oracle_config import Ora
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
def rh_nav(request):
    all_group_permissions = request.user.groups.values()
    context = {}
    for group_permission in all_group_permissions:
        context.update({group_permission["page_permission"]: group_permission["name"]})

    context.update({"user_name": request.user.get_full_name()})
    return render(request, "reports/rh_nav.html", context)


# RH Pharmacy
@login_required(login_url="login")
@allowed_users("RH Pharmacy - Pharmacy Sales Consumption And Return")
def pharmacy_sales_consumption_and_return(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "Pharmacy Sales Consumption And Return",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            pharmacy_sales_consumption_and_return_data,
            pharmacy_sales_consumption_and_return_column_name,
        ) = db.get_pharmacy_sales_consumption_and_return(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=pharmacy_sales_consumption_and_return_data,
            column=pharmacy_sales_consumption_and_return_column_name,
        )

        if not pharmacy_sales_consumption_and_return_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'pharmacy_sales_consumption_and_return_data':pharmacy_sales_consumption_and_return_data, "pharmacy_sales_consumption_and_return_column_name":pharmacy_sales_consumption_and_return_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


# Finance


@login_required(login_url="login")
@allowed_users("RH Finance - Package With Price")
def package_with_price(request):
    get_fac = request.user.employee.facility
    if get_fac.facility_name == "ALL":
        facility = FacilityDropdown.objects.values().order_by("facility_name")
    else:
        facility = [
            {
                "facility_name": get_fac.facility_name,
                "facility_code": get_fac.facility_code,
            },
        ]
    context = {
        "facility_template": "facility_template",
        "facilities": facility,
        "user_name": request.user.get_full_name(),
        "page_name": "Package With Price",
    }

    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        try:
            facility_code = request.POST["facility_dropdown"]
        except MultiValueDictKeyError:
            context["error"] = "😒 Please Select a facility from the dropdown list"
            return render(request, "reports/one_for_all.html", context)

        db = Ora()
        package_with_price_data, column_name = db.get_package_with_price(facility_code)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=package_with_price_data,
            column=column_name,
        )

        if not package_with_price_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)

        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'package_with_price_data':package_with_price_data, 'user_name':request.user.get_full_name(),'facilities' : facility})


@login_required(login_url="login")
@allowed_users("RH Finance - Card Report")
def card_report(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "Card Report",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        card_report_data, card_report_column_name = db.get_card_report(
            from_date, to_date
        )
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=card_report_data,
            column=card_report_column_name,
        )

        if not card_report_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'card_report_data':card_report_data, "card_report_column_name":card_report_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Doctor Fee Package")
def doctor_fee_package(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "Doctor Fee Package",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            doctor_fee_package_data,
            doctor_fee_package_column_name,
        ) = db.get_doctor_fee_package(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=doctor_fee_package_data,
            column=doctor_fee_package_column_name,
        )

        if not doctor_fee_package_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'doctor_fee_package_data':doctor_fee_package_data, "doctor_fee_package_column_name":doctor_fee_package_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - OP Pharmacy GST")
def op_pharmacy_gst(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "OP Pharmacy GST",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            op_pharmacy_gst_data,
            op_pharmacy_gst_column_name,
        ) = db.get_op_pharmacy_gst(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=op_pharmacy_gst_data,
            column=op_pharmacy_gst_column_name,
        )

        if not op_pharmacy_gst_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'op_pharmacy_gst_data':op_pharmacy_gst_data, "op_pharmacy_gst_column_name":op_pharmacy_gst_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Vaccine Report")
def vaccine_report(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "Vaccine Report",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            vaccine_report_data,
            vaccine_report_column_name,
        ) = db.get_vaccine_report(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=vaccine_report_data,
            column=vaccine_report_column_name,
        )

        if not vaccine_report_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'vaccine_report_data':vaccine_report_data, "vaccine_report_column_name":vaccine_report_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Pharmacy Report")
def pharmacy_report(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "Pharmacy Report",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        pharmacy_report_data, pharmacy_report_column_name = db.get_pharmacy_report(
            from_date, to_date
        )
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=pharmacy_report_data,
            column=pharmacy_report_column_name,
        )

        if not pharmacy_report_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'pharmacy_report_data':pharmacy_report_data, "pharmacy_report_column_name":pharmacy_report_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Health Checkup")
def health_checkup(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "Health Checkup",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            health_checkup_data,
            health_checkup_column_name,
        ) = db.get_health_checkup(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=health_checkup_data,
            column=health_checkup_column_name,
        )

        if not health_checkup_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'health_checkup_data':health_checkup_data, "health_checkup_column_name":health_checkup_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Admissions With Address")
def admissions_with_address(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "Admissions With Address",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            admissions_with_address_data,
            admissions_with_address_column_name,
        ) = db.get_admissions_with_address(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=admissions_with_address_data,
            column=admissions_with_address_column_name,
        )

        if not admissions_with_address_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'admissions_with_address_data':admissions_with_address_data, "admissions_with_address_column_name":admissions_with_address_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Admissions Report")
def admissions_report(request):
    get_fac = request.user.employee.facility
    if get_fac.facility_name == "ALL":
        facility = FacilityDropdown.objects.values()
    else:
        facility = [
            {
                "facility_name": get_fac.facility_name,
                "facility_code": get_fac.facility_code,
            },
        ]
    context = {
        "facilities": facility,
        "facility_template": "facility_template",
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "Admissions Report",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        try:
            facility_code = request.POST["facility_dropdown"]
        except MultiValueDictKeyError:
            context["error"] = "😒 Please Select a facility from the dropdown list"
            return render(request, "reports/one_for_all.html", context)
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            admissions_report_data,
            admissions_report_column_name,
        ) = db.get_admissions_report(from_date, to_date, facility_code)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=admissions_report_data,
            column=admissions_report_column_name,
        )

        if not admissions_report_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'admissions_report_data':admissions_report_data, "admissions_report_column_name":admissions_report_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Admissions Report With Billing Group")
def admissions_report_with_billing_group(request):
    get_fac = request.user.employee.facility
    if get_fac.facility_name == "ALL":
        facility = FacilityDropdown.objects.values()
    else:
        facility = [
            {
                "facility_name": get_fac.facility_name,
                "facility_code": get_fac.facility_code,
            },
        ]
    context = {
        "facilities": facility,
        "facility_template": "facility_template",
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "RH Finance - Admissions Report With Billing Group",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        try:
            facility_code = request.POST["facility_dropdown"]
        except MultiValueDictKeyError:
            context["error"] = "😒 Please Select a facility from the dropdown list"
            return render(request, "reports/one_for_all.html", context)
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            admissions_report_with_billing_group_data,
            admissions_report_with_billing_group_column_name,
        ) = db.get_admissions_report_with_billing_group(
            from_date, to_date, facility_code
        )
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=admissions_report_with_billing_group_data,
            column=admissions_report_with_billing_group_column_name,
        )

        if not admissions_report_with_billing_group_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'admissions_report_with_billing_group_data':admissions_report_with_billing_group_data, "admissions_report_with_billing_group_column_name":admissions_report_with_billing_group_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Admissions Referal")
def admissions_referal(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "Admissions Referal",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            admissions_referal_data,
            admissions_referal_column_name,
        ) = db.get_admissions_referal(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=admissions_referal_data,
            column=admissions_referal_column_name,
        )

        if not admissions_referal_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'admissions_referal_data':admissions_referal_data, "admissions_referal_column_name":admissions_referal_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Daily Revenue Reports")
def daily_revenue_reports(request):
    dropdown_options = [
        {
            "option_value": "revenue_data_rh",
            "option_name": "Revenue Data RH [0]",
        },
        {
            "option_value": "revenue_data_rh1",
            "option_name": "Revenue Data RH 1",
        },
        {
            "option_value": "revenue_data_rh2",
            "option_name": "Revenue Data RH 2",
        },
    ]
    context = {
        "user_name": request.user.get_full_name(),
        "page_name": "Daily Revenue Reports",
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
        daily_revenue_reports_value, column_name = db.get_daily_revenue_reports(
            revenue_data
        )
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=daily_revenue_reports_value,
            column=column_name,
        )

        if not daily_revenue_reports_value:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'daily_revenue_reports_value':daily_revenue_reports_value, 'user_name':request.user.get_full_name(),'date_form' : DateForm(),'facilities' : facility})


@login_required(login_url="login")
@allowed_users("RH Finance - Surgery Report")
def surgery_report(request):
    get_fac = request.user.employee.facility
    if get_fac.facility_name == "ALL":
        facility = FacilityDropdown.objects.values().order_by("facility_name")
    else:
        facility = [
            {
                "facility_name": get_fac.facility_name,
                "facility_code": get_fac.facility_code,
            },
        ]
    context = {
        "date_template": "date_template",
        "facility_template": "facility_template",
        "facilities": facility,
        "user_name": request.user.get_full_name(),
        "page_name": "Surgery Report",
        "date_form": DateForm(),
    }

    if request.method == "GET":

        return render(
            request,
            "reports/one_for_all.html",
            context,
        )

    elif request.method == "POST":
        # Manually format To Date fro Sql Query
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])

        # Select Function from model
        try:
            facility_code = request.POST["facility_dropdown"]
        except MultiValueDictKeyError:
            context["error"] = "😒 Please Select a facility from the dropdown list"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        db = Ora()
        (
            surgery_report_value,
            column_name,
        ) = db.get_surgery_report(facility_code, from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=surgery_report_value,
            column=column_name,
        )

        if not surgery_report_value:
            context["error"] = "Sorry!!! No Data Found"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'surgery_report_value':surgery_report_value, 'user_name':request.user.get_full_name(),'date_form' : DateForm(),'facilities' : facility})


@login_required(login_url="login")
@allowed_users("RH Finance - Billing Service-Wise Transaction")
def billing_servicewise_transaction(request):
    dropdown_options = [
        {
            "option_value": "('O')",
            "option_name": "Outpatient",
        },
        {
            "option_value": "('E')",
            "option_name": "Emergency",
        },
        {
            "option_value": "('R')",
            "option_name": "External",
        },
        {
            "option_value": "('I')",
            "option_name": "Inpatient",
        },
        {
            "option_value": ("O", "E", "R", "I"),
            "option_name": "All",
        },
    ]
    get_fac = request.user.employee.facility
    if get_fac.facility_name == "ALL":
        facility = FacilityDropdown.objects.values().order_by("facility_name")
    else:
        facility = [
            {
                "facility_name": get_fac.facility_name,
                "facility_code": get_fac.facility_code,
            },
        ]
    context = {
        "dropdown_options": dropdown_options,
        "date_template": "date_template",
        "facility_template": "facility_template",
        "facilities": facility,
        "user_name": request.user.get_full_name(),
        "page_name": "Surgery Report",
        "date_form": DateForm(),
    }

    if request.method == "GET":

        return render(
            request,
            "reports/one_for_all.html",
            context,
        )

    elif request.method == "POST":
        # Select Function from model
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        episode_code = request.POST["dropdown_options"]
        try:
            # Manually format To Date fro Sql Query

            facility_code = request.POST["facility_dropdown"]
        except MultiValueDictKeyError:
            context["error"] = "😒 Please Select a facility from the dropdown list"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        db = Ora()
        (
            billing_servicewise_transaction_value,
            column_name,
        ) = db.get_billing_servicewise_transaction(
            facility_code, episode_code, from_date, to_date
        )
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=billing_servicewise_transaction_value,
            column=column_name,
        )

        if not billing_servicewise_transaction_value:
            context["error"] = "Sorry!!! No Data Found"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'billing_servicewise_transaction_value':billing_servicewise_transaction_value, 'user_name':request.user.get_full_name(),'date_form' : DateForm(),'facilities' : facility})


@login_required(login_url="login")
@allowed_users("RH Finance - Patient Notes")
def patient_notes(request):
    context = {
        "user_name": request.user.get_full_name(),
        "page_name": "Patient Notes",
        "date_template": "date_template",
        "date_form": DateForm(),
    }

    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        try:
            from_date = date_formater(request.POST["from_date"])
            to_date = date_formater(request.POST["to_date"])
        except MultiValueDictKeyError:
            context["error"] = "😒 Please Select a facility from the dropdown list"
            return render(request, "reports/one_for_all.html", context)

        db = Ora()
        patient_notes_data, column_name = db.get_patient_notes(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=patient_notes_data,
            column=column_name,
        )

        if not patient_notes_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)

        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'patient_notes_data':patient_notes_data, 'user_name':request.user.get_full_name(),'facilities' : facility})


@login_required(login_url="login")
@allowed_users("RH Finance - Pharmacy Items List")
def pharmacy_items_list(request):
    input_tags = ["UHID", "Episode ID"]
    context = {
        "user_name": request.user.get_full_name(),
        "input_tags": input_tags,
        "page_name": "Pharmacy Items List",
    }

    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        uhid = request.POST["UHID"].upper()
        episode_id = request.POST["Episode"]
        db = Ora()
        (
            pharmacy_items_list_data,
            column_name,
        ) = db.get_pharmacy_items_list(uhid, episode_id)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=pharmacy_items_list_data,
            column=column_name,
        )

        if not pharmacy_items_list_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)

        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {"column_name":column_name,'pharmacy_items_list_data':pharmacy_items_list_data, 'user_name':request.user.get_full_name()})


@login_required(login_url="login")
@allowed_users("RH Finance - RH Revenue Report")
def rh_revenue_report(request):

    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "RH Revenue Report",
        "date_form": DateForm(),
    }

    if request.method == "GET":

        return render(
            request,
            "reports/one_for_all.html",
            context,
        )

    elif request.method == "POST":
        # Manually format To Date fro Sql Query
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])

        db = Ora()
        (
            rh_revenue_report_value,
            column_name,
        ) = db.get_rh_revenue_report(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=rh_revenue_report_value,
            column=column_name,
        )

        if not rh_revenue_report_value:
            context["error"] = "Sorry!!! No Data Found"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'rh_revenue_report_value':rh_revenue_report_value, 'user_name':request.user.get_full_name(),'date_form' : DateForm(),'facilities' : facility})


# RH Clinical Admin


@login_required(login_url="login")
@allowed_users("RH Clinical Administration - RH OPD Consultation")
def rh_opd_consultation(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "RH OPD Consultation",
        "date_form": DateForm(),
    }

    if request.method == "GET":

        return render(
            request,
            "reports/one_for_all.html",
            context,
        )

    elif request.method == "POST":
        # Manually format To Date fro Sql Query
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])

        db = Ora()
        (
            rh_opd_consultation_value,
            column_name,
        ) = db.get_rh_opd_consultation(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=rh_opd_consultation_value,
            column=column_name,
        )

        if not rh_opd_consultation_value:
            context["error"] = "Sorry!!! No Data Found"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'rh_opd_consultation_value':rh_opd_consultation_value, 'user_name':request.user.get_full_name(),'date_form' : DateForm(),'facilities' : facility})


@login_required(login_url="login")
@allowed_users("RH Clinical Administration - IP Referrals")
def ip_referrals(request):
    get_fac = request.user.employee.facility
    if get_fac.facility_name == "ALL":
        facility = FacilityDropdown.objects.values().order_by("facility_name")
    else:
        facility = [
            {
                "facility_name": get_fac.facility_name,
                "facility_code": get_fac.facility_code,
            },
        ]
    context = {
        "date_template": "date_template",
        "facility_template": "facility_template",
        "facilities": facility,
        "user_name": request.user.get_full_name(),
        "page_name": "IP Referrals",
        "date_form": DateForm(),
    }

    if request.method == "GET":

        return render(
            request,
            "reports/one_for_all.html",
            context,
        )

    elif request.method == "POST":
        # Manually format To Date fro Sql Query
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])

        # Select Function from model
        try:
            facility_code = request.POST["facility_dropdown"]
        except MultiValueDictKeyError:
            context["error"] = "😒 Please Select a facility from the dropdown list"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        db = Ora()
        (
            ip_referrals_value,
            column_name,
        ) = db.get_ip_referrals(facility_code, from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=ip_referrals_value,
            column=column_name,
        )

        if not ip_referrals_value:
            context["error"] = "Sorry!!! No Data Found"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'ip_referrals_value':ip_referrals_value, 'user_name':request.user.get_full_name(),'date_form' : DateForm(),'facilities' : facility})


# RH Marketing
@login_required(login_url="login")
@allowed_users("RH Marketing - Admission Report 2")
def rh_admission_report_2(request):
    get_fac = request.user.employee.facility
    if get_fac.facility_name == "ALL":
        facility = FacilityDropdown.objects.values().order_by("facility_name")
    else:
        facility = [
            {
                "facility_name": get_fac.facility_name,
                "facility_code": get_fac.facility_code,
            },
        ]
    context = {
        "date_template": "date_template",
        "facility_template": "facility_template",
        "facilities": facility,
        "user_name": request.user.get_full_name(),
        "page_name": "Admission Report 2",
        "date_form": DateForm(),
    }

    if request.method == "GET":

        return render(
            request,
            "reports/one_for_all.html",
            context,
        )

    elif request.method == "POST":
        # Manually format To Date fro Sql Query
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])

        # Select Function from model
        try:
            facility_code = request.POST["facility_dropdown"]
        except MultiValueDictKeyError:
            context["error"] = "😒 Please Select a facility from the dropdown list"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        db = Ora()
        (
            rh_admission_report_2_value,
            column_name,
        ) = db.get_rh_admission_report_2(facility_code, from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=rh_admission_report_2_value,
            column=column_name,
        )

        if not rh_admission_report_2_value:
            context["error"] = "Sorry!!! No Data Found"
            return render(
                request,
                "reports/one_for_all.html",
                context,
            )

        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'rh_admission_report_2_value':rh_admission_report_2_value, 'user_name':request.user.get_full_name(),'date_form' : DateForm(),'facilities' : facility})


# Miscellaneous Reports

# RH Labs
@login_required(login_url="login")
@allowed_users("RH Miscellaneous Reports - RH Lab - Phlebotomy Collection Report")
def phlebotomy_collection_report(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "Phlebotomy Collection Report",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            phlebotomy_collection_report_data,
            phlebotomy_collection_report_column_name,
        ) = db.get_phlebotomy_collection_report(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=phlebotomy_collection_report_data,
            column=phlebotomy_collection_report_column_name,
        )

        if not phlebotomy_collection_report_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'phlebotomy_collection_report_data':phlebotomy_collection_report_data, "phlebotomy_collection_report_column_name":phlebotomy_collection_report_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})


# RH Food and Beverage
@login_required(login_url="login")
@allowed_users(
    "RH Miscellaneous Reports - RH Food and Beverage  - F and B Order Report"
)
def f_and_b_order_report(request):
    context = {
        "date_template": "date_template",
        "user_name": request.user.get_full_name(),
        "page_name": "F and B Order Report",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            f_and_b_order_report_data,
            f_and_b_order_report_column_name,
        ) = db.get_f_and_b_order_report(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=f_and_b_order_report_data,
            column=f_and_b_order_report_column_name,
        )

        if not f_and_b_order_report_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'f_and_b_order_report_data':f_and_b_order_report_data, "f_and_b_order_report_column_name":f_and_b_order_report_column_name,'user_name':request.user.get_full_name(),'date_form' : DateForm(), "page_name" : "Angiography Kit"})
