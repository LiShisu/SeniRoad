// records.ts
Page({
  data: {
    currentTab: 'month',
    stats: {
      trips: '28',
      distance: '15.6km',
      duration: '42h'
    },
    records: [
      {
        id: 1,
        time: '2026-03-23 上午',
        path: '- 家 - 永辉超市 - 家',
        distance: '2.3km',
        duration: '45分钟',
        deviation: false
      },
      {
        id: 2,
        time: '2026-03-22 下午',
        path: '- 家 - 公园 - 家',
        distance: '1.5km',
        duration: '1小时30分钟',
        deviation: true
      },
      {
        id: 3,
        time: '2026-03-21 上午',
        path: '- 家 - 市人民医院 - 家',
        distance: '5.2km',
        duration: '2小时',
        deviation: false
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
   * 标签切换
   */
  onTabChange(e: any) {
    this.setData({
      currentTab: e.detail.value
    })
  },

  /**
   * 查看轨迹详情
   */
  viewDetail(e: any) {
    const { id } = e.currentTarget.dataset
    wx.showToast({
      title: `查看轨迹${id}`,
      icon: 'none'
    })
  }
})
