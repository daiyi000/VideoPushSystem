import request from './request';

/**
 * 获取首页推荐列表
 * 场景：首页
 * 逻辑：如果有 userId，返回协同过滤推荐；否则返回热门视频
 */
export function getRecommendVideos(userId) {
  return request({
    url: '/recommend/home',
    method: 'get',
    params: { user_id: userId }
  });
}

/**
 * 获取相关视频推荐
 * 场景：视频详情页右侧
 * 逻辑：基于内容(标签/标题)的相似度推荐
 */
export function getRelatedVideos(videoId) {
  return request({
    url: `/recommend/related/${videoId}`,
    method: 'get'
  });
}