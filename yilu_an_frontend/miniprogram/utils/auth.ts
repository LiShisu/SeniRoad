// 权限检查工具

/**
 * 检查用户是否有权限访问当前页面
 * @param requiredType 需要的用户类型 ('elder' 或 'guard')
 * @returns 是否有权限
 */
export function checkPermission(requiredType: 'elder' | 'guard'): boolean {
  // 从全局数据或本地存储获取用户类型
  const app = getApp()
  let userType = app.globalData?.userType || ''
  
  if (!userType) {
    userType = wx.getStorageSync('userType') || ''
  }
  
  return userType === requiredType
}

/**
 * 检查并重定向用户到正确的页面
 * @param requiredType 需要的用户类型 ('elder' 或 'guard')
 * @param redirectUrl 无权限时的重定向地址
 */
export function checkAndRedirect(requiredType: 'elder' | 'guard', redirectUrl?: string) {
  if (!checkPermission(requiredType)) {
    const app = getApp()
    const userType = app.globalData?.userType || wx.getStorageSync('userType') || ''
    
    if (userType) {
      // 如果用户已登录但类型不匹配，跳转到对应类型的首页
      const homeUrl = userType === 'elder' 
        ? '/elder/pages/index/index' 
        : '/guard/pages/index/index'
      
      wx.redirectTo({
        url: homeUrl
      })
    } else {
      // 如果用户未登录，跳转到登录页（如果有的话）
      // 这里暂时跳转到老人端首页，实际项目中应该有专门的登录页
      wx.redirectTo({
        url: redirectUrl || '/elder/pages/index/index'
      })
    }
  }
}
