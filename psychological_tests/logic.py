from .models import TestApplication, Baremo
from django.db.models import Sum

def calculate_test_results(application_id):
    """
    Calculates the total score and assigns a result label based on baremos.
    """
    try:
        application = TestApplication.objects.get(id=application_id)
        
        # 1. Calculate Total Score
        total_score = application.answers.aggregate(
            total=Sum('selected_option__value')
        )['total'] or 0
        
        application.total_score = total_score
        
        # 2. Assign Result Label (Baremo)
        # Find the baremo that fits the score
        baremo = Baremo.objects.filter(
            test=application.test,
            dimension__isnull=True, # Total score baremo
            min_score__lte=total_score,
            max_score__gte=total_score
        ).first()
        
        if baremo:
            application.result_label = baremo.result_text
            application.clinical_notes = baremo.clinical_interpretation
        
        application.save()
        return application
    except TestApplication.DoesNotExist:
        return None
