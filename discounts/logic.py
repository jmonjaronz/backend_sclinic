from .models import Benefit, CompanyAffiliation
from companies.models import Employee, Agreement
from patients.models import DependentLink
from django.db import models
from django.db.models import Max
from django.utils import timezone
from decimal import Decimal

def get_best_benefit(patient):
    """
    Returns the benefit with the highest precedence applicable to the patient.
    Considers legacy logic and the new B2B Agreements.
    """
    applicable_benefits: list = []
    today = timezone.now().date()
    
    # 1. NEW B2B Logic: Check Employee status and active Agreements
    if hasattr(patient, 'employment_info'):
        employee = patient.employment_info
        if employee.status == 'ACTIVE':
            # Find active agreements for this company
            agreements = Agreement.objects.filter(
                company=employee.company,
                is_active=True,
                valid_from__lte=today
            ).filter(models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today))
            
            for ag in agreements:
                # Wrap Agreement in a Benefit-like object or return it directly if we refactor.
                # For now, let's treat the highest discount as a candidate.
                applicable_benefits.append({
                    'name': ag.name,
                    'type': 'B2B_AGREEMENT',
                    'discount_percentage': ag.discount_percentage,
                    'precedence': 10, # B2B Agreements usually have high priority
                    'object': ag
                })

    # 2. LEGACY Logic: Check B2B via affiliation (discounts app)
    affiliations = CompanyAffiliation.objects.filter(
        document_type=patient.document_type,
        document_number=patient.document_number,
        company__is_active=True
    )
    
    for aff in affiliations:
        company_benefits = Benefit.objects.filter(company=aff.company, is_active=True)
        for b in company_benefits:
            applicable_benefits.append({
                'name': b.name,
                'type': 'B2B_LEGACY',
                'discount_percentage': b.discount_percentage,
                'precedence': b.precedence,
                'object': b
            })
        
    # 3. FAMILY Logic: If patient is a dependent, check tutor's benefits
    tutor_links = DependentLink.objects.filter(patient=patient).select_related('tutor__patient_profile')
    for link in tutor_links:
        if hasattr(link.tutor, 'patient_profile'):
            tutor_patient = link.tutor.patient_profile
            tutor_benefit = get_best_benefit(tutor_patient)
            if tutor_benefit:
                applicable_benefits.append({
                    'name': f"{tutor_benefit['name']} (Beneficio Familiar)",
                    'type': 'FAMILY',
                    'discount_percentage': tutor_benefit['discount_percentage'],
                    'precedence': tutor_benefit['precedence'],
                    'object': tutor_benefit['object']
                })

    # 4. Check General promo/recurring benefits (no company needed)
    general_benefits = Benefit.objects.filter(
        benefit_type__in=[Benefit.BenefitType.PROMO, Benefit.BenefitType.RECURRING],
        is_active=True,
        company__isnull=True
    )
    for b in general_benefits:
        applicable_benefits.append({
            'name': b.name,
            'type': 'PROMO',
            'discount_percentage': b.discount_percentage,
            'precedence': b.precedence,
            'object': b
        })

    if not applicable_benefits:
        return None

    # Sort by precedence desc, then by highest discount percentage desc
    applicable_benefits.sort(key=lambda x: (-x['precedence'], -x['discount_percentage']))

    return applicable_benefits[0]


def calculate_final_price(base_price: Decimal, patient) -> dict:
    """
    Returns the final price after applying the best benefit.
    Returns a dict with: original_price, discount_percentage, final_price, benefit_applied.
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
