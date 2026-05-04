import { TENCENT_MAP_KEY, GAODE_MAP_KEY } from './config';

export interface ReverseGeocodeResult {
  address: string;
  province: string;
  city: string;
  district: string;
}

export interface PlaceSearchResult {
  id: string;
  title: string;
  address: string;
  latitude: number;
  longitude: number;
}

export function reverseGeocode(latitude: number, longitude: number): Promise<ReverseGeocodeResult> {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `https://apis.map.qq.com/ws/geocoder/v1/?location=${latitude},${longitude}&key=${TENCENT_MAP_KEY}`,
      success: (res: any) => {
        if (res.data.status === 0) {
          const result = res.data.result;
          resolve({
            address: result.address || '未知地址',
            province: result.address_component?.province || '',
            city: result.address_component?.city || '',
            district: result.address_component?.district || ''
          });
        } else {
          reject(new Error(`逆地理编码失败: ${res.data.message}`));
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
}

export function gaodeReverseGeocode(latitude: number, longitude: number): Promise<ReverseGeocodeResult> {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `https://restapi.amap.com/v3/geocode/regeo?key=${GAODE_MAP_KEY}&location=${longitude},${latitude}&extensions=base`,
      success: (res: any) => {
        if (res.data.status === '1' && res.data.regeocode) {
          const result = res.data.regeocode;
          const addressComponent = result.addressComponent || {};
          resolve({
            address: result.formatted_address || '未知地址',
            province: addressComponent.province || '',
            city: addressComponent.city ? addressComponent.city[0] || addressComponent.city : '',
            district: addressComponent.district || ''
          });
        } else {
          reject(new Error(`逆地理编码失败: ${res.data.info || '未知错误'}`));
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
}

export function gaodePlaceSearch(keyword: string, city: string): Promise<PlaceSearchResult[]> {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `https://restapi.amap.com/v3/assistant/inputKeywords?key=${GAODE_MAP_KEY}&keywords=${encodeURIComponent(keyword)}&city=${encodeURIComponent(city)}&types=&citylimit=true`,
      success: (res: any) => {
        if (res.data.status === '1' && res.data.tips && res.data.tips.length > 0) {
          const results: PlaceSearchResult[] = res.data.tips
            .filter((item: any) => item.location)
            .map((item: any, index: number) => ({
              id: item.id || String(index),
              title: item.name || item.address || '',
              address: item.address || '',
              latitude: item.location.split(',')[1] ? parseFloat(item.location.split(',')[1]) : 0,
              longitude: item.location.split(',')[0] ? parseFloat(item.location.split(',')[0]) : 0
            }));
          resolve(results);
        } else {
          resolve([]);
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
}
