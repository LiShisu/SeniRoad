import { checkAndRedirect, removeToken, removeUserRole } from '../../../utils/auth'
import { userApi } from '../../../api/user'

Page({
  data: {
    userInfo: {
      phone: '',
      nickname: '',
      role: '',
      avatar_url: '' as string | null,
      is_active: false,
      created_at: ''
    },
    loading: false
  },

  onLoad() {
    checkAndRedirect('family')
    this.getUserInfo()
  },

  onShow() {
    this.getUserInfo()
  },

  async getUserInfo() {
    this.setData({ loading: true })
    try {
      const userInfo = await userApi.getProfile()
      this.setData({ userInfo })
    } catch (error: any) {
      wx.showToast({ title: error.message || '获取用户信息失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  onReady() {

  },

  onHide() {

  },

  onUnload() {

  },

  onPullDownRefresh() {

  },

  onReachBottom() {

  },

  onShareAppMessage() {

  },

  handleMenuClick(_e: any) {
    wx.navigateTo({
      url: '/family/pages/editProfile/editProfile'
    })
  },

  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          removeToken();
          removeUserRole();
          
          wx.reLaunch({
            url: '/common/login/login'
          })
        }
      }
    })
  },

  navigateToPage(e: any) {
    const url = e.currentTarget.dataset.url
    wx.navigateTo({
      url: url
    })
  }
});