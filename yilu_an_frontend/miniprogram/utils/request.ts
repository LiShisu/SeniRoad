// 基础网络请求工具
import { getToken, removeToken } from './auth';
import { API_BASE_URL } from './config';

const BASE_URL = API_BASE_URL;

// 构建查询参数
const buildQueryParams = (params: Record<string, any>): string => {
  const query = Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
  return query ? `?${query}` : '';
};

// 响应数据类型
export interface ApiResponse<T = any> {
  data: T;
  code: number;
  message: string;
}

// 请求配置类型
export interface RequestConfig {
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'OPTIONS' | 'HEAD' | 'TRACE' | 'CONNECT';
  data?: any;
  params?: any;
  header?: any;
  token?: boolean;
  responseType?: 'text' | 'arraybuffer';
}

// 网络请求函数
export const request = async <T = any>(config: RequestConfig): Promise<T> => {
  const { url, method, data, params, header = {}, token = true, responseType = 'text' } = config;
  
  // 构建请求头
  const headers = {
    'Content-Type': 'application/json',
    ...header,
  };
  
  // 如果需要token，添加Authorization头
  if (token) {
    const accessToken = getToken();
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }
  }
  
  // 构建最终URL（处理params）
  let finalUrl = url;
  if (params) {
    console.log('request params:', params);
    const queryString = buildQueryParams(params);
    console.log('queryString:', queryString);
    finalUrl = `${url}${queryString}`;
  }
  console.log('finalUrl:', finalUrl);
  // 因为微信小程序的 API 设计早于 Promise 普及，所以必须手动包装才能用现代异步语法
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${finalUrl}`,
      method,
      data,
      header: headers,
      responseType,
      success: (res) => {
        const { statusCode, data: rawData } = res;
        
        if (statusCode === 401) {
          removeToken();
          wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
          wx.reLaunch({
            url: '/common/login/login',
          });
          reject(new Error('登录已过期，请重新登录'));
          return;
        } 
        
        // 二进制响应直接返回原始数据
        if (responseType === 'arraybuffer') {
          if (statusCode >= 200 && statusCode < 300) {
            resolve(rawData as T);
          } else {
            wx.showToast({ title: `服务器请求失败 (${statusCode})`, icon: 'none' });
            reject(new Error(`服务器请求失败 (${statusCode})`));
          }
          return;
        }
        
        const responseData = rawData as any;
        // 2. 处理 HTTP 正常的请求 (200-299)
        if (statusCode >= 200 && statusCode < 300 && responseData?.code === 200) {
          resolve(responseData.data);
        } else {
          // 3. 处理 HTTP 层面的其他错误 (如 404, 500)
          const errorMsg = responseData?.message || `服务器请求失败 (${statusCode})`;
          // 统一弹出后端精心准备的错误提示
          wx.showToast({ title: errorMsg, icon: 'none' });
          reject(new Error(errorMsg));
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络请求失败', icon: 'none' });
        reject(new Error(`网络请求失败：${err.errMsg}`));
      },
      complete: () => {
        // 可以在这里添加加载状态管理
      },
    });
  });
};

// 便捷方法
export const api = {
  get: <T = any>(url: string, config?: Omit<RequestConfig, 'url' | 'method'>) => {
    return request<T>({ ...config, url, method: 'GET' });
  },
  post: <T = any>(url: string, data?: any, params?: any, config?: Omit<RequestConfig, 'url' | 'method' | 'data' | 'params'>) => {
    return request<T>({ ...config, url, method: 'POST', data, params });
  },
  put: <T = any>(url: string, data?: any, params?: any, config?: Omit<RequestConfig, 'url' | 'method' | 'data' | 'params'>) => {
    return request<T>({ ...config, url, method: 'PUT', data, params });
  },
  delete: <T = any>(url: string, config?: Omit<RequestConfig, 'url' | 'method'>) => {
    return request<T>({ ...config, url, method: 'DELETE' });
  }
};
