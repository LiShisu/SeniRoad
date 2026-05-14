import { favoritePlacesApi } from '../../../api/favorite-places';
import type { FavoritePlace } from '../../../api/favorite-places';
import { navigationApi, AddressNavigationResponse, SSEPlanResponse } from '../../../api/navigation';
import { getPlace, savePlace, getRoute, saveRoute, getNavigationExtra, saveNavigationExtra, type NavigationAdvice, type WeatherInfo } from '../../storage';
import { API_BASE_URL } from '../../../utils/config';
function removeStorageSync(key: string) {
  try {
    wx.removeStorageSync(key);
  } catch (error) {
    console.error(`删除存储失败: ${key}`, error);
  }
}

function formatDuration(seconds: number): string {
  const totalMinutes = Math.round(seconds / 60);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`;
  }
  return `${minutes}分钟`;
}

Page({
  data: {
    isVoiceMode: false, // 新增：标识是否为语音导航模式
    placeId: 0,
    placeName: '',
    routeInfo: {
      destination: '',
      distance: '',
      transport: '',
      estimate: ''
    },
    navigationAdvice: {} as NavigationAdvice,
    weather: {} as WeatherInfo,
    isLoading: true,
    loadingText: '正在规划路线...'
  },

  onLoad(options: any) {
    // 场景 1：来自常用地点点击
    if (options?.place_id) {
      this.setData({ 
        placeId: parseInt(options.place_id),
        isVoiceMode: false 
      });
      this.loadPlaceAndRoute();
    } 
    // 场景 2：来自语音输入跳转
    else if (options?.audioPath) {
      this.setData({ 
        isVoiceMode: true,
      });
      this.loadPlanByVoice(
        decodeURIComponent(options.audioPath), 
        options.lat, 
        options.lng
      );
    }
  },
  //语音录音规划逻辑
  async loadPlanByVoice(audioPath: string, lat: string, lng: string) {
    wx.showLoading({ title: this.data.loadingText });
    try {
      const res = await navigationApi.navigateByVoice({
        audio_file: audioPath,
        origin_lat: lat,
        origin_lng: lng
      });
      const { destInfo, routeInfo, weatherInfo, adviceInfo } = res;
      if (!routeInfo || !destInfo) {
        throw new Error('路线解析失败，请重试');
      }
      const durationNum = parseInt(routeInfo.duration);
      this.setData({
        placeName: destInfo.destination,
        routeInfo: {
          destination: destInfo.destination,
          distance: routeInfo.distance || '0',
          transport: '步行', 
          estimate: formatDuration(durationNum)
        },
        weather: weatherInfo || {},
        navigationAdvice: adviceInfo || {},
        isLoading: false
      });
      // 将语音路线存入“缓存桥梁”，供 startNavigate 跳转时使用
      wx.setStorageSync('tempVoiceRoute', {
        destInfo: destInfo,
        route: routeInfo
      });
      wx.hideLoading();
    } catch (err: any) {
      wx.hideLoading();
      this.setData({ isLoading: false });
      const errMsg = err.message || '网络请求超时';
      wx.showToast({ title: errMsg, icon: 'none', duration: 2000 });
      console.error('语音规划失败:', err);
      // 报错后停留两秒，自动退回上一页让长辈重新录音
      setTimeout(() => {
        wx.navigateBack();
      }, 2000);
    }
  },
  async loadPlaceAndRoute() {
    let loadingShown = false;
    try {
      wx.showLoading({ title: '规划路线中...' });
      loadingShown = true;
      
      let place: FavoritePlace | null = null;

      const cachedPlace = getPlace(this.data.placeId);
      if (cachedPlace) {
        place = cachedPlace as FavoritePlace;
      }

      if (!place) {
        place = await favoritePlacesApi.getFavoritePlaceById(this.data.placeId);
        savePlace(place);
      }

      this.setData({ placeName: place.place_name });
      await this.planRoute(place);
    } catch (err: any) {
      console.error('加载地点或路线失败:', err);
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    } finally {
      if (loadingShown) {
        wx.hideLoading();
      }
      this.setData({ isLoading: false });
    }
  },

  async planRoute(place: FavoritePlace) {
    try {
      const res = await wx.getLocation({
        type: 'gcj02'
      });

      console.log('当前定位:', res.latitude, res.longitude);
      console.log('目标地点:', place.place_id, place.place_name, place.latitude, place.longitude);

      let route: AddressNavigationResponse['route'] | null = null;
      let navigationAdvice: NavigationAdvice = {
        clothing_advice: '',
        items_to_bring: [],
        safety_reminders: [],
        best_time: '',
        tips: []
      };
      let weather: WeatherInfo = {
        weather_text: '',
        temperature: '',
        wind: '',
        humidity: '',
        air_quality: ''
      };

      const cachedRoute = getRoute(place.place_id);
      const cachedExtra = getNavigationExtra(place.place_id);

      if (cachedRoute && cachedExtra) {
        console.log('使用本地缓存路线和导航信息');
        console.log('缓存路线:', cachedRoute);
        console.log('缓存导航信息:', cachedExtra);
        
        route = cachedRoute as AddressNavigationResponse['route'];
        
        if (typeof cachedExtra.navigation_advice === 'object') {
          navigationAdvice = cachedExtra.navigation_advice as NavigationAdvice;
        } else {
          navigationAdvice = {
            clothing_advice: cachedExtra.navigation_advice || '',
            items_to_bring: [],
            safety_reminders: [],
            best_time: '',
            tips: []
          };
        }
        
        if (typeof cachedExtra.weather === 'object') {
          weather = cachedExtra.weather as WeatherInfo;
        } else {
          weather = {
            weather_text: '',
            temperature: '',
            wind: '',
            humidity: '',
            air_quality: ''
          };
        }
      } else {
        let planSuccess = false;
        try {
          const planResult = await new Promise<SSEPlanResponse>((resolve, reject) => {
            navigationApi.planRouteStream(
              {
                favorite_place_id: place.place_id,
                origin_lng: res.longitude.toString(),
                origin_lat: res.latitude.toString()
              },
              (event, data) => {
                console.log('SSE 事件:', event, typeof data, data);
              },
              (result) => {
                console.log('SSE 流式规划完成:', result);
                resolve(result);
              },
              (error) => {
                console.error('SSE 流式规划失败:', error);
                reject(error);
              }
            );
          });

          console.log('智能规划路线结果:', planResult);
          
          if (planResult.navigation_advice) {
            if (typeof planResult.navigation_advice === 'object') {
              navigationAdvice = planResult.navigation_advice as NavigationAdvice;
            } else {
              navigationAdvice = {
                clothing_advice: planResult.navigation_advice || '',
                items_to_bring: [],
                safety_reminders: [],
                best_time: '',
                tips: []
              };
            }
          }
          
          if (planResult.weather) {
            if (typeof planResult.weather === 'object') {
              weather = planResult.weather as WeatherInfo;
            } else {
              weather = {
                weather_text: '',
                temperature: '',
                wind: '',
                humidity: '',
                air_quality: ''
              };
            }
          }
          
          route = planResult.route || null;
          planSuccess = !!route;
          if (route) {
            saveRoute(place.place_id, route);
          }
          if (planSuccess) {
            saveNavigationExtra(place.place_id, {
              navigation_advice: navigationAdvice,
              weather: weather
            });
          }
        } catch (planErr) {
          console.error('智能导航接口调用失败:', planErr);
        }

        if (!planSuccess) {
          if (cachedRoute) {
            console.log('智能导航失败，使用本地缓存路线');
            route = cachedRoute as AddressNavigationResponse['route'];
          }else {
            const routeRes = await navigationApi.navigateByAddress({
              favorite_place_id: place.place_id,
              origin_lng: res.longitude.toString(),
              origin_lat: res.latitude.toString()
            });

            console.log('路线规划结果:', routeRes);
            route = routeRes.route;
            
            saveRoute(place.place_id, route);
          }
        }
      }

      if (!route) {
        console.error('路线数据为空');
        wx.showToast({ title: '路线规划失败', icon: 'none' });
        return;
      }

      const durationNum = parseInt(route.duration);
      this.setData({
        routeInfo: {
          destination: place.place_name,
          distance: route.distance,
          transport: '步行',
          estimate: formatDuration(durationNum)
        },
        navigationAdvice: navigationAdvice,
        weather: weather
      });
    } catch (err: any) {
      console.error('规划路线失败:', err);
      throw err;
    }
  },

  goBack() {
    wx.navigateBack();
  },
  startNavigate() {
    // 根据不同模式，给导航页传递不同的参数
    if (this.data.isVoiceMode) {
      // 语音模式：通过 voiceMode 标记，navigate.ts 会自动去读取 tempVoiceRoute 缓存
      wx.navigateTo({ url: '/elderly/pages/navigate/navigate?voiceMode=1' });
    } else {
      const url = `/elderly/pages/navigate/navigate?place_id=${this.data.placeId}`;
      wx.navigateTo({ url });
    }
  },
async replan() {
  if (this.data.isVoiceMode) {
    // 语音模式的重新规划：提示老人返回重新录音
    wx.showToast({ title: '请返回上一页重新说出目的地', icon: 'none', duration: 2000 });
    setTimeout(() => {
      wx.navigateBack();
    }, 2000);
  } else {
    // 收藏夹模式的重新规划
    const cachedPlace = getPlace(this.data.placeId);
    if (cachedPlace) {
      removeStorageSync(`route_${this.data.placeId}`);
      removeStorageSync(`nav_extra_${this.data.placeId}`);
      this.setData({ isLoading: true });
      await this.loadPlaceAndRoute();
    }
  }
}
});