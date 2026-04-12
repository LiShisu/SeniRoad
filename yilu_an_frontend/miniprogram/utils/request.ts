// 基础网络请求工具
import { config } from './config';
const BASE_URL = config.api.baseUrl; // 替换为实际的API地址

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
  header?: any;
  token?: boolean;
}

// 获取token
const getToken = (): string | null => {
  return wx.getStorageSync('access_token');
};

// 保存token
const saveToken = (token: string): void => {
  wx.setStorageSync('access_token', token);
};

// 保存用户信息
const saveUserInfo = (userInfo: any): void => {
  wx.setStorageSync('userInfo', userInfo);
};

// 微信登录并获取token
const wechatLogin = async (): Promise<string> => {
  // 显示加载提示
  wx.showLoading({ title: '正在登录...' });
  
  try {
    // 1. 调用微信登录接口获取code
    const wxLoginResult = await new Promise<any>((resolve, reject) => {
      wx.login({
        success: resolve,
        fail: reject,
      });
    });

    // 2. 调用微信code2Session接口获取openid和session_key
    const code2SessionResult = await new Promise<any>((resolve, reject) => {
      wx.request({
        url: `https://api.weixin.qq.com/sns/jscode2session`,
        method: 'GET',
        data: {
          appid: config.wechat.appid,
          secret: config.wechat.secret,
          js_code: wxLoginResult.code,
          grant_type: 'authorization_code'
        },
        success: resolve,
        fail: reject
      });
    });

    // 3. 获取用户信息
    const userInfoResult = await new Promise<any>((resolve, reject) => {
      wx.getUserProfile({
        desc: '用于完善用户资料',
        success: resolve,
        fail: reject
      });
    });

    // 4. 调用后端微信登录接口
    const authApi = require('../api/auth').authApi;
    const response = await authApi.wechatLogin(code2SessionResult.openid, code2SessionResult.session_key);

    // 5. 保存token和用户信息
    saveToken(response.access_token);
    saveUserInfo({
      ...userInfoResult.userInfo,
      openid: code2SessionResult.openid
    });

    // 6. 隐藏加载提示
    wx.hideLoading();
    wx.showToast({ title: '登录成功', icon: 'success' });

    return response.access_token;
  } catch (error) {
    // 隐藏加载提示
    wx.hideLoading();
    wx.showToast({ title: '登录失败', icon: 'none' });
    throw error;
  }
};

// 网络请求函数
export const request = async <T = any>(config: RequestConfig): Promise<T> => {
  const { url, method, data, header = {}, token = true } = config;
  
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
  
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header: headers,
      success: (res) => {
        const { statusCode, data: responseData } = res;
        
        if (statusCode >= 200 && statusCode < 300) {
          resolve(responseData as T);
        } else if (statusCode === 401) {
          // 未登录状态，触发自动登录
          wechatLogin().then(() => {
            // 登录成功后重新发起请求
            request(config).then(resolve).catch(reject);
          }).catch(reject);
        } else {
          // 处理其他错误
          const errorMessage = typeof responseData === 'object' && responseData !== null 
            ? (responseData as any).message 
            : `请求失败：${statusCode}`;
          reject(new Error(errorMessage));
        }
      },
      fail: (err) => {
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
  post: <T = any>(url: string, data?: any, config?: Omit<RequestConfig, 'url' | 'method' | 'data'>) => {
    return request<T>({ ...config, url, method: 'POST', data });
  },
  put: <T = any>(url: string, data?: any, config?: Omit<RequestConfig, 'url' | 'method' | 'data'>) => {
    return request<T>({ ...config, url, method: 'PUT', data });
  },
  delete: <T = any>(url: string, config?: Omit<RequestConfig, 'url' | 'method'>) => {
    return request<T>({ ...config, url, method: 'DELETE' });
  },
  patch: <T = any>(url: string, data?: any, config?: Omit<RequestConfig, 'url' | 'method' | 'data'>) => {
    return request<T>({ ...config, url, method: 'PUT', data });
  },
};
