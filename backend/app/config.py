import os

class Config:
        
    # 密钥
    SECRET_KEY = '8f4b2e1d9a3c5e7b1a2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v'
    
    # 数据库连接配置
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/video_push_db'
    
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
    ALIPAY_APPID = "9021000158639799"
    ALIPAY_DEBUG = True  # 开启沙盒模式
    
    # 支付成功后的前端跳转地址 (支付完跳回这里)
    ALIPAY_RETURN_URL = "http://localhost:5173/pay/result" 
    
    # 【重要】支付宝异步回调地址 (必须是公网可访问的地址)
    # 启动内网穿透后，实际获取的域名
    ALIPAY_NOTIFY_URL = "https://pay.aeasywink.top/api/pay/notify"

    # 应用私钥 (你提供的非Java语言私钥)
    ALIPAY_PRIVATE_KEY_STRING = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEApazmpt0TsQBtAFRUOmSXdfWCSVjywCytntUnkx2zSWJ8I9+C
T+xwzxbSECd0KUqKqupEaI57Ubo/e5y52oACQFPInlmE5HSwvKnid6oC+F12mSdO
RiwEcANk9KQ86ozksn6Si6E93AII0NXVTjB/cVb8vuZLUXmUXXecTeeLp4HZJcYU
lkGvZWLjgYinxps9np4AsCfWiVChWClKR4STsuL41qhtIGjp5zLTrL5YULWQpeml
tRYNj5GY7HqhQGHe/JgNaVNlGsDrWbOHk3cMO6A+frOMzHJAfPqWCUN4ja9NJW00
+fSybEiUJnYuktJJZD7+PM4CZXGzHvCSNlglmQIDAQABAoIBAAFmhsSeVc5HPKSm
Edg0hXs/ygworlSljAotrxn1RFC4fmgnOYjHbOSzQq9URg0bTjTHqjBgE/bK5kJ7
Pq70KhC1JJsCEreDrQLLRNjSHRhQYfJFfMnnEVqJDM9sm/83la9UlpSLlmRHuB9b
z2PL0Sf6HkTW2YgkyPZJTo7yCCIwWUgIqShHPuPQA/6xLnM3aN+V+InGrwPF6ZcX
XgSxDnGCdKyOI9emNIbQ8Rq0yp6lzPO8PqadYiCqwW50ZHXuE1fgNG4QHUQ7g7X8
3QlFPPIUMOyfhNcqDTIe3zVp8WCP+i04O5N1KNtXLUp88Y2FHhNiKYas6J0TcZv7
fyOeV+kCgYEA8u6NYa+YhZciLa+KF+hDt0CEVX25WdrmHeoEalXeawpwAahU/DoF
zsdRgQi9zist9gcwFQaWp8fLIKl3VCrj0DswpnaXi21Y4sNjXiBuhhjndSv16JPi
a8kB6sFqZpskDJbjPlrso7abW742KNVSmBervsSiIDu+yWOo627Vn9sCgYEArpZw
hhsnPLmAkXMvBCHfVsYks6Gxllj2XCaKBc71HU5jK2R6ErrtpyEMy98ywdtmhKdp
6BURE4Eg/qJJHc0ocaqCD/NoDx64dsumj/jp7Qk+VH/SOLMRDP+5NcbajY4bFX22
4YIKr0mH9gVA7X9EuzvUcemlR9SlqGEfZKWN1JsCgYBvFNODGnbkhwHy3/SGEAd+
sLqSGOX7B1P307znHpKQYXpr15vcpW9oaM2E8glQT4A5onnC83tKBtqD+dl9nAsF
eTs6srmC4KInNm6maLABEzwq4MoV6iE7ZfNBc+WCO2hVdV09cvgHuAT8A1LigwC8
WP6IQYNct9T6Y16nIMv/xwKBgHO6QSiEA0Rban//rCC/Gz535Yg1HHSez99RpJgp
EY21kkMHPWwBANuSKttRPmIGPzSbjLZMkJ8vL2HazUC156NA9SoBnO643GnSoLw6
sUVwpSJ6AC2ZdSn6sRiWkfTXR9i9FmbxPofm4/sOjHVhsXuzMyW3TNoKeSzeBGNA
4n0VAoGACPFa+4Obmhw972zvWrYFzy02ThjggkZJhXyX1DrebxjBTp+dAb0AjSup
tbPYOLahDdM2Da6mgQRuj1iEOaje7+P0ncNVNrwgvCkaP2HDwWylujl0dOUOTvFY
6SUBPjHVudAUlKV/jvbWPjuIxLvogVHGMi9VBsbhs9vNPsTBPpM=
-----END RSA PRIVATE KEY-----"""

    # 支付宝公钥 
    ALIPAY_PUBLIC_KEY_STRING = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAgEgYuVBJUSs+CHGJIgzy
54tEfSJ9devZkfjPdySYqqMgxcVanmo7+Qto3vEKFRCQgmVrbR2AIJX+PxdOy+Cv
MoJE3+JDg33SjOf2MZaf9N8JzRBgCm4THTJvWQokL/WAWwTWfJZ/39cvOmKiyMLW
f1xhZZMmjQUyN3PLXxXKC4kuJYVuglTfgiz+lJX5/din8zxi33hnLQFjbBNf09Oa
g4cutQ88ONyMXdIFBz90qDdQmnH8YWPvrRGZR+FdJQIW9wZ34xppbKDHrtTrAnfm
gKunbmHHchr8lORUgG4Q9kyNJc6NH80p89XY1bVqSc91zXbRykJpCt7odLew/72Q
HQIDAQAB
-----END PUBLIC KEY-----"""