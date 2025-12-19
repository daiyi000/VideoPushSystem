import os
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from ..algorithm.core import recommender
from ..models import Video, ActionLog, db
from sqlalchemy import func

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/home', methods=['GET'])
@swag_from('../docs/recommend/home.yml') # <--- 修改
def home_recommend():
    user_id = request.args.get('user_id', type=int)
    
    response_data = {}
    response_data['categories'] = recommender.get_user_preferred_categories(user_id)
    
    if user_id:
        response_data['discover'] = recommender.recommend_by_history(user_id, limit=8)
    else:
        response_data['discover'] = recommender.get_hot_videos(limit=8)
        
    shorts_query = Video.query.filter_by(status=1, visibility='public', is_short=True)
    shorts_videos = shorts_query.order_by(func.random()).limit(5).all()
    response_data['shorts'] = [v.to_dict() for v in shorts_videos]
    
    if user_id:
        subquery = db.session.query(
            ActionLog.video_id, 
            func.max(ActionLog.timestamp).label('max_time')
        ).filter_by(user_id=user_id, action_type='view').group_by(ActionLog.video_id).subquery()
        
        query = db.session.query(Video, ActionLog.progress, ActionLog.timestamp)\
            .join(subquery, Video.id == subquery.c.video_id)\
            .join(ActionLog, (ActionLog.video_id == Video.id) & (ActionLog.timestamp == subquery.c.max_time))\
            .filter(
                Video.status == 1, 
                Video.visibility == 'public',
                Video.is_short == False 
            )
            
        results = query.all()
        
        history_list = []
        for v, progress, timestamp in results:
            if v.duration and v.duration > 0:
                is_finished = False
                if progress >= v.duration - 10: is_finished = True 
                if (progress / v.duration) > 0.95: is_finished = True 
                
                if not is_finished:
                    v_dict = v.to_dict()
                    v_dict['progress'] = progress 
                    percent = (progress / v.duration) * 100
                    v_dict['progress_percent'] = min(percent, 100)
                    v_dict['_sort_time'] = timestamp 
                    history_list.append(v_dict)
        
        history_list.sort(key=lambda x: x['_sort_time'], reverse=True)
        final_history = history_list[:6]
        for item in final_history:
            item.pop('_sort_time', None)
            
        response_data['history'] = final_history
    else:
        response_data['history'] = []

    exclude_ids = [v['id'] for v in response_data.get('discover', [])]
    if user_id:
        exclude_ids += [v['id'] for v in response_data.get('history', [])]
        
    mix_query = Video.query.filter(
        Video.status == 1, 
        Video.visibility == 'public', 
        Video.is_short == False,
        Video.id.notin_(exclude_ids)
    ).order_by(func.random()).limit(6).all()
    
    response_data['mix_content'] = [v.to_dict() for v in mix_query]

    return jsonify({'code': 200, 'msg': 'success', 'data': response_data})

@recommend_bp.route('/related/<int:video_id>', methods=['GET'])
@swag_from('../docs/recommend/related.yml') # <--- 修改
def related_recommend(video_id):
    videos = recommender.recommend_similar_content(video_id)
    return jsonify({'code': 200, 'data': videos})