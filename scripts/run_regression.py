"""Run all active migrations' local API regressions; fail if any child fails."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
names=['check_boundaries.py','check_login_publish.py','check_profile.py','check_product_management.py','check_product_images.py','check_products.py','check_campus.py','check_conversations.py','check_matching_chat_notifications.py']
failed=[]
for name in names:
 result=subprocess.run([sys.executable,str(root/'scripts'/name)],cwd=root)
 if result.returncode:failed.append(name)
print('REGRESSION:',len(names)-len(failed),'passed;',len(failed),'failed')
if failed:print('FAILED:',', '.join(failed))
sys.exit(bool(failed))
