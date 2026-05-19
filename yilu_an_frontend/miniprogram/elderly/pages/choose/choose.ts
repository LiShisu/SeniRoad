const recorderManager = wx.getRecorderManager();

Page({
  data: {
    isRecording: false
  },

  onShow() {
    this.initRecorder();
  },

  initRecorder() {
      // 监听录音开始
    recorderManager.onStart(() => {
      this.setData({ isRecording: true });
      wx.showToast({ title: '正在聆听...', icon: 'none', duration: 60000 });
    });
    recorderManager.onStop(async (res) => {
      this.setData({ isRecording: false });
      const { tempFilePath } = res;
      // 获取位置

      // 带着音频路径和经纬度，秒切到 plan 页面
      wx.navigateTo({
        url: `/elderly/pages/plan/plan?audioPath=${encodeURIComponent(tempFilePath)}`
      });
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
