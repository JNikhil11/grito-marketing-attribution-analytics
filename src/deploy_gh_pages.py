import os
import shutil
import subprocess
import base64

repo_dir = 'Grito_Marketing_Analytics'

print("1. Checking out gh-pages...")
subprocess.run(['git', '-C', repo_dir, 'checkout', 'gh-pages'], check=True)

print("2. Copying updated files from main:dashboard...")
files_to_copy = [
    'index.html',
    'chart.min.js',
    'app.py',
    'dashboard_screenshot.png',
    'Dashboard_Report.pdf',
    'POWERBI_SPEC.md',
    'POWERBI_BUILD_CHECKLIST.md'
]

for f in files_to_copy:
    subprocess.run(['git', '-C', repo_dir, 'checkout', 'main', '--', f'dashboard/{f}'], check=True)
    src_f = os.path.join(repo_dir, 'dashboard', f)
    dst_f = os.path.join(repo_dir, f)
    if os.path.exists(src_f):
        shutil.move(src_f, dst_f)

dash_dir = os.path.join(repo_dir, 'dashboard')
if os.path.exists(dash_dir):
    shutil.rmtree(dash_dir)

print("3. Committing to gh-pages...")
subprocess.run(['git', '-C', repo_dir, 'add', '.'], check=True)
subprocess.run(['git', '-C', repo_dir, 'commit', '-m', 'deploy: update live interactive dashboard with verified attribution metrics and candidate name'], check=True)

print("4. Pushing gh-pages to origin...")
res = subprocess.run(['C:\\Program Files\\GitHub CLI\\gh.exe', 'auth', 'token'], capture_output=True, text=True)
token = res.stdout.strip()
auth_str = base64.b64encode(f'x-access-token:{token}'.encode()).decode()

cmd = ['git', '-C', repo_dir, '-c', f'http.extraHeader=AUTHORIZATION: basic {auth_str}', 'push', 'origin', 'gh-pages', '--force']
p = subprocess.run(cmd, capture_output=True, text=True)
print('STDOUT:', p.stdout)
print('STDERR:', p.stderr)
print('Exit code:', p.returncode)

print("5. Switching back to main...")
subprocess.run(['git', '-C', repo_dir, 'checkout', 'main'], check=True)
print("Done!")
