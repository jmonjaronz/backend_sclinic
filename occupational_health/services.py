from django.utils import timezone
from .models import EvaluationServiceStatus, OccupationalEvaluation
from companies.models import ProtocolService

class OccupationalHealthService:
    @staticmethod
    def initialize_evaluation_services(evaluation):
        """
        Popula los servicios a realizar basados en el protocolo asignado.
        """
        protocol = evaluation.protocol
        protocol_services = ProtocolService.objects.filter(protocol=protocol)
        
        created_count = 0
        for ps in protocol_services:
            EvaluationServiceStatus.objects.get_or_create(
                evaluation=evaluation,
                protocol_service=ps,
                defaults={'status': EvaluationServiceStatus.ServiceStatus.PENDING}
            )
            created_count += 1
            
        return created_count

    @staticmethod
    def update_evaluation_global_status(evaluation):
        """
        Revisa si todos los servicios están completados para mover el estado de la evaluación.
        """
        services = evaluation.service_tracking.all()
        if not services.exists():
            return evaluation.status

        all_completed = all(s.status == EvaluationServiceStatus.ServiceStatus.COMPLETED for s in services)
        
        if all_completed and evaluation.status != OccupationalEvaluation.EvaluationStatus.COMPLETED:
            evaluation.status = OccupationalEvaluation.EvaluationStatus.PENDING_RESULTS
            evaluation.save()
            
        return evaluation.status

    @staticmethod
    def generate_final_dictum(evaluation, doctor, result, restrictions="", recommendations=""):
        """
        Cierra la evaluación y genera el dictamen de aptitud.
        """
        from .models import AptitudeDictum
        import datetime
        
        # 1. Crear el dictamen
        dictum = AptitudeDictum.objects.create(
            evaluation=evaluation,
            doctor=doctor,
            result=result,
            labor_restrictions=restrictions,
            medical_recommendations=recommendations,
            expiry_date=timezone.now().date() + datetime.timedelta(days=365) # Default 1 year
        )
        
        # 2. Cerrar la evaluación
        evaluation.status = OccupationalEvaluation.EvaluationStatus.COMPLETED
        evaluation.completed_at = timezone.now()
        evaluation.save()
        
        return dictum
