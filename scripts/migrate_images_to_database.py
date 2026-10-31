"""One-time local migration. Reads old files, writes bytes and URL atomically. Never deletes files."""
import os
from pathlib import Path
import pymysql
root=Path(__file__).resolve().parents[1]
c=pymysql.connect(host=os.getenv('DB_HOST','127.0.0.1'),user=os.getenv('DB_USER','root'),password=os.environ['DB_PASSWORD'],database='sdu_smart_life',charset='utf8mb4')
try:
 with c.cursor() as q:
  q.execute('SELECT id,image_url FROM product');rows=q.fetchall();count=0
  for key,url in rows:
   if url.startswith('/api/images/product/'):continue
   if url.startswith('/api/images/'):file=root/'uploads'/Path(url).name
   elif url.startswith('/uploads/legacy-products/'):file=root/'frontend/public'/url.lstrip('/')
   else:continue
   data=file.read_bytes()
   mime='image/png' if data.startswith(b'\x89PNG') else 'image/jpeg' if data.startswith(b'\xff\xd8\xff') else None
   if not mime:raise ValueError('invalid image for product '+str(key))
   q.execute('INSERT INTO product_image(product_id,content_type,data) VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE data=VALUES(data),content_type=VALUES(content_type)',(key,mime,data))
   q.execute('UPDATE product SET image_url=%s WHERE id=%s',('/api/images/product/'+str(key),key));count+=1
 c.commit();print('migrated images:',count)
except: c.rollback();raise
finally:c.close()
