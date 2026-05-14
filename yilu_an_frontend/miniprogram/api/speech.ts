// 语音合成相关接口
import { api } from '../utils/request';

export interface TextToSpeechRequest {
  text: string;
}

export interface TextToSpeechResponse {
  // status: string;
  audio_data: string;
  audio_type: string;
}

export const speechApi = {
  textToSpeech: (data: TextToSpeechRequest) => {
    return api.post<TextToSpeechResponse>('/audio/tts', data);
  },
};

export const speechApi2 = {
  speechToText: (audio_file: any) => {
    return api.post<any>('/audio/asr', { audio_file });
  }
};