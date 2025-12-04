import os
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from ..models import Playlist, Video, db

playlist_bp = Blueprint('playlist', __name__)

def get_doc_path(filename):
    return os.path.join(os.path.dirname(__file__), '../docs/playlist', filename)

# 创建与删除接口 (保持不变)
@playlist_bp.route('/create', methods=['POST'])
@swag_from(get_doc_path('create.yml'))
def create_playlist():
    data = request.get_json()
    pl = Playlist(title=data.get('title'), user_id=data.get('user_id'), description=data.get('description', ''))
    db.session.add(pl)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '创建成功', 'data': pl.to_dict()})

@playlist_bp.route('/delete', methods=['POST'])
def delete_playlist():
    pl = Playlist.query.get(request.get_json().get('id'))
    if pl:
        db.session.delete(pl)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '删除成功'})
    return jsonify({'code': 404, 'msg': '列表不存在'})

# 【新增】向列表添加视频
@playlist_bp.route('/add_video', methods=['POST'])
def add_video_to_playlist():
    data = request.get_json()
    playlist_id = data.get('playlist_id')
    video_id = data.get('video_id')
    
    pl = Playlist.query.get(playlist_id)
    video = Video.query.get(video_id)
    
    if not pl or not video:
        return jsonify({'code': 404, 'msg': '资源不存在'}), 404
        
    # 检查是否已存在
    if video not in pl.videos:
        pl.videos.append(video)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '添加成功'})
    return jsonify({'code': 200, 'msg': '视频已在列表中'})

# 【新增】获取列表中的视频
@playlist_bp.route('/videos', methods=['GET'])
def get_playlist_videos():
    playlist_id = request.args.get('id')
    pl = Playlist.query.get(playlist_id)
    if not pl:
        return jsonify({'code': 404, 'msg': '列表不存在'}), 404
        
    return jsonify({'code': 200, 'data': [v.to_dict() for v in pl.videos]})

# 从列表移除视频
@playlist_bp.route('/remove_video', methods=['POST'])
def remove_video_from_playlist():
    data = request.get_json()
    playlist_id = data.get('playlist_id')
    video_id = data.get('video_id')
    
    pl = Playlist.query.get(playlist_id)
    video = Video.query.get(video_id)
    
    if not pl or not video:
        return jsonify({'code': 404, 'msg': '资源不存在'}), 404
        
    if video in pl.videos:
        pl.videos.remove(video)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '移除成功'})
    return jsonify({'code': 400, 'msg': '视频不在列表中'})