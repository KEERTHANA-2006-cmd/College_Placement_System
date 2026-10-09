
import sqlite3
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# CAMPUSCONNECT - COLLEGE PLACEMENT MANAGEMENT SYSTEM
# =========================================================

st.set_page_config(
    page_title="CampusConnect | Placement Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_NAME = "placement.db"

DEPARTMENTS = [
    "CSE", "IT", "ECE", "EEE", "MECH", "CIVIL", "Other"
]

STATUSES = ["Applied", "Interview", "Selected", "Rejected"]


# ----------------------- DATABASE -------------------------

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                roll_no TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                year INTEGER NOT NULL,
                cgpa REAL NOT NULL,
                email TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                min_cgpa REAL NOT NULL,
                eligible_department TEXT NOT NULL,
                package_lpa REAL NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS placements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT NOT NULL,
                company_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                application_date TEXT NOT NULL,
                UNIQUE(roll_no, company_id),
                FOREIGN KEY(roll_no) REFERENCES students(roll_no)
                    ON DELETE CASCADE,
                FOREIGN KEY(company_id) REFERENCES companies(id)
                    ON DELETE CASCADE
            )
        """)


def read_table(query, params=()):
    with connect_db() as conn:
        return pd.read_sql_query(query, conn, params=params)


def execute_query(query, params=()):
    with connect_db() as conn:
        conn.execute(query, params)


initialize_db()


# ----------------------- DESIGN ---------------------------

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(145deg, #f5f3ff 0%, #f8fafc 50%, #eef2ff 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #17153b 0%, #30246b 100%);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    .hero {
        padding: 30px 32px;
        border-radius: 22px;
        background: linear-gradient(120deg, #30246b, #6546d7, #8975f5);
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 12px 30px rgba(74, 55, 160, 0.18);
    }

    .hero h1 {
        color: white;
        font-size: 35px;
        margin: 0;
    }

    .hero p {
        color: #eeeaff;
        font-size: 16px;
        margin-top: 9px;
    }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 17px;
        border: 1px solid #e9e5ff;
        box-shadow: 0 5px 18px rgba(42, 32, 100, 0.06);
        min-height: 120px;
    }

    .metric-label {
        color: #77748d;
        font-size: 14px;
        font-weight: 600;
    }

    .metric-value {
        color: #30246b;
        font-size: 30px;
        font-weight: 800;
        margin-top: 8px;
    }

    .section-heading {
        color: #30246b;
        font-size: 23px;
        font-weight: 750;
        margin: 10px 0 15px 0;
    }

    div.stButton > button {
        border-radius: 10px;
        border: none;
        font-weight: 650;
        min-height: 42px;
        transition: 0.2s;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #5540bd, #7864ed);
        color: white;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 12px rgba(70, 55, 150, 0.15);
    }

    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.75);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e8e4ff;
    }

    h2, h3 {
        color: #30246b;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 22px;
        }
        .hero h1 {
            font-size: 27px;
        }
        .metric-value {
            font-size: 25px;
        }
    }
</style>
""", unsafe_allow_html=True)


# ----------------------- HELPERS -------------------------

def hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_students():
    return read_table("SELECT * FROM students ORDER BY name")


def get_companies():
    return read_table("SELECT * FROM companies ORDER BY name")


def get_placements():
    return read_table("""
        SELECT p.id, p.roll_no, s.name AS student_name,
               s.department, c.name AS company_name, c.role,
               c.package_lpa, p.status, p.application_date
        FROM placements p
        JOIN students s ON p.roll_no = s.roll_no
        JOIN companies c ON p.company_id = c.id
        ORDER BY p.id DESC
    """)


def download_csv(df, filename, label="⬇️ Download CSV"):
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


# ----------------------- SIDEBAR -------------------------

with st.sidebar:
    st.markdown("# 🎓 CampusConnect")
    st.caption("COLLEGE PLACEMENT PORTAL")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Dashboard",
            "👩‍🎓 Student Management",
            "🏢 Company Management",
            "🎯 Eligibility Checker",
            "📋 Placement Tracking",
            "📊 Reports & Analytics",
        ],
    )

    st.divider()
    st.markdown("### 💡 Quick Guide")
    st.caption("1. Add students")
    st.caption("2. Register companies")
    st.caption("3. Check eligibility")
    st.caption("4. Track applications")
    st.caption("5. View reports")

    st.divider()
    st.caption("CampusConnect • Student Placement Portal")


# ----------------------- DASHBOARD -----------------------

if page == "🏠 Dashboard":
    hero(
        "Welcome to CampusConnect 👋",
        "Your smart and simple college placement management portal.",
    )

    students = get_students()
    companies = get_companies()
    placements = get_placements()

    total_students = len(students)
    total_companies = len(companies)
    total_applications = len(placements)
    total_selected = (
        int((placements["status"] == "Selected").sum())
        if not placements.empty else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("👩‍🎓 Total Students", total_students)
    with c2:
        metric_card("🏢 Companies", total_companies)
    with c3:
        metric_card("📨 Applications", total_applications)
    with c4:
        metric_card("🏆 Students Selected", total_selected)

    st.write("")
    st.markdown(
        '<div class="section-heading">📈 Placement Overview</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        st.markdown("#### Applications by Status")
        if not placements.empty:
            status_counts = (
                placements["status"].value_counts()
                .rename_axis("Status")
                .reset_index(name="Applications")
            )
            fig = px.pie(
                status_counts,
                names="Status",
                values="Applications",
                hole=0.55,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_layout(
                margin=dict(t=20, b=20, l=10, r=10),
                legend_title_text="Status",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No applications yet. Add students and companies to begin.")

    with right:
        st.markdown("#### Students by Department")
        if not students.empty:
            dept_counts = (
                students["department"].value_counts()
                .rename_axis("Department")
                .reset_index(name="Students")
            )
            fig = px.bar(
                dept_counts,
                x="Department",
                y="Students",
                color="Department",
                text="Students",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_layout(
                showlegend=False,
                margin=dict(t=20, b=20, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add student records to see the department chart.")

    st.markdown("#### 🕒 Recent Placement Applications")
    if not placements.empty:
        st.dataframe(
            placements.head(5),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Your recent applications will appear here.")

    st.caption(
        "Note: Dashboard figures are calculated from the records "
        "currently stored in your database."
    )


# -------------------- STUDENT MANAGEMENT -----------------

elif page == "👩‍🎓 Student Management":
    hero(
        "Student Management 👩‍🎓",
        "Add, search, view, and manage student information.",
    )

    with st.expander("➕ Register a New Student", expanded=True):
        with st.form("student_form", clear_on_submit=True):
            a, b = st.columns(2)

            with a:
                roll_no = st.text_input("Roll Number *")
                name = st.text_input("Full Name *")
                department = st.selectbox("Department", DEPARTMENTS)

            with b:
                year = st.selectbox("Academic Year", [1, 2, 3, 4])
                cgpa = st.number_input(
                    "CGPA (0–10)", min_value=0.0,
                    max_value=10.0, value=7.0, step=0.1,
                )
                email = st.text_input("Email Address *")

            submitted = st.form_submit_button(
                "➕ Add Student",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if not roll_no.strip() or not name.strip() or not email.strip():
                    st.error("Please fill in all required fields.")
                elif "@" not in email or "." not in email:
                    st.error("Please enter a valid email address.")
                else:
                    try:
                        execute_query(
                            """INSERT INTO students
                            (roll_no, name, department, year, cgpa, email)
                            VALUES (?, ?, ?, ?, ?, ?)""",
                            (
                                roll_no.strip().upper(),
                                name.strip(),
                                department,
                                year,
                                cgpa,
                                email.strip(),
                            ),
                        )
                        st.success("Student registered successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error(
                            "This roll number already exists. "
                            "Please use a different roll number."
                        )

    st.markdown("### 🔎 Search Students")
    search = st.text_input(
        "Search by name, roll number, or department",
        placeholder="Example: CSE or 101 or Keerthana",
    )

    students = get_students()
    if search.strip():
        mask = students.astype(str).apply(
            lambda col: col.str.contains(
                search.strip(), case=False, na=False
            )
        ).any(axis=1)
        students = students[mask]

    st.write(f"**Records found: {len(students)}**")
    st.dataframe(students, use_container_width=True, hide_index=True)

    if not students.empty:
        download_csv(students, "student_records.csv")

    st.markdown("### 🗑️ Remove a Student")
    all_students = get_students()

    if not all_students.empty:
        with st.form("delete_student_form"):
            selected_roll = st.selectbox(
                "Choose student",
                all_students["roll_no"].tolist(),
                format_func=lambda r: (
                    f"{r} — "
                    f"{all_students.loc[all_students['roll_no'] == r, 'name'].iloc[0]}"
                ),
            )
            confirm_delete = st.checkbox(
                "I understand that this also removes the student's applications."
            )
            delete_student = st.form_submit_button(
                "Delete Student",
                type="primary",
            )

            if delete_student:
                if confirm_delete:
                    execute_query(
                        "DELETE FROM students WHERE roll_no = ?",
                        (selected_roll,),
                    )
                    st.success("Student and related applications deleted.")
                    st.rerun()
                else:
                    st.warning("Please confirm before deleting.")
    else:
        st.info("No students registered yet.")


# -------------------- COMPANY MANAGEMENT -----------------

elif page == "🏢 Company Management":
    hero(
        "Company Management 🏢",
        "Register hiring companies and define their job requirements.",
    )

    with st.expander("➕ Register a Company", expanded=True):
        with st.form("company_form", clear_on_submit=True):
            a, b = st.columns(2)

            with a:
                company_name = st.text_input("Company Name *")
                role = st.text_input("Job Role *")
                min_cgpa = st.number_input(
                    "Minimum Required CGPA",
                    min_value=0.0,
                    max_value=10.0,
                    value=6.0,
                    step=0.1,
                )

            with b:
                eligible_department = st.selectbox(
                    "Eligible Department",
                    ["All Departments"] + DEPARTMENTS,
                )
                package = st.number_input(
                    "Package (LPA)",
                    min_value=0.0,
                    max_value=200.0,
                    value=4.0,
                    step=0.5,
                )

            company_submit = st.form_submit_button(
                "🏢 Register Company",
                type="primary",
                use_container_width=True,
            )

            if company_submit:
                if not company_name.strip() or not role.strip():
                    st.error("Company name and job role are required.")
                else:
                    execute_query(
                        """INSERT INTO companies
                        (name, role, min_cgpa, eligible_department, package_lpa)
                        VALUES (?, ?, ?, ?, ?)""",
                        (
                            company_name.strip(),
                            role.strip(),
                            min_cgpa,
                            eligible_department,
                            package,
                        ),
                    )
                    st.success("Company registered successfully!")
                    st.rerun()

    companies = get_companies()
    st.markdown("### 🌟 Registered Companies")

    if not companies.empty:
        st.dataframe(
            companies,
            use_container_width=True,
            hide_index=True,
        )
        download_csv(companies, "company_records.csv")

        st.markdown("### 🗑️ Remove a Company")
        with st.form("delete_company_form"):
            company_id = st.selectbox(
                "Choose company",
                companies["id"].tolist(),
                format_func=lambda i: (
                    f"{companies.loc[companies['id'] == i, 'name'].iloc[0]} — "
                    f"{companies.loc[companies['id'] == i, 'role'].iloc[0]}"
                ),
            )
            confirm_company_delete = st.checkbox(
                "I understand that this also removes applications for this company."
            )
            delete_company = st.form_submit_button("Delete Company")

            if delete_company:
                if confirm_company_delete:
                    execute_query(
                        "DELETE FROM companies WHERE id = ?",
                        (int(company_id),),
                    )
                    st.success("Company and related applications deleted.")
                    st.rerun()
                else:
                    st.warning("Please confirm before deleting.")
    else:
        st.info("No companies registered yet. Add your first company above.")


# -------------------- ELIGIBILITY CHECKER ----------------

elif page == "🎯 Eligibility Checker":
    hero(
        "Smart Eligibility Checker 🎯",
        "Find students who meet a company's CGPA and department requirements.",
    )

    students = get_students()
    companies = get_companies()

    if students.empty or companies.empty:
        st.warning(
            "Please register at least one student and one company "
            "before checking eligibility."
        )
    else:
        company_id = st.selectbox(
            "Select Hiring Company",
            companies["id"].tolist(),
            format_func=lambda i: (
                f"{companies.loc[companies['id'] == i, 'name'].iloc[0]} — "
                f"{companies.loc[companies['id'] == i, 'role'].iloc[0]}"
            ),
        )

        company = companies.loc[companies["id"] == company_id].iloc[0]

        a, b, c = st.columns(3)
        with a:
            metric_card("🏢 Company", company["name"])
        with b:
            metric_card("📚 Minimum CGPA", f'{company["min_cgpa"]:.1f}')
        with c:
            metric_card("💼 Package", f'{company["package_lpa"]:.2f} LPA')

        dept_rule = company["eligible_department"]
        eligible = students[
            (students["cgpa"] >= company["min_cgpa"])
            & (
                (dept_rule == "All Departments")
                | (students["department"] == dept_rule)
            )
        ].copy()

        not_eligible = students.drop(eligible.index)

        st.write("")
        x, y = st.columns(2)
        with x:
            metric_card("✅ Eligible Students", len(eligible))
        with y:
            metric_card("📌 Not Matching Criteria", len(not_eligible))

        st.markdown("### ✅ Eligible Students")
        if not eligible.empty:
            st.dataframe(
                eligible,
                use_container_width=True,
                hide_index=True,
            )
            download_csv(eligible, "eligible_students.csv")
        else:
            st.info("No students currently meet this company's requirements.")

        with st.expander("View students who do not meet the criteria"):
            if not not_eligible.empty:
                st.dataframe(
                    not_eligible,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.success("All registered students meet the selected criteria.")

        st.caption(
            "Eligibility is based only on the minimum CGPA and department "
            "stored for the selected company."
        )


# -------------------- PLACEMENT TRACKING -----------------

elif page == "📋 Placement Tracking":
    hero(
        "Placement Tracking 📋",
        "Record applications and update student placement progress.",
    )

    students = get_students()
    companies = get_companies()

    if students.empty or companies.empty:
        st.warning(
            "Add at least one student and one company before tracking applications."
        )
    else:
        with st.expander("➕ Create or Update an Application", expanded=True):
            with st.form("placement_form"):
                a, b = st.columns(2)

                with a:
                    roll_no = st.selectbox(
                        "Student",
                        students["roll_no"].tolist(),
                        format_func=lambda r: (
                            f"{r} — "
                            f"{students.loc[students['roll_no'] == r, 'name'].iloc[0]}"
                        ),
                    )
                    company_id = st.selectbox(
                        "Company",
                        companies["id"].tolist(),
                        format_func=lambda i: (
                            f"{companies.loc[companies['id'] == i, 'name'].iloc[0]} — "
                            f"{companies.loc[companies['id'] == i, 'role'].iloc[0]}"
                        ),
                    )

                with b:
                    status = st.selectbox("Application Status", STATUSES)
                    application_date = st.date_input(
                        "Application Date",
                        value=date.today(),
                    )

                save_application = st.form_submit_button(
                    "💾 Save Application",
                    type="primary",
                    use_container_width=True,
                )

                if save_application:
                    try:
                        execute_query(
                            """INSERT INTO placements
                            (roll_no, company_id, status, application_date)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(roll_no, company_id)
                            DO UPDATE SET
                                status = excluded.status,
                                application_date = excluded.application_date
                            """,
                            (
                                roll_no,
                                int(company_id),
                                status,
                                application_date.isoformat(),
                            ),
                        )
                        st.success("Placement application saved successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Could not save this application. Check the records.")

    placements = get_placements()

    st.markdown("### 📋 All Placement Applications")
    if not placements.empty:
        st.dataframe(
            placements,
            use_container_width=True,
            hide_index=True,
        )
        download_csv(placements, "placement_applications.csv")

        st.markdown("### 🗑️ Delete an Application")
        with st.form("delete_application_form"):
            placement_id = st.selectbox(
                "Choose application",
                placements["id"].tolist(),
                format_func=lambda i: (
                    f"#{i} — "
                    f"{placements.loc[placements['id'] == i, 'student_name'].iloc[0]} / "
                    f"{placements.loc[placements['id'] == i, 'company_name'].iloc[0]}"
                ),
            )
            delete_application = st.form_submit_button("Delete Application")

            if delete_application:
                execute_query(
                    "DELETE FROM placements WHERE id = ?",
                    (int(placement_id),),
                )
                st.success("Application deleted.")
                st.rerun()
    else:
        st.info("No placement applications recorded yet.")


# -------------------- REPORTS & ANALYTICS ----------------

elif page == "📊 Reports & Analytics":
    hero(
        "Reports & Analytics 📊",
        "Understand student performance, applications, and placement outcomes.",
    )

    students = get_students()
    companies = get_companies()
    placements = get_placements()

    st.markdown("### 📌 Summary")
    total = len(students)
    selected = (
        int((placements["status"] == "Selected").sum())
        if not placements.empty else 0
    )
    selection_rate = (
        selected / len(placements) * 100 if len(placements) else 0
    )
    average_cgpa = (
        float(students["cgpa"].mean()) if not students.empty else 0
    )

    a, b, c, d = st.columns(4)
    with a:
        metric_card("👩‍🎓 Students", total)
    with b:
        metric_card("🏢 Companies", len(companies))
    with c:
        metric_card("📚 Average CGPA", f"{average_cgpa:.2f}")
    with d:
        metric_card("🏆 Selection Rate", f"{selection_rate:.1f}%")

    st.markdown("### 📈 Department Report")
    if not students.empty:
        department_report = (
            students.groupby("department")
            .agg(
                Total_Students=("roll_no", "count"),
                Average_CGPA=("cgpa", "mean"),
                Highest_CGPA=("cgpa", "max"),
            )
            .reset_index()
            .round(2)
        )

        st.dataframe(
            department_report,
            use_container_width=True,
            hide_index=True,
        )
        download_csv(department_report, "department_report.csv")

        fig = px.bar(
            department_report,
            x="department",
            y="Average_CGPA",
            color="department",
            text="Average_CGPA",
            title="Average CGPA by Department",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🌟 Top Performing Students")
        top_students = students.sort_values(
            "cgpa", ascending=False
        ).head(10)
        st.dataframe(
            top_students,
            use_container_width=True,
            hide_index=True,
        )
        download_csv(top_students, "top_students.csv")
    else:
        st.info("Register students to generate department reports.")

    st.markdown("### 🏢 Company Selection Report")
    if not placements.empty:
        selection_report = (
            placements.groupby(["company_name", "status"])
            .size()
            .reset_index(name="Number of Applications")
        )

        st.dataframe(
            selection_report,
            use_container_width=True,
            hide_index=True,
        )
        download_csv(selection_report, "company_selection_report.csv")

        fig = px.bar(
            selection_report,
            x="company_name",
            y="Number of Applications",
            color="status",
            barmode="group",
            title="Applications by Company and Status",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Record applications to generate placement reports.")

    st.markdown("### 📥 Export All Data")
    left, right = st.columns(2)
    with left:
        if not students.empty:
            download_csv(
                students, "all_students.csv", "⬇️ Download All Students"
            )
    with right:
        if not placements.empty:
            download_csv(
                placements, "all_placements.csv", "⬇️ Download All Placements"
            )


# ----------------------- FOOTER --------------------------

st.divider()
st.markdown(
    """
    <div style="text-align:center; padding:10px; color:#77748d;">
        <b>CampusConnect</b> 🎓 · College Placement Management System
        <br>
        Built with Python, Streamlit, SQLite, Pandas and Plotly
    </div>
    """,
    unsafe_allow_html=True,
)