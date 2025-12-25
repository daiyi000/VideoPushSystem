import random
from app import create_app, db
# 引入所有相关模型
from app.models import User, Video, ActionLog, Follow, Comment, Playlist, CommentLike, EmailCaptcha, playlist_video
from datetime import datetime, timedelta

app = create_app()

def seed():
    with app.app_context():
        print("正在清空旧数据...")
        
        # 1. 清理数据 (严格顺序)
        db.session.query(CommentLike).delete()
        db.session.execute(playlist_video.delete())
        
        # 解除自关联
        db.session.query(Comment).update({Comment.parent_id: None})
        db.session.commit()
        
    db.session.query(Comment).delete()
    db.session.query(Follow).delete()
        db.session.query(EmailCaptcha).delete()
        db.session.query(Video).delete()
        db.session.query(User).delete()
        
        db.session.commit()
        print("✅ 旧数据已清空")

        # 2. 生成新数据
        print("1. 生成用户 (含管理员)...")
        admin = User(username='Admin', email='admin@test.com', is_admin=True)
        admin.set_password('123456')
        db.session.add(admin)
        
        users = [admin]
        for i in range(1, 6):
            email = f'test{i}@example.com'
            u = User(username=f'User_{i}', email=email)
            u.set_password('123456')
            db.session.add(u)
            users.append(u)
        db.session.commit()
        
        print("2. 生成测试视频...")
        categories = ['科技', '生活', '娱乐', '教育', '电影', '音乐', '游戏', '体育']
        tags_pool = ['Python', 'Vue', 'Flask', 'AI', '美食', '旅行', '搞笑', 'Vlog', '教程', '编程']
        
        videos = []
        for i in range(1, 61): # 生成更多视频
            cat = random.choice(categories)
            tag_sample = ",".join(random.sample(tags_pool, 2)) 
            uploader = random.choice(users)
            
            status = random.choices([1, 0, 2], weights=[8, 1, 1])[0]
            visibility = random.choices(['public', 'private'], weights=[9, 1])[0]
            
            # 【新增】Shorts 逻辑
            # 20% 概率生成短视频 (时长<=60s)
            is_short = False
            duration = random.randint(60, 900) # 默认长视频
            
            if random.random() < 0.2:
                is_short = True
                duration = random.randint(5, 59) # 短视频时长
            
            # 使用更稳定的占位图
            cover_url = f'https://placehold.co/300x200/EEE/31343C?text=Video_{i}'
            if is_short:
                 # 竖屏封面模拟
                 cover_url = f'https://placehold.co/200x350/EEE/31343C?text=Short_{i}'

            v = Video(
                title=f'【{cat}】测试视频_{i} - {tag_sample}',
                description=f'这是一个关于 {tag_sample} 的测试视频内容简介...\n\n这里是详细说明部分。',
                url='http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4', 
                cover_url=cover_url,
                category=cat,
                tags=tag_sample,
                uploader_id=uploader.id,
                views=random.randint(100, 10000),
                duration=duration,
                is_short=is_short,
                status=status,
                visibility=visibility,
                upload_time=datetime.utcnow() - timedelta(days=random.randint(0, 60))
            )
            db.session.add(v)
            videos.append(v)
        db.session.commit()

        print("3. 生成互动数据...")
        # 关注
        for u in users:
            targets = random.sample(users, k=random.randint(0, 3))
            for target in targets:
                if u.id != target.id:
                    f = Follow(follower_id=u.id, followed_id=target.id)
                    db.session.add(f)
        
        # 观看记录 (带进度)
        for _ in range(400):
            user = random.choice(users)
            video = random.choice(videos)
            action_time = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            
            # 生成随机观看进度
            progress = 0
            if video.duration > 0:
                # 随机看了 10% 到 90%
                progress = int(video.duration * random.uniform(0.1, 0.9))
                
            log_view = ActionLog(
                user_id=user.id, 
                video_id=video.id, 
                action_type='view', 
                timestamp=action_time,
                progress=progress # 记录进度
            )
            db.session.add(log_view)
            
            if random.random() < 0.3:
                log_like = ActionLog(user_id=user.id, video_id=video.id, action_type='like', weight=3, timestamp=action_time)
                db.session.add(log_like)
            
        db.session.commit()
        print(f"✅ 数据填充完成！\n管理员账号: admin@test.com / 123456")

if __name__ == '__main__':
    seed()