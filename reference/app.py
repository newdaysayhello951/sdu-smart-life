#conn = pymysql.connect(host="127.0.0.1" , user="root" , password="<REDACTED>" , database="db003" , charset="utf8mb4" , port=3306)
#cursor = conn.cursor()
#print(cursor)
import pymysql
from flask import Flask
from flask import render_template
from flask import request,redirect, url_for, g
from flask import jsonify
import os
import base64
from werkzeug.utils import secure_filename





app = Flask(__name__,static_folder='static')

user_id = 0
user_name = '未登录用户'
need_id = 0
user_id_use = 0
g_good_id = 0
is_add = 0
is_login = 0

def init():
        global user_id
        global need_id
        global address_id
    ##连接数据库
        db = pymysql.connect(
      host='127.0.0.1',
      port=3306,
      user='root',
      passwd=os.environ.get('DB_PASSWORD', ''),
      db='test',
      charset='utf8'
        )
        #print('mysql connect success')
        #fin = open("C:/Users/86134/Downloads/sdu-database-experiment-three-master/sdu-database-experiment-three-main(1)/sdu-database-experiment-three-main/static/images/hdrenwu.png", 'rb')
        #img=fin.read()
        #fin.close()
    # 创建游标
        cur = db.cursor()
  
        # 查询最大用户ID
        sql = 'SELECT max(user_id) FROM user'
        cur.execute(sql)
        maxuser = cur.fetchone()[0] # 确保maxuser是整数
        if maxuser is None:
            maxuser = 0 # 如果没有用户，从0开始
        user_id = maxuser
        #查询最大need编号
        sql = 'SELECT max(need_id) FROM need'
        cur.execute(sql)
        max_need_id = cur.fetchone()[0]
        if max_need_id is None:
            max_need_id = 0 # 如果没有用户，从0开始
        need_id = max_need_id



@app.route('/')
def index():
    global user_name
    global is_login
    is_find = request.args.get('is_find')  # 获取 URL 中的 is_find 参数
    user_info_ = {
        'username': user_name,
        'profile_picture': 'picture/th1.jpg',
        'is_login': is_login
    }
    if(is_find):
        user_info_['profile_picture'] = 'images/test_new.png'

    return render_template('index.html',user_information = user_info_)


@app.route('/register', methods=['POST','GET'])
def register():
    global user_id
    init()
    username = request.args.get('username')  # 获取查询参数中的用户名
    password = request.args.get('password')  # 获取查询参数中的密码

    # 输出用户名和密码（在实际应用中，不建议输出密码）
    #print(f'用户名: {username}')
    #print(f'密码: {password}')
    # 进行一些简单的验证，假设用户名和密码不能为空
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    try:
 ##连接数据库
        db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            passwd=os.environ.get('DB_PASSWORD', ''),
            db='test',
            charset='utf8'
        )
        #print('mysql connect success')
        fin = open("static/images/hdrenwu.png",'rb')  #'rb'加上才能将图片读取为二进制
        img = fin.read()     #将二进制数据读取到img中
        fin.close()
        ##插入数据到表
        cur = db.cursor()
        sql = 'INSERT INTO user values (%s,%s,%s,%s,%s,%s,%s)'
        user_id = user_id + 1
        #print(user_id)
        #print('sad')
        value = (user_id, '908', username, img,password,'unKnow','这个人比较懒，还没有签名')
        cur.execute(sql, value)
        db.commit()
        print("数据插入成功")

    except pymysql.Error as e:
        print('connect error'+str(e))


    # 在这里可以执行注册逻辑，比如保存到数据库
    #print(f"注册成功！用户名: {username}, 密码: {password}")

    # 返回成功的响应
    return redirect(url_for('register_success'))


@app.route('/register_success')
def register_success():
    return render_template('register_success.html')

@app.route('/login')
def login():

    
    return render_template('login.html')

@app.route('/try_login',methods=['POST','GET'])
def try_login():
    global user_name
    global user_id_use
    global is_add
    global is_login
    init()
    # 从表单中获取提交的用户名和密码
    #to_do       
    #从数据库读取数据
    #从数据库读取数据
    username = request.form.get('username')
    password = request.form.get('pass')

    is_find = False

    sql_username = 'admin'
    sql_password = 'pass123'

    sql = 'SELECT * FROM user WHERE name = %s AND password = %s'

        # 连接数据库
    db = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        passwd=os.environ.get('DB_PASSWORD', ''),
        db='test',
        charset='utf8'
    )
    #print('mysql connect success')

        # 查询表中数据
    cur = db.cursor()
    cur.execute(sql, (username, password))
    #print(1111111111)
    result = cur.fetchone()
    if result:
        is_find = True
        # 假设user_name是第三列，passw是第五列
        sql_user_id = result[0]
        sql_username = result[2] # 根据实际列索引调整
        sql_images = result[3]
        sql_password = result[4]   # 根据实际列索引调整
        fout = open("C:\\Users\\86134\\Desktop\\sdu\\sdu-database-experiment-three-main\\static\\images\\test_new.png", 'wb')
        fout.write(sql_images)
        fout.close()
        #print("数据查询成功")
        # 在try块内打印user_name和passw，确保它们在查询成功时被定义
        #print(sql_username)
        #print(sql_password)
    else:
        print("没有找到匹配的用户")
   
    db.close()

    
    print("open success")

    # 进行简单的用户名和密码验证（这里只是示例，实际中应更复杂）
    if username == sql_username and password == sql_password:
        user_name = username
        user_id_use = sql_user_id
        is_add = 0
        is_login = 1
        return redirect(url_for('index',is_find = is_find))  # 如果登录成功，跳转到用户仪表板
    else:
        return redirect(url_for('login_error'))  # 登录失败时给出错误提示
    
@app.route('/login_error')
def login_error():
    return render_template('login_error.html')





#性别设置
@app.route('/upload_gender', methods=['POST'])
def upload_gender():
    gender = request.form['gender']
    db = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    user='root',
                    passwd=os.environ.get('DB_PASSWORD', ''),
                    db='test',
                    charset='utf8'
                )
    cur=db.cursor()
    sql='update user set sex=%s where user_id=%s'
    cur.execute(sql,(gender,user_id_use))
    db.commit()
    return '性别提交成功'

@app.route('/upload_signature', methods=['POST'])
def upload_signature():
    signature = request.form['signature']
    db = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    user='root',
                    passwd=os.environ.get('DB_PASSWORD', ''),
                    db='test',
                    charset='utf8'
                )
    cur=db.cursor()
    sql='update user set signature=%s where user_id=%s'
    cur.execute(sql,(signature,user_id_use))
    db.commit()
    return '个性签名提交成功'








# 设置上传文件的保存目录
UPLOAD_FOLDER = "C:\\Users\\86134\\Pictures\\Screenshot" +'\\' # 请替换为您的实际路径
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file.filename != '':
            # 确保文件名是安全的
            filename = secure_filename(file.filename)
            # 构建文件的绝对路径
            absolute_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 保存文件
            file.save(absolute_path)
            
            # 现在使用绝对路径读取文件内容
            with open(absolute_path, 'rb') as f:
                # 读取文件内容
                file_content = f.read()
            
            # 连接数据库
                db = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    user='root',
                    passwd=os.environ.get('DB_PASSWORD', ''),
                    db='test',
                    charset='utf8'
                )
                cur=db.cursor()
                sql='update user set picture=%s where user_id=%s'
                cur.execute(sql,(file_content,user_id_use))
                db.commit()
      # 可以重定向到其他页面或显示消息
                return redirect(url_for('success'))
    return redirect(url_for('index'))

# 确保使用werkzeug.secure_filename来避免安全问题
from werkzeug.utils import secure_filename


@app.route('/success')
def success():
    return '头像上传成功,下次登录时展示新头像'




UPLOAD_FOLDER = "C:\\Users\\86134\\Pictures\\Screenshot" +'\\' # 请替换为您的实际路径
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 检查文件扩展名是否合法
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/sendgood', methods=['POST'])
def send_good():
    # 获取表单数据
    product_name = request.form.get('productName')
    estimated_price = request.form.get('estimatedPrice')
    transaction_location = request.form.get('transactionLocation')
    description = request.form.get('description')
    print(product_name)
    print(estimated_price)
    print(transaction_location)
    print(description)
    file = request.files['productImage']
     # 确保文件名是安全的
    filename = secure_filename(file.filename)
            # 构建文件的绝对路径
    absolute_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 保存文件
    file.save(absolute_path)
            
            # 现在使用绝对路径读取文件内容
    with open(absolute_path, 'rb') as f:
                # 读取文件内容
        file_content = f.read()
    db = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    user='root',
                    passwd=os.environ.get('DB_PASSWORD', ''),
                    db='test',
                    charset='utf8'
                )
    cur=db.cursor()
    sql='select address_id from address where name=%s'
    cur.execute(sql,transaction_location)
    address_id=cur.fetchone()[0]
    print(address_id)
    sql='select max(good_id) from good '
    cur.execute(sql)
    max_good_id=cur.fetchone()[0]
    print(max_good_id)
    if max_good_id==None:
        max_good_id=1
    else:
        max_good_id=max_good_id+1
    sql='insert into good values(%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql,(user_id_use,max_good_id,product_name,file_content,description,address_id,0,estimated_price))
    db.commit()
     
        
    print('商品发布成功！')
    return redirect(url_for('success'))

from flask import Flask, request, make_response

@app.route('/reply', methods=['POST'])
def handle_reply():
    data = request.get_json()  # 获取JSON数据
    skill_id = data['skillId']  # 获取技能ID
    # 这里添加你的逻辑，比如保存回复内容到数据库
    # 假设我们返回一个URL作为响应
    return redirect(url_for('success'))



@app.route('/used_goods_trade')
def used_goods_trade():
    global user_name
    global need_id
    global user_id_use
    db = pymysql.connect(
      host='127.0.0.1',
      port=3306,
      user='root',
      passwd=os.environ.get('DB_PASSWORD', ''),
      db='test',
      charset='utf8'
        )
    # 创建游标
    cur = db.cursor()
  
    sql = 'SELECT user.name,need.name,need.content,need.price,need.need_id FROM need,user where user.user_id=need.user_id'
    cur.execute(sql)
    results = cur.fetchall()
    print(results)
    data_list = []
    for row in results:
        item = {
            'name':row[0],
            'product_name': row[1],
            'content': row[2],
            'price': row[3],
            'need_id':row[4]
        }
        data_list.append(item)
    print(data_list)
    print(user_id_use)
    sql = 'SELECT name,content,picture,good_id FROM good '
    cur.execute(sql)
    results = cur.fetchall()
    print(results)
    store_list = []
    i=1
    for row in results:
        item = {
            'product_name': row[0],
            'content': row[1],
            'good_id': row[3]
        }
        
        filepath =  'C:\\Users\\86134\\Desktop\\sdu\\sdu-database-experiment-three-main\\static\\images\\' + str(i) + '.png'
        print(filepath)
        store_list.append(item)
        i = i + 1
        fout = open(filepath, 'wb')
        fout.write(row[2])
        fout.close()
    print(store_list)
    
    sql='select address.name from user,address where user_id=%s and user.address_id=address.address_id'
    cur.execute(sql,user_id_use)
    result=cur.fetchall()
    address_name=None
    for row in result:
        address_name=row[0]
    


    sql = 'SELECT u1.name,u2.name,pruduct_name,price from record join user u1 on u1.user_id=record.user_id1 join user u2 on u2.user_id=record.user_id2 '
    cur.execute(sql)
    results = cur.fetchall()
    record_list = []
    for row in results:
        item = {
           'name1': row[0],
           'name2': row[1],
           'product_name': row[2],
           'price': row[3]
          }
        record_list.append(item)
    print(record_list)

    sql = 'select u.name ,c.content from user u join comment2 c on c.user_id=u.user_id join need n on n.need_id=c.need_id and n.user_id=%s'
    cur.execute(sql,(user_id_use))
    results = cur.fetchall()
    replay_list = []
    for row in results:
        item = {
           'name': row[0],
           'content':row[1]
          }
        replay_list.append(item)
    print(replay_list)
    sex='未知'
    signature='希望世界和平'
    sql='select sex,signature from user where user_id=%s'
    cur.execute(sql,(user_id_use))
    result=cur.fetchall()
    for row in result:
        sex=row[0]
        signature=row[1]

    if sex==None:
        sex='未知'
    if signature==None:
        signature='希望世界和平'
    
    user_info_ = {
    'username': user_name,
    'sex':sex,
    'signature':signature,
    'data_list': data_list,
    'store_list': store_list,
    'record_list':record_list,
    'replay_list':replay_list,
    'address_name':address_name
    }

    return render_template('used_goods_trade.html',user_information = user_info_)

@app.route('/map')
def map():
  global user_id_use
  db = pymysql.connect(
   host='127.0.0.1',
   port=3306,
   user='root',
   passwd=os.environ.get('DB_PASSWORD', ''),
   db='test',
   charset='utf8'
    )
  sql = 'select picture from user where user_id=%s'
  cur = db.cursor()
  cur.execute(sql, user_id_use)
  results = cur.fetchall()
  filepath =  'C:\\Users\\86134\\Desktop\\sdu\\sdu-database-experiment-three-main\\static\\images\\1.png' 
  ##print(filepath)
  for row in results:
    fout = open(filepath, 'wb')
    fout.write(row[0])
    fout.close()
  return render_template('map.html')



#给地址点赞
# 路由和视图函数
@app.route('/give_like_to_address', methods=['GET'])
def give_like_to_address():
    global user_id_use
    global address_id 
    db = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    user='root',
                    passwd=os.environ.get('DB_PASSWORD', ''),
                    db='test',
                    charset='utf8'
                )
    cur=db.cursor()
    sql='select user_id,address_id from star where user_id=%s and address_id=%s'
    cur.execute(sql,(user_id_use,address_id))
    if cur.fetchone() !=None:
        print(0)
        return render_template('warning_not_repeat_give_star.html')
       
    else:
        sql='insert into star values(%s,%s)'
        cur.execute(sql,(user_id_use,address_id))
        db.commit()
        sql='update address set star=star+1 where address_id=%s'
        cur.execute(sql,(address_id))
        db.commit()
        return render_template('give_star_success.html')
    
@app.route('/give_like_to_good', methods=['GET'])
def give_like_to_good():
    global user_id_use
    global g_good_id 
    global is_add
    if not is_add:
        db = pymysql.connect(
                        host='127.0.0.1',
                        port=3306,
                        user='root',
                        passwd=os.environ.get('DB_PASSWORD', ''),
                        db='test',
                        charset='utf8'
                    )
        cur=db.cursor()
        sql='update good set star=star+1 where good_id=%s'
        cur.execute(sql,(g_good_id))
        db.commit()
        is_add = 1
        return render_template('give_star_success.html')
    else:
        return render_template('warning_not_repeat_give_star.html')

@app.route('/get_likes_good', methods=['GET'])
def get_likes_good():
    global g_good_id
    global is_add
    # 假设这是从数据库或其他地方获取的点赞数
    db = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    user='root',
                    passwd=os.environ.get('DB_PASSWORD', ''),
                    db='test',
                    charset='utf8'
                )
    cur=db.cursor()
    sql='select star from good where good_id=%s'
    cur.execute(sql,g_good_id)
    likes_count = cur.fetchone()[0]  # 示例点赞数
    return jsonify({'likes': likes_count})

#获取点赞数
@app.route('/get_likes', methods=['GET'])
def get_likes():
    global address_id
    # 假设这是从数据库或其他地方获取的点赞数
    db = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    user='root',
                    passwd=os.environ.get('DB_PASSWORD', ''),
                    db='test',
                    charset='utf8'
                )
    cur=db.cursor()
    sql='select star from address where address_id=%s'
    cur.execute(sql,address_id)
    likes_count = cur.fetchone()[0]  # 示例点赞数
    return jsonify({'likes': likes_count})


@app.route('/upload_location', methods=['POST'])
def upload_location():
 
    location = request.form['location']
    print(location)
     # 连接数据库
    db = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    user='root',
                    passwd=os.environ.get('DB_PASSWORD', ''),
                    db='test',
                    charset='utf8'
                )
    cur=db.cursor()
    sql='select address_id from address where name=%s'
    cur.execute(sql,location)
    result=cur.fetchall()
    address_id=0
    for row in result:
        address_id=row[0]
    sql='update user set address_id=%s where user_id=%s'
    cur.execute(sql,(address_id,user_id_use))
    db.commit()
    # 这里添加你的逻辑，比如保存数据到数据库
    # 例如：save_signature_to_database(signature, location)
    
    # 假设保存成功，返回一个成功页面或消息
    return f'地区：{location} 已提交成功！'

@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    # 获取表单数据
    global address_id 
    global user_id_use
    print(address_id)
    comment = request.form.get('comment')
    input_code = request.form.get('inputCode')
    print(comment)
    print(input_code)
    db = pymysql.connect(
      host='127.0.0.1',
      port=3306,
      user='root',
      passwd=os.environ.get('DB_PASSWORD', ''),
      db='test',
      charset='utf8'
        )
    # 创建游标
    cur = db.cursor()
    sql='select max(comment_id) from comment1'
    cur.execute(sql)
    max_comment_id=cur.fetchone()[0]

    sql='insert into comment1 values(%s,%s,%s,%s)'
    cur.execute(sql,(user_id_use,address_id,max_comment_id+1,comment))
    db.commit()


    return render_template('deal.html')

@app.route('/submit_comment3', methods=['POST'])
def submit_comment3():
    # 获取表单数据
    global address_id 
    global user_id_use
    global g_good_id
    #print(address_id)
    comment = request.form.get('comment')
    input_code = request.form.get('inputCode')
    print(comment)
    print(input_code)
    db = pymysql.connect(
      host='127.0.0.1',
      port=3306,
      user='root',
      passwd=os.environ.get('DB_PASSWORD', ''),
      db='test',
      charset='utf8'
        )
    # 创建游标
    cur = db.cursor()
    sql='select max(comment_id) from comment3'
    cur.execute(sql)
    max_comment_id=cur.fetchone()[0]
    if max_comment_id==None:
        max_comment_id=0
    sql='insert into comment3 values(%s,%s,%s,%s)'
    cur.execute(sql,(user_id_use,g_good_id,max_comment_id+1,comment))
    db.commit()


    return render_template('deal.html')

@app.route('/personal_page')
def personal_page():
    global user_name
    global need_id
    global user_id_use
    db = pymysql.connect(
      host='127.0.0.1',
      port=3306,
      user='root',
      passwd=os.environ.get('DB_PASSWORD', ''),
      db='test',
      charset='utf8'
        )
    # 创建游标
    cur = db.cursor()
  
    sql = 'SELECT name,content,price FROM need WHERE user_id = %s'
    cur.execute(sql,user_id_use)
    results = cur.fetchall()
    print(results)
    data_list = []
    for row in results:
        item = {
            'product_name': row[0],
            'content': row[1],
            'price': row[2]
        }
        data_list.append(item)
    print(data_list)
    print(user_id_use)
    sql = 'SELECT name,content,picture,good_id FROM good WHERE user_id = %s'
    cur.execute(sql,user_id_use)
    results = cur.fetchall()
    print(results)
    store_list = []
    i=1
    for row in results:
        item = {
            'product_name': row[0],
            'content': row[1],
            'good_id': row[3]
        }
        filepath =  'C:\\Users\\86134\\Desktop\\sdu\\sdu-database-experiment-three-main\\static\\images\\' + str(i) + '.png'
        print(filepath)
        store_list.append(item)
        i = i + 1
        fout = open(filepath, 'wb')
        fout.write(row[2])
        fout.close()
    print(store_list)
    
    sql='select address.name from user,address where user_id=%s and user.address_id=address.address_id'
    cur.execute(sql,user_id_use)
    result=cur.fetchall()
    address_name=None
    for row in result:
        address_name=row[0]
    


    sql = 'SELECT u1.name,u2.name,pruduct_name,price from record join user u1 on u1.user_id=record.user_id1 join user u2 on u2.user_id=record.user_id2 where record.user_id1=%s or record.user_id2=%s'
    cur.execute(sql,(user_id_use,user_id_use))
    results = cur.fetchall()
    record_list = []
    for row in results:
        item = {
           'name1': row[0],
           'name2': row[1],
           'product_name': row[2],
           'price': row[3]
          }
        record_list.append(item)
    print(record_list)

    sql = 'select u.name ,c.content from user u join comment2 c on c.user_id=u.user_id join need n on n.need_id=c.need_id and n.user_id=%s'
    cur.execute(sql,(user_id_use))
    results = cur.fetchall()
    replay_list = []
    for row in results:
        item = {
           'name': row[0],
           'content':row[1]
          }
        replay_list.append(item)
    print(replay_list)
    sex='未知'
    signature='希望世界和平'
    sql='select sex,signature from user where user_id=%s'
    cur.execute(sql,(user_id_use))
    result=cur.fetchall()
    for row in result:
        sex=row[0]
        signature=row[1]

    if sex==None:
        sex='未知'
    if signature==None:
        signature='希望世界和平'
    
    user_info_ = {
    'username': user_name,
    'sex':sex,
    'signature':signature,
    'data_list': data_list,
    'store_list': store_list,
    'record_list':record_list,
    'replay_list':replay_list,
    'address_name':address_name
    }



    return render_template('personal_page.html',user_information = user_info_)
    

@app.route('/cancel/<int:good_id>', methods=['GET'])
def cancel(good_id):
    db = pymysql.connect(
      host='127.0.0.1',
      port=3306,
      user='root',
      passwd=os.environ.get('DB_PASSWORD', ''),
      db='test',
      charset='utf8'
        )
    # 创建游标
    cur = db.cursor()
  
    sql = 'DELETE FROM good WHERE good_id = %s'
    cur.execute(sql,good_id)
    db.commit()
    return render_template('cancel.html')


@app.route('/picview/<int:good_id>', methods=['GET'])
def picview(good_id):
    global address_id
    global g_good_id
    g_good_id = good_id
    db = pymysql.connect(
      host='127.0.0.1',
      port=3306,
      user='root',
      passwd=os.environ.get('DB_PASSWORD', ''),
      db='test',
      charset='utf8'
        )
    # 创建游标
    cur = db.cursor()
    sql = 'select picture,name,content,price FROM good WHERE good_id = %s'
    cur.execute(sql,good_id)
    results = cur.fetchall()
    filepath =  'C:\\Users\\86134\\Desktop\\sdu\\sdu-database-experiment-three-main\\static\\images\\side1.jpg'
    ##print(filepath)
    for row in results:
        fout = open(filepath, 'wb')
        fout.write(row[0])
        fout.close()
        show_good_name=row[1]
        show_good_price=row[3]
        show_good_content=row[2]

    

    sql='select user.name,user.picture,comment3.content from comment3 join user on user.user_id = comment3.user_id where good_id=%s'
    cur.execute(sql,good_id)
    results=cur.fetchall()
    #print(name)
    #print(results)
    comment_list = []
    #i = 1
    for row in results:
        #filepath =  'D:\\30726\\Desktop\\数据库实验三\\sdu-database-experiment-three-main\\static\\images\\' + str(i) + '.png'
        #i = i + 1
        if isinstance(row[1], bytes):
        # 将二进制数据转换为Base64编码的字符串
            image_data = base64.b64encode(row[1]).decode('utf-8')
        else:
            image_data = row[1]
        items = {
            'name':row[0],
            'text':row[2],
            'image':image_data
             }
        comment_list.append(items)



    ##print(comment_list)


    sql = 'select name,price,content from good order by good_id DESC limit 5'
    cur.execute(sql)
    results = cur.fetchall()
    store_list = []
    for row in results:
        # 尝试将字符串格式的价格转换为浮点数
        try:
            price = float(row[1])  # row[1] 是价格的字符串表示
        except ValueError:
            # 如果转换失败（例如，字符串为空或不是数字），则设置默认价格为0.0
            price = 0.0
        
        # 使用str.format()方法拼接字符串
        items = {
            'text': "{}, {:.2f}元, {}".format(row[0], price, row[2])
        }
        #print(items)
        store_list.append(items)


    sql = 'select name,price,content from need order by need_id DESC limit 5'
    cur.execute(sql)
    results = cur.fetchall()
    need_list = []
    for row in results:
        # 尝试将字符串格式的价格转换为浮点数
        try:
            price = float(row[1])  # row[1] 是价格的字符串表示
        except ValueError:
            # 如果转换失败（例如，字符串为空或不是数字），则设置默认价格为0.0
            price = 0.0
        
        # 使用str.format()方法拼接字符串
        items = {
            'text': "{}, {:.2f}元, {}".format(row[0], price, row[2])
        }
        #print(items)
        need_list.append(items)

    sql = 'select pruduct_name,price from record limit 5'
    cur.execute(sql)
    results = cur.fetchall()
    record_list = []
    for row in results:
        # 尝试将字符串格式的价格转换为浮点数
        try:
            price = float(row[1])  # row[1] 是价格的字符串表示
        except ValueError:
            # 如果转换失败（例如，字符串为空或不是数字），则设置默认价格为0.0
            price = 0.0
        
        # 使用str.format()方法拼接字符串
        items = {
            'text': "{}, {:.2f}元".format(row[0], price)
        }
        #print(items)
        record_list.append(items)
    
    sql = 'select count(*) from good'
    cur.execute(sql)
    results = cur.fetchone()
    good_count = results[0]
    sql = 'select count(*) from need'
    cur.execute(sql)
    results = cur.fetchone()
    need_count = results[0]
    sql = 'select count(*) from user'
    cur.execute(sql)
    results = cur.fetchone()
    user_count = results[0]
    sql = 'select count(*) from comment1'
    cur.execute(sql)
    results = cur.fetchone()
    comment1_count = results[0]
    sql = 'select count(*) from comment2'
    cur.execute(sql)
    results = cur.fetchone()
    comment2_count = results[0]
    sql = 'select count(*) from comment3'
    cur.execute(sql)
    results = cur.fetchone()
    comment3_count = results[0]
    comment_count = comment1_count + comment2_count + comment3_count
    num_list = {
        'good_count':good_count,
        'need_count':need_count,
        'user_count':user_count,
        'comment_count':comment_count
    }
    talk_information_ = {
        'store_list': store_list,
        'need_list': need_list,
        'record_list': record_list,
        'comment_list': comment_list,
        'num_list':num_list,
        'show_good_name':show_good_name,
        'show_good_content':show_good_content,
        'show_good_price':show_good_price
    }

    return render_template('picview.html',talk_information = talk_information_)

@app.route('/comment2/<int:good_id>', methods=['GET'])
def comment2(good_id):
    comment_content = request.args.get('comment', default='', type=str)
    print(good_id)#需求的id
    print(comment_content)#回复的内容
    db = pymysql.connect(
      host='127.0.0.1',
      port=3306,
      user='root',
      passwd=os.environ.get('DB_PASSWORD', ''),
      db='test',
      charset='utf8'
        )
    # 创建游标
    cur = db.cursor()
    sql='select max(comment_id) from comment2 '
    cur.execute(sql)
    max_comment_id=cur.fetchone()[0]
    if max_comment_id==None:
        max_comment_id=1
    else:
        max_comment_id=max_comment_id+1
    sql='insert into comment2 values(%s,%s,%s,%s)'
    cur.execute(sql,(user_id_use,good_id,max_comment_id,comment_content))
    db.commit()
    return render_template('comment2.html')


@app.route('/deal')
def deal():
    return render_template('deal.html')

@app.route('/deal_success')
def deal_success():
    global user_id_use
    global g_good_id
    db = pymysql.connect(
      host='127.0.0.1',
      port=3306,
      user='root',
      passwd=os.environ.get('DB_PASSWORD', ''),
      db='test',
      charset='utf8'
        )
    # 创建游标
    cur = db.cursor()
    sql='select user_id,price,name from good where good_id=%s'
    cur.execute(sql,g_good_id)
    result=cur.fetchone()
    user_id2=result[0]
    price=result[1]
    good_name=result[2]
    if(user_id2==user_id_use):
        return render_template('deal_fail.html')
    sql='insert into record values(%s,%s,%s,%s)'
    cur.execute(sql,(user_id_use,user_id2,good_name,price))
    db.commit()
    sql='delete from good where good_id =%s'
    cur.execute(sql,g_good_id)
    db.commit()
    return render_template('deal.html')


#talk页面显示
@app.route('/talk')
def talk():
    global address_id
    name = request.args.get('name')  # 从查询参数中获取 name
    db = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    user='root',
                    passwd=os.environ.get('DB_PASSWORD', ''),
                    db='test',
                    charset='utf8'
                )
    cur=db.cursor()
    sql='select address_id from address where name=%s'
    cur.execute(sql,name)
    results = cur.fetchone()
    address_id = None
    if results is not None:
        address_id=results[0]
    else:
        address_id = None
    print(address_id)
    sql='select user.name,user.picture,comment1.content from comment1 join address on comment1.address_id = address.address_id join user on user.user_id = comment1.user_id where address.name=%s'
    cur.execute(sql,name)
    results=cur.fetchall()
    #print(name)
    #print(results)
    comment_list = []
    #i = 1
    for row in results:
        #filepath =  'D:\\30726\\Desktop\\数据库实验三\\sdu-database-experiment-three-main\\static\\images\\' + str(i) + '.png'
        #i = i + 1
        if isinstance(row[1], bytes):
        # 将二进制数据转换为Base64编码的字符串
            image_data = base64.b64encode(row[1]).decode('utf-8')
        else:
            image_data = row[1]
        items = {
            'name':row[0],
            'text':row[2],
            'image':image_data
             }
        comment_list.append(items)
    ##print(comment_list)


    sql = 'select name,price,content from good order by good_id DESC limit 5'
    cur.execute(sql)
    results = cur.fetchall()
    store_list = []
    for row in results:
        # 尝试将字符串格式的价格转换为浮点数
        try:
            price = float(row[1])  # row[1] 是价格的字符串表示
        except ValueError:
            # 如果转换失败（例如，字符串为空或不是数字），则设置默认价格为0.0
            price = 0.0
        
        # 使用str.format()方法拼接字符串
        items = {
            'text': "{}, {:.2f}元, {}".format(row[0], price, row[2])
        }
        #print(items)
        store_list.append(items)


    sql = 'select name,price,content from need order by need_id DESC limit 5'
    cur.execute(sql)
    results = cur.fetchall()
    need_list = []
    for row in results:
        # 尝试将字符串格式的价格转换为浮点数
        try:
            price = float(row[1])  # row[1] 是价格的字符串表示
        except ValueError:
            # 如果转换失败（例如，字符串为空或不是数字），则设置默认价格为0.0
            price = 0.0
        
        # 使用str.format()方法拼接字符串
        items = {
            'text': "{}, {:.2f}元, {}".format(row[0], price, row[2])
        }
        #print(items)
        need_list.append(items)

    sql = 'select pruduct_name,price from record limit 5'
    cur.execute(sql)
    results = cur.fetchall()
    record_list = []
    for row in results:
        # 尝试将字符串格式的价格转换为浮点数
        try:
            price = float(row[1])  # row[1] 是价格的字符串表示
        except ValueError:
            # 如果转换失败（例如，字符串为空或不是数字），则设置默认价格为0.0
            price = 0.0
        
        # 使用str.format()方法拼接字符串
        items = {
            'text': "{}, {:.2f}元".format(row[0], price)
        }
        #print(items)
        record_list.append(items)
    

    sql = 'select count(*) from good'
    cur.execute(sql)
    results = cur.fetchone()
    good_count = results[0]
    sql = 'select count(*) from need'
    cur.execute(sql)
    results = cur.fetchone()
    need_count = results[0]
    sql = 'select count(*) from user'
    cur.execute(sql)
    results = cur.fetchone()
    user_count = results[0]
    sql = 'select count(*) from comment1'
    cur.execute(sql)
    results = cur.fetchone()
    comment1_count = results[0]
    sql = 'select count(*) from comment2'
    cur.execute(sql)
    results = cur.fetchone()
    comment2_count = results[0]
    sql = 'select count(*) from comment3'
    cur.execute(sql)
    results = cur.fetchone()
    comment3_count = results[0]
    comment_count = comment1_count + comment2_count + comment3_count
    num_list = {
        'good_count':good_count,
        'need_count':need_count,
        'user_count':user_count,
        'comment_count':comment_count
    }
    talk_information_ = {
        'address_name':name,
        'comment_list': comment_list,
        'store_list': store_list,
        'need_list': need_list,
        'record_list': record_list,
        'num_list':num_list
    }
    return render_template('talk.html',talk_information = talk_information_)



@app.route('/sendmessage',methods=['POST','GET'])
def search_store():
    global user_id_use
    global need_id
    productName = request.form.get('productName')
    estimatedPrice = request.form.get('estimatedPrice')
    description = request.form.get('description')
    #从数据库中搜索信息
    info = '待查询'
    try:
    ##连接数据库
        db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            passwd=os.environ.get('DB_PASSWORD', ''),
            db='test',
            charset='utf8'
        )

        need_id = need_id + 1
        cur = db.cursor()
        sql = 'INSERT INTO need values (%s,%s,%s,%s,%s)'
        value = (user_id_use,need_id,productName,description,estimatedPrice)
        cur.execute(sql, value)
        db.commit()
        print("数据插入成功")

    except pymysql.Error as e:
        print('connect error' + str(e))

    # 传递到前端并渲染
    return render_template('sendmessage.html')
    ##插入数据到表


if __name__ == '__main__':
# run的参数 debug的优点： 1： 修改自动重启 2：定位bug
    app.run(host='0.0.0.0', port=8000, debug=True)