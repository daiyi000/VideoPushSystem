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
    
    # 1. 动态分类
    response_data['categories'] = recommender.get_user_preferred_categories(user_id)
    
    # 2. 发现 (已在 core.py 过滤)
    if user_id:
        response_data['discover'] = recommender.recommend_by_history(user_id, limit=8)
    else:
        response_data['discover'] = recommender.get_hot_videos(limit=8)
        
    # 3. 最近上传 (【修复】增加过滤)
    recents = Video.query.filter_by(status=1, visibility='public').order_by(Video.upload_time.desc()).limit(8).all()
    response_data['recent'] = [v.to_dict() for v in recents]
    
    # 4. 继续观看
    if user_id:
        subquery = db.session.query(
            ActionLog.video_id, 
            func.max(ActionLog.timestamp).label('max_time')
        ).filter_by(user_id=user_id, action_type='view').group_by(ActionLog.video_id).subquery()
        
        # 【修复】历史记录里如果视频被下架或转私密，也不应该显示
        history_videos = db.session.query(Video)\
            .join(subquery, Video.id == subquery.c.video_id)\
            .filter(Video.status == 1, Video.visibility == 'public')\
            .order_by(subquery.c.max_time.desc())\
            .limit(8).all()
            
        response_data['history'] = [v.to_dict() for v in history_videos]
    else:
        response_data['history'] = []

    return jsonify({'code': 200, 'msg': 'success', 'data': response_data})

@recommend_bp.route('/related/<int:video_id>', methods=['GET'])
@swag_from(get_doc_path('related.yml'))
def related_recommend(video_id):
    videos = recommender.recommend_similar_content(video_id)
    return jsonify({'code': 200, 'data': videos})