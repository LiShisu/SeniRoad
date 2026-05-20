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

  // navigateByVoice: (data: { audio_file: string, origin_lng: string, origin_lat: string }): Promise<any> => {
  //   return new Promise((resolve, reject) => {
  //     const { audio_file, origin_lng, origin_lat } = data;
  //     const token = getToken(); 

  //     wx.uploadFile({
  //       url: `${BASE_URL}/navigation/routes/voice/stream`, 
  //       filePath: audio_file,
  //       name: 'audio_file', 
  //       timeout: 360000, // 360秒防中断
  //       formData: { origin_lng, origin_lat },
  //       header: { 'Authorization': `Bearer ${token}` },
  //       success: (res) => {
  //         const statusCode = res.statusCode;
  //         if (statusCode >= 200 && statusCode < 300) {
  //           const rawData = res.data; 
  //           // 1. 判断是否包含后端报错事件
  //           if (rawData.includes('event: error')) {
  //             const errMatch = extractSseEvent('error', rawData);
  //             const errMsg = errMatch?.error || '抱歉，没听清您想去哪';
  //             reject(new Error(errMsg));
  //             return;
  //           }
  //           // 2. 依次提取四大模块数据
  //           const destInfo = extractSseEvent('destination', rawData);
  //           const routeInfo = extractSseEvent('route', rawData);
  //           const weatherInfo = extractSseEvent('weather', rawData);
  //           const adviceInfo = extractSseEvent('advice', rawData);
  //           // 3. 将干净的 JSON 对象一次性返回给页面
  //           resolve({ destInfo, routeInfo, weatherInfo, adviceInfo });
  //         } else {
  //           reject(new Error(`服务器请求失败 (${statusCode})`));
  //         }
  //       },
  //       fail: (err) => {
  //         reject(new Error(`上传文件失败 (${err.errMsg}`));
  //       }
  //     });
  //   });
  // },
  // 替换原有的 navigateByVoice 函数
  // navigateByVoice: (data: { audio_file: string, origin_lng: string, origin_lat: string }): Promise<any> => {
  //   return new Promise((resolve, reject) => { // 必须显式返回 Promise
  //     const { audio_file, origin_lng, origin_lat } = data;
  //     const token = getToken();
      
  //     wx.uploadFile({
  //       url: `${BASE_URL}/navigation/routes/voice/stream`,
  //       filePath: audio_file,
  //       name: 'audio_file',
  //       timeout: 360000,
  //       formData: { origin_lng, origin_lat },
  //       header: { 
  //         'Authorization': `Bearer ${token}`,
  //         'Content-Type': 'multipart/form-data' // 显式声明类型（可选，但推荐）
  //       },
  //       success: (res) => {
  //         const statusCode = res.statusCode;
  //         if (statusCode >= 200 && statusCode < 300) {
  //           const rawData = res.data as string; // 确保类型为 string
            
  //           // 1. 错误处理
  //           // 修改正则：使用非贪婪匹配和更宽松的换行符匹配，防止特殊字符导致 match 为 null
  //           const errorRegex = /event:\s*error\s*data:\s*(\{.*\})/i;
  //           const errorMatch = rawData.match(errorRegex);
  //           if (errorMatch && errorMatch[1]) {
  //             try {
  //               const errData = JSON.parse(errorMatch[1]);
  //               reject(new Error(errData.error || '语音识别失败'));
  //               return;
  //             } catch (e) {
  //               reject(new Error('解析错误数据失败'));
  //               return;
  //             }
  //           }

  //           // 2. 数据提取
  //           // 修改正则：使用 [\s\S] 代替 . 来匹配换行符，防止 JSON 跨行导致无法匹配
  //           const extractSseEvent = (eventName: string): any => {
  //             // 匹配 event: eventName 后面的 data: {json}，支持跨行
  //             const regex = new RegExp(`event:\\s*${eventName}\\s*data:\\s*(\\{[\\s\\S]*?\\})`, 'i');
  //             const match = rawData.match(regex);
  //             if (match && match[1]) {
  //               try {
  //                 return JSON.parse(match[1]);
  //               } catch (e) {
  //                 console.error(`JSON解析失败 (${eventName}):`, e);
  //                 return null;
  //               }
  //             }
  //             return null;
  //           };

  //           const destInfo = extractSseEvent('destination');
  //           const routeInfo = extractSseEvent('route');
  //           const weatherInfo = extractSseEvent('weather');
  //           const adviceInfo = extractSseEvent('advice');

  //           // 防御性检查：确保至少有路线数据
  //           if (!routeInfo) {
  //             reject(new Error('未获取到路线信息'));
  //             return;
  //           }

  //           // 3. 返回结果
  //           resolve({ 
  //             destInfo, 
  //             routeInfo, 
  //             weatherInfo, 
  //             adviceInfo 
  //           });
  //         } else {
  //           reject(new Error(`HTTP ${statusCode}`));
  //         }
  //       },
  //       fail: (err) => {
  //         reject(new Error(`上传失败: ${err.errMsg}`));
  //       }
  //     });
  //   });
  // },
  navigateByVoice: (data: { audio_file: string, origin_lng: string, origin_lat: string }): Promise<any> => {
    return new Promise((resolve, reject) => {
      const { audio_file, origin_lng, origin_lat } = data;
      const token = getToken();
      
      wx.uploadFile({
        url: `${BASE_URL}/navigation/routes/voice/stream`,
        filePath: audio_file,
        name: 'audio_file',
        timeout: 360000, // 微信前端的超时足够长，不用管
        formData: { origin_lng, origin_lat },
        header: { 
          'Authorization': `Bearer ${token}`
        },
        success: (res) => {
          const statusCode = res.statusCode;
          
          if (statusCode >= 200 && statusCode < 300) {
            const rawData = res.data as string;
            
            // 准备好我们要返回的数据容器
            let destInfo = null;
            let routeInfo = null;
            let weatherInfo = null;
            let adviceInfo = null;

            // 1. 标准 SSE 解析：按双换行符切分每一个事件块
            const events = rawData.split('\n\n');
            
            for (const eventBlock of events) {
              // 忽略空块
              if (!eventBlock.trim()) continue;

              // 提取事件名和数据体
              const eventMatch = eventBlock.match(/event:\s*(\w+)/);
              const dataMatch = eventBlock.match(/data:\s*([\s\S]*)/);

              if (eventMatch && dataMatch) {
                const eventName = eventMatch[1];
                const rawJsonStr = dataMatch[1].trim();

                try {
                  // 2. 核心：只有提取出来的纯 JSON 字符串才去 parse
                  const parsedData = JSON.parse(rawJsonStr);

                  // 3. 根据不同的事件名，分别赋值
                  switch (eventName) {
                    case 'error':
                      reject(new Error(parsedData.error || '语音处理失败'));
                      return; // 遇到严重错误直接阻断
                    case 'destination':
                      destInfo = parsedData;
                      break;
                    case 'route':
                      routeInfo = parsedData;
                      break;
                    case 'weather':
                      weatherInfo = parsedData;
                      break;
                    case 'advice':
                      adviceInfo = parsedData;
                      break;
                  }
                } catch (e) {
                  console.error(`事件 [${eventName}] JSON 解析失败，可能是网关超时截断了数据:`, rawJsonStr);
                  // 故意不 reject，让其他成功的事件能继续
                }
              }
            }

            // 4. 防御性检查：确保核心路线数据存在
            if (!routeInfo) {
              reject(new Error('未获取到完整路线信息，请检查网络或稍后重试'));
              return;
            }

            // 5. 完美返回结果
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
