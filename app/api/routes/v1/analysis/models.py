from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String, Text, BigInteger, Integer, SmallInteger, Float, DECIMAL, DateTime, text, Index, UniqueConstraint
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMINT, VARCHAR

class JobResponse(SQLModel, table=True):
    __tablename__ = "jobresponse"

    NID: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))  # No comment, matches database
    CVSCORE: Optional[float] = Field(default=0, sa_column=Column(Float, nullable=True, server_default=text("'0'"), comment="cv score"))
    COMSCORE: Optional[float] = Field(default=None, sa_column=Column(Float, nullable=True))
    jobnumber: Optional[int] = Field(default=None, sa_column=Column(BigInteger, nullable=True))
    responsedate: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True))
    audiolink: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True, comment="recording link, plus text response incase of chatbot"))
    CANDIDATERANK: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True, comment="Candidate rank given by customer"))
    call_sid: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(50), nullable=True, comment="Call SID"))
    call_duration: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(20, charset="latin1", collation="latin1_swedish_ci"), nullable=True, comment="Call Duration"))
    userid: int = Field(sa_column=Column(Integer, nullable=False, comment="Candidate ID"))
    salary_preference: Optional[int] = Field(default=None, sa_column=Column(SmallInteger, nullable=True))
    available_in: Optional[int] = Field(default=None, sa_column=Column(SmallInteger, nullable=True))
    exp_salary: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    interview_time: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    sys_cv_score: Optional[float] = Field(default=None, sa_column=Column(DECIMAL(7, 4), nullable=True, comment="Machine score"))
    sys_comm_score: Optional[float] = Field(default=None, sa_column=Column(DECIMAL(7, 4), nullable=True, comment="Machine comm score"))
    STRSKILLS: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(100, charset="latin1", collation="latin1_swedish_ci"), nullable=True, comment="Candidate Skills"))
    CUST_RESP: Optional[int] = Field(default=0, sa_column=Column(Integer, nullable=True, server_default=text("'0'"), comment="Candidate status from customer (Shortlist Or Reject)"))
    STRCONURL: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(200), nullable=True, comment="Recruiter Candidate \n\nconversation url"))  # One newline, matches database
    upload_type: int = Field(sa_column=Column(Integer, nullable=False, server_default=text("'0'")))
    DTMFAnswer: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(25), nullable=True, comment="comma saparated DTMF answer 1-yes, 2-no"))
    NAUDIOSCORE: Optional[int] = Field(default=0, sa_column=Column(SmallInteger, nullable=True, server_default=text("'0'"), comment="calculated score of audio response multiplied by 100"))
    NSTATUS: int = Field(sa_column=Column(TINYINT, nullable=False, server_default=text("'1'"), comment="1-Active, 2-inactive"))
    NATTEMPTS: Optional[int] = Field(default=1, sa_column=Column(TINYINT, nullable=True, server_default=text("'1'"), comment="Response Attempt count"))
    DTRESCH: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True, comment="Re-schedule date from CLP for SMS only"))
    DTSLOTSTART: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True, comment="start time of the Drive Slot"))
    DTSLOTEND: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True, comment="end time of the Drive Slot"))
    CANSWERSCORE: Optional[int] = Field(default=0, sa_column=Column(Integer, nullable=True, server_default=text("'0'"), comment="answer score - xx.xx percentage multiply by 100 is stored"))
    CANSWERSCORES: Optional[str] = Field(default="", sa_column=Column(VARCHAR(25), nullable=True, server_default=text("''"), comment="comma saparated score for each answer"))
    CSKILLSMATCHED: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True, comment="Matched skills in answers"))
    NVIEWED: Optional[int] = Field(default=0, sa_column=Column(TINYINT, nullable=True, server_default=text("'0'")))

    __table_args__ = (
        Index("CANSWERSCORE_INDX", "CANSWERSCORE"),
    )

class JobInvite(SQLModel, table=True):
    __tablename__ = "jobinvite"

    nid: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True, comment="PK"))
    jobnumber: Optional[int] = Field(default=None, sa_column=Column(BigInteger, nullable=True))
    empnumber: Optional[int] = Field(default=None, sa_column=Column(BigInteger, nullable=True))
    name: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(50), nullable=True))
    mobileNo: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(15), nullable=True))
    countryCode: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    emailid: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(200), nullable=True))
    invite_dt: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True))
    email_set: int = Field(sa_column=Column(SmallInteger, nullable=False, server_default=text("'0'"), comment="Email sent status of the candidate"))
    NCALLSTATUS: int = Field(sa_column=Column(TINYINT, nullable=False, server_default=text("'0'"), comment="Calling status"))
    res_call_sid: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(40), nullable=True, comment="knowlarity response sid"))
    req_call_sid: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(40), nullable=True, comment="knowlarity request sid"))
    knowlarity_status: Optional[int] = Field(default=None, sa_column=Column(SmallInteger, nullable=True, comment="knowlarity status"))
    admin_status: int = Field(sa_column=Column(SmallInteger, nullable=False, comment="Admin status"))
    salary_preference: Optional[int] = Field(default=None, sa_column=Column(SmallInteger, nullable=True))
    NSMSSENT: int = Field(sa_column=Column(Integer, nullable=False, server_default=text("'0'"), comment="SMS sent status/count"))
    STRSMSREF: str = Field(sa_column=Column(VARCHAR(35), nullable=False, comment="SMS ref ID"))
    SMSSENTDT: datetime = Field(sa_column=Column(DateTime, nullable=False, comment="SMS sent date"))
    INSTCALDT: datetime = Field(sa_column=Column(DateTime, nullable=False, comment="Instant call date"))
    DTMF: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(8), nullable=True, comment="DTMF values ,comma separated"))
    RESDT: datetime = Field(sa_column=Column(DateTime, nullable=False, comment="DTNF updation date"))
    total_call: int = Field(sa_column=Column(Integer, nullable=False, comment="Total call duration"))
    CALMINUTES: int = Field(sa_column=Column(SmallInteger, nullable=False, server_default=text("'0'"), comment="calculated minutes"))
    call_start_time: datetime = Field(sa_column=Column(DateTime, nullable=False, comment="API Call start time"))
    call_end_time: datetime = Field(sa_column=Column(DateTime, nullable=False, comment="API Call end time"))
    CALLTYPE: int = Field(sa_column=Column(Integer, nullable=False, server_default=text("'0'")))
    SCHEDULEDTIME: datetime = Field(sa_column=Column(DateTime, nullable=False))
    PID: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(10), nullable=True))
    UPDATIONDATE: datetime = Field(sa_column=Column(DateTime, nullable=False))
    upload_type: int = Field(sa_column=Column(Integer, nullable=False, server_default=text("'0'"), comment="cv=1, excel=2"))
    DTUPDATEDMOBILE: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True, comment="Updated time of mobile"))
    COMMENT: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True, comment="Recruiter comment for candidate"))
    NLEFTFOLOWUP: Optional[int] = Field(default=0, sa_column=Column(TINYINT, nullable=True, server_default=text("'0'"), comment="Follow ups count remainng to go"))
    NTIMEZONE: int = Field(sa_column=Column(MEDIUMINT, nullable=False, server_default=text("'1'"), comment="timezone index as defined in ConstantTimeZones"))
    STRREFID: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(100), nullable=True, comment="candidate reference id parsed from Excel"))
    DTDRIVE: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True, comment="Drive date for which Candidate is invited"))
    STRLOCATION: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(100), nullable=True, comment="Candiate Location from Parsed data"))
    STRREFJDID: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(100), nullable=True, comment="Candidate external Demand ref id"))
    STRDOCUMENTS: Optional[str] = Field(default="", sa_column=Column(VARCHAR(100), nullable=True, server_default=text("''"), comment="data captured from documents col in excel upload"))
    NIVRTYPE: Optional[int] = Field(default=0, sa_column=Column(TINYINT, nullable=True, server_default=text("'0'"), comment="IVR type: 0 is for keypad based(default), 1 for Intent ASR"))
    NCALLIFYREFINVID: int = Field(sa_column=Column(Integer, nullable=False, server_default=text("'0'")))

    __table_args__ = (
        Index("INDX_NCALLIFYREFINVID", "NCALLIFYREFINVID"),
        Index("UPLOADTYPE_INDX", "upload_type"),
        UniqueConstraint("jobnumber", "emailid", name="unique_record"),  # Updated to match database
    )