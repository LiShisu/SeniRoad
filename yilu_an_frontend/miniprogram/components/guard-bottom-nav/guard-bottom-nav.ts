Component({
  /**
   * 组件的属性列表
   */
  properties: {
    // 当前激活的项目
    activeItem: {
      type: String,
      value: 'home'
    }
  },

  /**
   * 组件的初始数据
   */
  data: {
    // 首页相关配置
    homeIcon: '/guard/images/home.png',
    homeActiveIcon: '/guard/images/home_active.png',
    // 位置相关配置
    locationIcon: '/guard/images/map.png',
    locationActiveIcon: '/guard/images/map_active.png',
    // 个人中心相关配置
    profileIcon: '/guard/images/profile.png',
    profileActiveIcon: '/guard/images/profile_active.png'
  },

  /**
   * 组件的方法列表
   */
  methods: {

  }
})
