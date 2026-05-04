// common/login/login.ts
import { wechatLogin, phoneLogin } from '../../utils/auth';

Page({
  data: {
    wechatLoading: false,
    phoneLoading: false,
    showPhoneInput: false,
    showWechatLogin: false,
    phoneNumber: '',
    selectedRole: '',
    hidePhoneButton: false,
    hideWechatButton: false,
  },

  // 切换微信登录区域显示
  toggleWechatLogin() {
    const isShowing = this.data.showWechatLogin;

    if (isShowing) {
      this.setData({
        showWechatLogin: false,
        hidePhoneButton: false,
        selectedRole: ''
      });
    } else {
      this.setData({
        showWechatLogin: true,
        showPhoneInput: false,
        hidePhoneButton: true,
        hideWechatButton: false,
        selectedRole: ''
      });
    }
  },

  // 选择身份
  selectRole(e: any) {
    const role = e.currentTarget.dataset.role;
    this.setData({
      selectedRole: role
    });
  },

  // 确认微信登录
  async confirmWechatLogin() {
    if (!this.data.selectedRole) {
      wx.showToast({
        title: '请选择身份',
        icon: 'none',
      });
      return;
    }

    this.setData({ wechatLoading: true });

    try {
      const role = await wechatLogin(this.data.selectedRole as 'elderly' | 'family');

      wx.showToast({ title: `登录成功`, icon: 'success' });
      setTimeout(() => {
        wx.reLaunch({ url: `/${role}/pages/index/index` });
      }, 1000);
    } catch (error: any) {
      wx.showToast({
        title: '登录失败，请先注册',
        icon: 'none',
        duration: 2000,
        success: () => {
          setTimeout(() => {
            wx.reLaunch({ url: '/common/register/register' });
          }, 1500);
        }
      });
      setTimeout(() => {
        wx.reLaunch({ url: '/common/register/register' });
      }, 2500);
    } finally {
      this.setData({ wechatLoading: false });
    }
  },

  // 切换手机号输入框显示
  togglePhoneInput() {
    const isShowing = this.data.showPhoneInput;

    if (isShowing) {
      this.setData({
        showPhoneInput: false,
        hideWechatButton: false,
        phoneNumber: ''
      });
    } else {
      this.setData({
        showPhoneInput: true,
        showWechatLogin: false,
        hideWechatButton: true,
        hidePhoneButton: false,
        phoneNumber: ''
      });
    }
  },

  // 手机号输入
  onPhoneInput(e: any) {
    this.setData({
      phoneNumber: e.detail.value
    });
  },

  // 提交手机号登录
  async submitPhoneLogin() {
    const phone = this.data.phoneNumber;

    if (!phone || phone.length !== 11) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none',
      });
      return;
    }

    this.setData({ phoneLoading: true });

    try {
      const role = await phoneLogin(phone);

      wx.showToast({ title: `登录成功`, icon: 'success' });
      setTimeout(() => {
        wx.reLaunch({ url: `/${role}/pages/index/index` });
      }, 1000);
    } catch (error: any) {
      wx.showToast({
        title: '登录失败，请先注册',
        icon: 'none',
        duration: 2000,
        success: () => {
          setTimeout(() => {
            wx.reLaunch({ url: '/common/register/register' });
          }, 1500);
        }
      });
      setTimeout(() => {
        wx.reLaunch({ url: '/common/register/register' });
      }, 2500);
    } finally {
      this.setData({ phoneLoading: false });
    }
  },
});
