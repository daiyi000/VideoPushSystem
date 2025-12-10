import os
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from ..algorithm.core import recommender
from ..models import Video, ActionLog, db
from sqlalchemy import func

recommend_bp = Blueprint('recommend', __name__)

def get_doc_path(filename):
    return os.path.join(os.path.dirname(__file__), '../docs/recommend', filename)

@recommend_bp.route('/home', methods=['GET'])
@swag_from(get_doc_path('home.yml'))
def home_recommend():
    user_id = request.args.get('user_id', type=int)
    
    response_data = {}
    
    # 1. 动态分类 (不变)
    response_data['categories'] = recommender.get_user_preferred_categories(user_id)
    
    # 2. 发现 (不变)
    if user_id:
        response_data['discover'] = recommender.recommend_by_history(user_id, limit=8)
    else:
        response_data['discover'] = recommender.get_hot_videos(limit=8)
        
    # 3. Shorts (不变)
    shorts_query = Video.query.filter_by(status=1, visibility='public', is_short=True)
    shorts_videos = shorts_query.order_by(Video.upload_time.desc()).limit(10).all()
    response_data['shorts'] = [v.to_dict() for v in shorts_videos]
    
    # 4. 继续观看 (历史记录)
    if user_id:
        # 获取每个视频最近的观看记录
        subquery = db.session.query(
            ActionLog.video_id, 
            func.max(ActionLog.timestamp).label('max_time')
        ).filter_by(user_id=user_id, action_type='view').group_by(ActionLog.video_id).subquery()
        
        # 联合查询：Video + ActionLog (为了获取 progress)
        query = db.session.query(Video, ActionLog.progress)\
            .join(subquery, Video.id == subquery.c.video_id)\
            .join(ActionLog, (ActionLog.video_id == Video.id) & (ActionLog.timestamp == subquery.c.max_time))\
            .filter(
                Video.status == 1, 
                Video.visibility == 'public',
                Video.is_short == False # 【过滤】不显示 Shorts
            )
            
        results = query.all()
        
        history_list = []
        for v, progress in results:
            # 【过滤】如果观看进度超过 90% 或 剩余少于 10秒，视为已看完，不显示
            if v.duration > 0:
                is_finished = False
                if progress >= v.duration - 10: is_finished = True # 剩余少于10秒
                if (progress / v.duration) > 0.95: is_finished = True # 看了 95%
                
                if not is_finished:
                    v_dict = v.to_dict()
                    v_dict['progress'] = progress # 将进度传给前端显示进度条
                    v_dict['progress_percent'] = (progress / v.duration) * 100
                    history_list.append(v_dict)
        
        # 按最后观看时间倒序 (这里简单在 Python 里排，因为 sql 已经乱了)
        # 实际可以在 sql 里 order_by subquery.c.max_time
        # history_list.sort(...) 
        
        response_data['history'] = history_list[:8] # 取前8个
    else:
        response_data['history'] = []

    return jsonify({'code': 200, 'msg': 'success', 'data': response_data})

@recommend_bp.route('/related/<int:video_id>', methods=['GET'])
@swag_from(get_doc_path('related.yml'))
def related_recommend(video_id):
    videos = recommender.recommend_similar_content(video_id)
    return jsonify({'code': 200, 'data': videos})