// elder/pages/login/login.ts
import { authApi } from '../../../api/auth';

Page({
  data: {
    phone: '',
    password: '',
    showPassword: false,
    loading: false,
    wechatLoading: false,
  },

  // 手机号输入变化
  onPhoneChange(e: any) {
    this.setData({
      phone: e.detail.value,
    });
  },

  // 密码输入变化
  onPasswordChange(e: any) {
    this.setData({
      password: e.detail.value,
    });
  },

  // 切换密码显示/隐藏
  togglePassword() {
    this.setData({
      showPassword: !this.data.showPassword,
    });
  },

  // 登录
  async login() {
    const { phone, password } = this.data;

    // 验证输入
    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' });
      return;
    }

    if (!password) {
      wx.showToast({ title: '请输入密码', icon: 'none' });
      return;
    }

    // 显示加载状态
    this.setData({ loading: true });

    try {
      // 调用登录接口
      const response = await authApi.login({
        username: phone,
        password: password,
      });

      // 保存token
      wx.setStorageSync('access_token', response.access_token);

      // 登录成功，跳转到首页
      wx.showToast({ title: '登录成功', icon: 'success' });
      wx.redirectTo({ url: '/elder/pages/index/index' });
    } catch (error: any) {
      wx.showToast({ title: error.message || '登录失败', icon: 'none' });
    } finally {
      // 隐藏加载状态
      this.setData({ loading: false });
    }
  },

  // 微信快捷登录
  async wechatLogin() {
    // 显示加载状态
    this.setData({ wechatLoading: true });

    try {
      // 调用微信登录接口获取code
      const wxLoginResult = await new Promise<any>((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject,
        });
      });

      // 调用微信code2Session接口获取openid和session_key
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

      // 获取用户信息
      const userInfoResult = await new Promise<any>((resolve, reject) => {
        wx.getUserProfile({
          desc: '用于完善用户资料',
          success: resolve,
          fail: reject
        });
      });

      // 调用后端微信登录接口
      const response = await authApi.wechatLogin(code2SessionResult.openid, code2SessionResult.session_key);

      // 保存token和用户信息
      wx.setStorageSync('access_token', response.access_token);
      wx.setStorageSync('userInfo', {
        ...userInfoResult.userInfo,
        openid: code2SessionResult.openid
      });

      // 保存用户类型（实际项目中应该从后端返回）
      const userType = 'elder'; // 可以根据实际情况修改
      wx.setStorageSync('userType', userType);

      // 登录成功，跳转到首页
      wx.showToast({ title: '登录成功', icon: 'success' });
      wx.redirectTo({ url: '/elder/pages/index/index' });
    } catch (error: any) {
      wx.showToast({ title: error.message || '微信登录失败', icon: 'none' });
    } finally {
      // 隐藏加载状态
      this.setData({ wechatLoading: false });
    }
  },
});
