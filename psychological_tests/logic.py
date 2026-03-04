from .models import TestApplication, Baremo, DimensionResult, Dimension
from django.db.models import Sum
from django.utils import timezone

def calculate_test_results(application_id):
    """
    Calculates scores for each dimension and total score,
    then assigns result labels based on baremos.
    """
    try:
        application = TestApplication.objects.get(id=application_id)
        test = application.test
        
        # 1. Calculate and save scores per Dimension
        dimensions = test.dimensions.all()
        total_score = 0
        
        for dim in dimensions:
            # Sum values of answers belonging to this dimension
            dim_score = application.answers.filter(
                question__dimension=dim
            ).aggregate(total=Sum('selected_option__value'))['total'] or 0
            
            # Apply weight if defined
            weighted_score = dim_score * dim.weight
            
            # Find baremo for this dimension
            dim_baremo = Baremo.objects.filter(
                test=test,
                dimension=dim,
                min_score__lte=weighted_score,
                max_score__gte=weighted_score
            ).first()
            
            # Save dimension result
            DimensionResult.objects.update_or_create(
                application=application,
                dimension=dim,
                defaults={
                    'score': weighted_score,
                    'result_label': dim_baremo.result_text if dim_baremo else ""
                }
            )
            
            total_score += weighted_score

        # 2. Assign Global Total Score and Baremo
        application.total_score = int(total_score)
        
        global_baremo = Baremo.objects.filter(
            test=test,
            dimension__isnull=True,
            min_score__lte=total_score,
            max_score__gte=total_score
        ).first()
        
        if global_baremo:
            application.result_label = global_baremo.result_text
            application.clinical_notes = global_baremo.clinical_interpretation
        
        application.completed_at = timezone.now()
        application.save()
        
        return application
    except TestApplication.DoesNotExist:
        return None
