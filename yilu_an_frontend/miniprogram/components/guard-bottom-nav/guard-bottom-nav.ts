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
    homeIcon: '/family/images/home.png',
    homeActiveIcon: '/family/images/home_active.png',
    // 位置相关配置
    locationIcon: '/family/images/map.png',
    locationActiveIcon: '/family/images/map_active.png',
    // 个人中心相关配置
    profileIcon: '/family/images/profile.png',
    profileActiveIcon: '/family/images/profile_active.png'
  },

  /**
   * 组件的方法列表
   */
  methods: {

  }
})
