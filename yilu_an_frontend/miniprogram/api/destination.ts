// 目的地相关接口
import { api } from '../utils/request';

// 创建目的地请求参数
export interface CreateDestinationParams {
  name: string;
  address: string;
  latitude?: number;
  longitude?: number;
  is_common?: boolean;
}

// 目的地
export interface Destination {
  id: number;
  user_id: number;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  is_common: boolean;
  created_at: string;
}

// 目的地相关API
export const destinationApi = {
  // 获取目的地列表
  getDestinations: () => {
    return api.get<Destination[]>('/api/v1/destinations/');
  },
  
  // 创建目的地
  createDestination: (params: CreateDestinationParams) => {
    return api.post<Destination>('/api/v1/destinations/', params);
  },
};
