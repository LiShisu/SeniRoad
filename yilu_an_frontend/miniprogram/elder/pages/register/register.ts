// elder/pages/register/register.ts
import { authApi, RegisterParams } from '../../../api/auth';

Page({
  data: {
    phone: '',
    password: '',
    confirmPassword: '',
    nickname: '',
    role: 'elderly', // 默认角色为老人
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

  // 确认密码输入变化
  onConfirmPasswordChange(e: any) {
    this.setData({
      confirmPassword: e.detail.value,
    });
  },

  // 昵称输入变化
  onNicknameChange(e: any) {
    this.setData({
      nickname: e.detail.value,
    });
  },

  // 选择角色
  selectRole(e: any) {
    const role = e.currentTarget.dataset.role;
    this.setData({
      role: role,
    });
  },

  // 切换密码显示/隐藏
  togglePassword() {
    this.setData({
      showPassword: !this.data.showPassword,
    });
  },

  // 注册
  async register() {
    const { phone, password, confirmPassword, nickname, role } = this.data;

    // 验证输入
    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' });
      return;
    }

    if (password.length < 6) {
      wx.showToast({ title: '密码至少需要6位', icon: 'none' });
      return;
    }

    if (password !== confirmPassword) {
      wx.showToast({ title: '两次输入的密码不一致', icon: 'none' });
      return;
    }

    // 显示加载状态
    this.setData({ loading: true });

    try {
      // 准备注册参数
      const params: RegisterParams = {
        phone,
        password,
        nickname,
        role: role as 'elderly' | 'family',
      };

      // 调用注册接口
      await authApi.register(params);

      // 注册成功，跳转到登录页面
      wx.showToast({ title: '注册成功', icon: 'success' });
      wx.redirectTo({ url: '/elder/pages/login/login' });
    } catch (error: any) {
      wx.showToast({ title: error.message || '注册失败', icon: 'none' });
    } finally {
      // 隐藏加载状态
      this.setData({ loading: false });
    }
  },

  // 微信快捷注册
  async wechatRegister() {
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

      // 获取用户信息（可选）
      const userInfoResult = await new Promise<any>((resolve, reject) => {
        wx.getUserProfile({
          desc: '用于完善用户资料',
          success: resolve,
          fail: reject
        });
      });

      // 准备微信注册参数
      const wechatData = {
        openid: code2SessionResult.openid,
        session_key: code2SessionResult.session_key,
        nickname: userInfoResult.userInfo.nickName,
        avatar_url: userInfoResult.userInfo.avatarUrl,
        role: this.data.role as 'elderly' | 'family'
      };

      // 调用后端微信注册接口
      await authApi.wechatRegister(wechatData);

      // 注册成功，跳转到登录页面
      wx.showToast({ title: '注册成功', icon: 'success' });
      wx.redirectTo({ url: '/elder/pages/login/login' });
    } catch (error: any) {
      wx.showToast({ title: error.message || '微信注册失败', icon: 'none' });
    } finally {
      // 隐藏加载状态
      this.setData({ wechatLoading: false });
    }
  },
});
