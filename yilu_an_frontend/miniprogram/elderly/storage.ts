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

const ROUTE_STORAGE_PREFIX = 'route_';

export interface RouteData {
  distance: string;
  duration: string;
  steps: any[];
  polyline: string | string[];
  record_id: number;
  [key: string]: any;
}

export function getRoute(placeId: number): RouteData | null {
  return getStorageSync<RouteData>(`${ROUTE_STORAGE_PREFIX}${placeId}`);
}

export function saveRoute(placeId: number, route: RouteData): boolean {
  if (!placeId || !route) {
    console.error('保存路线数据无效:', { placeId, route });
    return false;
  }
  return setStorageSync(`${ROUTE_STORAGE_PREFIX}${placeId}`, route);
}
