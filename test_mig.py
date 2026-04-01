#test_mig.py
import sys
import subprocess

with open('mig_result.txt', 'w', encoding='utf-8') as f:
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'makemigrations', 'users'],
            capture_output=True,
            text=True
        )
        f.write('STDOUT:\n' + result.stdout + '\n')
        f.write('STDERR:\n' + result.stderr + '\n')
        f.write('RETURNCODE:\n' + str(result.returncode))
    except Exception as e:
        f.write(f'ERROR: {e}')
