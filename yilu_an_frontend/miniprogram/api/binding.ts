// 绑定相关接口
import { api } from '../utils/request';

// 创建绑定关系请求参数
export interface CreateBindingParams {
  elderly_phone: string;
}
// 对应后端新增的 BindingUser 子资源
export interface BindingUser {
  user_id: number;
  phone: string;
  nickname: string | null;
  avatar_url: string | null;
}
// 绑定关系资源表述 (完全对标后端的 BindingResponse)
export interface Binding {
  binding_id: number;
  status: 'pending' | 'accepted' | 'rejected'; // 使用联合类型确保安全
  created_at: string;
  approved_at: string | null;
  elderly: BindingUser | null; // 嵌套对象
  family: BindingUser | null;  // 嵌套对象
}
// 解除绑定关系请求参数
export interface UnbindParams {
  elderly_phone: string;
}

// 绑定关系
// export interface Binding {
//   binding_id: number;
//   elderly_id: number;
//   elderly_nickname: string;
//   elderly_phone: string | null;
//   family_id: number;
//   family_nickname: string;
//   family_phone: string | null;
//   status: string;
//   created_at: string;
//   approved_at: string | null;
// }

// 绑定相关API
export const bindingApi = {
  // 创建绑定关系
  createBinding: (data: CreateBindingParams) => {
    return api.post<Binding>('/bindings/', data);
  },

  // 获取绑定关系列表
  getBindings: () => {
    return api.get<Binding[]>('/bindings/');
  },

  // 解除绑定关系
  // unbind: (data: UnbindParams) => {
  //   return api.delete('/bindings', {data});
  // },
// 解除绑定关系 (遵循 REST：DELETE 请求不带 Body，通过 URL 路径传 ID)
deleteBinding: (bindingId: number) => {
  return api.delete(`/bindings/${bindingId}`);
},
//   // 批准绑定请求
//   approveBinding: (bindingId: number) => {
//     return api.put<Binding>(`/bindings/${bindingId}/approve`);
//   },

//   // 拒绝绑定请求
//   rejectBinding: (bindingId: number) => {
//     return api.put<Binding>(`/bindings/${bindingId}/reject`);
//   },
  // 批准绑定请求
  approveBinding: (bindingId: number) => {
    return api.put<Binding>(`/bindings/${bindingId}`, {
      status: "accepted" 
    });
  },

  // 拒绝绑定请求
  rejectBinding: (bindingId: number) => {
    return api.put<Binding>(`/bindings/${bindingId}`, {
      status: "rejected"
    });
  },
};
