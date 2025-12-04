import os
import time
import cv2
import jwt  # 【新增】需要解析Token
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ..models import Video, User, ActionLog, db
from flasgger import swag_from

video_bp = Blueprint('video', __name__)

def get_doc_path(filename):
    return os.path.join(os.path.dirname(__file__), '../docs/video', filename)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_thumbnail(video_path, thumbnail_path):
    try:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(thumbnail_path, frame)
        cap.release()
    except Exception as e:
        print(f"生成缩略图失败: {e}")

# 1. 上传接口
@video_bp.route('/upload', methods=['POST'])
@swag_from(get_doc_path('upload.yml'))
def upload_video():
    if 'file' not in request.files: return jsonify({'code': 400, 'msg': '没有文件'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'code': 400, 'msg': '未选择文件'}), 400
    
    # 获取参数
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

        # 默认 status=0 (待审核)
        video = Video(
            title=title, description=description, category=category,
            url=video_url, cover_url=cover_url, uploader_id=uploader_id,
            status=0 
        )
        db.session.add(video)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '上传成功，请等待审核', 'data': video.to_dict()})
    return jsonify({'code': 400, 'msg': '文件类型不支持'}), 400

# 2. 获取列表 (仅返回已发布的视频)
@video_bp.route('/list', methods=['GET'])
@swag_from(get_doc_path('list.yml'))
def get_video_list():
    category = request.args.get('category')
    search_query = request.args.get('q')
    
    # 【修复】增加 status=1 筛选
    query = Video.query.filter_by(status=1)
    
    if category and category != '全部':
        query = query.filter_by(category=category)
    if search_query:
        rule = f"%{search_query}%"
        query = query.filter((Video.title.like(rule)) | (Video.description.like(rule)))
        
    videos = query.order_by(Video.upload_time.desc()).all()
    return jsonify({'code': 200, 'data': [v.to_dict() for v in videos]})

# 3. 获取详情 (权限控制)
@video_bp.route('/<int:video_id>', methods=['GET'])
@swag_from(get_doc_path('detail.yml'))
def get_video_detail(video_id):
    video = Video.query.get(video_id)
    if not video:
        return jsonify({'code': 404, 'msg': '视频不存在'}), 404
    
    # 【修复】如果视频未过审/下架，检查权限
    if video.status != 1:
        has_permission = False
        token = request.headers.get('Authorization') # 从请求头获取Token (如果前端没传要配axios)
        
        # 尝试验证身份
        if token:
            try:
                # 去掉 Bearer 前缀 (如果有)
                if token.startswith('Bearer '): token = token.split(' ')[1]
                # 解析 Token
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user_id = payload.get('user_id')
                
                # 查询用户看是否是管理员或作者
                current_user = User.query.get(current_user_id)
                if current_user and (current_user.id == video.uploader_id or current_user.is_admin):
                    has_permission = True
            except Exception as e:
                print(f"Token Error: {e}")
        
        if not has_permission:
            return jsonify({'code': 403, 'msg': '该视频正在审核中或已下架'}), 403

    # 正常访问逻辑
    video.views += 1
    db.session.commit()
    
    likes_count = ActionLog.query.filter_by(video_id=video_id, action_type='like').count()
    uploader = User.query.get(video.uploader_id)
    
    video_data = video.to_dict()
    video_data['uploader_name'] = uploader.username if uploader else '未知用户'
    video_data['uploader_avatar'] = uploader.avatar if uploader else ''
    video_data['likes'] = likes_count
    
    return jsonify({'code': 200, 'data': video_data})

# 4. 删除视频
@video_bp.route('/delete/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    video = Video.query.get(video_id)
    if not video: return jsonify({'code': 404, 'msg': '视频不存在'}), 404
    db.session.delete(video)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})

# 5. 交互
@video_bp.route('/action', methods=['POST'])
@swag_from(get_doc_path('action.yml'))
def video_action():
    data = request.get_json()
    user_id = data.get('user_id')
    video_id = data.get('video_id')
    action_type = data.get('type')
    
    if action_type == 'view':
        log = ActionLog(user_id=user_id, video_id=video_id, action_type='view')
        db.session.add(log)
    elif action_type == 'favorite':
        exists = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='favorite').first()
        if not exists:
            log = ActionLog(user_id=user_id, video_id=video_id, action_type='favorite', weight=5)
            db.session.add(log)
    elif action_type == 'unfavorite':
        ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='favorite').delete()
    elif action_type == 'like':
        exists = ActionLog.query.filter_by(user_id=user_id, video_id=video_id, action_type='like').first()
        if not exists:
            log = ActionLog(user_id=user_id, video_id=video_id, action_type='like', weight=3)
            db.session.add(log)
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