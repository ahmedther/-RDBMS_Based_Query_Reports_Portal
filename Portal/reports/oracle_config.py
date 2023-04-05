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

    def check_users(self, pr_num, passw):
        sql_qurey = """
        

        SELECT a.APPL_USER_ID, a.APPL_USER_NAME Username,app_password.decrypt(a.APPL_USER_PASSWORD) Password  FROM sm_appl_user a   
        where  a.APPL_USER_ID= :user_id
        and  app_password.decrypt(a.APPL_USER_PASSWORD)=  :user_pass

        
        """

        self.cursor.execute(sql_qurey, [pr_num, passw])
        user_pass = self.cursor.fetchall()

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return user_pass

    def one_for_all(self, qurey):
        self.cursor.execute(qurey)
        data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        return data, column_name

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

    def get_patientwise_bill_details(
        self, uhid_id, episode_id, facility_code, episode_code, from_date, to_date
    ):
        patientwise_bill_details_qurey = f""" 

        
        select a.EPISODE_ID,a.PATIENT_ID,a.SERVICE_DATE,a.TRX_DATE,a.BLNG_SERV_CODE,a.SERV_ITEM_CODE,a.SERV_ITEM_DESC,a.EPISODE_TYPE,
        a.PRT_GRP_HDR_CODE,
        --a.PACKAGE_SERVICE_CODE,a.ENCOUNTER_ID
        a.SERV_QTY,a.ACT_GROSS_AMT Basic,a.ADDL_CHARGE_AMT_IN_CHARGE Tax,
        a.ORG_GROSS_CHARGE_AMT Gross,a.ORG_DISC_AMT Discount,a.ORG_NET_CHARGE_AMT Net_Amt,a.BILL_LEVEL_DISC_DSTRBTN_AMT overall_bill_disc,a.BLNG_GRP_ID,a.BED_CLASS_CODE,a.BILL_TYPE_CODE,
        a.DOC_DATE,a.BILL_DOC_TYPE_CODE,a.BILL_DOC_NUM,a.BILL_DOC_DATE,
        a.DISC_BY_ID,a.DISC_DATE,a.DISC_REASON_CODE,a.ACCT_DEPT_CODE,
        a.DISC_BY_ID,a.DISC_DATE,a.DISC_REASON_CODE,a.package_trx_yn,a.ACCT_DEPT_CODE,
        PACKAGE_SEQ_NO,ADDL_FACTOR_NUM
        from bl_patient_charges_folio A where 
        a.OPERATING_FACILITY_ID in ({facility_code})
        and a.EPISODE_TYPE in {episode_code} 
        and a.patient_id in {uhid_id}
        --BILL_DOC_NUM in('')
        and trx_status is null

"""
        if from_date == "":
            from_date = None

        if from_date is not None:
            patientwise_bill_details_qurey += f"and a.BILL_DOC_DATE between '{from_date}' and to_date('{to_date}') + 1\n"

        if "-" not in episode_id:
            patientwise_bill_details_qurey += f"and a.EPISODE_ID in {episode_id}"

        self.cursor.execute(patientwise_bill_details_qurey)
        patientwise_bill_details_qurey = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return patientwise_bill_details_qurey, column_name

    def get_tpa_cover_letter(self, from_date, to_date):
        gettpa_cover_letter_query = f"""
        
      -- SELECT distinct a.patient_id,b.PATIENT_NAME,a.DISCHARGE_DATE_TIME,
      -- h.long_name,f.TOT_BUS_GEN_AMT Total_Amount,i.bill_amt Pay_by_TPA,
      -- f.BILL_DOC_NUMBER Bill_Number,f.policy_number, g.credit_auth_ref
      -- ,i.doc_date
      -- FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f, 
      -- BL_ENCOUNTER_PAYER_Priority g,
      --  AR_CUSTOMER H, BL_Bill_HDR I
      -- WHERE a.PATIENT_ID=b.PATIENT_ID(+) AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID(+) and i.CUST_CODE = h.cust_code(+)
      -- and  a.PATIENT_ID=f.PATIENT_ID(+) and a.episode_id = f.episode_id(+) and f.episode_id = g.episode_id(+)
      --  and f.EPISODE_TYPE = 'I' 
      -- and a.patient_id = i.patient_id and a.episode_id = i.episode_id and a.episode_id = g.episode_id(+)
      -- and f.CUR_ACCT_SEQ_NO = g.ACCT_SEQ_NO(+)  and f.BLNG_GRP_ID = g.BLNG_GRP_ID(+)
      -- AND a.SPECIALTY_CODE = d.SPECIALITY_CODE(+) and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE(+) AND a.patient_class = 'IP' 
      -- and i.doc_type_code = f.bill_doc_type_code
      -- and i.doc_num = f.bill_doc_number
      -- and a.cancel_reason_code is null 
      -- and i.BLNG_GRP_ID IN ('1TPA','TPA','GTPA') 
      -- --and i.bill_amt <> 0
      -- and f.cust_code not in ('50000004','50000047','401240','30000332')
      -- AND i.doc_date between :from_date and to_date(:to_date) + 1
      -- and f.OPERATING_FACILITY_ID = 'KH'
      -- order by doc_date


            --SELECT distinct a.patient_id,b.PATIENT_NAME,i.doc_date,
            --h.long_name,f.TOT_BUS_GEN_AMT Total_Amount,i.bill_amt , F.APPROVED_AMT,
            --f.BILL_DOC_NUMBER Bill_Number,i.policy_number, g.credit_auth_ref,a.DISCHARGE_DATE_TIME

            SELECT distinct 
            a.patient_id,
            b.PATIENT_NAME,
            i.doc_date as DISCHARGE_DATE_TIME,
            --a.DISCHARGE_DATE_TIME,
            h.long_name,
            f.TOT_BUS_GEN_AMT Total_Amount,
            i.bill_amt Pay_by_TPA,
            f.BILL_DOC_NUMBER Bill_Number,
            i.policy_number,
            g.credit_auth_ref,
            i.doc_date
            FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f, 
            BL_ENCOUNTER_PAYER_Priority g, AR_CUSTOMER H, BL_Bill_HDR I
            WHERE a.PATIENT_ID=b.PATIENT_ID(+) AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID(+) and f.CUST_CODE = h.cust_code(+)
            and  a.PATIENT_ID=f.PATIENT_ID(+) and a.episode_id = f.episode_id(+) and f.episode_id = g.episode_id(+) and f.EPISODE_TYPE = 'I' 
            and a.patient_id = i.patient_id and a.episode_id = i.episode_id and a.episode_id = g.episode_id(+)
            and f.CUR_ACCT_SEQ_NO = g.ACCT_SEQ_NO(+)  
            and f.BLNG_GRP_ID = g.BLNG_GRP_ID(+)
            AND a.SPECIALTY_CODE = d.SPECIALITY_CODE(+) and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE(+) AND a.patient_class = 'IP' 
            and i.doc_type_code = f.bill_doc_type_code --and i.doc_num = f.bill_doc_number 
            and a.cancel_reason_code is null 
            and i.BLNG_GRP_ID IN ('1TPA','TPA','GTPA')      and i.bill_amt <> 0      
            and f.cust_code not in ('50000004','50000047','401240','30000332')
            AND i.doc_date between {from_date} and to_date({to_date}) + 1
            --and a.patient_id = 'KH1000846238'
            and f.OPERATING_FACILITY_ID = 'KH'
            and I.BILL_STATUS is null
            order by doc_date


"""
        self.cursor.execute(gettpa_cover_letter_query)
        gettpa_cover_letter_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return gettpa_cover_letter_data, column_name

    def get_revenue_data_with_dates(self, facility_code, from_date, to_date):
        revenue_data_with_dates_query = f""" 
        
        
        CREATE OR REPLACE FORCE VIEW revenue_data_vw (ser_date,
                                             ser_time,
                                             txn_date,
                                             txn_time,
                                             serv_code,
                                             serv_desc,
                                             serv_grp_code,
                                             serv_grp_desc,
                                             physician_id,
                                             patienttype,
                                             patient_id,
                                             pat_name,
                                             amount,
                                             disc_amount,
                                             rounding_amount,
                                             addl_chg,
                                             episode_id,
                                             encounter_id,
                                             store_code,
                                             blng_class_code,
                                             bed_class_code,
                                             gl_code,
                                             dept_code_rev
                                            )
AS
   SELECT NULL ser_date, NULL ser_time,
                                       --a.acct_dept_code dept_code, e.long_desc dept_name,
          NULL txn_date, NULL txn_time, NULL serv_code, NULL serv_desc,
          NULL serv_grp_code, NULL serv_grp_desc, NULL physician_id,
          NULL patienttype, NULL patient_id, NULL pat_name,
          NVL (f.amount, 0) amount, NVL (d.amount, 0) disc_amount,
          NVL (o.amount, 0) rounding_amount, 0 addl_chg, NULL episode_id,
          NULL encounter_id, NULL store_code, NULL blng_class_code,
          NULL bed_class_code, f.main_acc1_code gl_code,
          f.dept_code dept_code_rev
     FROM (SELECT   gl.main_acc1_code, gl.dept_code,
                    DECODE (gl.trx_type_code,
                            'F', SUM (gl.distribution_amt),
                            0
                           ) amount
               FROM bl_gl_distribution gl
              WHERE gl.operating_facility_id in ({facility_code})
                AND trunc(gl.trx_date) BETWEEN {from_date} and to_date({to_date})
                AND gl.main_acc1_code = '222410'
                AND gl.trx_type_code = 'F'
           GROUP BY gl.main_acc1_code, gl.dept_code, gl.trx_type_code) f,
          (SELECT   gl.main_acc1_code, gl.dept_code,
                    DECODE (gl.trx_type_code,
                            'D', SUM (gl.distribution_amt),
                            0
                           ) amount
               FROM bl_gl_distribution gl
              WHERE gl.operating_facility_id in ({facility_code})
                AND trunc(gl.trx_date) BETWEEN {from_date} and to_date({to_date})
                AND gl.main_acc1_code = '222410'
                AND gl.trx_type_code = 'D'
           GROUP BY gl.main_acc1_code, gl.dept_code, gl.trx_type_code) d,
          (SELECT   gl.main_acc1_code, gl.dept_code,
                    DECODE (gl.trx_type_code,
                            'O', SUM (gl.distribution_amt),
                            0
                           ) amount
               FROM bl_gl_distribution gl
              WHERE gl.operating_facility_id  in ({facility_code})
                AND trunc(gl.trx_date) BETWEEN {from_date} and to_date({to_date})
                AND gl.main_acc1_code = '222410'
                AND gl.trx_type_code = 'O'
           GROUP BY gl.main_acc1_code, gl.dept_code, gl.trx_type_code) o
    WHERE f.main_acc1_code = d.main_acc1_code(+) AND f.main_acc1_code = o.main_acc1_code(+)
   UNION ALL
   SELECT TO_CHAR (a.service_date, 'DD/MM/YY') ser_date,
          TO_CHAR (a.service_date, 'HH24:MI:SS') ser_time,
          
          --a.acct_dept_code dept_code, e.long_desc dept_name,
          TO_CHAR (a.trx_date, 'DD/MM/YY') txn_date,
          TO_CHAR (a.trx_date, 'HH24:MI:SS') txn_time,
          a.blng_serv_code serv_code, c.long_desc serv_desc,
          c.serv_grp_code serv_grp_code, d.long_desc serv_grp_desc,
          a.physician_id physician_id,
          DECODE (a.episode_type,
                  'I', 'IP',
                  'O', 'OP',
                  'E', 'Emergency',
                  'R', 'Referral',
                  'D', 'Daycare'
                 ) patienttype,
          a.patient_id patient_id, b.short_name pat_name,
          (CASE
              WHEN a.episode_type <> 'R'
              AND ((a.addl_charge_amt_in_charge * -1) = gl.distribution_amt)
                 THEN
                     --decode(gl.main_Acc1_code ,140211,(a.addl_charge_amt_in_charge*-1),0)
                     DECODE (gl.main_acc1_code,
                             140211, (a.addl_charge_amt_in_charge * -1),
                             140212, (a.addl_charge_amt_in_charge * -1),
                             140213, (a.addl_charge_amt_in_charge * -1),
                             140214, (a.addl_charge_amt_in_charge * -1),
                             0
                            )
              ELSE DECODE (gl.trx_type_code, 'F', gl.distribution_amt, 0)
           END
          ) amount,
          
          --DECODE(gl.trx_type_code,'F',gl.distribution_amt, 0)amount,
          DECODE (gl.trx_type_code, 'D', gl.distribution_amt, 0) disc_amount,
          DECODE (gl.trx_type_code,
                  'O', gl.distribution_amt,
                  0
                 ) rounding_amt,
          
          -- ADDED ON 30/10/2012
          (CASE
              WHEN a.episode_type = 'R' AND (gl.rule_code LIKE 'RULE%')
                 THEN (a.addl_charge_amt_in_charge)
              WHEN a.episode_type <> 'R' AND (gl.rule_code LIKE 'S%')
                 THEN (a.addl_charge_amt_in_charge)
              WHEN a.episode_type <> 'R'
              AND ((a.addl_charge_amt_in_charge * -1) = gl.distribution_amt)
                 THEN 0
              ELSE 0
           END
          ) addl_chg,
          
          -- 30/10/2012 commented DECODE (a.episode_type,'R', NVL (a.addl_charge_amt_in_charge, 0),0) addl_chg,
          a.episode_id episode_id, a.encounter_id encounter_id,
          a.store_code store_code, a.blng_class_code blng_class_code,
          a.bed_class_code bed_class_code, gl.main_acc1_code gl_code,
          gl.dept_code dept_code_rev
     FROM bl_gl_distribution gl,
          bl_patient_charges_folio a,
          mp_patient_mast b,
          bl_blng_serv c,
          bl_blng_serv_grp d,
          am_dept_lang_vw e
    WHERE a.operating_facility_id  in ({facility_code})
      AND a.patient_id = gl.patient_id
      AND a.patient_id = b.patient_id
      AND a.trx_doc_ref = gl.trx_doc_ref
      AND a.trx_doc_ref_line_num = gl.trx_doc_ref_line_num
      AND a.trx_doc_ref_seq_num = gl.trx_doc_ref_seq_num
      AND trunc(gl.trx_date) BETWEEN {from_date} and to_date({to_date})
      AND gl.main_acc1_code <> '222410'
      AND a.blng_serv_code = c.blng_serv_code
      AND c.serv_grp_code = d.serv_grp_code
      AND a.acct_dept_code = e.dept_code(+)
   UNION ALL
   SELECT TO_CHAR (a.doc_date, 'DD/MM/YY') ser_date,
          TO_CHAR (a.doc_date, 'HH24:MI:SS') ser_time,
          
          --gl.dept_code dept_code, e.long_desc dept_name,
          TO_CHAR (gl.trx_date, 'DD/MM/YY') txn_date,
          TO_CHAR (gl.trx_date, 'HH24:MI:SS') txn_time, NULL serv_code,
          'Discount' serv_desc, NULL serv_grp_code, NULL serv_grp_desc,
          NULL physician_id,
          DECODE (a.episode_type,
                  'I', 'IP',
                  'O', 'OP',
                  'E', 'Emergency',
                  'R', 'Referral',
                  'D', 'Daycare'
                 ) patienttype,
          a.patient_id patient_id, b.short_name pat_name, 0 amount,
          NVL (a.overall_disc_amt, 0) disc_amount, 0 rounding_amt, 0 addl_chg,
          a.episode_id episode_id, a.encounter_id encounter_id, NULL, NULL,
          a.bed_class_code bed_class_code, gl.main_acc1_code gl_code,
          gl.dept_code dept_code_rev
     FROM bl_gl_distribution gl,
          bl_bill_hdr a,
          mp_patient_mast b,
          am_dept_lang_vw e
    WHERE a.operating_facility_id  in ({facility_code})
      AND a.patient_id = gl.patient_id
      AND a.patient_id = b.patient_id
      AND a.doc_date = gl.trx_date
      AND a.doc_type_code = gl.doc_type
      AND a.doc_num = gl.doc_no
      AND a.overall_disc_amt <> 0
      AND trunc(gl.trx_date) BETWEEN {from_date} and to_date({to_date})
      --05/07/2012 AND gl.main_acc1_code  in  ('222410','409998','400570','400590','400580','400600','400610','400620','400630','400640','400650','400660','400670','400680')  -- ONLY DISCOUNT
      AND gl.main_acc1_code IN
             ('409998', '400575')
--, '400570', '400590', '400580', '400600','400610', '400620', '400630', '400640', '400650', '400660','400670', '400680')-- ONLY DISCOUNT
      AND gl.trx_type_code = 'D'
      AND gl.dept_code = e.dept_code(+)
   UNION ALL
   SELECT TO_CHAR (a.doc_date, 'DD/MM/YY') ser_date,
          TO_CHAR (a.doc_date, 'HH24:MI:SS') ser_time,
          
          --gl.dept_code dept_code, e.long_desc dept_name,
          TO_CHAR (gl.trx_date, 'DD/MM/YY') txn_date,
          TO_CHAR (gl.trx_date, 'HH24:MI:SS') txn_time, NULL serv_code,
          'Rounding off' serv_desc, NULL serv_grp_code, NULL serv_grp_desc,
          NULL physician_id,
          DECODE (a.episode_type,
                  'I', 'IP',
                  'O', 'OP',
                  'E', 'Emergency',
                  'R', 'Referral',
                  'D', 'Daycare'
                 ) patienttype,
          a.patient_id patient_id, b.short_name pat_name, 0 amount,
          0 disc_amount, NVL (a.bill_rounding_amt, 0) rounding_amt,
          0 addl_chg, a.episode_id episode_id, a.encounter_id encounter_id,
          NULL, NULL, a.bed_class_code bed_class_code,
          gl.main_acc1_code gl_code, gl.dept_code dept_code_rev
     FROM bl_gl_distribution gl,
          bl_bill_hdr a,
          mp_patient_mast b,
          am_dept_lang_vw e
    WHERE a.operating_facility_id in ({facility_code})
      AND a.patient_id = gl.patient_id
      AND a.patient_id = b.patient_id
      AND a.doc_date = gl.trx_date
      AND a.doc_type_code = gl.doc_type
      AND a.doc_num = gl.doc_no
      AND a.bill_rounding_amt <> 0
      AND trunc(gl.trx_date) BETWEEN {from_date} and to_date({to_date})
      AND gl.main_acc1_code IN ('401220')                 -- ONLY ROUNDING OFF
      AND gl.trx_type_code = 'O'
      AND gl.dept_code = e.dept_code(+)




"""

        self.cursor.execute(revenue_data_with_dates_query)

        revenue_data_with_dates_query_2 = f""" select * from revenue_data_vw """

        self.cursor.execute(revenue_data_with_dates_query_2)
        revenue_data_with_dates_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return revenue_data_with_dates_data, column_name


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
