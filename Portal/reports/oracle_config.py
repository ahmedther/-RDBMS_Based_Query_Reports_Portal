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

    def get_stock(self):

        stock_qurey = """
        
        
            SELECT DISTINCT A.STORE_CODE, A.ITEM_CODE, B.LONG_DESC, A.BATCH_ID,A.QTY_ON_HAND, A.COMMITTED_QTY FROM ST_ITEM_BATCH A, MM_ITEM B WHERE A.STORE_CODE = 'PS' AND A.ITEM_CODE=B.ITEM_CODE
        
        """

        self.cursor.execute(stock_qurey)
        data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_stock_reports(self, store_code):

        stock_reports_query = f"""
        
        
            SELECT a.QTY_ON_HAND, a.COMMITTED_QTY, 
            to_char(NVL (a.QTY_ON_HAND, 0) - NVL (a.COMMITTED_QTY, 0)) AVAIL_Qty,a.STORE_CODE, 
            a.BATCH_ID, a.EXPIRY_DATE_OR_RECEIPT_DATE, a.ITEM_CODE, b.LONG_DESC FROM IBAEHIS.ST_ITEM_BATCH a, 
            MM_ITEM b WHERE  a.ITEM_CODE = b.ITEM_CODE 
            and a.STORE_CODE in ({store_code})
            ORDER BY a.STORE_CODE, a.ITEM_CODE,a.EXPIRY_DATE_OR_RECEIPT_DATE
        
        """

        self.cursor.execute(stock_reports_query)
        stock_reports_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return stock_reports_data, column_name

    def get_store_code_stock_reports(self):

        stock_value_query = f""" 
        select distinct a.STORE_CODE,b.FACILITY_ID from st_item_batch a
        left join mm_store b on (a.STORE_CODE = b.STORE_CODE)
        ORDER BY b.FACILITY_ID, a.STORE_CODE

        """

        self.cursor.execute(stock_value_query)
        stock_value_data = self.cursor.fetchall()

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return stock_value_data

    def get_stock_value(self, store_code):

        stock_value_query = f""" 
            SELECT a.ITEM_CODE AS ItemCode, a.ITEM_DESC AS Description,a.STORE_CODE AS StoreCode,
            SUM(a.QTY_ON_HAND) AS QtyOnHand,sum(a.AVAIL_QTY) AS AvailStock,
            sum(a.QTY_ON_HAND - a.AVAIL_QTY) AS InTransitStock,
            d.last_receipt_date AS LastInward, 
             case when(d.material_group_code = 'KDHMD3') then('Pharma') 
             when(d.material_group_code <> 'KDHMD3') then('surgical') else null end as MaterialCategory
             FROM IBAEHIS.ST_BATCH_SEARCH_LANG_VIEW a 
            left join ST_BATCH_CONTROL b on(a.ITEM_CODE = b.ITEM_CODE and a.BATCH_ID = b.BATCH_ID 
            and a.EXPIRY_DATE = b.EXPIRY_DATE_OR_RECEIPT_DATE)
            left join st_item c on(a.ITEM_CODE = c.ITEM_CODE)
            left join mm_item d on(a.item_code = d.item_code)
            WHERE(b.SALE_PRICE >= '700' and b.SALE_PRICE <= '799') AND(a.STORE_CODE = :store_code)
            AND(a.ITEM_CODE LIKE '2000%') AND(c.CONSIGNMENT_ITEM_YN = 'N')
            GROUP BY a.ITEM_CODE, a.ITEM_DESC,a.STORE_CODE,d.last_receipt_date,d.material_group_code ORDER BY d.material_group_code,a.ITEM_DESC ASC
        """

        self.cursor.execute(stock_value_query, [store_code])
        stock_value_data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return stock_value_data, column_name

    def get_bin_location_op_value(self, store_code):

        bin_location_op_query = f""" 

        SELECT ST_ITEM_STORE.STORE_CODE, ST_ITEM_STORE.ITEM_CODE, MM_ITEM.LONG_DESC, MM_BIN_LOCATION.LONG_DESC 
        FROM IBAEHIS.MM_BIN_LOCATION MM_BIN_LOCATION, IBAEHIS.MM_ITEM MM_ITEM, IBAEHIS.ST_ITEM_STORE ST_ITEM_STORE
        WHERE ST_ITEM_STORE.ITEM_CODE = MM_ITEM.ITEM_CODE AND ST_ITEM_STORE.BIN_LOCATION_CODE = MM_BIN_LOCATION.BIN_LOCATION_CODE 
        AND ((ST_ITEM_STORE.STORE_CODE=:store_code))

            """

        self.cursor.execute(bin_location_op_query, [store_code])
        bin_location_op_query_data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return bin_location_op_query_data, column_name

    def get_store_code_ST_BATCH_SEARCH_LANG_VIEW(self):
        store_code_ST_BATCH_SEARCH_LANG_VIEW = f""" 

        select distinct a.STORE_CODE, a.STORE_DESC, b.FACILITY_ID from ST_BATCH_SEARCH_LANG_VIEW a, mm_store b
        where a.STORE_CODE = b.STORE_CODE
        order by FACILITY_ID

        """

        self.cursor.execute(store_code_ST_BATCH_SEARCH_LANG_VIEW)
        store_code_ST_BATCH_SEARCH_LANG_VIEW_data = self.cursor.fetchall()

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return store_code_ST_BATCH_SEARCH_LANG_VIEW_data

    def get_itemwise_storewise_stock(self):
        itemwise_storewise_stock_query = (
            "select"
            + " a.store_code AS STORE,"
            + " a.item_code AS ITEM_CODE,  "
            + "b.long_desc AS iTEM_NAME,"
            + "a.qty_on_hand AS QOH, "
            + "ROUND(a.item_value,0) AS VALUE "
            + " from st_item_store a , "
            + " mm_item b "
            + "where (a.item_code = b.item_code) "
            + "and ((a.qty_on_hand <> 0))"
            + " order by a.store_code"
        )

        self.cursor.execute(itemwise_storewise_stock_query)
        itemwise_storewise_stock_data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return itemwise_storewise_stock_data, column_name

    def get_batchwise_stock_report(self, facility_code):
        batchwise_stock_report_query = f""" 


        select a.STORE_CODE  as Store, a.ITEM_CODE as ItemCode,c.LONG_DESC  as ItemName,a.BATCH_ID as Batch,a.EXPIRY_DATE_OR_RECEIPT_DATE as Expiry,
        max(a.QTY_ON_HAND) as StockQty, max(a.COMMITTED_QTY) COMMITTED_QTY, max(to_char(NVL (a.QTY_ON_HAND, 0) - NVL (a.COMMITTED_QTY, 0))) AVAIL_Qty,
        max(decode(g.GRN_UNIT_COST_IN_PUR_UOM,null,c.UNIT_COST,g.GRN_UNIT_COST_IN_PUR_UOM)) as UnitCost,  max(g.SALE_PRICE) as MRP from 
        st_item_batch a, mm_item c,xi_trn_grn g where
        g.ITEM_CODE =a.ITEM_CODE and g.XI_BATCH_ID = a.BATCH_ID and g.EXPIRY_DATE= a.EXPIRY_DATE_OR_RECEIPT_DATE
        and a.ITEM_CODE = c.ITEM_CODE
        and g.SUPP_CODE <> '101320' 
        and a.STORE_CODE in (select store_code from mm_store where facility_id in ({facility_code}))
        group by     a.STORE_CODE  , a.ITEM_CODE ,c.LONG_DESC  ,a.BATCH_ID ,a.EXPIRY_DATE_OR_RECEIPT_DATE  
        order by a.STORE_CODE,a.ITEM_CODE


        """
        self.cursor.execute(batchwise_stock_report_query)
        batchwise_stock_report_data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return batchwise_stock_report_data, column_name

    def get_current_inpatients_report(self, facility_code):
        get_current_inpatients_report_qurey = f"""
        
        select distinct a.patient_id as Patient_UHID,b.PATIENT_NAME as Patient_Name, a.encounter_id as Encounter_ID,a.NURSING_UNIT_CODE,a.bed_num as Bed_No,  
        b.SEX as Sex,round(((sysdate-b.date_of_birth)/365)) as Patient_Age, c.PRACTITIONER_ID as Attending_Practitioner_ID ,c.PRACTITIONER_NAME as Attending_Practitioner,d.LONG_DESC Speciality,
        a.ADMISSION_DATE_TIME as Admitted_On  
        from ip_open_encounter a,mp_patient b,am_practitioner c,am_speciality d
        where a.facility_id in ({facility_code})  and a.PATIENT_ID=b.PATIENT_ID 
        and a.ATTEND_PRACTITIONER_ID=c.PRACTITIONER_ID 
        AND a.SPECIALTY_CODE = d.SPECIALITY_CODE

  
  """

        self.cursor.execute(get_current_inpatients_report_qurey)
        get_current_inpatients_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_current_inpatients_report_data, column_name

    def get_pharmacy_op_returns(self, facility_code):
        pharmacy_op_returns_query = f"select distinct * from  GST_DATA_PH_RET  where BILL_DOC_DATE >= ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -30) and OPERATING_FACILITY_ID in ({facility_code}) "

        self.cursor.execute(pharmacy_op_returns_query)
        pharmacy_op_returns_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return pharmacy_op_returns_data, column_name

    def get_restricted_antimicrobials_consumption_report(
        self, from_date, to_date, store_code, facility_code
    ):
        getrestricted_antimicrobials_consumption_report_query = f"""
        select distinct a.FACILITY_ID,a.ADDED_DATE TRN_DATE, b.ITEM_CODE ITEM_CODE, c.DRUG_DESC ITEM_NAME, c.GENERIC_NAME GENERIC_NAME, a.ENCOUNTER_ID ENCOUNTER_ID, 
        a.PATIENT_ID PATIENT_ID, d.PATIENT_NAME PATIENT_NAME,d.SEX ,TRUNC(MONTHS_BETWEEN(sysdate, d.DATE_OF_BIRTH )/12) as Age,  f.ASSIGN_BED_NUM CURR_BED_NO, b.SAL_ITEM_QTY SAL_QTY, b.RET_ITEM_QTY RETURN_QTY, 
        (b.SAL_ITEM_QTY-b.RET_ITEM_QTY) NET_CHARGED, f.VISIT_ADM_DATE_TIME ADMISSION_DATE, f.DISCHARGE_DATE_TIME DISCHARGED_DATE, a.STORE_CODE STORE_CODE, 
        a.DOC_NO DOC_NO,b.DOC_SRL_NO SRL_NO,a.DOC_TYPE_CODE TRN_TYPE,g.PRACTITIONER_NAME,g.PRIMARY_SPECIALITY_CODE  
        from st_sal_hdr a,st_sal_dtl_exp b,PH_DRUG_VW_LANG_VW c,mp_patient d,ip_nursing_unit_bed e,pr_encounter f ,am_practitioner g 
        where a.DOC_NO=b.DOC_NO and b.ITEM_CODE=c.DRUG_CODE and d.PATIENT_ID=a.PATIENT_ID and e.OCCUPYING_PATIENT_ID(+)=a.PATIENT_ID 
        and a.DOC_TYPE_CODE=b.DOC_TYPE_CODE and c.PRES_CATG_CODE = '10' and f.ENCOUNTER_ID=a.ENCOUNTER_ID and f.ATTEND_PRACTITIONER_ID=g.PRACTITIONER_ID   
        and a.DOC_TYPE_CODE = :store_code and a.FACILITY_ID in ({facility_code}) and a.DOC_DATE between :from_date and :to_date order by a.ADDED_DATE asc


"""
        self.cursor.execute(
            getrestricted_antimicrobials_consumption_report_query,
            [store_code, from_date, to_date],
        )
        getrestricted_antimicrobials_consumption_report_data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return getrestricted_antimicrobials_consumption_report_data, column_name

    def get_st_sal_hdr(self):
        getst_sal_hdr_query = f"""
        select distinct DOC_TYPE_CODE, FACILITY_ID  from st_sal_hdr 
        order by FACILITY_ID


"""
        self.cursor.execute(getst_sal_hdr_query)
        getst_sal_hdr_data = self.cursor.fetchall()
        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return getst_sal_hdr_data

    def get_pharmacy_itemwise_sale_report(
        self, drug_code, from_date, to_date, store_code, facility_code
    ):
        get_pharmacy_itemwise_sale_report_query = f"""
        
        select distinct a.ADDED_DATE TRN_DATE, b.ITEM_CODE ITEM_CODE, c.DRUG_DESC ITEM_NAME, c.GENERIC_NAME GENERIC_NAME, 
        a.ENCOUNTER_ID ENCOUNTER_ID, a.PATIENT_ID PATIENT_ID,d.PATIENT_NAME PATIENT_NAME,d.SEX ,
        MONTHS_BETWEEN(sysdate, d.DATE_OF_BIRTH )/12 as Age, f.ASSIGN_BED_NUM CURR_BED_NO ,f.ASSIGN_CARE_LOCN_CODE ORDERING_LOCN,
        h.PRACTITIONER_NAME TREATING_DOC, i.LONG_DESC SPECIALITY, f.REFERRAL_ID REFERRALID, b.SAL_ITEM_QTY SAL_QTY,
        b.RET_ITEM_QTY RETURN_QTY,(b.SAL_ITEM_QTY-b.RET_ITEM_QTY) NET_CHARGED,f.VISIT_ADM_DATE_TIME ADMISSION_DATE,
        f.DISCHARGE_DATE_TIME DISCHARGED_DATE, a.STORE_CODE STORE_CODE,a.DOC_NO DOC_NO,b.DOC_SRL_NO SRL_NO,a.DOC_TYPE_CODE TRN_TYPE,g.LONG_DESC as Description
        from st_sal_hdr a,st_sal_dtl_exp b,PH_DRUG_VW_LANG_VW c,mp_patient d,ip_nursing_unit_bed e,pr_encounter f ,
        PH_DRUG_CATG g, am_practitioner h, AM_SPECIALITY i
        where a.DOC_NO=b.DOC_NO and b.ITEM_CODE=c.DRUG_CODE and d.PATIENT_ID=a.PATIENT_ID and e.OCCUPYING_PATIENT_ID(+)=a.PATIENT_ID
        and a.DOC_TYPE_CODE=b.DOC_TYPE_CODE and f.ATTEND_PRACTITIONER_ID = h.PRACTITIONER_ID and f.SPECIALTY_CODE = i.SPECIALITY_CODE 
        and g.DRUG_CATG_CODE = c.PRES_CATG_CODE 
        and c.PRES_CATG_CODE in ({drug_code})
        and f.ENCOUNTER_ID=a.ENCOUNTER_ID 
        and a.DOC_TYPE_CODE in (:store_code) and a.FACILITY_ID in ({facility_code}) 
        and a.DOC_DATE between :from_date and :to_date order by a.ADDED_DATE asc


"""
        self.cursor.execute(
            get_pharmacy_itemwise_sale_report_query,
            [store_code, from_date, to_date],
        )
        get_pharmacy_itemwise_sale_report_query_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return (
            get_pharmacy_itemwise_sale_report_query_data,
            column_name,
        )

    def get_DOC_TYPE_CODE_st_sal_hdr(self):
        get_DOC_TYPE_CODE_st_sal_hdr = f"""
        
        select distinct DOC_TYPE_CODE , FACILITY_ID from st_sal_hdr order by FACILITY_ID


        """

        self.cursor.execute(get_DOC_TYPE_CODE_st_sal_hdr)
        get_DOC_TYPE_CODE_st_sal_hdr_data = self.cursor.fetchall()

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_DOC_TYPE_CODE_st_sal_hdr_data

    def get_pharmacy_indent_report(self):

        get_pharmacy_indent_report_qurey = (
            " select a.PATIENT_ID Pat_ID,a.ENCOUNTER_ID Enc_ID,a.PATIENT_CLASS Pat_Class,a.PAT_CURR_LOCN_CODE Current_Locn,a.ASSIGN_ROOM_NUM Room_No, "
            + " a.VISIT_ADM_DATE_TIME Visit_Date_Time,c.ORD_DATE_TIME Order_Date_Time,c.ORDER_CATALOG_CODE Item_Code,c.CATALOG_DESC Item_Desc,c.ORDER_QTY Order_Qty, "
            + " d.DISP_QTY Disp_Qty,e.LONG_DESC Order_Status,d.modified_date Dispensed_Date "
            + " from pr_encounter a, or_order b, or_order_line c,ph_disp_dtl d,OR_ORDER_STATUS_CODE e "
            + " where a.ENCOUNTER_ID = b.ENCOUNTER_ID and b.ORDER_ID=c.ORDER_ID  "
            + " and c.ORDER_ID=d.ORDER_ID and c.ORDER_LINE_STATUS=e.ORDER_STATUS_CODE  "
            + " and a.PAT_CURR_LOCN_CODE not in ('FL9C','FL9W')and a.facility_id = 'KH'  and a.patient_class = 'IP' and b.order_category = 'PH' "
            + " and b.ORD_DATE_TIME between a.VISIT_ADM_DATE_TIME and (a.VISIT_ADM_DATE_TIME+4/24) and trunc(a.visit_adm_date_time) >= trunc(sysdate) "
            + " order by d.modified_date desc "
        )

        self.cursor.execute(get_pharmacy_indent_report_qurey)
        get_pharmacy_indent_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_pharmacy_indent_report_data, column_name

    def get_new_admission_indents_report(self, from_date, to_date, facility_code):
        # get_pharmacy_indent_report_qurey = ('''
        #     select a.PATIENT_ID Pat_ID, a.PAT_CURR_LOCN_CODE Current_Location,a.ASSIGN_ROOM_NUM Room_No,c.ORDER_CATALOG_CODE Item_Code,
        #     c.CATALOG_DESC Item_Desc,c.ORDER_QTY Order_Qty,c.ORD_DATE_TIME Order_Date_Time
        #     from pr_encounter a, or_order b, or_order_line c,ph_disp_dtl d,OR_ORDER_STATUS_CODE e
        #     where a.ENCOUNTER_ID = b.ENCOUNTER_ID and b.ORDER_ID=c.ORDER_ID and c.ORDER_ID=d.ORDER_ID and c.ORDER_LINE_STATUS=e.ORDER_STATUS_CODE
        #     and a.PAT_CURR_LOCN_CODE not in ('FL9C','FL9W') and a.facility_id =  'KH' and a.patient_class = 'IP' and b.order_category = 'PH'
        #     and b.ORD_DATE_TIME between a.VISIT_ADM_DATE_TIME and (a.VISIT_ADM_DATE_TIME+4/24) and
        #     trunc(a.visit_adm_date_time) >= sysdate - 2 order by c.ORD_DATE_TIME desc
        #     '''
        # )

        get_pharmacy_indent_report_qurey = f""" 
        
            select a.visit_adm_date_time,a.PATIENT_ID Pat_ID, a.PAT_CURR_LOCN_CODE Current_Location,a.ASSIGN_ROOM_NUM Room_No,c.ORDER_CATALOG_CODE Item_Code, 
            c.CATALOG_DESC Item_Desc,c.ORDER_QTY Order_Qty,c.ORD_DATE_TIME Order_Date_Time 
            from pr_encounter a, or_order b, or_order_line c,ph_disp_dtl d,OR_ORDER_STATUS_CODE e 
            where a.ENCOUNTER_ID = b.ENCOUNTER_ID 
            and b.ORDER_ID=c.ORDER_ID 
            and c.ORDER_ID=d.ORDER_ID 
            and c.ORDER_LINE_STATUS=e.ORDER_STATUS_CODE 
            and a.PAT_CURR_LOCN_CODE not in ('FL9C','FL9W') 
            and a.facility_id in ({facility_code})
            and a.patient_class = 'IP' 
            and b.order_category = 'PH'  
            and b.ORD_DATE_TIME between a.VISIT_ADM_DATE_TIME 
            and (a.VISIT_ADM_DATE_TIME+4/24) 
            and a.visit_adm_date_time between :from_date and to_date(:to_date) +1
            order by c.ORD_DATE_TIME desc 
        
         """

        self.cursor.execute(get_pharmacy_indent_report_qurey, [from_date, to_date])
        get_pharmacy_indent_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_pharmacy_indent_report_data, column_name

    def get_return_medication_without_return_request_report_value(
        self, from_date, to_date
    ):
        get_return_medication_without_return_request_report_value_qurey = """ 
        
        select a.RETURNED_DATE as Returned_DateTime,c.EXP_DISCHARGE_DATE_TIME as Expected_Discharge,c.DISCHARGE_DATE_TIME as Discharge_DateTime,
        b.PATIENT_ID as Patient_ID,f.PATIENT_NAME as Patient_Name,a.DISP_NO Disp_No,a.ITEM_CODE as Item_Code,d.LONG_DESC as Item_Description,g.DRUG_ITEM_YN as Drug,
        a.BATCH_ID as Batch,a.EXPIRY_DATE as Expiry,a.DISP_QTY as DispQty,a.RTN_QTY as RtnQty,e.APPL_USER_NAME as Returned_by,a.MODIFIED_AT_WS_NO as PC_Name
        from ph_retn_medn a,ph_disp_hdr b,pr_encounter c,mm_item d,sm_appl_user e, mp_patient f,st_item g
        where a.DISP_NO=b.DISP_NO and b.ENCOUNTER_ID=c.ENCOUNTER_ID(+) and a.ITEM_CODE=d.ITEM_CODE and b.PATIENT_ID=f.PATIENT_ID and d.ITEM_CODE=g.ITEM_CODE
        and a.DISP_NO not in (select disp_no from ph_ward_return_hdr) and a.MODIFIED_BY_ID=e.APPL_USER_ID and trunc(RETURNED_DATE) between
        :from_date and :to_date
        and b.PATIENT_ID like 'KH100%' order by 1  

"""

        self.cursor.execute(
            get_return_medication_without_return_request_report_value_qurey,
            [from_date, to_date],
        )
        get_return_medication_without_return_request_report_value_data = (
            self.cursor.fetchall()
        )

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return (
            get_return_medication_without_return_request_report_value_data,
            column_name,
        )

    def get_deleted_pharmacy_prescriptions_report(
        self, from_date, to_date, facility_code
    ):
        get_deleted_pharmacy_prescriptions_report_qurey = f""" 
        
         select a.order_id as PrescriptionNo, a.patient_id as UHIDNo, c.patient_name as PatientName,
        a.source_code as PatientLocation, a.ORD_DATE_TIME as PrescriptionDate, a.added_by_id as OrderedBy,
        b.order_catalog_code as DrugCodeNo, b.catalog_desc as DrugDescription,e.DRUG_ITEM_YN as DrugYesNo, b.order_qty as PrescribedQty,
        a.modified_at_ws_no as modifiedatstation,d.appl_user_name as FilledByName
        from or_order a , or_order_line b, mp_patient c , sm_appl_user d, st_item e
        where a.order_id in (select order_id from or_order_line_ph where complete_order_reason is not null)
        and a.ORDERING_FACILITY_ID in ({facility_code}) and a.order_id = b.order_id and a.patient_id = c.patient_id and e.ITEM_CODE=b.ORDER_CATALOG_CODE and b.order_catalog_code like '20%'
        and b.modified_by_id = d.appl_user_id and a.ORD_DATE_TIME between to_date(:from_date,'dd-mon-yyyy hh24:mi:ss') 
        and to_date(:to_date,'dd-mon-yyyy hh24:mi:ss') order by a.order_id desc

"""

        self.cursor.execute(
            get_deleted_pharmacy_prescriptions_report_qurey, [from_date, to_date]
        )
        get_deleted_pharmacy_prescriptions_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_deleted_pharmacy_prescriptions_report_data, column_name

    def get_pharmacy_direct_sales_report(
        self, from_date, to_date, store_code, module_id, facility_code
    ):
        get_pharmacy_direct_sales_report_qurey = f""" 
        
        select distinct a.FACILITY_ID,a.ADDED_DATE DOCDATETIME,a.DOC_NO DOCNUM,a.PATIENT_ID PATIENTID,e.PATIENT_NAME PATIENTNAME,b.SAL_ITEM_QTY  ITEMCODE,c.LONG_DESC ITEMNAME, b.BATCH_ID BATCH,b.EXPIRY_DATE_OR_RECEIPT_DATE EXPIRYDATE,
        b.SAL_ITEM_QTY SALEQTY, d.APPL_USER_NAME INITIATEDBY from st_sal_hdr a,st_sal_dtl_exp b,mm_item c,sm_appl_user d,mp_patient e where a.DOC_NO=b.DOC_NO and b.ITEM_CODE=c.ITEM_CODE
        and a.PATIENT_ID=e.PATIENT_ID and a.ADDED_BY_ID=d.APPL_USER_ID and a.STORE_CODE = :store_code and a.MODULE_ID = :module_id and a.FACILITY_ID in ({facility_code}) and a.DOC_DATE between :from_date and :to_date order by a.ADDED_DATE desc

"""

        self.cursor.execute(
            get_pharmacy_direct_sales_report_qurey,
            [store_code, module_id, from_date, to_date],
        )
        get_pharmacy_direct_sales_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_pharmacy_direct_sales_report_data, column_name

    def get_store_code_st_sal_hdr(self):
        get_store_code_st_sal_hdr_qurey = f""" 
        
        select distinct a.STORE_CODE ,b.LONG_DESC ,a.FACILITY_ID
        from st_sal_hdr a, mm_store b
        where a.STORE_CODE = b.STORE_CODE
        order by a.FACILITY_ID
"""

        self.cursor.execute(get_store_code_st_sal_hdr_qurey)
        get_store_code_st_sal_hdr_data = self.cursor.fetchall()

        get_module_id = f"select distinct a.MODULE_ID from st_sal_hdr a"
        self.cursor.execute(get_module_id)
        get_module_id_data = self.cursor.fetchall()

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_store_code_st_sal_hdr_data, get_module_id_data

    def get_intransites_unf_sal(self, from_date, to_date):

        intransites_unf_sal_qurey = """
        
        
            select
            a.facility_id,
            a.doc_no,
            a.doc_date,
            a.store_code,
            b.ITEM_CODE,
            b.ITEM_QTY
            from st_sal_hdr a,st_sal_dtl b
            where
            a.facility_id = 'KH' and
            a.module_id = 'ST' and
            a.STORE_CODE in (select store_code from mm_store where eff_Status = 'E') and
            a.DOC_NO=b.DOC_NO and
            a.finalized_yn = 'N' and
            a.doc_date between :from_date and :to_date
            order by a.doc_date,a.store_code


        
        """

        self.cursor.execute(intransites_unf_sal_qurey, [from_date, to_date])
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_intransites_confirm_pending(self):

        intransites_confirm_pending_qurey = """
        
        select distinct a.DOC_DATE "Date",a.DOC_NO "Doc No",a.TRN_TYPE "Trn",a.ISSUING_STORE "From",a.RECEIVING_STORE "To",b.ITEM_CODE "ICode",
c.LONG_DESC "Item Name",b.BATCH_ID "Batch",b.ISSUE_QTY "Trn Qty",b.RECEIVED_QTY "Rec Qty",b.REJECTED_QTY "Rej Qty",b.REMARKS "Remarks",
b.TMP_REJECTED_QTY_1,b.TMP_REJECTED_QTY_2
from st_acknowledge_trn_hdr a,st_acknowledge_trn_dtl b,mm_item c
where a.DOC_TYPE_CODE=b.DOC_TYPE_CODE and 
a.DOC_NO=b.DOC_NO and
b.ITEM_CODE=c.ITEM_CODE and
b.ISSUE_QTY!=b.RECEIVED_QTY and
a.CONFIRM_YN = 'N' and
a.ISSUING_STORE in (select store_code from mm_store where eff_Status = 'E') and
a.RECEIVING_STORE in (select store_code from mm_store where eff_Status = 'E') and
a.ACKNOWLEDGE_YN='Y' and
a.CONFIRM_YN = 'N'
order by a.DOC_NO


        
        """

        self.cursor.execute(
            intransites_confirm_pending_qurey,
        )
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_non_billable_consumption(
        self, from_date, to_date, store_code, facility_code
    ):

        non_billable_consumption_qurey = f"""
        
        
            select b.doc_no "DOC NO", b.added_date "DATE", b.item_code "ITEM CODE",b.Doc_type_code, c.long_desc "ITEM NAME", b.item_qty "CONS QTY", 
            b.ITEM_UNIT_COST "UNIT COST", ROUND((b.item_qty * b.ITEM_UNIT_COST),2) "TOTAL COST VALUE", ROUND(b.GROSS_CHARGE_AMT,2) "TOTAL CHARGE VALUE"
            from ST_SAL_DTL b, MM_ITEM c
            where b.doc_no in (select doc_no from ST_SAL_HDR where BILLABLE_TRN_YN ='N') 
            and b.item_code = c.item_code and b.doc_type_code in (:store_code) and b.Facility_ID in ({facility_code})
            and b.added_date between :from_date and to_date(:to_date) + 1



        
        """

        self.cursor.execute(
            non_billable_consumption_qurey, [store_code, from_date, to_date]
        )
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_store_code_ST_SAL_DTL(self):

        non_billable_consumption_qurey = f"""
        
        
            select distinct doc_type_code, FACILITY_ID  from ST_SAL_DTL  order by FACILITY_ID 

        
        """

        self.cursor.execute(non_billable_consumption_qurey)
        data = self.cursor.fetchall()
        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data

    def get_non_billable_consumption1(self, from_date, to_date):

        non_billable_consumption1_qurey = """
        
        
            select a.doc_no, a.doc_date, a.store_code, b.long_desc, a.patient_id, a.sal_trn_type, a.BILLABLE_TRN_YN, a.added_by_id, c.APPL_USER_NAME 
            from ST_SAL_HDR a, MM_store b, SM_APPL_USER c
            where a.BILLABLE_TRN_YN ='N'
            and a.store_code = b.store_code
            and a.added_by_id = c.APPL_USER_ID and a.facility_id = 'KH'
            and a.doc_date between :from_date and to_date(:to_date)+1




        
        """

        self.cursor.execute(non_billable_consumption1_qurey, [from_date, to_date])
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_pharmacy_charges_and_implant_pending_indent_report(
        self, from_date, to_date, facility_code
    ):
        get_pharmacy_charges_and_implant_pending_indent_report_qurey = f""" 
        
       select distinct b.PATIENT_ID PATIENTID,d.PATIENT_NAME PATIENTNAME,a.ORD_DATE_TIME ORDDATETIME,c.APPL_USER_NAME ORDEREDBY,a.ORDER_CATALOG_CODE ITEMCODE,a.CATALOG_DESC ITEMNAME,f.LONG_DESC STATUS,
       a.CAN_DATE_TIME CANCELLEDON,e.PRACTITIONER_NAME CANCELLEDBY,a.CAN_LINE_REASON CANCELREASON from or_order_line a,or_order b,sm_appl_user c,mp_patient d,am_practitioner e,OR_ORDER_STATUS_CODE f
       where a.order_id=b.ORDER_ID and e.PRACTITIONER_ID(+)=a.CAN_PRACT_ID and a.ADDED_BY_ID=c.APPL_USER_ID and d.PATIENT_ID=b.PATIENT_ID and a.ORDER_LINE_STATUS=f.ORDER_STATUS_CODE and a.order_catalog_code in
       (select distinct item_code from mm_item where eff_status = 'E' and long_desc like '%PHARMACY%CHARGES%' or long_desc like '%IMPLANT%PENDING%') and d.ADDED_FACILITY_ID in ({facility_code})
       and a.ord_date_time between :from_date and :to_date order by a.ord_date_time desc

"""

        self.cursor.execute(
            get_pharmacy_charges_and_implant_pending_indent_report_qurey,
            [from_date, to_date],
        )
        get_pharmacy_charges_and_implant_pending_indent_report_data = (
            self.cursor.fetchall()
        )

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_pharmacy_charges_and_implant_pending_indent_report_data, column_name

    def get_pharmacy_direct_returns_sale_report(self, from_date, to_date):
        get_pharmacy_direct_returns_sale_report_qurey = """ 
        
       select distinct a.ADDED_DATE DOCDATETIME,a.DOC_NO DOCNUM,a.PATIENT_ID PATIENTID, e.PATIENT_NAME PATIENTNAME,b.ITEM_CODE ITEMCODE,c.LONG_DESC ITEMNAME, b.BATCH_ID BATCH,b.EXPIRY_DATE_OR_RECEIPT_DATE EXPIRYDATE,
       b.ITEM_QTY SALEQTY, d.APPL_USER_NAME INITIATEDBY from st_sal_ret_hdr a,st_sal_ret_dtl_exp b, mm_item c,sm_appl_user d, mp_patient e where a.DOC_NO = b.DOC_NO and b.ITEM_CODE = c.ITEM_CODE and a.PATIENT_ID = e.PATIENT_ID and
       a.ADDED_BY_ID = d.APPL_USER_ID and a.STORE_CODE = 'CP00' and e.ADDED_FACILITY_ID = 'KH' and trunc(a.ADDED_DATE) between :from_date and :to_date

"""

        self.cursor.execute(
            get_pharmacy_direct_returns_sale_report_qurey, [from_date, to_date]
        )
        get_pharmacy_direct_returns_sale_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_pharmacy_direct_returns_sale_report_data, column_name

    def get_consigned_item_detail_report(self, from_date, to_date, store_code):
        consigned_item_detail_report_qurey = f""" 

        SELECT ST_SAL_HDR.PATIENT_ID,ST_SAL_HDR.STORE_CODE,ST_SAL_DTL.ADDED_DATE, 
        ST_SAL_DTL.DOC_NO,ST_SAL_DTL.ITEM_CODE,MM_ITEM.LONG_DESC ,ST_SAL_DTL.ITEM_QTY 
        FROM IBAEHIS.ST_SAL_DTL ST_SAL_DTL, IBAEHIS.ST_SAL_HDR ST_SAL_HDR,IBAEHIS.MM_ITEM MM_ITEM,st_item c 
        WHERE (ST_SAL_DTL.ITEM_CODE = MM_ITEM.ITEM_CODE 
        AND ST_SAL_DTL.ITEM_CODE = C.item_code )  
        AND (ST_SAL_DTL.DOC_NO = ST_SAL_HDR.DOC_NO ) 
        AND ST_SAL_DTL.ADDED_DATE between to_date(:from_date  ,'dd/mm/yyyy hh24:mi:ss') and to_date(:to_date  ,'dd/mm/yyyy hh24:mi:ss')+1
        AND (ST_SAL_DTL.DOC_TYPE_CODE in (:store_code)) 
        --AND (ST_SAL_HDR.STORE_CODE like'%RH%OT%') 
        AND (c.consignment_item_yn = 'Y') 
        AND ((ST_SAL_DTL.ITEM_CODE LIKE 'C%') 
        or (ST_SAL_DTL.ITEM_CODE LIKE '2%'))
        order by ST_SAL_HDR.STORE_CODE



"""

        self.cursor.execute(
            consigned_item_detail_report_qurey, [from_date, to_date, store_code]
        )
        get_consigned_item_detail_report_data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_consigned_item_detail_report_data, column_name

    def get_schedule_h1_drug_report(self, facility_code, from_date, to_date):
        schedule_h1_drug_report_query = f""" 
        
        select distinct 
        c.ITEM_CODE Item_Code, e.PATIENT_CLASS , 
        a.FACILITY_ID FACILITY,a.STORE_CODE Store,a.DOC_DATE Doc_Date, 
        f.APC_NO,nvl(f.PRACTITIONER_NAME,a.PRACTITIONER_NAME) as PRACTITIONER_NAME,
        a.PATIENT_ID UHID,d.PATIENT_NAME PT_NAME,g.ADDR1_LINE1||','||g.ADDR1_LINE2||','||g.ADDR1_LINE3||','||g.ADDR1_LINE4||','||g.RES_TOWN1_CODE||','||g.POSTAL1_CODE ADDRESS,
        h.LONG_DESC ITEM_NAME,c.BATCH_ID Batch,c.EXPIRY_DATE_OR_RECEIPT_DATE Expiry,c.SAL_ITEM_QTY Sal_Qty,c.RET_ITEM_QTY Rtn_Qty,
        a.DOC_NO Doc_Num
        from st_sal_hdr a,st_sal_dtl b,st_sal_dtl_exp c,mp_patient d,pr_encounter e,am_practitioner f,MP_PAT_ADDRESSES g, mm_item h  
        where 
        a.DOC_NO=b.DOC_NO and a.PATIENT_ID=d.PATIENT_ID and a.PATIENT_ID=g.PATIENT_ID 
        and b.ITEM_CODE=h.ITEM_CODE and a.ENCOUNTER_ID=e.ENCOUNTER_ID(+)   
        and e.ATTEND_PRACTITIONER_ID=f.PRACTITIONER_ID(+) and b.DOC_NO=c.DOC_NO 
        and b.ITEM_CODE=c.ITEM_CODE and a.FACILITY_ID in ({facility_code})  
        and a.DOC_DATE between to_date(:from_date,'dd/mm/yyyy hh24:mi:ss') and to_date(:to_date,'dd/mm/yyyy hh24:mi:ss')
        and h.long_desc like '%H1%'


"""
        self.cursor.execute(schedule_h1_drug_report_query, [from_date, to_date])
        schedule_h1_drug_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return schedule_h1_drug_report_data, column_name

    def get_pharmacy_ward_return_requests_with_status_report(
        self, facility_code, from_date, to_date
    ):
        pharmacy_ward_return_requests_with_status_report_query = f""" 
        
        select a.PATIENT_ID ,d.PATIENT_NAME ,a.ENCOUNTER_ID ,a.DISP_DATE_TIME Dispensed_Dt_Tym,a.DISP_LOCN_CODE Disp_From,a.FROM_LOCN_CODE Returned_from,
        a.RET_TO_DISP_LOCN_CODE Returned_to,a.DISP_NO ,b.ITEM_CODE ,c.LONG_DESC Item_Name,b.STORE_ACKNOWLEDGE_STATUS Status,a.ADDED_DATE Return_On,b.RETURNED_QTY Returned,b.BAL_QTY Balance,
        b.REJ_QTY Rejected 
        from ph_ward_return_hdr a,ph_ward_return_dtl b,mm_item c,mp_patient d
        where a.DISP_NO=b.DISP_NO and a.RET_DOC_NO=b.RET_DOC_NO and a.ORDER_ID=b.ORDER_ID and a.PATIENT_ID=d.PATIENT_ID and b.ITEM_CODE=c.ITEM_CODE
        and a.FACILITY_ID in ({facility_code}) and trunc(a.ADDED_DATE) between to_date(:from_date,'dd/mm/yyyy hh24:mi:ss') and to_date(:to_date,'dd/mm/yyyy hh24:mi:ss')+1

"""
        self.cursor.execute(
            pharmacy_ward_return_requests_with_status_report_query,
            [from_date, to_date],
        )
        pharmacy_ward_return_requests_with_status_report = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return pharmacy_ward_return_requests_with_status_report, column_name

    def get_pharmacy_indent_deliver_summary_report(
        self, from_date, to_date, facility_code
    ):
        facility_code = facility_code[1] + facility_code[2] + "%"
        facility_code = f"'{facility_code}'"

        stock_qurey = f""" 
        
        select DISTINCT PATIENT_ID AS PatID,count(disp_no) AS IndentsCount,ORD_DATE_TIME  AS OrderDtTym,
        DISPENSED_DATE_TIME AS DispensedDtTym,LOCN_CODE AS IndentLocation,BED_NO  AS BedNo
        from ph_disp_hdr 
        where DISPENSED_DATE_TIME between to_date(:from_date,'dd-mon-yyyy hh24:mi:ss') and to_date(:to_date,'dd-mon-yyyy hh24:mi:ss')
        AND PATIENT_ID LIKE {facility_code}
        group by PATIENT_ID,DISPENSED_DATE_TIME,LOCN_CODE,BED_NO, ORD_DATE_TIME
        ORDER BY DISPENSED_DATE_TIME DESC
         """

        self.cursor.execute(stock_qurey, [from_date, to_date])
        data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_intransites_stk_tfr_acknowledgement_pending(self, facility_code):

        intransites_stk_tfr_acknowledgement_pending_qurey = f""" 
        select
        a.DOC_DATE "Date",a.DOC_NO "Doc No",a.DOC_TYPE_CODE "Trn",
        a.FM_STORE_CODE "From",a.TO_STORE_CODE "To",
        a.FINALIZED_YN "Finalize ?",a.PROCESS_FOR_ACKNOWLEDGE "Sent to Ack ?",
        b.ITEM_CODE "Item Code",d.LONG_DESC "Item Name",c.BATCH_ID "Batch",
        c.EXPIRY_DATE_OR_RECEIPT_DATE "Expiry",c.ITEM_QTY "Iss Qty"
        from st_transfer_hdr a,st_transfer_dtl b,st_transfer_dtl_exp c, mm_item d
        where 
        a.FACILITY_ID in ({facility_code}) and
        a.DOC_NO=b.DOC_NO and
        b.DOC_NO=c.DOC_NO and
        b.ITEM_CODE=c.ITEM_CODE and
        b.ITEM_CODE=d.ITEM_CODE and
        a.FINALIZED_YN = 'N' and
        a.PROCESS_FOR_ACKNOWLEDGE = 'Y' and
        a.FM_STORE_CODE in (select store_code from mm_store where eff_Status = 'E') and
        a.TO_STORE_CODE in (select store_code from mm_store where eff_Status = 'E') and
        a.DOC_NO not in (select distinct doc_no from st_acknowledge_trn_hdr where doc_type_code = 'ISS')
        order by a.DOC_DATE 
        """

        self.cursor.execute(intransites_stk_tfr_acknowledgement_pending_qurey)
        data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_folley_and_central_line(self, from_date, to_date):

        folley_and_central_line_qurey = """
        
        
            SELECT d.long_desc,a.ADDED_DATE,a.ADDED_FACILITY_ID,a.DOC_NO,a.DOC_SRL_NO,a.DOC_TYPE_CODE, 
            a.ITEM_CODE,c.long_desc,(a.SAL_ITEM_QTY-a.RET_ITEM_QTY) "SAL_ITEM_QTY",b.encounter_id,b.patient_id,a.ADDED_AT_WS_NO,a.ADDED_BY_ID
            FROM ST_SAL_DTL_EXP  a ,ST_SAL_HDR b , mm_item c,MM_STORE d
            where (a.doc_no = b.doc_no) and (a.item_code = c.item_code) and (a.store_code = d.store_code) and (a.SAL_ITEM_QTY-a.RET_ITEM_QTY) > 0 
            and  a.added_facility_id = 'KH' AND b.ADDED_FACILITY_ID = 'KH' and  
            (a.item_code = '2000059573' or a.item_code = '2000057627' or a.item_code = '2000058146' or a.item_code = '2000061806' or a.item_code = '2000029889')  and 
            a.ADDED_DATE between :from_date and to_date(:to_date) + 1
            order by a.added_date

    """

        self.cursor.execute(folley_and_central_line_qurey, [from_date, to_date])
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_angiography_kit(self, from_date, to_date):

        angiography_kit_qurey = """
        
        
            SELECT ST_SAL_DTL.ADDED_DATE, 
            ST_SAL_DTL.ITEM_QTY, 
            ST_SAL_DTL.ADDED_BY_ID, 
            ST_SAL_DTL.ITEM_CODE,
            ST_SAL_DTL.DOC_NO,
            ST_SAL_DTL.GROSS_CHARGE_AMT,
            ST_SAL_DTL.ITEM_COST_VALUE,
            ST_SAL_DTL.ITEM_QTY,
            ST_SAL_DTL.ITEM_SAL_VALUE,
            ST_SAL_DTL.ITEM_UNIT_COST,
            ST_SAL_DTL.ITEM_UNIT_PRICE,
            ST_SAL_DTL.PAT_GROSS_CHARGE_AMT,
            ST_SAL_DTL.PAT_NET_AMT,
            ST_SAL_HDR.STORE_CODE,
            ST_SAL_HDR.ENCOUNTER_ID,
            ST_SAL_HDR.PATIENT_ID,
            MM_ITEM.LONG_DESC 
            FROM IBAEHIS.ST_SAL_DTL ST_SAL_DTL, IBAEHIS.ST_SAL_HDR ST_SAL_HDR,IBAEHIS.MM_ITEM MM_ITEM
            WHERE (ST_SAL_DTL.ITEM_CODE = MM_ITEM.ITEM_CODE )  AND (ST_SAL_DTL.DOC_NO = ST_SAL_HDR.DOC_NO )  
            AND ST_SAL_DTL.ADDED_DATE between :from_date and to_date(:to_date)+1
            AND (ST_SAL_DTL.DOC_TYPE_CODE = 'SAL') AND (ST_SAL_HDR.STORE_CODE = 'COT' OR ST_SAL_HDR.STORE_CODE ='OTS' OR ST_SAL_HDR.STORE_CODE ='OTS5') 
            AND (ST_SAL_DTL.ITEM_CODE = '2000018108')

    """

        self.cursor.execute(angiography_kit_qurey, [from_date, to_date])
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_search_indents_by_code(self, from_date, location_code):

        search_indents_by_code_qurey = """
        
        
            select DISTINCT PATIENT_ID "Pat ID",count(disp_no) "Indents Count",ORD_DATE_TIME "Order Dt Tym", 
            DISPENSED_DATE_TIME "Dispensed Dt Tym",LOCN_CODE "Indent Location", DISP_LOCN_CODE "DISP_LOCN_CODE",BED_NO "Bed No"
            from ph_disp_hdr where DISPENSED_DATE_TIME >= :from_date AND PATIENT_ID LIKE 'KH%'
            and DISP_LOCN_CODE = :location_code
            group by PATIENT_ID,DISPENSED_DATE_TIME,LOCN_CODE,DISP_LOCN_CODE,BED_NO, ORD_DATE_TIME
            ORDER BY DISPENSED_DATE_TIME DESC

    """

        self.cursor.execute(search_indents_by_code_qurey, [from_date, location_code])
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_midnight_stock_report(self, midnight_stock_table):

        midnight_stock_report_qurey = f"""
        
        SELECT b.FACILITY_ID,a.*
        FROM {midnight_stock_table } a
        left join mm_store b on (a.STORE = b.STORE_CODE)
        """

        self.cursor.execute(midnight_stock_report_qurey)
        data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_overall_pharmacy_consumption_report(self, from_date, to_date):

        overall_pharmacy_consumption_report_qurey = """
        
        

            select TRX_NO           , 
            TRX_DATE              , 
            TRN_TYPE              ,
            FACILITY_ID           ,
            DOC_TYPE_CODE         , 
            DOC_NO                , 
            SEQ_NO                , 
            DOC_DATE              , 
            DOC_SRL_NO            , 
            STORE_CODE            , 
            X.ITEM_CODE             ,
            LONG_DESC ,
            BATCH_ID              ,
            EXPIRY_DATE           ,
            BIN_LOCATION_CODE      ,
            STK_UOM_CODE          , 
            TRADE_ID              ,
            ITEM_QTY              ,
            x.ITEM_UNIT_COST,
            DEPT_COST_CENTER_CODE  ,
            CONSIGNMENT_ITEM_YN    ,
            SUPP_CODE              ,
            DEPT_CONS_YN           ,
            SALE_TRN_TYPE         ,
            X.ADDED_BY_ID            ,
            X.ADDED_DATE            ,
            X.ADDED_AT_WS_NO         ,
            X.ADDED_FACILITY_ID     ,
            X.MODIFIED_BY_ID         ,
            X.MODIFIED_DATE          ,
            X.MODIFIED_AT_WS_NO     ,
            X.MODIFIED_FACILITY_ID ,
            APPLICATION_ID      ,
            URL_TEXT           ,
            EVENT_TYPE        ,
            ERR_MSG          ,
            CONS_YN          ,
            LOAD_STATUS      ,
            TRN_SIGN         ,
            XI_STORE_CODE     from xi_trn_cons x, mm_item m
            where X.ITEM_CODE=M.ITEM_CODE(+)
            and x.TRX_DATE between :from_date and to_date(:to_date) +1



            

    """

        self.cursor.execute(
            overall_pharmacy_consumption_report_qurey, [from_date, to_date]
        )
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_new_admission_dispense_report(self, from_date, to_date, facility_code):

        get_new_admission_dispense_qurey = f""" 
            select a.visit_adm_date_time, c.PATIENT_ID as PatientID,c.LOCN_CODE as PtLocation,c.ORD_DATE_TIME as OrderDateTime , 
            a.ASSIGN_BED_NUM as BedNo,c.DISPENSED_DATE_TIME as DispensedDateTime,count(d.DISP_QTY) as Dispensedcount 
            from pr_encounter a, or_order b, ph_disp_hdr c,ph_disp_dtl d 
            where c.DISP_NO = d.DISP_NO 
            and b.ORDER_ID = c.ORDER_ID 
            and a.PATIENT_ID = b.PATIENT_ID 
            and a.ENCOUNTER_ID = b.ENCOUNTER_ID 
            and c.LOCN_CODE not in ('FL9C', 'FL9W') 
            and a.facility_id in ({facility_code})
            and a.patient_class = 'IP' 
            and b.order_category = 'PH' 
            and b.ORD_DATE_TIME between a.VISIT_ADM_DATE_TIME and(a.VISIT_ADM_DATE_TIME+4 / 24) 
            and a.visit_adm_date_time between :from_date and to_date(:to_date) +1
            group by a.visit_adm_date_time,c.PATIENT_ID,c.LOCN_CODE,c.ORD_DATE_TIME,c.DISPENSED_DATE_TIME,a.ASSIGN_BED_NUM 
            order by c.DISPENSED_DATE_TIME desc

            """

        self.cursor.execute(get_new_admission_dispense_qurey, [from_date, to_date])
        get_new_admission_dispense_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_new_admission_dispense_data, column_name

    def get_pharmacy_op_sale_report_userwise(
        self, from_date, to_date, store_code, cash_counter, facility_code
    ):
        pharmacy_op_sale_report_userwise_qurey = f""" 
        
        select a.PATIENT_ID , a.doc_type_code,a.added_by_id,a.bill_amt, a.doc_num, a.cash_counter_code,a.doc_date
        from BL_BILL_HDR a
        where a.doc_type_code in (:store_code)
        and a.OPERATING_FACILITY_ID in ({facility_code})
        and a.cash_counter_code like ('%{cash_counter}%')
        --and a.cash_counter_code in ('PH1','PH2','PH3','PH4','PH5','PH6','PH7','PH8','PH9')
        and trunc(a.ADDED_DATE) between :from_date and :to_date


"""

        self.cursor.execute(
            pharmacy_op_sale_report_userwise_qurey, [store_code, from_date, to_date]
        )
        pharmacy_op_sale_report_userwise_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return pharmacy_op_sale_report_userwise_data, column_name

    def get_doc_type_code_BL_BILL_HDR(self):
        doc_type_code_BL_BILL_HDR_qurey = f""" 
        
         select distinct doc_type_code,OPERATING_FACILITY_ID from BL_BILL_HDR order by OPERATING_FACILITY_ID


"""

        self.cursor.execute(doc_type_code_BL_BILL_HDR_qurey)
        doc_type_code_BL_BILL_HDR_data = self.cursor.fetchall()

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return doc_type_code_BL_BILL_HDR_data

    def get_pharmacy_consumption_report(self, from_date, to_date, facility_code):

        get_pharmacy_consumption_re_qurey = f""" 
            
            SELECT ST_SAL_DTL.ADDED_DATE, ST_SAL_DTL.ITEM_QTY, ST_SAL_DTL.ADDED_BY_ID, ST_SAL_DTL.ITEM_CODE ,  
            ST_SAL_DTL.DOC_NO,ST_SAL_DTL.GROSS_CHARGE_AMT,ST_SAL_DTL.ITEM_COST_VALUE,ST_SAL_DTL.ITEM_QTY,ST_SAL_DTL.ITEM_SAL_VALUE ,  
            ST_SAL_DTL.ITEM_UNIT_COST,ST_SAL_DTL.ITEM_UNIT_PRICE,ST_SAL_DTL.PAT_GROSS_CHARGE_AMT,ST_SAL_DTL.PAT_NET_AMT,ST_SAL_HDR.STORE_CODE,ST_SAL_HDR.ENCOUNTER_ID,ST_SAL_HDR.PATIENT_ID,MM_ITEM.LONG_DESC  
            FROM IBAEHIS.ST_SAL_DTL ST_SAL_DTL, IBAEHIS.ST_SAL_HDR ST_SAL_HDR, IBAEHIS.MM_ITEM MM_ITEM  
            WHERE(ST_SAL_DTL.ITEM_CODE = MM_ITEM.ITEM_CODE)  AND(ST_SAL_DTL.DOC_NO = ST_SAL_HDR.DOC_NO) 
            
"""
        if facility_code == "'KH'":
            get_pharmacy_consumption_re_qurey += "AND(ST_SAL_DTL.DOC_TYPE_CODE = 'SAL') AND(ST_SAL_HDR.STORE_CODE = 'OP00') AND(ST_SAL_DTL.ITEM_CODE LIKE '2%') "

        if facility_code == "'RH'":
            get_pharmacy_consumption_re_qurey += f""" 
            
            AND(ST_SAL_DTL.DOC_TYPE_CODE = 'RHSAL') 
            AND(ST_SAL_HDR.STORE_CODE Like 'RH%' or ST_SAL_HDR.STORE_CODE='OP01')  
            --AND(ST_SAL_DTL.ITEM_CODE LIKE '2%') 

"""
        if facility_code == "'IN'":
            get_pharmacy_consumption_re_qurey += "AND(ST_SAL_DTL.DOC_TYPE_CODE = 'INSAL')  AND(ST_SAL_HDR.STORE_CODE Like '%IN%') "

        get_pharmacy_consumption_re_qurey += (
            f"and ST_SAL_DTL.ADDED_DATE between :from_date and to_date(:to_date) + 1"
        )

        self.cursor.execute(get_pharmacy_consumption_re_qurey, [from_date, to_date])
        get_pharmacy_consumption_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_pharmacy_consumption_report_data, column_name

    def get_food_drug_interaction_report(self, facility_code, from_date, to_date):
        food_drug_interaction_report_qurey = f""" 
        
       select l.ORD_DATE_TIME "Date",e.PATIENT_ID "UHID",e.EPISODE_ID,m.PATIENT_NAME,round(((sysdate-(m.DATE_OF_BIRTH))/365),0) "Age",m.sex,e.ASSIGN_BED_NUM,e.ASSIGN_CARE_LOCN_CODE,
d.DRUG_DESC,n.GENERIC_NAME,d.DRUG_INDICATION "Food-Drug Interation",o.SOURCE_CODE "Ordering location",o.ORD_PRACT_ID,o.ADDED_BY_ID,l.ORDER_QTY,e.VISIT_ADM_DATE_TIME,
e.DISCHARGE_DATE_TIME,e.ADMIT_PRACTITIONER_ID,a.PRACTITIONER_NAME,a.PRIMARY_SPECIALITY_CODE,r.ADDED_BY_ID returned_by,r.ADDED_DATE returned_date,r.RETURNED_QTY,h.RET_TO_DISP_LOCN_CODE
from mp_patient m, or_order o, or_order_line l,or_order_line_ph p,ph_drug d,pr_encounter e,ph_generic_name n,
am_practitioner a,ph_ward_return_dtl r, ph_ward_return_hdr h where 
e.PATIENT_ID = m.PATIENT_ID and o.EPISODE_ID = e.EPISODE_ID and 
o.PATIENT_ID = e.PATIENT_ID and o.ORDER_ID = l.ORDER_ID and o.ORDER_ID = p.ORDER_ID 
and p.GENERIC_ID = n.GENERIC_ID and   l.ORDER_CATALOG_CODE = d.DRUG_CODE and
o.ORDER_ID = h.ORDER_ID(+) and 
e.ADMIT_PRACTITIONER_ID = a.PRACTITIONER_ID and 
o.ORDER_ID = r.ORDER_ID(+) and l.ORD_DATE_TIME between :from_date and :to_date and d.DRUG_INDICATION is not null
and e.FACILITY_ID in ({facility_code})
      
"""

        self.cursor.execute(food_drug_interaction_report_qurey, [from_date, to_date])
        food_drug_interaction_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return food_drug_interaction_report_data, column_name

    def get_intransite_stock(self, store_code):

        get_intransite_stock_qurey = """
        
        
            select distinct
            a.STORE_CODE,
            a.ITEM_CODE,
            b.LONG_DESC,
            a.BATCH_ID,
            a.BIN_LOCATION_CODE,
            c.LONG_DESC,
            c.SHORT_DESC,
            a.QTY_ON_HAND,
            a.COMMITTED_QTY
            from st_item_batch a,mm_item b,mm_bin_location c
            where
            a.ITEM_CODE=b.ITEM_CODE and
            a.BIN_LOCATION_CODE=c.BIN_LOCATION_CODE 
            and c.STORE_CODE in (:store_code)
            and a.STORE_CODE in (:store_code)
            order by a.ITEM_CODE

        """

        self.cursor.execute(get_intransite_stock_qurey, [store_code])
        get_intransite_stock_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_intransite_stock_data, column_name

    def get_store_code_st_item_batch(self):

        get_store_code_st_item_batch_qurey = """
        
        select distinct a.STORE_CODE, b.LONG_DESC,b.FACILITY_ID from st_item_batch a, mm_store b
        where a.STORE_CODE = b.STORE_CODE
        order by b.FACILITY_ID

            
        """

        self.cursor.execute(get_store_code_st_item_batch_qurey)
        get_store_code_st_item_batch_data = self.cursor.fetchall()

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_store_code_st_item_batch_data

    def get_grn_data(self, from_date, to_date, facility_code, store_code):

        get_grn_data_query = f"""

        select distinct a.FACILITY_ID,b.DOC_DATE "GRN Date",b.DOC_NO "HIS Doc No",b.STORE_CODE "Store",b.EXT_DOC_NO "SAP GRN No",b.SUPP_CODE "Vendor Code",d.LONG_NAME "Vendor Name",
        a.ITEM_CODE "Item Code",e.LONG_DESC "Item Description",a.ITEM_QTY_NORMAL "GRN Qty",a.RTV_ITEM_QTY_NORMAL "RTV Qty",(a.ITEM_QTY_NORMAL-a.RTV_ITEM_QTY_NORMAL) "Net GRN Qty",
        c.BATCH_ID "Batch No",c.EXPIRY_DATE_OR_RECEIPT_DATE "Expiry Date",a.GRN_UNIT_COST_IN_PUR_UOM "Unit Rate",a.GRN_UNIT_COST_IN_PUR_UOM*(a.ITEM_QTY_NORMAL-a.RTV_ITEM_QTY_NORMAL) "GRN Value"
        from st_grn_dtl a,st_grn_hdr b,st_grn_dtl_exp c,ap_supplier d,mm_item e
        where a.DOC_NO=b.DOC_NO and a.DOC_TYPE_CODE = b.DOC_TYPE_CODE and a.ITEM_CODE = c.ITEM_CODE and 
        a.ITEM_CODE=c.ITEM_CODE and a.DOC_TYPE_CODE = c.DOC_TYPE_CODE and 
        a.DOC_NO=c.DOC_NO and a.ITEM_CODE=e.ITEM_CODE and 
        d.SUPP_CODE=b.SUPP_CODE and
        a.ITEM_CODE like '2000%' and
        b.DOC_DATE between :from_date and :to_date
        --and a.FACILITY_ID in ('AK','KH','DF','GO','RH','SL','IN')
        and a.FACILITY_ID in ({facility_code})
        and b.STORE_CODE in ({store_code})
        and b.EXT_DOC_NO is not null
        order by b.DOC_DATE 



"""
        self.cursor.execute(get_grn_data_query, [from_date, to_date])
        get_grn_data_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_grn_data_data, column_name

    def get_st_grn_hdr_store_code(self):

        get_st_grn_hdr_store_code = """

        select distinct a.STORE_CODE,a.FACILITY_ID, b.LONG_DESC 
        from st_grn_hdr a, mm_store b
        where a.STORE_CODE = b.STORE_CODE
        order by a.FACILITY_ID

        """
        self.cursor.execute(get_st_grn_hdr_store_code)
        get_st_grn_hdr_store_code = self.cursor.fetchall()

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_st_grn_hdr_store_code

    def get_drug_duplication_override_report(self, from_date, to_date):
        get_drug_duplication_override_report_query = """
        
        select c.patient_id  as PatID,d.patient_name as PatName,b.DUPLICATE_DRUG_OVERRIDE_REASON as DuplicateReason,a.order_catalog_code as IC,
        a.catalog_desc as ItemName,f.generic_name as Generic,a.ord_date_time as OrdDtTym,a.order_qty as Qty
        from or_order_line a,or_order_line_ph b, or_order c, mp_patient d, ph_drug e, ph_generic_name f
        where a.order_id = b.order_id and c.order_id = b.order_id and c.patient_id = d.patient_id
        and b.DUPLICATE_DRUG_OVERRIDE_REASON is not null
        and a.order_catalog_code = e.item_code and e.generic_id = f.generic_id
        and b.modified_date between  :from_date and to_date(:to_date)+1
        and a.added_by_id like 'KH%' order by c.patient_id,f.generic_name 

"""
        self.cursor.execute(
            get_drug_duplication_override_report_query, [from_date, to_date]
        )
        get_drug_duplication_override_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_drug_duplication_override_report_data, column_name

    def get_drug_interaction_override_report(self, from_date, to_date):
        get_drug_interaction_override_report_query = """
        
        select c.patient_id as PatID,d.patient_name  as PatName,b.INTERACTION_OVERRIDE_REASON  as InteractionOverrideReason,
        a.order_catalog_code as IC,a.catalog_desc  AS ItemName,f.generic_name  as Generic,a.ord_date_time  as OrdDtTym,a.order_qty as Qty
        from or_order_line a,or_order_line_ph b, or_order c, mp_patient d, ph_drug e, ph_generic_name f
        where a.order_id = b.order_id and c.order_id = b.order_id and c.patient_id = d.patient_id
        and b.INTERACTION_OVERRIDE_REASON is not null
        and a.order_catalog_code = e.item_code and e.generic_id = f.generic_id
        and b.modified_date between  :from_date and to_date(:to_date)+1
        and a.added_by_id like 'KH%'
        order by c.patient_id,f.generic_name 

"""
        self.cursor.execute(
            get_drug_interaction_override_report_query, [from_date, to_date]
        )
        get_drug_interaction_override_report_data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_drug_interaction_override_report_data, column_name

    def get_sale_consumption_report(self, from_date, to_date):
        get_sale_consumption_report_query = """
        
        SELECT a.STORE_CODE, a.ITEM_CODE, b.LONG_DESC, (-SAL_QTY+-CONS_QTY+-SRT_QTY), (-SAL_VALUE+-CONS_COST+-SRT_VALUE),a.facility_id 
        FROM IBAEHIS.ST_ITEM_MOVE_SUMM a, IBAEHIS.MM_ITEM b,ST_Item c
        WHERE  a.facility_id = 'KH' and (a.ITEM_CODE=b.item_code) and  (a.ITEM_CODE=c.item_code) and (c.consignment_item_yn = 'N')
        and a.ADDED_DATE between :from_date and to_date(:to_date)+1 and (-SAL_VALUE+-CONS_COST+-SRT_VALUE>0)
        ORDER BY a.STORE_CODE


"""
        self.cursor.execute(get_sale_consumption_report_query, [from_date, to_date])
        get_sale_consumption_report_data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_sale_consumption_report_data, column_name

    def get_sale_consumption_report1(self, month, year):
        get_sale_consumption_report1_query = """
        
        SELECT a.STORE_CODE, a.ITEM_CODE, b.LONG_DESC, (-SAL_QTY+-CONS_QTY+-SRT_QTY), (-SAL_VALUE+-CONS_COST+-SRT_VALUE), a.facility_Id, c.consignment_item_yn,a.MOVE_MONTH,a.MOVE_YEAR 
        FROM IBAEHIS.ST_ITEM_MOVE_SUMM a, IBAEHIS.MM_ITEM b,ST_Item c 
        WHERE (a.MOVE_MONTH=:month) AND (a.MOVE_YEAR=:year) AND (a.ITEM_CODE=b.item_code) AND (a.ITEM_CODE=c.item_code) AND ((-SAL_QTY+-CONS_QTY+-SRT_QTY)>0) and (c.consignment_item_yn = 'N')
        ORDER BY a.STORE_CODE



"""
        self.cursor.execute(get_sale_consumption_report1_query, [month, year])
        get_sale_consumption_report1_data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_sale_consumption_report1_data, column_name

    def get_new_code_creation(self, from_date, to_date):
        new_code_creation_query = """ 
        
select item_code "Item Code",long_desc "Item Description",added_date "Added on" from mm_item 
where added_date between :from_date and to_date(:to_date)+1
order by added_Date desc


 """

        self.cursor.execute(new_code_creation_query, [from_date, to_date])
        new_code_creation_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return new_code_creation_data, column_name

    def get_tvd_cabg_request(self, from_date, to_date):
        tvd_cabg_request_query = """ 
        
        SELECT ST_SAL_DTL.ADDED_DATE, 
        ST_SAL_DTL.ITEM_QTY, 
        ST_SAL_DTL.ADDED_BY_ID, 
        ST_SAL_DTL.ITEM_CODE,
        ST_SAL_DTL.DOC_NO,
        ST_SAL_DTL.GROSS_CHARGE_AMT,
        ST_SAL_DTL.ITEM_COST_VALUE,
        ST_SAL_DTL.ITEM_QTY,
        ST_SAL_DTL.ITEM_SAL_VALUE,
        ST_SAL_DTL.ITEM_UNIT_COST,
        ST_SAL_DTL.ITEM_UNIT_PRICE,
        ST_SAL_DTL.PAT_GROSS_CHARGE_AMT,
        ST_SAL_DTL.PAT_NET_AMT,
        ST_SAL_HDR.STORE_CODE,
        ST_SAL_HDR.ENCOUNTER_ID,
        ST_SAL_HDR.PATIENT_ID,
        MM_ITEM.LONG_DESC 
        FROM IBAEHIS.ST_SAL_DTL ST_SAL_DTL, IBAEHIS.ST_SAL_HDR ST_SAL_HDR,IBAEHIS.MM_ITEM MM_ITEM
        WHERE (ST_SAL_DTL.ITEM_CODE = MM_ITEM.ITEM_CODE )  AND (ST_SAL_DTL.DOC_NO = ST_SAL_HDR.DOC_NO )  
        AND ST_SAL_DTL.ADDED_DATE between :from_date and to_date(:to_date)+1
        AND (ST_SAL_DTL.DOC_TYPE_CODE = 'SAL') AND (ST_SAL_HDR.STORE_CODE = 'COT' OR ST_SAL_HDR.STORE_CODE ='OTS' OR ST_SAL_HDR.STORE_CODE ='OTS5') 
        AND (ST_SAL_DTL.ITEM_CODE LIKE '2000018108%')


 """

        self.cursor.execute(tvd_cabg_request_query, [from_date, to_date])
        tvd_cabg_request_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return tvd_cabg_request_data, column_name

    def get_stock_amount_wise(self, from_amount, to_amount, store_code):
        if store_code == "ALL":
            stock_amount_wise_qurey = f"""
        
            SELECT a.ITEM_CODE "Item Code", a.ITEM_DESC "Description",
            a.STORE_CODE "Store Code",SUM(a.QTY_ON_HAND)"Qty On Hand",
            sum(a.AVAIL_QTY) "Avail.Stock",sum(a.QTY_ON_HAND-a.AVAIL_QTY) "In Transit Stock",
            d.last_receipt_date "Last Inward",
            case 
            when (d.material_group_code = 'KDHMD3') then ('Pharma')
            when (d.material_group_code<> 'KDHMD3') then ('surgical')
            else null
            end as "Material Category"
            FROM IBAEHIS.ST_BATCH_SEARCH_LANG_VIEW a
            left join ST_BATCH_CONTROL b on ( a.ITEM_CODE=b.ITEM_CODE and a.BATCH_ID=b.BATCH_ID  and a.EXPIRY_DATE=b.EXPIRY_DATE_OR_RECEIPT_DATE)
            left join st_item c on (a.ITEM_CODE = c.ITEM_CODE )
            left join mm_item d on (a.item_code = d.item_code)
            WHERE ( b.SALE_PRICE >=:from_amount and b.SALE_PRICE <=:to_amount) AND  (a.ITEM_CODE LIKE '2000%') AND (c.CONSIGNMENT_ITEM_YN = 'N') 
            GROUP BY a.ITEM_CODE, a.ITEM_DESC,a.STORE_CODE,d.last_receipt_date,d.material_group_code
            ORDER BY d.material_group_code,a.ITEM_DESC   ASC

            
            """

            self.cursor.execute(stock_amount_wise_qurey, [from_amount, to_amount])

        else:
            stock_amount_wise_qurey = f"""
        
            SELECT a.ITEM_CODE "Item Code", a.ITEM_DESC "Description",a.STORE_CODE "Store Code",
            SUM(a.QTY_ON_HAND)"Qty On Hand",sum(a.AVAIL_QTY) "Avail.Stock",
            sum(a.QTY_ON_HAND-a.AVAIL_QTY) "In Transit Stock",d.last_receipt_date "Last Inward",
            case 
            when (d.material_group_code = 'KDHMD3') then ('Pharma')
            when (d.material_group_code<> 'KDHMD3') then ('surgical')
            else null
            end as "Material Category"
            FROM IBAEHIS.ST_BATCH_SEARCH_LANG_VIEW a
            left join ST_BATCH_CONTROL b on ( a.ITEM_CODE=b.ITEM_CODE and a.BATCH_ID=b.BATCH_ID  and a.EXPIRY_DATE=b.EXPIRY_DATE_OR_RECEIPT_DATE)
            left join st_item c on (a.ITEM_CODE = c.ITEM_CODE )
            left join mm_item d on (a.item_code = d.item_code)
            WHERE ( b.SALE_PRICE >=:from_amount and b.SALE_PRICE <=:to_amount) AND  (a.STORE_CODE in (:store_code)) AND (a.ITEM_CODE LIKE '2000%') AND (c.CONSIGNMENT_ITEM_YN = 'N') 
            GROUP BY a.ITEM_CODE, a.ITEM_DESC,a.STORE_CODE,d.last_receipt_date,d.material_group_code
            ORDER BY d.material_group_code,a.ITEM_DESC   ASC

            
            """

            self.cursor.execute(
                stock_amount_wise_qurey, [from_amount, to_amount, store_code]
            )

        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_dept_issue_pending_tracker(self, from_date, to_date):

        dept_issue_pending_tracker_qurey = """
        
        
        select
        a.doc_no "Doc No",b.doc_date "Doc Date",a.item_code "Item Code",c.LONG_DESC "Item Name",b.REQ_BY_STORE_CODE "By Store",b.REQ_ON_STORE_CODE "To Store",
        a.REQ_ITEM_QTY "Req Qty",
        a.iss_item_qty "Issue Qty",
        a.COMMITTED_ITEM_QTY "Committed Qty",a.PENDING_ITEM_QTY "Pending Qty"
        from st_request_dtl a,st_request_hdr b, mm_item c
        where a.DOC_NO=b.DOC_NO and c.ITEM_CODE=a.ITEM_CODE and b.facility_id = 'KH'
        and b.DOC_DATE between :from_date and to_date(:to_date)
        order by b.doc_date, a.doc_no


        
        """

        self.cursor.execute(dept_issue_pending_tracker_qurey, [from_date, to_date])
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_patient_indent_count(self, facility_code, from_date, to_date):
        get_patient_indent_count_qurey = f""" 
        
        select distinct
        trunc(dispensed_date_time) "Disp Date",
        patient_id "Pat ID",
        (count(distinct(dispensed_date_time))) "Dispensed items Count"
        from ph_disp_hdr
        where disp_date_time between :from_date and to_date(:to_date) + 1
        and facility_id in ({facility_code})
        group by trunc(dispensed_date_time),patient_id
        order by trunc(dispensed_date_time),patient_id



"""

        self.cursor.execute(get_patient_indent_count_qurey, [from_date, to_date])
        get_patient_indent_count_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_patient_indent_count_data, column_name

    def get_eto_item_report(self, facility_code, from_date, to_date):
        get_eto_item_report_qurey = f""" 

        SELECT ST_TRN_AUDIT.STORE_CODE,ST_TRN_AUDIT.DOC_NO, 
        ST_TRN_AUDIT.TRN_SRL_NO,ST_TRN_AUDIT.DOC_SRL_NO,ST_TRN_AUDIT.ADDED_DATE,
        ST_TRN_AUDIT.DOC_TYPE_CODE,ST_TRN_AUDIT.ADDED_BY_ID ,ST_TRN_AUDIT.ITEM_CODE,
        ST_TRN_AUDIT.ITEM_QTY_NORMAL,ST_TRN_AUDIT.ITEM_UNIT_COST,mm_item.long_desc,mm_store.long_desc 
        FROM IBAEHIS.ST_TRN_AUDIT,IBAEHIS.MM_ITEM,IBAEHIS.MM_STORE
        WHERE   ST_TRN_AUDIT.ITEM_CODE = MM_ITEM.ITEM_CODE AND 
        ST_TRN_AUDIT.STORE_CODE = MM_STORE.STORE_CODE AND 
        ST_TRN_AUDIT.DOC_TYPE_CODE = 'ETORP' 
        AND ST_TRN_AUDIT.ADDED_DATE between :from_date and to_date(:to_date) + 1
        AND ST_TRN_AUDIT.FACILITY_ID in ({facility_code})
        order by doc_srl_no,doc_no



"""

        self.cursor.execute(get_eto_item_report_qurey, [from_date, to_date])
        get_eto_item_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_eto_item_report_data, column_name

    def get_predischarge_medication(self, from_date, to_date):

        predischarge_medication_qurey = """
        
        
            select c.PATIENT_ID as PatientID,c.LOCN_CODE as PtLocation,c.ORD_DATE_TIME as OrderDateTime , a.pre_dis_initiated_date_time,
                a.ASSIGN_BED_NUM as BedNo,c.DISPENSED_DATE_TIME as DispensedDateTime,count(d.DISP_QTY) as Dispensedcount,e.FREQ_CODE as Frequency,e.ORD_PRACT_ID as OrderBy 
           from pr_encounter a, or_order b, ph_disp_hdr c,ph_disp_dtl d ,OR_ORDER_LINE e
          where c.DISP_NO = d.DISP_NO and b.ORDER_ID = c.ORDER_ID and a.PATIENT_ID = b.PATIENT_ID and b.ORDER_ID = e.order_id and
            a.ENCOUNTER_ID = b.ENCOUNTER_ID and c.LOCN_CODE not in ('FL9C', 'FL9W') and 
            a.facility_id = 'KH' and a.patient_class = 'IP' and b.order_category = 'PH' and b.PRIORITY='U' and b.PERFORMING_FACILITY_ID ='KH' and 
            b.ORD_DATE_TIME BETWEEN :from_date and :to_date
            group by c.PATIENT_ID,c.LOCN_CODE,c.ORD_DATE_TIME,c.DISPENSED_DATE_TIME,a.ASSIGN_BED_NUM,e.FREQ_CODE,e.ORD_PRACT_ID , a.pre_dis_initiated_date_time
            order by c.DISPENSED_DATE_TIME desc


        
        """

        self.cursor.execute(predischarge_medication_qurey, [from_date, to_date])
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_predischarge_initiate(self):
        predischarge_initiate_query = """ select a.PATIENT_ID, b.patient_name, a.VISIT_ADM_DATE_TIME Admission_Time, p.practitioner_name , a.PRE_DIS_INITIATED_DATE_TIME ,i.NURSING_UNIT_CODE, i.BED_NUM
from pr_encounter a, mp_patient b, am_practitioner p , ip_open_encounter i
where a.PATIENT_ID=b.PATIENT_ID  and  a.ADMIT_PRACTITIONER_ID=p.PRACTITIONER_ID
and a.PATIENT_ID = i.PATIENT_ID and a.ENCOUNTER_ID = i.ENCOUNTER_ID
and i.FACILITY_ID = 'KH' and a.PRE_DIS_INITIATED_DATE_TIME is not null
 """

        self.cursor.execute(predischarge_initiate_query)
        predischarge_initiate_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return predischarge_initiate_data, column_name

    def get_intransites_unf_sal_ret(self, from_date, to_date):

        intransites_unf_sal_ret_qurey = """
        
        
            select c.PATIENT_ID as PatientID,c.LOCN_CODE as PtLocation,c.ORD_DATE_TIME as OrderDateTime , a.pre_dis_initiated_date_time,
                a.ASSIGN_BED_NUM as BedNo,c.DISPENSED_DATE_TIME as DispensedDateTime,count(d.DISP_QTY) as Dispensedcount,e.FREQ_CODE as Frequency,e.ORD_PRACT_ID as OrderBy 
           from pr_encounter a, or_order b, ph_disp_hdr c,ph_disp_dtl d ,OR_ORDER_LINE e
          where c.DISP_NO = d.DISP_NO and b.ORDER_ID = c.ORDER_ID and a.PATIENT_ID = b.PATIENT_ID and b.ORDER_ID = e.order_id and
            a.ENCOUNTER_ID = b.ENCOUNTER_ID and c.LOCN_CODE not in ('FL9C', 'FL9W') and 
            a.facility_id = 'KH' and a.patient_class = 'IP' and b.order_category = 'PH' and b.PRIORITY='U' and b.PERFORMING_FACILITY_ID ='KH' and 
            b.ORD_DATE_TIME BETWEEN :from_date and :to_date
            group by c.PATIENT_ID,c.LOCN_CODE,c.ORD_DATE_TIME,c.DISPENSED_DATE_TIME,a.ASSIGN_BED_NUM,e.FREQ_CODE,e.ORD_PRACT_ID , a.pre_dis_initiated_date_time
            order by c.DISPENSED_DATE_TIME desc


        
        """

        self.cursor.execute(intransites_unf_sal_ret_qurey, [from_date, to_date])
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_intransites_unf_stk_tfr(self, from_date, to_date):

        intransites_unf_stk_tfr_qurey = """
        
        select
a.facility_id,
a.doc_no,
a.doc_date,
a.fm_store_code,
a.to_store_code,
b.ITEM_CODE,
b.ITEM_QTY
from st_transfer_hdr a,st_transfer_dtl b
where
a.DOC_NO=b.DOC_NO and
a.FM_STORE_CODE in (select store_code from mm_store where eff_Status = 'E') and
a.TO_STORE_CODE in (select store_code from mm_store where eff_Status = 'E') and
a.facility_id = 'KH' and
a.finalized_yn = 'N' and
a.doc_date between :from_date and :to_date
order by a.doc_date


        
        """

        self.cursor.execute(intransites_unf_stk_tfr_qurey, [from_date, to_date])
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_intransites_acknowledgement_pending_iss(self, facility_code):

        intransites_acknowledgement_pending_iss_qurey = f"""
        
        select
        a.DOC_DATE "Date",a.DOC_NO "Doc No",a.DOC_TYPE_CODE "Trn",
        a.FM_STORE_CODE "From",a.TO_STORE_CODE "To",
        a.FINALIZED_YN "Finalize ?",a.PROCESS_FOR_ACKNOWLEDGE "Sent to Ack ?",
        b.ITEM_CODE "Item Code",d.LONG_DESC "Item Name",c.BATCH_ID "Batch",
        c.EXPIRY_DATE_OR_RECEIPT_DATE "Expiry",c.ISS_ITEM_QTY "Trn Qty",a.FACILITY_ID
        from st_issue_hdr a,st_issue_dtl b,st_issue_dtl_exp c, mm_item d
        where 
        a.FACILITY_ID in ({facility_code})
         and
        a.DOC_NO=b.DOC_NO and
        b.DOC_NO=c.DOC_NO and
        b.ITEM_CODE=c.ITEM_CODE and
        b.ITEM_CODE=d.ITEM_CODE and
        a.FINALIZED_YN = 'N' and
        a.PROCESS_FOR_ACKNOWLEDGE = 'Y' and
        a.FM_STORE_CODE in (select store_code from mm_store where eff_Status = 'E') and
        a.TO_STORE_CODE in (select store_code from mm_store where eff_Status = 'E') and
        a.DOC_NO not in (select distinct doc_no from st_acknowledge_trn_hdr where doc_type_code = 'ISS')
        order by a.DOC_DATE

        
        """

        self.cursor.execute(intransites_acknowledgement_pending_iss_qurey)
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_intransites_acknowledgement_pending_iss_rt(self):

        intransites_acknowledgement_pending_iss_rt_qurey = """
        
        select
        a.DOC_DATE "Date",a.DOC_NO "Doc No",a.DOC_TYPE_CODE "Trn",
        a.FM_STORE_CODE "From",a.TO_STORE_CODE "To",
        a.FINALIZED_YN "Finalize ?",a.PROCESS_FOR_ACKNOWLEDGE "Sent to Ack ?",
        b.ITEM_CODE "Item Code",d.LONG_DESC "Item Name",c.BATCH_ID "Batch",
        c.EXPIRY_DATE_OR_RECEIPT_DATE "Expiry",c.ITEM_QTY "Trn Qty"
        from st_issue_ret_hdr a,st_issue_ret_dtl b,st_issue_ret_dtl_exp c, mm_item d
        where 
        a.FACILITY_ID = 'KH' and
        a.DOC_NO=b.DOC_NO and
        b.DOC_NO=c.DOC_NO and
        b.ITEM_CODE=c.ITEM_CODE and
        b.ITEM_CODE=d.ITEM_CODE and
        a.FINALIZED_YN = 'N' and
        a.PROCESS_FOR_ACKNOWLEDGE = 'Y' and
        a.FM_STORE_CODE in (select store_code from mm_store where eff_Status = 'E') and
        a.TO_STORE_CODE in (select store_code from mm_store where eff_Status = 'E') and
        a.DOC_NO not in (select distinct doc_no from st_acknowledge_trn_hdr where doc_type_code = 'ISRT')
        order by a.DOC_DATE

        
        """

        self.cursor.execute(intransites_acknowledgement_pending_iss_rt_qurey)
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_narcotic_stock_report(self):

        narcotic_stock_report_qurey = """
                    
            select a.store_code "Store Code",a.item_code "Item Code",a.item_desc "Item Description",a.batch_id,a.expiry_date,a.QTY_ON_HAND,a.AVAIL_QTY,c.consignment_item_yn "Consignment Flag"
            from st_batch_search_lang_view a
            left join st_item c on c.item_code = a.item_code
            left join mm_item b on b.item_code = a.item_code
            WHERE a.store_code  = 'CP00' and a.item_code in
            ('2000021578',
            '2000031359',
            '2000039945',
            '2000066488',
            '2000052442',
            '2000021261',
            '2000021262',
            '2000037679',
            '2000037680',
            '2000044178',
            '2000018475',
            '2000046318',
            '2000042077',
            '2000052521',
            '2000046422',
            '2000060693',
            '2000028973',
            '2000024878',
            '2000050688')
            and c.consignment_item_yn = 'N'
            and (a.QTY_ON_HAND > 0) 
            order by a.store_code,a.item_code

        
        """

        self.cursor.execute(narcotic_stock_report_qurey)
        data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        # column info
        # for x in self.cursor.description:
        #     print(x)

        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

        return data, column_name

    def get_schedule_item_iv_and_consumables(self, facility_code):
        get_schedule_item_iv_and_consumables_qurey = f""" 
        
            Select a.STORE_CODE "Store",a.ITEM_CODE "IC",b.LONG_DESC "Item Name",sum(a.QTY_ON_HAND-a.COMMITTED_QTY) "Available"
            from st_item_batch a,mm_item b
            where a.ITEM_CODE=b.ITEM_CODE
            and a.ADDED_FACILITY_ID in {(facility_code)} 
            and a.ITEM_CODE in 
            ('2000038048',
            '2000025129',
            '2000040082',
            '2000049104',
            '2000048218',
            '2000008631',
            '2000040083',
            '2000038612',
            '2000009710',
            '2000048219',
            '2000038608',
            '2000034198',
            '2000038641',
            '2000038713',
            '2000038614',
            '2000038607',
            '2000038605',
            '2000031762',
            '2000038629',
            '2000038609',
            '2000038740',
            '2000024061',
            '2000038549',
            '2000023222',
            '2000016494',
            '2000008840',
            '2000008849',
            '2000008839',
            '2000008850',
            '2000008844',
            '2000008838',
            '2000016495',
            '2000008842',
            '2000008859',
            '2000008843',
            '2000008858',
            '2000014219',
            '2000065105',
            '2000061981',
            '2000065106',
            '2000065104',
            '2000062068',
            '2000061592',
            '2000057677',
            '2000008088',
            '2000037748',
            '2000041353',
            '2000041352',
            '2000016453',
            '2000016454',
            '2000016235',
            '2000038631',
            '2000063937',
            '2000010575',
            '2000010576',
            '2000010563',
            '2000053155',
            '2000053153',
            '2000053154',
            '2000053152',
            '2000059665',
            '2000024904',
            '2000024903',
            '2000008798',
            '2000064537',
            '2000064649',
            '2000035702',
            '2000016186',
            '2000065906',
            '2000063922',
            '2000063914',
            '2000063923',
            '2000063719',
            '2000050323',
            '2000028708',
            '2000051724',
            '2000051725',
            '2000037887',
            '2000063750',
            '2000023581',
            '2000023582',
            '2000060700',
            '2000045983',
            '2000013799',
            '2000030996',
            '2000034186',
            '2000018469',
            '2000036975',
            '2000042706',
            '2000042707',
            '2000036974',
            '2000036973',
            '2000056385',
            '2000052432',
            '2000062448',
            '2000016310',
            '2000016315',
            '2000035255',
            '2000016358',
            '2000016341',
            '2000032772',
            '2000016320',
            '2000028879',
            '2000061555',
            '2000031739',
            '2000016313',
            '2000037872',
            '2000044901',
            '2000036186',
            '2000027494',
            '2000047152',
            '2000017607',
            '2000017605',
            '2000020369',
            '2000017606',
            '2000044899',
            '2000051918',
            '2000043966',
            '2000045984',
            '2000035785',
            '2000064747',
            '2000064746'
            )
            group by a.STORE_CODE,a.ITEM_CODE,b.LONG_DESC
            order by a.STORE_CODE,a.ITEM_CODE



"""

        self.cursor.execute(get_schedule_item_iv_and_consumables_qurey)
        get_schedule_item_iv_and_consumables_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_schedule_item_iv_and_consumables_data, column_name

    def get_credit_outstanding_bill_value(self, facility_code, from_date, to_date):
        get_credit_outstanding_bill_qurey = f""" 
        
        select distinct pack.patient_id,pack.NAME_PREFIX,pack.FIRST_NAME,pack.SECOND_NAME,pack.FAMILY_NAME,
       pack.ADDED_DATE,pack.LONG_DESC,B.LONG_DESC Service_name,a.blng_serv_code,
       a.trx_date,T.PRACTITIONER_NAME,T.primary_speciality_code,a.serv_item_desc,A.ORG_GROSS_CHARGE_AMT 
       from bl_patient_charges_folio a,bl_blng_serv b,am_practitioner t,
       (select E.patient_id,E.EPISODE_ID,M.NAME_PREFIX,M.FIRST_NAME,M.SECOND_NAME,M.FAMILY_NAME,H.ADDED_DATE,P.LONG_DESC  
       from mp_patient M,pr_encounter E,bl_package_sub_hdr h,bl_package p,bl_package_encounter_dtls f
       where e.specialty_code ='EHC'
       and M.PATIENT_ID =E.PATIENT_ID 
       and E.ADDED_FACILITY_ID in {(facility_code)} 
       and H.PACKAGE_CODE=P.PACKAGE_CODE 
       and f.PACKAGE_SEQ_NO = h.PACKAGE_SEQ_NO 
       and f.PACKAGE_CODE = h.PACKAGE_CODE
       and f.PATIENT_ID =h.PATIENT_ID 
       and f.ENCOUNTER_ID = e.EPISODE_ID
       and h.status='C' 
       and p.OPERATING_FACILITY_ID in {(facility_code)} 
       and h.added_date between :from_date and to_date(:to_date) + 1)pack
       where pack.patient_id=a.patient_id and NVL(trx_STATUS,'X')<>'C'and a.trx_date >pack.added_date and A.BLNG_SERV_CODE =B.BLNG_SERV_CODE(+)
       and A.PHYSICIAN_ID=T.PRACTITIONER_ID(+)
       and a.blng_Serv_code not in ('HSPK000001') and  a.OPERATING_FACILITY_ID in {(facility_code)} 
        and pack.added_date between :from_date and to_date(:to_date) + 1



"""

        self.cursor.execute(get_credit_outstanding_bill_qurey, [from_date, to_date])
        get_credit_outstanding_bill_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_credit_outstanding_bill_data, column_name

    def get_tpa_letter(self, facility_code, from_date, to_date):
        get_tpa_letter_qurey = f""" 
        
       SELECT distinct a.patient_id,b.PATIENT_NAME,TRUNC(a.DISCHARGE_DATE_TIME) DISCHARGE_DATE_TIME ,
       h.long_name,f.TOT_BUS_GEN_AMT Total_Amount, i.bill_amt Pay_by_TPA, 
       f.BILL_DOC_NUMBER Bill_Number, to_char(g.policy_number), to_char(g.credit_auth_ref),i.doc_date
       FROM pr_encounter a, mp_patient b,am_practitioner c, am_speciality d,ip_bed_class e, bl_episode_fin_dtls f,
       BL_ENCOUNTER_PAYER_APPROVAL g, AR_CUSTOMER H, BL_Bill_HDR I
       WHERE a.PATIENT_ID = b.PATIENT_ID(+) AND a.ATTEND_PRACTITIONER_ID = c.PRACTITIONER_ID(+) and i.CUST_CODE = h.cust_code(+)
       and a.PATIENT_ID = f.PATIENT_ID(+) and a.episode_id = f.episode_id(+) and f.episode_id = g.episode_id(+) and g.episode_type = 'I'
       and a.patient_id = i.patient_id and a.episode_id = i.episode_id and a.episode_id = g.episode_id
       AND a.SPECIALTY_CODE = d.SPECIALITY_CODE(+) and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE(+) AND a.patient_class = 'IP'
       and a.cancel_reason_code is null and i.BLNG_GRP_ID IN('TPA','GTPA') and i.bill_amt <> 0
       and f.cust_code not in ('50000004', '50000047', '401240', '30000332')
       AND TRUNC(i.doc_date) between :from_date and :to_date
       and f.OPERATING_FACILITY_ID in ({facility_code})



"""

        self.cursor.execute(get_tpa_letter_qurey, [from_date, to_date])
        get_tpa_letter_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_tpa_letter_data, column_name

    def get_online_consultation_report(self, from_date, to_date):
        get_online_consultation_report_qurey = """ 
        
       SELECT   TO_CHAR (a.service_date, 'DD/MM/YY') ser_date,TO_CHAR (a.service_date, 'HH24:MI:SS') ser_time, a.blng_serv_code serv_code, c.long_desc serv_desc,DECODE (a.episode_type,'I', 'IP','O', 'OP','E', 'Emergency','R', 'Referral','D', 'Daycare') pat_Type,
       a.patient_id pat_id, b.short_name pat_name, a.upd_net_charge_amt amount, a.episode_id episode_id, a.blng_class_code blng_class_code, a.bed_class_code bed_class_code, a.serv_qty,p.LONG_DESC, a.physician_id, q.PRACTITIONER_NAME
       FROM bl_patient_charges_folio a, mp_patient_mast b,bl_blng_serv c, BL_PACKAGE_ENCOUNTER_DTLS e,bl_package p, am_practitioner q
       WHERE a.operating_facility_id = 'KH' AND a.patient_id = b.patient_id AND a.blng_serv_code = c.blng_serv_code
       and NVL(A.BILLED_FLAG,'N') = decode(a.episode_type, 'O', 'Y', 'E', 'Y', 'R', 'Y', NVL(A.BILLED_FLAG, 'N'))
       AND a.service_date between :from_date and  to_date(:to_date) + 1 
       and a.blng_serv_code in ('CNOP000029', 'CNOP000040', 'CNOP000041', 'CNOP000044')
       and a.physician_id = q.PRACTITIONER_ID
       and a.ENCOUNTER_ID = e.ENCOUNTER_ID(+) and a.PACKAGE_SEQ_NO = e.PACKAGE_SEQ_NO(+) and a.OPERATING_FACILITY_ID = e.OPERATING_FACILITY_ID(+)
       and e.PACKAGE_CODE = p.PACKAGE_CODE(+) and e.OPERATING_FACILITY_ID = p.OPERATING_FACILITY_ID(+)

"""

        self.cursor.execute(get_online_consultation_report_qurey, [from_date, to_date])
        get_online_consultation_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_online_consultation_report_data, column_name

    def get_contract_report(self, facility_code):

        get_contract_report_qurey = f"""
        
        
            select CUST_CODE,LONG_NAME,CUST_GROUP_CODE,IP_YN,OP_YN,VALID_TO,MODIFIED_FACILITY_ID 
            from ar_customer 
            where MODIFIED_FACILITY_ID in ({facility_code})  
            --and VALID_TO is not null  
            --and ADDED_FACILITY_ID in ({facility_code})  
            order by VALID_TO 
        
        """

        self.cursor.execute(get_contract_report_qurey)
        get_contract_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_contract_report_data, column_name

    def get_admission_census(self, from_date, to_date, facility_code):
        admission_census_qurey = f""" 

        
        SELECT a.FACILITY_ID , a.patient_id,b.PATIENT_NAME,a.VISIT_ADM_DATE_TIME Admission_Date,E.LONG_DESC,a.episode_id
        FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f,mp_country m
        WHERE a.PATIENT_ID=b.PATIENT_ID AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID 
        and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id
        AND a.patient_class = 'IP'  AND a.SPECIALTY_CODE = d.SPECIALITY_CODE 
        and m.COUNTRY_CODE=b.NATIONALITY_CODE
        and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE and a.cancel_reason_code is null
        AND a.VISIT_ADM_DATE_TIME between :from_date and to_date (:to_date) + 1
        and a.FACILITY_ID in ({facility_code})
        ORDER BY A.ASSIGN_CARE_LOCN_CODE



"""

        self.cursor.execute(admission_census_qurey, [from_date, to_date])
        admission_censust_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return admission_censust_data, column_name

    def get_card(self, from_date, to_date, facility_code):
        card_qurey = f""" 

        
        select  TO_CHAR (d.doc_date, 'DD/MM/YY') dat         ,TO_CHAR (d.doc_date, 'HH24:MI:SS') tim
        ,d.doc_type_code||'/'||d.doc_number rec_doc_no          ,d.patient_id UHID
        ,a.SHORT_NAME patient_name          ,d.customer_code          ,c.payer_name
        ,d.doc_amt amount       
        ,d.recpt_type_code          ,d.recpt_nature_code          ,d.recpt_refund_ind
        ,c.slmt_type_code          ,c.slmt_doc_ref_desc "Chq No./Card No."
        ,c.slmt_doc_remarks          ,d.NARRATION          ,c.cash_slmt_flag          ,d.cash_counter_code
        ,d.added_by_id          ,c.cancelled_ind          ,c.bank_code          ,c.bank_branch
        ,d.bill_doc_type_code||'/'||d.bill_doc_number bill_no          ,d.episode_id
        ,c.APPROVAL_REF_NO,c.RCPT_RFND_ID_NO TID
        ,c.CC_BATCH_NO, c.CC_SALE_DRAFT_NO,c.TERM_ID_NUM,C.RCPT_RFND_ID_NO
        FROM bl_receipt_refund_dtl c, bl_receipt_refund_hdr d,mp_patient_mast a    ,BL_SLMT_TYPE e 
        --WHERE  c.operating_facility_id = :p_facility_id--
        WHERE  c.operating_facility_id in ({facility_code}) 
        --AND TRUNC (d.doc_date) >= to_date(:nd_period_from,'DD/MM/YYYY')--
        --AND TRUNC (d.doc_date) < to_date(:nd_period_to,'DD/MM/YYYY')+1--
        AND TRUNC (d.doc_date) >= :from_date
        AND TRUNC (d.doc_date) < to_date(:to_date)+1--
        AND c.doc_type_code = d.doc_type_code--
        AND c.doc_number = d.doc_number--
        and( d.RECPT_REFUND_IND='R' or
        (d.RECPT_REFUND_IND='F' and d.recpt_nature_code='BI'))
        and c.SLMT_TYPE_CODE=e.SLMT_TYPE_CODE
        and e.CASH_SLMT_FLAG='A'
        --and d.added_by_id in ('KH51000578')
        --and c.slmt_type_code= 'OG'
        --and c.SLMT_TYPE_CODE in ('AM')  added by manu on 29/8/13   
        and d.patient_id = a.patient_id--
        AND NOT EXISTS (
        SELECT 1
        FROM bl_cancelled_bounced_trx f
        WHERE f.doc_type_code = d.doc_type_code
        AND f.doc_number = d.doc_number
        --AND trunc(f.cancelled_date)  >= to_date(:nd_period_from,'DD/MM/YYYY')
        AND trunc(f.cancelled_date)  >= :from_date
        AND NVL (d.cancelled_ind, 'N') = 'Y'
        --AND trunc(f.cancelled_date)  < to_date(:nd_period_to,'DD/MM/YYYY')+1)
        AND trunc(f.cancelled_date)  < to_date(:to_date)+1)
        union all  
        select  TO_CHAR (f.cancelled_date, 'DD/MM/YY') dat         ,TO_CHAR (f.cancelled_date, 'HH24:MI:SS') tim
        ,d.doc_type_code||'/'||d.doc_number rec_doc_no          ,d.patient_id UHID
        ,a.SHORT_NAME patient_name          ,d.customer_code          ,c.payer_name
        ,-1*d.doc_amt amount       
        ,d.recpt_type_code          ,d.recpt_nature_code          ,d.recpt_refund_ind
        ,c.slmt_type_code          ,c.slmt_doc_ref_desc "Chq No./Card No."
        ,c.slmt_doc_remarks          ,d.NARRATION          ,c.cash_slmt_flag          ,d.cash_counter_code
        ,d.added_by_id          ,c.cancelled_ind          ,c.bank_code          ,c.bank_branch
        ,d.bill_doc_type_code||'/'||d.bill_doc_number bill_no          ,d.episode_id
        ,c.APPROVAL_REF_NO,c.RCPT_RFND_ID_NO TID
        ,c.CC_BATCH_NO, c.CC_SALE_DRAFT_NO,c.TERM_ID_NUM,C.RCPT_RFND_ID_NO
        FROM bl_receipt_refund_dtl c, bl_receipt_refund_hdr d,mp_patient_mast a  ,bl_cancelled_bounced_trx f ,BL_SLMT_TYPE e 
        --WHERE  c.operating_facility_id = :p_facility_id--
        WHERE  c.operating_facility_id in ({facility_code})
        --and d.added_by_id in ('KH51000578')
        --and c.slmt_type_code= 'OG'
        --and c.SLMT_TYPE_CODE in ('AM') added by manu on 29/8/13
        AND c.doc_type_code = d.doc_type_code--
        AND c.doc_number = d.doc_number--
        and d.patient_id = a.patient_id--
        and( d.RECPT_REFUND_IND='R' or
        (d.RECPT_REFUND_IND='F' and d.recpt_nature_code='BI'))
        and c.SLMT_TYPE_CODE=e.SLMT_TYPE_CODE
        and e.CASH_SLMT_FLAG='A'
        and f.doc_type_code = d.doc_type_code
        AND f.doc_number = d.doc_number
        --AND trunc(f.cancelled_date)  >= to_date(:nd_period_from,'DD/MM/YYYY')
        --AND trunc(f.cancelled_date)  < to_date(:nd_period_to,'DD/MM/YYYY')+1
        AND trunc(f.cancelled_date)  >= to_date(:from_date)
        AND trunc(f.cancelled_date)  < to_date(:to_date)
        AND trunc(f.cancelled_date)  > trunc(d.doc_date)
        AND NVL (d.cancelled_ind, 'N') = 'Y'






"""

        self.cursor.execute(card_qurey, [from_date, to_date])
        card_qurey = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return card_qurey, column_name

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

    def get_pd_report(self, facility_code):

        pd_report_qurey = f""" 

        
            select a.PATIENT_ID, b.patient_name, a.VISIT_ADM_DATE_TIME Admission_Time, E.LONG_DESC,a.assign_bed_num, 
            c.DIS_ADV_DATE_TIME DISCHARGE_REQUEST_TIME,c.EXPECTED_DISCHARGE_DATE ,D.BILL_DOC_DATE,a.DISCHARGE_DATE_TIME Bed_Clear_Date_Time,D.BLNG_GRP_ID,a.PRE_DIS_INITIATED_DATE_TIME DRS_Discharge_Adv_Time,a.ASSIGN_CARE_LOCN_CODE,
            f.PRACTITIONER_NAME Treating_Doctor,g.LONG_DESC Speciality,c.ENCOUNTER_ID,c.added_by_id,h.appl_user_name
            from pr_encounter a, mp_patient b, ip_discharge_advice c, bl_episode_fin_dtls d,ip_bed_class e,am_practitioner f,am_speciality g,sm_appl_user h
            where a.PATIENT_ID=b.PATIENT_ID and a.PATIENT_CLASS = 'IP' and a.ENCOUNTER_ID=c.ENCOUNTER_ID and a.ENCOUNTER_ID=d.EPISODE_ID 
            and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE 
            and a.cancel_reason_code is null
            and a.ATTEND_PRACTITIONER_ID =f.PRACTITIONER_ID
            AND a.SPECIALTY_CODE = g.SPECIALITY_CODE
            and c.added_by_id = h.appl_user_id
            and a.facility_id in ({facility_code})
            and DIS_ADV_STATUS = '0'
            order by BILL_DOC_DATE

"""
        self.cursor.execute(pd_report_qurey)
        pd_report_qurey = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return pd_report_qurey, column_name

    def get_current_inpatients_employee_and_dependants(self, from_date, to_date):
        get_current_inpatients_employee_and_dependants_query = """
        
       SELECT a.patient_id,b.PATIENT_NAME,b.REGN_DATE,get_age(b.date_of_birth,SYSDATE) Age,b.SEX Gender,a.VISIT_ADM_DATE_TIME Admission_Date,a.DISCHARGE_DATE_TIME
        ,E.LONG_DESC WARD,a.ASSIGN_BED_NUM Bed_Num,c.PRACTITIONER_NAME Treating_Doctor,d.LONG_DESC Speciality,
        decode(f.BLNG_GRP_ID,'EMPL','Employee','EMDP','Dependant') EMP_DEP
        ,f.cust_code,f.NON_INS_BLNG_GRP_ID
        ,b.ALT_ID2_NO prno
        FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f ,mp_country m,
        mp_pat_addresses k,mp_postal_code p,empdata r,  XF_INT.XF_EXT_DEMOGRAPHICS t,sm_Appl_user u
        WHERE a.PATIENT_ID=b.PATIENT_ID AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID and a.patient_id=k.patient_id(+)
        and k.POSTAL2_CODE = p.POSTAL_CODE(+) and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id AND a.patient_class = 'IP'
        AND a.SPECIALTY_CODE = d.SPECIALITY_CODE and m.COUNTRY_CODE=b.NATIONALITY_CODE and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE
        and a.cancel_reason_code is null AND a.VISIT_ADM_DATE_TIME between :from_date and to_date(:to_date)+1 and a.ADDED_FACILITY_ID = 'KH'
        and b.ALT_ID2_NO is not null      
        and r.ALT_ID2_NO(+) =b.ALT_ID2_NO
        and r.PATIENT_ID(+) =b.PATIENT_ID
        and t.EXT_PAT_ID(+) =b.ALT_ID2_NO
        and t.EHIS_PAT_ID(+) =b.PATIENT_ID
        and u.FUNC_ROLE_ID(+) = b.ALT_ID2_NO
        ORDER BY a.PATIENT_ID






"""
        self.cursor.execute(
            get_current_inpatients_employee_and_dependants_query, [from_date, to_date]
        )
        get_current_inpatients_employee_and_dependants_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_current_inpatients_employee_and_dependants_data, column_name

    def get_treatment_sheet_data(self):

        treatment_sheet_data_qurey = """
        
        
            select e.PATIENT_ID,m.PATIENT_NAME,e.NURSING_UNIT_CODE, e.BED_NUM,p.PRACTITIONER_NAME ATTEND_PRACTITIONER, s.LONG_DESC SPECIALITY,
            trunc(e.ADMISSION_DATE_TIME),trunc(sysdate) CURRENT_DATE,trunc(sysdate)-trunc(e.ADMISSION_DATE_TIME) ALOS,
            (trunc(sysdate)-trunc(e.ADMISSION_DATE_TIME))/5 CODE
            from ip_open_encounter e,mp_patient m,am_practitioner p,am_Speciality s where e.PATIENT_ID = m.PATIENT_ID 
             and e.FACILITY_ID = 'KH' and e.ATTEND_PRACTITIONER_ID= p.PRACTITIONER_ID and  
             p.PRIMARY_SPECIALITY_CODE =s.SPECIALITY_CODE


        
        """

        self.cursor.execute(treatment_sheet_data_qurey)
        treatment_sheet_data_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return treatment_sheet_data_data, column_name

    def get_package_contract_report(self, from_date, to_date, facility_code):
        get_package_contract_report_qurey = f""" 
        
       select PACKAGE_CODE,LONG_DESC,EFF_TO_DATE,OP_YN,IP_YN from BL_PACKAGE 
       where EFF_TO_DATE between :from_date and to_date(:to_date) + 1 and OPERATING_FACILITY_ID in ({facility_code})
       and EFF_TO_DATE is not null order by EFF_TO_DATE
      
"""

        self.cursor.execute(get_package_contract_report_qurey, [from_date, to_date])
        get_package_contract_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_package_contract_report_data, column_name

    def get_credit_card_reconciliation_report(self, facility_code, from_date, to_date):
        get_credit_card_reconciliation_report_qurey = f""" 
        
       select  TO_CHAR (d.doc_date, 'DD/MM/YY') dat,TO_CHAR (d.doc_date, 'HH24:MI:SS') tim,d.doc_type_code||'/'||d.doc_number rec_doc_no,d.patient_id UHID,
       a.SHORT_NAME patient_name,d.customer_code,c.payer_name,d.doc_amt amount,d.recpt_type_code,d.recpt_nature_code,d.recpt_refund_ind,
       c.slmt_type_code,c.slmt_doc_ref_desc ChqNo_CardNo,c.slmt_doc_remarks,d.NARRATION,c.cash_slmt_flag,d.cash_counter_code,
       d.added_by_id,c.cancelled_ind,c.bank_code,c.bank_branch,d.bill_doc_type_code||'/'||d.bill_doc_number bill_no,d.episode_id,
       c.APPROVAL_REF_NO,c.RCPT_RFND_ID_NO TID,c.CC_BATCH_NO, c.CC_SALE_DRAFT_NO,c.TERM_ID_NUM,C.RCPT_RFND_ID_NO
       FROM bl_receipt_refund_dtl c, bl_receipt_refund_hdr d,mp_patient_mast a,BL_SLMT_TYPE e
       WHERE  c.operating_facility_id in ({facility_code})  AND TRUNC (d.doc_date) between :from_date and :to_date
       AND c.doc_type_code = d.doc_type_code
       AND c.doc_number = d.doc_number and( d.RECPT_REFUND_IND='R' or (d.RECPT_REFUND_IND='F' and d.recpt_nature_code='BI'))
       and c.SLMT_TYPE_CODE=e.SLMT_TYPE_CODE and e.CASH_SLMT_FLAG='A'and d.patient_id = a.patient_id
       AND NOT EXISTS ( SELECT 1 FROM bl_cancelled_bounced_trx f WHERE f.doc_type_code = d.doc_type_code AND f.doc_number = d.doc_number
       AND trunc(f.cancelled_date) >= to_date(:from_date,'DD/MM/YYYY')
       AND NVL (d.cancelled_ind, 'N') = 'Y' AND trunc(f.cancelled_date)  < to_date(:to_date,'DD/MM/YYYY')+1)
       union all
       select  TO_CHAR (f.cancelled_date, 'DD/MM/YY') dat,TO_CHAR (f.cancelled_date, 'HH24:MI:SS') tim,d.doc_type_code||'/'||d.doc_number rec_doc_no,d.patient_id UHID,
       a.SHORT_NAME patient_name,d.customer_code,c.payer_name,-1*d.doc_amt amount,d.recpt_type_code,d.recpt_nature_code,d.recpt_refund_ind,
       c.slmt_type_code,c.slmt_doc_ref_desc ChqNo_CardNo,c.slmt_doc_remarks,d.NARRATION,c.cash_slmt_flag,d.cash_counter_code,
       d.added_by_id,c.cancelled_ind,c.bank_code,c.bank_branch ,d.bill_doc_type_code||'/'||d.bill_doc_number bill_no,d.episode_id,c.APPROVAL_REF_NO,
       c.RCPT_RFND_ID_NO TID,c.CC_BATCH_NO, c.CC_SALE_DRAFT_NO,c.TERM_ID_NUM,C.RCPT_RFND_ID_NO
       FROM bl_receipt_refund_dtl c, bl_receipt_refund_hdr d,mp_patient_mast a,bl_cancelled_bounced_trx f ,BL_SLMT_TYPE e
       WHERE  c.operating_facility_id in ({facility_code})  AND c.doc_type_code = d.doc_type_code AND c.doc_number = d.doc_number
       and d.patient_id = a.patient_id and( d.RECPT_REFUND_IND='R' or (d.RECPT_REFUND_IND='F' and d.recpt_nature_code='BI'))
       and c.SLMT_TYPE_CODE=e.SLMT_TYPE_CODE and e.CASH_SLMT_FLAG='A'and f.doc_type_code = d.doc_type_code AND f.doc_number = d.doc_number
       AND trunc(f.cancelled_date)  >= to_date(:from_date ,'DD/MM/YYYY') AND trunc(f.cancelled_date)  < to_date(:to_date,'DD/MM/YYYY')+1
       AND trunc(f.cancelled_date)  > trunc(d.doc_date) AND NVL (d.cancelled_ind, 'N') = 'Y' 
      


"""

        self.cursor.execute(
            get_credit_card_reconciliation_report_qurey,
            [from_date, to_date],
        )
        get_credit_card_reconciliation_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_credit_card_reconciliation_report_data, column_name

    def get_covid_ot_surgery_details(self, facility_code, from_date, to_date):
        get_covid_ot_surgery_details_qurey = f""" 
        
       select distinct g.patient_id,b.patient_name,get_age(b.date_of_birth,SYSDATE) Age,b.sex,C.ORDER_ID,a.ENCOUNTER_ID COVID_TEST_ENCOUNTER_,g.ENCOUNTER_ID OT_ORDERED_ENCOUNTER,g.ORDER_DATE_TIME OT_ORDER_TIME,C.ORDER_CATALOG_CODE,C.CATALOG_DESC,
       g.pref_surg_date, D.PRACTITIONER_NAME,E.LONG_DESC,g.added_date,dbms_lob.substr(f.ORDER_COMMENT,5000,1),o.ord_date_time,SPEC_REGD_DATE_TIME,
       o.PATIENT_CLASS, t.result_text result
       from ot_pending_order g,mp_patient b, or_order_line c,AM_PRACTITIONER d,AM_SPECIALITY e,or_order_comment f,
       or_order o,OR_ORDER_LINE L,RL_REQUEST_HEADER A,RL_result_text t
       where o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMB000094' and o.ORDER_STATUS = 'CD'
       and t.SPECIMEN_NO(+)=a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and  o.ORDERING_FACILITY_ID in ({facility_code})
       and g.patient_id = a.patient_id and a.patient_id = b.patient_id and g.order_id = c.order_id
       and g.PHYSICIAN_ID = D.PRACTITIONER_ID and g.order_id = f.order_id(+) and D.PRIMARY_SPECIALITY_CODE = E.SPECIALITY_CODE
       AND trunc(PREF_SURG_DATE)  between :from_date and :to_date
      
"""

        self.cursor.execute(get_covid_ot_surgery_details_qurey, [from_date, to_date])
        get_covid_ot_surgery_details_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_covid_ot_surgery_details_data, column_name

    def get_gst_data_of_pharmacy(self, facility_code):

        gst_data_of_pharmacy_qurey = f"""
        
        
            Select * from gst_data_ph
            where OPERATING_FACILITY_ID in ({facility_code})
        
        """

        self.cursor.execute(gst_data_of_pharmacy_qurey)
        gst_data_of_pharmacy_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return gst_data_of_pharmacy_data, column_name

    def get_cathlab(self, from_date, to_date, facility_code):
        cathlab_qurey = f""" 

        select a.PERFORMING_FACILITY_ID, a.PATIENT_ID,trunc(a.ORD_DATE_TIME),trunc(a.regn_date_time),a.order_id,
        b.order_catalog_code,b.catalog_desc,b.ORDER_LINE_STATUS,b.ADDED_DATE,b.MODIFIED_BY_ID
        from or_order a,or_order_line b
        where 
        a.order_id = b.order_id and a.order_category = 'TR' and a.order_type_code in ('CATH','PRCH') 
        and b.order_Catalog_code not in ('PRSN000040','PRSN000003','PRAF000012','PRAF000013','PRAF000014','PRCH000001','PRCH000002','PRCH000003','PRSN000006','PRSN000087','PRSN000106','PRSN000107','PRSN000132','PRSN000120','PRSN000104','PRUG000001','PRUG000002','PRUG000003','PRUG000004','PRSN000094','PRSN000001','PRSN000042','PRSN000108','PRBI000001','PRSN000131','PRSN000005','PRSN000128','PRSN000127','PRSN000149','PRSN000150','PRSN000043','PRSN000125','OPGN000253')
        and b.order_line_status = 'RG'
        and a.regn_date_time between :from_date and to_date (:to_date) + 1
        and a.PERFORMING_FACILITY_ID in ({facility_code})
        order by a.patient_id



"""

        self.cursor.execute(cathlab_qurey, [from_date, to_date])
        cathlab_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return cathlab_data, column_name

    def get_form_61(self, facility_code, from_date, to_date):

        form_61_query = f""" 
        
        SELECT a.*,b.APPL_USER_NAME as ADDED_BY_NAME,c.APPL_USER_NAME as MODIFIED_BY
        FROM
            MP_FORM60 a
        LEFT OUTER JOIN
            SM_APPL_USER b
        ON
            a.ADDED_BY_ID = b.APPL_USER_ID
        LEFT OUTER JOIN
            SM_APPL_USER c
        ON 
            a.MODIFIED_BY_ID = c.APPL_USER_ID
        where
            a.FACILITY_ID in ({facility_code})
            and a.ADDED_DATE between :from_date and to_date(:to_date) + 1
        order by a.ADDED_DATE 

"""
        self.cursor.execute(form_61_query, [from_date, to_date])
        form_61_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return form_61_data, column_name

    def get_packages_applied_to_patients(self, facility_code, from_date, to_date):

        packages_applied_to_patients_query = f""" 
        
        select A.PATIENT_ID,d.ENCOUNTER_ID, c.patient_name name,get_age(c.date_of_birth,SYSDATE)  Age,c.sex,A.PACKAGE_CODE code,
        B.LONG_DESC Pack_Name,A.EFF_FROM_DATE,A.EFF_TO_DATE,A.PACKAGE_AMT Pack_Amt,
        (nvl(A.PACKAGE_AMT,0)) - (nvl(A.PACKAGE_VARIANCE,0)) utilised, A.PACKAGE_VARIANCE Variance,a.status,
        a.blng_class_code Class,a.BILL_DOC_NUM,c.contact1_no,c.contact2_no
        from BL_PACKAGE_SUB_HDR a, bl_package b,mp_patient c,bl_package_encounter_dtls d
        where A.PACKAGE_CODE = B.PACKAGE_CODE
        and A.PATIENT_ID = d.PATIENT_ID(+)
        and A.PACKAGE_CODE = d.PACKAGE_CODE(+)
        and a.PACKAGE_SEQ_NO = d.PACKAGE_SEQ_NO(+)
        and A.PATIENT_ID = C.PATIENT_ID and a.status in ('C')
        and A.EFF_FROM_DATE between :from_date and to_date(:to_date) + 1
        and b.OPERATING_FACILITY_ID in ({facility_code})
        order by eff_from_Date

"""
        self.cursor.execute(packages_applied_to_patients_query, [from_date, to_date])
        packages_applied_to_patients_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return packages_applied_to_patients_data, column_name

    def get_gst_data_of_pharmacy_return(self, facility_code):

        gst_data_of_pharmacy_return_qurey = f"""
        
        
            Select * from gst_data_ph_ret
            where OPERATING_FACILITY_ID in ({facility_code})
        
        """

        self.cursor.execute(gst_data_of_pharmacy_return_qurey)
        gst_data_of_pharmacy_return_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return gst_data_of_pharmacy_return_data, column_name

    def get_gst_data_of_ip(self):

        gst_data_of_ip_qurey = """
        
        
            Select * from gst_data_ip
        
        """

        self.cursor.execute(gst_data_of_ip_qurey)
        gst_data_of_ip_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return gst_data_of_ip_data, column_name

    def get_gst_data_of_op(self):

        gst_data_of_op_qurey = """
        
        
            Select * from gst_data_op
        
        """

        self.cursor.execute(gst_data_of_op_qurey)
        gst_data_of_op_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return gst_data_of_op_data, column_name

    def get_item_substitution_report(self, from_date, to_date, facility_code):
        item_substitution_report_qurey = f""" 

        select a.PATIENT_ID, p.PATIENT_NAME  ,d.ORD_DATE_TIME Indent_Date_TIME,b.ORDER_CATALOG_CODE Indent_Item_code,
        b.CATALOG_DESC ItemNameIndented,v1.GENERIC_NAME GenericNameIndented,b.ORDER_QTY, a.DISP_DATE_TIME,c.DISP_DRUG_CODE,u.drug_desc ItemNameDispensed,v.GENERIC_NAME GenericNameDispensed,  c.DISP_QTY
        from ph_disp_hdr a,or_order_line b,ph_disp_dtl c,or_order d,mp_patient p,PH_DRug u,ph_generic_name v,PH_DRug u1,ph_generic_name v1
        where a.ORDER_ID=b.ORDER_ID 
        and b.ORDER_ID =d.order_id  
        and a.DISP_NO=c.DISP_NO 
        and a.PATIENT_ID = p.PATIENT_ID
        and  c.DISP_DRUG_CODE = u.DRUG_CODE 
        and u.GENERIC_ID = v.GENERIC_ID
        and b.ORDER_CATALOG_CODE = u1.DRUG_CODE 
        and u1.GENERIC_ID = v1.GENERIC_ID
        and b.ORDER_CATALOG_CODE <> c.DISP_DRUG_CODE
        and a.FACILITY_ID in ({facility_code})
        and d.ORDERING_FACILITY_ID in ({facility_code})
        and d.ORD_DATE_TIME between :from_date and to_date (:to_date) + 1



"""

        self.cursor.execute(item_substitution_report_qurey, [from_date, to_date])
        item_substitution_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return item_substitution_report_data, column_name

    def get_foc_grn_report(self, facility_code):

        foc_grn_report_qurey = f"""
        
        
        select
        a.GRN_DATE "GRN date",a.STORE_CODE "Store Code",a.ITEM_CODE "Item Code",b.LONG_DESC "Item Description",a.GRN_ITEM_QTY "GRN Qty"
        from xi_trn_grn a,mm_item b
        where a.ITEM_CODE=b.ITEM_CODE
        and a.item_code in (select item_code from st_item)
        and (b.long_desc like '%DISCOUNTED%'
        or b.long_desc like '%Discounted%')
        and a.facility_id in ({facility_code})
        order by a.GRN_DATE desc
        
        """

        self.cursor.execute(foc_grn_report_qurey)
        foc_grn_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return foc_grn_report_data, column_name

    def get_critical_supply_list(self, facility_code):

        critical_supply_list_qurey = f"""
        

            Select a.STORE_CODE "Store",a.ITEM_CODE "IC",b.LONG_DESC "Item Name",sum(a.QTY_ON_HAND-a.COMMITTED_QTY) "Available"
            from st_item_batch a,mm_item b
            where a.ITEM_CODE=b.ITEM_CODE
            and a.ADDED_FACILITY_ID in ({facility_code})
            and a.ITEM_CODE in 	
            ('2000016755',		
            '2000016786',		
            '2000013123',		
            '2000019598',		
            '2000013124',		
            '2000007938',		
            '2000007936',		
            '2000017316',		
            '2000046453',		
            '2000013142',		
            '2000013485',		
            '2000017364',		
            '2000013082',		
            '2000013626',		
            '2000013318',		
            '2000013742',		
            '2000008218',		
            '2000013787',		
            '2000013180',		
            '2000013730',		
            '2000013798',		
            '2000013799',		
            '2000012910',		
            '2000013200',		
            '2000012882',		
            '2000012945',		
            '2000008806',		
            '2000016576',		
            '2000016573',		
            '2000017606',		
            '2000017607',		
            '2000011269',		
            '2000008796',		
            '2000033553',		
            '2000033554',		
            '2000033555',		
            '2000031717',		
            '2000029043',		
            '2000011839',		
            '2000011817',		
            '2000016489',		
            '2000016513',		
            '2000019087',		
            '2000011701',		
            '2000053307',		
            '2000014206',		
            '2000047149',		
            '2000047150',		
            '2000014279',		
            '2000016653',		
            '2000014214',		
            '2000018377',		
            '2000043104',		
            '2000036587',		
            '2000044074',		
            '2000040058',		
            '2000014072',		
            '2000016642',		
            '2000009190',		
            '2000014000',		
            '2000016644',		
            '2000012295',		
            '2000035658',		
            '2000016247',		
            '2000018025',		
            '2000009700',		
            '2000011998',		
            '2000060512',		
            '2000012752',		
            '2000012808',		
            '2000042029',		
            '2000016756',		
            '2000009756',		
            '2000009794',		
            '2000012476',		
            '2000054182',		
            '2000050323',		
            '2000045111',		
            '2000009844',		
            '2000011331',		
            '2000051920',		
            '2000049157',		
            '2000011476',		
            '2000024676',		
            '2000049759',		
            '2000012715',		
            '2000019119',		
            '2000055152',		
            '2000020416',		
            '2000020415',		
            '2000036588',		
            '2000057062',		
            '2000025848',		
            '2000013002',		
            '2000014164',		
            '2000013241',		
            '2000012999',		
            '2000013102',		
            '2000013678',		
            '2000013842',		
            '2000031359',		
            '2000021578',		
            '2000043123',		
            '2000048931',		
            '2000048930',		
            '2000046084',		
            '2000011555',		
            '2000030196',		
            '2000018416',		
            '2000018475',		
            '2000046318',		
            '2000043404',		
            '2000043403',		
            '2000059240',		
            '2000012053',		
            '2000039945',		
            '2000014071',		
            '2000014091',		
            '2000050325',		
            '2000017029',		
            '2000046343',		
            '2000011877',		
            '2000059528',		
            '2000048288',		
            '2000020368',		
            '2000017025',		
            '2000061667',		
            '2000028154',		
            '2000012588',		
            '2000012587',		
            '2000062115',		
            '2000059594',		
            '2000059169',		
            '2000059134',		
            '2000019137',		
            '2000019136',		
            '2000011799',		
            '2000011797',		
            '2000013064',		
            '2000047925',		
            '2000018458',		
            '2000020698',		
            '2000049071',		
            '2000054225',		
            '2000011751',		
            '2000061803',		
            '2000012276',		
            '2000044175',		
            '2000032680',		
            '2000016787',		
            '2000013051',		
            '2000013079',		
            '2000017028',		
            '2000026862',		
            '2000023138',		
            '2000023137',		
            '2000011372',		
            '2000011816',		
            '2000017829',		
            '2000027557',		
            '2000012753',		
            '2000024356',		
            '2000035979',		
            '2000046467',		
            '2000048895',		
            '2000050737',		
            '2000055620',		
            '2000060017',		
            '2000061600',		
            '2000061647',		
            '2000061698',		
            '2000064844',		
            '2000064676',		
            '2000054720',		
            '2000064376',		
            '2000064375',		
            '2000064226',		
            '2000064227',		
            '2000063803',		
            '2000061915',		
            '2000059789',		
            '2000057359',		
            '2000061791',		
            '2000043017',		
            '2000056692',		
            '2000036673',		
            '2000065127',		
            '2000065623',		
            '2000062773'		
            )			
            group by a.STORE_CODE,a.ITEM_CODE,b.LONG_DESC
            order by a.STORE_CODE,a.ITEM_CODE

        
        """

        self.cursor.execute(critical_supply_list_qurey)
        critical_supply_list_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return critical_supply_list_data, column_name

    def get_consignment_grn_report(self, from_date, to_date, facility_code):
        consignment_grn_report_qurey = f""" 


            select h.DOC_TYPE_CODE, h.DOC_NO GRN, h.DOC_DATE GRNDATE,h.DOC_REF,h.STORE_CODE,h.RECEIPT_DATE,
            h.SUPP_CODE,C.LONG_NAME "Supplier Name", d.ITEM_CODE Code,m.long_desc Description, 
            d.ITEM_QTY_NORMAL Quantity,d.GRN_UNIT_COST_IN_PUR_UOM CostPrice,e.SALE_PRICE SalePrice
            from st_grn_hdr h,st_grn_dtl d,st_grn_dtl_exp e,mm_item m,st_item i, AP_SUPPLIER C
            where h.DOC_NO = d.DOC_NO and d.DOC_NO = e.DOC_NO and h.EXT_DOC_NO is null --and d.ITEM_CODE not like '2%'
            and d.ITEM_CODE = m.ITEM_CODE AND TRIM(D.ITEM_CODE) = TRIM(E.ITEM_CODE)
            AND h.SUPP_CODE=C.SUPP_CODE 
            and i.ITEM_CODE=m.ITEM_CODE
            and i.CONSIGNMENT_ITEM_YN = 'Y' 
            and h.FACILITY_ID in ({facility_code})
            and h.DOC_DATE between :from_date and :to_date
            union
            select h.DOC_TYPE_CODE, h.DOC_NO GRN, h.DOC_DATE GRNDATE,h.DOC_REF,h.STORE_CODE,null,
            h.SUPP_CODE,C.LONG_NAME "Supplier Name", d.ITEM_CODE Code,m.long_desc Description, 
            d.ITEM_QTY_NORMAL Quantity,null,null
            from st_rtv_hdr h,st_rtv_dtl d,mm_item m,st_item i, AP_SUPPLIER C
            where h.DOC_NO = d.DOC_NO   --and d.ITEM_CODE not like '2%'
            and d.ITEM_CODE = m.ITEM_CODE 
            AND h.SUPP_CODE=C.SUPP_CODE 
            and i.ITEM_CODE=m.ITEM_CODE
            and i.CONSIGNMENT_ITEM_YN = 'Y' 
            and h.FACILITY_ID in ({facility_code})
            and h.DOC_DATE between :from_date and :to_date
            order by 3 asc


"""

        self.cursor.execute(consignment_grn_report_qurey, [from_date, to_date])
        consignment_grn_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return consignment_grn_report_data, column_name

    def get_revenue_data_of_sl(self, revenue_data_table):

        get_revenue_data_of_sl_qurey = f"""
        
        
            select * from {revenue_data_table}
        
        """

        self.cursor.execute(get_revenue_data_of_sl_qurey)
        get_revenue_data_of_sl_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_revenue_data_of_sl_data, column_name

    def get_discharge_with_mis_report(self, facility_code, from_date, to_date):
        discharge_with_mis_report_qurey = f""" 
        
       select a.PATIENT_ID, b.patient_name, a.VISIT_ADM_DATE_TIME Admission_Time, 
       E.LONG_DESC,a.assign_bed_num,   c.DIS_ADV_DATE_TIME DISCHARGE_REQUEST_TIME,c.EXPECTED_DISCHARGE_DATE ,
       D.BILL_DOC_DATE,a.DISCHARGE_DATE_TIME Bed_Clear_Date_Time,D.BLNG_GRP_ID,  
       f.PRACTITIONER_NAME Treating_Doctor,g.LONG_DESC Speciality,c.ENCOUNTER_ID,
       c.added_by_id,h.appl_user_name,i.AUTHORIZED_DATE_TIME  from pr_encounter a, 
       mp_patient b, ip_discharge_advice c, bl_episode_fin_dtls d,ip_bed_class e,
       am_practitioner f,am_speciality g,sm_appl_user h,CA_ENCNTR_NOTE i  
       where a.PATIENT_ID=b.PATIENT_ID and a.PATIENT_CLASS = 'IP' and a.ENCOUNTER_ID=c.ENCOUNTER_ID 
       and a.ENCOUNTER_ID=d.EPISODE_ID   and a.ENCOUNTER_ID=i.ENCOUNTER_ID  
       and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE   
       and a.ATTEND_PRACTITIONER_ID =f.PRACTITIONER_ID  
       AND a.SPECIALTY_CODE = g.SPECIALITY_CODE  
       and c.added_by_id = h.appl_user_id  and i.note_type= 'DIST' 
       and a.FACILITY_ID in ({facility_code}) and DIS_ADV_STATUS = '0'  
       and trunc(d.bill_doc_date) between :from_date and :to_date  order by BILL_DOC_DATE
                 
      
"""

        self.cursor.execute(discharge_with_mis_report_qurey, [from_date, to_date])
        get_covid_ot_surgery_details_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_covid_ot_surgery_details_data, column_name

    def get_pre_discharge_report(self, from_date, to_date):
        pre_discharge_report_qurey = """ 

        select a.PATIENT_ID, b.patient_name, a.VISIT_ADM_DATE_TIME Admission_Time, E.LONG_DESC,a.assign_bed_num,a.ASSIGN_CARE_LOCN_CODE,
        c.DIS_ADV_DATE_TIME DISCHARGE_REQUEST_TIME, c.EXPECTED_DISCHARGE_DATE ,D.BILL_DOC_DATE,a.DISCHARGE_DATE_TIME Bed_Clear_Date_Time, n.LAST_AMENDED_DATE_TIME,n.AUTHORIZED_DATE_TIME, D.BLNG_GRP_ID,
        f.PRACTITIONER_NAME Treating_Doctor, g.LONG_DESC Speciality, c.ENCOUNTER_ID,c.added_by_id,h.appl_user_name,b.ALT_ID2_NO AS PR_NO,
        B.Contact2_no AS Patient_no,b.Contact3_no as Relative_No from pr_encounter a, mp_patient b, ip_discharge_advice c, bl_episode_fin_dtls d, ip_bed_class e, am_practitioner f, am_speciality g, sm_appl_user h, ca_encntr_note n
        where a.PATIENT_ID = b.PATIENT_ID and a.PATIENT_CLASS = 'IP' and a.ENCOUNTER_ID = c.ENCOUNTER_ID and a.ENCOUNTER_ID = d.EPISODE_ID  and n.PATIENT_ID = c.PATIENT_ID and
        n.ENCOUNTER_ID = c.ENCOUNTER_ID
        and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE
        and a.ATTEND_PRACTITIONER_ID = f.PRACTITIONER_ID
        AND a.SPECIALTY_CODE = g.SPECIALITY_CODE
        and c.added_by_id = h.appl_user_id
       and a.FACILITY_ID = 'KH'
        and a.VISIT_ADM_DATE_TIME between :from_date and to_date(:to_date) + 1
        order by BILL_DOC_DATE


"""

        self.cursor.execute(pre_discharge_report_qurey, [from_date, to_date])
        pre_discharge_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return pre_discharge_report_data, column_name

    def get_pre_discharge_report_2(
        self,
    ):
        pre_discharge_report_2_qurey = """ 

       select a.PATIENT_ID ,a.ENCOUNTER_ID ,initcap(b.short_name) , d.PRACTITIONER_NAME Doctor,e.ASSIGN_CARE_LOCN_CODE,e.ASSIGN_BED_NUM,  DIS_ADV_DATE_TIME , a.ADDED_BY_ID ,c.APPL_USER_NAME    
        from ip_discharge_advice a,mp_patient_mast b, sm_appl_user_vw c,pr_encounter e, am_practitioner d  where A.DIS_ADV_STATUS='0'
        and e.ENCOUNTER_ID=a.ENCOUNTER_ID and e.ATTEND_PRACTITIONER_ID=d.PRACTITIONER_ID and e.CANCEL_REASON_CODE is null and e.DISCHARGE_DATE_TIME is null
        and a.patient_id = b.patient_id   and a.added_by_id = c.APPL_USER_ID   and c.language_id ='en'  
         and a.FACILITY_ID='KH'  order by DIS_ADV_DATE_TIME



"""

        self.cursor.execute(pre_discharge_report_2_qurey)
        pre_discharge_report_2_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return pre_discharge_report_2_data, column_name

    def get_discharge_report_2(self, from_date, to_date):
        discharge_report_2_qurey = """ 

        select a.PATIENT_ID,b.patient_name,a.VISIT_ADM_DATE_TIME as Admission_Time,
        f.LONG_DESC BED_CLASS,a.ASSIGN_BED_NUM as BED_NUMBER,i.LONG_DESC as BED_LOCATION,p.practitioner_name,
        a.PRE_DIS_INITIATED_DATE_TIME as DRS_DISCHARGE_ADVISE_TIME,c.DIS_ADV_DATE_TIME as Nursing_Predischarge,
        max(e.AUTHORIZED_DATE_TIME) as Discharge_Summary_time,
        D.BILL_DOC_DATE,a.DISCHARGE_DATE_TIME as bedClear,D.BLNG_GRP_ID,
        trunc(a.DISCHARGE_DATE_TIME-a.PRE_DIS_INITIATED_DATE_TIME) || ' dy, ' || mod(trunc((a.DISCHARGE_DATE_TIME-a.PRE_DIS_INITIATED_DATE_TIME) * 24), 24)  || ' hr, ' || mod(trunc((a.DISCHARGE_DATE_TIME-a.PRE_DIS_INITIATED_DATE_TIME) * 1440), 60)  || ' mn, ' || mod(trunc((a.DISCHARGE_DATE_TIME-a.PRE_DIS_INITIATED_DATE_TIME) * 86400), 60)  || ' sc ' as BedClearnctoDschrgeAdvs ,
        trunc(c.DIS_ADV_DATE_TIME-a.PRE_DIS_INITIATED_DATE_TIME) || ' dy, ' || mod(trunc((c.DIS_ADV_DATE_TIME-a.PRE_DIS_INITIATED_DATE_TIME) * 24), 24)  || ' hr, ' || mod(trunc((c.DIS_ADV_DATE_TIME-a.PRE_DIS_INITIATED_DATE_TIME) * 1440), 60)  || ' mn, ' || mod(trunc((c.DIS_ADV_DATE_TIME-a.PRE_DIS_INITIATED_DATE_TIME) * 86400), 60)  || ' sc ' as NrsgPredschrgetoDschrgeIntmtn,
        trunc(D.BILL_DOC_DATE-a.PRE_DIS_INITIATED_DATE_TIME) || ' dy, ' || mod(trunc((D.BILL_DOC_DATE-a.PRE_DIS_INITIATED_DATE_TIME) * 24), 24)  || ' hr, ' || mod(trunc((D.BILL_DOC_DATE-a.PRE_DIS_INITIATED_DATE_TIME) * 1440), 60)  || ' mn, ' || mod(trunc((D.BILL_DOC_DATE-a.PRE_DIS_INITIATED_DATE_TIME) * 86400), 60)  || ' sc ' as FinlBilPdTmtoDrsDschrgAdvcTim,
        trunc(a.DISCHARGE_DATE_TIME-D.BILL_DOC_DATE) || ' dy, ' || mod(trunc((a.DISCHARGE_DATE_TIME-D.BILL_DOC_DATE) * 24), 24)  || ' hr, ' || mod(trunc((a.DISCHARGE_DATE_TIME-D.BILL_DOC_DATE) * 1440), 60)  || ' mn, ' || mod(trunc((a.DISCHARGE_DATE_TIME-D.BILL_DOC_DATE) * 86400), 60)  || ' sc ' as BdClrnctoFinalBilPdTim
        from pr_encounter a, mp_patient b,bl_episode_fin_dtls d, ip_nursing_unit i,am_practitioner p,ip_discharge_advice c,ca_encntr_note e,ip_bed_class f
        where a.PATIENT_ID=b.PATIENT_ID and a.ENCOUNTER_ID=c.ENCOUNTER_ID and d.bill_doc_type_code='IPBL' and a.ASSIGN_CARE_LOCN_CODE = i.NURSING_UNIT_CODE and a.ENCOUNTER_ID=d.EPISODE_ID 
        and a.ADMIT_PRACTITIONER_ID=p.PRACTITIONER_ID and e.ENCOUNTER_ID(+) = c.ENCOUNTER_ID and a.ASSIGN_BED_CLASS_CODE   = f.BED_CLASS_CODE and  trunc(a.DISCHARGE_DATE_TIME) between :from_date and :to_date
        and DIS_ADV_STATUS = '1' group by a.PATIENT_ID, b.patient_name,a.PRE_DIS_INITIATED_DATE_TIME, a.VISIT_ADM_DATE_TIME ,f.LONG_DESC,a.ASSIGN_BED_NUM ,i.LONG_DESC,d.BED_BILL_BED_TYPE_CODE,p.practitioner_name ,c.DIS_ADV_DATE_TIME ,D.BILL_DOC_DATE,a.DISCHARGE_DATE_TIME,D.BLNG_GRP_ID order by 1 desc


"""

        self.cursor.execute(discharge_report_2_qurey, [from_date, to_date])
        discharge_report_2_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return discharge_report_2_data, column_name

    def get_revenue_data_of_sl_with_date(self, from_date, to_date, facility_code):
        get_revenue_data_of_sl_with_date_qurey = f""" 
        
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
                AND gl.trx_date between to_date( :from_date, 'dd-mon-yyyy' )
and to_date( :to_date, 'dd-mon-yyyy' ) + (1-1/24/60/60)
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
                AND gl.trx_date between to_date( :from_date, 'dd-mon-yyyy' )
and to_date( :to_date, 'dd-mon-yyyy' ) + (1-1/24/60/60)
                AND gl.main_acc1_code = '222410'
                AND gl.trx_type_code = 'D'
           GROUP BY gl.main_acc1_code, gl.dept_code, gl.trx_type_code) d,
          (SELECT   gl.main_acc1_code, gl.dept_code,
                    DECODE (gl.trx_type_code,
                            'O', SUM (gl.distribution_amt),
                            0
                           ) amount
               FROM bl_gl_distribution gl
              WHERE gl.operating_facility_id in ({facility_code})
                AND gl.trx_date between to_date( :from_date, 'dd-mon-yyyy' )
and to_date( :to_date, 'dd-mon-yyyy' ) + (1-1/24/60/60)
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
    WHERE a.operating_facility_id in ({facility_code})
      AND a.patient_id = gl.patient_id
      AND a.patient_id = b.patient_id
      AND a.trx_doc_ref = gl.trx_doc_ref
      AND a.trx_doc_ref_line_num = gl.trx_doc_ref_line_num
      AND a.trx_doc_ref_seq_num = gl.trx_doc_ref_seq_num
      AND gl.trx_date between to_date( :from_date, 'dd-mon-yyyy' )
and to_date( :to_date, 'dd-mon-yyyy' ) + (1-1/24/60/60)
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
    WHERE a.operating_facility_id in ({facility_code})
      AND a.patient_id = gl.patient_id
      AND a.patient_id = b.patient_id
      AND a.doc_date = gl.trx_date
      AND a.doc_type_code = gl.doc_type
      AND a.doc_num = gl.doc_no
      AND a.overall_disc_amt <> 0
      AND gl.trx_date between to_date( :from_date, 'dd-mon-yyyy' )
and to_date( :to_date, 'dd-mon-yyyy' ) + (1-1/24/60/60)
      AND gl.main_acc1_code IN
             ('409998', '400570', '400575', '400590', '400580', '400600',
              '400610', '400620', '400630', '400640', '400650', '400660',
              '400670', '400680')                             -- ONLY DISCOUNT
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
      AND gl.trx_date between to_date( :from_date, 'dd-mon-yyyy' )
and to_date( :to_date, 'dd-mon-yyyy' ) + (1-1/24/60/60)
      AND gl.main_acc1_code IN ('401220')
      AND gl.trx_type_code = 'O'
      AND gl.dept_code = e.dept_code(+)
      
      
"""

        self.cursor.execute(
            get_revenue_data_of_sl_with_date_qurey, [from_date, to_date]
        )
        get_revenue_data_of_sl_with_date_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_revenue_data_of_sl_with_date_data, column_name

    def get_revenue_jv(self, revenue_data):
        revenue_jv_qurey = f""" 

        Select * from {revenue_data} order by amount desc 

"""

        self.cursor.execute(
            revenue_jv_qurey,
        )
        revenue_jv_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return revenue_jv_data, column_name

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
                AND trunc(gl.trx_date) BETWEEN '{from_date}' and to_date('{to_date}')
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
                AND trunc(gl.trx_date) BETWEEN '{from_date}' and to_date('{to_date}')
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
                AND trunc(gl.trx_date) BETWEEN '{from_date}' and to_date('{to_date}')
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
      AND trunc(gl.trx_date) BETWEEN '{from_date}' and to_date('{to_date}')
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
      AND trunc(gl.trx_date) BETWEEN '{from_date}' and to_date('{to_date}')
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
      AND trunc(gl.trx_date) BETWEEN '{from_date}' and to_date('{to_date}')
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

    def get_collection_report(self, facility_code, from_date, to_date):
        collection_report_query = f""" 
        



        select  TO_CHAR (d.doc_date, 'DD/MM/YY') dat         ,TO_CHAR (d.doc_date, 'HH24:MI:SS') tim
        ,d.doc_type_code||'/'||d.doc_number rec_doc_no          ,d.patient_id UHID
        ,a.SHORT_NAME patient_name          ,d.customer_code          ,c.payer_name
        ,d.doc_amt amount       
        ,d.recpt_type_code          ,d.recpt_nature_code          ,d.recpt_refund_ind
        ,c.slmt_type_code          ,c.slmt_doc_ref_desc "Chq No./Card No."
        ,c.slmt_doc_remarks          ,d.NARRATION          ,c.cash_slmt_flag          ,d.cash_counter_code
        ,d.added_by_id          ,c.cancelled_ind          ,c.bank_code          ,c.bank_branch
        ,d.bill_doc_type_code||'/'||d.bill_doc_number bill_no          ,d.episode_id      
        FROM bl_receipt_refund_dtl c, bl_receipt_refund_hdr d,mp_patient_mast a    
        WHERE d.recpt_nature_code <> 'BI'
        and c.operating_facility_id in ({facility_code}) --
        AND TRUNC (d.doc_date) >= to_date(:from_date)--
        AND TRUNC (d.doc_date) < to_date(:to_date)+1--
        AND c.doc_type_code = d.doc_type_code--
        AND c.doc_number = d.doc_number--
        and d.patient_id = a.patient_id--
        AND NOT EXISTS (
        SELECT 1
        FROM bl_cancelled_bounced_trx f
        WHERE f.doc_type_code = d.doc_type_code
        AND f.doc_number = d.doc_number
        AND trunc(f.cancelled_date)  >= to_date(:from_date)
        AND NVL (d.cancelled_ind, 'N') = 'Y'
        AND trunc(f.cancelled_date)  < to_date(:to_date)+1)
        union all
        select  TO_CHAR (d.doc_date, 'DD/MM/YY') dat         ,TO_CHAR (d.doc_date, 'HH24:MI:SS') tim
        ,d.doc_type_code||'/'||d.doc_number rec_doc_no          ,d.patient_id UHID
        ,a.SHORT_NAME patient_name          ,d.customer_code          ,c.payer_name
        ,d.doc_amt amount       
        ,d.recpt_type_code          ,d.recpt_nature_code          ,d.recpt_refund_ind
        ,c.slmt_type_code          ,c.slmt_doc_ref_desc "Chq No./Card No."
        ,c.slmt_doc_remarks          ,d.NARRATION          ,c.cash_slmt_flag          ,d.cash_counter_code
        ,d.added_by_id          ,c.cancelled_ind          ,c.bank_code          ,c.bank_branch
        ,d.bill_doc_type_code||'/'||d.bill_doc_number bill_no          ,d.episode_id      
        FROM bl_receipt_refund_dtl c, bl_receipt_refund_hdr d,mp_patient_mast a,bl_bill_hdr b         
        WHERE d.recpt_nature_code = 'BI'
        AND b.doc_type_code = d.bill_doc_type_code
        AND b.doc_num = d.bill_doc_number
        and c.operating_facility_id in ({facility_code}) --
        AND TRUNC (d.doc_date) >= to_date(:from_date)--
        AND TRUNC (d.doc_date) < to_date(:to_date)+1--
        --    AND TRUNC (b.doc_date) >= to_date(:from_date)--
        --    AND TRUNC (b.doc_date) < to_date(:to_date)+1--    
        AND c.doc_type_code = d.doc_type_code--
        AND c.doc_number = d.doc_number--
        and d.patient_id = a.patient_id--
        AND NOT EXISTS (
        SELECT 1
        FROM bl_cancelled_bounced_trx f
        WHERE f.doc_type_code = d.doc_type_code
        AND f.doc_number = d.doc_number
        and NVL (d.cancelled_ind, 'N') = 'Y'
        AND trunc(f.cancelled_date)  >= to_date(:from_date)
        AND trunc(f.cancelled_date)  < to_date(:to_date)+1)
        AND NOT EXISTS (
        SELECT 1
        FROM bl_receipt_refund_dtl e
        WHERE e.doc_type_code = d.doc_type_code
        AND e.doc_number =d.doc_number
        AND nvl(e.consolidated_receipt_yn,'N')='Y')                         
        union all
        select  TO_CHAR (d.doc_date, 'DD/MM/YY') dat         ,TO_CHAR (d.doc_date, 'HH24:MI:SS') tim
        ,d.doc_type_code||'/'||d.doc_number rec_doc_no          ,d.patient_id UHID
        ,a.SHORT_NAME patient_name          ,d.customer_code          ,c.payer_name
        ,i.settled_amt amount       
        ,d.recpt_type_code          ,d.recpt_nature_code          ,d.recpt_refund_ind
        ,c.slmt_type_code          ,c.slmt_doc_ref_desc "Chq No./Card No."
        ,c.slmt_doc_remarks          ,d.NARRATION          ,c.cash_slmt_flag          ,d.cash_counter_code
        ,d.added_by_id          ,c.cancelled_ind          ,c.bank_code          ,c.bank_branch
        ,d.bill_doc_type_code||'/'||d.bill_doc_number bill_no          ,d.episode_id      
        FROM bl_receipt_refund_dtl c, bl_receipt_refund_hdr d,mp_patient_mast a,bl_bill_hdr b, bl_bills_for_cons_receipt i          
        WHERE d.recpt_nature_code = 'BI'
        AND b.doc_type_code = i.bill_doc_type_code
        AND b.doc_num = i.bill_doc_num
        AND d.doc_type_code = i.doc_type_code
        AND d.doc_number = i.doc_number
        and c.operating_facility_id in ({facility_code}) --
        AND TRUNC (d.doc_date) >= to_date(:from_date)--
        AND TRUNC (d.doc_date) < to_date(:to_date)+1--
        --    AND TRUNC (b.doc_date) >= to_date(:from_date)--
        --    AND TRUNC (b.doc_date) < to_date(:to_date)+1--    
        AND c.doc_type_code = d.doc_type_code--
        AND c.doc_number = d.doc_number--
        and d.patient_id = a.patient_id--
        AND NOT EXISTS (
        SELECT 1
        FROM bl_cancelled_bounced_trx f
        WHERE f.doc_type_code = d.doc_type_code
        AND f.doc_number =d.doc_number
        and NVL (d.cancelled_ind, 'N') = 'Y'
        AND trunc(f.cancelled_date)  >= to_date(:from_date)
        AND trunc(f.cancelled_date)  < to_date(:to_date)+1)
        AND NOT EXISTS (
        SELECT 1
        FROM bl_receipt_refund_dtl e
        WHERE e.doc_type_code = d.doc_type_code
        AND e.doc_number = d.doc_number
        AND nvl(e.consolidated_receipt_yn,'N')='N')            
        union all
        select  TO_CHAR (f.cancelled_date, 'DD/MM/YY') dat         ,TO_CHAR (f.cancelled_date, 'HH24:MI:SS') tim
        ,d.doc_type_code||'/'||d.doc_number rec_doc_no          ,d.patient_id UHID
        ,a.SHORT_NAME patient_name          ,d.customer_code          ,c.payer_name
        ,-1 * nvl(d.doc_amt,0) amount       
        ,d.recpt_type_code          ,d.recpt_nature_code          ,d.recpt_refund_ind
        ,c.slmt_type_code          ,c.slmt_doc_ref_desc "Chq No./Card No."
        ,c.slmt_doc_remarks          ,d.NARRATION          ,c.cash_slmt_flag          ,d.cash_counter_code
        ,d.added_by_id          ,c.cancelled_ind          ,c.bank_code          ,c.bank_branch
        ,d.bill_doc_type_code||'/'||d.bill_doc_number bill_no          ,d.episode_id      
        FROM bl_receipt_refund_dtl c, bl_receipt_refund_hdr d,mp_patient_mast a  ,bl_cancelled_bounced_trx f  
        WHERE d.recpt_nature_code <> 'BI'
        and c.operating_facility_id in ({facility_code}) --
        AND c.doc_type_code = d.doc_type_code--
        AND c.doc_number = d.doc_number--
        and d.patient_id = a.patient_id--
        and f.doc_type_code = d.doc_type_code
        AND f.doc_number = d.doc_number
        AND trunc(f.cancelled_date)  >= to_date(:from_date)
        AND trunc(f.cancelled_date)  < to_date(:to_date)+1
        AND trunc(f.cancelled_date)  > trunc(d.doc_date)
        AND NVL (d.cancelled_ind, 'N') = 'Y'
        union all
        select  TO_CHAR (f.cancelled_date, 'DD/MM/YY') dat         ,TO_CHAR (f.cancelled_date, 'HH24:MI:SS') tim
        ,d.doc_type_code||'/'||d.doc_number rec_doc_no          ,d.patient_id UHID
        ,a.SHORT_NAME patient_name          ,d.customer_code          ,c.payer_name
        , -1 * nvl(d.doc_amt,0) amount       
        ,d.recpt_type_code          ,d.recpt_nature_code          ,d.recpt_refund_ind
        ,c.slmt_type_code          ,c.slmt_doc_ref_desc "Chq No./Card No."
        ,c.slmt_doc_remarks          ,d.NARRATION          ,c.cash_slmt_flag          ,d.cash_counter_code
        ,d.added_by_id          ,c.cancelled_ind          ,c.bank_code          ,c.bank_branch
        ,d.bill_doc_type_code||'/'||d.bill_doc_number bill_no          ,d.episode_id      
        FROM bl_receipt_refund_dtl c, bl_receipt_refund_hdr d,mp_patient_mast a,bl_bill_hdr b , bl_cancelled_bounced_trx f        
        WHERE d.recpt_nature_code = 'BI'
        AND b.doc_type_code = d.bill_doc_type_code
        AND b.doc_num = d.bill_doc_number
        and c.operating_facility_id in ({facility_code}) --
        AND c.doc_type_code = d.doc_type_code--
        AND c.doc_number = d.doc_number--
        and d.patient_id = a.patient_id--
        and f.doc_type_code = d.doc_type_code
        AND f.doc_number = d.doc_number
        and NVL (d.cancelled_ind, 'N') = 'Y'
        AND trunc(f.cancelled_date)  >= to_date(:from_date)
        AND trunc(f.cancelled_date)  < to_date(:to_date)+1
        AND trunc(f.cancelled_date)  > trunc(d.doc_date)
        AND NOT EXISTS (
        SELECT 1
        FROM bl_receipt_refund_dtl e
        WHERE e.doc_type_code = d.doc_type_code
        AND e.doc_number =d.doc_number
        AND nvl(e.consolidated_receipt_yn,'N')='Y')   
        union all
        select  TO_CHAR (f.cancelled_date, 'DD/MM/YY') dat         ,TO_CHAR (f.cancelled_date, 'HH24:MI:SS') tim
        ,d.doc_type_code||'/'||d.doc_number rec_doc_no          ,d.patient_id UHID
        ,a.SHORT_NAME patient_name          ,d.customer_code          ,c.payer_name
        , -1 * nvl(i.settled_amt,0) amount       
        ,d.recpt_type_code          ,d.recpt_nature_code          ,d.recpt_refund_ind
        ,c.slmt_type_code          ,c.slmt_doc_ref_desc "Chq No./Card No."
        ,c.slmt_doc_remarks          ,d.NARRATION          ,c.cash_slmt_flag          ,d.cash_counter_code
        ,d.added_by_id          ,c.cancelled_ind          ,c.bank_code          ,c.bank_branch
        ,d.bill_doc_type_code||'/'||d.bill_doc_number bill_no          ,d.episode_id      
        FROM bl_receipt_refund_dtl c, bl_receipt_refund_hdr d,mp_patient_mast a,bl_bill_hdr b, bl_bills_for_cons_receipt i ,bl_cancelled_bounced_trx f         
        WHERE d.recpt_nature_code = 'BI'
        AND b.doc_type_code = i.bill_doc_type_code
        AND b.doc_num = i.bill_doc_num
        AND d.doc_type_code = i.doc_type_code
        AND d.doc_number = i.doc_number
        and c.operating_facility_id in ({facility_code}) --
        AND c.doc_type_code = d.doc_type_code--
        AND c.doc_number = d.doc_number--
        and d.patient_id = a.patient_id--
        and f.doc_type_code = d.doc_type_code
        AND f.doc_number =d.doc_number
        and NVL (f.cancelled_ind, 'N') = 'Y'
        AND trunc(f.cancelled_date)  >= to_date(:from_date)
        AND trunc(f.cancelled_date)  < to_date(:to_date)+1
        AND trunc(f.cancelled_date)  > trunc(d.doc_date)
        AND NOT EXISTS (
        SELECT 1
        FROM bl_receipt_refund_dtl e
        WHERE e.doc_type_code = d.doc_type_code
        AND e.doc_number = d.doc_number
        AND nvl(e.consolidated_receipt_yn,'N')='N')                        
        order by dat, tim




"""
        self.cursor.execute(collection_report_query, [from_date, to_date])
        collection_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return collection_report_data, column_name

    def get_discount_report_em(
        self, from_date, to_date, nd_episode_type, facility_code
    ):
        discount_report_em_qurey = f""" 
            
            select a.patient_id,a.episode_id,b.short_name,a.doc_type_code||' / '||a.doc_num BILL_NUM,trunc(a.doc_date) doc_date, 
            trunc(a.added_date),a.gross_amt GROSSAMT,nvl(a.MAN_DISC_AMT,0)+nvl(a.OVERALL_DISC_AMT,0)+nvl(a.serv_disc_amt,0) discount,a.BILL_AMT bill_amount,
            d.APPL_USER_NAME,COALESCE(c.ACTION_REASON_DESC, 'N/A') as ACTION_REASON_DESC,a.BLNG_GRP_ID,a.CUST_CODE,E.LONG_NAME as CUST_DESC
            from bl_bill_hdr a 
            JOIN mp_patient_mast  b ON a.patient_id = b.patient_id 
            LEFT JOIN BL_ACTION_REASON c ON a.reason_code = c.ACTION_REASON_CODE 
            LEFT JOIN SM_APPL_USER D ON a.added_by_id = D.APPL_USER_ID
            LEFT JOIN AR_CUSTOMER E ON a.CUST_CODE = E.CUST_CODE
            where nvl(a.bill_status,'X') != 'C'
            AND a.doc_date  between :from_date and to_date(:to_date)  +1 
            AND a.episode_type in {nd_episode_type}
            --decode(:nd_episode_type, 'A', a.episode_type, :nd_episode_type)
            AND (nvl(a.MAN_DISC_AMT,0)+nvl(a.OVERALL_DISC_AMT,0)+nvl(a.serv_disc_amt,0)) >  0
            AND a.operating_facility_id in ({facility_code})
            order by 1,5


"""

        self.cursor.execute(discount_report_em_qurey, [from_date, to_date])
        discount_report_em_qurey = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return discount_report_em_qurey, column_name

    def get_total_bills_for_period(
        self, from_date, to_date, nd_episode_type, facility_code
    ):
        total_bills_for_period_qurey = f""" 

                        SELECT   BILL_POSTED_FLAG, (a.doc_type_code || '/' || a.doc_num) bill_no,
            TRUNC (a.doc_date) bill_date, a.patient_id,f.PATIENT_NAME, a.episode_id,
            a.CUST_CODE,E.LONG_NAME as CUST_DESC,
            (CASE
            WHEN a.cust_code IS NOT NULL
            THEN 'CR'
            ELSE 'CS'
            END) bill_type, NVL (a.gross_amt, 0) gross_amt,
            NVL (a.serv_disc_amt, 0) serdiscount,
            NVL (a.overall_disc_amt, 0) overall_disc,
            (a.serv_disc_amt + a.overall_disc_amt) tot_discounts,sum(B.ADDL_CHARGE_AMT_IN_CHARGE) addl_charge,
            NVL (a.bill_amt, 0) net_amt, NVL (a.bill_tot_outst_amt, 0) out_amt,b.BLNG_CLASS_CODE
            FROM bl_bill_hdr a,bl_patient_charges_folio b,AR_CUSTOMER E, mp_patient f
            WHERE NVL (a.bill_status, 'A') != 'C'
            AND a.operating_facility_id in ({facility_code})
            and a.operating_Facility_id=b.operating_facility_id
            and a.doc_type_code=b.bill_doc_type_code
            and a.doc_num=b.bill_doc_num
            --     AND NVL (a.gross_amt, 0) != 0
            and nvl(a.bill_amt,0) != 0
            /*AND ( (NVL(a.BILL_POSTED_FLAG,'N')='Y' and :P_POSTED_BILLS='Y' and a.cust_Code is not null
            )
                or (:P_POSTED_BILLS='N' or a.cust_code is null 
                ))*/
            AND a.episode_type in {nd_episode_type}
            AND (   (--:p_cust_code = 'C' AND 
            a.cust_code IS NULL)
            OR (--:p_cust_code = 'R' AND 
            a.cust_code IS NOT NULL)
            OR (  --  :p_cust_code = 'A'  AND 
            (a.cust_code IS NOT NULL OR a.cust_code IS NULL)
            )
            )
            and a.CUST_CODE = E.CUST_CODE (+)
            AND a.doc_date between :from_date and to_date(:to_date)  +1 
            and a.PATIENT_ID = f.PATIENT_ID
            group by 
            a.CUST_CODE, BILL_POSTED_FLAG, (a.doc_type_code || '/' || a.doc_num) ,
            TRUNC (a.doc_date) , a.patient_id, f.PATIENT_NAME,a.episode_id,
            a.gross_amt ,
            a.serv_disc_amt ,
            a.overall_disc_amt ,
            a.bill_amt , a.bill_tot_outst_amt ,
            b.BLNG_CLASS_CODE,
            E.LONG_NAME
            ORDER BY 4      


"""
        self.cursor.execute(
            total_bills_for_period_qurey,
            [from_date, to_date],
        )
        total_bills_for_period_qurey = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return total_bills_for_period_qurey, column_name

    def get_ot(self, from_date, to_date):
        ot_qurey = """ 

        
select a.PERFORMING_FACILITY_ID,a.ord_date_time,d.NURSING_DOC_COMP_TIME,b.order_catalog_code,b.catalog_desc,
--e.TOT_BUS_GEN_AMT,e.TOT_BUS_DISC_AMT,e.TOT_BUS_MAN_DISC_AMT,e.TOT_DEP_PAID_AMT,
e.tot_bus_gen_amt, 
(nvl(e.TOT_BUS_DISC_AMT,0)+ nvl(e.TOT_BUS_MAN_DISC_AMT,0))Discount, 
e.TOT_OUTST_AMT TPA_Approval,
(NVL(e.tot_bus_gen_amt,0))-(nvl(e.TOT_OUTST_AMT,0))-((nvl(e.TOT_BUS_DISC_AMT,0)+ nvl(e.TOT_BUS_MAN_DISC_AMT,0)))Gross_Due,
e.TOT_DEP_PAID_AMT,
--G.DEPOSIT_ADJ_AMT, 
--case G.DEPOSIT_ADJ_AMT 
--when 0 then (NVL(e.tot_bus_gen_amt,0))-(nvl(e.TOT_OUTST_AMT,0))-(nvl(e.TOT_DEP_PAID_AMT,0))-((nvl(e.TOT_BUS_DISC_AMT,0)+nvl(e.TOT_BUS_MAN_DISC_AMT,0))) 
--else (NVL(e.tot_bus_gen_amt,0))-(nvl(e.TOT_OUTST_AMT,0))-(nvl(G.DEPOSIT_ADJ_AMT,0))-((nvl(e.TOT_BUS_DISC_AMT,0)+nvl(e.TOT_BUS_MAN_DISC_AMT,0))) end NetDue_Refund,
e.BLNG_GRP_ID,e.CUST_CODE,e.DISCH_BILL_DOC_NUMBER,
e.DISCHARGE_BILL_DATE_TIME Discharge_Billing,e.DISCHARGE_DATE_TIME Discharge_Nurse,
a.patient_id,c.patient_name
from or_order a,or_order_line b,mp_patient c,OT_POST_OPER_HDR d,bl_episode_fin_dtls e
--,BL_BILL_DCP_DTL_VW g
where a.order_id = d.order_id and b.order_id = d.order_id and a.patient_id = e.patient_id and a.EPISODE_ID = e.EPISODE_ID 
and b.order_Catalog_code not in ('OTM0000109','OTMN000146','OTMN000148','OTMN000149','OTMN000153','OTMN000180','OTMN000181','OTMN000186','OTMP000095','OTMP000447','OTMP000457','OTSM000461') 
--a.patient_ID = 'KH1000149360' and
--c.patient_id = g.patient_id and
--a.episode_id = G.EPISODE_ID and
--e.BILL_DOC_TYPE_CODE = G.DOC_TYPE_CODE and 
--e.BILL_DOC_NUMBER = G.DOC_NUM and
and a.PERFORMING_FACILITY_ID='KH'
and a.order_id = b.order_id and a.order_category = 'OT' and  b.order_line_status = 'CD' and a.patient_id = c.patient_id 
and d.NURSING_DOC_COMP_TIME between :from_date and to_date(:to_date) + 1
order by d.NURSING_DOC_COMP_TIME



"""

        self.cursor.execute(ot_qurey, [from_date, to_date])
        ot_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return ot_data, column_name

    def get_discharge_census(self, from_date, to_date, facility_code):
        discharge_census_qurey = f""" 

        

        SELECT a.FACILITY_ID,  a.patient_id,b.PATIENT_NAME,a.DISCHARGE_DATE_TIME,E.LONG_DESC,a.episode_id
        FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f,mp_country g
        WHERE a.PATIENT_ID=b.PATIENT_ID AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID 
        and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id
        and g.country_code=b.nationality_code
        AND a.patient_class = 'IP'  AND a.SPECIALTY_CODE = d.SPECIALITY_CODE 
        and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE and a.cancel_reason_code is null
        AND a.DISCHARGE_DATE_TIME between :from_date and to_date (:to_date) + 1
        and a.FACILITY_ID in ({facility_code})
        ORDER BY A.ASSIGN_CARE_LOCN_CODE



"""

        self.cursor.execute(discharge_census_qurey, [from_date, to_date])
        discharge_census_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return discharge_census_data, column_name

    def get_gst_ipd(self, facility_code):
        gst_ipd_qurey = f""" 

        
        SELECT OPERATING_FACILITY_ID,EPISODE_TYPE,EPISODE_ID,            
        BILL_DOC_DATE,"BILL NUM", PATIENT_ID,PATNAMEMAST,HSN_SAC_CODE,
        GSTIN,"State Place of Supply",   GROSS_AMT,            SERV_DISC_AMT,         
        MAN_DISC_AMT,          DISC ,        BILL_AMT,
        RULE_CODE,--RULETYPE,GST_TYPE, 
        INCLUDED_IN_PRICE_YN,GOODS_SERVICES,                
        BILL_PRV_DOC_NUMBER,    BILL_PRV_DOC_TYPE_CODE,    ADDED_AT_WS_NO,        
        SUM(ACT_GROSS_AMT-ORG_DISC_AMT) "EXCLUDING TAX",
        sum(ACT_GROSS_AMT),SUM(ADDL_CHARGE_AMT_IN_CHARGE),
        SUM(ORG_NET_CHARGE_AMT),  sum(bill_level_discount_breakup),         
        SUM(ADDL_CHARGE_AMT) CGST_ADDL_CHARGE_AMT,
        SUM(ADDL_CHARGE_AMT) SGST_ADDL_CHARGE_AMT,
        SUM(SERV_QTY) from gst_data_ip
        where (gst_type != 'CGST' or gst_type is null)
        and OPERATING_FACILITY_ID in ({facility_code})
        --(where PATIENT_ID = 'AK1000000109'
        --AND EPISODE_ID = 10000598
        --and bill_doc_type_code = 'AKIPBL'
        --and bill_doc_num = '20000076'
        group By OPERATING_FACILITY_ID,EPISODE_TYPE,EPISODE_ID,            
        BILL_DOC_DATE,"BILL NUM", PATIENT_ID,PATNAMEMAST,HSN_SAC_CODE,
        GSTIN,"State Place of Supply",      
        GROSS_AMT,            
        SERV_DISC_AMT,         
        MAN_DISC_AMT,          
        DISC ,        
        BILL_AMT,
        RULE_CODE,--RULETYPE,GST_TYPE,
        INCLUDED_IN_PRICE_YN,GOODS_SERVICES,                
        BILL_PRV_DOC_NUMBER,    
        BILL_PRV_DOC_TYPE_CODE,    
        ADDED_AT_WS_NO



"""

        self.cursor.execute(gst_ipd_qurey)
        gst_ipd_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return gst_ipd_data, column_name

    def get_bed_charges_occupancy(self, from_date, to_date, facility_code):
        bed_charges_occupancy_qurey = f""" 

        
            SELECT   TO_CHAR (a.service_date, 'DD/MM/YY') serv_date,  c.long_desc serv_desc,
            a.Serv_qty, a.patient_id, b.patient_name, f.PRACTITIONER_NAME, a.episode_id,  a.upd_net_charge_amt
            FROM bl_patient_charges_folio a,  mp_patient b,  bl_blng_serv c,  bl_blng_serv_grp d,  am_dept_lang_vw e,  am_practitioner f,  am_speciality g
            WHERE a.operating_facility_id in {facility_code}
            AND a.blng_serv_code = c.blng_serv_code AND f.primary_SPECIALITY_CODE = g.SPECIALITY_CODE
            AND a.patient_id = b.patient_id AND c.serv_grp_code = d.serv_grp_code AND a.acct_dept_code = e.dept_code
            and a.physician_id = f.PRACTITIONER_ID
            and NVL(A.BILLED_FLAG,'N') = decode(a.episode_type,'O','Y','E','Y','R','Y',NVL(A.BILLED_FLAG,'N'))
            AND e.language_id = 'en'
            AND a.service_date >= :from_date
            AND a.service_date <= TO_DATE (:to_date)+1
            AND A.UPD_NET_CHARGE_AMT !=0
            -- AND a.patient_id = 'KH1000204359'
            -- AND a.blng_serv_code in ('RMDC000001')
            and (a.blng_serv_code like'IC%' or a.blng_serv_code like  'RM%')
            union all
            SELECT   TO_CHAR (a.service_date, 'DD/MM/YY') serv_date,
            c.long_desc serv_desc,
            a.Serv_qty, a.patient_id, b.patient_name, f.PRACTITIONER_NAME, a.episode_id,
            a.upd_net_charge_amt
            FROM bl_patient_charges_folio a,  mp_patient b,  bl_blng_serv c,  bl_blng_serv_grp d, am_dept_lang_vw e, am_practitioner f, am_speciality g
            WHERE a.operating_facility_id in {facility_code}
            AND a.blng_serv_code = c.blng_serv_code
            AND f.primary_SPECIALITY_CODE = g.SPECIALITY_CODE
            AND a.patient_id = b.patient_id
            AND c.serv_grp_code = d.serv_grp_code
            AND a.acct_dept_code = e.dept_code
            and a.physician_id = f.PRACTITIONER_ID
            and NVL(A.BILLED_FLAG,'N') = decode(a.episode_type,'O','Y','E','Y','R','Y',NVL(A.BILLED_FLAG,'N'))
            AND e.language_id = 'en'
            AND a.service_date >=  :from_date  
            AND a.service_date <= TO_DATE (:to_date)+1
            AND A.UPD_NET_CHARGE_AMT =0
            and a.blng_grp_id in ('IPFY','IPFO')
            -- AND a.patient_id = 'KH1000204359'
            -- AND a.blng_serv_code in ('RMDC000001')
            and (a.blng_serv_code like'IC%' or a.blng_serv_code like  'RM%')
      
       
"""

        self.cursor.execute(bed_charges_occupancy_qurey, [from_date, to_date])
        bed_charges_occupancy_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return bed_charges_occupancy_data, column_name

    def get_needle_prick_injury_report(self, facility_code, from_date, to_date):
        needle_prick_injury_report_qurey = f""" 
        
       SELECT  o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID,
       Patient_Name as PatientName,map.SEX,trunc((sysdate - map.DATE_OF_BIRTH) / 365, 0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code,b.remark
       test_code,t.result_text result, 
       map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,
       F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,
       g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state  FROM or_order o,OR_ORDER_LINE L, RL_REQUEST_HEADER A,RL_result_text t, pr_encounter e,
       bl_episode_fin_dtls b, mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g, MP_RES_TOWN h , MP_RES_AREA i, mp_region j
       WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMB000094' and a.PATIENT_ID = map.PATIENT_ID
       and f.POSTAL1_CODE = g.POSTAL_CODE(+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+)
       and i.REGION_CODE = j.REGION_CODE(+) AND A.PATIENT_ID = F.PATIENT_ID
       and t.SPECIMEN_NO(+) = a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+) = o.ORDER_STATUS
       and o.PATIENT_ID = b.PATIENT_ID and o.episode_id = b.episode_id and   o.ORDERING_FACILITY_ID in ({facility_code})
       and e.PATIENT_ID = o.PATIENT_ID and e.EPISODE_ID = o.EPISODE_ID AND o.ORD_DATE_TIME BETWEEN :from_date and to_date(:to_date)+1        
      
"""

        self.cursor.execute(needle_prick_injury_report_qurey, [from_date, to_date])
        needle_prick_injury_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return needle_prick_injury_report_data, column_name

    def get_practo_report(self, facility_code, from_date, to_date):
        practo_report_qurey = f""" 
        
       select a.CONTACT_REASON_CODE,c.CONTACT_REASON,PATIENT_NAME,PATIENT_ID,encounter_id,
       PRACTITIONER_Name,a.ADDED_DATE,a.ADDED_BY_ID,APPT_REMARKS from oa_appt a,am_practitioner p,
       am_contact_reason c where a.PRACTITIONER_ID = p.PRACTITIONER_ID 
       and a.CONTACT_REASON_CODE=c.CONTACT_REASON_CODE and a.ADDED_FACILITY_ID in ({facility_code}) 
       and a.added_date between :from_date and to_date(:to_date)+1 
      
      
"""

        self.cursor.execute(practo_report_qurey, [from_date, to_date])
        practo_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return practo_report_data, column_name

    def get_unbilled_report(self, facility_code):

        get_unbilled_report_qurey = f"""
        
        
            select a.service_date,a.patient_id,b.patient_name,a.episode_id,a.Blng_grp_id,a.store_code, a.serv_item_code,a.serv_item_desc
 ,a.base_rate,a.serv_qty,a.base_charge_amt,a.org_net_charge_amt,a.trx_status,A.BILL_DOC_NUM from bl_patient_charges_folio a,mp_patient b 
 where prt_grp_hdr_code='PROCE' and episode_type ='O'and nvl(a.bill_doc_num,0)=0 and nvl(a.trx_status,'A')='A'  
 and a.service_date between sysdate-30 and (sysdate-1) + 0.99999
 and a.patient_id =b.patient_id and a.OPERATING_FACILITY_ID in ({facility_code})

        """

        self.cursor.execute(get_unbilled_report_qurey)
        get_unbilled_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_unbilled_report_data, column_name

    def get_unbilled_deposit_report(self, facility_code):

        get_unbilled_deposit_report_qurey = f"""
        
        
            select distinct * from gst_data_ph a where a.BILL_DOC_DATE >= ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -30) 
            and a.OPERATING_FACILITY_ID in ({facility_code})

        """

        self.cursor.execute(get_unbilled_deposit_report_qurey)
        get_unbilled_deposit_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_unbilled_deposit_report_data, column_name

    def get_contact_report(self, facility_code, from_date, to_date):
        get_contact_report_qurey = f""" 
        
       select distinct e.practitioner_name,a.PATIENT_CLASS,a.patient_id,b.patient_name, a.SPECIALTY_CODE,VISIT_ADM_DATE_TIME,B.CONTACT1_NO,B.CONTACT2_NO ,b.EMAIL_ID from pr_encounter a,mp_patient b,am_practitioner e 
       where a.patient_id=b.patient_id 
       AND  A.PATIENT_ID=b.PATIENT_ID and  a.FACILITY_ID in ({facility_code})
       and a.ATTEND_PRACTITIONER_ID = e.practitioner_id 
       and a.SPECIALTY_CODE in ('EHC','NEPH','NEUR','UROL','SUON','GYNA','GNMD','MDON','ENDO','HPBL')  and  VISIT_ADM_DATE_TIME between :from_date and to_date(:to_date) + 1
      
      
"""

        self.cursor.execute(get_contact_report_qurey, [from_date, to_date])
        get_contact_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_contact_report_data, column_name

    def get_employees_antibodies_reactive_report(
        self, from_date, to_date, facility_code
    ):
        employees_antibodies_reactive_report_qurey = f""" 
        
       SELECT  o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID,
       Patient_Name as PatientName,map.SEX,trunc((sysdate - map.DATE_OF_BIRTH) / 365, 0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code,
       max(t.NUMERIC_RESULT) Numeric,max(t.RESULT_COMMENT_DESC1) text ,map.ALT_ID2_NO, map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,
       F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,
       g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state
       FROM or_order o,OR_ORDER_LINE L, RL_REQUEST_HEADER A,RL_test_result t, pr_encounter e,
       bl_episode_fin_dtls b, mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g, MP_RES_TOWN h , MP_RES_AREA i, mp_region j
       WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMC00223' and a.PATIENT_ID = map.PATIENT_ID
       and f.POSTAL1_CODE = g.POSTAL_CODE(+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+)
       and i.REGION_CODE = j.REGION_CODE(+) AND A.PATIENT_ID = F.PATIENT_ID
       and t.SPECIMEN_NO(+) = a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+) = o.ORDER_STATUS
       and t.TEST_CODE in ('CUTOFFINDE', 'SARC1')
       and b.BLNG_GRP_ID = 'EMPL'
       and o.PATIENT_ID = b.PATIENT_ID and o.episode_id = b.episode_id
       and e.PATIENT_ID = o.PATIENT_ID and e.EPISODE_ID = o.EPISODE_ID
       AND o.ORD_DATE_TIME BETWEEN :from_date and to_date(:to_date) + 1
       and o.ORDERING_FACILITY_ID in ({facility_code})
       group by o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc ,l.modified_date ,CATALOG_DESC,A.PATIENT_ID,
       Patient_Name ,map.SEX,(sysdate - map.DATE_OF_BIRTH) / 365, 0 , o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code,map.ALT_ID2_NO,
       map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,
       F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4  ,
       g.LONG_DESC , h.LONG_DESC , i.LONG_DESC , j.LONG_DESC
       having max(t.RESULT_COMMENT_DESC1) = 'Reactive'
      
"""

        self.cursor.execute(
            employees_antibodies_reactive_report_qurey,
            [from_date, to_date],
        )
        employees_antibodies_reactive_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return employees_antibodies_reactive_report_data, column_name

    def get_employees_reactive_and_non_pcr_report(self):

        employees_reactive_and_non_pcr_report_qurey = (
            " SELECT  A.PATIENT_ID,Patient_Name as PatientName,map.SEX,trunc((sysdate-map.DATE_OF_BIRTH)/365,0) age ,map.ALT_ID2_NO,map.EMAIL_ID,map.CONTACT1_NO, "
            + " map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO, F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,  "
            + " g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state "
            + " FROM or_order o,OR_ORDER_LINE L,RL_REQUEST_HEADER A,RL_test_result t,pr_encounter e, "
            + " bl_episode_fin_dtls b ,mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,MP_POSTAL_CODE g,MP_RES_TOWN h,MP_RES_AREA i,mp_region j "
            + " WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMC00223' and a.PATIENT_ID = map.PATIENT_ID "
            + " and f.POSTAL1_CODE = g.POSTAL_CODE (+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+) "
            + " and i.REGION_CODE = j.REGION_CODE(+) AND  A.PATIENT_ID=F.PATIENT_ID  "
            + " and t.SPECIMEN_NO(+)=a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+)= o.ORDER_STATUS "
            + " and t.TEST_CODE in ('CUTOFFINDE', 'SARC1') and b.BLNG_GRP_ID = 'EMPL' and  o.PATIENT_ID=b.PATIENT_ID "
            + " and o.episode_id = b.episode_id and e.PATIENT_ID =o.PATIENT_ID and e.EPISODE_ID=o.EPISODE_ID "
            + " group by o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc ,l.modified_date ,CATALOG_DESC,A.PATIENT_ID, "
            + " Patient_Name ,map.SEX,trunc((sysdate-map.DATE_OF_BIRTH)/365,0) , o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code,map.ALT_ID2_NO, "
            + " map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,  "
            + " F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4,g.LONG_DESC ,h.LONG_DESC ,i.LONG_DESC ,j.LONG_DESC "
            + " having max(t.RESULT_COMMENT_DESC1)='Reactive'  "
            + " minus "
            + " SELECT  A.PATIENT_ID,Patient_Name as PatientName,map.SEX,trunc((sysdate-map.DATE_OF_BIRTH)/365,0) age ,map.ALT_ID2_NO, map.EMAIL_ID,map.CONTACT1_NO, "
            + " map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO, F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address , "
            + " g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state "
            + " FROM or_order o,OR_ORDER_LINE L,RL_REQUEST_HEADER A,RL_result_text t,pr_encounter e ,"
            + " bl_episode_fin_dtls b ,mp_patient map,or_order_status_code s,MP_PAT_ADDRESSES F ,MP_POSTAL_CODE g,MP_RES_TOWN h ,MP_RES_AREA i,mp_region j "
            + " WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMB000094' and a.PATIENT_ID = map.PATIENT_ID "
            + " and f.POSTAL1_CODE = g.POSTAL_CODE (+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+) "
            + " and i.REGION_CODE = j.REGION_CODE(+) AND  A.PATIENT_ID=F.PATIENT_ID  "
            + " and t.SPECIMEN_NO(+)=a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+)= o.ORDER_STATUS "
            + " and  o.PATIENT_ID=b.PATIENT_ID and o.episode_id = b.episode_id and e.PATIENT_ID =o.PATIENT_ID and e.EPISODE_ID=o.EPISODE_ID  "
        )

        self.cursor.execute(employees_reactive_and_non_pcr_report_qurey)
        employees_reactive_and_non_pcr_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return employees_reactive_and_non_pcr_report_data, column_name

    def get_employee_covid_test_report(self, facility_code, from_date, to_date):
        employee_covid_test_report_qurey = f""" 
        
        SELECT  o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID,
        Patient_Name as "Patient Name",map.SEX,trunc((sysdate-map.DATE_OF_BIRTH)/365,0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code,b.remark 
        test_code,t.result_text result--,consultant_code,p.practitioner_name 
         ,map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO, 
         F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,  
         g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state  FROM or_order o,OR_ORDER_LINE L,RL_REQUEST_HEADER A,RL_result_text t,pr_encounter e,
        bl_episode_fin_dtls b ,mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g,  MP_RES_TOWN h , MP_RES_AREA i, mp_region j--,am_practitioner p 
        WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE in('LMMB000094','LMMC000227','LMMC000224')
        and a.PATIENT_ID = map.PATIENT_ID
        and f.POSTAL1_CODE = g.POSTAL_CODE (+) 
        and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) 
        and h.RES_AREA_CODE = i.RES_AREA_CODE(+)
        and i.REGION_CODE = j.REGION_CODE(+) 
        AND  A.PATIENT_ID=F.PATIENT_ID 
        and t.SPECIMEN_NO(+)=a.SPECIMEN_NO 
        AND o.ORDER_ID = l.ORDER_ID 
        and s.ORDER_STATUS_CODE(+)= o.ORDER_STATUS
        and b.BLNG_GRP_ID in ('EMPL', 'EMCO')
        and  o.PATIENT_ID=b.PATIENT_ID and o.episode_id = b.episode_id 
        and e.PATIENT_ID =o.PATIENT_ID and e.EPISODE_ID=o.EPISODE_ID
        and o.ORDERING_FACILITY_ID in ({facility_code})
        AND o.ORD_DATE_TIME between :from_date and to_date(:to_date) +1

"""

        self.cursor.execute(employee_covid_test_report_qurey, [from_date, to_date])
        employee_covid_test_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return employee_covid_test_report_data, column_name

    def get_bed_location_report(self, facility_code):

        get_bed_location_report_qurey = f"""
        
        
            select o.patient_class,o.ord_date_time,s.long_desc,c.LONG_DESC,l.modified_date stat_change_date,o.patient_id,
            p.patient_name,i.BED_NUM,i.BED_ALLOCATION_DATE_TIME
            from or_order o,mp_patient p,or_order_status_code s,or_order_line l,or_order_catalog c,bl_order_catalog b,rd_section d,ip_open_encounter i
            where o.PATIENT_ID=p.PATIENT_ID and s.ORDER_STATUS_CODE=o.ORDER_STATUS and o.ORDER_TYPE_CODE=d.order_type_code
            and o.ORDER_ID=l.ORDER_ID and l.ORDER_CATALOG_CODE=c.ORDER_CATALOG_CODE and b.ORDER_CATALOG_CODE = c.ORDER_CATALOG_CODE
            and o.ENCOUNTER_ID=i.ENCOUNTER_ID and o.PATIENT_ID=i.PATIENT_ID and o.ORDERING_FACILITY_ID in ({facility_code})

        """

        self.cursor.execute(get_bed_location_report_qurey)
        get_bed_location_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_bed_location_report_data, column_name

    def get_home_visit_report(self, facility_code, from_date, to_date):
        home_visit_report_qurey = f""" 
        
       select DISTINCT a.patient_id,a.episode_id,ALL_DOC_TYPE_CODE BILL_TYPE,
       ALL_DOC_NUM Bill_NUM,b.ADDED_BY_ID,A.ADDED_DATE,C.aPPL_USER_NAME,e.VISIT_ADM_TYPE
       from bl_patient_ledger a,bl_bill_hdr b, SM_aPPL_USER C,pr_encounter e
       where b.doc_num = ALL_DOC_NUM  and b.doc_type_code = ALL_DOC_TYPE_CODE
       AND b.ADDED_BY_ID = C.APPL_USER_ID  and a.OPERATING_FACILITY_ID in ({facility_code}) and a.PATIENT_ID =e.PATIENT_ID
       and a.EPISODE_ID = e.EPISODE_ID and a.EPISODE_TYPE = 'O' and e.VISIT_ADM_TYPE = 'HM'
       and  a.patient_id = b.patient_id  AND B.ADDED_DATE between :from_date and to_date(:to_date)+1
      
"""

        self.cursor.execute(home_visit_report_qurey, [from_date, to_date])
        home_visit_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return home_visit_report_data, column_name

    def get_cco_billing_count_reports(self, from_date):

        get_cco_billing_count_reports_qurey = """
        
        
            select count(*),added_by_id,trunc(ADDED_DATE) 
from bl_bill_hdr where trunc(ADDED_DATE) >= to_date(:to_date, 'dd/mm/yyyy') 
and DOC_TYPE_CODE = 'OPBL' group by added_by_id,trunc(ADDED_DATE)

        """

        self.cursor.execute(get_cco_billing_count_reports_qurey, [from_date])
        get_cco_billing_count_reports_data = self.cursor.fetchall()

        # only print head
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_cco_billing_count_reports_data, column_name

    def get_total_number_of_online_consultation_by_doctors(
        self, facility_code, from_date, to_date
    ):
        total_number_of_online_consultation_by_doctors_qurey = f""" 
        
       SELECT nvl (m.PRACTITIONER_NAME, ' Grand Total :') practitioner_name , count(1) as total
       FROM bl_patient_charges_folio a,mp_patient_mast b,bl_blng_serv c,BL_PACKAGE_ENCOUNTER_DTLS e,bl_package p ,am_practitioner m
       WHERE a.operating_facility_id in ({facility_code}) AND a.patient_id = b.patient_id AND a.blng_serv_code = c.blng_serv_code
       and NVL(A.BILLED_FLAG,'N') = decode(a.episode_type,'O','Y','E','Y','R','Y',NVL(A.BILLED_FLAG,'N'))
       AND a.service_date  between :from_date and to_date(:to_date) + 1  and e.OPERATING_FACILITY_ID = p.OPERATING_FACILITY_ID(+)
       and a.blng_serv_code in ('CNOP000029','CNOP000040','CNOP000041','CNOP000044') and a.ENCOUNTER_ID=e.ENCOUNTER_ID(+)
       and a.PACKAGE_SEQ_NO = e.PACKAGE_SEQ_NO(+) and a.OPERATING_FACILITY_ID=e.OPERATING_FACILITY_ID(+) and e.PACKAGE_CODE=p.PACKAGE_CODE(+) 
       AND a.PHYSICIAN_ID=m.PRACTITIONER_ID  group by grouping sets((),(m.PRACTITIONER_NAME))
      
"""

        self.cursor.execute(
            total_number_of_online_consultation_by_doctors_qurey,
            [from_date, to_date],
        )
        total_number_of_online_consultation_by_doctors_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return total_number_of_online_consultation_by_doctors_data, column_name

    def get_tpa_current_inpatients(self):
        tpa_current_inpatients_qurey = """ 
        
        select a.PATIENT_ID, b.patient_name, a.ADMISSION_DATE_TIME Admission_Time, E.LONG_DESC,a.BED_NUM ,c.DIS_ADV_DATE_TIME DISCHARGE_REQUEST_TIME,
        n.AUTHORIZED_DATE_TIME,D.BILL_DOC_DATE,D.BLNG_GRP_ID,
        f.PRACTITIONER_NAME Treating_Doctor
        from ip_open_encounter a, mp_patient b, ip_discharge_advice c ,
        bl_episode_fin_dtls d, ip_bed_class e, am_practitioner f, am_speciality g, sm_appl_user h, ca_encntr_note n
        where a.PATIENT_ID = b.PATIENT_ID and 
        a.ENCOUNTER_ID = c.ENCOUNTER_ID and 
        a.ENCOUNTER_ID = d.EPISODE_ID and 
        n.PATIENT_ID = c.PATIENT_ID and 
        n.ENCOUNTER_ID = c.ENCOUNTER_ID and 
        A.BED_CLASS_CODE = E.BED_CLASS_CODE 
        and a.ATTEND_PRACTITIONER_ID = f.PRACTITIONER_ID 
        AND a.SPECIALTY_CODE = g.SPECIALITY_CODE 
        and a.FACILITY_ID = 'KH'
        and c.added_by_id = h.appl_user_id
        and c.DIS_ADV_DATE_TIME > To_Date(CURRENT_DATE)
        and d.BLNG_GRP_ID !='CASH'
        order by DIS_ADV_DATE_TIME desc
      
"""

        self.cursor.execute(tpa_current_inpatients_qurey)
        tpa_current_inpatients_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return tpa_current_inpatients_data, column_name

    def get_tpa_cover_letter(self, from_date, to_date):
        gettpa_cover_letter_query = """
        
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
            AND i.doc_date between :from_date and to_date(:to_date) + 1
            --and a.patient_id = 'KH1000846238'
            and f.OPERATING_FACILITY_ID = 'KH'
            and I.BILL_STATUS is null
            order by doc_date


"""
        self.cursor.execute(gettpa_cover_letter_query, [from_date, to_date])
        gettpa_cover_letter_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return gettpa_cover_letter_data, column_name

    def get_total_number_of_ip_patients_by_doctors(self, from_date, to_date):
        gettotal_number_of_ip_patients_by_doctors_query = """
        
        select nvl (c.PRACTITIONER_NAME, ' Grand Total :')  Doctor,Count(a.patient_id) Total_patient from pr_encounter a, mp_patient b,am_practitioner c,
        am_speciality e  where a.PATIENT_ID=b.PATIENT_ID and  a.SPECIALTY_CODE = e.SPECIALITY_CODE and a.PATIENT_CLASS = 'IP'
        and a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID and a.VISIT_ADM_DATE_TIME between :from_date and to_date(:to_date)+1
        and a.cancel_reason_code is null and a.facility_id = 'KH' group by grouping sets((),(C.PRACTITIONER_NAME))
        order by c.PRACTITIONER_NAME,2 asc



"""
        self.cursor.execute(
            gettotal_number_of_ip_patients_by_doctors_query, [from_date, to_date]
        )
        gettotal_number_of_ip_patients_by_doctors_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return gettotal_number_of_ip_patients_by_doctors_data, column_name

    def get_total_number_of_op_patients_by_doctors(self, from_date, to_date):
        get_total_number_of_op_patients_by_doctors_query = """
        
        select  nvl (c.PRACTITIONER_NAME, 'Grand Total :') Doctor,Count(a.patient_id) Total_patient  from pr_encounter a, mp_patient b,am_practitioner c,am_speciality e
        where a.PATIENT_ID=b.PATIENT_ID and  a.SPECIALTY_CODE = e.SPECIALITY_CODE and a.PATIENT_CLASS in ('OP','EM')
        and a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID and A.VISIT_ADM_TYPE in ('RV','FV','SD','FU','FF')
        and a.ASSIGN_CARE_LOCN_CODE not in ('DIAG') and TRUNC(a.VISIT_ADM_DATE_TIME) between :from_date and :to_date
        and a.cancel_reason_code is null  group by grouping sets((),(C.PRACTITIONER_NAME))
        order by c.PRACTITIONER_NAME,2 asc


"""
        self.cursor.execute(
            get_total_number_of_op_patients_by_doctors_query, [from_date, to_date]
        )
        get_total_number_of_op_patients_by_doctors_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_total_number_of_op_patients_by_doctors_data, column_name

    def get_opd_changes_report(self, facility_code, from_date, to_date):
        opd_changes_report_qurey = f""" 
        
       select to_char(o.appt_slab_from_time,'HH24:MI:SS') from_time , to_char(o.appt_slab_to_time,'HH24:MI:SS')   to_time,o.appt_ref_no,
       o.clinic_code,o.practitioner_id,to_char(o.appt_date,'dd/mm/yyyy') new_Appt_date,to_char(o.appt_date,'dd/mm/yyyy') i_Appt_date,
       to_char(o.appt_date,'Day') appt_day1,o.APPT_TYPE_CODE visit_type_ind,a.PRACTITIONER_NAME,c.LONG_DESC clinic_name,o.patient_id,
       o.patient_name,o.res_tel_no,o.oth_contact_no
       from oa_appt o,am_practitioner a,op_clinic c where o.PRACTITIONER_ID =a.PRACTITIONER_ID(+) and o.CLINIC_CODE=c.CLINIC_CODE(+) 
       and o.appt_date between :from_date and :to_date and o.patient_id is null and oth_contact_no is null and res_TEL_No not like '__________'
       and appt_remarks is null and o.CONTACT_REASON_CODE <> 11 and o.clinic_code <> 'PRAD' and o.FACILITY_ID in ({facility_code})
      
"""

        self.cursor.execute(opd_changes_report_qurey, [from_date, to_date])
        opd_changes_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return opd_changes_report_data, column_name

    def get_ehc_conversion_report(self, facility_code, from_date, to_date):
        ehc_conversion_report_qurey = f""" 
        
       select distinct pack.patient_id,pack.NAME_PREFIX,pack.FIRST_NAME,pack.SECOND_NAME,pack.FAMILY_NAME, pack.ADDED_DATE,pack.LONG_DESC,
       B.LONG_DESC Service_name,a.blng_serv_code,a.trx_date,T.PRACTITIONER_NAME,T.primary_speciality_code,a.serv_item_desc,A.ORG_GROSS_CHARGE_AMT
       from bl_patient_charges_folio a,bl_blng_serv b,am_practitioner t,(select E.patient_id,E.EPISODE_ID,M.NAME_PREFIX,M.FIRST_NAME,M.SECOND_NAME,
       M.FAMILY_NAME,H.ADDED_DATE,P.LONG_DESC from mp_patient M,pr_encounter E,bl_package_sub_hdr h,bl_package p,bl_package_encounter_dtls f
       where e.specialty_code ='EHC' and M.PATIENT_ID =E.PATIENT_ID and H.PACKAGE_CODE=P.PACKAGE_CODE and f.PACKAGE_SEQ_NO = h.PACKAGE_SEQ_NO
       and f.PACKAGE_CODE = h.PACKAGE_CODE and f.PATIENT_ID =h.PATIENT_ID and f.ENCOUNTER_ID = e.EPISODE_ID and h.status='C' and p.OPERATING_FACILITY_ID in ({facility_code})
    and h.added_date between :from_date and :to_date)pack where pack.patient_id=a.patient_id and NVL(trx_STATUS,'X')<>'C'
    and a.trx_date >pack.added_date and A.BLNG_SERV_CODE =B.BLNG_SERV_CODE(+) and A.PHYSICIAN_ID=T.PRACTITIONER_ID(+)
    and a.blng_Serv_code not in ('HSPK000001') and pack.added_date between :from_date and :to_date
"""

        self.cursor.execute(
            ehc_conversion_report_qurey,
            [from_date, to_date, from_date, to_date],
        )
        ehc_conversion_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return ehc_conversion_report_data, column_name

    def get_ehc_package_range_report(self, facility_code, from_date, to_date):
        ehc_package_range_report_qurey = f""" 
        
       select distinct  P.LONG_DESC, H.ADDED_DATE, E.patient_id, M.NAME_PREFIX, M.FIRST_NAME, M.SECOND_NAME, M.FAMILY_NAME, M.EMAIL_ID,f.CUST_CODE, c.LONG_NAME ,h.PACKAGE_AMT
       from mp_patient M,pr_encounter E,bl_patient_charges_folio f,bl_package_sub_hdr h,bl_package p,ar_customer c
       where e.specialty_code ='EHC' and M.PATIENT_ID =E.PATIENT_ID and E.EPISODE_ID=F.EPISODE_ID and e.FACILITY_ID in ({facility_code})
       and p.ADDED_FACILITY_ID = 'KH' and F.PACKAGE_SEQ_NO=H.PACKAGE_SEQ_NO and H.PACKAGE_CODE=P.PACKAGE_CODE  and c.cust_code(+) = f.CUST_CODE and h.status='C'
       and h.added_date between :from_date and to_date(:to_date)+1 and p.OP_YN='Y' order by  H.ADDED_DATE
"""

        self.cursor.execute(ehc_package_range_report_qurey, [from_date, to_date])
        ehc_package_range_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return ehc_package_range_report_data, column_name

    def get_error_report(self, from_date, to_date):
        get_error_report_query = """
        
        SELECT a.patient_id,b.PATIENT_NAME,b.REGN_DATE,get_age(b.date_of_birth,SYSDATE) Age,b.SEX Gender,a.VISIT_ADM_DATE_TIME Admission_Date,
        A.ASSIGN_CARE_LOCN_CODE,A.ASSIGN_BED_CLASS_CODE,E.LONG_DESC,a.ASSIGN_BED_NUM Bed_Num,c.PRACTITIONER_NAME Treating_Doctor,d.LONG_DESC Speciality,
        A.ASSIGN_BED_CLASS_CODE, f.BLNG_GRP_ID,f.cust_code,f.remark,m.long_name,f.NON_INS_BLNG_GRP_ID,b.ALT_ID2_NO prno,f.TOT_UNADJ_DEP_AMT deposit,
        p.LONG_DESC postal_code 
        FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f ,mp_country m,
        mp_pat_addresses k,mp_postal_code p 
        WHERE a.PATIENT_ID=b.PATIENT_ID AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID and a.patient_id=k.patient_id(+)
        and k.POSTAL2_CODE = p.POSTAL_CODE(+) and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id AND a.patient_class = 'IP'
        AND a.SPECIALTY_CODE = d.SPECIALITY_CODE and m.COUNTRY_CODE=b.NATIONALITY_CODE and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE
        and a.cancel_reason_code is null AND a.VISIT_ADM_DATE_TIME between :from_date and to_date(:to_date)+1 and a.ADDED_FACILITY_ID = 'KH' ORDER BY A.ASSIGN_CARE_LOCN_CODE


"""
        self.cursor.execute(get_error_report_query, [from_date, to_date])
        get_error_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_error_report_data, column_name

    def get_ot_query_report(self, from_date, to_date):
        get_ot_query_report_query = """
        
        select a.patient_id,b.patient_name,get_age(b.date_of_birth,SYSDATE) Age,b.sex,b.CONTACT2_NO,C.CATALOG_DESC,
a.pref_surg_date, D.PRACTITIONER_NAME,E.LONG_DESC,a.added_date,dbms_lob.substr(f.ORDER_COMMENT,5000,1)
from ot_pending_order a,mp_patient b, or_order_line c,AM_PRACTITIONER d,AM_SPECIALITY e,or_order_comment f
where a.patient_id = b.patient_id and a.order_id = c.order_id and A.PHYSICIAN_ID = D.PRACTITIONER_ID and a.order_id = f.order_id(+) and
D.PRIMARY_SPECIALITY_CODE = E.SPECIALITY_CODE and PREF_SURG_DATE between :from_date and :to_date order by PRACTITIONER_NAME



"""
        self.cursor.execute(get_ot_query_report_query, [from_date, to_date])
        get_ot_query_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_ot_query_report_data, column_name

    def get_outreach_cancer_hospital(self, from_date, to_date):
        outreach_cancer_hospital_query = """
        
        select  m.PATIENT_NAME,a.patient_id,b.PHYSICIAN_ID,e.REFERRAL_ID,r.FROM_PRACT_NAME
          ,p.PRACTITIONER_NAME,b.DOC_NUM,b.DOC_TYPE_CODE, b.DOC_DATE , a.SERV_ITEM_DESC,s.LONG_DESC, b.GROSS_AMT Bill_Gross_AMT,b.SERV_DISC_AMT BILL_DISC_AMT,b.BILL_AMT ,a.ORG_GROSS_CHARGE_AMT Service_AMT,
          a.ORG_DISC_AMT Service_disc_amt,a.ORG_NET_CHARGE_AMT SERVICE_NET_AMT,  C.aPPL_USER_NAME,a.ADDED_FACILITY_ID
        from bl_patient_charges_folio a,bl_bill_hdr b, SM_aPPL_USER C,mp_patient m,am_practitioner p,pr_encounter e, pr_referral_register r,bl_blng_serv s
          where b.doc_num = a.BILL_DOC_NUM  and b.doc_type_code = a.BILL_DOC_TYPE_CODE
          and a.BLNG_SERV_CODE= s.BLNG_SERV_CODE(+)
          and a.PATIENT_ID = e.PATIENT_ID
          and e.PATIENT_ID=r.PATIENT_ID(+)
          and e.REFERRAL_ID = r.REFERRAL_ID(+)
          and a.EPISODE_ID = e.EPISODE_ID
          AND b.ADDED_BY_ID = C.APPL_USER_ID(+) 
          and  m.PATIENT_ID = a.PATIENT_ID 
          and a.patient_id = b.patient_id 
          and a.PHYSICIAN_ID = p.PRACTITIONER_ID(+)
          and NVL(a.TRX_STATUS,'X')<>'C' 
          and a.ORG_GROSS_CHARGE_AMT <>0
        and trunc(a.TRX_DATE)  between :from_date and :to_date
        and a.ADDED_FACILITY_ID in ('AK','GO','SL')



"""
        self.cursor.execute(outreach_cancer_hospital_query, [from_date, to_date])
        outreach_cancer_hospital_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return outreach_cancer_hospital_data, column_name

    def get_gipsa_report(self):

        gipsa_report_qurey = """
        
        
            select a.order_id,d.NURSING_DOC_COMP_TIME,b.order_catalog_code,b.catalog_desc, f.LONG_DESC,
            a.patient_id,c.patient_name, c.DATE_OF_BIRTH, c.SEX,g.PRACTITIONER_NAME,k.BLNG_GRP_ID,k.NON_INS_BLNG_GRP_ID,k.CUST_CODE,l.PACKAGE_SEQ_NO,  l.PACKAGE_CODE,n.LONG_DESC
            from or_order a , or_order_line b , mp_patient c , OT_POST_OPER_HDR d , OT_OPER_MAST e, OT_OPER_TYPE f, am_practitioner g,ip_open_encounter i,
            bl_episode_fin_dtls k,bl_package_sub_hdr l,bl_package_encounter_dtls m,bl_package n
            where a.order_id = d.order_id and b.order_id = d.order_id and b.order_catalog_code =e.ORDER_CATALOG_CODE and e.OPER_TYPE_CODE = f.OPER_TYPE
            and a.order_id = b.order_id and a.order_category = 'OT' and  b.order_line_status = 'CD' and a.patient_id = c.patient_id and c.PATIENT_ID = i.PATIENT_ID
            and d.surgeon_code = g.PRACTITIONER_ID(+) and i.ENCOUNTER_ID =d.ENCOUNTER_ID and k.ENCOUNTER_ID = i.ENCOUNTER_ID and k.PATIENT_ID = i.PATIENT_ID and
            i.PATIENT_ID=m.PATIENT_ID(+) and i.ENCOUNTER_ID=m.ENCOUNTER_ID(+) and l.PATIENT_ID(+)=m.PATIENT_ID and l.PACKAGE_SEQ_NO(+)=m.PACKAGE_SEQ_NO and
            l.PACKAGE_CODE=n.PACKAGE_CODE(+)

        """

        self.cursor.execute(gipsa_report_qurey)
        gipsa_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return gipsa_report_data, column_name

    def get_precision_patient_opd_and_online_consultation_list_report(
        self, from_date, to_date
    ):
        get_precision_patient_opd_and_online_consultation_list_report_query = """
        
        select distinct m.patient_id,m.patient_NAME,a.SERV_ITEM_DESC,a.trx_date,m.CONTACT1_NO,m.CONTACT2_NO ,m.EMAIL_ID,
        g.addr1_line1 || ' ' || g.addr1_line2 || ' ' || g.addr1_line3 || ' ' || g.addr1_line4 Address
        from bl_patient_charges_folio a,bl_blng_serv b,mp_patient M,MP_PAT_ADDRESSES g
        where a.patient_id=m.patient_id and m.patient_id=g.patient_id and a.OPERATING_FACILITY_ID = 'KH'
        and NVL(trx_STATUS,'X')<>'C' and A.BLNG_SERV_CODE =B.BLNG_SERV_CODE(+) and a.blng_Serv_code = 'CNOP000047' and a.trx_date between :from_date and :to_date


"""
        self.cursor.execute(
            get_precision_patient_opd_and_online_consultation_list_report_query,
            [from_date, to_date],
        )
        get_precision_patient_opd_and_online_consultation_list_report_data = (
            self.cursor.fetchall()
        )

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return (
            get_precision_patient_opd_and_online_consultation_list_report_data,
            column_name,
        )

    def get_appointment_details_by_call_center_report(self, from_date, to_date):
        get_appointment_details_by_call_center_report_query = """
        
        select APPT_date,a.APPT_REF_NO,a.CLINIC_CODE,b.PRACTITIONER_NAME,a.APPT_SLAB_FROM_TIME,a.APPT_SLAB_TO_TIME,a.PATIENT_ID,a.PATIENT_NAME,a.RES_TEL_NO,
        a.OTH_CONTACT_NO,a.OVERBOOKED_YN,a.APPT_REMARKS,a.NO_OF_SLOTS,a.REASON_FOR_TRANSFER,a.FORCED_APPT_YN,a.TRANSFERRED_APPT_YN,a.ADDED_BY_ID,a.MODIFIED_BY_ID
        from OA_APPT a,AM_PRACTITIONER b,sm_appl_user c where a.PRACTITIONER_ID = b.PRACTITIONER_ID and a.ADDED_BY_ID = c.APPL_USER_ID and a.MODIFIED_BY_ID = c.APPL_USER_ID
        and to_date(APPT_DATE) between :from_date and :to_date and a.FACILITY_ID = 'KH' 


"""
        self.cursor.execute(
            get_appointment_details_by_call_center_report_query, [from_date, to_date]
        )
        get_appointment_details_by_call_center_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_appointment_details_by_call_center_report_data, column_name

    def get_trf_report(self, from_date, to_date):
        get_trf_report_query = """
        
        select PATIENT_ID,PATIENT_NAME,GENDER,FROM_NURSING_UNIT_SHORT_DESC,FROM_BED_NO,PRACTITIONER_NAME,TFR_REQ_DATE_TIME,NURSING_UNIT_SHORT_DESC,TFR_REQ_STATUS_DESC from IP_TRANSFER_REQUEST_VW where TFR_REQ_TYPE ='RT' AND TFR_REQ_DATE_TIME between to_date(:from_date) and to_date(:to_date) ORDER BY TFR_REQ_DATE_TIME DESC


"""
        self.cursor.execute(get_trf_report_query, [from_date, to_date])
        get_trf_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_trf_report_data, column_name

    def get_current_inpatients_clinical_admin(self, billing_group):
        if billing_group == "dietitian":
            current_inpatients_clinical_admin_qurey = """
            
                select a.PATIENT_ID, b.patient_name, a.ADMISSION_DATE_TIME Admission_Time, E.LONG_DESC,a.BED_NUM ,c.DIS_ADV_DATE_TIME DISCHARGE_REQUEST_TIME,
                f.PRACTITIONER_NAME Treating_Doctor,  g.LONG_DESC Speciality,
                c.EXPECTED_DISCHARGE_DATE ,--n.LAST_AMENDED_DATE_TIME,
                B.Contact2_no AS Patient_no,b.Contact3_no as Relative_Phone_No,b.EMAIL_ID
                from ip_open_encounter a, mp_patient b, ip_discharge_advice c ,
                bl_episode_fin_dtls d, ip_bed_class e, am_practitioner f, am_speciality g, sm_appl_user h--, ca_encntr_note n
                where a.PATIENT_ID = b.PATIENT_ID and 
                a.ENCOUNTER_ID = c.ENCOUNTER_ID and 
                a.ENCOUNTER_ID = d.EPISODE_ID and 
                --n.PATIENT_ID = c.PATIENT_ID and 
                --n.ENCOUNTER_ID = c.ENCOUNTER_ID and 
                A.BED_CLASS_CODE = E.BED_CLASS_CODE 
                and a.ATTEND_PRACTITIONER_ID = f.PRACTITIONER_ID 
                AND a.SPECIALTY_CODE = g.SPECIALITY_CODE 
                and a.FACILITY_ID = 'KH'
                and c.CANCELLATION_DATE_TIME is null 
                and c.added_by_id = h.appl_user_id
                order by BILL_DOC_DATE
"""
            self.cursor.execute(current_inpatients_clinical_admin_qurey)

        else:
            current_inpatients_clinical_admin_qurey = """
        
        
                    select a.PATIENT_ID, b.patient_name, a.ADMISSION_DATE_TIME Admission_Time, E.LONG_DESC,a.BED_NUM ,c.DIS_ADV_DATE_TIME DISCHARGE_REQUEST_TIME,
                    f.PRACTITIONER_NAME Treating_Doctor,  g.LONG_DESC Speciality,
                    c.EXPECTED_DISCHARGE_DATE ,n.LAST_AMENDED_DATE_TIME,B.Contact2_no AS Patient_no,b.Contact3_no as Relative_Phone_No,b.EMAIL_ID,
                    n.AUTHORIZED_DATE_TIME,D.BILL_DOC_DATE,d.DISCHARGE_DATE_TIME Bed_Clear_Date_Time, D.BLNG_GRP_ID,b.ALT_ID2_NO AS PR_NO ,
                    c.ENCOUNTER_ID,c.added_by_id ,
                    h.appl_user_name ,a.NURSING_UNIT_CODE
                    from ip_open_encounter a, mp_patient b, ip_discharge_advice c ,
                    bl_episode_fin_dtls d, ip_bed_class e, am_practitioner f, am_speciality g, sm_appl_user h, ca_encntr_note n
                    where a.PATIENT_ID = b.PATIENT_ID and 
                    a.ENCOUNTER_ID = c.ENCOUNTER_ID and 
                    a.ENCOUNTER_ID = d.EPISODE_ID and 
                    n.PATIENT_ID = c.PATIENT_ID and 
                    n.ENCOUNTER_ID = c.ENCOUNTER_ID and 
                    A.BED_CLASS_CODE = E.BED_CLASS_CODE 
                    and a.ATTEND_PRACTITIONER_ID = f.PRACTITIONER_ID 
                    AND a.SPECIALTY_CODE = g.SPECIALITY_CODE 
                    and a.FACILITY_ID = 'KH'
                    and c.added_by_id = h.appl_user_id
                    and d.BLNG_GRP_ID !=:billing_group
                    order by BILL_DOC_DATE
            
        """

            self.cursor.execute(
                current_inpatients_clinical_admin_qurey, [billing_group]
            )

        current_inpatients_clinical_admin = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return current_inpatients_clinical_admin, column_name

    def get_check_patient_registration_date(self, uhid):

        check_patient_registration_date_qurey = """
        
        Select PATIENT_ID, REGN_DATE,ADDED_DATE from MP_PATIENT where PATIENT_ID =:uhid


        """

        self.cursor.execute(check_patient_registration_date_qurey, [uhid])
        check_patient_registration_date = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return check_patient_registration_date, column_name

    def get_covid_pcr(self, facility_code, from_date, to_date):
        covid_pcr_qurey = f""" 
        
     SELECT  o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID,
Patient_Name as PatientName,map.SEX,trunc((sysdate - map.DATE_OF_BIRTH) / 365, 0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code,b.remark 
     test_code,t.result_text result , map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,  
 F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,   
 g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state  FROM or_order o,OR_ORDER_LINE L, RL_REQUEST_HEADER A,RL_result_text t, pr_encounter e, 
bl_episode_fin_dtls b, mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g, MP_RES_TOWN h , MP_RES_AREA i, mp_region j 
WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMB000094' and a.PATIENT_ID = map.PATIENT_ID 
 and f.POSTAL1_CODE = g.POSTAL_CODE(+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+) 
 and i.REGION_CODE = j.REGION_CODE(+) AND A.PATIENT_ID = F.PATIENT_ID 
and t.SPECIMEN_NO(+) = a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+) = o.ORDER_STATUS 
and o.PATIENT_ID = b.PATIENT_ID and o.episode_id = b.episode_id 
and e.PATIENT_ID = o.PATIENT_ID and e.EPISODE_ID = o.EPISODE_ID and  o.ORDERING_FACILITY_ID in ({facility_code}) AND o.ORD_DATE_TIME BETWEEN :from_date and to_date(:to_date) + 1
      
"""

        self.cursor.execute(covid_pcr_qurey, [from_date, to_date])
        covid_pcr_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return covid_pcr_data, column_name

    def get_covid_2(self, from_date, to_date):
        covid_2_qurey = """ 
        
                select o.patient_id,p.patient_name,o.PATIENT_CLASS,  o.ord_date_time,o.order_id,l.ORDER_LINE_NUM,
                c.LONG_DESC,s.long_desc orderstatus, l.modified_date stat_change_date,
                p.EMAIL_ID,p.CONTACT1_NO,p.CONTACT2_NO,p.CONTACT3_NO,p.CONTACT4_NO 
                 from or_order o, mp_patient p,or_order_status_code s, or_order_line l,or_order_catalog c where 
                o.PATIENT_ID = p.PATIENT_ID(+)and s.ORDER_STATUS_CODE(+) = o.ORDER_STATUS 
                 and o.ORDER_ID = l.ORDER_ID(+)and l.ORDER_CATALOG_CODE = c.ORDER_CATALOG_CODE(+)
                and L.ORDER_CATALOG_CODE in('LMMB000094', 'LMMC000227') AND o.ORD_DATE_TIME BETWEEN :from_date and :to_date
      
"""

        self.cursor.execute(covid_2_qurey, [from_date, to_date])
        covid_2_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return covid_2_data, column_name

    def get_covid_antibodies(self, facility_code, from_date, to_date):
        covid_antibodies_qurey = f""" 
        
        SELECT  o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus, l.modified_date stat_change_date, CATALOG_DESC, A.PATIENT_ID,
        Patient_Name as PatientName,map.SEX,trunc((sysdate - map.DATE_OF_BIRTH) / 365, 0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code 
        ,max(t.NUMERIC_RESULT) Numeric,max(t.RESULT_COMMENT_DESC1) text ,map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO, 
        F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,
        g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state 
        FROM or_order o,OR_ORDER_LINE L, RL_REQUEST_HEADER A,RL_test_result t, pr_encounter e, 
        bl_episode_fin_dtls b, mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g, MP_RES_TOWN h , MP_RES_AREA i, mp_region j 
        WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMC00223' and a.PATIENT_ID = map.PATIENT_ID 
        and f.POSTAL1_CODE = g.POSTAL_CODE(+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+) 
        and i.REGION_CODE = j.REGION_CODE(+) AND A.PATIENT_ID = F.PATIENT_ID 
        and t.SPECIMEN_NO(+) = a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+) = o.ORDER_STATUS 
        and t.TEST_CODE in ('CUTOFFINDE', 'SARC1') and  o.ORDERING_FACILITY_ID in ({facility_code})
        and o.PATIENT_ID = b.PATIENT_ID and o.episode_id = b.episode_id 
        and e.PATIENT_ID = o.PATIENT_ID and e.EPISODE_ID = o.EPISODE_ID AND o.ORD_DATE_TIME BETWEEN :from_date and to_date(:to_date) + 1
        group by o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc ,l.modified_date ,CATALOG_DESC,A.PATIENT_ID, 
        Patient_Name ,map.SEX,trunc((sysdate - map.DATE_OF_BIRTH) / 365, 0) , o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code 
        ,map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,  
        F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4  , 
        g.LONG_DESC , h.LONG_DESC , i.LONG_DESC , j.LONG_DESC

"""

        self.cursor.execute(covid_antibodies_qurey, [from_date, to_date])
        covid_antibodies_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return covid_antibodies_data, column_name

    def get_covid_antigen(self, facility_code, from_date, to_date):
        covid_antigen_qurey = f""" 
        
    SELECT   o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID,
    Patient_Name PatientName,map.SEX,trunc((sysdate - map.DATE_OF_BIRTH) / 365, 0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code,
    t.RESULT_COMMENT_DESC1 text, map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,
    g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state   FROM 
    or_order o,OR_ORDER_LINE L, RL_REQUEST_HEADER A,RL_test_result t, pr_encounter e,
    bl_episode_fin_dtls b, mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g, MP_RES_TOWN h , MP_RES_AREA i, mp_region j
    WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMC000224' and a.PATIENT_ID = map.PATIENT_ID
    and f.POSTAL1_CODE = g.POSTAL_CODE(+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+)
    and i.REGION_CODE = j.REGION_CODE(+) AND A.PATIENT_ID = F.PATIENT_ID
    and t.SPECIMEN_NO(+) = a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+) = o.ORDER_STATUS
    and t.TEST_CODE in ('COVIDAG') and  o.ORDERING_FACILITY_ID in ({facility_code})
    and o.PATIENT_ID = b.PATIENT_ID and o.episode_id = b.episode_id
    and e.PATIENT_ID = o.PATIENT_ID and e.EPISODE_ID = o.EPISODE_ID AND o.ORD_DATE_TIME BETWEEN :from_date and to_date(:to_date) + 1

"""

        self.cursor.execute(covid_antigen_qurey, [from_date, to_date])
        covid_antigen_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return covid_antigen_data, column_name

    def get_cbnaat_test_data(self, facility_code, from_date, to_date):
        cbnaat_test_data_qurey = f""" 
        
    SELECT  o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID, 
    Patient_Name as PatientName,map.SEX,trunc((sysdate-map.DATE_OF_BIRTH)/365,0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code,b.remark 
    test_code,t.result_text result,map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO, 
    F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state 
    FROM or_order o,OR_ORDER_LINE L,RL_REQUEST_HEADER A,RL_result_text t,pr_encounter e, 
    bl_episode_fin_dtls b ,mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g,  MP_RES_TOWN h , MP_RES_AREA i, mp_region j  
    WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMC000227' and a.PATIENT_ID = map.PATIENT_ID 
    and f.POSTAL1_CODE = g.POSTAL_CODE (+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+) 
    and i.REGION_CODE = j.REGION_CODE(+) AND  A.PATIENT_ID=F.PATIENT_ID and  o.PATIENT_ID=b.PATIENT_ID and o.episode_id = b.episode_id  
    and t.SPECIMEN_NO(+)=a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+)= o.ORDER_STATUS and o.ADDED_FACILITY_ID in ({facility_code})
    and e.PATIENT_ID =o.PATIENT_ID and e.EPISODE_ID=o.EPISODE_ID AND o.ORD_DATE_TIME BETWEEN :from_date and to_date(:to_date) + 1

"""

        self.cursor.execute(cbnaat_test_data_qurey, [facility_code, from_date, to_date])
        cbnaat_test_data_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return cbnaat_test_data_data, column_name

    def get_lab_tat_report(self, facility_code, from_date, to_date, dept_name):
        lab_tat_report_qurey = f""" 
        
    SELECT distinct a.PATIENT_ID UHID,a.specimen_no SpecNo,a.SPECIMEN_TYPE_CODE SpecType,a.SOURCE_CODE Locn,l.PRIORITY Priority,e.LONG_NAME Section, 
q.GROUP_TEST_CODE GrpTest,q.TEST_CODE TestCode,d.LONG_DESC TestName,q.INSTRUMENT_CODE MachineName,l.ORD_DATE_TIME OrdDateTime, 
a.SPEC_COLLTD_DATE_TIME CollDate,a.SPEC_REGD_DATE_TIME RegDate,a.VERIFIED_DATE AckDate,q.RELEASED_DATE FirstRelease, 
trunc(24*mod(q.RELEASED_DATE-a.SPEC_REGD_DATE_TIME,1)) || 'Hrs '||  
trunc( mod(mod(q.RELEASED_DATE-a.SPEC_REGD_DATE_TIME,1)*24,1)*60 ) || 'Mins ' || 
trunc(mod(mod(mod(q.RELEASED_DATE-a.SPEC_REGD_DATE_TIME,1)*24,1)*60,1)*60 ) || 'Secs ' FirstReleaseDiff, 
q.REVIEWED_DATE FinalRelease, trunc(24*mod(q.REVIEWED_DATE-a.SPEC_REGD_DATE_TIME,1)) || 'Hrs '||  
trunc( mod(mod(q.REVIEWED_DATE-a.SPEC_REGD_DATE_TIME,1)*24,1)*60 ) || 'Mins ' || 
trunc(mod(mod(mod(q.REVIEWED_DATE-a.SPEC_REGD_DATE_TIME,1)*24,1)*60,1)*60 ) || 'Secs ' FinalReleasediff 
,q.NORMAL_REVIEWED_BY Reviewdby,p.APPL_USER_NAME   
FROM OR_ORDER_LINE L,RL_REQUEST_HEADER A,or_order_catalog b, rl_test_code d,rl_test_result q,rl_section_code e,sm_APPL_USER p 
WHERE d.SECTION_CODE=e.SECTION_CODE and a.SPECIMEN_NO=q.SPECIMEN_NO and L.ORDER_ID(+) = A.ORDER_ID and l.ORDER_CATALOG_CODE=b.ORDER_CATALOG_CODE 
and  b.CONTR_MSR_PANEL_ID = d.TEST_CODE and L.ORDER_CATEGORY = 'LB' AND p.APPL_USER_ID(+)=q.NORMAL_REVIEWED_BY 
and l.ORD_DATE_TIME between :from_date and to_date (:to_date) + 1  and a.OPERATING_FACILITY_ID in ({facility_code}) and e.LONG_NAME = :dept_name

"""

        self.cursor.execute(lab_tat_report_qurey, [from_date, to_date, dept_name])
        lab_tat_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return lab_tat_report_data, column_name

    def get_histopath_fixation_data(self, year_input, from_date, to_date):
        histopath_fixation_data_qurey = """ 
        
  SELECT A.SPECIMEN_NO as Specimen_No,a.CATEGORY_YEAR as Yr,a.CATEGORY_CODE as Cat_Code,a.CATEGORY_NUMBER as Cat_No,c.TEST_CODE as Test_Code, 
d.LONG_DESC as Test_Name,b.SPECIMEN_DESC as Specimen_Type,e.RESULT_COMMENT_DESC1 as Fixation_Time,a.SPEC_COLLTD_DATE_TIME as Collectn_Dt, 
a.SPEC_RECD_DATE_TIME as Reg_Dt,a.RELEASED_DATE as Release_Dt,a.RELEASED_BY_ID as Who_Released 
FROM RL_REQUEST_HEADER A, rl_specimen_type_code b, RL_REQUEST_detail c, rl_test_code d, rl_test_result e 
WHERE a.SPECIMEN_NO=c.SPECIMEN_NO and c.TEST_CODE=d.TEST_CODE and a.SPECIMEN_NO = e.SPECIMEN_NO and a.SPECIMEN_TYPE_CODE=b.SPECIMEN_TYPE_CODE 
and c.OPERATING_FACILITY_ID = 'KH' and A.RELEASED_DATE IS NOT NULL 
and CATEGORY_YEAR = :year_input and A.SPEC_COLLTD_DATE_TIME between :from_date and to_date(:to_date)+1
and e.RESULT_COMMENT_DESC1 IS NOT NULL ORDER BY A.SPEC_COLLTD_DATE_TIME 

"""

        self.cursor.execute(
            histopath_fixation_data_qurey, [year_input, from_date, to_date]
        )
        histopath_fixation_data_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return histopath_fixation_data_data, column_name

    def get_slide_label_data(self):

        slide_label_data_qurey = """
        
        
                  select a.SPEC_REGD_DATE_TIME as REGDDATE,
                substr(a.CATEGORY_YEAR, -2) || a.CATEGORY_CODE || '-' || a.CATEGORY_NUMBER as CatNo,
                a.PATIENT_ID as PatID,
                b.PATIENT_NAME as PatientName,TO_CHAR(b.DATE_OF_BIRTH, 'YYYY-MM-DD') as DOB,b.SEX,
                substr(a.CATEGORY_YEAR, -2) || a.CATEGORY_CODE || '-' || a.CATEGORY_NUMBER || ';' || a.PATIENT_ID || ';' || b.SEX as BarcodedataSingleSection 
                 from rl_request_header a, mp_patient b where a.PATIENT_ID = b.PATIENT_ID and a.CATEGORY_YEAR >= '2020' and a.CATEGORY_CODE = 'H'
                order by a.SPEC_REGD_DATE_TIME desc
        """

        self.cursor.execute(slide_label_data_qurey)
        slide_label_data_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return slide_label_data_data, column_name

    def get_current_inpatients_pan_card_and_form16_report(self, facility_code):
        current_inpatients_pan_card_and_form16_report_qurey = f""" 
        
            SELECT d.CUST_CODE CUSTCODE,d.patient_id ,BLCOMMON.GET_PAN_CARD_NO({facility_code},d.patient_id) PAN_no ,c.short_name patient_name,NVL(d.episode_id, 0) episodeid,
            TO_CHAR(d.admission_date_time, 'DD/MM/YYYY HH24:MI') admission_date_time,m.ACKNOWLEDG_NO_FORM60,
            cur_ward_code,cur_bed_num bed_num,cur_bed_class_code,
            c.other_contact_num res1_tel_no,d.blng_grp_id blnggrpid 
            FROM ip_episode b,mp_patient_mast c,bl_episode_fin_dtls d,mp_form60 m WHERE 
            d.operating_facility_id in ({facility_code}) AND d.episode_type IN ('D', 'I') AND d.operating_facility_id = b.facility_id
            AND d.episode_id = b.episode_id AND d.patient_id = b.patient_id 
            and m.PATIENT_ID(+) = d.PATIENT_ID and m.ENCOUNTER_ID(+) = d.ENCOUNTER_ID
            AND d.patient_id = c.patient_id 
            AND NVL(d.discharge_bill_gen_ind, 'N') != 'Y'  
            AND d.episode_id IN
                                (SELECT open_episode_id
                                    FROM ip_open_episode
                                    WHERE facility_id   in ({facility_code}))

    

"""

        self.cursor.execute(current_inpatients_pan_card_and_form16_report_qurey)
        current_inpatients_pan_card_and_form16_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return current_inpatients_pan_card_and_form16_report_data, column_name

    def get_contract_effective_date_report(self, facility_code, from_date, to_date):
        contract_effective_date_report_qurey = f""" 
        
        select CUST_CODE,LONG_NAME,CUST_GROUP_CODE,IP_YN,OP_YN,VALID_TO,MODIFIED_FACILITY_ID 
        from ar_customer where MODIFIED_FACILITY_ID in ({facility_code}) and VALID_TO is not null  
        and ADDED_FACILITY_ID in ({facility_code}) and VALID_TO between :from_date and to_date(:to_date) + 1
        order by VALID_TO DESC

"""

        self.cursor.execute(
            contract_effective_date_report_qurey,
            [from_date, to_date],
        )
        contract_effective_date_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return contract_effective_date_report_data, column_name

    def get_admission_report(self, from_date, to_date, facility_code):
        admission_report_qurey = f""" 
    
        select a.PATIENT_ID,b.patient_name, m.long_name,b.email_id,b.contact1_no,b.contact2_no,b.contact3_no,b.email_id as EMAIL_ID2,
        j.ADDR1_LINE1,j.ADDR1_LINE2,j.ADDR1_LINE3,j.ADDR1_LINE4 ,p1.long_desc City_Area, r1.long_desc district,
        o1.long_desc State, q1.LONG_DESC postal_code, k.LONG_NAME COUNTRY, n.ADDR2_LINE1,n.ADDR2_LINE2,n.ADDR2_LINE3,n.ADDR2_LINE4,p.long_desc City_Area, r.long_desc district,
        o.long_desc State, q.LONG_DESC postal_code, l.LONG_NAME as Country,sex,b.mar_status_code,a.VISIT_ADM_DATE_TIME Admission_date, a.DISCHARGE_DATE_TIME,c.PRACTITIONER_NAME Doctor, A.ADDED_BY_ID, 
        a.ASSIGN_BED_CLASS_CODE,a.episode_id, b.REGN_DATE,b.added_date,get_age(b.date_of_birth, SYSDATE) Age,a.ASSIGN_BED_NUM Bed_Num, d.LONG_DESC Speciality 
        from pr_encounter a,mp_patient b, am_practitioner c,bl_episode_fin_dtls f, mp_country m,mp_pat_addresses j, mp_country k,mp_country l, mp_pat_addresses n,am_speciality d, 
        mp_region o, mp_res_town p, mp_postal_code q , mp_res_area r, mp_region o1, mp_res_town p1, mp_postal_code q1 , mp_res_area r1 
        where a.PATIENT_ID = b.PATIENT_ID and a.PATIENT_ID = f.PATIENT_ID and A.episode_id = f.episode_id and m.COUNTRY_CODE = b.NATIONALITY_CODE 
        AND a.SPECIALTY_CODE = d.SPECIALITY_CODE and j.PATIENT_ID = b.PATIENT_ID and n.PATIENT_ID = b.PATIENT_ID and j.COUNTRY1_CODE = k.COUNTRY_CODE(+) 
        and n.COUNTRY2_CODE = l.COUNTRY_CODE(+)   and a.PATIENT_CLASS = 'IP' and a.ATTEND_PRACTITIONER_ID = c.PRACTITIONER_ID 
        and n.res_town1_code = p.res_town_code(+) and n.res_area1_code = r.res_area_code(+) and n.region1_code = o.region_code(+) 
        and n.postal1_code = q.POSTAL_CODE(+) and j.res_town1_code = p1.res_town_code(+) and j.res_area1_code = r1.res_area_code(+) and j.region1_code = o1.region_code(+)
        and j.postal1_code = q1.POSTAL_CODE(+)
        and a.VISIT_ADM_DATE_TIME between :from_date and to_date(:to_date) + 1
        and a.facility_id in ({facility_code})
        and a.cancel_reason_code is null  order by a.VISIT_ADM_DATE_TIME
    
                        
                            
    
"""

        self.cursor.execute(admission_report_qurey, [from_date, to_date])

        admission_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return admission_report_data, column_name

    def get_patient_discharge_report(self, from_date, to_date):
        patient_discharge_report_qurey = """ 
        
select a.PATIENT_ID,b.patient_name, m.long_name,b.email_id,b.contact1_no,b.contact2_no,b.contact3_no,b.email_id as EMAIL_ID2, 
j.ADDR1_LINE1,j.ADDR1_LINE2,j.ADDR1_LINE3,j.ADDR1_LINE4 ,j.POSTAL1_CODE,k.LONG_NAME,n.ADDR2_LINE1,n.ADDR2_LINE2,n.ADDR2_LINE3,n.ADDR2_LINE4,n.POSTAL2_CODE, 
l.LONG_NAME as LONG_NAME4,sex,b.mar_status_code,a.VISIT_ADM_DATE_TIME Admission_date,a.DISCHARGE_DATE_TIME,c.PRACTITIONER_NAME Doctor,A.ADDED_BY_ID, 
a.ASSIGN_BED_CLASS_CODE,a.episode_id, b.REGN_DATE,get_age(b.date_of_birth,SYSDATE) Age,a.ASSIGN_BED_NUM Bed_Num,d.LONG_DESC Speciality  
from pr_encounter a, mp_patient b,am_practitioner c,bl_episode_fin_dtls f,mp_country m, 
mp_pat_addresses j,mp_country k,mp_country l,mp_pat_addresses n,am_speciality d 
where a.PATIENT_ID=b.PATIENT_ID and  a.PATIENT_ID=f.PATIENT_ID   
and A.episode_id = f.episode_id and m.COUNTRY_CODE=b.NATIONALITY_CODE  AND a.SPECIALTY_CODE = d.SPECIALITY_CODE  
and j.PATIENT_ID = b.PATIENT_ID and n.PATIENT_ID = b.PATIENT_ID and j.COUNTRY1_CODE=k.COUNTRY_CODE(+) 
and n.COUNTRY2_CODE=l.COUNTRY_CODE(+) and a.PATIENT_CLASS = 'IP' and a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID  
and a.DISCHARGE_DATE_TIME between :from_date and to_date(:to_date)+1 and a.cancel_reason_code is null and a.facility_id in ('AK','KH','DF','GO','RH','SL')  order by a.DISCHARGE_DATE_TIME 
                            
                             
      
"""

        self.cursor.execute(patient_discharge_report_qurey, [from_date, to_date])
        patient_discharge_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return patient_discharge_report_data, column_name

    def get_credit_letter_report(self, from_date, to_date):
        credit_letter_report_qurey = """ 
        
select a.PATIENT_ID, b.patient_name,G.LONG_NAME ,a.VISIT_ADM_DATE_TIME Admission_date, a.DISCHARGE_DATE_TIME,c.PRACTITIONER_NAME Doctor, a.REFERRAL_ID,e.LONG_DESC Department, F.BLNG_GRP_ID,F.CUST_CODE 
from pr_encounter a, mp_patient b,am_practitioner c,am_speciality e,bl_episode_fin_dtls f,ar_customer g 
where a.PATIENT_ID=b.PATIENT_ID and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id and  F.CUST_CODE = G.CUST_CODE 
and a.FACILITY_ID in ('AK','KH','DF','GO','RH','SL') and a.SPECIALTY_CODE = e.SPECIALITY_CODE and f.blng_grp_id = 'TPA'  
and  a.PATIENT_CLASS = 'IP' and a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID  and a.VISIT_ADM_DATE_TIME between :from_date and to_date(:to_date)+1
and a.cancel_reason_code is null  order by a.VISIT_ADM_DATE_TIME 
                            
                             
      
"""

        self.cursor.execute(credit_letter_report_qurey, [from_date, to_date])
        credit_letter_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return credit_letter_report_data, column_name

    def get_corporate_discharge_report(self, facility_code, from_date, to_date):
        corporate_discharge_report_qurey = f""" 
        
        SELECT unique a.patient_id,b.PATIENT_NAME,b.REGN_DATE,get_age(b.date_of_birth,SYSDATE) Age,b.SEX Sex,a.VISIT_ADM_DATE_TIME Admission_Date,trunc(a.DISCHARGE_DATE_TIME),
        A.ASSIGN_CARE_LOCN_CODE,
        A.ASSIGN_BED_CLASS_CODE,E.LONG_DESC,a.ASSIGN_BED_NUM Bed_Num,c.PRACTITIONER_NAME Treating_Doctor,d.LONG_DESC Speciality,A.ASSIGN_BED_CLASS_CODE, f.BLNG_GRP_ID,f.cust_code,f.Remark,g.long_name,A.episode_id episode
        ,h.DOC_TYPE_CODE ,h.doc_date
        FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f,mp_country g
        ,BL_bill_HDR h
        WHERE a.PATIENT_ID=b.PATIENT_ID AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID
        and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id
        and g.country_code=b.nationality_code
        AND a.patient_class = 'IP'  AND a.SPECIALTY_CODE = d.SPECIALITY_CODE
        and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE and a.cancel_reason_code is null
        AND h.DOC_DATE between :from_date and to_date (:to_date) +1
        and a.FACILITY_ID in ({facility_code})
        and h.DOC_TYPE_CODE = 'IPBL'
        and h.GROSS_AMT > 0
        and A.episode_id = h.episode_id
        and h.BILL_STATUS is null
        ORDER BY A.episode_id
        
      
"""

        self.cursor.execute(corporate_discharge_report_qurey, [from_date, to_date])
        corporate_discharge_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return corporate_discharge_report_data, column_name

    def get_corporate_discharge_report_with_customer_code(self, from_date, to_date):
        corporate_discharge_report_with_customer_code_qurey = f""" 
        
        SELECT unique a.patient_id,b.PATIENT_NAME,b.REGN_DATE,get_age(b.date_of_birth,SYSDATE) Age,b.SEX Sex,a.VISIT_ADM_DATE_TIME Admission_Date,trunc(a.DISCHARGE_DATE_TIME),
        A.ASSIGN_CARE_LOCN_CODE,
        A.ASSIGN_BED_CLASS_CODE,E.LONG_DESC,a.ASSIGN_BED_NUM Bed_Num,c.PRACTITIONER_NAME Treating_Doctor,d.LONG_DESC Speciality,A.ASSIGN_BED_CLASS_CODE, f.BLNG_GRP_ID,f.cust_code,f.Remark,g.long_name,A.episode_id episode
        ,h.DOC_TYPE_CODE ,h.doc_date
        FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f,mp_country g
        ,BL_bill_HDR h
        WHERE a.PATIENT_ID=b.PATIENT_ID AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID
        and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id
        and g.country_code=b.nationality_code
        AND a.patient_class = 'IP'  AND a.SPECIALTY_CODE = d.SPECIALITY_CODE
        and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE and a.cancel_reason_code is null
        AND h.DOC_DATE between :from_date and to_date(:to_date) +1
        and a.FACILITY_ID = 'KH'
        and h.DOC_TYPE_CODE = 'IPBL'
        and h.GROSS_AMT > 0
        and A.episode_id = h.episode_id
        and h.BILL_STATUS is null
        ORDER BY A.episode_id
        
      
"""

        self.cursor.execute(
            corporate_discharge_report_with_customer_code_qurey, [from_date, to_date]
        )
        corporate_discharge_report_with_customer_code_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return corporate_discharge_report_with_customer_code_data, column_name

    def get_corporate_ip_report(self, from_date, to_date):
        corporate_ip_report_qurey = """ 
        
SELECT a.patient_id,b.PATIENT_NAME,a.VISIT_ADM_DATE_TIME Admission_Date,a.ASSIGN_BED_NUM Bed_Num,d.LONG_DESC Speciality,E.LONG_DESC,c.PRACTITIONER_NAME Treating_Doctor,f.BLNG_GRP_ID,f.cust_code,f.remark
FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f ,mp_country m 
WHERE a.PATIENT_ID=b.PATIENT_ID AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID and  a.FACILITY_ID in ('AK','KH','DF','GO','RH','SL') 
and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id AND a.patient_class = 'IP'  AND a.SPECIALTY_CODE = d.SPECIALITY_CODE  
and m.COUNTRY_CODE=b.NATIONALITY_CODE and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE and a.cancel_reason_code is null 
AND a.VISIT_ADM_DATE_TIME  between :from_date and to_date(:to_date)+1
order by a.VISIT_ADM_DATE_TIME
                            
                             
      
"""

        self.cursor.execute(corporate_ip_report_qurey, [from_date, to_date])
        corporate_ip_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return corporate_ip_report_data, column_name

    def get_opd_consultation_report(self, facility_code, from_date, to_date):
        opd_consultation_report_qurey = f""" 
        
        SELECT a.patient_id,b.patient_name,TO_CHAR (a.service_date, 'DD/MM/YY') serv_date,a.blng_serv_code serv_code,
        c.long_desc serv_desc,a.Serv_qty,a.upd_net_charge_amt,a.EPISODE_TYPE,a.service_date,physician_id,f.PRACTITIONER_NAME
        FROM bl_patient_charges_folio a,mp_patient b,bl_blng_serv c,bl_blng_serv_grp d,am_dept_lang_vw e,AM_PRACTITIONER f
        WHERE a.operating_facility_id in ({facility_code})
        AND a.blng_serv_code = c.blng_serv_code AND a.patient_id = b.patient_id AND c.serv_grp_code = d.serv_grp_code
        AND a.acct_dept_code = e.dept_code and NVL(A.BILLED_FLAG,'N') = decode(a.episode_type,'O','Y','E','Y','R','Y',NVL(A.BILLED_FLAG,'N'))
        AND e.language_id = 'en' AND a.service_date >= TO_DATE (:from_date) AND a.service_date < TO_DATE (:to_date)+1
        and physician_id = f.PRACTITIONER_ID
        and A.UPD_NET_CHARGE_AMT !=0 and a.blng_serv_code like ('CNOP%')
                            
                             
      
"""

        self.cursor.execute(opd_consultation_report_qurey, [from_date, to_date])
        opd_consultation_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return opd_consultation_report_data, column_name

    def get_opd_consultation_report_with_address(
        self, facility_code, from_date, to_date
    ):
        opd_consultation_report_with_address_qurey = f""" 
        
SELECT a.patient_id,b.patient_name,TO_CHAR (a.service_date, 'DD/MM/YY') serv_date,a.blng_serv_code serv_code,
c.long_desc serv_desc,a.Serv_qty,a.upd_net_charge_amt,a.EPISODE_TYPE,a.service_date,physician_id,f.ADDR1_LINE4 as CITY,f.POSTAL1_CODE as PIN_CODE,
f.ADDR1_LINE1||','||f.ADDR1_LINE2||','||f.ADDR1_LINE3 as ADDRESS
FROM bl_patient_charges_folio a,mp_patient b,bl_blng_serv c,bl_blng_serv_grp d,am_dept_lang_vw e,mp_pat_addresses f
WHERE a.operating_facility_id in ({facility_code})
AND a.blng_serv_code = c.blng_serv_code 
AND a.patient_id = b.patient_id
and a.patient_id = f.PATIENT_ID
AND c.serv_grp_code = d.serv_grp_code
AND a.acct_dept_code = e.dept_code 
and NVL(A.BILLED_FLAG,'N') = decode(a.episode_type,'O','Y','E','Y','R','Y',NVL(A.BILLED_FLAG,'N'))
AND e.language_id = 'en' 
AND a.service_date >= TO_DATE (:from_date) 
AND a.service_date < TO_DATE (:to_date)+1
and A.UPD_NET_CHARGE_AMT !=0 
and a.blng_serv_code like ('CNOP%')
                            
                             
      
"""

        self.cursor.execute(
            opd_consultation_report_with_address_qurey, [from_date, to_date]
        )
        opd_consultation_report_with_address_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return opd_consultation_report_with_address_data, column_name

    def get_initial_assessment_indicator(self, facility_code, from_date, to_date):
        initial_assessment_indicator_qurey = f""" 
        
        select a.PATIENT_ID,b.patient_name,a.VISIT_ADM_DATE_TIME Admission_date,I.LONG_DESC Bed_class ,a.ASSIGN_BED_NUM Bed_Num,U.LONG_DESC Bed_location,  d.LONG_DESC Speciality, A.BED_ALLOCATION_DATE_TIME Admission_Acceptance_Time  
        from pr_encounter a,mp_patient b,am_practitioner c,am_speciality d ,IP_BED_CLASS i,IP_NURSING_UNIT_BED n, ip_nursing_unit u
        where a.PATIENT_ID=b.PATIENT_ID and a.SPECIALTY_CODE = d.SPECIALITY_CODE and a.PATIENT_CLASS = 'IP' and N.NURSING_UNIT_CODE = U.NURSING_UNIT_CODE
        and a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID and n.BED_NO =  A.ASSIGN_BED_NUM and I.BED_CLASS_CODE =  a.ASSIGN_BED_CLASS_CODE
        and a.VISIT_ADM_DATE_TIME between :from_date and to_date(:to_date) + 1
        and a.facility_id in ({facility_code}) 
        and a.cancel_reason_code is null  order by a.VISIT_ADM_DATE_TIME


"""

        self.cursor.execute(initial_assessment_indicator_qurey, [from_date, to_date])
        initial_assessment_indicator_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return initial_assessment_indicator_data, column_name

    def get_emergency_casualty_report(self, from_date, to_date, facility_code):
        emergency_casualty_report_qurey = f""" 
        
            select a.patient_id, b.patient_name,TO_CHAR(a.service_date, 'DD/MM/YY') serv_date,a.blng_serv_code serv_code, c.long_desc serv_desc, a.Serv_qty, a.upd_net_charge_amt,a.EPISODE_TYPE,a.service_date
            FROM bl_patient_charges_folio a,mp_patient b,bl_blng_serv c,bl_blng_serv_grp d,am_dept_lang_vw e
            WHERE a.operating_facility_id in ({facility_code}) AND a.blng_serv_code = c.blng_serv_code AND a.patient_id = b.patient_id
            AND c.serv_grp_code = d.serv_grp_code AND a.acct_dept_code = e.dept_code
            and NVL(A.BILLED_FLAG,'N') = decode(a.episode_type,'O','Y','E','Y','R','Y',NVL(A.BILLED_FLAG,'N'))
            AND e.language_id = 'en' AND a.service_date between :from_date and to_date(:to_date)+1
            and A.UPD_NET_CHARGE_AMT !=0 and a.blng_serv_code in ('OPGN000017')
                                        
                             
      
"""

        self.cursor.execute(emergency_casualty_report_qurey, [from_date, to_date])
        emergency_casualty_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return emergency_casualty_report_data, column_name

    def get_new_registration_report(
        self, from_date, to_date, city_input, facility_code
    ):
        new_registration_report_qurey = f""" 
    
        select b.patient_id,b.regn_date,a.PATIENT_CLASS,a.ASSIGN_BED_CLASS_CODE, g.long_desc specilaity,e.practitioner_name, b.patient_name,b.email_id,b.contact2_no,j.ADDR1_TYPE,
        j.addr1_line1 || ' ' || j.addr1_line2 || ' ' || j.addr1_line3 || ' ' || j.addr1_line4 Address, j.POSTAL1_CODE as Postal_Code ,
        k.LONG_NAME as Country from pr_encounter a,mp_patient b,mp_pat_addresses j,mp_country k,am_speciality g ,am_practitioner e
        where a.patient_id=b.patient_id AND j.PATIENT_ID = b.PATIENT_ID and j.COUNTRY1_CODE=k.COUNTRY_CODE
        and a.ATTEND_PRACTITIONER_ID = e.practitioner_id 
        and g.SPECIALITY_CODE = a.SPECIALTY_CODE and  g.SPECIALITY_CODE = e.PRIMARY_SPECIALITY_CODE
        and b.regn_date  between :from_date and to_date(:to_date)+1   
        and b.ADDED_FACILITY_ID in ({facility_code})
        and (upper(addr1_line1) like '%'||:city_input||'%' or 
        upper(addr1_line2) like '%'||:city_input||'%' or upper(addr1_line3) 
        like '%'||:city_input||'%' or upper(addr1_line4) like '%'||:city_input||'%' )

"""
        self.cursor.execute(
            new_registration_report_qurey, [from_date, to_date, city_input]
        )

        new_registration_report_data = self.cursor.fetchall()
        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return new_registration_report_data, column_name

    def get_hospital_tariff_report(self, facility_code, from_date, to_date):
        hospital_tariff_report_qurey = f""" 
        
select a.blng_serv_code ,b.long_desc,c.long_desc SERVICE_GROUP,d.long_desc SERVICE_CLASSIFICATION ,a.CUST_PC_CODE, 
a.blng_class_code,b.PRT_GRP_HDR_CODE ,a.valid_from , a.valid_to , a.ip_rate , a.op_rate 
from bl_serv_cust_pc_price a, bl_blng_serv b,BL_BLNG_SERV_GRP c,BL_SERV_CLASSIFICATION d 
where a.BLNG_SERV_CODE = b.BLNG_SERV_CODE and valid_to is null and a.BLNG_CLASS_CODE not in ('ER','EX','LD') 
and b.SERV_GRP_CODE not in ('CO','PH','AI','AP','BL','BS','BW','CL','DR','DS','DY','GC','GL','GW','HV','IA', 
'IE','IJ','IM','IP','IS','IT','IU','IV','LA','LE','LG','LP','LS','LY','ME','NA','ND','NJ','NK','NL','NO','NS','NV', 
'NW','OB','OM','PE','PL','PN','RL','SB','SC','SL','ST','SV','SW','SY','VA','VB','VC','VL','XY') 
and CUST_PC_CODE in ({facility_code}) AND a.valid_from between :from_date and to_date(:to_date)+1 
and b.serv_grp_code = c.serv_grp_code  and b.SERV_CLASSIFICATION_CODE = d.SERV_CLASSIFICATION_CODE and b.status is null order by CUST_PC_CODE

"""

        self.cursor.execute(hospital_tariff_report_qurey, [from_date, to_date])
        hospital_tariff_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return hospital_tariff_report_data, column_name

    def get_international_patient_report(self, from_date, to_date, facility_code):

        international_patient_report_qurey = f""" 
        
select a.PATIENT_ID,b.patient_name,m.long_name,b.DATE_OF_BIRTH,a.VISIT_ADM_DATE_TIME Admission_date,a.DISCHARGE_DATE_TIME,a.SPECIALTY_CODE,c.PRACTITIONER_NAME Doctor, A.ADDED_BY_ID,
b.CONTACT2_NO, b.EMAIL_ID,l.ADDR1_LINE1, l.ADDR1_LINE2,l.ADDR1_LINE3,l.ADDR1_LINE4,a.FACILITY_ID
from pr_encounter a, mp_patient b,am_practitioner c,bl_episode_fin_dtls f,mp_country m, MP_PAT_ADDRESSES l
where a.PATIENT_ID=b.PATIENT_ID and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id and m.COUNTRY_CODE=b.NATIONALITY_CODE
and f.blng_grp_id = 'FOR1' and a.PATIENT_CLASS = 'OP' and a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID and b.PATIENT_ID = l.PATIENT_ID
and a.VISIT_ADM_DATE_TIME between :from_date and to_date(:to_date)+1
and a.FACILITY_ID in ({facility_code})
and a.cancel_reason_code is null order by a.VISIT_ADM_DATE_TIME             
                             
      
"""

        self.cursor.execute(
            international_patient_report_qurey,
            [
                from_date,
                to_date,
            ],
        )

        international_patient_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return international_patient_report_data, column_name

    def get_tpa_query(self, from_date, to_date):
        tpa_query_qurey = """ 
        
SELECT a.patient_id,b.PATIENT_NAME,a.VISIT_ADM_DATE_TIME Admission_Date, E.LONG_DESC,
a.ASSIGN_BED_NUM Bed_Num,c.PRACTITIONER_NAME Treating_Doctor,d.LONG_DESC Speciality,f.BLNG_GRP_ID,f.cust_code,f.remark
 FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f,mp_country m
 WHERE a.PATIENT_ID=b.PATIENT_ID AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID
 and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id
 AND a.patient_class = 'IP'  AND a.SPECIALTY_CODE = d.SPECIALITY_CODE
 and m.COUNTRY_CODE=b.NATIONALITY_CODE
 and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE and a.cancel_reason_code is null
 AND  a.VISIT_ADM_DATE_TIME BETWEEN :from_date and to_date(:to_date)+1
order by a.VISIT_ADM_DATE_TIME        
                             
      
"""

        self.cursor.execute(tpa_query_qurey, [from_date, to_date])
        tpa_query_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return tpa_query_data, column_name

    def get_new_admission_report(self, from_date, to_date, facility_code):

        new_admission_report_qurey = f""" 
        
select a.PATIENT_ID,b.patient_name,a.VISIT_ADM_DATE_TIME Admission_date,a.DISCHARGE_DATE_TIME,a.REFERRAL_ID,  c.PRACTITIONER_NAME Doctor,e.LONG_DESC Department,F.BLNG_GRP_ID,F.CUST_CODE,G.LONG_NAME ,a.FACILITY_ID 
from pr_encounter a, mp_patient b,am_practitioner c,am_speciality e,bl_episode_fin_dtls f,ar_customer g  where a.PATIENT_ID=b.PATIENT_ID and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id 
and  F.CUST_CODE = G.CUST_CODE and a.SPECIALTY_CODE = e.SPECIALITY_CODE and f.blng_grp_id = 'TPA' and  a.PATIENT_CLASS = 'IP' and a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID
AND  a.VISIT_ADM_DATE_TIME BETWEEN :from_date and to_date(:to_date)+1
AND a.FACILITY_ID in ({facility_code})
and a.cancel_reason_code is null  order by a.VISIT_ADM_DATE_TIME 
                
      
"""

        self.cursor.execute(new_admission_report_qurey, [from_date, to_date])

        new_admission_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return new_admission_report_data, column_name

    def get_discharge_billing_report(self, facility_code, from_date, to_date):
        discharge_billing_report_qurey = f""" 
        
    select a.patient_id,a.encounter_id,initcap(short_name),alternate_id3_num,dis_adv_date_time,a.added_by_id,c.appl_user_name, 
    b.other_contact_num,d.BED_NUM,e.BLNG_GRP_ID
    from ip_discharge_advice a,mp_patient_mast b,sm_appl_user_vw c,IP_OPEN_ENCOUNTER d,bl_episode_fin_dtls e
    where --a.dis_adv_status='0' 
    a.patient_id = b.patient_id 
    and a.patient_id = d.patient_id
    and a.patient_id = e.patient_id
    and a.encounter_id = d.ENCOUNTER_ID
    and a.encounter_id = e.ENCOUNTER_ID
    and a.added_by_id = c.appl_user_id 
    --and c.language_id='en' 
    and a.FACILITY_ID  in ({facility_code}) 
    and a.DIS_ADV_DATE_TIME between :from_date and to_date(:to_date) + 1
    order by dis_adv_date_time
                             
      
"""

        self.cursor.execute(discharge_billing_report_qurey, [from_date, to_date])
        discharge_billing_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return discharge_billing_report_data, column_name

    # def get_discharge_billing_report_without_date_range(self):

    #     discharge_billing_report_without_date_range_query = """

    #         select a.FACILITY_ID,a.patient_id,a.encounter_id,initcap(short_name),alternate_id3_num,dis_adv_date_time,a.added_by_id,c.appl_user_name from ip_discharge_advice a,mp_patient_mast b,sm_appl_user_vw c where a.dis_adv_status='0' and a.patient_id = b.patient_id and a.added_by_id = c.appl_user_id and c.language_id='en' and a.FACILITY_ID  ='KH' and trunc(a.DIS_ADV_DATE_TIME) = trunc(sysdate) order by dis_adv_date_time

    #     """

    #     self.cursor.execute(discharge_billing_report_without_date_range_query)
    #     discharge_billing_report_without_date_range_data = self.cursor.fetchall()

    #     column_name = [i[0] for i in self.cursor.description]

    #     if self.cursor:
    #         self.cursor.close()
    #     if self.ora_db:
    #         self.ora_db.close()

    #     return discharge_billing_report_without_date_range_data, column_name

    def get_discharge_billing_report_without_date_range(self):

        discharge_billing_report_without_date_range_query = """
        
        

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
      and c.language_id='en' and a.FACILITY_ID  ='KH' 
      and not exists (select * from bl_bill_hdr h where h.patient_id=a.patient_id and h.episode_id = a.encounter_id and h.bill_status<>'C')
      order by dis_adv_date_time 
        
        """

        self.cursor.execute(discharge_billing_report_without_date_range_query)
        discharge_billing_report_without_date_range_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return discharge_billing_report_without_date_range_data, column_name

    def get_discharge_billing_user(self):

        discharge_billing_user_query = """
        
        
           select a.PATIENT_ID,a.ENCOUNTER_ID,initcap(short_name),DIS_ADV_DATE_TIME,a.ADDED_BY_ID ,c.APPL_USER_NAME
           from ip_discharge_advice a,mp_patient_mast b, sm_appl_user_vw c   where A.DIS_ADV_STATUS='0'
           and a.patient_id = b.patient_id and a.added_by_id = c.APPL_USER_ID and c.language_id ='en'
           order by DIS_ADV_DATE_TIME  
            

        """

        self.cursor.execute(discharge_billing_user_query)
        discharge_billing_user_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return discharge_billing_user_data, column_name

    def get_discount_report(self, from_date, to_date, facility_code):
        discount_report_qurey = f""" 
        
        SELECT distinct b.patient_name,a.PATIENT_ID,a.episode_id,a.PATIENT_CLASS,d.DOC_TYPE_CODE,
        d.DOC_NUM Bill_Num, c.PRACTITIONER_NAME Doctor, round(d.BILL_HOSP_TOT_AMT) as Totalbill,
        round(d.serv_disc_amt) servicediscount,round(D.MAN_DISC_AMT),round(d.OVERALL_DISC_AMT) 
        as overall_discount,round(d.DEPOSIT_ADJ_AMT) advance, round(d.BILL_AMT),round(d.BILL_TOT_OUTST_AMT) as TPA_DUE_Amount,
        round(d.bill_paid_amt) CASH_CC, round(d.TOT_REFUND_AMT)Refund, d.modified_by_id as 
        Prepared_by,D.DOC_TYPE_CODE,D.DOC_NUM,d.doc_date,d.BLNG_GRP_ID,d.CUST_CODE,
        d.REASON_CODE,e.DISC_REASON_CODE,d.BILL_DISC_DATE,d.BILL_DISC_BY_ID,d.BILL_DISC_AUTH_BY_ID,f.REMARK 
        FROM pr_encounter a, mp_patient b,am_practitioner c, bl_bill_hdr d,
        bl_patient_charges_folio e, bl_episode_fin_dtls f 
        WHERE a.PATIENT_ID = b.PATIENT_ID AND a.patient_id = d.patient_id AND 
        a.Episode_id = d.EPISODE_ID AND a.ATTEND_PRACTITIONER_ID = c.PRACTITIONER_ID and
        f.EPISODE_ID = d.EPISODE_ID and f.PATIENT_ID = d.PATIENT_ID 
        and d.DOC_NUM = e.BILL_DOC_NUM(+)
        and d.DOC_TYPE_CODE = e.BILL_DOC_TYPE_CODE(+)
        AND E.DISC_REASON_CODE IS NOT NULL
        AND D.SERV_DISC_AMT > 0
        and d.bill_status IS NULL
        and D.DOC_DATE between :from_date and to_date(:to_date) + 1
        and a.FACILITY_ID in ({facility_code})
        union 
        SELECT b.patient_name,a.PATIENT_ID,a.episode_id,a.PATIENT_CLASS,d.DOC_TYPE_CODE,d.DOC_NUM Bill_Num, 
        c.PRACTITIONER_NAME Doctor, round(d.BILL_HOSP_TOT_AMT) Total_bill,
        round(d.serv_disc_amt) servicediscount,round( D.MAN_DISC_AMT),round(d.OVERALL_DISC_AMT)
        overall_discount,round(d.DEPOSIT_ADJ_AMT) advance, round(d.BILL_AMT),round(d.BILL_TOT_OUTST_AMT)
        TPA_DUE_Amount,round(d.bill_paid_amt) CASH_CC, round(d.TOT_REFUND_AMT) Refund, d.modified_by_id
        as Prepared_by,D.DOC_TYPE_CODE,D.DOC_NUM,d.doc_date,d.BLNG_GRP_ID,d.CUST_CODE,
        d.REASON_CODE,null,d.BILL_DISC_DATE,d.BILL_DISC_BY_ID,d.BILL_DISC_AUTH_BY_ID,f.REMARK 
        FROM pr_encounter a, mp_patient b,am_practitioner c, bl_bill_hdr d,bl_episode_fin_dtls f 
        WHERE a.PATIENT_ID = b.PATIENT_ID AND a.patient_id = d.patient_id AND 
        f.EPISODE_ID = d.EPISODE_ID and f.PATIENT_ID = d.PATIENT_ID and 
        a.Episode_id = d.EPISODE_ID AND a.ATTEND_PRACTITIONER_ID = c.PRACTITIONER_ID 
        and d.bill_status IS NULL
        and D.DOC_DATE between :from_date and to_date(:to_date) + 1
        and a.FACILITY_ID in ({facility_code})
                                 
                                   """

        self.cursor.execute(discount_report_qurey, [from_date, to_date])
        discount_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return discount_report_data, column_name

    def get_refund_report(self, from_date, to_date, facility_code):
        refund_report_qurey = f""" 
        
                select a.patient_id,c.patient_name,B.SLMT_TYPE_CODE,E.LONG_DESC,round(A.DOC_AMT) as DOC_AMT,A.DOC_DATE,A.DOC_TYPE_CODE,
                A.DOC_NUMBER,A.BILL_DOC_TYPE_CODE,A.BILL_DOC_NUMBER,A.NARRATION,
                b.MODIFIED_BY_ID,a.CANCELLED_IND
                from bl_receipt_refund_hdr a, bl_receipt_refund_dtl b,mp_patient c, mp_pat_addresses d,BL_SLMT_TYPE E
                where A.PATIENT_ID = B.PATIENT_ID
                and A.PATIENT_ID = c.patient_id and a.patient_id = d.patient_id
                and B.SLMT_TYPE_CODE in ('SD', 'ED', 'CH', 'DN', 'BC', 'BF', 'CA', 'CF', 'T1', 'T2') and A.BILL_DOC_NUMBER is not null
                and A.DOC_AMT <= -1
                and b.SLMT_TYPE_CODE = E.SLMT_TYPE_CODE
                and A.DOC_TYPE_CODE = B.DOC_TYPE_CODE and A.DOC_NUMBER = B.DOC_NUMBER
                and A.DOC_DATE between :from_date and to_date(:to_date)+1 
                and a.OPERATING_FACILITY_ID in ({facility_code})
                                 
                                   """

        self.cursor.execute(refund_report_qurey, [from_date, to_date])
        refund_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return refund_report_data, column_name

    def get_non_medical_equipment_report(self, uhid, episode_id):

        non_medical_equipment_report_qurey = """
        
        SELECT bl_patient_charges_folio.SERVICE_DATE, bl_patient_charges_folio.TRX_DATE, bl_patient_charges_folio.CONFIRMED_DATE,
        bl_patient_charges_folio.PATIENT_ID, bl_patient_charges_folio.EPISODE_ID, bl_patient_charges_folio.PRT_GRP_HDR_CODE,
        bl_patient_charges_folio.BLNG_SERV_CODE,b.LONG_DESC ITEM_DESC, bl_patient_charges_folio.SERV_ITEM_DESC, bl_patient_charges_folio.ORG_GROSS_CHARGE_AMT,
        bl_patient_charges_folio.ORG_DISC_AMT, bl_patient_charges_folio.ORG_NET_CHARGE_AMT 
        FROM IBAEHIS.bl_patient_charges_folio bl_patient_charges_folio,bl_blng_serv b 
        WHERE(bl_patient_charges_folio.PATIENT_ID = :uhid) 
        AND(bl_patient_charges_folio.EPISODE_ID = :episode_id)
        and  bl_patient_charges_folio.BLNG_SERV_CODE = b.BLNG_SERV_CODE
        AND(bl_patient_charges_folio.TRX_STATUS Is Null) 
        AND(bl_patient_charges_folio.BLNG_GRP_ID Not In('TPA', 'FTPA','1TPA' , 'GTPA')) AND(bl_patient_charges_folio.ADJ_NET_CHARGE_AMT <> 0) 
        UNION 
        SELECT null,null,null, 
        bl_patient_charges_folio.PATIENT_ID, bl_patient_charges_folio.EPISODE_ID, null, 
        NULL,NULL, 'GRAND TOTAL',SUM(bl_patient_charges_folio.ORG_GROSS_CHARGE_AMT), 
        SUM(bl_patient_charges_folio.ORG_DISC_AMT),SUM(bl_patient_charges_folio.ORG_NET_CHARGE_AMT) 
        FROM IBAEHIS.bl_patient_charges_folio bl_patient_charges_folio 
        WHERE(bl_patient_charges_folio.PATIENT_ID = :uhid) 
        AND(bl_patient_charges_folio.EPISODE_ID = :episode_id) 
        AND(bl_patient_charges_folio.TRX_STATUS Is Null) 
        AND(bl_patient_charges_folio.BLNG_GRP_ID Not In('TPA', 'FTPA','1TPA' , 'GTPA')) AND(bl_patient_charges_folio.ADJ_NET_CHARGE_AMT <> 0) 
        group by bl_patient_charges_folio.PATIENT_ID, bl_patient_charges_folio.EPISODE_ID



        """

        self.cursor.execute(non_medical_equipment_report_qurey, [uhid, episode_id])
        non_medical_equipment_report = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return non_medical_equipment_report, column_name

    def get_additional_tax_on_package_room_rent(self, uhid, episode_id):

        additional_tax_on_package_room_rent_qurey = """
        
        select PATIENT_ID,EPISODE_ID,ADDL_CHARGE_AMT_IN_CHARGE,PACKAGE_TRX_YN from BL_PATIENT_CHARGES_FOLIO
        where PATIENT_ID = :uhid and episode_id=:episode_id
        and 
        EPISODE_TYPE='I' and
        BLNG_SERV_CODE like 'RM%' 
        and PACKAGE_TRX_YN in ('Y','P')
        and TRX_STATUS IS NULL
        and ADDL_CHARGE_AMT_IN_CHARGE >0



        """

        self.cursor.execute(
            additional_tax_on_package_room_rent_qurey, [uhid, episode_id]
        )
        additional_tax_on_package_room_rent = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return additional_tax_on_package_room_rent, column_name

    def get_due_deposit_report(self, facility_code):
        due_deposit_report_qurey = f""" 
        
                select ahiid Patient_ID, patient_name, admission_date_time,
                BLCOMMON.GET_PAN_CARD_NO({facility_code},ahiid) PAN_no , bed_num, 
                (nvl(vNonPkgAmount,0) + nvl(voutsidePkgAmount,0) + nvl(cf_package_amount,0)) Total_Bill_Amount_as_on_Date , 
                nvl(advancepaid,0) + nvl(cf_unadj_ext_dep_amt,0) Advance_Paid, APP_AMT TPA_Approval_Amount , 
                nvl(vNonPkgDiscAmount,0) + nvl(voutsideDiscPkgAmount,0) + nvl(vPkgDiscount,0) Discount,
                CF_package_amount Package_Amount, 
                (ABS(NVL( nvl(vNonPkgAmount,0) + nvl(voutsidePkgAmount,0) + nvl(cf_package_amount,0), 0) - 
                    nvl( nvl(vNonPkgDiscAmount,0) + nvl(voutsideDiscPkgAmount,0) + nvl(vPkgDiscount,0),0) - 
                    (NVL(tot_unadj_dep_amt, 0) + 
                    NVL(tot_unadj_prep_amt, 0) + 
                    nvl(CF_unadj_ext_dep_amt,0)))) Due_Amount,
                cur_physician_id Consulting_Doctor,
                contact1_name Next_of_Kin,
                res1_tel_no Contact_No,
                nd_payer_name Payer,
                --added from here viren
                --FORM_60_YN,ADDED_BY_ID,this field is also required
                    CURACCTSEQNO,
                    cur_ward_code,
                    date_of_birth,
                    credit_auth_ref,
                    credit_auth_date,
                    cur_physician_id,
                    long_desc,
                    contact1_relation,
                    contact1_name,
                    res1_tel_no,
                    episodetype,
                    blnggrpid,
                    CUR_BED_CLASS_CODE,
                    --CUST_CODE,
                    episodeid,
                    --added till here viren
                     NOTES
                from 
                (
                select ahiid , patient_name, admission_date_time,
                BLCOMMON.GET_PAN_CARD_NO({facility_code},ahiid) PAN_no , bed_num, 
                (select sum(nvl(ORG_GROSS_CHARGE_AMT,0)) 
                from bl_patient_charges_folio
                where operating_facility_id in ({facility_code})
                and   patient_id= ahiid
                and   episode_type= episodetype
                and   episode_id= episodeid
                and   nvl(BILLED_FLAG,'N')='N'
                and   bill_doc_type_code is null
                and   nvl(package_trx_yn,'N')='N') vNonPkgAmount  , 
                (select sum(nvl(ORG_disc_AMT,0))  vNonPkgDiscAmount
                from bl_patient_charges_folio
                where operating_facility_id in ({facility_code})
                and   patient_id= ahiid
                and   episode_type= episodetype
                and   episode_id= episodeid
                and   nvl(BILLED_FLAG,'N')='N'
                and   bill_doc_type_code is null
                and   nvl(package_trx_yn,'N')='N') vNonPkgDiscAmount  ,   
                    (select sum(nvl(ORG_GROSS_CHARGE_AMT,0)) 
                from bl_package_folio
                where (operating_facility_id, trx_doc_ref, trx_doc_ref_line_num, trx_doc_Ref_seq_num) in
                (select operating_facility_id, trx_doc_ref, trx_doc_ref_line_num, trx_doc_Ref_seq_num
                from bl_patient_charges_folio
                where operating_facility_id in ({facility_code})
                and   patient_id=ahiid
                and   episode_type= episodetype
                and   episode_id= episodeid
                and   nvl(BILLED_FLAG,'N')='N'
                and   bill_doc_type_code is null
                and   nvl(package_trx_yn,'N')='P')
                and   nvl(package_trx_yn,'N')='N' ) voutsidePkgAmount,
                    (select sum(nvl(ORG_disc_AMT,0)) 
                from bl_package_folio
                where (operating_facility_id, trx_doc_ref, trx_doc_ref_line_num, trx_doc_Ref_seq_num) in
                (select operating_facility_id, trx_doc_ref, trx_doc_ref_line_num, trx_doc_Ref_seq_num
                from bl_patient_charges_folio
                where operating_facility_id in ({facility_code})
                and   patient_id=ahiid
                and   episode_type= episodetype
                and   episode_id= episodeid
                and   nvl(BILLED_FLAG,'N')='N'
                and   bill_doc_type_code is null
                and   nvl(package_trx_yn,'N')='P')
                and   nvl(package_trx_yn,'N')='N' ) voutsideDiscPkgAmount,
                (select sum(nvl(PKG_SERV_DISC,0))  
                from bl_package_folio
                where (operating_facility_id, trx_doc_ref, trx_doc_ref_line_num, trx_doc_Ref_seq_num) in
                (select operating_facility_id, trx_doc_ref, trx_doc_ref_line_num, trx_doc_Ref_seq_num
                from bl_patient_charges_folio
                where operating_facility_id in ({facility_code})
                and   patient_id= ahiid
                and   episode_type= episodetype
                and   episode_id= episodeid
                and   nvl(BILLED_FLAG,'N')='N'
                and   bill_doc_type_code is null
                and   nvl(package_trx_yn,'N') in ('Y','P'))
                and   nvl(package_trx_yn,'N')='Y') vPkgDiscount,    
                    (SELECT  sum(NVL(PACKAGE_AMT,0))  --into v_package_amt
                            FROM  bl_package_sub_hdr  
                            WHERE PATIENT_ID= AHIID
                    AND STATUS='O'
                    and package_seq_no in (select package_Seq_no from bl_package_encounter_Dtls where   
                    operating_facility_id in ({facility_code})
                    and patient_id= AHIID
                    and episode_type= episodetype
                    and encounter_id= episodeid)) cf_package_amount ,
                    
                (select sum(nvl(-1*DOC_OUTST_AMT,0))  
                from bl_patient_ledger
                where patient_id= ahiid
                and operating_facility_id in ({facility_code})
                and episode_type='R'
                and trx_type_code='5'
                and trx_status is null) cf_unadj_ext_dep_amt     , advancepaid, 
                (SELECT SUM(NVL(APPROVED_AMT,0))  
                    FROM BL_ENCOUNTER_PAYER_PRIORITY WHERE BLNG_GRP_ID = blnggrpid
                    AND PATIENT_ID = Ahiid AND EPISODE_ID = Episodeid AND EPISODE_TYPE = episodetype
                    AND ACCT_SEQ_NO = CURACCTSEQNO ) APP_AMT,
                (SELECT LONG_NAME   FROM AR_CUSTOMER_LANG_VW 
                    WHERE CUST_CODE = custCODE) nd_payer_name ,
                    (SELECT RTRIM(XMLAGG(XMLELEMENT(E,notes,',   ').EXTRACT('//text()') ORDER BY patient_id).GetClobVal(),',') AS Recent_Notes
                        FROM mp_patient_notes
                        where patient_id= ahiid
                        --and ENCOUNTER_ID = episodeid
                        ) NOTES,
                res1_tel_no, contact1_name, cur_physician_id, tot_unadj_prep_amt, tot_unadj_dep_amt,
                --added from here viren
                blnggrpid,episodetype, CURACCTSEQNO,
                cur_ward_code,
                date_of_birth,
                credit_auth_ref,
                credit_auth_date,
                long_desc,
                contact1_relation,
                cur_bed_class_code,
                --CUST_CODE,
                episodeid
                --added till here viren
                from 
                (
                SELECT d.CUST_CODE CUSTCODE,d.patient_id ahiid,
                    c.short_name patient_name,
                    NVL(d.episode_id, 0) episodeid,
                D.CUR_ACCT_SEQ_NO CURACCTSEQNO,
                    TO_CHAR(d.admission_date_time, 'DD/MM/YYYY HH24:MI') admission_date_time,
                    cur_ward_code,
                    cur_bed_num bed_num,
                    cur_bed_class_code,
                    c.national_id_num,
                    c.date_of_birth,
                    DECODE(c.sex, 'M', 'male', 'F', 'female') gender,
                    -- e.full_name,
                    TO_CHAR(SYSDATE, 'DD/MM/YYYY HH24:MI') doc_date_time,   
                    NVL(d.approved_amt, 0) approved_amt,
                    d.credit_auth_ref,
                    d.credit_auth_date,
                    NVL(d.tot_unadj_dep_amt, 0) tot_unadj_dep_amt,
                    NVL(d.tot_unadj_prep_amt, 0) tot_unadj_prep_amt,
                    NVL(d.tot_unadj_dep_amt, 0) + NVL(d.tot_unadj_prep_amt, 0) deposit_amt,
                    NVL(d.tot_unbld_amt, 0) total_bill_amount,
                    NVL(d.tot_unadj_dep_amt, 0) + NVL(d.tot_unadj_prep_amt, 0) advancepaid,
                    ABS(NVL(d.tot_unbld_amt, 0) -
                        (NVL(d.tot_unadj_dep_amt, 0) + NVL(d.tot_unadj_prep_amt, 0))) due_amt_act,
                    NVL(d.tot_unbld_amt, 0) -
                    (NVL(d.tot_unadj_dep_amt, 0) + NVL(d.tot_unadj_prep_amt, 0)) due_amt_cr,
                    b.cur_physician_id cur_physician_id,
                    g.long_desc,
                    h.contact1_relation,
                    h.contact1_name contact1_name,
                    c.other_contact_num  res1_tel_no,
                    d.episode_type episodetype,
                    d.blng_grp_id blnggrpid
                FROM ip_episode          b,   
                    mp_patient_mast     c,
                    bl_episode_fin_dtls d,
                    pr_encounter        a,
                    bl_blng_grp         g,
                    mp_pat_rel_contacts h
                WHERE d.operating_facility_id  in ({facility_code})
                AND d.episode_type IN ('D', 'I')
                AND d.operating_facility_id = b.facility_id
                AND d.episode_id = b.episode_id
                AND d.patient_id = b.patient_id
                AND NVL(d.discharge_bill_gen_ind, 'N') != 'Y'
                AND d.episode_id IN
                    (SELECT open_episode_id
                        FROM ip_open_episode
                        WHERE facility_id  in ({facility_code}))
                AND d.patient_id = c.patient_id
                AND b.facility_id = a.facility_id
                AND b.episode_id = a.encounter_id
                --AND cur_ward_code BETWEEN NVL(:l_fr_ward_code, '!!!!') AND
                --NVL(:l_to_ward_code, '~~~~')
                --AND d.episode_id BETWEEN NVL(:l_fr_episode_id, 0) AND
                    --NVL(:l_to_episode_id, 99999999)
                --AND c.patient_id BETWEEN NVL(:nd_fm_patient_id, '!!!!!!!!!!!!!!!!!!!!') AND
                    --NVL(:nd_to_patient_id, '~~~~~~~~~~~~~~~~~~~~')
                AND h.patient_id(+) = d.patient_id
                AND d.blng_grp_id = g.blng_grp_id
                ORDER BY 5, 1
                )
                )



"""

        # l_to_ward_code = None
        # l_fr_ward_code = None
        # l_fr_episode_id = None
        # nd_to_patient_id = None
        # nd_fm_patient_id = None
        # l_to_episode_id = None

        self.cursor.execute(
            due_deposit_report_qurey,
            # [
            #     l_to_ward_code,
            #     l_fr_ward_code,
            #     l_fr_episode_id,
            #     nd_to_patient_id,
            #     nd_fm_patient_id,
            #     l_to_episode_id,
            # ],
        )
        due_deposit_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        # if self.cursor:
        #     self.cursor.close()
        # if self.ora_db:
        #     self.ora_db.close()

        return due_deposit_report_data, column_name

    def get_transfer_ar_report(
        self, from_date, to_date, nd_episode_type, facility_code
    ):
        transfer_ar_report_qurey = f""" 




    SELECT   --doc_type_code || ' / ' || doc_num BILL_NUM,
         TRUNC (trx_date) doc_date, a.patient_id,
         mp_get_desc.mp_patient (a.patient_id, 1) pat_name,
         SUM (a.distribution_amt * -1) bill_amount,
         (CASE
             WHEN a.cust_code IS NOT NULL
                THEN SUM (a.distribution_amt * -1)
             ELSE 0
          END
         ) pay_by_comp,
         
         --   DECODE(b.cust_code, null, 0, SUM( a.DISTRIBUTION_AMT *-1)) pay_by_comp,
         stragg (b.doc_type_code || ' / ' || b.doc_num || '  ') multi_bill,
         a.episode_type, a.episode_id, NVL (a.cust_code, 'X') cust_code,
         b.added_by_id,d.APPL_USER_NAME
        FROM bl_gl_distribution a, bl_bill_hdr b
        LEFT JOIN SM_APPL_USER D ON b.added_by_id = D.APPL_USER_ID
   WHERE a.operating_facility_id in ({facility_code})
     AND a.trx_date = b.doc_date
     AND a.doc_type = b.doc_type_code
     AND a.doc_no = b.doc_num
     AND a.trx_date BETWEEN :from_date and to_date(:to_date)  +1 
     AND a.trx_type_code = 'B'
     AND a.main_acc1_code IN (222410)
     AND NVL (b.bill_status, 'X') != 'C'
--&P_outstnd_where
     AND a.patient_id = b.patient_id
     AND a.episode_type = b.episode_type
     AND NVL(a.episode_id,0) = NVL(b.episode_id,0)
     AND a.distribution_amt <> 0
--     AND (a.patient_id BETWEEN :patient_id_fm AND :patient_id_to)
--    AND (   (:p_billtype = 'C' AND a.cust_code IS NULL)
--          OR (:p_billtype = 'I' AND a.cust_code IS NOT NULL)
 --         OR :p_billtype = 'B'
--         )
     AND a.episode_type in {nd_episode_type}
GROUP BY TRUNC (trx_date),
         a.patient_id,
         a.episode_type,
         a.episode_id,
         a.cust_code,
         b.added_by_id,
         d.APPL_USER_NAME
UNION ALL
SELECT   --doc_type_code || ' / ' || doc_num BILL_NUM,
         TRUNC (trx_date) doc_date, a.patient_id,
         mp_get_desc.mp_patient (a.patient_id, 1) pat_name,
         SUM (a.distribution_amt * -1) bill_amount,
         (CASE
             WHEN a.cust_code IS NOT NULL
                THEN SUM (a.distribution_amt * -1)
             ELSE 0
          END
         ) pay_by_comp,         
         --   DECODE(b.cust_code, null, 0, SUM( a.DISTRIBUTION_AMT *-1)) pay_by_comp,
--         stragg (c.adj_doc_type_code || ' / ' || c.adj_doc_num || '  ') multi_bill,
c.doc_type_code||'/'||c.doc_num multi_bill,
         a.episode_type, a.episode_id, NVL (a.cust_code, 'X') cust_code,
         b.added_by_id,d.APPL_USER_NAME
        FROM bl_gl_distribution a, bl_bill_adj_hdr b, bl_bill_adj_dtl c, SM_APPL_USER D  
   WHERE a.operating_facility_id in ({facility_code})
     AND a.trx_date = b.doc_date
     AND a.doc_type = b.doc_type_code
     AND a.doc_no = b.doc_num
     AND c.doc_type_code = b.doc_type_code
     AND c.doc_num = b.doc_num
     AND a.trx_date BETWEEN :from_date and to_date(:to_date)  +1 
     AND a.trx_type_code = 'B'
     AND a.main_acc1_code IN (222410)
     AND NVL (b.status, 'X') != 'C'
--&P_outstnd_where
     AND a.patient_id = b.patient_id
     AND a.episode_type = c.episode_type
     AND NVL(a.episode_id,0) = NVL(c.episode_id,0)
--   AND a.distribution_amt < 0
--     AND (a.patient_id BETWEEN :patient_id_fm AND :patient_id_to)
--     AND (   (:p_billtype = 'C' AND a.cust_code IS NULL)
--          OR (:p_billtype = 'I' AND a.cust_code IS NOT NULL)
--          OR :p_billtype = 'B'
--         )
     AND a.episode_type in {nd_episode_type}
GROUP BY TRUNC (trx_date),
         a.patient_id,
         c.doc_type_code||'/'||c.doc_num,
         a.episode_type,
         a.episode_id,
         a.cust_code,
         b.added_by_id,
         d.APPL_USER_NAME
ORDER BY 1, 2


"""

        self.cursor.execute(transfer_ar_report_qurey, [from_date, to_date])
        transfer_ar_report_qurey = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return transfer_ar_report_qurey, column_name

    def close_connection(self):
        if self.cursor:
            self.cursor.close()

        if self.ora_db:
            self.ora_db.close()

    def get_ehc_operation_report(self, facility_code, from_date, to_date):
        ehc_operation_report_qurey = f""" 
        
select distinct pack.patient_id,pack.NAME_PREFIX,pack.FIRST_NAME,pack.SECOND_NAME,pack.FAMILY_NAME,
TO_CHAR (pack.ADDED_DATE,'DD-Mon-YYYY'),pack.LONG_DESC,B.LONG_DESC Service_name,a.blng_serv_code, 
a.trx_date,T.PRACTITIONER_NAME,T.primary_speciality_code,a.serv_item_desc,A.ORG_GROSS_CHARGE_AMT from bl_patient_charges_folio a,bl_blng_serv b,am_practitioner t, 
(select E.patient_id,E.EPISODE_ID,M.NAME_PREFIX,M.FIRST_NAME,M.SECOND_NAME,M.FAMILY_NAME,H.ADDED_DATE,P.LONG_DESC  from  
mp_patient M,pr_encounter E,bl_package_sub_hdr h,bl_package p,bl_package_encounter_dtls f  
where e.specialty_code ='EHC' 
and M.PATIENT_ID =E.PATIENT_ID and E.ADDED_FACILITY_ID in ({facility_code}) and H.PACKAGE_CODE=P.PACKAGE_CODE and f.PACKAGE_SEQ_NO = h.PACKAGE_SEQ_NO and f.PACKAGE_CODE = h.PACKAGE_CODE 
and f.PATIENT_ID =h.PATIENT_ID and f.ENCOUNTER_ID = e.EPISODE_ID  
and h.status='C' and p.OPERATING_FACILITY_ID in ({facility_code}) and h.added_date between :from_date and :to_date )pack 
where pack.patient_id=a.patient_id and NVL(trx_STATUS,'X')<>'C'and a.trx_date >pack.added_date and A.BLNG_SERV_CODE =B.BLNG_SERV_CODE(+) 
and A.PHYSICIAN_ID=T.PRACTITIONER_ID(+) 
and a.blng_Serv_code not in ('HSPK000001') and  a.OPERATING_FACILITY_ID in ({facility_code})
and pack.added_date between :from_date and to_date(:to_date) + 1


"""

        self.cursor.execute(ehc_operation_report_qurey, [from_date, to_date])
        ehc_operation_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return ehc_operation_report_data, column_name

    def get_ehc_operation_report_2(self, facility_code, from_date, to_date):
        ehc_operation_report_2_qurey = f""" 
        
 select distinct  P.LONG_DESC, H.ADDED_DATE, E.patient_id, M.NAME_PREFIX, M.FIRST_NAME, M.SECOND_NAME, 
 M.FAMILY_NAME, f.CUST_CODE, c.LONG_NAME ,f.BILL_DOC_DATE 
 from mp_patient M,pr_encounter E,bl_patient_charges_folio f,bl_package_sub_hdr h,bl_package p,ar_customer c  
 where e.specialty_code ='EHC' and M.PATIENT_ID =E.PATIENT_ID and E.EPISODE_ID=F.EPISODE_ID and e.FACILITY_ID in ({facility_code})
 and p.ADDED_FACILITY_ID in ({facility_code}) and F.PACKAGE_SEQ_NO=H.PACKAGE_SEQ_NO and H.PACKAGE_CODE=P.PACKAGE_CODE and c.cust_code(+) = f.CUST_CODE 
  and h.status='C' and h.added_date between :from_date and to_date(:to_date)+1  and p.OP_YN='Y' order by  H.ADDED_DATE

"""

        self.cursor.execute(
            ehc_operation_report_2_qurey,
            [from_date, to_date],
        )
        ehc_operation_report_2_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return ehc_operation_report_2_data, column_name

    def get_oncology_drugs_report(self, facility_code, from_date, to_date):
        oncology_drugs_report_qurey = f""" 
        
SELECT distinct d.long_desc,a.ADDED_DATE,a.ADDED_FACILITY_ID,a.DOC_NO,a.DOC_SRL_NO,a.DOC_TYPE_CODE, 
a.ITEM_CODE,c.long_desc,(a.SAL_ITEM_QTY-a.RET_ITEM_QTY) SAL_ITEM_QTY,b.encounter_id,b.patient_id,e.PATIENT_NAME, a.ADDED_AT_WS_NO,a.ADDED_BY_ID 
FROM ST_SAL_DTL_EXP  a ,ST_SAL_HDR b , mm_item c,MM_STORE d, mp_patient e 
where (a.doc_no = b.doc_no) and (a.item_code = c.item_code) and (a.store_code = d.store_code) and (a.SAL_ITEM_QTY-a.RET_ITEM_QTY) > 0  
and  a.added_facility_id in ({facility_code}) AND b.ADDED_FACILITY_ID in ({facility_code}) and  b.PATIENT_ID=e.PATIENT_ID and 
a.item_code in ('2000045213','2000045761','2000043187','2000048184','2000049844','2000047877','2000047579','2000051797', 
 '2000038532','2000043071','2000058396','2000024382','2000051697','2000047878','2000023973','2000058197','2000019952','2000053939', 
'2000055419','2000051706','2000029792','2000052924','2000059375','2000017355','2000023833','2000024381','2000056129','2000023975', 
'2000038531','2000052744','2000060598','2000059374','2000019945','2000052743','2000058729','2000051550','2000059506','2000018369','2000047003')  
and a.ADDED_DATE between  :from_date and to_date(:to_date)+1 order by a.added_date


"""

        self.cursor.execute(
            oncology_drugs_report_qurey,
            [from_date, to_date],
        )
        oncology_drugs_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return oncology_drugs_report_data, column_name

    def get_radiology_tat_report(self, facility_code, from_date, to_date):
        get_radiology_tat_report_query = f"""
        
        select distinct TO_CHAR (r.EXAM_DATE_TIME , 'DD/MM/YY') ser_date,TO_CHAR (r.EXAM_DATE_TIME, 'HH24:MI:SS') ser_time, 
        r.EXAM_CODE serv_code, c.long_desc serv_desc,l.ORDER_QTY,
        DECODE (o.patient_class ,'IP', 'IP','OP', 'OP','EM', 'Emergency','R', 'Referral','D', 'Daycare') pat_Type,
        r.patient_id pat_id, b.short_name pat_name, o.patient_class,o.ord_date_time,r.START_TIME,r.END_TIME
        from or_order o,rd_exam_view_requested r,mp_patient_mast b,         bl_blng_serv c,or_order_line l
        where r.order_id=o.order_id and o.ORDER_TYPE_CODE in (select order_type_code from rd_section)
        --and o.ord_date_time between '1-Aug-2015' and '07-Aug-2015' 
        and r.END_TIME is NOT NULL
        and o.ORDERING_FACILITY_ID in ({facility_code})
        and r.ORDER_ID =l.ORDER_ID
        and r.ORDER_LINE_NO = l.ORDER_LINE_NUM
        AND r.patient_id = b.patient_id
        AND r.EXAM_CODE = c.blng_serv_code
        and NVL(o.BILL_YN,'N') = decode(o.PATIENT_CLASS ,'OP','Y','EM','Y','R','Y',NVL(o.BILL_YN,'N'))
        AND r.EXAM_DATE_TIME between :from_date and to_date(:to_date) + 1
 

"""
        self.cursor.execute(get_radiology_tat_report_query, [from_date, to_date])
        get_radiology_tat_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_radiology_tat_report_data, column_name

    def get_day_care_report(self, from_date, to_date):
        get_day_care_report_query = """
        
        SELECT a.patient_id,b.PATIENT_NAME,TRUNC(a.VISIT_ADM_DATE_TIME) Admission_Date,A.ASSIGN_CARE_LOCN_CODE, 
        A.ASSIGN_BED_CLASS_CODE,E.LONG_DESC,a.ASSIGN_BED_NUM Bed_Num,c.PRACTITIONER_NAME Treating_Doctor,d.LONG_DESC Speciality,A.ASSIGN_BED_CLASS_CODE, f.BLNG_GRP_ID
        FROM pr_encounter a, mp_patient b,am_practitioner c,am_speciality d,ip_bed_class e,bl_episode_fin_dtls f 
        ,mp_country m
        WHERE a.PATIENT_ID=b.PATIENT_ID AND a.ATTEND_PRACTITIONER_ID =c.PRACTITIONER_ID 
        and  a.PATIENT_ID=f.PATIENT_ID and A.episode_id = f.episode_id
        AND a.patient_class = 'IP'  AND a.SPECIALTY_CODE = d.SPECIALITY_CODE 
        and m.COUNTRY_CODE=b.NATIONALITY_CODE
        and A.ASSIGN_BED_CLASS_CODE = E.BED_CLASS_CODE and a.cancel_reason_code is null AND a.VISIT_ADM_DATE_TIME between :from_date and to_date(:to_date)+1 
        and A.ASSIGN_BED_CLASS_CODE in ('DC','SU')
        and A.FACILITY_ID = 'KH'
        ORDER BY A.ASSIGN_CARE_LOCN_CODE
 

"""
        self.cursor.execute(get_day_care_report_query, [from_date, to_date])
        get_day_care_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_day_care_report_data, column_name

    def get_ot_scheduling_list_report(self):
        get_ot_scheduling_list_report_query = """
        
select a.patient_id,b.patient_name,get_age(b.date_of_birth,SYSDATE) Age,b.sex,C.ORDER_ID,C.ORDER_CATALOG_CODE,C.CATALOG_DESC, 
a.pref_surg_date, D.PRACTITIONER_NAME,E.LONG_DESC,a.added_date,dbms_lob.substr(f.ORDER_COMMENT,5000,1) 
from ot_pending_order a,mp_patient b, or_order_line c,AM_PRACTITIONER d,AM_SPECIALITY e,or_order_comment f  
where a.patient_id = b.patient_id and a.order_id = c.order_id and A.PHYSICIAN_ID = D.PRACTITIONER_ID and a.order_id = f.order_id(+) 
and D.PRIMARY_SPECIALITY_CODE = E.SPECIALITY_CODE and PREF_SURG_DATE = to_date(sysdate)+1

"""
        self.cursor.execute(get_ot_scheduling_list_report_query)
        get_ot_scheduling_list_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_ot_scheduling_list_report_data, column_name

    def get_non_package_covid_patient_report(self):
        non_package_covid_patient_report_query = """
        
select distinct E.patient_id,E.ENCOUNTER_ID ,M.NAME_PREFIX,M.FIRST_NAME,M.SECOND_NAME,M.FAMILY_NAME,E.NURSING_UNIT_CODE,E.BED_TYPE_CODE,E.ADMISSION_DATE_TIME,E.BED_CLASS_CODE,
E.BED_NUM from mp_patient M,ip_open_encounter E,IP_aDT_trn I where M.PATIENT_ID = E.PATIENT_ID AND I.ENCOUNTER_ID = E.ENCOUNTER_ID(+) AND I.PATIENT_ID = E.PATIENT_ID(+) 
 and e.ADMISSION_DATE_TIME >= '21-Jul-2021'
and (I.FR_BED_NO in ('5018','5018A','5019','5019A','5020','5020A','5021','5021A','5022','5022A','5023','5023A','5024','5024A','13083','13083A','13084','13084A','13085','13085A','13086','13086A','13087','13087A','13088','13088A',
'13089','13089A','13090','13090A','13091','13091A','13092','13092A','13093','13093A','13094','13094A','13095','13095A' ,'13096','13096A','13097','13097A','13098','13098A','13098B','13098C','13098D','13098E','13098F' )
or I.TO_BED_NO in ('5018','5018A','5019','5019A','5020','5020A','5021','5021A','5022','5022A','5023','5023A','5024','5024A','13083','13083A','13084','13084A','13085','13085A','13086','13086A','13087','13087A','13088','13088A',
'13089','13089A','13090','13090A','13091','13091A','13092','13092A','13093','13093A','13094','13094A','13095','13095A' ,'13096','13096A','13097','13097A','13098','13098A','13098B','13098C','13098D','13098E','13098F'))
minus 
select distinct E.patient_id,E.ENCOUNTER_ID ,c.NAME_PREFIX,c.FIRST_NAME,c.SECOND_NAME,c.FAMILY_NAME,E.NURSING_UNIT_CODE,E.BED_TYPE_CODE,E.ADMISSION_DATE_TIME,E.BED_CLASS_CODE, 
E.BED_NUM from BL_PACKAGE_SUB_HDR d, bl_package b,mp_patient c, ip_open_encounter E,bl_package_encounter_dtls f, IP_aDT_trn I where d.PACKAGE_CODE = B.PACKAGE_CODE 
and c.PATIENT_ID = e.PATIENT_ID and f.PACKAGE_SEQ_NO = d.PACKAGE_SEQ_NO and f.PACKAGE_CODE = d.PACKAGE_CODE AND I.ENCOUNTER_ID = E.ENCOUNTER_ID AND I.PATIENT_ID = E.PATIENT_ID 
and f.PATIENT_ID = d.PATIENT_ID and f.ENCOUNTER_ID = e.ENCOUNTER_ID and d.PATIENT_ID = C.PATIENT_ID and b.PACKAGE_CODE = 'COVID19' and e.FACILITY_ID = 'KH' 
and e.ADMISSION_DATE_TIME >= '21-Jul-2021'




"""
        self.cursor.execute(non_package_covid_patient_report_query)
        non_package_covid_patient_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return non_package_covid_patient_report_data, column_name

    def get_gx_flu_a_flu_b_rsv(self, from_date, to_date):
        gx_flu_a_flu_b_rsv_qurey = """ 

        SELECT  DISTINCT  o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID,
        Patient_Name as "Patient Name",map.SEX,trunc((sysdate-map.DATE_OF_BIRTH)/365,0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code
        --,consultant_code,p.practitioner_name
        , t.RESULT_COMMENT_DESC1 text ,map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,
        F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,
        g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state
        FROM or_order o,OR_ORDER_LINE L,RL_REQUEST_HEADER A,RL_test_result t,pr_encounter e,
        bl_episode_fin_dtls b ,mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g,  MP_RES_TOWN h , MP_RES_AREA i, mp_region j--,am_practitioner p
        WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMB000097'
        and a.PATIENT_ID = map.PATIENT_ID
        and f.POSTAL1_CODE = g.POSTAL_CODE (+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+)
        and i.REGION_CODE = j.REGION_CODE(+) AND  A.PATIENT_ID=F.PATIENT_ID --and consultant_code=p.PRACTITIONER_ID(+)
        and t.SPECIMEN_NO(+)=a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+)= o.ORDER_STATUS
        and t.TEST_CODE in ('COMMENTONE')--('PCRSPEC','PCRSARS','PCRMETH','PCRINS')
        and  o.PATIENT_ID=b.PATIENT_ID and o.episode_id = b.episode_id
        and e.PATIENT_ID =o.PATIENT_ID and e.EPISODE_ID=o.EPISODE_ID AND o.ORD_DATE_TIME between :from_date and to_date(:to_date) + 1






"""

        self.cursor.execute(gx_flu_a_flu_b_rsv_qurey, [from_date, to_date])
        gx_flu_a_flu_b_rsv_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return gx_flu_a_flu_b_rsv_data, column_name

    def get_h1n1_detection_by_pcr(self, from_date, to_date):
        h1n1_detection_by_pcr_qurey = """ 

        SELECT  DISTINCT L.ORDER_CATALOG_CODE ,t.TEST_CODE ,o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID,
        Patient_Name as "Patient Name",map.SEX,trunc((sysdate-map.DATE_OF_BIRTH)/365,0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code
        --,consultant_code,p.practitioner_name
        , t.RESULT_COMMENT_DESC1 text ,map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,
        F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,
        g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state
        FROM or_order o,OR_ORDER_LINE L,RL_REQUEST_HEADER A,RL_test_result t,pr_encounter e,
        bl_episode_fin_dtls b ,mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g,  MP_RES_TOWN h , MP_RES_AREA i, mp_region j--,am_practitioner p
        WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'H1N1ONE'
        and a.PATIENT_ID = map.PATIENT_ID
        and f.POSTAL1_CODE = g.POSTAL_CODE (+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+)
        and i.REGION_CODE = j.REGION_CODE(+) AND  A.PATIENT_ID=F.PATIENT_ID --and consultant_code=p.PRACTITIONER_ID(+)
        and t.SPECIMEN_NO(+)=a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+)= o.ORDER_STATUS
        and t.TEST_CODE in ('COMMENTONE')--('PCRSPEC','PCRSARS','PCRMETH','PCRINS')
        and  o.PATIENT_ID=b.PATIENT_ID and o.episode_id = b.episode_id
        and e.PATIENT_ID =o.PATIENT_ID and e.EPISODE_ID=o.EPISODE_ID AND o.ORD_DATE_TIME between :from_date and to_date(:to_date) + 1



"""

        self.cursor.execute(h1n1_detection_by_pcr_qurey, [from_date, to_date])
        h1n1_detection_by_pcr_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return h1n1_detection_by_pcr_data, column_name

    def get_biofire_respiratory(self, from_date, to_date):
        biofire_respiratory_qurey = """ 

        SELECT  DISTINCT o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID,
        Patient_Name as "Patient Name",map.SEX,trunc((sysdate-map.DATE_OF_BIRTH)/365,0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code
        --,consultant_code,p.practitioner_name
        , t.RESULT_COMMENT_DESC1 text ,map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,
        F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,
        g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state
        FROM or_order o,OR_ORDER_LINE L,RL_REQUEST_HEADER A,RL_test_result t,pr_encounter e,
        bl_episode_fin_dtls b ,mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g,  MP_RES_TOWN h , MP_RES_AREA i, mp_region j--,am_practitioner p
        WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMB000068' and a.PATIENT_ID = map.PATIENT_ID
        and f.POSTAL1_CODE = g.POSTAL_CODE (+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+)
        and i.REGION_CODE = j.REGION_CODE(+) AND  A.PATIENT_ID=F.PATIENT_ID --and consultant_code=p.PRACTITIONER_ID(+)
        and t.SPECIMEN_NO(+)=a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+)= o.ORDER_STATUS
        and t.TEST_CODE in ('RESULTONE')--('PCRSPEC','PCRSARS','PCRMETH','PCRINS')
        and  o.PATIENT_ID=b.PATIENT_ID and o.episode_id = b.episode_id
        and e.PATIENT_ID =o.PATIENT_ID and e.EPISODE_ID=o.EPISODE_ID AND o.ORD_DATE_TIME between :from_date and to_date(:to_date) + 1



"""

        self.cursor.execute(biofire_respiratory_qurey, [from_date, to_date])
        biofire_respiratory_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return biofire_respiratory_data, column_name

    def get_covid_19_report_with_pincode_and_ward(self, from_date, to_date):
        covid_19_report_with_pincode_and_ward_qurey = """ 

        SELECT o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID,
        Patient_Name as "Patient Name",map.SEX,trunc((sysdate-map.DATE_OF_BIRTH)/365,0) age, o.PATIENT_CLASS, test_code,t.result_text result--,consultant_code,p.practitioner_name 
        ,map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO, 
        F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address ,  
        g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state  FROM or_order o,OR_ORDER_LINE L,RL_REQUEST_HEADER A,RL_result_text t,
        mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g,  MP_RES_TOWN h , MP_RES_AREA i, mp_region j--,am_practitioner p 
        WHERE o.ORDER_ID = A.ORDER_ID(+) AND L.ORDER_CATALOG_CODE = 'LMMB000094' 
        and a.PATIENT_ID = map.PATIENT_ID
        and f.POSTAL1_CODE = g.POSTAL_CODE (+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+)
        and i.REGION_CODE = j.REGION_CODE(+)
        AND  A.PATIENT_ID=F.PATIENT_ID (+)
        --and consultant_code=p.PRACTITIONER_ID(+)
        and t.SPECIMEN_NO (+) =a.SPECIMEN_NO 
        AND o.ORDER_ID = l.ORDER_ID 
        and s.ORDER_STATUS_CODE(+)= o.ORDER_STATUS 
        AND o.ORD_DATE_TIME between :from_date and to_date(:to_date) + 1



"""

        self.cursor.execute(
            covid_19_report_with_pincode_and_ward_qurey, [from_date, to_date]
        )
        covid_19_report_with_pincode_and_ward_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return covid_19_report_with_pincode_and_ward_data, column_name

    def get_cbnaat_covid_report_with_pincode(self, from_date, to_date):
        cbnaat_covid_report_with_pincode_qurey = """ 

        SELECT  o.ord_date_time,SPEC_REGD_DATE_TIME,s.long_desc orderstatus,l.modified_date stat_change_date,CATALOG_DESC,A.PATIENT_ID,
        Patient_Name as "Patient Name",map.SEX,trunc((sysdate-map.DATE_OF_BIRTH)/365,0) age, o.PATIENT_CLASS,b.BLNG_GRP_ID,b.cust_code,b.remark
        test_code,t.result_text result--,consultant_code,p.practitioner_name
        ,map.EMAIL_ID,map.CONTACT1_NO,map.CONTACT2_NO,map.CONTACT3_NO,map.CONTACT4_NO,
        F.addr1_line1 || ' ' || F.addr1_line2 || ' ' || F.addr1_line3 || ' ' || F.addr1_line4 Address , 
        g.LONG_DESC postalcode, h.LONG_DESC area, i.LONG_DESC town, j.LONG_DESC state  FROM or_order o,OR_ORDER_LINE L,RL_REQUEST_HEADER A,RL_result_text t,pr_encounter e,
        bl_episode_fin_dtls b ,mp_patient map,or_order_status_code s, MP_PAT_ADDRESSES F ,  MP_POSTAL_CODE g,  MP_RES_TOWN h , MP_RES_AREA i, mp_region j--,am_practitioner p
        WHERE o.ORDER_ID = A.ORDER_ID AND L.ORDER_CATALOG_CODE = 'LMMC000227' and a.PATIENT_ID = map.PATIENT_ID
        and f.POSTAL1_CODE = g.POSTAL_CODE (+) and g.RES_TOWN_CODE = h.RES_TOWN_CODE(+) and h.RES_AREA_CODE = i.RES_AREA_CODE(+)
        and i.REGION_CODE = j.REGION_CODE(+) AND  A.PATIENT_ID=F.PATIENT_ID --and consultant_code=p.PRACTITIONER_ID(+)
        and t.SPECIMEN_NO(+)=a.SPECIMEN_NO AND o.ORDER_ID = l.ORDER_ID and s.ORDER_STATUS_CODE(+)= o.ORDER_STATUS
        and  o.PATIENT_ID=b.PATIENT_ID and o.episode_id = b.episode_id
        and e.PATIENT_ID =o.PATIENT_ID and e.EPISODE_ID=o.EPISODE_ID AND o.ORD_DATE_TIME between :from_date and to_date(:to_date) + 1



"""

        self.cursor.execute(
            cbnaat_covid_report_with_pincode_qurey, [from_date, to_date]
        )
        cbnaat_covid_report_with_pincode_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return cbnaat_covid_report_with_pincode_data, column_name

    def get_mucormycosis_report(self, from_date, to_date):
        mucormycosis_report_qurey = """ 

        select b.PATIENT_ID,d.PATIENT_NAME,b.SOURCE_CODE,a.SPECIMEN_NO,b.SPEC_REGD_DATE_TIME,
        a.GROUP_TEST_CODE,a.TEST_CODE,a.RESULT_COMMENT_DESC1||' '||a.RESULT_COMMENT_DESC2
        from rl_test_result a,rl_request_header b,mp_patient d
        where
        a.SPECIMEN_NO=b.SPECIMEN_NO and
        b.PATIENT_ID=d.PATIENT_ID and
        --a.SPECIMEN_NO = '3121003099' and
        a.GROUP_TEST_CODE in ('CULTSENSFU','KOHMOUNTT') and 
        a.TEST_CODE in ('CULT11','RESULT1','SPECIMEN11','KOHMOUNT2','SPEC105') and 
        --(a.RESULT_COMMENT_DESC1 is not null or a.RESULT_COMMENT_DESC2 is not null) and 
        b.SPEC_REGD_DATE_TIME between :from_date and to_date(:to_date) + 1
        order by b.SPEC_REGD_DATE_TIME,a.SPECIMEN_NO,a.TEST_SEQ_NO 



"""

        self.cursor.execute(mucormycosis_report_qurey, [from_date, to_date])
        mucormycosis_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return mucormycosis_report_data, column_name

    def get_patient_registration_report(self, from_date, to_date):
        get_patient_registration_report_query = """
        
SELECT b.NAME_PREFIX,b.FIRST_NAME,b.FAMILY_NAME,b.SEX Gender,b.PAT_CAT_CODE, get_age(b.date_of_birth,SYSDATE) Age ,b.date_of_birth, 
m.LONG_DESC nationality, k.ADDR1_LINE1,k.ADDR1_LINE2,k.ADDR1_LINE3,k.ADDR1_LINE4 ,p.LONG_DESC postal_code, m.long_name country, 
b.email_id,b.CONTACT2_NO,r.CONTACT1_Name,r.CONTACT1_RELATION,r.CONTACT1_MOB_TEL_NO,b.ADDED_BY_ID,C.aPPL_USER_NAME ADDED_BY_NAME, 
b.patient_id,b.PATIENT_NAME,b.REGN_DATE 
FROM mp_patient b, mp_country m,mp_pat_addresses k, mp_postal_code p,mp_pat_rel_contacts r, SM_aPPL_USER C 
WHERE b.patient_id = k.patient_id(+) 
and b.ADDED_BY_ID = c.APPL_USER_ID(+) 
and k.POSTAL2_CODE = p.POSTAL_CODE(+) 
and m.COUNTRY_CODE = b.NATIONALITY_CODE 
and b.patient_id = r.patient_id(+) 
and nvl(r.CONTACT1_ROLE,'NEXT')= 'NEXT' 
and b.REGN_DATE between :from_date and to_date(:to_date)+1


"""
        self.cursor.execute(get_patient_registration_report_query, [from_date, to_date])
        get_patient_registration_report_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return get_patient_registration_report_data, column_name

    def get_run_query_directly(self, sql_query):
        self.cursor.execute(sql_query)
        sql_data = self.cursor.fetchall()

        column_name = [i[0] for i in self.cursor.description]

        if self.cursor:
            self.cursor.close()
        if self.ora_db:
            self.ora_db.close()

        return sql_data, column_name


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
