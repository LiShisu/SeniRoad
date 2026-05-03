// 基础网络请求工具
import { getToken, wechatLogin } from './auth';
import { API_BASE_URL } from './config';

const BASE_URL = API_BASE_URL;



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
        // } else if (statusCode === 401) {
        //   // 检查是否是登录相关接口，如果是则直接抛出错误，避免无限循环
        //   const isAuthEndpoint = url.includes('/auth/login') ||
        //                           url.includes('/auth/register') ||
        //                           url.includes('/auth/wechat');

        //   if (isAuthEndpoint) {
        //     // 登录接口返回401，直接抛出错误
        //     const errorMessage = typeof responseData === 'object' && responseData !== null
        //       ? (responseData as any).detail || (responseData as any).message || '登录失败，请检查凭证'
        //       : '登录失败，请检查凭证';
        //     reject(new Error(errorMessage));
        //   } else {
        //     // 其他接口返回401，尝试自动重新登录
        //     wechatLogin().then(() => {
        //       // 登录成功后重新发起请求
        //       request(config).then(resolve).catch(reject);
        //     }).catch(reject);
        //   }
        } else {
          // 处理其他错误
          // 优先提取detail字段（FastAPI HTTPException格式），其次提取message字段
          const errorMessage = typeof responseData === 'object' && responseData !== null
            ? (responseData as any).detail || (responseData as any).message || `请求失败：${statusCode}`
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
//RequestConfig 是一个定义了所有请求选项（如 headers, timeout, data 等）的接口。
//Omit<RequestConfig, 'url' | 'method'> 是 TypeScript 的一个工具类型，它的作用是从 RequestConfig 类型中排除（omit）掉 url 和 method 这两个属性。
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
