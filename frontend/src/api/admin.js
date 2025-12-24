import request from './request';

// 获取大屏数据
export function getStats() { return request.get('/admin/stats'); }

// 视频管理
export function getAdminVideos(params) { return request.get('/admin/videos', { params }); }
export function auditVideo(data) { return request.post('/admin/video/audit', data); } // data: {id, status}
export function deleteVideoAdmin(id) { return request.post('/admin/video/delete', { id }); }

// 用户管理
export function getAdminUsers(q) { return request.get('/admin/users', { params: { q } }); }
export function banUser(id) { return request.post('/admin/user/ban', { id }); }

// 重置请求管理
export function getResetRequests() { return request.get('/admin/reset_requests'); }
export function sendResetEmail(id) { return request.post('/admin/send_reset_email', { id }); }