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
    const url = `https://restapi.amap.com/v5/place/text?keywords=${encodeURIComponent(keyword)}&region=${encodeURIComponent(city)}&key=${GAODE_MAP_KEY}`;
    console.log('高德搜索请求URL:', url);

    wx.request({
      url,
      success: (res: any) => {
        console.log('高德搜索结果状态码:', res.statusCode);
        console.log('高德搜索结果数据:', res.data);

        if (res.statusCode !== 200) {
          reject(new Error(`请求失败，状态码: ${res.statusCode}`));
          return;
        }

        if (res.data.status === '1' && res.data.pois && res.data.pois.length > 0) {
          const results: PlaceSearchResult[] = res.data.pois
            .filter((item: any) => item.location)
            .map((item: any, index: number) => ({
              id: item.id || String(index),
              title: item.name || '',
              address: item.address || item.pname || '',
              latitude: item.location.split(',')[1] ? parseFloat(item.location.split(',')[1]) : 0,
              longitude: item.location.split(',')[0] ? parseFloat(item.location.split(',')[0]) : 0
            }));
          console.log('高德搜索解析结果:', results);
          resolve(results);
        } else {
          console.log('高德搜索无结果或失败:', res.data.info, 'count:', res.data.count);
          resolve([]);
        }
      },
      fail: (err) => {
        console.error('高德搜索请求失败:', err);
        reject(err);
      }
    });
  });
}
