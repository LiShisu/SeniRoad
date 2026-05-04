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
    homeIcon: '/assets/svg/home-icon.svg',
    homeActiveIcon: '/assets/svg/home-icon-active.svg',
    // 位置相关配置
    locationIcon: '/assets/svg/loc-icon.svg',
    locationActiveIcon: '/assets/svg/loc-icon-active.svg',
    // 个人中心相关配置
    profileIcon: '/assets/svg/profile-icon.svg',
    profileActiveIcon: '/assets/svg/profile-icon-active.svg'
  },

  /**
   * 组件的方法列表
   */
  methods: {

  }
})
