// 导航相关接口
import { api } from '../utils/request';
import { getToken } from '../utils/auth';
import { createSSEStream, SSEEventType } from '../utils/sse';
import { API_BASE_URL } from '../utils/config';
const BASE_URL=API_BASE_URL
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
  record_id: number;
  text: string;
  origin: string;
  destination: string;
  distance: string;
  duration: string;
  steps: NavigationStep[];
  polyline: string;
}

// 智能导航响应
export interface NavigationRouteResponse {
  status: string;
  destination: string;
  place_name: string;
  navigation_advice: string;
  route: NavigationRouteData;
  weather: string;
  latitude: number;
  longitude: number;
}



// SSE 完整响应
export interface SSEPlanResponse {
  destination?: string;
  place_name?: string;
  route?: NavigationRouteData;
  weather?: string;
  navigation_advice?: string;
  latitude?: number;
  longitude?: number;
}

// 语音导航响应
export interface VoiceNavigationResponse {
  status: string;
  voice_text: string;
  record_id: number;
  destination: string;
  matched_type: string;
  navigation_advice: string;
  route: NavigationRouteData;
  weather: string;
  latitude: number;
  longitude: number;
}
export interface CoordinateNavigationParams {
  origin_lng: string;
  origin_lat: string;
  dest_lng: string;
  dest_lat: string;
}
const extractSseEvent = (eventName: string, rawText: string) => {
  // 使用 [\s\S]*? 替代 .*? 完美解决 JSON 中带换行符的问题
  const regex = new RegExp(`event: ${eventName}\\s+data: (\\{[\\s\\S]*?\\})(?:\\n\\n|$)`);
  const match = rawText.match(regex);
  if (match && match[1]) {
    try {
      return JSON.parse(match[1]);
    } catch (e) {
      console.error(`JSON解析失败 (${eventName}):`, e);
    }
  }
  return null;
};
// 导航相关API
export const navigationApi = {
  // 地址导航（直接调用高德地图）
  navigateByAddress: (data: PlanRouteParams) => {
    return api.post<AddressNavigationResponse>('/navigation/routes/standard', data);
  },

  // 规划导航路线（智能导航）
  planRoute: (data: PlanRouteParams) => {
    return api.post<NavigationRouteResponse>('/navigation/routes/smart', data);
  },
    navigateByVoice: (data: { audio_file: string, origin_lng: string, origin_lat: string }): Promise<any> => {
      return new Promise((resolve, reject) => {
        const { audio_file, origin_lng, origin_lat } = data;
        const token = wx.getStorageSync('access_token') || wx.getStorageSync('token'); 
  
        wx.uploadFile({
          url: `${BASE_URL}/navigation/routes/voice/stream`, 
          filePath: audio_file,
          name: 'audio_file', 
          timeout: 120000, // 120秒防中断
          formData: { origin_lng, origin_lat },
          header: { 'Authorization': `Bearer ${token}` },
          success: (res) => {
            const statusCode = res.statusCode;
            if (statusCode >= 200 && statusCode < 300) {
              const rawData = res.data; 
              // 1. 判断是否包含后端报错事件
              if (rawData.includes('event: error')) {
                const errMatch = extractSseEvent('error', rawData);
                const errMsg = errMatch?.error || '抱歉，没听清您想去哪';
                reject(new Error(errMsg));
                return;
              }
              // 2. 依次提取四大模块数据
              const destInfo = extractSseEvent('destination', rawData);
              const routeInfo = extractSseEvent('route', rawData);
              const weatherInfo = extractSseEvent('weather', rawData);
              const adviceInfo = extractSseEvent('advice', rawData);
              // 3. 将干净的 JSON 对象一次性返回给页面
              resolve({ destInfo, routeInfo, weatherInfo, adviceInfo });
            } else {
              reject(new Error(`服务器请求失败 (${statusCode})`));
            }
          },
          fail: (err) => {
            reject(new Error('网络请求失败，请检查网络'));
          }
        });
      });
    },
  // 流式规划导航路线（SSE）
  // planRouteStream: (
  //   data: PlanRouteParams,
  //   onEvent: (event: SSEEventType, data: any) => void,
  //   onComplete: (result: SSEPlanResponse) => void,
  //   onError: (error: any) => void
  // ) => {
  //   const token = getToken();
  //   return createSSEStream<SSEPlanResponse>(
  //     {
  //       url: `${BASE_URL}/navigation/routes/smart/stream`,
  //       method: 'POST',
  //       data: data,
  //       headers: {
  //         'Authorization': `Bearer ${token}`
  //       }
  //     },
  //     {
  //       onEvent,
  //       onComplete,
  //       onError
  //     }
  //   );

  planRouteStream: (
    data: PlanRouteParams,
    onEvent: (event: SSEEventType, data: any) => void,
    onComplete: (result: SSEPlanResponse) => void,
    onError: (error: any) => void
  ) => {
    const token = wx.getStorageSync('access_token'); 
    return createSSEStream<SSEPlanResponse>(
      {
        url: `${BASE_URL}/navigation/routes/smart/stream`,
        method: 'POST',
        data: data,
        headers: {
          'Authorization': `Bearer ${token}`
        }
      },
      {
        onEvent,
        onComplete,
        onError
      }
    );
  },
  navigateByCoordinates: (data: CoordinateNavigationParams): Promise<any> => {
    return new Promise((resolve, reject) => {
      const token = wx.getStorageSync('access_token'); 

      wx.request({
        url: `${BASE_URL}/navigation/routes/coordinates`, // 后端对应的纯坐标导航接口
        method: 'POST',
        data: data,
        header: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        success: (res: any) => {
          const statusCode = res.statusCode;
          if (statusCode >= 200 && statusCode < 300 && res.data?.code === 200) {
            resolve(res.data.data); 
          } else {
            const errorMsg = res.data?.message || `路线重算失败 (${statusCode})`;
            reject(new Error(errorMsg));
          }
        },
        fail: (err) => {
          reject(new Error('网络请求失败，请检查网络'));
        }
      });
    });
  }
};
