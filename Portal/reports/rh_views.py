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

    context.update({"user_name": request.user})
    return render(request, "reports/rh_nav.html", context)


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
        "reliance_hospital": "reliance_hospital",
        "facility_template": "facility_template",
        "facilities": facility,
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'package_with_price_data':package_with_price_data, 'user_name':request.user.username,'facilities' : facility})


@login_required(login_url="login")
@allowed_users("RH Finance - Card Report")
def card_report(request):
    context = {
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'card_report_data':card_report_data, "card_report_column_name":card_report_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Doctor Fee Package")
def doctor_fee_package(request):
    context = {
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'doctor_fee_package_data':doctor_fee_package_data, "doctor_fee_package_column_name":doctor_fee_package_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - OP Pharmacy GST")
def op_pharmacy_gst(request):
    context = {
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'op_pharmacy_gst_data':op_pharmacy_gst_data, "op_pharmacy_gst_column_name":op_pharmacy_gst_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Vaccine Report")
def vaccine_report(request):
    context = {
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'vaccine_report_data':vaccine_report_data, "vaccine_report_column_name":vaccine_report_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Pharmacy Report")
def pharmacy_report(request):
    context = {
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'pharmacy_report_data':pharmacy_report_data, "pharmacy_report_column_name":pharmacy_report_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Discharge Census Revised")
def discharge_census_revised(request):
    context = {
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
        "page_name": "Discharge Census Revised",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            discharge_census_revised_data,
            discharge_census_revised_column_name,
        ) = db.get_discharge_census_revised(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=discharge_census_revised_data,
            column=discharge_census_revised_column_name,
        )

        if not discharge_census_revised_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'discharge_census_revised_data':discharge_census_revised_data, "discharge_census_revised_column_name":discharge_census_revised_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Health Checkup")
def health_checkup(request):
    context = {
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'health_checkup_data':health_checkup_data, "health_checkup_column_name":health_checkup_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Admissions With Address")
def admissions_with_address(request):
    context = {
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'admissions_with_address_data':admissions_with_address_data, "admissions_with_address_column_name":admissions_with_address_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


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
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'admissions_report_data':admissions_report_data, "admissions_report_column_name":admissions_report_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Admissions Referal")
def admissions_referal(request):
    context = {
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'admissions_referal_data':admissions_referal_data, "admissions_referal_column_name":admissions_referal_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


@login_required(login_url="login")
@allowed_users("RH Finance - Cathlab Report")
def cathlab_report(request):
    context = {
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "user_name": request.user.username,
        "page_name": "Cathlab Report",
        "date_form": DateForm(),
    }
    if request.method == "GET":
        return render(request, "reports/one_for_all.html", context)

    elif request.method == "POST":
        from_date = date_formater(request.POST["from_date"])
        to_date = date_formater(request.POST["to_date"])
        db = Ora()
        (
            cathlab_report_data,
            cathlab_report_column_name,
        ) = db.get_cathlab_report(from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=cathlab_report_data,
            column=cathlab_report_column_name,
        )

        if not cathlab_report_data:
            context["error"] = "Sorry!!! No Data Found"
            return render(request, "reports/one_for_all.html", context)
        else:
            return FileResponse(
                open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
            )
            # return render(request,'reports/one_for_all.html', {'cathlab_report_data':cathlab_report_data, "cathlab_report_column_name":cathlab_report_column_name,'user_name':request.user.username,'date_form' : DateForm(), "page_name" : "Angiography Kit"})


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
        "reliance_hospital": "reliance_hospital",
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'daily_revenue_reports_value':daily_revenue_reports_value, 'user_name':request.user.username,'date_form' : DateForm(),'facilities' : facility})


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
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "facility_template": "facility_template",
        "facilities": facility,
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'surgery_report_value':surgery_report_value, 'user_name':request.user.username,'date_form' : DateForm(),'facilities' : facility})


# RH Clinical Admin


@login_required(login_url="login")
@allowed_users("RH Clinical Administration - Admission Report for Nursing")
def admission_report_for_nursing(request):
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
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "facility_template": "facility_template",
        "facilities": facility,
        "user_name": request.user.username,
        "page_name": "Admission Report for Nursing",
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
            admission_report_for_nursing_value,
            column_name,
        ) = db.get_admission_report_for_nursing(facility_code, from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=admission_report_for_nursing_value,
            column=column_name,
        )

        if not admission_report_for_nursing_value:
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
            # return render(request,'reports/one_for_all.html', {'admission_report_for_nursing_value':admission_report_for_nursing_value, 'user_name':request.user.username,'date_form' : DateForm(),'facilities' : facility})


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
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "facility_template": "facility_template",
        "facilities": facility,
        "user_name": request.user.username,
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
            # return render(request,'reports/one_for_all.html', {'rh_admission_report_2_value':rh_admission_report_2_value, 'user_name':request.user.username,'date_form' : DateForm(),'facilities' : facility})


@login_required(login_url="login")
@allowed_users("RH Marketing - Discharge Report 2")
def rh_discharge_report_2(request):
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
        "reliance_hospital": "reliance_hospital",
        "date_template": "date_template",
        "facility_template": "facility_template",
        "facilities": facility,
        "user_name": request.user.username,
        "page_name": "Discharge Report 2",
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
            rh_discharge_report_2_value,
            column_name,
        ) = db.get_rh_discharge_report_2(facility_code, from_date, to_date)
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=rh_discharge_report_2_value,
            column=column_name,
        )

        if not rh_discharge_report_2_value:
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
            # return render(request,'reports/one_for_all.html', {'rh_discharge_report_2_value':rh_discharge_report_2_value, 'user_name':request.user.username,'date_form' : DateForm(),'facilities' : facility})
