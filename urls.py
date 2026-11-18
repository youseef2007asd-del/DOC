from django.contrib import admin
from django.urls import path
from library import views

urlpatterns = [
    path("doctor/", views.doctor_dashboard, name="doctor_dashboard"),
    path("doctor/login/", views.doctor_login, name="doctor_login"),
    path("doctor/logout/", views.doctor_logout, name="doctor_logout"),
    path("doctor/upload/", views.upload_document, name="upload_document"),
    path("doctor/codes/", views.create_access_code, name="create_access_code"),
    path("doctor/admin/", admin.site.urls),
    path("", views.guest_gate, name="home"),
    path("library/", views.library_list, name="library_list"),
    path("file/<int:pk>/", views.document_detail, name="document_detail"),
    path("file/<int:pk>/download/", views.download_document, name="download_document"),
]
