from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum
from core.permissions import IsSuperAdmin
from core.models import Clinic
from appointments.models import Appointment
from users.models import User
from companies.models import Agreement

class SuperAdminDashboardView(APIView):
    """
    Global metrics for the SuperAdmin.
    """
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        total_clinics = Clinic.objects.count()
        active_clinics = Clinic.objects.filter(status=Clinic.Status.ACTIVE).count()
        
        total_appointments = Appointment.objects.count()
        confirmed_appointments = Appointment.objects.filter(status='CONFIRMED').count()
        
        total_users = User.objects.count()
        total_patients = User.objects.filter(role='PATIENT').count()
        
        # Revenue estimate (sum of service prices for confirmed appointments)
        total_revenue = Appointment.objects.filter(status__in=['CONFIRMED', 'COMPLETED']).aggregate(
            total=Sum('service__price')
        )['total'] or 0
        
        # B2B activity
        total_agreements = Agreement.objects.count()
        
        # Breakdown by clinic
        clinics_data = Clinic.objects.annotate(
            appointment_count=Count('appointments'),
            user_count=Count('users')
        ).values('id', 'name', 'appointment_count', 'user_count', 'status')

        return Response({
            "summary": {
                "total_clinics": total_clinics,
                "active_clinics": active_clinics,
                "total_appointments": total_appointments,
                "confirmed_appointments": confirmed_appointments,
                "total_users": total_users,
                "total_patients": total_patients,
                "total_revenue": total_revenue,
                "total_agreements": total_agreements,
            },
            "clinics": clinics_data
        })
