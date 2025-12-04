from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from .config import Config

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    mail.init_app(app)
    
    # 允许跨域
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # 1. 注册视频蓝图
    from .api.video import video_bp
    app.register_blueprint(video_bp, url_prefix='/api/video')
    
    # 2. 注册认证蓝图
    from .api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # 3. 【重点】注册用户蓝图 (你之前可能漏了这段，或者没保存)
    from .api.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    #4. 算法
    from .api.recommend import recommend_bp
    app.register_blueprint(recommend_bp, url_prefix='/api/recommend')
    
    #5. 弹幕 评论
    from .api.interaction import interaction_bp
    app.register_blueprint(interaction_bp, url_prefix='/api/interaction')

    #6. 播放列表
    from .api.playlist import playlist_bp
    app.register_blueprint(playlist_bp, url_prefix='/api/playlist')

    #注册后台管理蓝图
    from .api.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    with app.app_context():
        from . import models 
        db.create_all()
        
    return app