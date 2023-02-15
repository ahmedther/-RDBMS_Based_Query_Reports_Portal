import cx_Oracle as oracle

# from oracle_config import *

ip = "172.20.200.16"

host = "khdb-scan.kdahit.com"

port = 1521

service_name = "newdb.kdahit.com"

instance_name = "NEWDB"

# ora_db = oracle.connect("appluser","appluser",dsn_tns)

# cursor = ora_db.cursor()


# host = 'khdb-scan'

# port = 1521

# service_name = "newdb.kdahit.com"

# instance_name = "NEWDB"

# dsn_tns = oracle.makedsn(ip,port,instance_name)

# ora_db = oracle.connect("ibaehis","ib123",dsn_tns)

# cursor = ora_db.cursor()


#   'oracle': {
#     'ENGINE': 'django.db.backends.oracle',
#     'NAME': 'NEWDB:1521/newdb.kdahit.com',
#     'NAME': ('(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=khdb-scan)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=newdb.kdahit.com)))'),
#     'USER': 'ibaehis',
#     'PASSWORD': 'ib123',


class Ora:
    def __init__(self):
        self.dsn_tns = oracle.makedsn(host, port, service_name=service_name)
        self.ora_db = oracle.connect("ibaehis", "ib123", self.dsn_tns)
        self.cursor = self.ora_db.cursor()

    def status_update(self):

        if self.ora_db:
            return "You have connected to the Database"

        else:
            return "Unable to connect to the database! Please contact the IT Department"

    # def __del__(self):
    # self.cursor.close()
    # self.ora_db.close()

    def get_indore_revenue_report(self, revenue_data_indore):
        daily_revenue_reports_qurey = f""" 

        Select * from {revenue_data_indore} order by amount desc 

"""

        self.cursor.execute(
            daily_revenue_reports_qurey,
        )
        data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    # Indore Miscellaneous
    # Indore Billing

    def get_discharge_billing_report_without_date_range_indore(self):

        discharge_billing_report_without_date_range_indore_query = """
        
        

      select a.patient_id,a.encounter_id,initcap(short_name),alternate_id3_num,dis_adv_date_time,a.added_by_id,c.appl_user_name, 
      b.other_contact_num,d.BED_NUM,e.BLNG_GRP_ID
      from ip_discharge_advice a,mp_patient_mast b,sm_appl_user_vw c,IP_OPEN_ENCOUNTER d,bl_episode_fin_dtls e
      where a.dis_adv_status='0' 
      and a.patient_id = b.patient_id 
      and a.patient_id = d.patient_id
      and a.patient_id = e.patient_id
      and a.encounter_id = d.ENCOUNTER_ID
      and a.encounter_id = e.ENCOUNTER_ID
      and a.added_by_id = c.appl_user_id 
      and c.language_id='en' and a.FACILITY_ID  ='IN' 
      and not exists (select * from bl_bill_hdr h where h.patient_id=a.patient_id and h.episode_id = a.encounter_id and h.bill_status<>'C')
      order by dis_adv_date_time 
        
        """

        self.cursor.execute(discharge_billing_report_without_date_range_indore_query)
        discharge_billing_report_without_date_range_indore_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return discharge_billing_report_without_date_range_indore_data, column_name


if __name__ == "__main__":
    a = Ora()
    # b = a.get_online_consultation_report('01-Mar-2022','03-Apr-2022')
    b = a.get_employee_covid_test_report(
        "KH",
        "13-Aug-2022",
        "13-Aug-2022",
    )

    print(b)

    for x in b:
        print(x)
