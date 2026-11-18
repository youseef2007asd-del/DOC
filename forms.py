from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Document, AccessCode

class CodeEntryForm(forms.Form):
    code = forms.CharField(max_length=32, label="كود الدخول", widget=forms.TextInput(attrs={
        "placeholder": "XXXX-XXXX-XXXX", "autocomplete": "off", "dir": "ltr"
    }))

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "subject", "description", "file", "allow_download", "is_published"]

class AccessCodeForm(forms.Form):
    label = forms.CharField(max_length=120, required=False, label="اسم الكود / ملاحظة")
    duration_hours = forms.IntegerField(min_value=1, max_value=8760, initial=24, label="مدة الصلاحية بالساعات")
    max_uses = forms.IntegerField(min_value=1, required=False, label="عدد مرات الاستخدام (اتركه فارغًا بلا حد)")
    subject = forms.ModelChoiceField(queryset=None, required=False, label="مادة محددة (اختياري)")

    def __init__(self, *args, **kwargs):
        from .models import Subject
        super().__init__(*args, **kwargs)
        self.fields["subject"].queryset = Subject.objects.all()

    def save_code(self):
        from .models import AccessCode
        data = self.cleaned_data
        plain = AccessCode.generate_plain_code()
        obj = AccessCode(
            label=data["label"],
            expires_at=timezone.now() + timedelta(hours=data["duration_hours"]),
            max_uses=data["max_uses"],
            subject=data["subject"],
        )
        obj.set_code(plain)
        obj.save()
        return obj, plain
