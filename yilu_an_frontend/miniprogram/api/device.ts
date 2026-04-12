// 设备相关接口
import { api } from '../utils/request';

// 创建设备请求参数
export interface CreateDeviceParams {
  user_id: number;
  device_token: string;
  device_model?: string;
  status?: 0 | 1;
}

// 更新设备请求参数
export interface UpdateDeviceParams {
  device_model?: string;
  status?: 0 | 1;
}

// 设备
export interface Device {
  device_id: number;
  user_id: number;
  device_token: string;
  device_model: string;
  status: number;
  created_at: string;
  updated_at: string;
}

// 设备相关API
export const deviceApi = {
  // 创建设备
  createDevice: (params: CreateDeviceParams) => {
    return api.post<Device>('/api/v1/devices/', params);
  },
  
  // 获取设备列表
  getDevices: (userId?: number) => {
    return api.get<Device[]>('/api/v1/devices/', { data: { user_id: userId } });
  },
  
  // 根据ID获取设备
  getDeviceById: (deviceId: number) => {
    return api.get<Device>(`/api/v1/devices/${deviceId}`);
  },
  
  // 根据设备token获取设备
  getDeviceByToken: (deviceToken: string) => {
    return api.get<Device>(`/api/v1/devices/token/${deviceToken}`);
  },
  
  // 更新设备
  updateDevice: (deviceId: number, params: UpdateDeviceParams) => {
    return api.put<Device>(`/api/v1/devices/${deviceId}`, params);
  },
  
  // 删除设备
  deleteDevice: (deviceId: number) => {
    return api.delete(`/api/v1/devices/${deviceId}`);
  },
  
  // 更新设备状态
  updateDeviceStatus: (deviceId: number, status: 0 | 1) => {
    return api.patch<Device>(`/api/v1/devices/${deviceId}/status/${status}`);
  },
};
