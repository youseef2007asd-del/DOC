from django.contrib import admin
from .models import Subject, Document, AccessCode

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "is_published", "allow_download", "views", "downloads", "uploaded_at")
    list_filter = ("subject", "is_published", "allow_download")
    search_fields = ("title", "description")
    readonly_fields = ("views", "downloads", "uploaded_at")
    list_per_page = 50

@admin.register(AccessCode)
class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ("label", "code_hint", "subject", "expires_at", "uses", "max_uses", "is_active")
    list_filter = ("is_active", "subject")
    readonly_fields = ("code_hash", "code_hint", "uses", "created_at")
    search_fields = ("label",)
    actions = ["deactivate_codes"]

    @admin.action(description="إيقاف الأكواد المحددة")
    def deactivate_codes(self, request, queryset):
        queryset.update(is_active=False)
