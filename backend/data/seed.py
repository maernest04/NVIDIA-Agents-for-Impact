"""
Creates and seeds campus_resources.db with SJSU campus resource data.
Run once: python backend/data/seed.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "campus_resources.db"


def seed():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS campus_resources;
        CREATE TABLE campus_resources (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_name TEXT NOT NULL,
            phone_number  TEXT,
            email         TEXT,
            description   TEXT
        );
    """)

    resources = [
        # --- SJSU CAMPUS RESOURCES (Cleaned & Completed) ---
        ("College of Graduate Studies (CGS)", "408-924-2447", "graduate-studies@sjsu.edu", "Oversees and implements the University's graduate policies and procedures; provides guidance for thesis and dissertation submission."),
        ("Graduate Admissions & Program Evaluations (GAPE)", "408-283-7500", "admissions@sjsu.edu", "Processes advancement to candidacy and graduation."),
        ("Bursar's Office", "408-924-1601", "bursar@sjsu.edu", "Collects student tuition and fee payment, and disburses funds."),
        ("Financial Aid and Scholarship Office (FASO)", "408-283-7500", "fao@sjsu.edu", "Assists students in securing federal, state, and university financial aid."),
        ("Office of the Registrar", "408-283-7500", "registrar@sjsu.edu", "Oversees course registration, grade posting, and academic records."),
        ("Alumni Association", "408-924-6515", "alumni@sjsu.edu", "Connects graduates to their alma mater and each other."),
        ("Associated Students", "408-924-6242", "as-info@sjsu.edu", "Supports and represents SJSU's student body through leadership advocacy, programs, events, and funding."),
        ("Student Involvement", "408-924-5950", "getinvolved@sjsu.edu", "Oversees all fraternities, sororities, clubs, and other student organizations; hosts campus events."),
        ("Office of Research and Innovation", "408-924-2272", "OfficeofResearch@sjsu.edu", "Provides services related to research, scholarship, and creative activities, including proposal development and ethical standards."),
        ("Dr. Martin Luther King, Jr. Library", "408-808-2000", "library-reference-group@sjsu.edu", "Collaborative library offering research assistance, study spaces, and extensive digital and physical collections."),
        ("Writing Center", "408-924-2308", "writingcenter@sjsu.edu", "Offers free resources to help students become better writers."),
        ("AS Print & Technology Center", "408-924-6976", "printshop@sjsu.edu", "Provides printing, copying, and technology services including repairs and rentals."),
        ("IT Service Desk", "408-924-1530", "itservicedesk@sjsu.edu", "Help students, faculty, and staff with all their technical needs."),
        ("Career Center", "408-924-6031", "careerhelp@sjsu.edu", "Supports graduate students with career counseling, workshops, and planning tools."),
        ("International Student and Scholar Services (ISSS)", "408-924-5920", "international-office@sjsu.edu", "Assists international students with OPT, CPT, STEM OPT, and immigration advising."),
        ("International House (I-House)", "408-924-6570", "ihouse@sjsu.edu", "Provides a diverse and welcoming intercultural living environment for U.S. and international students."),
        ("Accessible Education Center", "408-924-6000", "aec-info@sjsu.edu", "Provides comprehensive services that support the educational development of students with disabilities."),
        ("The Black Leadership and Opportunity Center (BLOC)", "408-924-5105", "thebloc@sjsu.edu", "Hub for Black student life, providing cultural programming and professional development."),
        ("Chicanx/Latinx Student Success Center", "408-924-5102", "chicanxlatinxssc@sjsu.edu", "Provides community space and services to support Chicanx and Latinx students."),
        ("Gender Equity Center", "408-924-6500", "genec@sjsu.edu", "Advocates for social justice and safety regarding gender and gender identity issues."),
        ("Veterans Resource Center", "408-924-8129", "veterans@sjsu.edu", "One-stop resource for veterans, reservists, active duty personnel, and dependents."),
        ("MOSAIC Cross Cultural Center", "408-924-6255", "mosaic@sjsu.edu", "Provides support and advocacy for historically underrepresented groups."),
        ("PRIDE Center", "408-924-6976", "sjsupride@gmail.com", "Supports LGBTQ+ students and advocates for respect and safety."),
        ("UndocuSpartan Student Resource Center", "408-924-2762", "undocuspartan@sjsu.edu", "Provides holistic support and resources to undocumented students."),
        ("Counseling and Psychological Services (CAPS)", "408-924-5678", "studentwellnesscenter@sjsu.edu", "Provides counseling services on psychological and academic issues."),
        ("Ombudsperson", "408-924-5995", "ombuds@sjsu.edu", "Advocate for procedural fairness and neutral, confidential discussion of concerns."),
        ("Spartan Recreation and Aquatic Center (SRAC)", "408-924-6368", "srac-info@sjsu.edu", "Fitness classes, club sports, and state-of-the-art aquatic and workout facilities."),
        ("Student Wellness Center", "408-924-6122", "wellness.center@sjsu.edu", "On-campus health care including primary care, pharmacy, and wellness workshops."),
        ("University Housing Services (UHS)", "408-795-5600", "uhs-frontdesk@sjsu.edu", "Assists students seeking on-campus housing and residential life support."),
        ("Spartan Eats Campus Dining", "408-924-1740", "spartaneats@compass-usa.com", "Manages SJSU meal plans and provides diverse on-campus dining options."),
        ("Parking Services", "408-924-6566", "parking@sjsu.edu", "Provides parking permits and manages campus parking garage facilities."),
        ("Transportation Solutions", "408-924-7433", "transportation@sjsu.edu", "Assists with SmartPass Clipper cards, bike support, and commuting alternatives."),
        ("University Police Department (UPD)", "408-924-2222", "police@sjsu.edu", "Emergency services, campus safety escorts, and 24/7 law enforcement."),
        ("SJSU Cares", "408-924-1234", "sjsucares@sjsu.edu", "Support for basic needs like food, housing, and emergency financial assistance."),

        # --- NATIONAL CRISIS HOTLINES ---
        ("988 Suicide & Crisis Lifeline", "988", "N/A", "24/7, free, and confidential support for people in distress and prevention resources."),
        ("Crisis Text Line", "741741", "Text HOME to 741741", "Free 24/7 text-based mental health support and crisis intervention."),
        ("The Trevor Project (LGBTQ+)", "1-866-488-7386", "Text START to 678-678", "24/7 crisis intervention and suicide prevention for LGBTQ young people."),
        ("National Domestic Violence Hotline", "1-800-799-7233", "Text START to 88788", "24/7 support for anyone experiencing domestic violence or seeking help."),
        ("RAINN Sexual Assault Hotline", "1-800-656-4673", "N/A", "Confidential support for survivors of sexual assault and their loved ones."),
        ("SAMHSA National Helpline", "1-800-662-4357", "N/A", "24/7 treatment referral and info for substance use and mental health disorders.")
    ]

    cur.executemany(
        "INSERT INTO campus_resources (resource_name, phone_number, email, description) VALUES (?, ?, ?, ?)",
        resources,
    )
    con.commit()
    con.close()
    print(f"Successfully seeded {len(resources)} records into {DB_PATH}")