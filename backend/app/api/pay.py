from flask import Blueprint, request, jsonify, current_app
from alipay import AliPay
from ..models import db, User, Order
import uuid

pay_bp = Blueprint('pay', __name__)

def get_alipay_client():
    return AliPay(
        appid=current_app.config['ALIPAY_APPID'],
        app_notify_url=current_app.config['ALIPAY_NOTIFY_URL'],
        app_private_key_string=current_app.config['ALIPAY_PRIVATE_KEY_STRING'],
        alipay_public_key_string=current_app.config['ALIPAY_PUBLIC_KEY_STRING'],
        sign_type="RSA2",
        debug=current_app.config['ALIPAY_DEBUG']
    )

# 1. 创建订单
@pay_bp.route('/create', methods=['POST'])
def create_payment():
    data = request.get_json()
    user_id = data.get('user_id')
    ver_type = data.get('ver_type') # 1=普通, 2=音乐人
    
    amount = 0.01 if ver_type == 1 else 0.02 # 沙盒测试金额设小一点
    subject = "个人认证" if ver_type == 1 else "音乐人认证"
    
    # 存入数据库
    order_no = str(uuid.uuid4()).replace('-', '')
    order = Order(order_no=order_no, user_id=user_id, total_amount=amount, subject=subject, target_ver_type=ver_type)
    db.session.add(order)
    db.session.commit()
    
    # 生成跳转链接
    alipay = get_alipay_client()
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_no,
        total_amount=str(amount),
        subject=subject,
        return_url=current_app.config['ALIPAY_RETURN_URL']
    )
    
    # 拼接沙盒网关
    pay_url = f"https://openapi-sandbox.dl.alipaydev.com/gateway.do?{order_string}"
    return jsonify({'code': 200, 'pay_url': pay_url, 'order_no': order_no})

# 2. 异步通知回调 (支付宝调用此接口)
@pay_bp.route('/notify', methods=['POST'])
def alipay_notify():
    data = request.form.to_dict()
    signature = data.pop("sign")
    
    alipay = get_alipay_client()
    # 验证签名
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        order_no = data["out_trade_no"]
        order = Order.query.filter_by(order_no=order_no).first()
        
        if order and order.trade_status != 'TRADE_SUCCESS':
            order.trade_status = 'TRADE_SUCCESS'
            # 更新用户认证状态
            user = User.query.get(order.user_id)
            if user:
                user.verification_type = order.target_ver_type
            db.session.commit()
            print(f"订单 {order_no} 支付成功，用户权益已发放")
            
        return "success"
    return "failure"

# 3. 前端查询状态 (主动查单)
@pay_bp.route('/query', methods=['POST'])
def query_order():
    order_no = request.json.get('order_no')
    order = Order.query.filter_by(order_no=order_no).first()
    
    if not order:
        return jsonify({'code': 404, 'msg': '订单不存在'})

    # 1. 快速路径：如果本地已经是成功状态，直接返回
    if order.trade_status == 'TRADE_SUCCESS':
        return jsonify({'code': 200, 'status': 'success'})

    # 2. 慢速路径：如果本地显示没支付，去支付宝查一下到底付没付
    try:
        alipay = get_alipay_client()
        # 主动调用支付宝查询接口
        result = alipay.api_alipay_trade_query(out_trade_no=order_no)
        
        # 打印结果方便调试
        print(f"-------- 主动查单结果: {order_no} --------")
        print(result) 
        
        # 判断支付宝返回的状态
        # code='10000' 代表接口调用成功
        # trade_status='TRADE_SUCCESS' 代表用户已付款
        if result.get("code") == "10000" and result.get("trade_status") in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            
            # --- 补单逻辑：虽然回调没来，但我查到了，赶紧更新数据库 ---
            order.trade_status = 'TRADE_SUCCESS'
            
            user = User.query.get(order.user_id)
            if user:
                user.verification_type = order.target_ver_type
                
            db.session.commit()
            print("主动查单发现支付成功，已同步数据库")
            
            return jsonify({'code': 200, 'status': 'success'})
            
    except Exception as e:
        print(f"支付宝查单出错: {e}")

    # 3. 真的还没付，或者查单报错
    return jsonify({'code': 200, 'status': 'pending'})