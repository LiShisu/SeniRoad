// map.ts
Page({
  data: {
    longitude: 116.397128,
    latitude: 39.907387,
    locationTitle: '北京市朝阳区XX小区附近',
    locationDetail: '朝阳北路与建国路交叉口东200米',
    updateTime: '更新于 刚刚',
    markers: [
      {
        id: 1,
        longitude: 116.397128,
        latitude: 39.907387,
        iconPath: '/assets/images/location-marker.png',
        width: 50,
        height: 50
      }
    ]
  },

  /**
   * 返回上一页
   */
  goBack() {
    wx.navigateBack()
  },

  /**
   * 打电话
   */
  makeCall() {
    wx.makePhoneCall({
      phoneNumber: '13800138000',
      success: () => {
        console.log('拨打电话成功')
      },
      fail: () => {
        console.log('拨打电话失败')
      }
    })
  },

  /**
   * 发消息
   */
  sendMessage() {
    wx.showToast({
      title: '发消息功能',
      icon: 'none'
    })
  },

  /**
   * 页面加载
   */
  onLoad() {
    // 获取当前位置
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        this.setData({
          latitude: res.latitude,
          longitude: res.longitude
        })
      }
    })
  }
})
