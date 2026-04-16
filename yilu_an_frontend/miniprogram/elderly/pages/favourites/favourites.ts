// elder/pages/favourites/favourites.ts
import { checkAndRedirect } from '../../../utils/auth'

Page({

  /**
   * 页面的初始数据
   */
  data: {
    places: [
      {
        id: 1,
        name: '家',
        address: '北京市朝阳区建国路88号',
        type: 'home'
      },
      {
        id: 2,
        name: '北京协和医院',
        address: '北京市东城区帅府园1号',
        type: 'hospital'
      },
      {
        id: 3,
        name: '三里屯菜市场',
        address: '北京市朝阳区三里屯路19号',
        type: 'market'
      },
      {
        id: 4,
        name: '朝阳公园',
        address: '北京市朝阳区朝阳公园南路1号',
        type: 'park'
      }
    ]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    // 检查用户类型权限
    checkAndRedirect('elderly')
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
   * 选择地点
   */
  selectPlace(e: any) {
    // 实际项目中这里可以显示地点详情
    wx.showToast({
      title: '选择地点',
      icon: 'none'
    })
  },

  /**
   * 导航到地点
   */
  navigateToPlace(e: any) {
    // 实际项目中这里应该跳转到导航页面
    wx.navigateTo({
      url: '/elderly/pages/navigate/navigate?destination=家'
    })
  },

  /**
   * 编辑地点
   */
  editPlace(e: any) {
    // 实际项目中这里应该跳转到编辑页面
    wx.showToast({
      title: '编辑地点',
      icon: 'none'
    })
  },

  /**
   * 添加新地点
   */
  addNewPlace() {
    // 实际项目中这里应该跳转到添加页面
    wx.showToast({
      title: '添加新地点',
      icon: 'none'
    })
  }
})