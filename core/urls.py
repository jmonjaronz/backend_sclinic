#core/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App endpoints
    path('api/users/', include('users.urls')),
    path('api/clinics/', include('clinics.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/clinical-records/', include('clinical_records.urls')),
    path('api/psychological-tests/', include('psychological_tests.urls')),
    path('api/medical-results/', include('medical_results.urls')),
    path('api/companies/', include('companies.urls')),
    path('api/discounts/', include('discounts.urls')),
    path('api/insurances/', include('insurances.urls')),
    path('api/occupational-health/', include('occupational_health.urls')),
]
