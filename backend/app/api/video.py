import os
import time
import cv2
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ..models import Video, User, ActionLog, db

video_bp = Blueprint('video', __name__)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 生成缩略图函数
def generate_thumbnail(video_path, thumbnail_path):
    try:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(thumbnail_path, frame)
        cap.release()
    except Exception as e:
        print(f"生成缩略图失败: {e}")

# 1. 视频上传接口
@video_bp.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': '没有文件部分'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'msg': '未选择文件'}), 400
        
    title = request.form.get('title')
    description = request.form.get('description')
    category = request.form.get('category')
    uploader_id = request.form.get('uploader_id')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        new_video_name = f"{timestamp}_{filename}"
        
        static_folder = os.path.join(os.getcwd(), 'app/static')
        upload_folder = os.path.join(static_folder, 'uploads')
        cover_folder = os.path.join(static_folder, 'covers')
        
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(cover_folder, exist_ok=True)
        
        video_path = os.path.join(upload_folder, new_video_name)
        file.save(video_path)
        
        new_cover_name = f"{timestamp}_{filename.rsplit('.', 1)[0]}.jpg"
        cover_path = os.path.join(cover_folder, new_cover_name)
        generate_thumbnail(video_path, cover_path)
        
        base_url = "http://localhost:5000"
        video_url = f"{base_url}/static/uploads/{new_video_name}"
        cover_url = f"{base_url}/static/covers/{new_cover_name}"

        video = Video(
            title=title,
            description=description,
            category=category,
            url=video_url,
            cover_url=cover_url,
            uploader_id=uploader_id
        )
        db.session.add(video)
        db.session.commit()
        
        return jsonify({'code': 200, 'msg': '上传成功', 'data': video.to_dict()})
        
    return jsonify({'code': 400, 'msg': '文件类型不支持'}), 400

# 2. 获取视频列表
@video_bp.route('/list', methods=['GET'])
def get_video_list():
    category = request.args.get('category')
    search_query = request.args.get('q')
    
    query = Video.query
    if category and category != '全部':
        query = query.filter_by(category=category)
    if search_query:
        rule = f"%{search_query}%"
        query = query.filter(
            (Video.title.like(rule)) | (Video.description.like(rule))
        )
    videos = query.order_by(Video.upload_time.desc()).all()
    return jsonify({'code': 200, 'data': [v.to_dict() for v in videos]})

# 3. 获取视频详情
@video_bp.route('/<int:video_id>', methods=['GET'])
def get_video_detail(video_id):
    video = Video.query.get(video_id)
    if not video:
        return jsonify({'code': 404, 'msg': '视频不存在'}), 404
    
    # 增加播放量
    video.views += 1
    db.session.commit()
    
    # 【核心修改】统计点赞数量
    likes_count = ActionLog.query.filter_by(video_id=video_id, action_type='like').count()
    
    uploader = User.query.get(video.uploader_id)
    video_data = video.to_dict()
    video_data['uploader_name'] = uploader.username if uploader else '未知用户'
    video_data['uploader_avatar'] = uploader.avatar if uploader else ''
    
    # 将点赞数加入返回数据
    video_data['likes'] = likes_count 
    
    return jsonify({'code': 200, 'data': video_data})

# 4. 删除视频
@video_bp.route('/delete/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    video = Video.query.get(video_id)
    if not video:
        return jsonify({'code': 404, 'msg': '视频不存在'}), 404
    db.session.delete(video)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})

# 5. 用户交互 (收藏/取消收藏/记录观看/点赞/取消点赞)
@video_bp.route('/action', methods=['POST'])
def video_action():
    data = request.get_json()
    user_id = data.get('user_id')
    video_id = data.get('video_id')
    action_type = data.get('type') # 'view', 'favorite', 'unfavorite', 'like', 'unlike'
    
    if action_type == 'view':
        # 记录观看历史
        log = ActionLog(user_id=user_id, video_id=video_id, action_type='view')
        db.session.add(log)
        
    elif action_type == 'favorite':
        # 收藏
        exists = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='favorite').first()
        if not exists:
            log = ActionLog(user_id=user_id, video_id=video_id, action_type='favorite', weight=5)
            db.session.add(log)
            
    elif action_type == 'unfavorite':
        # 取消收藏
        ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='favorite').delete()

    # 【新增】点赞逻辑
    elif action_type == 'like':
        exists = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='like').first()
        if not exists:
            # 点赞权重设为 3
            log = ActionLog(user_id=user_id, video_id=video_id, action_type='like', weight=3)
            db.session.add(log)
            
    # 【新增】取消点赞逻辑
    elif action_type == 'unlike':
        ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='like').delete()
        
    db.session.commit()
    return jsonify({'code': 200, 'msg': '操作成功'})

# 6. 检查视频是否被我收藏 (用于前端高亮收藏按钮)
@video_bp.route('/check_fav', methods=['GET'])
def check_fav():
    user_id = request.args.get('user_id')
    video_id = request.args.get('video_id')
    exists = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='favorite').first()
    return jsonify({'is_fav': bool(exists)})