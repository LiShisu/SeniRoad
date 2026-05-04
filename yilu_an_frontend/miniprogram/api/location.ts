// 位置相关接口
import { api } from '../utils/request';

// 创建位置记录请求参数
export interface CreateLocationParams {
  latitude: number;
  longitude: number;
  address?: string;
  accuracy?: number;
  record_id?: number;
}

// 查询历史轨迹请求参数
export interface HistoryParams {
  user_id?: number;
  start_time?: string;
  end_time?: string;
  limit?: number;
}

// 获取最新位置请求参数
export interface LatestParams {
  user_id?: number;
}

// 删除旧位置记录请求参数
export interface DeleteOldParams {
  days?: number;
}

// 位置记录
export interface Location {
  location_id: number;
  user_id: number;
  record_id: number;
  latitude: number;
  longitude: number;
  address: string;
  accuracy: number;
  created_at: string;
}


// 位置相关API
export const locationApi = {
  // 创建位置记录
  createLocation: (data: CreateLocationParams) => {
    return api.post<Location>('/locations/', data);
  },

  // 获取位置历史
  getHistory: (params?: HistoryParams) => {
    return api.get<Location[]>('/locations/history', { params });
  },

  // 获取最新位置
  getLatest: (params?: LatestParams) => {
    return api.get<Location>('/locations/latest', { params });
  },

  // 通过记录ID获取位置列表
  getByRecord: (recordId: number) => {
    return api.get<Location[]>(`/locations/record/${recordId}`);
  },

  // 获取单个位置详情
  getById: (locationId: number) => {
    return api.get<Location>(`/locations/${locationId}`);
  },

  // 删除旧位置记录
  deleteOld: (userId: number, params?: DeleteOldParams) => {
    return api.delete<{ deleted_count: number }>(`/locations/user/${userId}/old`, { params });
  },
};
