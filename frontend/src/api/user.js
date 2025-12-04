import request from './request';

// 登录
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  });
}

// 注册
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  });
}

// 获取个人资料
export function getProfile(userId) {
  return request({ url: `/user/profile?user_id=${userId}`, method: 'get' });
}
// 修改个人资料
export function updateProfile(data) {
  return request({ url: '/user/profile', method: 'post', data });
}
// 获取我的视频
export function getMyVideos(userId) {
  return request({ url: `/user/my_videos?user_id=${userId}`, method: 'get' });
}
// 获取收藏
export function getMyFavs(userId) {
  return request({ url: `/user/favorites?user_id=${userId}`, method: 'get' });
}
// 获取历史
export function getMyHistory(userId) {
  return request({ url: `/user/history?user_id=${userId}`, method: 'get' });
}
// 上传头像
export function uploadAvatar(formData) {
  return request({
    url: '/user/upload_avatar',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}
// 关注相关 API
export function toggleFollow(data) {
  // data: { follower_id, followed_id }
  return request({ url: '/user/follow', method: 'post', data });
}

// 获取频道页数据
export function getChannelInfo(params) {
  // params: { author_id, visitor_id, sort_by, q }
  return request({ url: '/user/channel_info', method: 'get', params });
}

export function uploadBanner(formData) {
  return request({ 
    url: '/user/upload_banner', 
    method: 'post', 
    data: formData, 
    headers: { 'Content-Type': 'multipart/form-data' } 
  });
}