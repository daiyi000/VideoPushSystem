import request from './request';

// 创建播放列表
export function createPlaylist(data) {
  return request({ url: '/playlist/create', method: 'post', data });
}

// 删除播放列表
export function deletePlaylist(id) {
  return request({ url: '/playlist/delete', method: 'post', data: { id } });
}
// 向播放列表添加视频
export function addVideoToPlaylist(data) {
  // data: { playlist_id, video_id }
  return request({ url: '/playlist/add_video', method: 'post', data });
}
// 【新增】从列表移除视频
export function removeVideoFromPlaylist(data) {
  // data: { playlist_id, video_id }
  return request({ url: '/playlist/remove_video', method: 'post', data });
}
// 获取播放列表中的视频
export function getPlaylistVideos(id) {
  return request({ url: `/playlist/videos?id=${id}`, method: 'get' });
}
// 修改信息 (重命名)
export const updatePlaylist = (data) => {
  return request.post('/playlist/update', data);
};