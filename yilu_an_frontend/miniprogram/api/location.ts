// 位置相关接口
import { api } from '../utils/request';

// 更新实时位置请求参数
export interface UpdateLocationParams {
  latitude: number;
  longitude: number;
  address?: string;
  accuracy?: number;
}

// 位置记录
export interface Location {
  id: number;
  user_id: number;
  latitude: number;
  longitude: number;
  address: string;
  accuracy: number;
  created_at: string;
}

// 查询历史轨迹请求参数
export interface HistoryParams {
  start_time?: string;
  end_time?: string;
  limit?: number;
}

// 位置相关API
export const locationApi = {
  // 更新实时位置
  updateLocation: (params: UpdateLocationParams) => {
    return api.post<Location>('/locations/update', params);
  },
  
  // 查询历史轨迹
  getHistory: (params?: HistoryParams) => {
    return api.get<Location[]>('/locations/history', { data: params });
  },
  
  // 获取最新位置
  getLatest: () => {
    return api.get<Location>('/locations/latest');
  },
};
