import axios from 'axios';

// 创建 axios 实例
const service = axios.create({
  // 【修改这里】把 127.0.0.1 改成 localhost
  baseURL: 'http://localhost:5000/api', 
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 (可以在这里统一加 Token，目前先留空)
service.interceptors.request.use(
  (config) => {
    // 比如：config.headers['Authorization'] = 'Bearer ' + token;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 (可以在这里统一处理错误)
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