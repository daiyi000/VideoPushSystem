import random
from app import create_app, db
from app.models import User, Video, ActionLog
from datetime import datetime, timedelta

app = create_app()

def seed():
    with app.app_context():
        print("正在清空旧数据...")
        db.session.query(ActionLog).delete()
        db.session.query(Video).delete()
        db.session.query(User).delete() 
        db.session.commit()

        print("1. 生成用户 (含管理员)...")
        # 创建管理员
        admin = User(username='Admin', email='admin@test.com', is_admin=True)
        admin.set_password('123456')
        db.session.add(admin)
        
        # 创建普通用户
        users = [admin]
        for i in range(1, 11):
            email = f'test{i}@example.com'
            u = User(username=f'User_{i}', email=email)
            u.set_password('123456')
            db.session.add(u)
            users.append(u)
        db.session.commit()
        
        print("2. 生成测试视频...")
        categories = ['科技', '生活', '娱乐', '教育', '电影']
        tags_pool = ['Python', 'Vue', 'Flask', 'AI', '美食', '旅行', '搞笑', 'Vlog']
        
        for i in range(1, 61):
            cat = random.choice(categories)
            tag_sample = ",".join(random.sample(tags_pool, 2)) 
            
            # 随机生成状态：大部分是 1(通过)，少量 0(待审核) 和 2(下架)
            status = random.choices([0, 1, 2], weights=[2, 8, 1])[0]
            
            v = Video(
                title=f'【{cat}】测试视频_{i}',
                description=f'这是一个测试视频...',
                url='http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4', 
                cover_url=f'https://via.placeholder.com/300x200?text=Video_{i}',
                category=cat,
                tags=tag_sample,
                uploader_id=random.choice(users).id,
                views=random.randint(100, 10000),
                status=status # 设置状态
            )
            db.session.add(v)
        db.session.commit()
        
        # ... (ActionLog 生成逻辑同之前，省略以节省空间) ...
        
        print("✅ 数据填充完成！管理员账号: admin@test.com / 123456")

if __name__ == '__main__':
    seed()