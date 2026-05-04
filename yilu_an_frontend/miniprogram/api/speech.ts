// 语音合成相关接口
import { api } from '../utils/request';

export interface TextToSpeechRequest {
  text: string;
}

export interface TextToSpeechResponse {
  status: string;
  audio_data: string;
  audio_type: string;
}

export const speechApi = {
  textToSpeech: (data: TextToSpeechRequest) => {
    return api.post<TextToSpeechResponse>('/speech/text-to-speech', data);
  },
};