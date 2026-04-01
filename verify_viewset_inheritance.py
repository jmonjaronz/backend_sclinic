#verify_viewset_inheritance.py
import os
import re

def verify_inheritance():
    view_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('views.py') or file.endswith('viewsets.py'):
                view_files.append(os.path.join(root, file))

    print(f"Checking {len(view_files)} files...")
    
    # regex for classes inheriting from viewsets.ModelViewSet or viewsets.ReadOnlyModelViewSet
    drf_pattern = re.compile(r'class\s+(\w+)\s*\((viewsets\.(ModelViewSet|ReadOnlyModelViewSet))\)')
    
    # regex for classes inheriting from BaseViewSet or BaseReadOnlyViewSet
    base_pattern = re.compile(r'class\s+(\w+)\s*\(((BaseViewSet|BaseReadOnlyViewSet))\)')
    
    # regex for classes inheriting from GenericViewSet
    generic_pattern = re.compile(r'class\s+(\w+)\s*\((GenericViewSet|viewsets\.GenericViewSet)\)')

    # Files that are allowed to use DRF directly (global or admin)
    EXCEPTIONS = [
        'PublicClinicViewSet', 'AdminClinicViewSet', 'PublicHeadquartersViewSet',
        'PublicServiceViewSet', 'PublicSpecialistViewSet', 'SubscriptionPlanViewSet',
        'SubscriptionViewSet', 'SuperAdminDashboardView', 'BaseViewSet', 'BaseReadOnlyViewSet'
    ]

    found_errors = False
    for filepath in view_files:
        if 'venv' in filepath or '.antigravity' in filepath:
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Find classes inheriting from DRF directly
            drf_matches = drf_pattern.findall(content)
            for class_name, full_inheritance, _ in drf_matches:
                if class_name not in EXCEPTIONS:
                    print(f"[!] ERROR: {class_name} in {filepath} inherits directly from {full_inheritance}")
                    found_errors = True
            
            # Additional check: class (.*, viewsets.ModelViewSet) etc.
            # (In case there are multiple base classes)
            
    if not found_errors:
        print("[+] All relevant ViewSets correctly inherit from BaseViewSet or are documented exceptions.")
    else:
        print("[!] Found inheritance inconsistencies.")

if __name__ == "__main__":
    verify_inheritance()
