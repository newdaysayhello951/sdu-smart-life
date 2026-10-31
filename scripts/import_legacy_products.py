"""Explicit local import; reads old goods, never changes the source database.
Requires PyMySQL. Credentials come from DB_PASSWORD / DB_USER / DB_HOST.
"""
import os, json, struct
from pathlib import Path
from decimal import Decimal, InvalidOperation
import pymysql
root=Path(__file__).resolve().parents[1]
source=pymysql.connect(host=os.getenv('DB_HOST','127.0.0.1'),user=os.getenv('DB_USER','root'),password=os.environ['DB_PASSWORD'],database=os.getenv('LEGACY_DB','test'),charset='utf8mb4')
target=pymysql.connect(host=os.getenv('DB_HOST','127.0.0.1'),user=os.getenv('DB_USER','root'),password=os.environ['DB_PASSWORD'],database='sdu_smart_life',charset='utf8mb4')
# Images are stored in MySQL, not frontend static files.
report={'imported':0,'skipped':[],'locationConflicts':[]}
try:
 with source.cursor() as q:
  q.execute('SELECT address_id,name FROM address');addresses={}
  for key,name in q.fetchall():
   if key in addresses and addresses[key]!=name:report['locationConflicts'].append(key);addresses[key]=''
   else:addresses[key]=name or ''
  q.execute('SELECT good_id,name,content,price,picture,address_id FROM good');rows=q.fetchall()
 with target.cursor() as q:
  for key,title,description,raw_price,image,address in rows:
   try:
    price=Decimal(raw_price).quantize(Decimal('.01'))
    if not price.is_finite() or price<0 or price>=Decimal('10000000000'):raise ValueError()
    if not title or len(title)>120:raise ValueError()
   except (InvalidOperation,ValueError,TypeError):report['skipped'].append({'id':key,'reason':'invalid title or price'});continue
   extension='png' if image and image.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if image and image.startswith(b'\xff\xd8\xff') else None
   url='/assets/legacy/images/default.jpg'
   if extension:
    url='/assets/legacy/images/default.jpg'
   q.execute('INSERT INTO product(legacy_id,title,description,price,location,image_url) VALUES(%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE legacy_id=VALUES(legacy_id)',(key,title,description or '',price,addresses.get(address,''),url));report['imported']+=q.rowcount==1
   if extension:
    q.execute('SELECT id,image_url FROM product WHERE legacy_id=%s',(key,));product_id,current_url=q.fetchone()
    if not current_url.startswith('/api/images/product/'):
     q.execute('INSERT INTO product_image(product_id,content_type,data) VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE data=VALUES(data),content_type=VALUES(content_type)',(product_id,'image/png' if extension=='png' else 'image/jpeg',image))
     q.execute('UPDATE product SET image_url=%s WHERE id=%s',('/api/images/product/'+str(product_id),product_id))
 target.commit()
finally:source.close();target.close()
print(json.dumps(report,ensure_ascii=True))
