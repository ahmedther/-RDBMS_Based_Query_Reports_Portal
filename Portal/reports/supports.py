import pandas as pd
import os
import logging
import xlwings as xw


from pathlib import Path
from django.shortcuts import render
from datetime import datetime
from multiprocessing.dummy import Pool

from .oracle_config import Ora


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
    date = date.split("-")
    date_year = int(date[0])
    date_month = int(date[1])
    date_day = int(date[2])
    date_format = datetime(date_year, date_month, date_day)
    date = date_format.strftime("%d-%b-%Y")
    return date


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
            pass

        # Setting the length if the column header is larger
        # than the max column value length
        try:
            column_len = max(column_len, len(col)) + 4

        except:
            pass

        # set the column length
        worksheet.set_column(i, i, column_len)

    generate_excel.save()
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

def excel_generator_tpa(data, column,page_name):
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
    #TPA File Location
    #Was forced to keep this location, as ref https://stackoverflow.com/questions/14037412/cannot-access-excel-file
    tpa_excel_path = r"C:\Windows\System32\config\systemprofile\desktop\tpa_cover_format.xlsb"
    #tpa_excel_path = f"{parent_path}/web_excel_files/tpa_cover_letter/tpa_cover_format.xlsb"
    
    #Have to use unconventional import here to avoid errors deployment in Linux

    import pythoncom
    #Initialize to avoid error Using XLWings with parallel processing
    pythoncom.CoInitialize()

    #load workbook
    xlwing_app = xw.App(visible=False)
    tpa_workbook = xw.Book(tpa_excel_path)  
    tpa_worksheet_query = tpa_workbook.sheets['Query']
    tpa_worksheet_uhid = tpa_workbook.sheets['UHID']

    tpa_worksheet_query.range('A2:J500').clear_contents()
    tpa_worksheet_uhid.range("A1:A500").clear_contents()
    excel_data = pd.DataFrame(data=data, columns=list(column))

    #Update workbook at specified range for Query Sheet
    tpa_worksheet_query.range('A2').options(index=False,header=False).value = excel_data
    tpa_worksheet_uhid.range('A1').options(index=False,header=False).value = excel_data['PATIENT_ID']

    #Close workbook
    tpa_workbook.save(excel_file_path)
    tpa_workbook.close()
    xlwing_app.quit()

    return excel_file_path
