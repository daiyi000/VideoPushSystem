import os

class Config:
        
    # 你的密钥
    SECRET_KEY = '8f4b2e1d9a3c5e7b1a2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v'
    
    # 数据库连接配置
    # 请务必确保这里的 root:123456 是你正确的 MySQL 账号密码
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/video_push_db'
    
    # 关闭追踪，节省内存
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 上传文件保存路径
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app/static/uploads')


    MAIL_SERVER = 'smtp.qq.com' # QQ邮箱的SMTP服务器
    MAIL_PORT = 465             # SSL 端口
    MAIL_USE_SSL = True
    MAIL_USERNAME = '2954377102@qq.com'  # 【替换】你的邮箱账号
    MAIL_PASSWORD = 'cyhkabcuqxqjdcje'     # 【替换】你的邮箱授权码 (不是登录密码！)
    MAIL_DEFAULT_SENDER = '2954377102@qq.com' # 【替换】发送者地址