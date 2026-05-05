import { api } from '../utils/request';

// 来源类型枚举
export enum SourceType {
  FAMILY_PRESET = 1,
  AUTO_DETECTED = 2,
}

// 常用地点类型
export interface FavoritePlace {
  place_id: number;
  user_id: number;
  place_name: string;
  latitude: number;
  longitude: number;
  address: string;
  source_type: SourceType;
  tag_id?: number;
  is_active: boolean;
}

// 创建常用地点请求参数
export interface CreateFavoritePlaceParams {
  user_id?: number;
  place_name: string;
  latitude: number;
  longitude: number;
  address: string;
  source_type?: SourceType;
  tag_id?: number;
  is_active?: boolean;
}

// 更新常用地点请求参数
export interface UpdateFavoritePlaceParams {
  place_name?: string;
  latitude?: number;
  longitude?: number;
  address?: string;
  source_type?: SourceType;
  tag_id?: number;
  is_active?: boolean;
}

// 获取常用地点列表查询参数
export interface GetFavoritePlacesParams {
  user_id?: number;
  source_type?: SourceType;
  tag_id?: number;
  active_only?: boolean;
}

// 常用地点相关API
export const favoritePlacesApi = {
  // 创建常用地点
  createFavoritePlace: (params: CreateFavoritePlaceParams) => {
    return api.post<FavoritePlace>('/favorite-places/', params);
  },

  // 获取常用地点列表
  getFavoritePlaces: (params?: GetFavoritePlacesParams) => {
    const queryParts: string[] = [];
    if (params?.user_id !== undefined) queryParts.push(`user_id=${params.user_id}`);
    if (params?.source_type !== undefined) queryParts.push(`source_type=${params.source_type}`);
    if (params?.tag_id !== undefined) queryParts.push(`tag_id=${params.tag_id}`);
    if (params?.active_only !== undefined) queryParts.push(`active_only=${params.active_only}`);
    
    const url = queryParts.length ? `/favorite-places/?${queryParts.join('&')}` : '/favorite-places/';
    return api.get<FavoritePlace[]>(url);
  },

  // 根据ID获取常用地点
  getFavoritePlaceById: (placeId: number) => {
    return api.get<FavoritePlace>(`/favorite-places/${placeId}`);
  },

  // 更新常用地点
  updateFavoritePlace: (placeId: number, data: UpdateFavoritePlaceParams) => {
    return api.put<FavoritePlace>(`/favorite-places/${placeId}`, data);
  },

  // 删除常用地点
  deleteFavoritePlace: (placeId: number) => {
    return api.delete(`/favorite-places/${placeId}`);
  },

  // 停用常用地点
  deactivateFavoritePlace: (placeId: number) => {
    return api.put<FavoritePlace>(`/favorite-places/${placeId}/deactivate`);
  },
};
