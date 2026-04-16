// common/login/login.ts
import { wechatLogin } from '../../utils/auth';

Page({
  data: {

  },

  // 微信快捷登录
  async wechatLogin() {
    // 显示加载提示
    wx.showLoading({ title: '正在登录...' });

    try {
      // 调用 auth.ts 中的微信登录函数
      const role = await wechatLogin();

      // 登录成功，跳转到首页
      wx.showToast({ title: `登录成功`, icon: 'success' });
      wx.redirectTo({ url: `/${role}/pages/index/index` });
    } catch (error: any) {
      wx.showToast({ title: error.message || '登录失败', icon: 'none' });
    } finally {
      // 隐藏加载状态
      wx.hideLoading();
    }
  },
});
