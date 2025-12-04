import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUserStore = defineStore('user', () => {
  // 从本地缓存读取 token，防止刷新丢失
  const token = ref(localStorage.getItem('token') || '');
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'));

  // 登录动作
  function setLoginState(newToken, user) {
    token.value = newToken;
    userInfo.value = user;
    localStorage.setItem('token', newToken);
    localStorage.setItem('userInfo', JSON.stringify(user));
  }

  // 登出动作
  function logout() {
    token.value = '';
    userInfo.value = {};
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
  }

  return { token, userInfo, setLoginState, logout };
});