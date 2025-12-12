from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from flasgger import Swagger
from .config import Config

db = SQLAlchemy()
mail = Mail()
swagger = Swagger()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Swagger 配置 (Flasgger 默认生成的 specs 路由)
    app.config['SWAGGER'] = {
        'title': 'VideoHub API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': '基于 Flask + Vue 的智能视频推送系统 API 文档',
        'specs_route': '/apidocs/' # 这是 Swagger UI 的默认路径
    }
    
    db.init_app(app)
    mail.init_app(app)
    swagger.init_app(app) # 绑定 Swagger
    
    # 允许跨域
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"] 
        }
    }, supports_credentials=True)
    
    # 1. 注册视频蓝图
    from .api.video import video_bp
    app.register_blueprint(video_bp, url_prefix='/api/video')
    
    # 2. 注册认证蓝图
    from .api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # 3. 注册用户蓝图
    from .api.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    # 4. 注册推荐蓝图
    from .api.recommend import recommend_bp
    app.register_blueprint(recommend_bp, url_prefix='/api/recommend')
    
    # 5. 注册互动蓝图 (评论/弹幕)
    from .api.interaction import interaction_bp
    app.register_blueprint(interaction_bp, url_prefix='/api/interaction')

    # 6. 注册播放列表蓝图
    from .api.playlist import playlist_bp
    app.register_blueprint(playlist_bp, url_prefix='/api/playlist')

    # 7. 注册后台管理蓝图
    from .api.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # 8. 注册支付蓝图
    from .api.pay import pay_bp
    app.register_blueprint(pay_bp, url_prefix='/api/pay')

    # 注册自定义文档路由 (ReDoc)
    @app.route('/docs')
    def redoc_docs():
        return render_template('redoc.html')
    
    with app.app_context():
        from . import models 
        db.create_all()
        
    return app