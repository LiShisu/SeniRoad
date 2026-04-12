// elder/pages/home/home.ts
import { checkAndRedirect } from '../../../utils/auth'

Page({

  /**
   * 页面的初始数据
   */
  data: {
    currentTime: ''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    // 检查用户类型权限
    checkAndRedirect('elder')
    
    // 更新时间
    this.updateTime()
    setInterval(() => {
      this.updateTime()
    }, 1000)
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

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
   * 更新时间
   */
  updateTime() {
    const now = new Date()
    const hours = now.getHours().toString().padStart(2, '0')
    const minutes = now.getMinutes().toString().padStart(2, '0')
    const seconds = now.getSeconds().toString().padStart(2, '0')
    this.setData({
      currentTime: `${hours}:${minutes}:${seconds}`
    })
  },

  /**
   * 开始录音
   */
  startRecord() {
    wx.showToast({
      title: '开始录音',
      icon: 'none'
    })
    // 实际项目中这里应该调用录音API
  },

  /**
   * 停止录音
   */
  stopRecord() {
    wx.showToast({
      title: '录音结束',
      icon: 'none'
    })
    // 实际项目中这里应该停止录音并处理语音识别
  },

  /**
   * 搜索
   */
  onSearch(e: any) {
    const keyword = e.detail.value
    if (keyword) {
      this.navigateToPlace(keyword)
    }
  },

  /**
   * 前往家
   */
  goToHome() {
    this.navigateToPlace('家')
  },

  /**
   * 前往医院
   */
  goToHospital() {
    this.navigateToPlace('医院')
  },

  /**
   * 前往菜市场
   */
  goToMarket() {
    this.navigateToPlace('菜市场')
  },

  /**
   * 前往公园
   */
  goToPark() {
    this.navigateToPlace('公园')
  },

  /**
   * 导航到指定地点
   */
  navigateToPlace(place: string) {
    wx.navigateTo({
      url: `/elder/pages/navigate/navigate?destination=${encodeURIComponent(place)}`
    })
  },

  /**
   * 紧急求助
   */
  callEmergency() {
    wx.showModal({
      title: '紧急求助',
      content: '确定要联系紧急联系人吗？',
      success: (res) => {
        if (res.confirm) {
          // 实际项目中这里应该调用紧急联系人
          wx.showToast({
            title: '正在联系紧急联系人',
            icon: 'none'
          })
        }
      }
    })
  }
})