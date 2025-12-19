# backend/run.py
from flask import render_template  # <--- 必须导入这个，否则无法显示文档页面
from app import create_app

# 创建 Flask 应用实例
app = create_app()

# --- 【关键修改 1】测试路由 ---
# 同时监听 '/' 和 '/api/'
@app.route('/')
@app.route('/api/')
def hello():
    return "恭喜！内网穿透成功，后端正在运行！(路径检测正常)"

# --- 【关键修改 2】文档路由 (解决 404 问题) ---
# 我们把文档路径改到 /api/docs，这样 Nginx 才会放行。
# 注意：函数名改成了 'video_sys_docs'，防止和 __init__.py 里的 'redoc_docs' 冲突报错。
@app.route('/api/docs')
def video_sys_docs():
    return render_template('redoc.html')

# --- 路由自检逻辑 (保留) ---
# 这段代码会在启动时打印所有注册的 API 路由，方便你排查 404 问题
print("\n" + "="*30)
print("正在检查系统路由表...")
found_profile = False
found_docs = False

# app.url_map.iter_rules() 获取所有路由规则
for rule in app.url_map.iter_rules():
    rule_str = str(rule)
    # 只打印 api 相关的，防止刷屏
    if "/api/" in rule_str:
        print(f"检测到路由: {rule_str}")
    
    # 特别检查用户信息接口
    if "/api/user/profile" in rule_str:
        found_profile = True
    
    # 检查文档接口
    if "/api/docs" in rule_str:
        found_docs = True

print("="*30)

if found_profile:
    print("✅ 核心接口检测通过：/api/user/profile 已加载")
else:
    print("❌ 警告：未检测到 /api/user/profile")

if found_docs:
    print("✅ 文档接口检测通过：/api/docs 已加载 (可通过 https://pay.aeasywink.top/api/docs 访问)")
else:
    print("❌ 警告：未检测到 /api/docs")

print("="*30 + "\n")
# -------------------------

if __name__ == '__main__':
    # 【核心配置】
    # host='0.0.0.0': 必须这样写，否则 Docker 外部（如 Nginx）连不上后端
    # threaded=True : 开启多线程模式，防止视频播放卡顿
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)