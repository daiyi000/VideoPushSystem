import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
        
    # 密钥
    SECRET_KEY = '8f4b2e1d9a3c5e7b1a2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v'
    
    # 数据库连接配置
    db_host = os.getenv('DB_HOST', 'localhost')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:123456@{db_host}/video_push_db'
    
    
    # 关闭追踪，节省内存
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 上传文件保存路径
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app/static/uploads')


    MAIL_SERVER = 'smtp.qq.com' # QQ邮箱的SMTP服务器
    MAIL_PORT = 465             # SSL 端口
    MAIL_USE_SSL = True
    MAIL_USERNAME = '2954377102@qq.com'  # 邮箱账号
    MAIL_PASSWORD = 'cyhkabcuqxqjdcje'     # 邮箱授权码
    MAIL_DEFAULT_SENDER = '2954377102@qq.com' # 发送者地址

    # 支付宝沙盒配置
    ALIPAY_APPID = os.getenv("ALIPAY_APPID")
    ALIPAY_DEBUG = True
    site_domain = os.getenv('SITE_DOMAIN', 'http://localhost:5173')
    
    ALIPAY_RETURN_URL = f"{site_domain}/pay/result"
    
    ALIPAY_NOTIFY_URL = "https://pay.aeasywink.top/api/pay/notify" 

    # 读取私钥
    ALIPAY_PRIVATE_KEY_STRING = os.getenv("ALIPAY_PRIVATE_KEY")
    
    # 读取公钥
    ALIPAY_PUBLIC_KEY_STRING = os.getenv("ALIPAY_PUBLIC_KEY")