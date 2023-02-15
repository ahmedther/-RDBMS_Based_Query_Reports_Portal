SELECT  sum(B.ADDL_CHARGE_AMT_IN_CHARGE) addl_charge, 
a.CUST_CODE, BILL_POSTED_FLAG, (a.doc_type_code || '/' || a.doc_num) bill_no,
         TRUNC (a.doc_date) bill_date, a.patient_id, a.episode_id,
         a.cust_code,
         (CASE
             WHEN a.cust_code IS NOT NULL
                THEN 'CR'
             ELSE 'CS'
          END) bill_type, NVL (a.gross_amt, 0) gross_amt,
         NVL (a.serv_disc_amt, 0) serdiscount,
         NVL (a.overall_disc_amt, 0) overall_disc,
         (a.serv_disc_amt + a.overall_disc_amt) tot_discounts,
         NVL (a.bill_amt, 0) net_amt, NVL (a.bill_tot_outst_amt, 0) out_amt
    FROM bl_bill_hdr a,bl_patient_charges_folio b
   WHERE NVL (a.bill_status, 'A') != 'C'
     AND a.operating_facility_id = :p_facility_id
     and a.operating_Facility_id=b.operating_facility_id
     and a.doc_type_code=b.bill_doc_type_code
     and a.doc_num=b.bill_doc_num
--     AND NVL (a.gross_amt, 0) != 0
and nvl(a.bill_amt,0) != 0
AND ( (NVL(a.BILL_POSTED_FLAG,'N')='Y' and :P_POSTED_BILLS='Y' and a.cust_Code is not null)
      or (:P_POSTED_BILLS='N' or a.cust_code is null))
     AND a.episode_type =
                 DECODE (:p_episode_type,
                         'A', a.episode_type,
                         :p_episode_type
                        )

     AND a.doc_date >=
            TO_DATE (NVL (:nd_period_from,
                          TO_DATE ('01/02/1978', 'DD/MM/YYYY')
                         ),
                     'DD/MM/YYYY'
                    )
     AND a.doc_date <
              TO_DATE (NVL (:nd_period_to,
                            TO_CHAR (SYSDATE + 1, 'DD/MM/YYYY')),
                       'DD/MM/YYYY'
                      )
            + 1
group by 
a.CUST_CODE, BILL_POSTED_FLAG, (a.doc_type_code || '/' || a.doc_num) ,
         TRUNC (a.doc_date) , a.patient_id, a.episode_id,
         a.gross_amt ,
         a.serv_disc_amt ,
         a.overall_disc_amt ,
         a.bill_amt , a.bill_tot_outst_amt 
ORDER BY 4