// elderly/pages/choose/choose.ts
Page({
  data: {
    isRecording: false
  },

  onLoad() {
  },

  goBack() {
    wx.navigateBack();
  },

  startVoice() {
    wx.showToast({
      title: '语音识别功能开发中',
      icon: 'none'
    });
  },

  goToPlaces() {
    wx.navigateTo({
      url: '/elderly/pages/places/places'
    });
  },

  goToContact() {
    wx.navigateTo({
      url: '/elderly/pages/contact/contact'
    });
  }
})