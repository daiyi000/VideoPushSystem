import request from './request';

// 创建订单
export function createPayment(data) {
  return request({
    url: '/pay/create',
    method: 'post',
    data
  });
}

// 查询订单状态
export function queryOrder(data) {
  return request({
    url: '/pay/query',
    method: 'post',
    data
  });
}