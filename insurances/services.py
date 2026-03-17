from decimal import Decimal
from .models import InsuranceCoverage

def calculate_patient_cost(patient_insurance, service):
    """
    Calcula el costo para el paciente basado en su seguro y el servicio solicitado.
    Busca cobertura específica por servicio o por especialidad.
    """
    plan = patient_insurance.plan
    base_price = Decimal(str(service.price))
    
    # 1. Buscar cobertura específica para el servicio
    coverage = InsuranceCoverage.objects.filter(plan=plan, service=service, is_covered=True).first()
    
    # 2. Si no hay, buscar por especialidad
    if not coverage:
        coverage = InsuranceCoverage.objects.filter(plan=plan, specialty=service.specialty, is_covered=True).first()
    
    if not coverage:
        # Sin cobertura: paga precio total (o lo que defina el negocio por defecto)
        return base_price, Decimal('0.00')

    # Cálculos
    copay = Decimal(str(coverage.copay_amount))
    coinsurance_pct = Decimal(str(coverage.coinsurance_percentage))
    
    # Coaseguro se aplica sobre el saldo después del copago? 
    # Generalmente en sistemas médicos: Copago es entrada, Coaseguro es % del neto.
    coinsurance_amount = (base_price - copay) * (coinsurance_pct / Decimal('100.00'))
    
    if coinsurance_amount < 0:
        coinsurance_amount = Decimal('0.00')
        
    return copay, coinsurance_amount
