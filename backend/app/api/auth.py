import jwt
import datetime
import random
from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from flasgger import swag_from # 引入 swag_from 装饰器
from .. import mail 
from ..models import User, EmailCaptcha, PasswordResetRequest, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'code': 400, 'msg': '邮箱不能为空'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        # 为了安全，即使邮箱不存在也提示发送成功，防止枚举，或者明确提示不存在
        # 这里为了演示方便，提示不存在
        return jsonify({'code': 404, 'msg': '该邮箱未注册'}), 404
    
    # 创建重置请求
    # 检查是否已有待处理的请求
    existing = PasswordResetRequest.query.filter_by(user_id=user.id, status='pending').first()
    if not existing:
        req = PasswordResetRequest(user_id=user.id, email=email)
        db.session.add(req)
        db.session.commit()
    
    return jsonify({'code': 200, 'msg': '请求已提交，请联系管理员或等待邮件'})

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')
    
    if not token or not new_password:
        return jsonify({'code': 400, 'msg': '参数缺失'}), 400
        
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload.get('reset_user_id') # 专门的 reset payload key
        if not user_id:
             return jsonify({'code': 400, 'msg': '无效的令牌'}), 400
             
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'msg': '用户不存在'}), 404
            
        user.set_password(new_password)
        
        # 将请求标记为完成
        reqs = PasswordResetRequest.query.filter_by(user_id=user.id, status='sent').all()
        for r in reqs:
            r.status = 'completed'
            
        db.session.commit()
        return jsonify({'code': 200, 'msg': '密码重置成功，请重新登录'})
        
    except jwt.ExpiredSignatureError:
        return jsonify({'code': 400, 'msg': '链接已过期'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'code': 400, 'msg': '无效的链接'}), 400

@auth_bp.route('/send_code', methods=['POST'])
@swag_from('../docs/auth/send_code.yml')
def send_code():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'code': 400, 'msg': '邮箱不能为空'}), 400
        
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

@auth_bp.route('/register', methods=['POST'])
@swag_from('../docs/auth/register.yml')
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

@auth_bp.route('/login', methods=['POST'])
@swag_from('../docs/auth/login.yml')
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
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