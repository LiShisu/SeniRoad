// app.ts
import { wechatLogin } from './utils/auth';

App<IAppOption>({
  globalData: {
    userInfo: undefined,
    userType: '' // 'elderly' 或 'family'
  },
  onLaunch() {
    // 展示本地存储能力
    // const logs = wx.getStorageSync('logs') || []
    // logs.unshift(Date.now())
    // wx.setStorageSync('logs', logs)

    // 检查是否已有登录状态
    const accessToken = wx.getStorageSync('access_token');
    if (accessToken) {
      // 已有登录状态，检查用户类型
      const userType = wx.getStorageSync('userType');
      if (userType) {
        this.globalData.userType = userType;
        this.switchToCorrectHomePage();
      } else {
        // 有token但无用户类型，重新登录
        this.login();
      }
    } else {
      // 无登录状态，执行登录
      this.login();
    }
  },
  
  async login() {
    try {
      // 调用 auth.ts 中的微信登录函数
      await wechatLogin();
      // 跳转到对应首页
      this.switchToCorrectHomePage();
    } catch (error: any) {
      console.error('登录失败:', error);
      // 错误处理已在 wechatLogin 函数中完成
    }
  },
  
  switchToCorrectHomePage() {
    const userType = this.globalData.userType
    
    if (userType === 'elderly') {
      // 跳转到老人端首页
      wx.reLaunch({
        url: '/elderly/pages/index/index'
      })
    } else if (userType === 'family') {
      // 跳转到家属端首页
      wx.reLaunch({
        url: '/family/pages/index/index'
      })
    } else {
      // 未获取到用户类型，显示错误信息
      wx.showToast({
        title: '无法获取用户信息',
        icon: 'none'
      })
    }
  },
  
  getUserInfo(code: string) {
    // 根据code获取用户信息的方法
    // 这里可以实现通过code获取用户信息的逻辑
    console.log('获取用户信息，code:', code);
    wx.getStorageSync('userInfo');
  }
})