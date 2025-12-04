from app import create_app

app = create_app()

# --- 路由自检逻辑 (保留) ---
print("\n" + "="*30)
print("正在检查系统路由表...")
found_profile = False
for rule in app.url_map.iter_rules():
    # 只打印 api 相关的，防止刷屏
    if "/api/" in str(rule):
        print(f"检测到路由: {rule}")
    if "/api/user/profile" in str(rule):
        found_profile = True
print("="*30)
if found_profile:
    print("✅ 系统自检通过：核心路由已加载")
else:
    print("❌ 警告：未检测到 /api/user/profile，请检查 __init__.py")
print("="*30 + "\n")
# -------------------------

if __name__ == '__main__':
    # 【核心修改】threaded=True
    # 开启多线程模式。如果不加这个，视频播放时会阻塞整个服务器，
    # 导致图片、弹幕、评论等接口请求排队，从而产生“卡顿”的错觉。
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)