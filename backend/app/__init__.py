import os
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
    # 1. 强制锁定根目录
    app_root = os.path.dirname(os.path.abspath(__file__)) #通常是 /app/app
    app = Flask(__name__, root_path=app_root)
    app.config.from_object(Config)

    # === 🔍 启动诊断 (Debug) ===
    print(f"--- [DEBUG] App Root: {app_root}")
    docs_dir = os.path.join(app_root, 'docs')
    print(f"--- [DEBUG] Looking for docs at: {docs_dir}")
    
    if os.path.exists(docs_dir):
        print(f"--- [DEBUG] 'docs' directory FOUND.")
        # 打印 docs 目录下的前几个文件，确认结构
        for root, dirs, files in os.walk(docs_dir):
            for file in files:
                if file.endswith('.yml'):
                    print(f"--- [DEBUG] Found YML: {os.path.join(root, file)}")
    else:
        print(f"!!! [ERROR] 'docs' directory NOT FOUND at {docs_dir} !!!")
        print(f"!!! [ERROR] Please check .dockerignore or docker-compose volumes !!!")
    # ============================

    # 2. Swagger 配置
    app.config['SWAGGER'] = {
        'title': 'VideoHub API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'API 文档',
        'specs_route': '/api/apidocs/', 
        'static_url_path': "/flasgger_static", 
        'swagger_ui': True,
        'specs': [
            {
                'endpoint': 'apispec_1',
                'route': '/api/apispec_1.json',
                'rule_filter': lambda rule: True,
                'model_filter': lambda tag: True,
            }
        ]
    }
    
    # 3. 强制指定 template_folder 为绝对路径
    swagger.template_folder = docs_dir
    
    db.init_app(app)
    mail.init_app(app)
    swagger.init_app(app)
    
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}}, supports_credentials=True)
    
    # 注册蓝图
    from .api.video import video_bp
    app.register_blueprint(video_bp, url_prefix='/api/video')
    
    from .api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from .api.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    from .api.recommend import recommend_bp
    app.register_blueprint(recommend_bp, url_prefix='/api/recommend')
    
    from .api.interaction import interaction_bp
    app.register_blueprint(interaction_bp, url_prefix='/api/interaction')

    from .api.playlist import playlist_bp
    app.register_blueprint(playlist_bp, url_prefix='/api/playlist')

    from .api.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    from .api.pay import pay_bp
    app.register_blueprint(pay_bp, url_prefix='/api/pay')

    @app.route('/docs')
    def redoc_docs():
        return render_template('redoc.html')
    
    with app.app_context():
        from . import models 
        db.create_all()
        
    return app