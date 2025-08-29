import pandas as pd
from sqlalchemy import create_engine

# ---------------------------
# Database connection details
# ---------------------------
username = "your_user"
password = "your_password"
host = "localhost"
port = "3306"
database = "your_db"

# Create SQLAlchemy engine
engine = create_engine("mysql+pymysql://root:2004@localhost:3306/callify")

# ---------------------------
# SQL Query: employerjob + jobinvite + location
# ---------------------------
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
    ji.NCALLIFYREFINVID


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

ORDER BY ej.empnumber, ej.jobnumber, ji.nid;
"""

# ---------------------------
# Run query & load into DataFrame
# ---------------------------
with engine.connect() as conn:
    df = pd.read_sql(query, conn)

# ---------------------------
# Save to CSV
# ---------------------------
output_file = "employerjob_jobinvite_combined.csv"
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"✅ Data exported successfully to {output_file}")
