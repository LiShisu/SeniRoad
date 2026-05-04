// app.ts
import { wechatLogin } from './utils/auth';

// 全局应用类型定义
interface IAppOption {
  globalData: {
    userInfo: any;
    userType: string;
  };
  onLaunch(): void;
  checkLoginState(): void;
  login(): Promise<void>;
  switchToCorrectHomePage(): void;
  getUserInfo(code: string): any;
}

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


    // 延迟执行存储操作，避免 "too early" 错误
    setTimeout(() => {
      this.checkLoginState();
    }, 300);
  },

  // 检查登录状态
  checkLoginState() {
    try {
      // 检查是否已有登录状态（使用安全的方式）
      let accessToken = '';
      let userType = '';
      try {
        accessToken = wx.getStorageSync('access_token');
        userType = wx.getStorageSync('userType');
      } catch (e) {
        console.log('存储系统尚未就绪，稍后重试...');
        // 存储系统未就绪，稍后再检查
        setTimeout(() => {
          this.checkLoginState();
        }, 200);
        return;
      }

      if (accessToken) {
        // 已有登录状态，检查用户类型
        if (userType) {
          this.globalData.userType = userType;
          this.switchToCorrectHomePage();
        } else {
          // 有token但无用户类型，重新登录
          this.login();
        }
      } else {
        // 无登录状态，跳转到登录页
        console.log('无登录状态，跳转到登录页');
        wx.showToast({
          title: '请先登录',
          icon: 'none',
          duration: 2000, // 延长显示时间到2秒
        })
        wx.reLaunch({
          url: '/common/login/login'
        })
      }
    } catch (error) {
      console.error('检查登录状态失败:', error);
      // 失败时跳转到登录页
      wx.reLaunch({
        url: '/common/login/login'
      })
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
      // 未获取到用户类型，显示错误信息并跳转到登录页
      wx.showToast({
        title: '无法获取用户信息',
        icon: 'none',
        duration: 2000
      })
      setTimeout(() => {
        wx.reLaunch({
          url: '/common/login/login'
        })
      }, 2000)
    }
  },
  
  getUserInfo(code: string) {
    // 根据code获取用户信息的方法
    console.log('获取用户信息，code:', code);
    try {
      let userInfo = null;
      try {
        userInfo = wx.getStorageSync('userInfo');
      } catch (e) {
        console.warn('获取用户信息时存储系统未就绪');
      }
      return userInfo || null;
    } catch (error) {
      console.error('获取用户信息失败:', error);
      return null;
    }
  }
})