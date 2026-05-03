// 认证相关接口
import { api } from '../utils/request';

// 微信用户注册请求参数
export interface WechatUserCreate {
  code: string;
  role: 'elderly' | 'family';
  nickname?: string;
  avatar_url?: string;
  phone: string;
}

// 用户信息响应
export interface UserInfo {
  id: number;
  phone: string;
  nickname: string;
  role: string;
  gender: number;
  birthday: string | null;
  avatar_url: string | null;
  is_active: boolean;
  created_at: string;
}

// 登录响应
export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: 'elderly' | 'family';
}

// 认证相关API
export const authApi = {
  // 微信注册
  wechatRegister: (wechatData: WechatUserCreate) => {
    return api.post<UserInfo>('/auth/wechat/register', wechatData, { token: false });
  },

  // 微信登录
  wechatLogin: (code: string, role?: 'elderly' | 'family') => {
    return api.post<LoginResponse>('/auth/wechat/login', { code, role }, { token: false });
  },

  // 手机号登录
  phoneLogin: (phone: string) => {
    return api.post<LoginResponse>('/auth/phone/login', { phone }, { token: false });
  },
};
