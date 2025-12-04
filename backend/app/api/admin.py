from flask import Blueprint, jsonify, request
from sqlalchemy import func
from datetime import datetime, timedelta
from ..models import User, Video, ActionLog, db

admin_bp = Blueprint('admin', __name__)

# 1. 仪表盘数据统计 (Dashboard Stats)
@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    # A. 基础计数
    total_users = User.query.count()
    total_videos = Video.query.count()
    pending_videos = Video.query.filter_by(status=0).count()
    
    # B. 每日新增用户 (最近7天)
    # MySQL 使用 func.date(), SQLite 使用 func.date() 或 strftime
    # 这里假设使用 MySQL
    daily_users = db.session.query(
        func.date(User.created_at).label('date'), 
        func.count(User.id)
    ).group_by('date').order_by('date').limit(7).all()
    
    chart_users = {
        'dates': [str(r[0]) for r in daily_users],
        'counts': [r[1] for r in daily_users]
    }
    
    # C. 视频分类占比
    category_stats = db.session.query(
        Video.category, func.count(Video.id)
    ).group_by(Video.category).all()
    
    chart_category = [{'name': r[0], 'value': r[1]} for r in category_stats]
    
    # D. 热门视频 Top 10
    top_videos = Video.query.order_by(Video.views.desc()).limit(10).all()
    chart_top10 = {
        'titles': [v.title[:10] + '...' for v in top_videos], # 截断标题
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

# 2. 视频管理 (列表 + 搜索 + 筛选)
@admin_bp.route('/videos', methods=['GET'])
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

# 3. 视频审核/操作 (通过、驳回/下架、修改)
@admin_bp.route('/video/audit', methods=['POST'])
def audit_video():
    data = request.get_json()
    video_id = data.get('id')
    new_status = data.get('status') # 1=通过, 2=下架
    
    video = Video.query.get(video_id)
    if not video: return jsonify({'code': 404, 'msg': '视频不存在'})
    
    video.status = new_status
    db.session.commit()
    return jsonify({'code': 200, 'msg': '操作成功'})

@admin_bp.route('/video/delete', methods=['POST'])
def delete_video_admin():
    data = request.get_json()
    video = Video.query.get(data.get('id'))
    if video:
        db.session.delete(video)
        db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})

# 4. 用户管理 (列表 + 封禁)
@admin_bp.route('/users', methods=['GET'])
def get_admin_users():
    q = request.args.get('q')
    query = User.query
    if q:
        query = query.filter(User.username.like(f'%{q}%') | User.email.like(f'%{q}%'))
    
    users = query.all()
    return jsonify({'code': 200, 'data': [u.to_dict() for u in users]})

@admin_bp.route('/user/ban', methods=['POST'])
def ban_user():
    data = request.get_json()
    user = User.query.get(data.get('id'))
    if not user: return jsonify({'code': 404, 'msg': '用户不存在'})
    
    # 切换封禁状态
    user.is_banned = not user.is_banned
    db.session.commit()
    
    msg = '已封禁' if user.is_banned else '已解封'
    return jsonify({'code': 200, 'msg': msg})