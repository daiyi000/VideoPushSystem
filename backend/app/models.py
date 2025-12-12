from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

# 多对多关系表：播放列表 <-> 视频
playlist_video = db.Table('playlist_video',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlists.id'), primary_key=True),
    db.Column('video_id', db.Integer, db.ForeignKey('videos.id'), primary_key=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)

# 1. 用户表
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, default="新用户")
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) 
    avatar = db.Column(db.String(256), default='https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png')
    banner = db.Column(db.String(256), default='https://via.placeholder.com/1200x300?text=Channel+Banner')
    description = db.Column(db.String(256), default='这个人很懒，什么都没写')
    verification_type = db.Column(db.Integer, default=0)  # 认证类型: 0=无, 1=普通认证(对勾), 2=音乐人认证(音符)
    
    # 权限与状态
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系定义
    logs = db.relationship('ActionLog', back_populates='user', lazy='dynamic')
    comments = db.relationship('Comment', back_populates='user', lazy='dynamic')
    playlists = db.relationship('Playlist', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def to_dict(self):
        return {
            'id': self.id, 'username': self.username, 'email': self.email, 
            'avatar': self.avatar, 'banner': self.banner, 'description': self.description,
            'is_admin': self.is_admin, 'is_banned': self.is_banned,
            'created_at': self.created_at.strftime('%Y-%m-%d'),
            'verification_type': self.verification_type,
        }

# 2. 视频表
class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(256), nullable=False) 
    cover_url = db.Column(db.String(256))
    category = db.Column(db.String(50))
    tags = db.Column(db.String(128)) 
    views = db.Column(db.Integer, default=0)
    
    duration = db.Column(db.Integer, default=0)
    
    # 【新增】是否为 Shorts 短视频
    is_short = db.Column(db.Boolean, default=False)
    
    status = db.Column(db.Integer, default=0) 
    visibility = db.Column(db.String(20), default='public')
    
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    uploader = db.relationship('User', backref='videos')

    def to_dict(self):
        author_name = self.uploader.username if self.uploader else '未知用户'
        author_avatar = self.uploader.avatar if self.uploader else ''
        return {
            'id': self.id, 'title': self.title, 'description': self.description,
            'url': self.url, 'cover_url': self.cover_url, 'category': self.category,
            'views': self.views, 'tags': self.tags, 'status': self.status,
            'visibility': self.visibility, 
            'duration': self.duration,
            'is_short': self.is_short, # 返回标记
            'upload_time': self.upload_time.strftime('%Y-%m-%d %H:%M'),
            'uploader_id': self.uploader_id, 'uploader_name': author_name, 'uploader_avatar': author_avatar,
            'uploader_verification_type': self.uploader.verification_type if self.uploader else 0,
        }

# 3. 行为日志
class ActionLog(db.Model):
    __tablename__ = 'action_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'))
    action_type = db.Column(db.String(20)) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    weight = db.Column(db.Integer, default=1)
    progress = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', back_populates='logs')

# 4. 评论
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1024), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    is_pinned = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer, default=0)
    user = db.relationship('User', back_populates='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

class CommentLike(db.Model):
    __tablename__ = 'comment_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 5. 弹幕
class Danmaku(db.Model):
    __tablename__ = 'danmakus'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(128), nullable=False)
    time_point = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(128), default='#ffffff') 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 6. 关注
class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 7. 播放列表
class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='playlists')
    videos = db.relationship('Video', secondary=playlist_video, backref=db.backref('in_playlists', lazy='dynamic'), lazy='dynamic')
    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'description': self.description,
            'count': self.videos.count(),
            'created_at': self.created_at.strftime('%Y-%m-%d'),
            'cover_url': self.videos.first().cover_url if self.videos.first() else 'https://via.placeholder.com/300x200?text=Empty'
        }

# 8. 邮箱验证码
class EmailCaptcha(db.Model):
    __tablename__ = 'email_captchas'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 9. 订单表
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(64), unique=True, nullable=False) # 比如 "20231212xxxxx"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subject = db.Column(db.String(128)) # 订单标题: "购买个人认证"
    total_amount = db.Column(db.Float)  # 金额
    trade_status = db.Column(db.String(32), default='WAIT_BUYER_PAY') # 交易状态
    # 购买的具体认证类型
    target_ver_type = db.Column(db.Integer) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)