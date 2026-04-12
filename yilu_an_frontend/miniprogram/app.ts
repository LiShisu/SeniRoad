// app.ts
import { authApi } from './api/auth';

App<IAppOption>({
  globalData: {
    userInfo: undefined,
    userType: '' // 'elder' 或 'guard'
  },
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

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
    wx.showLoading({ title: '正在登录...' });
    
    try {
      // 1. 调用微信登录接口获取code
      const wxLoginResult = await new Promise<any>((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject,
        });
      });

      // 2. 调用微信code2Session接口获取openid和session_key
      const code2SessionResult = await new Promise<any>((resolve, reject) => {
        wx.request({
          url: `https://api.weixin.qq.com/sns/jscode2session`,
          method: 'GET',
          data: {
            appid: 'YOUR_APPID', // 替换为你的小程序AppID
            secret: 'YOUR_APPSECRET', // 替换为你的小程序AppSecret
            js_code: wxLoginResult.code,
            grant_type: 'authorization_code'
          },
          success: resolve,
          fail: reject
        });
      });

      // 3. 获取用户信息
      const userInfoResult = await new Promise<any>((resolve, reject) => {
        wx.getUserProfile({
          desc: '用于完善用户资料',
          success: resolve,
          fail: reject
        });
      });

      // 4. 调用后端微信登录接口
      const response = await authApi.wechatLogin(code2SessionResult.openid, code2SessionResult.session_key);

      // 5. 保存token和用户信息
      wx.setStorageSync('access_token', response.access_token);
      wx.setStorageSync('userInfo', {
        ...userInfoResult.userInfo,
        openid: code2SessionResult.openid
      });

      // 6. 模拟获取用户类型（实际项目中应该从后端返回）
      // 这里暂时默认设置为老人用户
      const userType = 'elder'; // 可以根据实际情况修改
      this.globalData.userType = userType;
      wx.setStorageSync('userType', userType);

      // 7. 隐藏加载提示
      wx.hideLoading();
      wx.showToast({ title: '登录成功', icon: 'success' });

      // 8. 跳转到对应首页
      this.switchToCorrectHomePage();
    } catch (error: any) {
      // 隐藏加载提示
      wx.hideLoading();
      console.error('登录失败:', error);
      wx.showToast({
        title: error.message || '登录失败，请重试',
        icon: 'none'
      });
    }
  },
  
  switchToCorrectHomePage() {
    const userType = this.globalData.userType
    
    if (userType === 'elder') {
      // 跳转到老人端首页
      wx.reLaunch({
        url: '/elder/pages/index/index'
      })
    } else if (userType === 'guard') {
      // 跳转到监护人端首页
      wx.reLaunch({
        url: '/guard/pages/index/index'
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