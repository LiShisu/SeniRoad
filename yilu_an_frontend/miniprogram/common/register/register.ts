// common/register/register.ts
import { authApi, RegisterParams } from '../../api/auth';

Page({
  data: {
    phone: '',
    nickname: '',
    role: 'elderly', // 默认角色为老人
    loading: false,
  },

  // 手机号输入变化
  onPhoneChange(e: any) {
    this.setData({
      phone: e.detail.value,
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

  // 注册
  async register() {
    const { phone, nickname, role } = this.data;

    // 验证输入
    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' });
      return;
    }

    // 验证手机号格式
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phoneRegex.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号格式', icon: 'none' });
      return;
    }

    // 显示加载状态
    this.setData({ loading: true });

    try {
      // 调用微信登录接口获取code
      const wxLoginResult = await new Promise<any>((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject,
        });
      });

      // 调用后端微信注册接口
      await authApi.wechatRegister({
        code: wxLoginResult.code,
        role: role as 'elderly' | 'family',
        nickname: nickname,
        phone: phone,
      });

      // 注册成功，跳转到登录页面
      wx.showToast({ title: '注册成功', icon: 'success' });
      wx.redirectTo({ url: '/common/login/login' });
    } catch (error: any) {
      wx.showToast({ title: error.message || '注册失败', icon: 'none' });
    } finally {
      // 隐藏加载状态
      this.setData({ loading: false });
    }
  },
});
