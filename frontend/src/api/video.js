import request from './request';

// 获取列表
export function getVideoList(params) {
  return request({
    url: '/video/list',
    method: 'get',
    params // 包含 category, q
  });
}

// 获取详情
export function getVideoDetail(id) {
  return request({
    url: `/video/${id}`,
    method: 'get'
  });
}

// 上传视频 (注意要设置 Content-Type)
export function uploadVideo(formData) {
  return request({
    url: '/video/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

// 删除视频
export function deleteVideo(videoId) {
  return request({ url: `/video/delete/${videoId}`, method: 'delete' });
}

// 提交交互 (收藏/观看)
export function postAction(data) {
  // data: { user_id, video_id, type: 'view'/'favorite'/'unfavorite' }
  return request({ url: '/video/action', method: 'post', data });
}

// 检查收藏状态
export function checkFavStatus(userId, videoId) {
  return request({ 
    url: `/video/check_fav`, 
    method: 'get', 
    params: { user_id: userId, video_id: videoId } 
  });
}