import axios from 'axios';

// 创建 axios 实例
const service = axios.create({
  // 确保这里的地址和你的后端地址一致
  baseURL: '/api', 
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 【核心修复】请求拦截器：每次请求前自动携带 Token
service.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token (登录时存进去的)
    const token = localStorage.getItem('token');
    if (token) {
      // 按照标准格式添加 Authorization 头
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 (可选，用于全局处理错误)
service.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('请求出错:', error);
    return Promise.reject(error);
  }
);

export default service;