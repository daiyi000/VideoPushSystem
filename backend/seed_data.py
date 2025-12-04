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
        # 注意：这里不删用户，以免把你刚才注册的账号删了
        # db.session.query(User).delete() 
        db.session.commit()

        print("1. 生成虚拟用户...")
        users = []
        for i in range(1, 11):
            # 确保邮箱唯一
            email = f'test{i}@example.com'
            u = User.query.filter_by(email=email).first()
            if not u:
                # 用户名和邮箱都必须有
                u = User(username=f'test_user_{i}', email=email)
                u.set_password('123456')
                db.session.add(u)
            users.append(u)
        db.session.commit()
        
        # 获取所有用户
        users = User.query.all()
        if not users:
            print("❌ 错误：没有用户，无法生成视频。请先注册一个用户或检查数据库。")
            return

        print("2. 生成测试视频...")
        categories = ['科技', '生活', '娱乐', '教育', '电影']
        tags_pool = ['Python', 'Vue', 'Flask', 'AI', '美食', '旅行', '搞笑', 'Vlog', '教程', '音乐']
        
        videos = []
        for i in range(1, 51):
            cat = random.choice(categories)
            tag_sample = ",".join(random.sample(tags_pool, 2)) 
            
            v = Video(
                title=f'【{cat}】测试视频_{i} - {tag_sample}',
                description=f'这是一个关于 {tag_sample} 的测试视频...',
                # 使用一个稳定的国内可访问视频源，或者保留之前的
                url='http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4', 
                cover_url=f'https://via.placeholder.com/300x200?text=Video_{i}',
                category=cat,
                tags=tag_sample,
                uploader_id=users[0].id, # 默认都给第1个用户
                views=random.randint(100, 10000)
            )
            db.session.add(v)
            videos.append(v)
        db.session.commit()
        videos = Video.query.all()

        print("3. 生成用户行为数据...")
        for _ in range(500):
            user = random.choice(users)
            video = random.choice(videos)
            action_type = random.choice(['view', 'view', 'favorite', 'like']) 
            weight = 1
            if action_type == 'like': weight = 3
            if action_type == 'favorite': weight = 5
            
            log = ActionLog(
                user_id=user.id,
                video_id=video.id,
                action_type=action_type,
                weight=weight,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(log)
        
        db.session.commit()
        print("✅ 数据填充完成！")

if __name__ == '__main__':
    seed()

