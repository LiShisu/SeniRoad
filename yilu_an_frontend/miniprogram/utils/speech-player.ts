import { speechApi } from '../api/speech';

export interface AudioPlayer {
  stop: () => void;
  play: () => void;
  src: string;
}

export const playSpeech = async (
  text: string,
  audioPlayer: AudioPlayer | null,
  initAudioContext: () => AudioPlayer
): Promise<void> => {
  if (!audioPlayer) {
    audioPlayer = initAudioContext();
  }

  const speakText = text.replace(/<[^>]+>/g, '');
  console.log('speakText:', speakText);
  if (!speakText) return;

  try {
    const audioBuffer = await speechApi.textToSpeech({ text: speakText });
    
    if (audioBuffer) {
      const fs = wx.getFileSystemManager();
      const filePath = `${wx.env.USER_DATA_PATH}/current_nav_voice.mp3`;
      
      return new Promise((resolve) => {
        fs.writeFile({
          filePath: filePath,
          data: audioBuffer,
          encoding: 'binary',
          success: () => {
            console.log('语音文件缓存/覆盖成功:', filePath);
            audioPlayer!.stop();
            audioPlayer!.src = filePath;
            audioPlayer!.play();
            resolve();
          },
          fail: (err) => {
            console.error('写入音频文件失败:', err);
            resolve();
          }
        });
      });
    }
  } catch (err) {
    console.error('TTS请求失败:', err);
  }
};