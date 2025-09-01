import pandas as pd
from sqlalchemy import create_engine

# MySQL connection
engine = create_engine("mysql+pymysql://root:2004@localhost:3306/callify")
# SQL query
query = """
SELECT
    -- Employer Job
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
    ej.STRSKILLS AS job_skills,
    ej.audioLink AS job_audio,
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

    -- Job Response
    jr.NID AS jr_NID,
    jr.CVSCORE,
    jr.COMSCORE,
    jr.responsedate,
    jr.audiolink AS jr_audio,
    jr.CANDIDATERANK,
    jr.call_sid,
    jr.call_duration,
    jr.userid,
    jr.salary_preference AS jr_salary_preference,
    jr.available_in AS jr_available_in,
    jr.exp_salary AS jr_exp_salary,
    jr.interview_time AS jr_interview_time,
    jr.sys_cv_score,
    jr.sys_comm_score,
    jr.STRSKILLS AS jr_skills,
    jr.CUST_RESP,
    jr.STRCONURL,
    jr.upload_type,
    jr.DTMFAnswer,
    jr.NAUDIOSCORE,
    jr.NSTATUS,
    jr.NATTEMPTS,
    jr.DTRESCH,
    jr.DTSLOTSTART,
    jr.DTSLOTEND,
    jr.CANSWERSCORE,
    jr.CANSWERSCORES,
    jr.CSKILLSMATCHED,
    jr.NVIEWED,

    -- Candidate Details
    cd.NID AS cd_NID,
    cd.usernumber,
    cd.firstname,
    cd.lastname,
    cd.mobileno,
    cd.country AS cd_country,
    cd.state AS cd_state,
    cd.city AS cd_city,
    cd.countrycode,
    cd.jobdomain,
    cd.jobseekingstatus,
    cd.profilecreated_dt,
    cd.upload_photo,
    cd.upload_cv,
    cd.available_in AS cd_available_in,
    cd.exp_salary AS cd_exp_salary,
    cd.portfolio_links,
    cd.personality_score,
    cd.interview_time AS cd_interview_time,
    cd.salary_preference AS cd_salary_preference,
    cd.summary,
    cd.is_photo_upload,
    cd.is_cv_upload,
    cd.pin_code,
    cd.NPSCORE,
    cd.NMOBILEUPDATES,
    cd.DTUPDATEDMOBILE

FROM employerjob ej
LEFT JOIN jobresponse jr
    ON ej.jobnumber = jr.jobnumber
LEFT JOIN candidatedetails cd
    ON jr.userid = cd.usernumber
LEFT JOIN location c
    ON ej.country = c.location_id
LEFT JOIN location s
    ON ej.state = s.location_id
LEFT JOIN location ci
    ON ej.city = ci.location_id
LEFT JOIN location_zip_codes zc
    ON ej.pin_code = zc.zip_id

ORDER BY ej.empnumber, ej.jobnumber, jr.NID, cd.NID;
"""

# Run query and fetch into DataFrame
df = pd.read_sql(query, engine)
chunksize = 50000  

# Save to CSV with safe quoting
output_file = "employerjob_jobresponse_candidates.csv"
with engine.connect() as conn:
    first = True
    i = 0
    for chunk in pd.read_sql(query, conn, chunksize=chunksize):
        chunk.to_csv(output_file, mode="a", index=False, encoding="utf-8", header=first)
        i += 1
        print(f"✅ Wrote chunk {i} ({len(chunk)} rows)")
        first = False

print(f"\n✅ Export finished: {output_file}")
