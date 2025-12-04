import pandas as pd
import random # 【新增】
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..models import Video, ActionLog, db

class RecommendationEngine:
    
    # 场景1：冷启动 & 游客 (随机热门)
    def get_hot_videos(self, limit=20): # limit 稍微改大点
        # 获取更多视频然后打乱，制造随机感
        videos = Video.query.order_by(Video.views.desc()).limit(limit * 2).all()
        random.shuffle(videos) # 【核心】随机打乱
        return [v.to_dict() for v in videos[:limit]]

    # 场景2：首页个性化推荐
    def recommend_by_history(self, user_id, limit=20):
        logs = ActionLog.query.all()
        if not logs: return self.get_hot_videos(limit)

        data = [{'user_id': log.user_id, 'video_id': log.video_id, 'weight': log.weight} for log in logs]
        df = pd.DataFrame(data)

        if user_id not in df['user_id'].values:
            return self.get_hot_videos(limit)

        user_item_matrix = df.pivot_table(index='user_id', columns='video_id', values='weight', fill_value=0)
        
        # 简单的余弦相似度
        if user_item_matrix.shape[1] < 2: # 视频太少算不了相似度
             return self.get_hot_videos(limit)

        item_similarity = cosine_similarity(user_item_matrix.T)
        item_sim_df = pd.DataFrame(item_similarity, index=user_item_matrix.columns, columns=user_item_matrix.columns)

        user_history = df[df['user_id'] == user_id]
        watched_videos = user_history['video_id'].tolist()

        score_series = pd.Series(dtype=float)
        for video_id in watched_videos:
            if video_id in item_sim_df.index:
                similar_videos = item_sim_df[video_id] 
                score_series = score_series.add(similar_videos, fill_value=0)

        score_series = score_series.drop(watched_videos, errors='ignore')
        recommended_ids = score_series.sort_values(ascending=False).head(limit * 2).index.tolist() # 取多一点

        result_videos = []
        for vid in recommended_ids:
            v = Video.query.get(vid)
            if v: result_videos.append(v.to_dict())
            
        # 补齐
        if len(result_videos) < limit:
            hots = self.get_hot_videos(limit - len(result_videos))
            existing_ids = [v['id'] for v in result_videos]
            for h in hots:
                if h['id'] not in existing_ids:
                    result_videos.append(h)
        
        # 【核心】最后再打乱一次顺序，保证每次刷新都不一样
        random.shuffle(result_videos)
        return result_videos[:limit]

    # 场景3：详情页相关推荐 (内容相似)
    def recommend_similar_content(self, video_id, limit=10):
        all_videos = Video.query.all()
        if not all_videos: return []
        
        video_ids = [v.id for v in all_videos]
        corpus = [v.tags.replace(',', ' ') if v.tags else "" for v in all_videos]
        
        try:
            target_index = video_ids.index(video_id)
        except ValueError:
            return [] 

        cv = CountVectorizer()
        try:
            tfidf_matrix = cv.fit_transform(corpus)
        except ValueError:
            return []

        cosine_sim = cosine_similarity(tfidf_matrix[target_index], tfidf_matrix)
        similarity_scores = list(enumerate(cosine_sim[0]))
        sorted_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        recommend_res = []
        count = 0
        for idx, score in sorted_scores:
            if idx == target_index: continue
            if count >= limit: break
            v_obj = all_videos[idx]
            recommend_res.append(v_obj.to_dict())
            count += 1
            
        return recommend_res

recommender = RecommendationEngine()