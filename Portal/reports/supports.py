import pandas as pd
import os
import logging
import xlwings as xw
import platform
from pathlib import Path
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.http import FileResponse
from datetime import datetime, timedelta
from multiprocessing.dummy import Pool

from .oracle_config import Ora
from reports.models import FacilityDropdown, IAACR


def check_user_pass(userid, userpass):
    user = Ora()
    user_d = user.check_user(userid, userpass)

    if user_d != None:
        for data in user_d:
            user_id = data[0]
            user_name = data[1]
            user_pass = data[2]

            return user_id, user_name, user_pass


def date_formater(date):
    if not date:
        return None
    date = date.split("-")
    date_year = int(date[0])
    date_month = int(date[1])
    date_day = int(date[2])
    date_format = datetime(date_year, date_month, date_day)
    date = date_format.strftime("%d-%b-%Y")
    return f"'{date}'"


def excel_generator(data, column, page_name):
    # add special characters here to avoid errors and breaks
    # Filter Special Characters
    if "/" in page_name:
        page_name = page_name.replace("/", "")

    # datetime object containing current date and time
    add_time_to_page = datetime.now()

    # dd/mm/YY H:M:S
    # Add time with miliseconds to avoid conflict with apache and nginx
    add_time_to_page_string = add_time_to_page.strftime("%d-%b-%Y-%H-%M-%S-%f")
    add_time_to_page_string = str(add_time_to_page_string)

    # gives you location of manage.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    curret_path = Path(current_dir)
    parent_path = curret_path.parent
    # write the print fuction in error log. Test on Apache reverse proxy but not on nginx
    # sys.stderr.write(excel_file_path)

    excel_file_path = (
        f"{parent_path}/web_excel_files/{page_name}-{add_time_to_page_string}.xlsx"
    )

    # creates a log file and report errors
    # logging.basicConfig(filename="report_error.log", level=logging.DEBUG)
    # logging.error(f"Error on {add_time_to_page_string} :")
    # sys.stderr.write(excel_file_path)

    # excel_file_path = page_name + ".xlsx"
    excel_data = pd.DataFrame(data=data, columns=list(column))

    # Set destination directory to save excel.
    generate_excel = pd.ExcelWriter(
        excel_file_path,
        engine="xlsxwriter",
        datetime_format="dd-mm-yyyy hh:mm:ss",
        date_format="dd-mm-yyyy",
    )

    # Write excel to file using pandas to_excel
    if len(page_name) > 31:
        page_name = page_name[0:31]
    excel_data.to_excel(generate_excel, startrow=0, sheet_name=page_name, index=False)

    # Indicate workbook and worksheet for formatting
    workbook = generate_excel.book
    worksheet = generate_excel.sheets[page_name]

    # Iterate through each column and set the width == the max length in that column. A padding length of 2 is also added.
    for i, col in enumerate(excel_data.columns):
        # find length of column i
        try:
            column_len = excel_data[col].astype(str).str.len().max()

        except:
            column_len = 12

        # Setting the length if the column header is larger
        # than the max column value length
        try:
            column_len = max(column_len, len(col)) + 4

        except:
            column_len = 12

        # set the column length
        worksheet.set_column(i, i, column_len)

    generate_excel.close()
    return excel_file_path


def input_validator(request, context, value_in_post, error_name):
    try:
        user_input = request.POST[value_in_post]
    except:
        context[
            "error"
        ] = f"{error_name} left empty 😒. This is a mandatory field. Please fill up all the fields, all are required fields"
        return render(request, "reports/signupuser.html", context)
    if user_input:
        return user_input


def excel_generator_tpa(data, column, page_name):
    add_time_to_page = datetime.now()

    # dd/mm/YY H:M:S
    # Add time with miliseconds to avoid conflict with apache and nginx
    add_time_to_page_string = add_time_to_page.strftime("%d-%b-%Y-%H-%M-%S-%f")
    add_time_to_page_string = str(add_time_to_page_string)

    # gives you location of manage.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    curret_path = Path(current_dir)
    parent_path = curret_path.parent
    # write the print fuction in error log. Test on Apache reverse proxy but not on nginx
    # sys.stderr.write(excel_file_path)

    excel_file_path = (
        f"{parent_path}/web_excel_files/{page_name}-{add_time_to_page_string}.xlsb"
    )
    # gives you location of manage.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    curret_path = Path(current_dir)
    parent_path = curret_path.parent
    # TPA File Location
    # Was forced to keep this location, as ref https://stackoverflow.com/questions/14037412/cannot-access-excel-file
    tpa_excel_path = (
        r"C:\Windows\System32\config\systemprofile\desktop\tpa_cover_format.xlsb"
    )
    # tpa_excel_path = f"{parent_path}/web_excel_files/tpa_cover_letter/tpa_cover_format.xlsb"

    # Have to use unconventional import here to avoid errors deployment in Linux

    import pythoncom

    # Initialize to avoid error Using XLWings with parallel processing
    pythoncom.CoInitialize()

    # load workbook
    xlwing_app = xw.App(visible=False)
    tpa_workbook = xw.Book(tpa_excel_path)
    tpa_worksheet_query = tpa_workbook.sheets["Query"]
    tpa_worksheet_uhid = tpa_workbook.sheets["UHID"]

    tpa_worksheet_query.range("A2:J500").clear_contents()
    tpa_worksheet_uhid.range("A1:A500").clear_contents()
    excel_data = pd.DataFrame(data=data, columns=list(column))

    # Update workbook at specified range for Query Sheet
    tpa_worksheet_query.range("A2").options(
        index=False, header=False
    ).value = excel_data
    tpa_worksheet_uhid.range("A1").options(
        index=False, header=False
    ).value = excel_data["PATIENT_ID"]

    # Close workbook
    tpa_workbook.close(excel_file_path)
    # tpa_workbook.close()
    xlwing_app.quit()

    return excel_file_path


def get_last_three_dates():
    dates = []
    for i in range(1, 4):
        print(i)
        date_now = datetime.now() - timedelta(days=i)
        dates.append(date_now.strftime(f"%d-%b-%Y"))
    return dates


def get_dropdown_options(
    sql_query, dropdown_option_value, dropdown_option_name1, dropdown_option_name2
):
    dropdown_options = []
    all_dropdown_options = {"ALL": " "}
    db = Ora()
    dropdown_data, _ = db.one_for_all(sql_query)

    for data in dropdown_data:
        dropdown_options.append(
            {
                "option_value": f"'{data[dropdown_option_value]}'",
                "option_name": f"{data[dropdown_option_name1]} - {data[dropdown_option_name2]}",
            }
        )
        all_dropdown_options["ALL"] = (
            all_dropdown_options["ALL"] + f"'{data[dropdown_option_value]}',"
        )

    all_dropdown_options["ALL"] = all_dropdown_options["ALL"][:-1]

    dropdown_options.append(
        {
            "option_value": all_dropdown_options["ALL"],
            "option_name": "ALL",
        }
    )

    return dropdown_options


def get_pharmacy_IAARC():
    dropdown_options1 = []

    drugs = IAACR.objects.all()
    for drug in drugs:
        dropdown_options1.append(
            {"option_value": drug.drug_code, "option_name": drug.drug_name}
        )
    return dropdown_options1


def get_custom_dropdowns(options_value: str, options_name: str):
    dropdown_options2 = []
    all_dropdown_options = {"ALL": " "}
    options_value_list = [
        value.strip() for value in options_value.split(",") if value.strip()
    ]
    options_name_list = [
        name.strip() for name in options_name.split(",") if name.strip()
    ]
    for op_val, op_name in zip(options_value_list, options_name_list):
        # dropdown_options2.append(
        #     {"option_value": drug.drug_code, "option_name": drug.drug_name}
        # )
        dropdown_options2.append(
            {
                "option_value": f"{op_val}",
                "option_name": f"{op_name}",
            }
        )
        all_dropdown_options["ALL"] = all_dropdown_options["ALL"] + f"{op_val},"

    all_dropdown_options["ALL"] = all_dropdown_options["ALL"][:-1]

    dropdown_options2.append(
        {
            "option_value": all_dropdown_options["ALL"],
            "option_name": "ALL",
        }
    )

    return dropdown_options2


def get_input_tags(input_values):
    options_value_list = strip_input_vaules(input_values)
    input_tags = []
    for values in options_value_list:
        input_tags.append(values)
    return input_tags


def strip_input_vaules(input_values):
    options_value_list = [
        value.strip() for value in input_values.split(",") if value.strip()
    ]
    return options_value_list


def get_facility_dropdown(request):
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
    return facility


def sql_query_formater(sql_query: str, request, type=None, other_values=None):
    variables = {
        "variable1": request.POST.get("dropdown_options", ""),
        "variable2": request.POST.get("dropdown_options1", ""),
        "variable3": request.POST.get("dropdown_options2", ""),
        "facility_code": request.POST.get("facility_dropdown", ""),
        "from_date": date_formater(request.POST.get("from_date", "")),
        "to_date": date_formater(request.POST.get("to_date", "")),
    }

    if type == "input_tags":
        input_tag_values = strip_input_vaules(other_values)
        for inputs in input_tag_values:
            variables[inputs] = request.POST.get(inputs, "")

    if type == "date_time":
        from_time = request.POST.get("from_time", "")
        to_time = request.POST.get("to_time", "")
        variables["from_date"] = f"'{variables['from_date'][1:-1]} {from_time}'"
        variables["to_date"] = f"'{variables['to_date'][1:-1]} {to_time}'"

    # Remove empty or None values
    variables = {k: v for k, v in variables.items() if v}
    return sql_query, variables


def special_case_handler(request, sql_query, context):
    if sql_query.split(",")[-1] == "patient_wise_bill_details":
        excel_file_path = patient_wise_bill_details(request, context)
        return excel_file_path

    if sql_query.split(",")[-1] == "tpa_cover_letter":
        excel_file_path = tpa_cover_letter(request, context)
        return excel_file_path

    if sql_query.split(",")[-1] == "revenue_data_with_dates":
        excel_file_path = revenue_data_with_dates(request, context)
        return excel_file_path


def patient_wise_bill_details(request, context):
    try:
        from_date = request.POST["From_Date"]
        to_date = request.POST["To_Date"]

    except:
        from_date = None
        to_date = None

    try:
        facility_code = request.POST["facility_dropdown"]
        episode_code = request.POST["dropdown_options2"]
    except MultiValueDictKeyError:
        context["error"] = "😒 Please Select a facility from the dropdown list"
        return context

    # Convert and Split all Episode and UHID with commer separated values and then to tuple example : ('KH1000', 'KH1000')
    episode_id = request.POST["Episode_ID"]
    episode_id = tuple(episode_id.split())
    if len(episode_id) == 1:
        episode_id = f"('{episode_id[0]}')"

    uhid = request.POST["UHID"]
    uhid = tuple(uhid.split())
    if len(uhid) == 1:
        uhid = f"('{uhid[0]}')"

    db = Ora()
    (
        patientwise_bill_details_data,
        column_name,
    ) = db.get_patientwise_bill_details(
        uhid, episode_id, facility_code, episode_code, from_date, to_date
    )
    excel_file_path = excel_generator(
        page_name=context["page_name"],
        data=patientwise_bill_details_data,
        column=column_name,
    )

    if patientwise_bill_details_data:
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=patientwise_bill_details_data,
            column=column_name,
        )
        return excel_file_path
        return FileResponse(
            open(excel_file_path, "rb"), content_type="application/vnd.ms-excel"
        )
        # return render(request,'reports/one_for_all.html', {'patientwise_bill_details_data':patientwise_bill_details_data, 'user_name':request.user.get_full_name()})


def tpa_cover_letter(request, context):
    # Manually format To Date fro Sql Query
    from_date = date_formater(request.POST["from_date"])
    to_date = date_formater(request.POST["to_date"])

    db = Ora()
    (
        tpa_cover_letter_value,
        column_name,
    ) = db.get_tpa_cover_letter(from_date, to_date)
    system_os = platform.system()

    if system_os == "Linux":
        excel_file_path = excel_generator(
            data=tpa_cover_letter_value,
            column=column_name,
            page_name=context["page_name"],
        )
    else:
        excel_file_path = excel_generator_tpa(
            data=tpa_cover_letter_value,
            column=column_name,
            page_name=context["page_name"],
        )

    if tpa_cover_letter_value:
        return excel_file_path
        # return render(request,'reports/one_for_all.html', {'tpa_cover_letter_value':tpa_cover_letter_value, 'user_name':request.user.get_full_name(),'date_form' : DateForm()})


def revenue_data_with_dates(request, context):
    # Manually format To Date fro Sql Query
    # from_date = date_formater(request.POST["from_date"])
    # to_date = date_formater(request.POST["to_date"])
    from_date = request.POST["Date"]
    try:
        datetime.strptime(from_date, "%d-%b-%Y")
    except ValueError:
        context[
            "error"
        ] = " ❌ Incorrect date format.\n Please enter a date format in dd-Mon-yyyy. \n For Example 10-Mar-1993"
        return context

    # Select Function from model
    try:
        facility_code = request.POST["facility_dropdown"]
    except MultiValueDictKeyError:
        context["error"] = "😒 Please Select a facility from the dropdown list"
        return context

    db = Ora()
    revenue_data_with_dates_value, column_name = db.get_revenue_data_with_dates(
        facility_code, f"'{from_date}'", None
    )

    if revenue_data_with_dates_value:
        excel_file_path = excel_generator(
            page_name=context["page_name"],
            data=revenue_data_with_dates_value,
            column=column_name,
        )
        return excel_file_path
        # return render(request,'reports/one_for_all.html', {'revenue_data_with_dates_value':revenue_data_with_dates_value, 'user_name':request.user.get_full_name(),'date_form' : DateForm(),'facilities' : facility})
