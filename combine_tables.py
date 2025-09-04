import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:2004@localhost:3306/callify")

query = """
SELECT
    ej.empnumber,
    ej.jobnumber,
    ej.NMAXSAL,
    ej.NMINEXP,
    ej.NMAXEXP,
    COALESCE(c.name,'Unknown') AS country_name,
    COALESCE(s.name,'Unknown') AS state_name,
    COALESCE(ci.name,'Unknown') AS city_name,
    COALESCE(zc.zip_code,'Unknown') AS zip_code,
    COALESCE(zc.area,'Unknown') AS location_area,
    ej.STRSKILLS,
    ej.audioLink,
    ej.flagStatus,
    ej.JOBSTATUS,
    ej.ISACTIVE,
    ej.JOBROLE,
    ej.rec_ivr_flow,
    ej.CALLERID,
    ej.DTLASTINVITE,
    ej.STRRECORDCOUNT,
    ej.ISCOPIED,
    ej.NEDITINGSTEP,
    ej.NINVITETYPE,
    ej.NTEMPLATEID,
    ej.NFORWARDPRPFILE,
    ej.NTIMEZONE,
    ej.STRWEBLINK,
    ej.NCUSTINTRN,
    ej.NIVRLANG,

    ji.nid,
    ji.empnumber AS ji_empnumber,
    ji.jobnumber AS ji_jobnumber,
    ji.name,
    ji.mobileNo,
    ji.countryCode,
    ji.emailid,
    ji.invite_dt,
    ji.email_set,
    ji.NCALLSTATUS,
    ji.res_call_sid,
    ji.req_call_sid,
    ji.knowlarity_status,
    ji.admin_status,
    ji.salary_preference,
    ji.NSMSSENT,
    ji.STRSMSREF,
    ji.SMSSENTDT,
    ji.INSTCALDT,
    ji.DTMF,
    ji.RESDT,
    ji.total_call,
    ji.CALMINUTES,
    ji.call_start_time,
    ji.call_end_time,
    ji.CALLTYPE,
    ji.SCHEDULEDTIME,
    ji.PID,
    ji.UPDATIONDATE,
    ji.upload_type,
    ji.DTUPDATEDMOBILE,
    ji.COMMENT,
    ji.NLEFTFOLOWUP,
    ji.NTIMEZONE,
    ji.STRREFID,
    ji.DTDRIVE,
    ji.STRLOCATION,
    ji.STRREFJDID,
    ji.STRDOCUMENTS,
    ji.NIVRTYPE,
    ji.NCALLIFYREFINVID,

    -- ✅ new field: all transcripts merged
    COALESCE(rt.transcripts, '') AS transcripts

FROM employerjob ej
LEFT JOIN jobinvite ji
    ON ej.empnumber = ji.empnumber
   AND ej.jobnumber = ji.jobnumber
LEFT JOIN location c
    ON ej.country = c.location_id
LEFT JOIN location s
    ON ej.state = s.location_id
LEFT JOIN location ci
    ON ej.city = ci.location_id
LEFT JOIN location_zip_codes zc
    ON ej.pin_code = zc.zip_id
LEFT JOIN (
    SELECT 
        NEMPID, 
        NJDID, 
        GROUP_CONCAT(STRTRANS ORDER BY NID SEPARATOR '** ') AS transcripts
    FROM recruiter_transcripts
    GROUP BY NEMPID, NJDID
) rt
    ON ej.empnumber = rt.NEMPID
   AND ej.jobnumber = rt.NJDID

ORDER BY ej.empnumber, ej.jobnumber, ji.nid
"""

output_file = "employerjob_jobinvite_transcripts_combined.csv"
chunksize = 50000   # adjust as needed

with engine.connect() as conn:
    first = True
    i = 0
    for chunk in pd.read_sql(query, conn, chunksize=chunksize):
        chunk.to_csv(output_file, mode="a", index=False, encoding="utf-8", header=first)
        i += 1
        print(f"✅ Wrote chunk {i} ({len(chunk)} rows)")
        first = False

print(f"\n✅ Export finished: {output_file}")
