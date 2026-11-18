from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.files.base import File
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import CodeEntryForm, DocumentUploadForm, AccessCodeForm
from .models import AccessCode, Document, Subject

def current_guest_code(request):
    code_id = request.session.get("guest_code_id")
    if not code_id:
        return None
    try:
        code = AccessCode.objects.get(pk=code_id)
    except AccessCode.DoesNotExist:
        return None
    if not code.usable():
        request.session.pop("guest_code_id", None)
        return None
    return code

def guest_gate(request):
    if current_guest_code(request):
        return redirect("library_list")
    if request.method == "POST":
        form = CodeEntryForm(request.POST)
        if form.is_valid():
            raw = form.cleaned_data["code"].strip().upper()
            # Compare against active codes only; code strings are never stored in plaintext.
            for code in AccessCode.objects.filter(is_active=True, expires_at__gt=timezone.now()).select_related("subject"):
                if code.matches(raw) and code.usable():
                    code.uses += 1
                    code.save(update_fields=["uses"])
                    request.session["guest_code_id"] = code.pk
                    request.session.set_expiry(max(60, int((code.expires_at - timezone.now()).total_seconds())))
                    return redirect("library_list")
            form.add_error("code", "الكود غير صحيح أو منتهي الصلاحية أو استنفد عدد مرات الاستخدام.")
    else:
        form = CodeEntryForm()
    return render(request, "library/gate.html", {"form": form})

def library_list(request):
    code = current_guest_code(request)
    if not code:
        return redirect("home")
    docs = Document.objects.filter(is_published=True)
    if code.subject_id:
        docs = docs.filter(subject_id=code.subject_id)
    q = request.GET.get("q", "").strip()
    subject_id = request.GET.get("subject", "").strip()
    if q:
        docs = docs.filter(title__icontains=q) | docs.filter(description__icontains=q)
    if subject_id:
        docs = docs.filter(subject_id=subject_id)
    subjects = Subject.objects.all()
    if code.subject_id:
        subjects = subjects.filter(pk=code.subject_id)
    return render(request, "library/list.html", {
        "documents": docs.select_related("subject"), "subjects": subjects,
        "q": q, "selected_subject": subject_id, "code": code,
    })

def _authorized_document(request, pk):
    code = current_guest_code(request)
    if not code:
        raise PermissionDenied("يلزم إدخال كود دخول صالح.")
    doc = get_object_or_404(Document, pk=pk, is_published=True)
    if code.subject_id and doc.subject_id != code.subject_id:
        raise PermissionDenied("هذا الملف غير متاح لهذا الكود.")
    return doc

def document_detail(request, pk):
    doc = _authorized_document(request, pk)
    Document.objects.filter(pk=doc.pk).update(views=doc.views + 1)
    return render(request, "library/detail.html", {"document": doc})

def download_document(request, pk):
    doc = _authorized_document(request, pk)
    if not doc.allow_download:
        raise PermissionDenied("الدكتور لا يسمح بتحميل هذا الملف.")
    try:
        handle = doc.file.open("rb")
    except (FileNotFoundError, OSError):
        raise Http404("الملف غير متاح حاليًا.")
    Document.objects.filter(pk=doc.pk).update(downloads=doc.downloads + 1)
    response = FileResponse(handle, as_attachment=True, filename=doc.file.name.split("/")[-1])
    response["Cache-Control"] = "private, no-store"
    return response

def staff_required(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(staff_required, login_url="/doctor/login/")
def doctor_dashboard(request):
    from django.contrib.auth import get_user_model
    from django.db.models import Sum
    stats = {
        "documents": Document.objects.count(),
        "subjects": Subject.objects.count(),
        "codes": AccessCode.objects.filter(is_active=True, expires_at__gt=timezone.now()).count(),
        "views": Document.objects.aggregate(v=Sum("views"))["v"] or 0,
    }
    recent = Document.objects.select_related("subject").order_by("-uploaded_at")[:8]
    codes = AccessCode.objects.select_related("subject").order_by("-created_at")[:8]
    return render(request, "library/doctor_dashboard.html", {"stats": stats, "recent": recent, "codes": codes})

def doctor_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("doctor_dashboard")
    error = None
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""), password=request.POST.get("password", ""))
        if user and user.is_staff:
            login(request, user)
            return redirect("doctor_dashboard")
        error = "بيانات الدخول غير صحيحة أو الحساب ليس حساب دكتور."
    return render(request, "library/doctor_login.html", {"error": error})

@user_passes_test(staff_required, login_url="/doctor/login/")
def doctor_logout(request):
    logout(request)
    return redirect("doctor_login")

@user_passes_test(staff_required, login_url="/doctor/login/")
def upload_document(request):
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "تم رفع الملف بنجاح.")
            return redirect("doctor_dashboard")
    else:
        form = DocumentUploadForm()
    return render(request, "library/upload.html", {"form": form})

@user_passes_test(staff_required, login_url="/doctor/login/")
def create_access_code(request):
    plain = None
    if request.method == "POST":
        form = AccessCodeForm(request.POST)
        if form.is_valid():
            obj, plain = form.save_code()
            request.session["new_code_once"] = plain
            return redirect("create_access_code")
    else:
        form = AccessCodeForm()
    if request.session.get("new_code_once"):
        plain = request.session.pop("new_code_once")
    return render(request, "library/create_code.html", {"form": form, "plain": plain})
