import csv
import io
from django.db import transaction
from companies.models import Company, CompanyEmployee

class BulkImportService:
    """
    Handles bulk importing of data (Patients, Employees) via CSV/Excel.
    Req: 6_0_GestionEmpresas.md (Carga Masiva)
    """

    @staticmethod
    @transaction.atomic
    def import_employees(company_id, csv_file):
        """
        Imports employees from a CSV file into a specific company.
        Expected headers: first_name, last_name, document_type, document_number, job_title, department
        """
        company = Company.objects.get(id=company_id)
        file_data = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(file_data))
        
        created_count = 0
        updated_count = 0
        
        for row in reader:
            employee, created = CompanyEmployee.objects.update_or_create(
                company=company,
                document_type=row.get('document_type', 'DNI'),
                document_number=row.get('document_number'),
                defaults={
                    'first_name': row.get('first_name'),
                    'last_name': row.get('last_name'),
                    'job_title': row.get('job_title', ''),
                    'department': row.get('department', ''),
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        return {
            'created': created_count,
            'updated': updated_count
        }

    @staticmethod
    @transaction.atomic
    def import_patients(clinic_id, csv_file):
        """
        Imports patients from a CSV file.
        """
        # Logic similar to import_employees but for Patient model
        pass
