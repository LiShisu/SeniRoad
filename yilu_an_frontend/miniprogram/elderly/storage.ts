// // TODO：待与utils/storage.ts合并
// export function getStorageSync<T>(key: string): T | null {
//   try {
//     const value = wx.getStorageSync(key);
//     if (value) {
//       return value as T;
//     }
//     return null;
//   } catch (error) {
//     console.error(`获取存储失败: ${key}`, error);
//     return null;
//   }
// }

// export function setStorageSync<T>(key: string, value: T): boolean {
//   try {
//     wx.setStorageSync(key, value);
//     return true;
//   } catch (error) {
//     console.error(`设置存储失败: ${key}`, error);
//     return false;
//   }
// }

// export function removeStorageSync(key: string): boolean {
//   try {
//     wx.removeStorageSync(key);
//     return true;
//   } catch (error) {
//     console.error(`删除存储失败: ${key}`, error);
//     return false;
//   }
// }

// const PLACE_STORAGE_PREFIX = 'place_';

// export interface PlaceData {
//   place_id: number;
//   place_name: string;
//   latitude: number;
//   longitude: number;
//   address: string;
//   [key: string]: any;
// }

// export function getPlace(placeId: number): PlaceData | null {
//   return getStorageSync<PlaceData>(`${PLACE_STORAGE_PREFIX}${placeId}`);
// }

// export function savePlace(place: PlaceData): boolean {
//   if (!place || !place.place_id) {
//     console.error('保存地点数据无效:', place);
//     return false;
//   }
//   return setStorageSync(`${PLACE_STORAGE_PREFIX}${place.place_id}`, place);
// }

// const ROUTE_STORAGE_PREFIX = 'route_';

// export interface RouteData {
//   distance: string;
//   duration: string;
//   steps: any[];
//   polyline: string | string[];
//   record_id: number;
//   [key: string]: any;
// }

// export function getRoute(placeId: number): RouteData | null {
//   return getStorageSync<RouteData>(`${ROUTE_STORAGE_PREFIX}${placeId}`);
// }

// export function saveRoute(placeId: number, route: RouteData): boolean {
//   if (!placeId || !route) {
//     console.error('保存路线数据无效:', { placeId, route });
//     return false;
//   }
//   return setStorageSync(`${ROUTE_STORAGE_PREFIX}${placeId}`, route);
// }

// const NAV_EXTRA_STORAGE_PREFIX = 'nav_extra_';

// export interface NavigationAdvice {
//   clothing_advice: string;
//   items_to_bring: string[];
//   safety_reminders: string[];
//   best_time: string;
//   tips: string[];
// }

// export interface WeatherInfo {
//   weather_text: string;
//   temperature: string;
//   wind: string;
//   humidity: string;
//   air_quality: string;
// }

// export interface NavigationExtraData {
//   navigation_advice: string | NavigationAdvice;
//   weather: string | WeatherInfo;
// }

// export function getNavigationExtra(placeId: number): NavigationExtraData | null {
//   return getStorageSync<NavigationExtraData>(`${NAV_EXTRA_STORAGE_PREFIX}${placeId}`);
// }

// export function saveNavigationExtra(placeId: number, extra: NavigationExtraData): boolean {
//   if (!placeId || !extra) {
//     console.error('保存导航额外数据无效:', { placeId, extra });
//     return false;
//   }
//   return setStorageSync(`${NAV_EXTRA_STORAGE_PREFIX}${placeId}`, extra);
// }
// TODO：待与utils/storage.ts合并
export function getStorageSync<T>(key: string): T | null {
  try {
    const value = wx.getStorageSync(key);
    if (value) {
      return value as T;
    }
    return null;
  } catch (error) {
    console.error(`获取存储失败: ${key}`, error);
    return null;
  }
}

export function setStorageSync<T>(key: string, value: T): boolean {
  try {
    wx.setStorageSync(key, value);
    return true;
  } catch (error) {
    console.error(`设置存储失败: ${key}`, error);
    return false;
  }
}

export function removeStorageSync(key: string): boolean {
  try {
    wx.removeStorageSync(key);
    return true;
  } catch (error) {
    console.error(`删除存储失败: ${key}`, error);
    return false;
  }
}

const PLACE_STORAGE_PREFIX = 'place_';

export interface PlaceData {
  place_id: number;
  place_name: string;
  latitude: number;
  longitude: number;
  address: string;
  [key: string]: any;
}

export function getPlace(placeId: number): PlaceData | null {
  return getStorageSync<PlaceData>(`${PLACE_STORAGE_PREFIX}${placeId}`);
}

export function savePlace(place: PlaceData): boolean {
  if (!place || !place.place_id) {
    console.error('保存地点数据无效:', place);
    return false;
  }
  return setStorageSync(`${PLACE_STORAGE_PREFIX}${place.place_id}`, place);
}


// ==========================================
// 🌟 路线缓存隔离区 (加入 mode 参数)
// ==========================================
const ROUTE_STORAGE_PREFIX = 'route_';

export interface RouteData {
  distance: string;
  duration: string;
  steps: any[]; // 因为我们在 navigation.ts 中处理了具体的强类型，这里用 any[] 兼容底层存储即可
  polyline: string | string[];
  record_id: number;
  [key: string]: any;
}

// 🌟 修改：默认 fallback 到 'walking'，拼接 mode 到 key 中
export function getRoute(placeId: number, mode: string = 'walking'): RouteData | null {
  return getStorageSync<RouteData>(`${ROUTE_STORAGE_PREFIX}${placeId}_${mode}`);
}

// 🌟 修改：存储时拼接 mode
export function saveRoute(placeId: number, route: RouteData, mode: string = 'walking'): boolean {
  if (!placeId || !route) {
    console.error('保存路线数据无效:', { placeId, route });
    return false;
  }
  return setStorageSync(`${ROUTE_STORAGE_PREFIX}${placeId}_${mode}`, route);
}


// ==========================================
// 🌟 附加信息(天气/建议)缓存隔离区 (加入 mode 参数)
// ==========================================
const NAV_EXTRA_STORAGE_PREFIX = 'nav_extra_';

export interface NavigationAdvice {
  clothing_advice: string;
  items_to_bring: string[];
  safety_reminders: string[];
  best_time: string;
  tips: string[];
}

export interface WeatherInfo {
  weather_text: string;
  temperature: string;
  wind: string;
  humidity: string;
  air_quality: string;
}

export interface NavigationExtraData {
  navigation_advice: string | NavigationAdvice;
  weather: string | WeatherInfo;
}

// 🌟 修改：出行建议和天气也应该跟 mode 绑定。因为公交和步行的建议是截然不同的！
export function getNavigationExtra(placeId: number, mode: string = 'walking'): NavigationExtraData | null {
  return getStorageSync<NavigationExtraData>(`${NAV_EXTRA_STORAGE_PREFIX}${placeId}_${mode}`);
}

// 🌟 修改：存储时拼接 mode
export function saveNavigationExtra(placeId: number, extra: NavigationExtraData, mode: string = 'walking'): boolean {
  if (!placeId || !extra) {
    console.error('保存导航额外数据无效:', { placeId, extra });
    return false;
  }
  return setStorageSync(`${NAV_EXTRA_STORAGE_PREFIX}${placeId}_${mode}`, extra);
}