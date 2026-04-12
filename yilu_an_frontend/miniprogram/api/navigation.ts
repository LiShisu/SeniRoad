// 导航相关接口
import { api } from '../utils/request';
import { Destination } from './destination';

// 规划导航路线请求参数
export interface PlanRouteParams {
  origin: string;
  destination: string;
  priority?: 'elderly_friendly' | 'time' | 'distance';
}

// 导航路线数据
export interface NavigationRoute {
  // 具体字段根据后端返回定义
  route_id: string;
  origin: string;
  destination: string;
  distance: number;
  duration: number;
  steps: any[];
}

// 导航相关API
export const navigationApi = {
  // 规划导航路线
  planRoute: (params: PlanRouteParams) => {
    return api.post<NavigationRoute>('/api/v1/navigation/plan', params);
  },
  
  // 获取常用地点列表
  getCommonDestinations: () => {
    return api.get<Destination[]>('/api/v1/navigation/common-destinations');
  },
};
