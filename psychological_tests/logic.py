#psychological_tests/logic.py
from .models import TestApplication, Baremo, DimensionResult
from django.db import models
from django.utils import timezone

def calculate_test_results(application_id):
    """
    Calculates scores for each dimension and total score,
    then assigns result labels based on baremos.
    """
    try:
        # Optimization: use select_related for the test
        application = TestApplication.objects.select_related('test').get(id=application_id)
        test = application.test
        
        # Optimization: calculate scale limits once per test
        scale_stats = test.scale_options.aggregate(
            mx=models.Max('value'),
            mn=models.Min('value')
        )
        max_scale_value = scale_stats['mx'] or 0
        min_scale_value = scale_stats['mn'] or 0
        
        # 1. Calculate and save scores per Dimension
        dimensions = test.dimensions.all()
        total_score = 0.0
        
        for dim in dimensions:
            dim_score = 0
            # Optimization: use select_related for question and selected_option
            answers = application.answers.filter(question__dimension=dim).select_related('question', 'selected_option')
            
            for answer in answers:
                raw_value = answer.selected_option.value
                if answer.question.is_reverse_scored:
                    # Inversion logic: max + min - valor_actual
                    raw_value = max_scale_value + min_scale_value - raw_value
                dim_score += raw_value

            # Apply weight safely
            weight = getattr(dim, 'weight', 1.0)
            weighted_score = float(dim_score) * weight

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
