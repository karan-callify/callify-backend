import pandas as pd
from sqlalchemy import create_engine

# MySQL connection
engine = create_engine("mysql+pymysql://root:2004@localhost:3306/callify")

query = """
-- Case 1: employerjob + jobinvite (+ jobresponse if linked)
SELECT
    ej.jobnumber,
    ej.empnumber,
    ej.jobmode,
    ej.jobdesc,

    ji.nid AS invite_id,
    ji.name AS candidate_name,
    ji.mobileNo,
    ji.countryCode,

    jr.userid AS candidate_user_id,
    jr.CANDIDATERANK,
    jr.CVSCORE

FROM employerjob ej
LEFT JOIN jobinvite ji
    ON ej.jobnumber = ji.jobnumber
LEFT JOIN jobresponse jr
    ON ej.jobnumber = jr.jobnumber
   AND ji.nid = jr.NID

UNION

-- Case 2: employerjob + jobresponse even if NO jobinvite exists
SELECT
    ej.jobnumber,
    ej.empnumber,
    ej.jobmode,
    ej.jobdesc,

    NULL AS invite_id,
    NULL AS candidate_name,
    NULL AS mobileNo,
    NULL AS countryCode,

    jr.userid AS candidate_user_id,
    jr.CANDIDATERANK,
    jr.CVSCORE

FROM employerjob ej
LEFT JOIN jobresponse jr
    ON ej.jobnumber = jr.jobnumber
WHERE NOT EXISTS (
    SELECT 1
    FROM jobinvite ji
    WHERE ji.jobnumber = ej.jobnumber
      AND ji.nid = jr.NID
);
"""

df = pd.read_sql(query, engine)
df.to_csv("combined_job_data.csv", index=False)
print("✅ Exported with invites-only, responses-only, and matched rows")