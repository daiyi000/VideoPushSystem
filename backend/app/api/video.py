import os
import time
import cv2
import random
import jwt
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ..models import Video, User, ActionLog, Follow, db, Comment, Danmaku, playlist_video
from flasgger import swag_from
from sqlalchemy import func

video_bp = Blueprint('video', __name__)

def get_doc_path(filename):
    return os.path.join(os.path.dirname(__file__), '../docs/video', filename)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_auto_thumbnails(video_path, output_folder, file_prefix):
    thumbnails = []
    duration = 0
    is_short = False
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        # 获取视频元数据
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        if fps > 0:
            duration = int(total_frames / fps)
            
        # 【核心逻辑】判断是否为 Shorts: 时长 <= 60秒 且 高 >= 宽
        if duration <= 60 and height >= width:
            is_short = True
            
        percentages = [0.2, 0.5, 0.8]
        for idx, pct in enumerate(percentages):
            target_frame = int(total_frames * pct)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = cap.read()
            if ret:
                thumb_filename = f"{file_prefix}_auto_{idx}.jpg"
                save_path = os.path.join(output_folder, thumb_filename)
                cv2.imwrite(save_path, frame)
                url = f"http://localhost:5000/static/covers/{thumb_filename}"
                thumbnails.append(url)
        cap.release()
    except Exception as e:
        print(f"视频处理失败: {e}")
    
    return thumbnails, duration, is_short

# 1. 上传接口
@video_bp.route('/upload_file', methods=['POST'])
@swag_from(get_doc_path('upload.yml'))
def upload_video_file():
    if 'file' not in request.files: return jsonify({'code': 400, 'msg': '无文件'})
    file = request.files['file']
    uploader_id = request.form.get('uploader_id')
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        static_folder = os.path.join(os.getcwd(), 'app/static')
        upload_folder = os.path.join(static_folder, 'uploads')
        cover_folder = os.path.join(static_folder, 'covers')
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(cover_folder, exist_ok=True)
        
        new_video_name = f"{timestamp}_{filename}"
        video_path = os.path.join(upload_folder, new_video_name)
        file.save(video_path)
        
        base_url = "http://localhost:5000"
        video_url = f"{base_url}/static/uploads/{new_video_name}"
        
        # 自动生成封面并判断是否为 Short
        auto_covers, duration, is_short = generate_auto_thumbnails(video_path, cover_folder, f"{timestamp}_{filename}")
        default_cover = auto_covers[0] if auto_covers else "https://via.placeholder.com/300x200"

        video = Video(
            title=file.filename,
            description="",
            url=video_url,
            cover_url=default_cover,
            uploader_id=uploader_id,
            duration=duration,
            is_short=is_short, # 存入数据库
            status=-1, 
            visibility='private' 
        )
        db.session.add(video)
        db.session.commit()
        
        return jsonify({
            'code': 200, 
            'msg': '上传完成', 
            'data': {
                'id': video.id,
                'url': video.url,
                'title': video.title,
                'auto_covers': auto_covers,
                'is_short': is_short
            }
        })
    return jsonify({'code': 400, 'msg': '格式不支持'})

# ... (publish, update, delete, action 等其他接口保持不变) ...

@video_bp.route('/publish', methods=['POST'])
@swag_from(get_doc_path('publish.yml'))
def publish_video():
    data = request.get_json()
    video = Video.query.get(data.get('id'))
    if not video: return jsonify({'code': 404, 'msg': '视频不存在'})
    if 'title' in data: video.title = data['title']
    if 'description' in data: video.description = data['description']
    if 'category' in data: video.category = data['category']
    if 'tags' in data: video.tags = data['tags']
    if 'cover_url' in data: video.cover_url = data['cover_url']
    if 'visibility' in data: video.visibility = data['visibility']
    
    action = data.get('action')
    if action == 'draft':
        video.status = -1
        msg = '已保存为草稿'
    else:
        video.status = 0
        msg = '发布成功，等待审核'
    
    db.session.commit()
    return jsonify({'code': 200, 'msg': msg})

@video_bp.route('/update', methods=['POST'])
def update_video():
    data = request.get_json()
    video_id = data.get('id')
    user_id = data.get('user_id')
    action = data.get('action')

    video = Video.query.get(video_id)
    if not video: return jsonify({'code': 404, 'msg': '视频不存在'})
    current_user = User.query.get(user_id)
    if not current_user or (str(current_user.id) != str(video.uploader_id) and not current_user.is_admin):
         return jsonify({'code': 403, 'msg': '无权操作'})

    if 'title' in data: video.title = data['title']
    if 'description' in data: video.description = data['description']
    if 'visibility' in data: video.visibility = data['visibility']
    if 'category' in data: video.category = data['category']
    if 'tags' in data: video.tags = data['tags']
    if 'cover_url' in data: video.cover_url = data['cover_url']
    
    if action == 'draft':
        video.status = -1
        msg = '已撤回为草稿'
    else:
        if video.status != -1: video.status = 0
        msg = '更新成功'
    
    db.session.commit()
    return jsonify({'code': 200, 'msg': msg})

@video_bp.route('/list', methods=['GET'])
@swag_from(get_doc_path('list.yml'))
def get_video_list():
    category = request.args.get('category')
    search_query = request.args.get('q')
    query = Video.query.filter_by(status=1, visibility='public')
    if category and category != '全部': query = query.filter_by(category=category)
    if search_query:
        rule = f"%{search_query}%"
        query = query.join(User).filter((Video.title.like(rule)) | (Video.description.like(rule)) | (User.username.like(rule)))
    videos = query.order_by(Video.upload_time.desc()).all()
    return jsonify({'code': 200, 'data': [v.to_dict() for v in videos]})

@video_bp.route('/<int:video_id>', methods=['GET'])
@swag_from(get_doc_path('detail.yml'))
def get_video_detail(video_id):
    video = Video.query.get(video_id)
    if not video: return jsonify({'code': 404, 'msg': '视频不存在'}), 404
    if video.status != 1 or video.visibility == 'private':
        has_permission = False
        token = request.headers.get('Authorization')
        if token:
            try:
                if token.startswith('Bearer '): token = token.split(' ')[1]
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user_id = payload.get('user_id')
                current_user = User.query.get(current_user_id)
                if current_user and (str(current_user.id) == str(video.uploader_id) or current_user.is_admin):
                    has_permission = True
            except Exception: pass
        if not has_permission: return jsonify({'code': 403, 'msg': '该视频为私享视频或已下架'}), 403
    video.views += 1
    db.session.commit()
    likes_count = ActionLog.query.filter_by(video_id=video_id, action_type='like').count()
    uploader = User.query.get(video.uploader_id)
    video_data = video.to_dict()
    video_data['uploader_name'] = uploader.username if uploader else '未知'
    video_data['uploader_avatar'] = uploader.avatar if uploader else ''
    video_data['likes'] = likes_count
    return jsonify({'code': 200, 'data': video_data})

@video_bp.route('/delete/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    video = Video.query.get(video_id)
    if not video: return jsonify({'code': 404, 'msg': '视频不存在'}), 404
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
        return jsonify({'code': 500, 'msg': '删除失败'})

@video_bp.route('/action', methods=['POST'])
@swag_from(get_doc_path('action.yml'))
def video_action():
    data = request.get_json()
    user_id = data.get('user_id')
    video_id = data.get('video_id')
    action_type = data.get('type')
    
    # 1. 处理 "观看/进入页面" (view)
    if action_type == 'view':
        # 【核心修改】先查找是否已存在记录
        existing_log = ActionLog.query.filter_by(
            user_id=user_id, 
            video_id=video_id, 
            action_type='view'
        ).first()

        if existing_log:
            # 如果存在：只更新“最后观看时间”，保留原有的 progress！
            existing_log.timestamp = datetime.utcnow()
            # 注意：这里千万不要写 existing_log.progress = 0
        else:
            # 如果不存在：才创建新记录
            log = ActionLog(user_id=user_id, video_id=video_id, action_type='view', progress=0)
            db.session.add(log)
        
    # 2. 处理 "更新进度" (progress)
    elif action_type == 'progress':
        progress = data.get('progress', 0)
        # 查找记录进行更新
        log = ActionLog.query.filter_by(
            user_id=user_id, 
            video_id=video_id, 
            action_type='view'
        ).first() # 这里不需要 order_by 了，因为现在逻辑保证了唯一性(或只操作这一个)

        if log:
            log.progress = int(progress)
            log.timestamp = datetime.utcnow() # 更新进度时也顺便更新时间
        else:
            # 防御性代码：如果万一没找到（极少见），补一条
            log = ActionLog(user_id=user_id, video_id=video_id, action_type='view', progress=int(progress))
            db.session.add(log)

    # 3. 处理 "收藏" (favorite)
    elif action_type == 'favorite':
        exists = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='favorite').first()
        if not exists:
            log = ActionLog(user_id=user_id, video_id=video_id, action_type='favorite', weight=5)
            db.session.add(log)
    
    # 4. 处理 "取消收藏" (unfavorite)
    elif action_type == 'unfavorite':
        ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='favorite').delete()
    
    # 5. 处理 "点赞" (like)
    elif action_type == 'like':
        exists = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='like').first()
        if not exists:
            log = ActionLog(user_id=user_id, video_id=video_id, action_type='like', weight=3)
            db.session.add(log)
    
    # 6. 处理 "取消点赞" (unlike)
    elif action_type == 'unlike':
        ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='like').delete()
        
    db.session.commit()
    return jsonify({'code': 200, 'msg': '操作成功'})

@video_bp.route('/check_fav', methods=['GET'])
def check_fav():
    user_id = request.args.get('user_id')
    video_id = request.args.get('video_id')
    exists = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='favorite').first()
    return jsonify({'is_fav': bool(exists)})

@video_bp.route('/creator/stats', methods=['GET'])
def get_creator_stats():
    user_id = request.args.get('user_id')
    if not user_id: return jsonify({'code': 400, 'msg': '缺少 user_id'})
    total_videos = Video.query.filter_by(uploader_id=user_id).count()
    total_views = db.session.query(func.sum(Video.views)).filter(Video.uploader_id == user_id).scalar() or 0
    total_fans = Follow.query.filter_by(followed_id=user_id).count()
    total_likes = db.session.query(func.count(ActionLog.id)).join(Video, ActionLog.video_id == Video.id).filter(Video.uploader_id == user_id, ActionLog.action_type == 'like').scalar() or 0
    total_watch_seconds = db.session.query(func.sum(Video.views * Video.duration)).filter(Video.uploader_id == user_id).scalar() or 0
    total_watch_hours = round(total_watch_seconds / 3600, 2)
    all_videos = Video.query.filter_by(uploader_id=user_id).order_by(Video.upload_time.desc()).all()
    cat_stats = db.session.query(Video.category, func.count(Video.id)).filter(Video.uploader_id == user_id).group_by(Video.category).all()
    chart_category = [{'name': r[0], 'value': r[1]} for r in cat_stats]
    return jsonify({
        'code': 200,
        'data': {
            'total_videos': total_videos, 'total_views': total_views, 'total_fans': total_fans, 'total_likes': total_likes, 'total_watch_hours': total_watch_hours,
            'recent_videos': [v.to_dict() for v in all_videos[:5]], 'all_videos': [v.to_dict() for v in all_videos], 'chart_category': chart_category
        }
    })