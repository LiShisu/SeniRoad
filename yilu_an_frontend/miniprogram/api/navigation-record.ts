// 导航记录相关接口
import { api } from '../utils/request';

// 创建导航记录请求参数
export interface CreateNavigationRecordParams {
  user_id: number;
  device_id: number;
  start_location: string;
  end_location: string;
  start_time: string;
  status: 1 | 2 | 3; // 1-进行中, 2-完成, 3-取消
}

// 更新导航记录请求参数
export interface UpdateNavigationRecordParams {
  end_time?: string;
  status?: 1 | 2 | 3;
}

// 导航记录
export interface NavigationRecord {
  id: number;
  user_id: number;
  device_id: number;
  start_location: string;
  end_location: string;
  start_time: string;
  end_time: string | null;
  status: number;
  created_at: string;
  updated_at: string;
}

// 导航记录相关API
export const navigationRecordApi = {
  // 创建导航记录
  createRecord: (params: CreateNavigationRecordParams) => {
    return api.post<NavigationRecord>('/api/v1/navigation-records/', params);
  },
  
  // 获取导航记录列表
  getRecords: (userId: number, status?: number) => {
    return api.get<NavigationRecord[]>('/api/v1/navigation-records/', { data: { user_id: userId, status } });
  },
  
  // 获取用户的进行中导航记录
  getActiveRecords: (userId: number) => {
    return api.get<NavigationRecord[]>(`/api/v1/navigation-records/user/${userId}/active`);
  },
  
  // 获取用户的已完成导航记录
  getCompletedRecords: (userId: number, startDate?: string, endDate?: string) => {
    return api.get<NavigationRecord[]>(`/api/v1/navigation-records/user/${userId}/completed`, {
      data: { start_date: startDate, end_date: endDate }
    });
  },
  
  // 根据ID获取导航记录
  getRecordById: (recordId: number) => {
    return api.get<NavigationRecord>(`/api/v1/navigation-records/${recordId}`);
  },
  
  // 更新导航记录
  updateRecord: (recordId: number, params: UpdateNavigationRecordParams) => {
    return api.put<NavigationRecord>(`/api/v1/navigation-records/${recordId}`, params);
  },
  
  // 删除导航记录
  deleteRecord: (recordId: number) => {
    return api.delete(`/api/v1/navigation-records/${recordId}`);
  },
  
  // 完成导航记录
  completeRecord: (recordId: number) => {
    return api.patch<NavigationRecord>(`/api/v1/navigation-records/${recordId}/complete`);
  },
  
  // 取消导航记录
  cancelRecord: (recordId: number) => {
    return api.patch<NavigationRecord>(`/api/v1/navigation-records/${recordId}/cancel`);
  },
};
