import os
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from ..algorithm.core import recommender
from ..models import Video, ActionLog, db
from sqlalchemy import func  # 用于随机排序

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
    
    # 2. 发现/最近上传 (普通视频)
    if user_id:
        response_data['discover'] = recommender.recommend_by_history(user_id, limit=8)
    else:
        response_data['discover'] = recommender.get_hot_videos(limit=8)
        
    # 3. Shorts (随机 5 个)
    shorts_query = Video.query.filter_by(status=1, visibility='public', is_short=True)
    shorts_videos = shorts_query.order_by(func.random()).limit(5).all()
    response_data['shorts'] = [v.to_dict() for v in shorts_videos]
    
    # 4. 已观看 (History) (最多 6 个)
    if user_id:
        # 获取每个视频最近的观看记录
        subquery = db.session.query(
            ActionLog.video_id, 
            func.max(ActionLog.timestamp).label('max_time')
        ).filter_by(user_id=user_id, action_type='view').group_by(ActionLog.video_id).subquery()
        
        # 联合查询：Video + ActionLog (为了获取 progress)
        query = db.session.query(Video, ActionLog.progress, ActionLog.timestamp)\
            .join(subquery, Video.id == subquery.c.video_id)\
            .join(ActionLog, (ActionLog.video_id == Video.id) & (ActionLog.timestamp == subquery.c.max_time))\
            .filter(
                Video.status == 1, 
                Video.visibility == 'public',
                Video.is_short == False # 不显示 Shorts
            )
            
        results = query.all()
        
        history_list = []
        for v, progress, timestamp in results:
            # 过滤逻辑：观看超过 95% 或 剩余不足 10s 视为已看完
            if v.duration and v.duration > 0:
                is_finished = False
                if progress >= v.duration - 10: is_finished = True 
                if (progress / v.duration) > 0.95: is_finished = True 
                
                if not is_finished:
                    v_dict = v.to_dict()
                    v_dict['progress'] = progress 
                    
                    # 【优化】防止除零和超过100%
                    percent = (progress / v.duration) * 100
                    v_dict['progress_percent'] = min(percent, 100)
                    
                    # 用于排序的临时字段
                    v_dict['_sort_time'] = timestamp 
                    history_list.append(v_dict)
        
        # 按最后观看时间倒序排序
        history_list.sort(key=lambda x: x['_sort_time'], reverse=True)
        
        # 【优化】取前6个并清理临时字段
        final_history = history_list[:6]
        for item in final_history:
            item.pop('_sort_time', None)
            
        response_data['history'] = final_history
    else:
        response_data['history'] = []

    # 5. 混合推荐 (Mix)
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
@swag_from(get_doc_path('related.yml'))
def related_recommend(video_id):
    videos = recommender.recommend_similar_content(video_id)
    return jsonify({'code': 200, 'data': videos})