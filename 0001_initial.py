# Generated initial migration
import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Subject", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=160, unique=True, verbose_name="اسم المادة")),
            ("description", models.TextField(blank=True, verbose_name="وصف المادة")),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"verbose_name": "مادة", "verbose_name_plural": "المواد", "ordering": ["name"]}),
        migrations.CreateModel(name="AccessCode", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("label", models.CharField(blank=True, max_length=120, verbose_name="اسم/ملاحظة الكود")),
            ("code_hash", models.CharField(editable=False, max_length=256)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("expires_at", models.DateTimeField(verbose_name="ينتهي في")),
            ("max_uses", models.PositiveIntegerField(blank=True, null=True, verbose_name="عدد مرات الاستخدام (فارغ = غير محدود)")),
            ("uses", models.PositiveIntegerField(default=0, editable=False)),
            ("is_active", models.BooleanField(default=True, verbose_name="نشط")),
            ("code_hint", models.CharField(blank=True, editable=False, max_length=4)),
            ("subject", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="library.subject", verbose_name="مادة محددة (فارغ = كل المواد)")),
        ], options={"verbose_name": "كود دخول", "verbose_name_plural": "أكواد الدخول", "ordering": ["-created_at"]}),
        migrations.CreateModel(name="Document", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=220, verbose_name="اسم الملف")),
            ("description", models.TextField(blank=True, verbose_name="وصف")),
            ("file", models.FileField(upload_to="library.models.document_upload_path", verbose_name="الملف")),
            ("allow_download", models.BooleanField(default=True, verbose_name="السماح بالتحميل")),
            ("is_published", models.BooleanField(default=True, verbose_name="ظاهر للطلاب")),
            ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ("views", models.PositiveIntegerField(default=0, editable=False)),
            ("downloads", models.PositiveIntegerField(default=0, editable=False)),
            ("subject", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="documents", to="library.subject", verbose_name="المادة")),
        ], options={"verbose_name": "ملف", "verbose_name_plural": "الملفات", "ordering": ["-uploaded_at"]}),
    ]
