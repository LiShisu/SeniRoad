const recorderManager = wx.getRecorderManager();
import { getRealLocation } from '../../../utils/geo';
Page({
  data: {
    isRecording: false
  },

  onShow() {
    this.initRecorder();
  },

  initRecorder() {
    recorderManager.onStart(() => {
      this.setData({ isRecording: true });
      wx.showToast({ title: '正在聆听...', icon: 'none', duration: 60000 });
    });
    
    recorderManager.onStop(async (res) => {
      this.setData({ isRecording: false });
      const { tempFilePath } = res;

      // 🌟 核心修复 1：在跳转前，获取当前的定位，用于提取城市（公交必需）
      try {
        const location = await getRealLocation(); // 确保文件顶部引入了 your geo utils
        const curLat = location.latitude.toString();
        const curLng = location.longitude.toString();
        const realCity = location.city;
        // 假设这里默认给长辈推荐公交模式 'transit'，城市默认为 '济南市'
        // 后续可以通过逆地理编码让 city 变成动态的
        const defaultMode = 'transit'; 
        wx.navigateTo({
          url: `/elderly/pages/plan/plan?audioPath=${encodeURIComponent(tempFilePath)}&travelMode=${defaultMode}&city=${encodeURIComponent(realCity)}`
        });
        
      } catch (err) {
        console.error('语音录制结束获取位置失败:', err);
        // 兜底：如果获取不到，也至少传个保底城市，防止后端崩溃
        wx.navigateTo({
          url: `/elderly/pages/plan/plan?audioPath=${encodeURIComponent(tempFilePath)}&travelMode=walking&city=${encodeURIComponent('济南市')}`
        });
      }
    });
  },
  handleTouchStart() {
    // 开始录音，后端 ASR 需要 wav 格式，这里配置为 wav
    recorderManager.start({
      duration: 15000, // 最长录音 15 秒
      sampleRate: 16000,
      numberOfChannels: 1,
      encodeBitRate: 48000,
      format: 'wav' 
    });
  },

  handleTouchEnd() {
    // 松开手指，停止录音
    if (this.data.isRecording) {
      recorderManager.stop();
    }
  },

  goBack() {
    wx.navigateBack();
  },
  goToPlaces() {
    wx.navigateTo({ url: '/elderly/pages/places/places' });
  },
  goToContact() {
    wx.navigateTo({ url: '/elderly/pages/contact/contact' });
  }
});
