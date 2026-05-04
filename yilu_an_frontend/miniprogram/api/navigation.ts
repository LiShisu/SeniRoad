// 导航相关接口
import { api } from '../utils/request';
import { Destination } from './destination';

// 规划导航路线请求参数
export interface PlanRouteParams {
  favorite_place_id: number;
  origin_lng: string;
  origin_lat: string;
}

// 语音导航请求参数
export interface VoiceNavigationParams {
  origin_lng: string;
  origin_lat: string;
  audio_file: any;
}

// 导航步骤
export interface NavigationStep {
  instruction: string;
  distance: string;
  duration: string;
  road: string;
  polyline: string;
}

// 地址导航路线数据
export interface AddressRouteData {
  distance: string;
  duration: string;
  steps: NavigationStep[];
  polyline: string;
  record_id: number;
}

// 地址导航响应
export interface AddressNavigationResponse {
  status: string;
  destination: string;
  place_name: string;
  route: AddressRouteData;
  latitude: string;
  longitude: string;
}

// 导航路线数据（智能导航）
export interface NavigationRouteData {
  text: string;
  origin: string;
  destination: string;
  distance: string;
  duration: string;
  steps: any[];
  polyline: string;
}

// 智能导航响应
export interface NavigationRouteResponse {
  status: string;
  destination: string;
  navigation_advice: string;
  route: NavigationRouteData;
  weather: string;
  latitude: number;
  longitude: number;
}

// 语音导航响应
export interface VoiceNavigationResponse {
  status: string;
  voice_text: string;
  destination: string;
  matched_type: string;
  navigation_advice: string;
  route: NavigationRouteData;
  weather: string;
  latitude: number;
  longitude: number;
}

// 导航相关API
export const navigationApi = {
  // 地址导航（直接调用高德地图）
  navigateByAddress: (data: PlanRouteParams) => {
    return api.post<AddressNavigationResponse>('/navigation/', data);
  },

  // 规划导航路线（智能导航）
  planRoute: (data: PlanRouteParams) => {
    return api.post<NavigationRouteResponse>('/navigation/plan', data);
  },

  // 语音导航
  navigateByVoice: (data: VoiceNavigationParams) => {
    const { audio_file, origin_lng, origin_lat } = data;
    return api.post<VoiceNavigationResponse>('/navigation/process', { audio_file }, { origin_lng, origin_lat });
  },

  // 获取常用地点列表
  getCommonDestinations: () => {
    return api.get<Destination[]>('/navigation/common-destinations');
  },
};
