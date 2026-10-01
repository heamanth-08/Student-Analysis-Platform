"""
Seed the database with realistic sample data for CampusIQ.
Called once at startup when the database has no students.
"""

import random
from sqlalchemy.orm import Session
from app.models import (
    Student, Department, Achievement, StridePoint, AdminProfile
)

DEPARTMENTS = [
    {"name": "Computer Science & Engineering", "code": "CSE", "head": "Dr. Ramesh Kumar"},
    {"name": "AI & Data Science", "code": "AIDS", "head": "Dr. Priya Nair"},
    {"name": "Mechanical Engineering", "code": "ME", "head": "Dr. Suresh Iyer"},
    {"name": "Electronics & Communication", "code": "ECE", "head": "Dr. Meera Pillai"},
    {"name": "Biotechnology", "code": "BT", "head": "Dr. Anita Sharma"},
]

ACHIEVEMENT_CATEGORIES = [
    "Hackathon", "Certifications", "Sports", "Cultural", "Research",
    "Internship", "Paper Publication", "Open Source"
]

STRIDE_CATEGORIES = [
    "Academic Excellence", "Extracurricular", "Research & Innovation",
    "Community Service", "Leadership", "Sports"
]

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Infosys", "TCS", "Wipro",
    "Cognizant", "Accenture", "IBM", "Oracle", "Adobe", "Flipkart"
]

FIRST_NAMES = [
    "Aarav", "Priya", "Rahul", "Ananya", "Rohit", "Sneha", "Kiran",
    "Deepika", "Arjun", "Pooja", "Vikram", "Meera", "Sanjay", "Lakshmi",
    "Amit", "Divya", "Rajesh", "Kavya", "Suresh", "Nithya", "Vijay",
    "Bhavya", "Harish", "Swathi", "Dinesh", "Sowmya", "Ganesh", "Rekha"
]

LAST_NAMES = [
    "Sharma", "Reddy", "Kumar", "Nair", "Patel", "Iyer", "Singh",
    "Rao", "Pillai", "Joshi", "Verma", "Gupta", "Menon", "Shetty",
    "Agarwal", "Bhat", "Chandra", "Das", "Fernandez", "Giri"
]


def seed_database(db: Session) -> None:
    if db.query(Student).first():
        return  # already seeded

    random.seed(42)

    # ── Departments ──────────────────────────────────────────────────────────
    dept_objects = {}
    for dept_data in DEPARTMENTS:
        dept = Department(
            name=dept_data["name"],
            code=dept_data["code"],
            head=dept_data["head"],
        )
        db.add(dept)
        dept_objects[dept_data["code"]] = dept_data["name"]
    db.flush()

    # ── Students ─────────────────────────────────────────────────────────────
    students = []
    dept_codes = list(dept_objects.keys())
    for i in range(1, 201):
        dept_code = random.choice(dept_codes)
        year = random.randint(1, 4)
        cgpa = round(random.uniform(5.5, 9.8), 2)
        attendance = round(random.uniform(55.0, 98.0), 1)
        placed = random.random() < 0.55
        company = random.choice(COMPANIES) if placed else None
        package = round(random.uniform(3.5, 22.0), 2) if placed else None
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        student_id = f"{dept_code}{2024 - year + 1}{i:04d}"

        s = Student(
            student_id=student_id,
            name=name,
            department=dept_objects[dept_code],
            year=year,
            semester=year * 2 - random.randint(0, 1),
            cgpa=cgpa,
            attendance_percentage=attendance,
            email=f"{first.lower()}.{last.lower()}{i}@campusiq.edu",
            phone=f"+91-9{random.randint(100000000, 999999999)}",
            batch=f"20{24 - year + 1}",
            section=random.choice(["A", "B", "C"]),
            gender=random.choice(["Male", "Female"]),
            hostel=random.random() < 0.4,
            placed=placed,
            company=company,
            package_lpa=package,
        )
        db.add(s)
        students.append(s)
    db.flush()

    # Update department aggregates
    for dept_data in DEPARTMENTS:
        dept_name = dept_data["name"]
        dept_students = [s for s in students if s.department == dept_name]
        if not dept_students:
            continue
        dept_obj = db.query(Department).filter_by(name=dept_name).first()
        if dept_obj:
            dept_obj.total_students = len(dept_students)
            dept_obj.average_cgpa = round(
                sum(s.cgpa for s in dept_students if s.cgpa) / len(dept_students), 2
            )
            dept_obj.average_attendance = round(
                sum(s.attendance_percentage for s in dept_students if s.attendance_percentage) / len(dept_students), 1
            )
            placed_count = sum(1 for s in dept_students if s.placed)
            dept_obj.placement_rate = round(placed_count / len(dept_students) * 100, 1)

    # ── Achievements ─────────────────────────────────────────────────────────
    cert_names = [
        "AWS Solutions Architect", "Google Cloud Professional", "Python for Data Science",
        "Machine Learning Specialization", "Cybersecurity Fundamentals",
        "React Developer Certification", "Azure AI Engineer", "NPTEL Elite"
    ]
    for student in students:
        n = random.randint(0, 4)
        for _ in range(n):
            category = random.choice(ACHIEVEMENT_CATEGORIES)
            a = Achievement(
                student_id=student.student_id,
                title=f"{random.choice(['Winner', 'Participant', 'Merit', '1st Place', 'Certificate'])} – {category}",
                category=category,
                certification_name=random.choice(cert_names) if category == "Certifications" else None,
                issuer=random.choice(["Coursera", "NPTEL", "AWS", "Google", "Microsoft", "Institution"]),
                date_achieved=f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                score=round(random.uniform(70, 100), 1) if category == "Certifications" else None,
            )
            db.add(a)

    # ── Stride Points ────────────────────────────────────────────────────────
    activities = {
        "Academic Excellence": ["Dean's List", "Top CGPA", "Subject Topper"],
        "Extracurricular": ["Cultural Fest", "Club Lead", "Event Organization"],
        "Research & Innovation": ["Paper Published", "Patent Filed", "Research Intern"],
        "Community Service": ["NSS Camp", "Blood Donation", "Outreach Program"],
        "Leadership": ["Student Council", "Department Head", "Mentor Program"],
        "Sports": ["Inter-College Gold", "University Meet", "National Selection"],
    }
    for student in students:
        n = random.randint(0, 6)
        for _ in range(n):
            category = random.choice(STRIDE_CATEGORIES)
            activity = random.choice(activities[category])
            pts = random.randint(5, 50)
            sp = StridePoint(
                student_id=student.student_id,
                category=category,
                activity=activity,
                points=pts,
                academic_year="2024-25",
                verified=True,
            )
            db.add(sp)

    # ── Admin Profile ────────────────────────────────────────────────────────
    admin = AdminProfile(
        full_name="Dr. Evelyn Vance",
        email="evelyn.vance@campusiq.edu",
        institutional_role="Dean of Academic Affairs",
        department="Office of Academic Affairs",
        phone="+91-9876543210",
        notifications_enabled=True,
        theme="dark",
        language="English",
    )
    db.add(admin)

    db.commit()
    print("[OK] Database seeded with 200 students and sample data.")
