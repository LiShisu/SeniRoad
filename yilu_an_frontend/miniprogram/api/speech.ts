// 语音合成相关接口
import { api } from '../utils/request';

export interface TextToSpeechRequest {
  text: string;
}

export const speechApi = {
  textToSpeech: (data: TextToSpeechRequest) => {
    return api.post<ArrayBuffer>('/audio/tts', data, undefined, { responseType: 'arraybuffer' });
  },
  speechToText: (audio_file: any) => {
    return api.post<any>('/audio/asr', { audio_file });
  }
};
