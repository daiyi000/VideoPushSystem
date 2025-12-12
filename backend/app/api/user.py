import os
import time
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from ..models import User, Video, ActionLog, Follow, Playlist, db
from flasgger import swag_from

def get_doc_path(filename):
    return os.path.join(os.path.dirname(__file__), '../docs/user', filename)

user_bp = Blueprint('user', __name__)

ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename): return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMG_EXTENSIONS

# ... (upload_avatar, upload_banner, profile, toggle_follow 保持不变) ...
@user_bp.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'file' not in request.files: return jsonify({'code': 400, 'msg': '没有文件'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'code': 400, 'msg': '未选择文件'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        new_filename = f"avatar_{timestamp}_{filename}"
        save_dir = os.path.join(current_app.root_path, 'static/avatars')
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        file.save(os.path.join(save_dir, new_filename))
        file_url = f"http://localhost:5000/static/avatars/{new_filename}"
        return jsonify({'code': 200, 'msg': '上传成功', 'url': file_url})
    return jsonify({'code': 400, 'msg': '格式不支持'})

@user_bp.route('/upload_banner', methods=['POST'])
def upload_banner():
    if 'file' not in request.files: return jsonify({'code': 400, 'msg': '没有文件'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'code': 400, 'msg': '未选择文件'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        new_filename = f"banner_{timestamp}_{filename}"
        save_dir = os.path.join(current_app.root_path, 'static/avatars') 
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        file.save(os.path.join(save_dir, new_filename))
        file_url = f"http://localhost:5000/static/avatars/{new_filename}"
        return jsonify({'code': 200, 'msg': '上传成功', 'url': file_url})
    return jsonify({'code': 400, 'msg': '格式不支持'})

@user_bp.route('/profile', methods=['GET', 'POST'])
@swag_from(get_doc_path('profile.yml'))
def profile():
    user_id = None
    if request.method == 'GET':
        user_id = request.args.get('user_id')
    else:
        data = request.get_json()
        if data: user_id = data.get('user_id')
    if not user_id: return jsonify({'code': 400, 'msg': '参数缺失'}), 400
    user = User.query.get(user_id)
    if not user: return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    if request.method == 'GET':
        return jsonify({'code': 200, 'data': user.to_dict()})
    if request.method == 'POST':
        data = request.get_json()
        if 'username' in data: 
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user.id:
                return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
            user.username = data['username']
        if 'avatar' in data: user.avatar = data['avatar']
        if 'banner' in data: user.banner = data['banner']
        if 'description' in data: user.description = data['description']
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        try:
            db.session.commit()
            return jsonify({'code': 200, 'msg': '修改成功', 'data': user.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({'code': 500, 'msg': f'数据库错误: {str(e)}'}), 500

@user_bp.route('/follow', methods=['POST'])
@swag_from(get_doc_path('follow.yml'))
def toggle_follow():
    data = request.get_json()
    follower_id = data.get('follower_id')
    followed_id = data.get('followed_id')
    if str(follower_id) == str(followed_id): return jsonify({'code': 400, 'msg': '不能关注自己'}), 400
    existing = Follow.query.filter_by(follower_id=follower_id, followed_id=followed_id).first()
    is_following = False
    if existing:
        db.session.delete(existing)
        is_following = False
    else:
        new_follow = Follow(follower_id=follower_id, followed_id=followed_id)
        db.session.add(new_follow)
        is_following = True
    db.session.commit()
    fans_count = Follow.query.filter_by(followed_id=followed_id).count()
    return jsonify({'code': 200, 'msg': '操作成功', 'is_following': is_following, 'fans_count': fans_count})

@user_bp.route('/channel_info', methods=['GET'])
@swag_from(get_doc_path('channel_info.yml'))
def get_channel_info():
    author_id = request.args.get('author_id')
    username = request.args.get('username')
    visitor_id = request.args.get('visitor_id')
    sort_by = request.args.get('sort_by', 'new')
    keyword = request.args.get('q', '')
    
    author = None
    if author_id:
        author = User.query.get(author_id)
    elif username:
        author = User.query.filter_by(username=username).first()
        
    if not author: return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    target_id = author.id
    fans_count = Follow.query.filter_by(followed_id=target_id).count()
    is_following = False
    is_owner = False
    if visitor_id:
        exists = Follow.query.filter_by(follower_id=visitor_id, followed_id=target_id).first()
        is_following = bool(exists)
        if str(visitor_id) == str(target_id):
            is_owner = True
            
    query = Video.query.filter_by(uploader_id=target_id)
    
    # 【核心修复】过滤逻辑
    if not is_owner:
        query = query.filter_by(status=1, visibility='public')
    else:
        pass # 主人看全部
    
    if keyword:
        rule = f"%{keyword}%"
        query = query.filter(Video.title.like(rule))
    if sort_by == 'hot': query = query.order_by(Video.views.desc())
    elif sort_by == 'old': query = query.order_by(Video.upload_time.asc())
    else: query = query.order_by(Video.upload_time.desc())
    
    videos = query.all()
    playlists = Playlist.query.filter_by(user_id=target_id).order_by(Playlist.created_at.desc()).all()
    
    return jsonify({
        'code': 200,
        'data': {
            'author': author.to_dict(),
            'stats': {
                'fans': fans_count,
                'is_following': is_following
            },
            'videos': [v.to_dict() for v in videos],
            'playlists': [p.to_dict() for p in playlists]
        }
    })

# ... (following_list, my_videos, etc. 保持不变) ...
@user_bp.route('/following_list', methods=['GET'])
def get_following_list():
    user_id = request.args.get('user_id')
    if not user_id: return jsonify({'code': 200, 'data': []})
    follows = Follow.query.filter_by(follower_id=user_id).all()
    result = []
    for f in follows:
        author = User.query.get(f.followed_id)
        if author: result.append({ 'id': author.id, 'username': author.username, 'avatar': author.avatar })
    return jsonify({'code': 200, 'data': result})

@user_bp.route('/my_videos', methods=['GET'])
def my_videos():
    user_id = request.args.get('user_id')
    videos = Video.query.filter_by(uploader_id=user_id).order_by(Video.upload_time.desc()).all()
    return jsonify({'code': 200, 'data': [v.to_dict() for v in videos]})

@user_bp.route('/favorites', methods=['GET'])
def my_favorites():
    user_id = request.args.get('user_id')
    logs = ActionLog.query.filter_by(user_id=user_id, action_type='favorite').order_by(ActionLog.timestamp.desc()).all()
    video_list = []
    for log in logs:
        video = Video.query.get(log.video_id)
        if video: video_list.append(video.to_dict())
    return jsonify({'code': 200, 'data': video_list})

@user_bp.route('/history', methods=['GET'])
def my_history():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'msg': 'User ID is required'})
    
    logs = ActionLog.query.filter_by(user_id=user_id, action_type='view')\
        .order_by(ActionLog.timestamp.desc()).limit(50).all()
    
    video_list = []
    seen = set()
    
    for log in logs:
        if log.video_id in seen:
            continue
        seen.add(log.video_id)
        
        video = Video.query.get(log.video_id)
        if video:
            v_dict = video.to_dict()
            # 注入进度
            v_dict['progress'] = log.progress 
            if video.duration and video.duration > 0:
                percent = (log.progress / video.duration) * 100
                v_dict['progress_percent'] = min(percent, 100)
            else:
                v_dict['progress_percent'] = 0
            
            v_dict['view_at'] = log.timestamp.strftime('%Y-%m-%d %H:%M')
            video_list.append(v_dict)
            
    return jsonify({'code': 200, 'data': video_list})