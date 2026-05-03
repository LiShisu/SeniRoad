// 用户相关接口
import { api } from '../utils/request';
import { UserInfo } from './auth';

// 更新用户信息请求参数
export interface UpdateUserParams {
  nickname?: string;
  avatar_url?: string;
  gender?: 0 | 1 | 9;
  birthday?: string;
  phone?: string;
}

// 绑定关系
export interface Binding {
  id: number;
  phone: string;
  nickname: string;
}

// 绑定关系响应
export interface BindingsResponse {
  elderly_bindings: Binding[];
  family_bindings: Binding[];
}

// 用户相关API
export const userApi = {
  // 获取当前用户信息
  getProfile: () => {
    return api.get<UserInfo>('/users/profile');
  },
  
  // 更新用户信息
  updateProfile: (params: UpdateUserParams) => {
    return api.put<UserInfo>('/users/profile', params);
  },
  
  // 获取用户的绑定关系
  getBindings: () => {
    return api.get<BindingsResponse>('/users/bindings');
  },
};
