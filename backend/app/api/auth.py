import jwt
import datetime
import random
from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from .. import mail 
from ..models import User, EmailCaptcha, db

auth_bp = Blueprint('auth', __name__)

# 1. 发送验证码接口
@auth_bp.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'code': 400, 'msg': '邮箱不能为空'}), 400
        
    # 生成 6 位随机验证码
    code = str(random.randint(100000, 999999))
    
    try:
        msg = Message("VideoHub 注册验证码", recipients=[email])
        msg.body = f"您的注册验证码是：{code}，请在 5 分钟内完成注册。"
        mail.send(msg)
        
        captcha = EmailCaptcha(email=email, code=code)
        db.session.add(captcha)
        db.session.commit()
        
        return jsonify({'code': 200, 'msg': '验证码已发送'})
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'msg': '邮件发送失败，请检查邮箱地址或联系管理员'}), 500

# 2. 注册接口
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    code = data.get('code')
    
    if not email or not password or not code:
        return jsonify({'code': 400, 'msg': '信息不全'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'msg': '该邮箱已注册'}), 400
        
    captcha = EmailCaptcha.query.filter_by(email=email).order_by(EmailCaptcha.created_at.desc()).first()
    if not captcha or captcha.code != code:
        return jsonify({'code': 400, 'msg': '验证码错误'}), 400
        
    if (datetime.datetime.utcnow() - captcha.created_at).total_seconds() > 300:
        return jsonify({'code': 400, 'msg': '验证码已过期'}), 400
        
    username = email.split('@')[0]
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '注册成功'})

# 3. 登录接口 (已修复封禁逻辑)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        # 【核心修复】检查是否被封禁
        if user.is_banned:
            return jsonify({'code': 403, 'msg': '该账号已被封禁，请联系管理员申诉'}), 403

        payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'code': 200, 
            'msg': '登录成功',
            'data': {
                'token': token,
                'user': user.to_dict()
            }
        })
        
    return jsonify({'code': 401, 'msg': '邮箱或密码错误'}), 401