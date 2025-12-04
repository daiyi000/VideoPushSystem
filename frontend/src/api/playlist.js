import request from './request';

// 创建播放列表
export function createPlaylist(data) {
  return request({ url: '/playlist/create', method: 'post', data });
}

// 删除播放列表
export function deletePlaylist(id) {
  return request({ url: '/playlist/delete', method: 'post', data: { id } });
}

export function addVideoToPlaylist(data) {
  // data: { playlist_id, video_id }
  return request({ url: '/playlist/add_video', method: 'post', data });
}

export function getPlaylistVideos(id) {
  return request({ url: `/playlist/videos?id=${id}`, method: 'get' });
}