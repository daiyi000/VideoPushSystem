import torch
import numpy as np
import pickle
import os

# 复用模型结构定义 (实际应拆分到 common 文件，这里简化)
# 这里的 Item 数量和维度需要和训练时一致
class SimpleUserTower(torch.nn.Module):
    def __init__(self, num_items, embed_dim, pretrained_embeddings):
        super().__init__()
        # 加载预训练的 item embedding，用于 encoding 用户历史
        # freeze=True 表示这部分在推理时不更新
        self.item_embedding = torch.nn.Embedding.from_pretrained(
            torch.FloatTensor(pretrained_embeddings), freeze=True, padding_idx=0
        )
    
    def forward(self, history_tensor):
        # history_tensor: [1, seq_len]
        seq_emb = self.item_embedding(history_tensor)
        # 计算 mask 以忽略 padding 的影响
        mask = (history_tensor != 0).unsqueeze(-1).float()
        sum_emb = (seq_emb * mask).sum(dim=1)
        count = mask.sum(dim=1).clamp(min=1) # clamp 避免除以 0
        return sum_emb / count # [1, dim]

class RecallService:
    def __init__(self):
        # 路径相对于 backend/ 目录
        self.model_path = "./app/services/model_data/recall_data.pkl"
        self.loaded = False
        self.item_vectors = None
        self.item2id = None
        self.id2item = None
        self.user_tower = None
        
    def load_model(self):
        """在 Flask app 启动时加载模型和数据"""
        if not os.path.exists(self.model_path):
            print(f"Warning: Model file not found at {self.model_path}. Recall service will not work.")
            print("Please run 'python train_two_tower.py' first.")
            return

        with open(self.model_path, 'rb') as f:
            data = pickle.load(f)
            
        self.item_vectors = data['item_embeddings'] # numpy array [n_items, dim]
        self.item2id = data['item2id_map']
        self.id2item = data['id2item_map']
        embed_dim = data['embedding_dim']
        
        # 初始化只包含 User Tower 部分的推理模型
        self.user_tower = SimpleUserTower(
            len(self.item_vectors), embed_dim, self.item_vectors
        )
        self.user_tower.eval() # 设置为评估模式
        self.loaded = True
        print("Recall model loaded successfully.")

    def get_candidates(self, history_video_ids, top_k=20):
        """
        输入: 用户看过的 MySQL Video ID 列表 (int)
        输出: 推荐的 MySQL Video ID 列表 (int)
        """
        if not self.loaded:
            return []
            
        # 1. 将 Video ID 转换为模型内的 index (MovieLens ID)
        model_indices = [self.item2id.get(int(vid), 0) for vid in history_video_ids]
        
        # 2. 截断或填充序列
        seq_len = 20
        padded_indices = model_indices[-seq_len:]
        if len(padded_indices) < seq_len:
            padded_indices = [0] * (seq_len - len(padded_indices)) + padded_indices
            
        input_tensor = torch.tensor([padded_indices], dtype=torch.long)
        
        # 3. 生成 User Embedding
        with torch.no_grad():
            user_vec = self.user_tower(input_tensor).numpy() # [1, dim]
            
        # 4. 暴力检索 (Dot Product)
        # item_vectors: [n_items, dim], user_vec: [1, dim]
        scores = np.dot(self.item_vectors, user_vec.T).flatten() # [n_items]
        
        # 获取 TopK 的索引
        # argsort 是从小到大，取最后 k 个并反转得到从大到小的索引
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        # 5. 将模型索引转回 Video ID
        recommend_ids = []
        for idx in top_indices:
            if idx == 0: continue # 跳过 padding
            real_id = self.id2item.get(idx)
            if real_id:
                # 确保返回的是 Python 的 int 类型
                recommend_ids.append(int(real_id))
                
        return recommend_ids

# 创建一个全局单例
recall_service = RecallService()
