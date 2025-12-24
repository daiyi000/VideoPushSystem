from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import func
from flasgger import swag_from
from ..models import User, Video, ActionLog, db, Comment, Danmaku, playlist_video, PasswordResetRequest
from .. import mail
from flask_mail import Message
import jwt
import datetime
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/reset_requests', methods=['GET'])
def get_reset_requests():
    reqs = PasswordResetRequest.query.order_by(PasswordResetRequest.created_at.desc()).all()
    return jsonify({'code': 200, 'data': [r.to_dict() for r in reqs]})

@admin_bp.route('/send_reset_email', methods=['POST'])
def send_reset_email():
    data = request.get_json()
    req_id = data.get('id')
    
    req = PasswordResetRequest.query.get(req_id)
    if not req:
        return jsonify({'code': 404, 'msg': '请求不存在'}), 404
        
    user = User.query.get(req.user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404

    # 生成 1 小时有效的 Token
    payload = {
        'reset_user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    # 构造链接
    domain = os.getenv('SITE_DOMAIN', 'http://localhost:5173') # 前端地址
    reset_link = f"{domain}/reset-password?token={token}"
    
    try:
        msg = Message("VideoHub 密码重置", recipients=[req.email])
        msg.body = f"亲爱的 {user.username}：\n\n管理员已批准您的重置请求。请点击以下链接重置密码：\n{reset_link}\n\n该链接1小时内有效。"
        mail.send(msg)
        
        req.status = 'sent'
        db.session.commit()
        return jsonify({'code': 200, 'msg': '邮件已发送'})
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'msg': '邮件发送失败'}), 500

@admin_bp.route('/stats', methods=['GET'])
@swag_from('../docs/admin/stats.yml') # <--- 修改
def get_stats():
    total_users = User.query.count()
    total_videos = Video.query.count()
    pending_videos = Video.query.filter_by(status=0).count()
    
    daily_users = db.session.query(
        func.date(User.created_at).label('date'), 
        func.count(User.id)
    ).group_by('date').order_by('date').limit(7).all()
    
    chart_users = {
        'dates': [str(r[0]) for r in daily_users],
        'counts': [r[1] for r in daily_users]
    }
    
    category_stats = db.session.query(
        Video.category, func.count(Video.id)
    ).group_by(Video.category).all()
    
    chart_category = [{'name': r[0], 'value': r[1]} for r in category_stats]
    
    top_videos = Video.query.order_by(Video.views.desc()).limit(10).all()
    chart_top10 = {
        'titles': [v.title[:10] + '...' for v in top_videos], 
        'views': [v.views for v in top_videos]
    }

    return jsonify({
        'code': 200,
        'data': {
            'total_users': total_users,
            'total_videos': total_videos,
            'pending_videos': pending_videos,
            'chart_users': chart_users,
            'chart_category': chart_category,
            'chart_top10': chart_top10
        }
    })

@admin_bp.route('/videos', methods=['GET'])
@swag_from('../docs/admin/videos.yml') # <--- 修改
def get_admin_videos():
    status = request.args.get('status')
    q = request.args.get('q')
    
    query = Video.query
    if status is not None and status != '':
        query = query.filter_by(status=int(status))
    if q:
        query = query.filter(Video.title.like(f'%{q}%'))
        
    videos = query.order_by(Video.upload_time.desc()).all()
    return jsonify({'code': 200, 'data': [v.to_dict() for v in videos]})

@admin_bp.route('/video/audit', methods=['POST'])
@swag_from('../docs/admin/audit_video.yml') # <--- 修改
def audit_video():
    data = request.get_json()
    video_id = data.get('id')
    new_status = data.get('status') 
    
    video = Video.query.get(video_id)
    if not video: return jsonify({'code': 404, 'msg': '视频不存在'})
    
    video.status = new_status
    db.session.commit()
    return jsonify({'code': 200, 'msg': '操作成功'})

@admin_bp.route('/video/delete', methods=['POST'])
@swag_from('../docs/admin/delete_video.yml') # <--- 修改
def delete_video_admin():
    data = request.get_json()
    video_id = data.get('id')
    
    video = Video.query.get(video_id)
    if video:
        try:
            db.session.execute(playlist_video.delete().where(playlist_video.c.video_id == video_id))
            Danmaku.query.filter_by(video_id=video_id).delete()
            Comment.query.filter_by(video_id=video_id).delete()
            ActionLog.query.filter_by(video_id=video_id).delete()
            db.session.delete(video)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '删除成功'})
        except Exception as e:
            db.session.rollback()
            print(f"删除失败: {e}")
            return jsonify({'code': 500, 'msg': '删除失败，数据库错误'})
            
    return jsonify({'code': 404, 'msg': '视频不存在'})

@admin_bp.route('/users', methods=['GET'])
@swag_from('../docs/admin/users.yml') # <--- 修改
def get_admin_users():
    q = request.args.get('q')
    query = User.query
    if q:
        query = query.filter(User.username.like(f'%{q}%') | User.email.like(f'%{q}%'))
    
    users = query.all()
    return jsonify({'code': 200, 'data': [u.to_dict() for u in users]})

@admin_bp.route('/user/ban', methods=['POST'])
@swag_from('../docs/admin/ban_user.yml') # <--- 修改
def ban_user():
    data = request.get_json()
    user = User.query.get(data.get('id'))
    if not user: return jsonify({'code': 404, 'msg': '用户不存在'})
    
    user.is_banned = not user.is_banned
    db.session.commit()
    
    msg = '已封禁' if user.is_banned else '已解封'
    return jsonify({'code': 200, 'msg': msg})