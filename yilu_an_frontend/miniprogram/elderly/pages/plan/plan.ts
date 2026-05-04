import { favoritePlacesApi } from '../../../api/favorite-places';
import type { FavoritePlace } from '../../../api/favorite-places';
import { navigationApi, AddressNavigationResponse, NavigationRouteResponse } from '../../../api/navigation';
import { getPlace, savePlace, getRoute, saveRoute, getNavigationExtra, saveNavigationExtra } from '../../storage';

function removeStorageSync(key: string) {
  try {
    wx.removeStorageSync(key);
  } catch (error) {
    console.error(`删除存储失败: ${key}`, error);
  }
}

Page({
  data: {
    placeId: 0,
    placeName: '',
    routeInfo: {
      destination: '',
      distance: '',
      transport: '',
      estimate: '',
      navigationAdvice: '',
      weather: ''
    },
    isLoading: true
  },

  onLoad(options: any) {
    const placeId = options?.place_id;
    if (placeId) {
      this.setData({ placeId: parseInt(placeId) });
      this.loadPlaceAndRoute();
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
      let navigationAdvice = '';
      let weather = '';

      const cachedRoute = getRoute(place.place_id);
      const cachedExtra = getNavigationExtra(place.place_id);

      if (cachedRoute && cachedExtra) {
        console.log('使用本地缓存路线和导航信息');
        route = cachedRoute as AddressNavigationResponse['route'];
        navigationAdvice = cachedExtra.navigation_advice;
        weather = cachedExtra.weather;
      } else {
        let planSuccess = false;
        try {
          const planRes: NavigationRouteResponse = await navigationApi.planRoute({
            favorite_place_id: place.place_id,
            origin_lng: res.longitude.toString(),
            origin_lat: res.latitude.toString()
          });

          console.log('智能规划路线结果:', planRes);
          navigationAdvice = planRes.navigation_advice || '';
          weather = planRes.weather || '';
          route = planRes.route;
          planSuccess = true;
          saveRoute(place.place_id, route);
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

      this.setData({
        routeInfo: {
          destination: place.place_name,
          distance: route.distance,
          transport: '步行',
          estimate: route.duration,
          navigationAdvice: navigationAdvice,
          weather: weather
        }
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
    const url = `/elderly/pages/navigate/navigate?place_id=${this.data.placeId}`;
    wx.navigateTo({ url });
  },

  async replan() {
    const cachedPlace = getPlace(this.data.placeId);
    if (cachedPlace) {
      removeStorageSync(`route_${this.data.placeId}`);
      removeStorageSync(`nav_extra_${this.data.placeId}`);
      this.setData({ isLoading: true });
      await this.loadPlaceAndRoute();
    }
  }
})