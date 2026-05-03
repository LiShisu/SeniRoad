// common/register/register.ts
import { authApi,} from '../../api/auth';
import { wechatLogin } from '../../utils/auth';

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

      // 注册成功，自动登录并跳转首页
      wx.showToast({ title: '注册成功，正在登录...', icon: 'success', duration: 1500 });
      
      // 延迟执行自动登录，确保用户能看到成功提示
      setTimeout(async () => {
        try {
          await wechatLogin(role as 'elderly' | 'family');
          wx.showToast({ title: '登录成功', icon: 'success', duration: 1500 });
          setTimeout(() => {
            wx.reLaunch({ url: `/${role}/pages/index/index` });
          }, 1000);
        } catch (error: any) {
          wx.showToast({ title: error.message || '自动登录失败，请手动登录', icon: 'none', duration: 2000 });
          setTimeout(() => {
            wx.redirectTo({ url: '/common/login/login' });
          }, 2000);
        }
      }, 1500);
    } catch (error: any) {
      wx.showToast({ title: error.message || '注册失败', icon: 'none' });
    } finally {
      // 隐藏加载状态
      this.setData({ loading: false });
    }
  },
});
