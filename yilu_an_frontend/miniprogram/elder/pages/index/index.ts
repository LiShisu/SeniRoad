// elder/pages/index/index.ts
Page({

  /**
   * 页面的初始数据
   */
  data: {

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    this.checkLoginStatus();
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    this.checkLoginStatus();
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('access_token');
    if (!token) {
      // 未登录，使用微信小程序自带的获取用户信息方式登录
      this.loginWithWeChat();
    }
  },

  // 使用微信登录
  loginWithWeChat() {
    wx.getUserProfile({
      desc: '用于完善会员资料',
      success: (res) => {
        // 获取用户信息成功
        const userInfo = res.userInfo;
        console.log('用户信息:', userInfo);
        
        // 这里需要调用登录接口获取token
        // 假设调用登录接口的函数为 loginApi
        // 实际项目中需要替换为真实的登录接口调用
        this.loginApi(userInfo);
      },
      fail: (err) => {
        // 用户拒绝授权
        console.log('用户拒绝授权:', err);
        // 可以提示用户需要授权才能使用小程序
        wx.showToast({
          title: '需要授权才能使用小程序',
          icon: 'none'
        });
      }
    });
  },

  // 登录接口调用（示例）
  loginApi(userInfo) {
    // 实际项目中需要替换为真实的登录接口调用
    // 这里模拟登录成功，生成token
    const mockToken = 'mock_token_' + Date.now();
    
    // 存储token
    wx.setStorageSync('access_token', mockToken);
    
    // 登录成功提示
    wx.showToast({
      title: '登录成功',
      icon: 'success'
    });
    
    // 可以在这里刷新页面数据
    // this.loadData();
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },



  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})