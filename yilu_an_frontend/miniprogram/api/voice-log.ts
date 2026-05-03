// 语音日志相关接口
import { api } from '../utils/request';

// 创建语音日志请求参数
export interface CreateVoiceLogParams {
  user_id: number;
  device_id: number;
  voice_text: string;
  audio_url?: string;
  duration?: number;
}

// 更新语音日志请求参数
export interface UpdateVoiceLogParams {
  voice_text?: string;
  audio_url?: string;
  duration?: number;
}

// 语音日志
export interface VoiceLog {
  id: number;
  user_id: number;
  device_id: number;
  voice_text: string;
  audio_url: string | null;
  duration: number | null;
  created_at: string;
  updated_at: string;
}

// 语音日志相关API
export const voiceLogApi = {
  // 创建语音日志
  createLog: (params: CreateVoiceLogParams) => {
    return api.post<VoiceLog>('/voice-logs/', params);
  },
  
  // 获取用户的语音日志列表
  getUserLogs: (userId: number, limit?: number) => {
    return api.get<VoiceLog[]>('/voice-logs/', { data: { user_id: userId, limit } });
  },
  
  // 根据设备ID获取语音日志列表
  getDeviceLogs: (deviceId: number, limit?: number) => {
    return api.get<VoiceLog[]>(`/voice-logs/device/${deviceId}`, { data: { limit } });
  },
  
  // 根据时间范围获取语音日志
  getLogsByTimeRange: (userId: number, startTime: string, endTime: string) => {
    return api.get<VoiceLog[]>(`/voice-logs/time-range/${userId}`, {
      data: { start_time: startTime, end_time: endTime }
    });
  },
  
  // 获取最近几小时的语音日志
  getRecentLogs: (userId: number, hours?: number) => {
    return api.get<VoiceLog[]>(`/voice-logs/recent/${userId}`, { data: { hours } });
  },
  
  // 根据ID获取语音日志
  getLogById: (logId: number) => {
    return api.get<VoiceLog>(`/voice-logs/${logId}`);
  },
  
  // 更新语音日志
  updateLog: (logId: number, params: UpdateVoiceLogParams) => {
    return api.put<VoiceLog>(`/voice-logs/${logId}`, params);
  },
  
  // 删除语音日志
  deleteLog: (logId: number) => {
    return api.delete(`/voice-logs/${logId}`);
  },
};
