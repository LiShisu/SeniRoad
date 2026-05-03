// 绑定相关接口
import { api } from '../utils/request';

// 创建绑定关系请求参数
export interface CreateBindingParams {
  elderly_phone: string;
}

// 解除绑定关系请求参数
export interface UnbindParams {
  elderly_phone: string;
}

// 绑定关系
export interface Binding {
  binding_id: number;
  elderly_id: number;
  elderly_nickname: string;
  family_id: number;
  status: string;
  created_at: string;
  approved_at: string | null;
}

// 绑定相关API
export const bindingApi = {
  // 创建绑定关系
  createBinding: (data: CreateBindingParams) => {
    return api.post<Binding>('/bindings/bind', data);
  },

  // 获取绑定关系列表
  getBindings: () => {
    return api.get<Binding[]>('/bindings/');
  },

  // 解除绑定关系
  unbind: (data: UnbindParams) => {
    return api.post('/bindings/unbind', data);
  },

  // 批准绑定请求
  approveBinding: (bindingId: number) => {
    return api.put<Binding>(`/bindings/${bindingId}/approve`);
  },

  // 拒绝绑定请求
  rejectBinding: (bindingId: number) => {
    return api.put<Binding>(`/bindings/${bindingId}/reject`);
  },
};
