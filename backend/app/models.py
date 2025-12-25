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
        avatar_url = self.avatar
        # 强制修复混合内容问题：如果数据库存的是 http 的本站链接，转为相对路径
        if avatar_url and 'pay.aeasywink.top' in avatar_url:
             avatar_url = avatar_url.replace('http://pay.aeasywink.top', '').replace('https://pay.aeasywink.top', '')
        
        return {
            'id': self.id, 'username': self.username, 'email': self.email, 
            'avatar': avatar_url, 'banner': self.banner, 'description': self.description,
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
    
    # 【新增】字幕文件链接
    subtitle_url = db.Column(db.String(256))
    
    # 【新增】片尾推荐视频ID列表 (逗号分隔 "1,2,3")
    end_screen_video_ids = db.Column(db.String(256))

    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    uploader = db.relationship('User', backref='videos')

    def to_dict(self):
        author_name = self.uploader.username if self.uploader else '未知用户'
        author_avatar = self.uploader.avatar if self.uploader else ''
        
        # 强制修复混合内容问题 (将绝对路径转为相对路径)
        cover = self.cover_url
        if cover and 'pay.aeasywink.top' in cover:
             cover = cover.replace('http://pay.aeasywink.top', '').replace('https://pay.aeasywink.top', '')
             
        video_url = self.url
        if video_url and 'pay.aeasywink.top' in video_url:
             video_url = video_url.replace('http://pay.aeasywink.top', '').replace('https://pay.aeasywink.top', '')

        sub_url = self.subtitle_url
        if sub_url and 'pay.aeasywink.top' in sub_url:
             sub_url = sub_url.replace('http://pay.aeasywink.top', '').replace('https://pay.aeasywink.top', '')

        return {
            'id': self.id, 'title': self.title, 'description': self.description,
            'url': video_url, 'cover_url': cover, 'category': self.category,
            'views': self.views, 'tags': self.tags, 'status': self.status,
            'visibility': self.visibility, 
            'duration': self.duration,
            'is_short': self.is_short, # 返回标记
            'subtitle_url': sub_url, # 返回字幕链接
            'end_screen_video_ids': self.end_screen_video_ids, # 返回片尾推荐ID
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

# 10. 密码重置请求
class PasswordResetRequest(db.Model):
    __tablename__ = 'password_reset_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, sent, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('reset_requests', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'email': self.email,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 11. 通知系统
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # 接收者
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # 触发者
    type = db.Column(db.String(32)) # 'subscribe', 'recommend', 'interaction', 'reply', 'mention', 'promotion', 'system'
    content = db.Column(db.String(256))
    target_url = db.Column(db.String(256)) # 跳转链接
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 简单的关联，方便查询发送者信息
    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[user_id], backref=db.backref('notifications', lazy='dynamic'))

class NotificationSetting(db.Model):
    __tablename__ = 'notification_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
    notify_subscription = db.Column(db.Boolean, default=True) # 订阅频道有新动态
    notify_recommendation = db.Column(db.Boolean, default=True) # 推荐内容
    notify_interaction = db.Column(db.Boolean, default=True) # 我的频道/视频有互���
    notify_comment = db.Column(db.Boolean, default=True) # 评论回复/点赞
    notify_mention = db.Column(db.Boolean, default=True) # @我
    notify_promotion = db.Column(db.Boolean, default=True) # 促销
    notify_system = db.Column(db.Boolean, default=True) # 系统/密码重置

    user = db.relationship('User', backref=db.backref('notification_setting', uselist=False))