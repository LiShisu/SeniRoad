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
  travel_mode?: 'walking' | 'transit'; // 新增
  city?: string;                       // 新增
}

// 语音导航请求参数
export interface VoiceNavigationParams {
  origin_lng: string;
  origin_lat: string;
  audio_file: any;
  travel_mode?: 'walking' | 'transit'; // 新增
  city?: string;                       // 新增
}

// 导航步骤
export interface NavigationStep {
  instruction: string;
  polyline: string;
  distance?: string; // 变成可选
  duration?: string; // 变成可选
  road?: string;     // 变成可选
}
// 地址导航路线数据
export interface AddressRouteData {
  distance: string;
  duration: string;
  steps: NavigationStep[];
  polyline: string;
  record_id: number;
}
//增加公交段落类型
export interface TransitSegment {
  walking?: { steps?: NavigationStep[] };
  bus?: {
    name: string;
    departure_stop: string;
    arrival_stop: string;
    via_num: number;
    polyline: string;
  };
}
//统一使用 type 定义返回的 RouteData，兼容双模
export type SmartRouteData = {
  record_id: number;
  distance: string;
  duration: string;
  polyline: string;
  steps: NavigationStep[];         // 必须有，公交模式由适配器生成空数组
  segments?: TransitSegment[];      // 公交模式特有
  [key: string]: any;
}
// 地址导航响应
export interface AddressNavigationResponse {
  status: string;
  destination: string;
  place_name: string;
  route: SmartRouteData; // 指向新类型
  latitude: string;
  longitude: string;
}

// 导航路线数据（智能导航）
// export interface NavigationRouteData {
//   record_id: number;
//   text: string;
//   origin: string;
//   destination: string;
//   distance: string;
//   duration: string;
//   steps: NavigationStep[];
//   polyline: string;
// }
// 为了向下兼容代码里写到的 NavigationRouteData，也让它等同于 SmartRouteData
export type NavigationRouteData = SmartRouteData;
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
  travel_mode?: 'walking' | 'transit'; // 新增
  city?: string;                       // 新增
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
  navigateByVoice: (data: { audio_file: string, origin_lng: string, origin_lat: string, travel_mode?: string, city?: string }): Promise<any> => {
    return new Promise((resolve, reject) => {
      const { audio_file, origin_lng, origin_lat, travel_mode, city } = data;
      const token = getToken();
      
      wx.uploadFile({
        url: `${BASE_URL}/navigation/routes/voice/stream`,
        filePath: audio_file,
        name: 'audio_file',
        timeout: 360000,
        // 🌟 把新参数加进 formData 里传给后端
        formData: { 
          origin_lng, 
          origin_lat,
          travel_mode: travel_mode || 'walking',
          city: city || '济南市' 
        },
        header: { 
          'Authorization': `Bearer ${token}`
        },
        success: (res) => {
          const statusCode = res.statusCode;
          if (statusCode >= 200 && statusCode < 300) {
            const rawData = res.data as string;
            let destInfo = null, routeInfo = null, weatherInfo = null, adviceInfo = null;
            const events = rawData.split('\n\n');
            
            for (const eventBlock of events) {
              if (!eventBlock.trim()) continue;
              const eventMatch = eventBlock.match(/event:\s*(\w+)/);
              const dataMatch = eventBlock.match(/data:\s*([\s\S]*)/);
              if (eventMatch && dataMatch) {
                const eventName = eventMatch[1];
                const rawJsonStr = dataMatch[1].trim();
                try {
                  const parsedData = JSON.parse(rawJsonStr);
                  switch (eventName) {
                    case 'error':
                      reject(new Error(parsedData.error || '语音处理失败'));
                      return; 
                    case 'destination': destInfo = parsedData; break;
                    case 'route': routeInfo = parsedData; break;
                    case 'weather': weatherInfo = parsedData; break;
                    case 'advice': adviceInfo = parsedData; break;
                  }
                } catch (e) {
                  console.error(`事件 [${eventName}] JSON 解析失败:`, rawJsonStr);
                }
              }
            }
            if (!routeInfo) {
              reject(new Error('未获取到完整路线信息，请检查网络或稍后重试'));
              return;
            }
            resolve({ destInfo, routeInfo, weatherInfo, adviceInfo });
          } else {
            reject(new Error(`服务器错误: HTTP ${statusCode}`));
          }
        },
        fail: (err) => {
          reject(new Error(`录音上传失败: ${err.errMsg}`));
        }
      });
    });
  },
  // TODO: 流式响应，待后端支持
//   实现真正流式传输的方案 （需要后端支持）：
// 1. 先上传音频文件获取任务 ID
// 2. 使用 wx.request 开启分块传输（ enableChunked: true ）订阅结果流
  navigateByVoiceStream: (
    data: { audio_file: string, origin_lng: string, origin_lat: string },
    onEvent: (event: SSEEventType, data: any) => void,
    onComplete: (result: SSEPlanResponse) => void,
    onError: (error: any) => void
  ): () => void => {
    const { audio_file, origin_lng, origin_lat } = data;
    const token = getToken();
    let requestTask: any = null;

    wx.uploadFile({
      url: `${BASE_URL}/navigation/routes/voice/stream`,
      filePath: audio_file,
      name: 'audio_file',
      timeout: 120000,
      formData: { origin_lng, origin_lat },
      header: { 'Authorization': `Bearer ${token}` },
      success: (uploadRes) => {
        const statusCode = uploadRes.statusCode;
        if (statusCode >= 200 && statusCode < 300) {
          try {
            const rawData = uploadRes.data;
            
            if (rawData.includes('event: error')) {
              const errMatch = extractSseEvent('error', rawData);
              onError(new Error(errMatch?.error || '语音识别失败'));
              return;
            }

            const destInfo = extractSseEvent('destination', rawData);
            const routeInfo = extractSseEvent('route', rawData);
            const weatherInfo = extractSseEvent('weather', rawData);
            const adviceInfo = extractSseEvent('advice', rawData);

            if (destInfo) {
              onEvent('destination', destInfo);
            }
            if (routeInfo) {
              onEvent('route', routeInfo);
            }
            if (weatherInfo) {
              onEvent('weather', weatherInfo);
            }
            if (adviceInfo) {
              onEvent('advice', adviceInfo);
            }

            onComplete({
              destination: destInfo?.destination,
              place_name: destInfo?.place_name,
              route: routeInfo,
              weather: weatherInfo,
              navigation_advice: adviceInfo,
              latitude: destInfo?.latitude,
              longitude: destInfo?.longitude
            });
          } catch (parseError) {
            onError(new Error('解析响应数据失败'));
          }
        } else {
          onError(new Error(`服务器请求失败 (${statusCode})`));
        }
      },
      fail: (err) => {
        onError(new Error(`上传文件失败: ${err.errMsg}`));
      }
    });

    return () => {
      if (requestTask?.abort) {
        requestTask.abort();
      }
    };
  },

  planRouteStream: (
    data: PlanRouteParams,
    onEvent: (event: SSEEventType, data: any) => void,
    onComplete: (result: SSEPlanResponse) => void,
    onError: (error: any) => void
  ) => {
    const token = getToken(); 
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
      const token = getToken(); 

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
          reject(new Error(`请求失败 (${err.errMsg})`));
        }
      });
    });
  }
};
