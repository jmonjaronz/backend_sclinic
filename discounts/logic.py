from .models import Benefit, CompanyAffiliation
from django.db.models import Max

def get_best_benefit(patient):
    """
    Returns the benefit with the highest precedence applicable to the patient.
    """
    applicable_benefits = []
    
    # 1. Check B2B via affiliation
    affiliations = CompanyAffiliation.objects.filter(
        document_type=patient.document_type,
        document_number=patient.document_number,
        company__is_active=True
    )
    
    for aff in affiliations:
        company_benefits = Benefit.objects.filter(company=aff.company, is_active=True)
        applicable_benefits.extend(list(company_benefits))
        
    # 2. Check General promo benefits (non-B2B)
    general_benefits = Benefit.objects.filter(benefit_type__in=[Benefit.BenefitType.PROMO, Benefit.BenefitType.RECURRING], is_active=True, company__isnull=True)
    applicable_benefits.extend(list(general_benefits))
    
    if not applicable_benefits:
        return None
        
    # Sort by precedence (higher first) and then by highest discount percentage
    applicable_benefits.sort(key=lambda x: (-x.precedence, -x.discount_percentage))
    
    return applicable_benefits[0]
