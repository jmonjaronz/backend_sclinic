from .models import Benefit, CompanyAffiliation
from companies.models import Employee, Agreement
from django.db import models
from django.db.models import Max
from django.utils import timezone

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
        
    # 3. Check General promo benefits
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
        
    # Sort by precedence and then by highest discount percentage
    applicable_benefits.sort(key=lambda x: (-x['precedence'], -x['discount_percentage']))
    
    return applicable_benefits[0]
