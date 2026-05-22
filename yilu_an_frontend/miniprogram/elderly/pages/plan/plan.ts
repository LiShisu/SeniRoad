import { favoritePlacesApi } from '../../../api/favorite-places';
import type { FavoritePlace } from '../../../api/favorite-places';
import { navigationApi, AddressNavigationResponse, SSEPlanResponse,SmartRouteData } from '../../../api/navigation';
import { getPlace, savePlace, getRoute, saveRoute, getNavigationExtra, saveNavigationExtra, type NavigationAdvice, type WeatherInfo } from '../../storage';
import { getLocation } from '../../../utils/geo';
import { getRealLocation } from '../../../utils/geo';
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
    isVoiceMode: false,
    placeId: 0,
    placeName: '',
    currentPlace: null as FavoritePlace | null,
    travelMode: 'walking',
    city: '济南市',
    currentAudioPath: '',
    routeInfo: {
      destination: '',
      distance: '',
      transport: '',
      estimate: ''
    },
    navigationAdvice: {} as NavigationAdvice,
    weather: {} as WeatherInfo,
    isLoading: true,
    loadingText: '正在规划路线...',
    cur_lat: '',
    cur_lng: '',
    hasRouteData: false
  },

  // elderly/pages/plan/plan.ts -> onLoad

  onLoad(options: any) {
    if (options?.travelMode) {
      this.setData({
        travelMode: options.travelMode,
        city: decodeURIComponent(options.city || '济南市')
      });
    }

    if (options?.place_id) {
      this.setData({ 
        placeId: parseInt(options.place_id),
        isVoiceMode: false 
      });
    } 
    else if (options?.audioPath) {
      this.setData({ 
        isVoiceMode: true,
        currentAudioPath: decodeURIComponent(options.audioPath) 
      });
    }
    
    this.setData({ 
      isLoading: false 
    });
  },
  selectTravelMode(e: any) {
    const mode = e.currentTarget.dataset.mode; 
    if (mode === this.data.travelMode) return;
    
    this.setData({ travelMode: mode });
  },

  async confirmAndPlan() {
    await this.getLocation();
    
    if (!this.data.cur_lat || !this.data.cur_lng) {
      wx.showToast({ title: '获取位置失败，请重试', icon: 'none', duration: 2000 });
      return;
    }

    wx.showLoading({ title: '正在规划路线...', mask: true });

    if (this.data.isVoiceMode && this.data.currentAudioPath) {
      await this.loadPlanByVoice(this.data.currentAudioPath);
    } 
    else if (this.data.placeId) {
      await this.loadPlaceAndRoute();
    }
    
    this.setData({ hasRouteData: true });
    wx.hideLoading();
  },

  switchTravelMode(e: any) {
    if (!this.data.hasRouteData) return;
    
    const mode = e.currentTarget.dataset.mode; 
    if (mode === this.data.travelMode) return;
    
    this.setData({ travelMode: mode });
    
    if (this.data.isVoiceMode && this.data.currentAudioPath) {
      wx.showLoading({ title: '正在重新规划...', mask: true });
      this.loadPlanByVoice(this.data.currentAudioPath);
    } 
    else if (this.data.currentPlace) {
      wx.showLoading({ title: '正在重新规划...', mask: true }); 
      this.planRoute(this.data.currentPlace);
    }
  },
  // 获取当前位置
  async getLocation() {
    try {
      // 🌟 核心修改 4：將原本的 getLocation 替換為 getRealLocation
      const location = await getRealLocation();
      console.log('成功動態感知長輩所在環境，當前城市為:', location.city);
      
      // 一箭三雕：把坐標和真正的城市統統寫進 data 狀態機中
      this.setData({
        cur_lat: location.latitude.toString(),
        cur_lng: location.longitude.toString(),
        city: location.city // 動態覆蓋！從此徹底告別死代碼
      });
      
    } catch (error) {
      console.error('獲取位置失敗:', error);
      wx.showToast({ title: '獲取位置失敗，請重試', icon: 'none', duration: 2000 });
      setTimeout(() => { wx.navigateBack(); }, 2000);
    }
  },

  //语音录音规划逻辑
  async loadPlanByVoice(audioPath: string) {
    await this.getLocation();
    wx.showLoading({ title: this.data.loadingText });
    if (!this.data.cur_lat || !this.data.cur_lng) {
      throw new Error('获取当前位置失败，请重试');
    }
    try {
      const res = await navigationApi.navigateByVoice({
        audio_file: audioPath,
        origin_lat: this.data.cur_lat,
        origin_lng: this.data.cur_lng,
        travel_mode: this.data.travelMode, // 传入模式
        city: this.data.city               // 传入城市
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
          transport: this.data.travelMode === 'transit' ? '公交' : '步行', // 动态文案
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
    await this.getLocation();
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

      this.setData({ 
        placeName: place.place_name,
        currentPlace: place // 🌟 记录当前地点，方便切换模式时复用
      });
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
      console.log('当前定位:', this.data.cur_lat, this.data.cur_lng);
      const travelMode = this.data.travelMode as 'walking' | 'transit';
      const city = this.data.city;

      let route: SmartRouteData | null = null;
      let navigationAdvice: NavigationAdvice = {
        clothing_advice: '', items_to_bring: [], safety_reminders: [], best_time: '', tips: []
      };
      let weather: WeatherInfo = {
        weather_text: '', temperature: '', wind: '', humidity: '', air_quality: ''
      };

      const cachedRoute = getRoute(place.place_id, travelMode);
      const cachedExtra = getNavigationExtra(place.place_id, travelMode);

      if (cachedRoute && cachedExtra) {
        console.log('使用本地缓存路线和导航信息');
        route = cachedRoute as SmartRouteData;
        if (typeof cachedExtra.navigation_advice === 'object') {
          navigationAdvice = cachedExtra.navigation_advice as NavigationAdvice;
        } else {
          navigationAdvice.clothing_advice = cachedExtra.navigation_advice || '';
        }
        if (typeof cachedExtra.weather === 'object') {
          weather = cachedExtra.weather as WeatherInfo;
        }
        
        // 🌟 核心修复 2：如果直接命中本地缓存，速度极快（毫秒级），直接在这里手动关掉 Loading
        wx.hideLoading();
        
      } else {
        let planSuccess = false;
        try {
          const planResult = await new Promise<SSEPlanResponse>((resolve, reject) => {
            navigationApi.planRouteStream(
              {
                favorite_place_id: place.place_id,
                origin_lng: this.data.cur_lng,
                origin_lat: this.data.cur_lat,
                travel_mode: travelMode,
                city: city
              },
              (event, data) => { console.log('SSE 事件:', event, typeof data, data); },
              (result) => { resolve(result); },
              (error) => { reject(error); }
            );
          });

          if (planResult.navigation_advice) {
            if (typeof planResult.navigation_advice === 'object') {
              navigationAdvice = planResult.navigation_advice as NavigationAdvice;
            } else {
              navigationAdvice.clothing_advice = planResult.navigation_advice || '';
            }
          }
          if (planResult.weather) {
            if (typeof planResult.weather === 'object') {
              weather = planResult.weather as WeatherInfo;
            }
          }
          
          route = planResult.route || null;
          planSuccess = !!route;
          if (route) {
            saveRoute(place.place_id, route, travelMode);
          }
          if (planSuccess) {
            saveNavigationExtra(place.place_id, {
              navigation_advice: navigationAdvice,
              weather: weather
            }, travelMode);
          }
        } catch (planErr) {
          console.error('智能导航接口调用失败:', planErr);
        }

        if (!planSuccess) {
          if (cachedRoute) {
            route = cachedRoute as SmartRouteData;
          } else {
            const routeRes = await navigationApi.navigateByAddress({
              favorite_place_id: place.place_id,
              origin_lng: this.data.cur_lng,
              origin_lat: this.data.cur_lat,
              travel_mode: travelMode,
              city: city
            });
            route = routeRes.route;
            saveRoute(place.place_id, route, travelMode);
          }
        }
        
        // 🌟 核心修复 3：不管大模型流式请求是完美跑完，还是降级走到了保底的高德标准接口，
        // 只要这个异步流程尘埃落定了，立刻在这里关掉转圈圈，把屏幕控制权交还长辈！
        wx.hideLoading();
      }

      if (!route) {
        wx.showToast({ title: '路线规划失败', icon: 'none' });
        return;
      }

      const durationNum = parseInt(route.duration);
      this.setData({
        routeInfo: {
          destination: place.place_name,
          distance: route.distance,
          transport: travelMode === 'transit' ? '公交' : '步行',
          estimate: formatDuration(durationNum)
        },
        navigationAdvice: navigationAdvice,
        weather: weather
      });
      
    } catch (err: any) {
      // 🌟 核心修复 4：极端的异常捕获区，万一彻底断网或者崩溃了，也必须解开 Loading
      wx.hideLoading();
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
      wx.navigateTo({ url: `/elderly/pages/navigate/navigate?voiceMode=1&travelMode=${this.data.travelMode}&city=${this.data.city}` }); // 将状态传递给导航页
    } else {
      const url = `/elderly/pages/navigate/navigate?place_id=${this.data.placeId}&travelMode=${this.data.travelMode}&city=${this.data.city}`; // 同上
      wx.navigateTo({ url });
    }
  },
// async replan() {
//   if (this.data.isVoiceMode) {
//     // 语音模式的重新规划：提示老人返回重新录音
//     wx.showToast({ title: '请返回上一页重新说出目的地', icon: 'none', duration: 2000 });
//     setTimeout(() => {
//       wx.navigateBack();
//     }, 2000);
//   } else {
//       const cachedPlace = getPlace(this.data.placeId);
//       if (cachedPlace) {
//         // 清除当前模式下的路线缓存
//         removeStorageSync(`route_${this.data.placeId}_${this.data.travelMode}`); 
//         removeStorageSync(`nav_extra_${this.data.placeId}`);
//         this.setData({ isLoading: true });
//         await this.loadPlaceAndRoute();
//       }
//     }
//   }
  async replan() {
    if (this.data.isVoiceMode) {
      wx.showToast({ title: '请返回上一页重新说出目的地', icon: 'none', duration: 2000 });
      setTimeout(() => { wx.navigateBack(); }, 2000);
    } else {
      // 返回选择出行方式状态
      this.setData({ 
        hasRouteData: false
      });
    }
  }
});
