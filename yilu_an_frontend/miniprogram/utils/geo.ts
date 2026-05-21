import { TENCENT_MAP_KEY, AMAP_KEY } from './config';
// utils/geo.ts
import AmapWX from './amap-wx.js'; // 🌟 确保引入了高德小程序SDK
const GAODE_KEY = AMAP_KEY; // 你的高德 KEY
const amapInstance = new AmapWX.AMapWX({ key: GAODE_KEY });
// 定位配置常量 - 统一设置
export const LOCATION_CONFIG: WechatMiniprogram.GetLocationOption = {
  type: 'gcj02',
  isHighAccuracy: true,
  highAccuracyExpireTime: 10000
};

// 统一的获取位置函数 - 返回 Promise
export function getLocation(options?: Partial<WechatMiniprogram.GetLocationOption>): Promise<WechatMiniprogram.GetLocationSuccessCallbackResult> {
  const config = { ...LOCATION_CONFIG, ...options };
  return new Promise((resolve, reject) => {
    wx.getLocation({
      ...config,
      success: (res) => resolve(res),
      fail: (err) => reject(err)
    });
  });
}
// 核心新增
// 1. 先定义高德逆地理编码返回的类型（解决TS报错核心）
interface AddressComponent {
  city: string;
  province: string;
}

interface RegeocodeData {
  addressComponent: AddressComponent;
}

interface AmapRegeoItem {
  regeocodeData: RegeocodeData;
}

// 继承微信原生定位结果，扩展city字段
export interface RealLocation extends WechatMiniprogram.GetLocationSuccessCallbackResult {
  city: string; 
}

export async function getRealLocation(options?: Partial<WechatMiniprogram.GetLocationOption>): Promise<RealLocation> {
  try {
    // 完美的复用：直接 await 你原本的 Promise 版本的 getLocation
    const geoRes = await getLocation(options);
    
    // 拿着拿到的经纬度，立刻去高德做逆地理编码
    return new Promise((resolve) => {
      amapInstance.getRegeo({
        location: `${geoRes.longitude},${geoRes.latitude}`,
        success: (regeoRes: AmapRegeoItem[]) => {
          console.log('🗺️ 高德动态逆地理感知成功:', regeoRes);
          
          const component = regeoRes[0].regeocodeData.addressComponent;
          let city = '';
          
          // 适老化脏数据清洗：直辖市（北京、上海等）的 city 字段为空，省份字段即为城市名
          if (typeof component.city === 'string' && component.city.length > 0) {
            city = component.city; 
          } else if (typeof component.province === 'string') {
            city = component.province; 
          }
          
          // 完美继承原 geoRes 的全部字段（latitude、longitude、accuracy等），并强行注入 city
          resolve({
            ...geoRes,
            city: city || '济南市' // 极限保底
          });
        },
        fail: (err: any) => {
          console.error('高德逆地理转换失败，降级使用保底城市:', err);
          resolve({
            ...geoRes,
            city: '济南市' // 降级保底城市，确保长辈端即使高德欠费也能正常步行导航
          });
        }
      });
    });
    
  } catch (error) {
    // 如果你原本的 getLocation 失败了（比如长辈没开GPS、拒绝了定位权限），直接向上抛出错误
    throw error;
  }
}
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
