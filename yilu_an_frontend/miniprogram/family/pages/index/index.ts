// index.ts
import { getCurrentElder } from '../../storage';

Page({
  data: {
    elderName: '请选择监护老人',
    currentLocation: '未获取到位置',
    lastUpdate: '未知',
    navigationStatus: '未出行',
    currentElderId: ''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    console.log('family index load')
    // checkAndRedirect('family')
    this.loadCurrentElderInfo();
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    this.loadCurrentElderInfo();
  },

  /**
   * 加载当前监护老人信息
   */
  loadCurrentElderInfo() {
    const currentElder = getCurrentElder();
    if (currentElder) {
      this.setData({
        elderName: currentElder.name,
        currentElderId: currentElder.id
      });
    }
  },

  /**
   * 切换老人
   */
  switchElder() {
    wx.showToast({
      title: '切换老人',
      icon: 'none'
    })
  },

  /**
   * 跳转预设常用地点
   */
  goToPlaces() {
    wx.navigateTo({
      url: '/family/pages/places/places'
    })
  },

  /**
   * 跳转出行记录
   */
  goToRecords() {
    wx.navigateTo({
      url: '/family/pages/records/records'
    })
  },

  /**
   * 跳转老人管理
   */
  goToElders() {
    wx.navigateTo({
      url: '/family/pages/elders/elders'
    })
  }
})
