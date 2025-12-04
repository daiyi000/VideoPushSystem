import os
from flasgger import swag_from
from flask import Blueprint, jsonify, request
from ..algorithm.core import recommender

recommend_bp = Blueprint('recommend', __name__)

def get_doc_path(filename):
    return os.path.join(os.path.dirname(__file__), '../docs/recommend', filename)

# 1. 首页个性化推荐接口
@recommend_bp.route('/home', methods=['GET'])
@swag_from(get_doc_path('home.yml'))
def home_recommend():
    user_id = request.args.get('user_id', type=int)
    
    if user_id:
        # 有用户ID：走协同过滤
        videos = recommender.recommend_by_history(user_id)
        msg = "基于您的兴趣推荐"
    else:
        # 无用户ID (游客)：走热门排行
        videos = recommender.get_hot_videos()
        msg = "热门视频推荐"
        
    return jsonify({'code': 200, 'msg': msg, 'data': videos})

# 2. 详情页“猜你喜欢”接口
@recommend_bp.route('/related/<int:video_id>', methods=['GET'])
@swag_from(get_doc_path('related.yml'))
def related_recommend(video_id):
    videos = recommender.recommend_similar_content(video_id)
    return jsonify({'code': 200, 'data': videos})