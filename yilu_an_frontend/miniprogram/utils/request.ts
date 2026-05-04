// 基础网络请求工具
import { getToken, wechatLogin } from './auth';
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
}

// 网络请求函数
export const request = async <T = any>(config: RequestConfig): Promise<T> => {
  const { url, method, data, params, header = {}, token = true } = config;
  
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
    const queryString = buildQueryParams(params);
    finalUrl = `${url}${queryString}`;
  }
  
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${finalUrl}`,
      method,
      data,
      header: headers,
      success: (res) => {
        const { statusCode, data: responseData } = res;
        
        if (statusCode >= 200 && statusCode < 300) {
          resolve(responseData as T);
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
  },
  // patch: <T = any>(url: string, data?: any, params?: any, config?: Omit<RequestConfig, 'url' | 'method' | 'data' | 'params'>) => {
  //   return request<T>({ ...config, url, method: 'PATCH', data, params });
  // },
};
