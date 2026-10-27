from dataclasses import dataclass
from collections import defaultdict, deque
from html import escape
import csv
import webbrowser
from pathlib import Path

# ============================================================
# EXAM ALLOCATOR | Clean terminal UI + polished HTML dashboard
# Uses only Python's standard library.
# ============================================================

@dataclass
class Student:
    roll_no: str
    name: str
    course: str


@dataclass
class Room:
    room_no: str
    capacity: int


@dataclass
class Faculty:
    faculty_id: str
    name: str
    department: str


@dataclass
class SeatAssignment:
    student: Student
    room_no: str
    row: int
    column: int
    seat_no: int


students = [
    Student("101", "Aarav Sharma", "CSE"),
    Student("102", "Riya Verma", "AIML"),
    Student("103", "Arjun Singh", "CSE"),
    Student("104", "Ananya Gupta", "DS"),
    Student("105", "Kabir Mehta", "AIML"),
    Student("106", "Ishita Jain", "CSE"),
    Student("107", "Vivaan Rao", "DS"),
    Student("108", "Diya Kapoor", "AIML"),
    Student("109", "Reyansh Das", "CSE"),
    Student("110", "Myra Malhotra", "DS"),
    Student("111", "Aditya Kumar", "AIML"),
    Student("112", "Sara Khan", "CSE"),
]

rooms = [Room("A101", 6), Room("A102", 6)]

faculty = [
    Faculty("F01", "Dr. Sharma", "CSE"),
    Faculty("F02", "Prof. Verma", "AIML"),
    Faculty("F03", "Dr. Gupta", "DS"),
    Faculty("F04", "Prof. Singh", "CSE"),
]

assignments = []
faculty_duties = []


def line(char="─", width=76):
    print(char * width)


def heading(title, subtitle=""):
    print()
    line("═")
    print(f"  {title}")
    if subtitle:
        print(f"  {subtitle}")
    line("═")


def pause():
    input("\nPress Enter to return to the menu...")


def validate_data():
    roll_numbers = [s.roll_no for s in students]
    if len(roll_numbers) != len(set(roll_numbers)):
        raise ValueError("Duplicate roll numbers found.")
    capacity = sum(room.capacity for room in rooms)
    if len(students) > capacity:
        raise ValueError(
            f"Not enough seats: {len(students)} students but only {capacity} seats."
        )


def display_students():
    heading("STUDENT DIRECTORY", f"{len(students)} students registered")
    print(f"{'ROLL NO.':<12}{'STUDENT NAME':<28}{'COURSE':<12}")
    line()
    for student in students:
        print(f"{student.roll_no:<12}{student.name:<28}{student.course:<12}")
    line()
    print(f"  Total students: {len(students)}")


def display_rooms():
    heading("CLASSROOM OVERVIEW")
    print(f"{'ROOM':<18}{'CAPACITY':<14}{'STATUS':<18}")
    line()
    for room in rooms:
        print(f"{room.room_no:<18}{room.capacity:<14}{'Available':<18}")
    line()
    print(f"  Total capacity: {sum(room.capacity for room in rooms)} seats")


def arrange_students(show=True):
    global assignments
    validate_data()

    course_groups = defaultdict(deque)
    for student in students:
        course_groups[student.course].append(student)

    # Round-robin course ordering helps reduce same-course clustering.
    ordered_students = []
    while course_groups:
        for course_name in list(course_groups):
            ordered_students.append(course_groups[course_name].popleft())
            if not course_groups[course_name]:
                del course_groups[course_name]

    assignments = []
    index = 0

    for room in rooms:
        for seat in range(1, room.capacity + 1):
            if index >= len(ordered_students):
                break
            student = ordered_students[index]
            index += 1
            assignments.append(
                SeatAssignment(
                    student=student,
                    room_no=room.room_no,
                    row=(seat - 1) // 4 + 1,
                    column=(seat - 1) % 4 + 1,
                    seat_no=seat,
                )
            )

    if show:
        heading("SEATING PLAN GENERATED", f"{len(assignments)} seats assigned")
        for room in rooms:
            room_seats = [a for a in assignments if a.room_no == room.room_no]
            print(f"\n  ROOM {room.room_no}  •  {len(room_seats)}/{room.capacity} seats used")
            line("─", 76)
            print(f"  {'SEAT':<7}{'ROW':<6}{'COL':<6}{'ROLL NO.':<12}{'NAME':<25}{'COURSE':<8}")
            line("─", 76)
            for a in room_seats:
                print(
                    f"  {a.seat_no:<7}{a.row:<6}{a.column:<6}"
                    f"{a.student.roll_no:<12}{a.student.name:<25}{a.student.course:<8}"
                )
        line()
        print("  Note: Course interleaving reduces clustering but cannot guarantee")
        print("  that students from the same course are never seated adjacent.")


def allocate_faculty(show=True):
    global faculty_duties
    if not faculty:
        print("No faculty records available.")
        return

    faculty_duties = []
    for index, room in enumerate(rooms):
        member = faculty[index % len(faculty)]
        faculty_duties.append({
            "room_no": room.room_no,
            "faculty_id": member.faculty_id,
            "faculty_name": member.name,
            "department": member.department,
        })

    if show:
        heading("FACULTY DUTY ROSTER", f"{len(faculty_duties)} room duties assigned")
        print(f"{'ROOM':<14}{'FACULTY ID':<16}{'FACULTY MEMBER':<24}{'DEPARTMENT':<12}")
        line()
        for duty in faculty_duties:
            print(
                f"{duty['room_no']:<14}{duty['faculty_id']:<16}"
                f"{duty['faculty_name']:<24}{duty['department']:<12}"
            )
        line()


def export_csv():
    if not assignments:
        arrange_students(show=False)

    seating_path = Path("seating_plan.csv")
    with seating_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Roll Number", "Student Name", "Course", "Room",
            "Seat Number", "Row", "Column"
        ])
        for a in assignments:
            writer.writerow([
                a.student.roll_no, a.student.name, a.student.course,
                a.room_no, a.seat_no, a.row, a.column
            ])

    if not faculty_duties:
        allocate_faculty(show=False)

    faculty_path = Path("faculty_duties.csv")
    with faculty_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["room_no", "faculty_id", "faculty_name", "department"]
        )
        writer.writeheader()
        writer.writerows(faculty_duties)

    print("\n  ✓ CSV files saved:")
    print(f"    • {seating_path.resolve()}")
    print(f"    • {faculty_path.resolve()}")


def generate_html_dashboard():
    if not assignments:
        arrange_students(show=False)
    if not faculty_duties:
        allocate_faculty(show=False)

    total_students = len(assignments)
    total_capacity = sum(r.capacity for r in rooms)
    room_cards = []

    for room in rooms:
        room_seats = [a for a in assignments if a.room_no == room.room_no]
        seat_rows = "".join(
            "<tr>"
            f"<td>{a.seat_no}</td><td>{escape(a.student.roll_no)}</td>"
            f"<td>{escape(a.student.name)}</td><td><span class='tag'>{escape(a.student.course)}</span></td>"
            f"<td>{a.row}</td><td>{a.column}</td>"
            "</tr>"
            for a in room_seats
        )
        # Visual seat map, four seats per row.
        seat_map = ""
        for start in range(0, len(room_seats), 4):
            seat_map += "<div class='seat-row'>"
            for a in room_seats[start:start + 4]:
                seat_map += (
                    "<div class='seat'>"
                    f"<strong>{a.seat_no:02d}</strong>"
                    f"<span>{escape(a.student.roll_no)}</span>"
                    f"<small>{escape(a.student.course)}</small>"
                    "</div>"
                )
            seat_map += "</div>"

        room_cards.append(f"""
        <section class="panel room-panel">
          <div class="panel-heading">
            <div><p class="eyebrow">CLASSROOM</p><h2>{escape(room.room_no)}</h2></div>
            <span class="capacity">{len(room_seats)} / {room.capacity} seats</span>
          </div>
          <h3>Seat map</h3>
          <div class="seat-map">{seat_map}</div>
          <h3>Detailed allocation</h3>
          <div class="table-wrap"><table>
            <thead><tr><th>Seat</th><th>Roll no.</th><th>Student</th><th>Course</th><th>Row</th><th>Column</th></tr></thead>
            <tbody>{seat_rows}</tbody>
          </table></div>
        </section>
        """)

    faculty_rows = "".join(
        "<tr>"
        f"<td>{escape(d['room_no'])}</td><td>{escape(d['faculty_id'])}</td>"
        f"<td>{escape(d['faculty_name'])}</td><td>{escape(d['department'])}</td>"
        "</tr>"
        for d in faculty_duties
    )

    student_rows = "".join(
        "<tr>"
        f"<td>{escape(s.roll_no)}</td><td>{escape(s.name)}</td><td><span class='tag'>{escape(s.course)}</span></td>"
        "</tr>"
        for s in students
    )

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Exam Allocator | Dashboard</title>
<style>
:root {{
  --bg:#f4f6fb; --panel:#ffffff; --ink:#172033; --muted:#68738a;
  --line:#e6eaf2; --accent:#5146e5; --accent-soft:#eeedff;
  --green:#16866a; --shadow:0 12px 34px rgba(28,39,75,.07);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
header{{background:#171b32;color:#fff;padding:34px max(24px,calc((100% - 1180px)/2)) 30px}}
.topline{{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}}
.brand{{display:flex;align-items:center;gap:12px}}
.logo{{width:44px;height:44px;border-radius:14px;background:#6d63ff;display:grid;place-items:center;font-size:22px;font-weight:800}}
.eyebrow{{margin:0 0 5px;color:#9ca6c6;font-size:11px;font-weight:800;letter-spacing:1.6px}}
h1{{font-size:clamp(25px,4vw,38px);line-height:1.1;margin:4px 0 8px}}
header p{{color:#c4c9dc;margin:0}}
.header-actions{{display:flex;gap:10px;flex-wrap:wrap}}
button,.button{{border:0;border-radius:10px;padding:11px 15px;font-weight:700;cursor:pointer;text-decoration:none}}
button{{background:#fff;color:#222743}}.secondary{{background:#2c3150;color:#fff;border:1px solid #484e70}}
main{{max-width:1180px;margin:28px auto;padding:0 22px 50px}}
.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px;margin-bottom:22px}}
.metric,.panel{{background:var(--panel);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow)}}
.metric{{padding:20px}}.metric .label{{color:var(--muted);font-size:13px;font-weight:650}}
.metric .number{{font-size:30px;font-weight:800;letter-spacing:-1px;margin-top:5px}}
.metric .note{{font-size:12px;color:var(--green);margin-top:2px}}
.section-title{{display:flex;align-items:end;justify-content:space-between;gap:12px;margin:28px 0 14px}}
.section-title h2{{margin:0;font-size:22px}}.section-title p{{margin:4px 0 0;color:var(--muted)}}
.panel{{padding:22px;margin-bottom:18px;min-width:0}}
.panel-heading{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}}
.panel h2{{font-size:24px;margin:0}}.panel h3{{font-size:14px;margin:22px 0 10px}}
.capacity{{background:var(--accent-soft);color:var(--accent);padding:7px 11px;border-radius:99px;font-size:12px;font-weight:800}}
.seat-map{{background:#f8f9fd;border:1px solid var(--line);padding:16px;border-radius:14px;display:flex;flex-direction:column;gap:10px;max-width:520px}}
.seat-row{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}}
.seat{{min-height:82px;background:#fff;border:1px solid #dfe3f0;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;box-shadow:0 3px 8px rgba(25,30,60,.04)}}
.seat strong{{font-size:16px;color:var(--accent)}}.seat span{{font-size:12px;font-weight:750}}.seat small{{font-size:10px;color:var(--muted)}}
.table-wrap{{overflow-x:auto;border:1px solid var(--line);border-radius:12px}}
table{{width:100%;border-collapse:collapse;white-space:nowrap;font-size:13px}}
th{{text-align:left;background:#f8f9fd;color:#5c6680;font-size:11px;letter-spacing:.5px;text-transform:uppercase}}
th,td{{padding:12px 14px;border-bottom:1px solid var(--line)}}tbody tr:last-child td{{border-bottom:0}}tbody tr:hover{{background:#fafaff}}
.tag{{display:inline-block;background:#f0efff;color:#5146e5;border-radius:7px;padding:3px 8px;font-size:11px;font-weight:800}}
.notice{{background:#fff9e9;border:1px solid #f1dfad;color:#6e5718;border-radius:12px;padding:14px 16px;font-size:13px}}
footer{{text-align:center;color:var(--muted);font-size:12px;padding:12px}}
@media(max-width:760px){{.metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}main{{padding:0 14px 30px}}.panel{{padding:15px}}}}
@media print{{body{{background:#fff}}header{{padding:20px;background:#171b32!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}}main{{max-width:none;margin:12px auto;padding:0}}.metric,.panel{{box-shadow:none;break-inside:avoid}}.header-actions{{display:none}}button{{display:none}}.room-panel{{break-before:page}}}}
</style>
</head>
<body>
<header>
  <div class="topline">
    <div class="brand"><div class="logo">EA</div><div><p class="eyebrow">ACADEMIC OPERATIONS</p><strong>EXAM ALLOCATOR</strong></div></div>
    <div class="header-actions"><button onclick="window.print()">Print / Save as PDF</button><button class="secondary" onclick="location.reload()">Refresh dashboard</button></div>
  </div>
  <div style="margin-top:28px"><p class="eyebrow">EXAM MANAGEMENT • DEMO REPORT</p><h1>Seating & Duty Dashboard</h1><p>A clear overview of student seating, room capacity and faculty assignments.</p></div>
</header>
<main>
  <div class="metrics">
    <div class="metric"><div class="label">Students allocated</div><div class="number">{total_students}</div><div class="note">All sample students assigned</div></div>
    <div class="metric"><div class="label">Classrooms</div><div class="number">{len(rooms)}</div><div class="note">Rooms in this demonstration</div></div>
    <div class="metric"><div class="label">Total capacity</div><div class="number">{total_capacity}</div><div class="note">Available seats</div></div>
    <div class="metric"><div class="label">Faculty duties</div><div class="number">{len(faculty_duties)}</div><div class="note">Room assignments created</div></div>
  </div>
  <div class="section-title"><div><h2>Room seating plans</h2><p>Seat map first, followed by a detailed searchable-looking table.</p></div></div>
  {''.join(room_cards)}
  <div class="section-title"><div><h2>Faculty duty roster</h2><p>Assigned invigilators for each classroom.</p></div></div>
  <section class="panel"><div class="table-wrap"><table><thead><tr><th>Room</th><th>Faculty ID</th><th>Faculty member</th><th>Department</th></tr></thead><tbody>{faculty_rows}</tbody></table></div></section>
  <div class="section-title"><div><h2>Student directory</h2><p>Reference list of registered students.</p></div></div>
  <section class="panel"><div class="table-wrap"><table><thead><tr><th>Roll number</th><th>Student name</th><th>Course</th></tr></thead><tbody>{student_rows}</tbody></table></div></section>
  <div class="notice"><strong>Algorithm note:</strong> Students are interleaved by course to reduce clustering. This simple heuristic does not guarantee that same-course students will never sit adjacent. Replace the sample records with verified college data before real use.</div>
  <footer>Exam Allocator • Generated locally by Python • No internet connection or third-party packages required</footer>
</main>
</body>
</html>"""

    dashboard_path = Path("exam_allocator_dashboard.html")
    dashboard_path.write_text(html_doc, encoding="utf-8")
    return dashboard_path.resolve()


def run_full_demo():
    display_students()
    display_rooms()
    arrange_students()
    allocate_faculty()
    export_csv()
    dashboard = generate_html_dashboard()
    print(f"\n  ✓ Beautiful HTML dashboard created:\n    {dashboard}")
    try:
        opened = webbrowser.open(dashboard.as_uri())
        if opened:
            print("  ✓ Opening dashboard in your browser...")
        else:
            print("  Open the HTML file above in Safari or Chrome.")
    except Exception:
        print("  Open the HTML file above in Safari or Chrome.")


def main():
    while True:
        print()
        print("╭" + "─" * 48 + "╮")
        print("│" + "          EXAM ALLOCATOR SYSTEM          " + "│")
        print("├" + "─" * 48 + "┤")
        print("│  1  Student directory                    │")
        print("│  2  Classroom overview                   │")
        print("│  3  Generate seating plan                │")
        print("│  4  Allocate faculty duties              │")
        print("│  5  Export CSV files                     │")
        print("│  6  Run full demo + open visual dashboard│")
        print("│  0  Exit                                 │")
        print("╰" + "─" * 48 + "╯")
        choice = input("  Choose an option [0-6]: ").strip()

        try:
            if choice == "1":
                display_students()
                pause()
            elif choice == "2":
                display_rooms()
                pause()
            elif choice == "3":
                arrange_students()
                pause()
            elif choice == "4":
                allocate_faculty()
                pause()
            elif choice == "5":
                export_csv()
                pause()
            elif choice == "6":
                run_full_demo()
                pause()
            elif choice == "0":
                print("\n  Thanks for using Exam Allocator. Goodbye!\n")
                break
            else:
                print("\n  Please enter a number from 0 to 6.")
        except (ValueError, OSError) as error:
            print(f"\n  ERROR: {error}")
            pause()


if __name__ == "__main__":
    main()
