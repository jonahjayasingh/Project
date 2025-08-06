from django.shortcuts import render,redirect
from .models import Work
from datetime import datetime
from django.contrib import messages
from django.http import Http404
import os
from django.conf import settings
from collections import defaultdict
from app.models import StaffPermission, Student,Payment,Receipt,CourseName
from django.contrib.auth.models import User
import pandas as pd
from staff.models import Attendance
from staff.CustomOpreation.WorkUpdate import create_work_excel
from staff.CustomOpreation.attendance import create_attendance_excel
# Create your views here.
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required


@login_required
def staff_dashboard(request):
    work_queryset = Work.objects.filter(user=request.user, date=datetime.now().date()).order_by("time_slot")

    grouped_work = defaultdict(list)
    for work in work_queryset:
        grouped_work[work.time_slot].append(work)
    try:
            permission = StaffPermission.objects.get(user=request.user)
    except StaffPermission.DoesNotExist:
        permission = None
    grouped_work_dict = dict(grouped_work)
    content ={
        "grouped_work":grouped_work_dict,
        "permission":permission
    }
    return render(request, "staff/dashbord.html", content)

@login_required
def add_work(request):
    if request.method == "POST":
        user = request.user
        time_slot = request.POST.get("time_slot")
        work = request.POST.get("work")
        work = Work(work=work,time_slot=time_slot,user=user)
        work.save()
        return redirect("staff:staff_dashboard")


    return redirect("staff:staff_dashboard")

@login_required
def edit_work(request):
    if request.method == "POST":
        work = Work.objects.get(id=request.POST.get("work_id"))
        work.work = request.POST.get("work")
        work.save()
        return redirect("staff:staff_dashboard")
    return redirect("staff:staff_dashboard")

@login_required
def add_student(request):
    try:
        permission = StaffPermission.objects.get(user=request.user)
    except StaffPermission.DoesNotExist:
        permission = None

    content ={
        "students":Student.objects.filter(certificate_id__isnull=True),
        "permission":permission,
        "faculty":User.objects.filter(is_staff=True , is_superuser=False),
        "courses":CourseName.objects.all()
    }
    return render(request,"staff/add_Student.html",content)


@login_required
def show_certificate(request, location):

    try:
        filename = os.path.basename(location)
        pdf_path = os.path.join(settings.BASE_DIR,  "static",'media', 'certificates', filename)

        if not os.path.exists(pdf_path):
            raise Http404("Certificate not found")

        pdf_url = f"/media/certificates/{filename}"


    except Exception as e:

        raise Http404("Invalid certificate request")

    return render(request, "staff/show_certificate.html", {
        "pdf_url": pdf_url,
        "filename": filename,
        'doc_type': 'certificate'
    })

def send_email_with_pdf(pdf_path):
    id = pdf_path.split("_")[-1].split(".")[0]
    filename = pdf_path.split("\\")[-1]
    student = Student.objects.get(id=id)
    receipt = Receipt.objects.filter(student=student).order_by("-id")[0]

    subject = f'Recipt No: {receipt.reg_no} for {student.name} '
    body = f'Student Name: {student.name}\nCourse Name: {student.course_name}\nAmount: {receipt.amount}\nDate: {receipt.date.strftime("%d %B, %Y")}\n'
    from_email = settings.EMAIL_HOST_USER
    to_email = [settings.EMAIL_RECIVER ]

    email = EmailMessage(subject, body, from_email, to_email)

    with open(pdf_path, 'rb') as f:
        email.attach(f'{filename}', f.read(), 'application/pdf')

    email.send()

@login_required
def show_receipt(request, location):
    try:
        filename = os.path.basename(location)
        pdf_path = os.path.join(settings.BASE_DIR, "static",'media', 'receipt', filename)
        if not os.path.exists(pdf_path):
            raise Http404("Receipt not found")

        pdf_url = f"/media/receipt/{filename}"

    except Exception as e:
        raise Http404("Invalid receipt request")
    send_email_with_pdf(pdf_path)
    return render(request, "staff/show_certificate.html", {
        "pdf_url": pdf_url,
        "filename": filename
    })

@login_required
def single_student(request,id):
    student = Student.objects.get(id=id)
    faculty = User.objects.filter(is_staff=True)
    courses = CourseName.objects.all()
    if Payment.objects.filter(user=student).exists():
        payment = Payment.objects.get(user=student)
    else:
        payment = None
    try:
        permission = StaffPermission.objects.get(user=request.user)
    except StaffPermission.DoesNotExist:
        permission = None

    return render(request,"staff/single_student.html",{"student":student,"faculty":faculty,"payment":payment,"permission":permission,"courses":courses})

@login_required
def attendance(request):
    students = Student.objects.filter(faculty_name=request.user)
    today = datetime.now().date()

    if Attendance.objects.filter(user=request.user, date=today).exists():
        return redirect("staff:staff_dashboard")

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"student_{student.id}_status")
            if not status or status == "class_over":
                continue

            Attendance.objects.create(
                student=student,
                status=status,
                date=today,
                user=request.user
            )

        return redirect("staff:staff_dashboard")

    return render(request, "staff/attendance.html", {"students": students})


@login_required
def excel_view(request):
    last_month = request.POST.get("last_month")
    if last_month:
        work = Work.objects.filter(user=request.user,date__month=datetime.now().month-1)
    else:
        work = Work.objects.filter(user=request.user,date__month=datetime.now().month)
    if len(work) != 0:
        location = create_work_excel(work,request.user.username)
    else:
        return redirect("staff:staff_dashboard")
    try:
        location = os.path.join(settings.BASE_DIR, "static",'media', 'work', location)
    except Exception as e:
        raise Http404("Invalid location")

    df = pd.read_excel(location, engine='openpyxl')
    df = df.fillna("")
    html_table = df.to_html(
    index=False,
    escape=False
    )

    try:
        filename = os.path.basename(location)
        excel_url = f"/media/work/{filename}"


    except Exception as e:
        raise Http404("Invalid receipt request")

    return render(request, "staff/excel_view.html", {
        "html_table": html_table,
        "filename": excel_url
    })



@login_required
def excel_attendance(request):
    students = Student.objects.filter(faculty_name=request.user)
    last_month = request.POST.get("last_month")

    current_month = datetime.now().month
    query_month = current_month - 1 if last_month else current_month

    attendance = Attendance.objects.filter(
        user=request.user,
        student__in=students,
        date__month=query_month
    )

    if not attendance.exists():
        return redirect("staff:staff_dashboard")

    try:
        filename = create_attendance_excel(attendance, request.user.username)
        file_path = os.path.join(settings.BASE_DIR, "static", "media", "attendance", filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_excel(file_path, engine='openpyxl').fillna("")
        html_table = df.to_html(index=False, escape=False)

        excel_url = f"/media/attendance/{filename}"

        return render(request, "staff/excel_view.html", {
            "html_table": html_table,
            "filename": excel_url
        })

    except Exception as e:
        # Log error or display a user-friendly message
        raise Http404(f"Something went wrong generating the Excel file: {str(e)}")
