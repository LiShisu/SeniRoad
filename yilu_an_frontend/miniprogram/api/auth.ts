// 认证相关接口
import { api } from '../utils/request';

// 用户注册请求参数
export interface RegisterParams {
  phone: string;
  password: string;
  nickname?: string;
  role?: 'elderly' | 'family';
  avatar_url?: string;
}

// 用户登录请求参数
export interface LoginParams {
  username: string;
  password: string;
}

// 微信用户注册请求参数
export interface WechatUserCreate {
  openid: string;
  session_key: string;
  nickname?: string;
  avatar_url?: string;
  role?: 'elderly' | 'family';
}

// 用户信息响应
export interface UserInfo {
  id: number;
  phone: string;
  nickname: string;
  role: string;
  avatar_url: string | null;
  is_active: boolean;
  created_at: string;
}

// 登录响应
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// 认证相关API
export const authApi = {
  // 用户注册
  register: (params: RegisterParams) => {
    return api.post<UserInfo>('/api/v1/auth/register', params, { token: false });
  },
  
  // 用户登录
  login: (params: LoginParams) => {
    return api.post<LoginResponse>('/api/v1/auth/login', params, { token: false });
  },
  
  // 微信注册
  wechatRegister: (wechatData: WechatUserCreate) => {
    return api.post<UserInfo>('/api/v1/auth/wechat/register', wechatData, { token: false });
  },
  
  // 微信登录
  wechatLogin: (openid: string, session_key: string) => {
    return api.post<LoginResponse>('/api/v1/auth/wechat/login', { openid, session_key }, { token: false });
  },
};
