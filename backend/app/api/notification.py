from flask import Blueprint, request, jsonify
from ..models import Notification, NotificationSetting, User, db
from flasgger import swag_from
from datetime import datetime

notification_bp = Blueprint('notification', __name__)

def create_notification(user_id, sender_id, type, content, target_url=None):
    """
    内部辅助函数：创建通知，检查用户设置
    """
    if not user_id:
        return
        
    try:
        # 1. 截断内容防止溢出 (content 长度限制为 256)
        safe_content = (content[:250] + '...') if len(content) > 250 else content

        # 2. 检查���户设置
        setting = NotificationSetting.query.filter_by(user_id=user_id).first()
        if not setting:
            # 如果没有设置，默认允许所有通知
            should_notify = True
        else:
            should_notify = True
            if type == 'subscribe' and not setting.notify_subscription: should_notify = False
            elif type == 'recommend' and not setting.notify_recommendation: should_notify = False
            elif type == 'interaction' and not setting.notify_interaction: should_notify = False
            elif type == 'comment' and not setting.notify_comment: should_notify = False
            elif type == 'mention' and not setting.notify_mention: should_notify = False
            elif type == 'promotion' and not setting.notify_promotion: should_notify = False
            elif type == 'system' and not setting.notify_system: should_notify = False
        
        if should_notify:
            notif = Notification(
                user_id=user_id,
                sender_id=sender_id,
                type=type,
                content=safe_content,
                target_url=target_url
            )
            db.session.add(notif)
            # 注意：这里不再执行 db.session.commit()，交给外部路由函数统一 commit
            # 这样可以保证原子性，也能避免 session 冲突
    except Exception as e:
        print(f"Internal Notification Creation Error: {e}")

@notification_bp.route('/list', methods=['GET'])
def get_notifications():
    """
    获取用户通知列表
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'msg': 'User ID required'}), 400
        
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(50).all()
    
    data = []
    for n in notifs:
        sender_data = None
        if n.sender:
            sender_data = {
                'id': n.sender.id,
                'username': n.sender.username,
                'avatar': n.sender.avatar
            }
            
        data.append({
            'id': n.id,
            'type': n.type,
            'content': n.content,
            'target_url': n.target_url,
            'is_read': n.is_read,
            'time': n.created_at.strftime('%Y-%m-%d %H:%M'),
            'sender': sender_data
        })
        
    return jsonify({'code': 200, 'data': data})

@notification_bp.route('/read', methods=['POST'])
def mark_read():
    """
    标记通知为已读 (单条或全部)
    """
    data = request.get_json()
    notif_id = data.get('id')
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'code': 400, 'msg': 'User ID required'}), 400

    if notif_id == 'all':
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    else:
        notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
        if notif:
            notif.is_read = True
            
    db.session.commit()
    return jsonify({'code': 200, 'msg': 'Success'})

@notification_bp.route('/settings', methods=['GET'])
def get_settings():
    """
    获取通知设置
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'msg': 'User ID required'}), 400
        
    setting = NotificationSetting.query.filter_by(user_id=user_id).first()
    if not setting:
        setting = NotificationSetting(user_id=user_id)
        db.session.add(setting)
        db.session.commit()
        
    return jsonify({
        'code': 200,
        'data': {
            'notify_subscription': setting.notify_subscription,
            'notify_recommendation': setting.notify_recommendation,
            'notify_interaction': setting.notify_interaction,
            'notify_comment': setting.notify_comment,
            'notify_mention': setting.notify_mention,
            'notify_promotion': setting.notify_promotion,
            'notify_system': setting.notify_system
        }
    })

@notification_bp.route('/settings', methods=['POST'])
def update_settings():
    """
    更新通知设置
    """
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'code': 400, 'msg': 'User ID required'}), 400
        
    setting = NotificationSetting.query.filter_by(user_id=user_id).first()
    if not setting:
        setting = NotificationSetting(user_id=user_id)
        db.session.add(setting)
        
    # Update fields if present
    if 'notify_subscription' in data: setting.notify_subscription = data['notify_subscription']
    if 'notify_recommendation' in data: setting.notify_recommendation = data['notify_recommendation']
    if 'notify_interaction' in data: setting.notify_interaction = data['notify_interaction']
    if 'notify_comment' in data: setting.notify_comment = data['notify_comment']
    if 'notify_mention' in data: setting.notify_mention = data['notify_mention']
    if 'notify_promotion' in data: setting.notify_promotion = data['notify_promotion']
    if 'notify_system' in data: setting.notify_system = data['notify_system']
    
    db.session.commit()
    return jsonify({'code': 200, 'msg': 'Settings updated'})
