from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.utils.text import slugify
import secrets
import string

def document_upload_path(instance, filename):
    safe = slugify(filename.rsplit(".", 1)[0])[:70] or "document"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"library/{instance.subject_id or 'general'}/{safe}-{secrets.token_hex(5)}.{ext}"

class Subject(models.Model):
    name = models.CharField(max_length=160, unique=True, verbose_name="اسم المادة")
    description = models.TextField(blank=True, verbose_name="وصف المادة")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "مادة"
        verbose_name_plural = "المواد"

    def __str__(self):
        return self.name

class Document(models.Model):
    title = models.CharField(max_length=220, verbose_name="اسم الملف")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="documents", verbose_name="المادة")
    description = models.TextField(blank=True, verbose_name="وصف")
    file = models.FileField(upload_to=document_upload_path, verbose_name="الملف")
    allow_download = models.BooleanField(default=True, verbose_name="السماح بالتحميل")
    is_published = models.BooleanField(default=True, verbose_name="ظاهر للطلاب")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0, editable=False)
    downloads = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "ملف"
        verbose_name_plural = "الملفات"

    def __str__(self):
        return self.title

class AccessCode(models.Model):
    label = models.CharField(max_length=120, blank=True, verbose_name="اسم/ملاحظة الكود")
    code_hash = models.CharField(max_length=256, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name="ينتهي في")
    max_uses = models.PositiveIntegerField(null=True, blank=True, verbose_name="عدد مرات الاستخدام (فارغ = غير محدود)")
    uses = models.PositiveIntegerField(default=0, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name="مادة محددة (فارغ = كل المواد)")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    code_hint = models.CharField(max_length=4, blank=True, editable=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "كود دخول"
        verbose_name_plural = "أكواد الدخول"

    def __str__(self):
        return self.label or f"كود ينتهي {self.expires_at:%Y-%m-%d %H:%M}"

    @staticmethod
    def generate_plain_code():
        alphabet = string.ascii_uppercase + string.digits
        return "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3))

    def set_code(self, raw):
        self.code_hash = make_password(raw)
        self.code_hint = raw[-4:]

    def matches(self, raw):
        return check_password(raw.strip().upper(), self.code_hash)

    def usable(self):
        now = timezone.now()
        return (self.is_active and self.expires_at > now and
                (self.max_uses is None or self.uses < self.max_uses))
