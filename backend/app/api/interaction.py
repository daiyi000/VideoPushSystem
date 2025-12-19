import os
from flask import Blueprint, request, jsonify
from ..models import Comment, Danmaku, User, Video, db, ActionLog, CommentLike
from datetime import datetime
from flasgger import swag_from

interaction_bp = Blueprint('interaction', __name__)

# --- 评论功能 (升级版) ---

@interaction_bp.route('/comments', methods=['GET'])
@swag_from('../docs/interaction/comments.yml') # <--- 修改
def get_comments():
    video_id = request.args.get('video_id')
    user_id = request.args.get('user_id', type=int) 
    sort_by = request.args.get('sort_by', 'hot')
    
    liked_comment_ids = set()
    if user_id:
        user_likes = CommentLike.query.filter_by(user_id=user_id).all()
        liked_comment_ids = {like.comment_id for like in user_likes}

    query = Comment.query.filter_by(video_id=video_id, parent_id=None)
    
    if sort_by == 'new':
        comments = query.order_by(Comment.is_pinned.desc(), Comment.timestamp.desc()).all()
    else:
        comments = query.order_by(Comment.is_pinned.desc(), Comment.likes.desc()).all()
    
    data = []
    for c in comments:
        replies_obj = c.replies.order_by(Comment.timestamp.asc()).all()
        replies_data = []
        for r in replies_obj:
            replies_data.append({
                'id': r.id,
                'content': r.content,
                'time': r.timestamp.strftime('%Y-%m-%d %H:%M'),
                'likes': r.likes,
                'is_liked': r.id in liked_comment_ids,
                'user': {'id': r.user.id, 'username': r.user.username, 'avatar': r.user.avatar, 'verification_type': r.user.verification_type}
            })

        data.append({
            'id': c.id,
            'content': c.content,
            'time': c.timestamp.strftime('%Y-%m-%d %H:%M'),
            'likes': c.likes,
            'is_pinned': c.is_pinned,
            'is_liked': c.id in liked_comment_ids,
            'user': {'id': c.user.id, 'username': c.user.username, 'avatar': c.user.avatar, 'verification_type': c.user.verification_type},
            'replies': replies_data
        })
        
    return jsonify({'code': 200, 'data': data})

@interaction_bp.route('/comment/add', methods=['POST'])
@swag_from('../docs/interaction/add_comment.yml') # <--- 修改
def add_comment():
    data = request.get_json()
    new_comment = Comment(
        content=data.get('content'),
        user_id=data.get('user_id'),
        video_id=data.get('video_id'),
        parent_id=data.get('parent_id')
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '评论成功'})

@interaction_bp.route('/comment/like', methods=['POST'])
@swag_from('../docs/interaction/like_comment.yml') # <--- 修改
def like_comment():
    data = request.get_json()
    comment_id = data.get('comment_id')
    user_id = data.get('user_id')
    
    if not user_id or not comment_id:
        return jsonify({'code': 400, 'msg': '参数缺失'}), 400

    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'code': 404, 'msg': '评论不存在'}), 404

    existing_like = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    
    action = ''
    if existing_like:
        db.session.delete(existing_like)
        comment.likes = max(0, comment.likes - 1)
        action = 'unlike'
    else:
        new_like = CommentLike(user_id=user_id, comment_id=comment_id)
        db.session.add(new_like)
        comment.likes += 1
        action = 'like'
        
    db.session.commit()
    return jsonify({'code': 200, 'msg': '操作成功', 'likes': comment.likes, 'action': action})

@interaction_bp.route('/comment/pin', methods=['POST'])
@swag_from('../docs/interaction/pin_comment.yml') # <--- 修改
def pin_comment():
    data = request.get_json()
    comment_id = data.get('comment_id')
    user_id = data.get('user_id')
    
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'code': 404, 'msg': '评论不存在'}), 404
        
    video = Video.query.get(comment.video_id)
    if str(video.uploader_id) != str(user_id):
        return jsonify({'code': 403, 'msg': '无权操作'}), 403
        
    if comment.is_pinned:
        comment.is_pinned = False
    else:
        old_pinned = Comment.query.filter_by(video_id=video.id, is_pinned=True).first()
        if old_pinned: old_pinned.is_pinned = False
        comment.is_pinned = True
        
    db.session.commit()
    return jsonify({'code': 200, 'msg': '操作成功'})

@interaction_bp.route('/danmaku', methods=['GET'])
@swag_from('../docs/interaction/danmaku.yml') # <--- 修改
def get_danmaku():
    video_id = request.args.get('video_id')
    danmakus = Danmaku.query.filter_by(video_id=video_id).all()
    data = [{'text': d.content, 'time': d.time_point, 'color': d.color} for d in danmakus]
    return jsonify({'code': 200, 'data': data})

@interaction_bp.route('/danmaku/send', methods=['POST'])
@swag_from('../docs/interaction/send_danmaku.yml') # <--- 修改
def send_danmaku():
    data = request.get_json()
    new_dm = Danmaku(
        content=data.get('text'), time_point=data.get('time'), color=data.get('color', '#ffffff'),
        user_id=data.get('user_id'), video_id=data.get('video_id')
    )
    db.session.add(new_dm)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '发送成功'})

@interaction_bp.route('/check_status', methods=['GET'])
@swag_from('../docs/interaction/check_status.yml') # <--- 修改
def check_status():
    user_id = request.args.get('user_id')
    video_id = request.args.get('video_id')
    is_fav = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='favorite').first()
    is_like = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='like').first()
    view_log = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='view')\
        .order_by(ActionLog.timestamp.desc()).first()
    last_progress = view_log.progress if view_log else 0
    return jsonify({
        'code': 200, 
        'data': {
            'is_fav': bool(is_fav), 
            'is_like': bool(is_like),
            'last_progress': last_progress
        }
    })