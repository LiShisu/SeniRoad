// index.ts
import { checkAndRedirect } from '../../../utils/auth'
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

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    // 检查用户类型权限
    checkAndRedirect('elderly')
    this.getUserInfo()
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    this.getUserInfo()
  },

  // 获取用户信息
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

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },



  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  },



  /**
   * 点击菜单
   */
  handleMenuClick(_e: any) {
    // 跳转到编辑个人资料页面
    wx.navigateTo({
      url: '/elderly/pages/editProfile/editProfile'
    })
  },

  /**
   * 退出登录
   */
  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除登录状态
          wx.removeStorageSync('access_token')
          wx.removeStorageSync('userType')
          
          // 跳转到登录页面
          wx.reLaunch({
            url: '/common/login/login'
          })
        }
      }
    })
  },

  /**
   * 导航到其他页面
   */
  navigateToPage(e: any) {
    const url = e.currentTarget.dataset.url
    wx.navigateTo({
      url: url
    })
  }
});