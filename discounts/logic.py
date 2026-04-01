#discounts/logic.py
from .models import Benefit
from companies.models import CompanyEmployee, Agreement
from patients.models import DependentLink
from django.db import models
from django.utils import timezone
from decimal import Decimal

def get_best_benefit(patient):
    """
    Returns the benefit with the highest precedence applicable to the patient.
    """
    applicable_benefits: list = []
    today = timezone.now().date()
    
    # 1. NEW B2B Logic: Check CompanyEmployee status and active Agreements
    employments = CompanyEmployee.objects.filter(patient=patient, status='ACTIVE')
    for emp in employments:
        # Find active agreements for this company
        agreements = Agreement.objects.filter(
            company=emp.company,
            is_active=True,
            valid_from__lte=today
        ).filter(models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today))
        
        for ag in agreements:
            applicable_benefits.append({
                'name': f"{emp.company.razon_social}: {ag.name}",
                'type': 'B2B_AGREEMENT',
                'discount_percentage': ag.discount_percentage,
                'precedence': 100, # Agreements usually have top priority
                'object': ag
            })

    # 2. General Benefits Logic: Adulto Mayor, Promo, etc.
    # We match by segmentation rules in models.py
    # Calculate patient age
    patient_age = None
    if patient.birth_date:
        patient_age = (today - patient.birth_date).days // 365

    general_benefits = Benefit.objects.filter(
        is_active=True
    ).filter(
        models.Q(valid_from__isnull=True) | models.Q(valid_from__lte=today)
    ).filter(
        models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today)
    )

    for b in general_benefits:
        # Filter by age if defined
        if b.min_age and (patient_age is None or patient_age < b.min_age):
            continue
        if b.max_age and (patient_age is None or patient_age > b.max_age):
            continue
        
        # Filter by previous visits (placeholder logic, would need Appointment counts)
        # if b.min_previous_visits and patient.appointments.count() < b.min_previous_visits:
        #     continue

        applicable_benefits.append({
            'name': b.name,
            'type': b.benefit_type,
            'discount_percentage': b.discount_percentage,
            'precedence': b.precedence,
            'object': b
        })

    # 3. FAMILY Logic: If patient is a dependent, check tutor's benefits
    tutor_links = DependentLink.objects.filter(patient=patient).select_related('tutor')
    for link in tutor_links:
        if hasattr(link.tutor, 'patient_profile'):
            tutor_patient = link.tutor.patient_profile
            tutor_benefit = get_best_benefit(tutor_patient)
            if tutor_benefit:
                applicable_benefits.append({
                    'name': f"{tutor_benefit['name']} (Familiar)",
                    'type': 'FAMILY',
                    'discount_percentage': tutor_benefit['discount_percentage'],
                    'precedence': tutor_benefit['precedence'],
                    'object': tutor_benefit['object']
                })

    if not applicable_benefits:
        return None

    # Sort by precedence desc, then by highest discount percentage desc
    applicable_benefits.sort(key=lambda x: (-x['precedence'], -x['discount_percentage']))

    return applicable_benefits[0]


def calculate_final_price(base_price: Decimal, patient) -> dict:
    """
    Returns the final price after applying the best benefit.
    """
    best = get_best_benefit(patient)
    if not best:
        return {
            'original_price': base_price,
            'discount_percentage': Decimal('0'),
            'final_price': base_price,
            'benefit_applied': None
        }

    discount_pct = Decimal(str(best['discount_percentage']))
    final_price = base_price * (1 - discount_pct / 100)
    return {
        'original_price': base_price,
        'discount_percentage': discount_pct,
        'final_price': round(final_price, 2),
        'benefit_applied': best['name']
    }

