// 绑定相关接口
import { api } from '../utils/request';

// 创建绑定关系请求参数
export interface CreateBindingParams {
  elderly_id: number;
  family_id: number;
}

// 解除绑定关系请求参数
export interface UnbindParams {
  elderly_id: number;
  family_id: number;
}

// 绑定关系
export interface Binding {
  id: number;
  elderly_id: number;
  family_id: number;
  status: string;
  created_at: string;
}

// 绑定相关API
export const bindingApi = {
  // 创建绑定关系
  createBinding: (params: CreateBindingParams) => {
    return api.post<Binding>('/api/v1/bindings/', params);
  },
  
  // 获取绑定关系列表
  getBindings: () => {
    return api.get<Binding[]>('/api/v1/bindings/');
  },
  
  // 解除绑定关系
  unbind: (params: UnbindParams) => {
    return api.post('/api/v1/bindings/unbind', params);
  },
  
  // 批准绑定请求
  approveBinding: (bindingId: number) => {
    return api.put<Binding>(`/api/v1/bindings/${bindingId}/approve`);
  },
  
  // 拒绝绑定请求
  rejectBinding: (bindingId: number) => {
    return api.put<Binding>(`/api/v1/bindings/${bindingId}/reject`);
  },
};
