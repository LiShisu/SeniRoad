// 权限检查工具
/**
 * 检查用户是否有权限访问当前页面
 * @param requiredType 需要的用户类型 ('elderly' 或 'family')
 * @returns 是否有权限
 */
export function checkPermission(requiredType: 'elderly' | 'family'): boolean {
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
 * @param requiredType 需要的用户类型 ('elderly' 或 'family')
 */
export function checkAndRedirect(requiredType: 'elderly' | 'family') {
  if (!checkPermission(requiredType)) {
    const app = getApp()
    const userType = app.globalData?.userType || wx.getStorageSync('userType') || ''
    
    if (userType) {
      // 如果用户已登录但类型不匹配，跳转到对应类型的首页
      const homeUrl = userType === 'elderly' 
        ? '/elderly/pages/index/index' 
        : '/family/pages/index/index'
      
      wx.redirectTo({
        url: homeUrl
      })
    } else {
      // 如果用户未登录，跳转到登录页（如果有的话）
      // 这里暂时跳转到老人端首页，实际项目中应该有专门的登录页
      wx.redirectTo({
        url: '/common/login/login'
      })
    }
  }
}

// 获取token
export const getToken = (): string | null => {
  return wx.getStorageSync('access_token');
};

// 保存token
export const saveToken = (token: string): void => {
  wx.setStorageSync('access_token', token);
};

// 保存用户类型
export const saveUserRole = (role: string): void => {
  wx.setStorageSync('userType', role);
};

// 微信登录并获取token
export const wechatLogin = async (): Promise<'elderly' | 'family'> => {
  
  try {
    // 1. 调用微信登录接口获取code
    const wxLoginResult = await new Promise<any>((resolve, reject) => {
      wx.login({
        success: resolve,
        fail: reject,
      });
    });

    // 2. 直接将code发送给后端服务器进行登录操作
    const authApi = require('../api/auth').authApi;
    const response = await authApi.wechatLogin(wxLoginResult.code);

    console.log('登录成功:', response);
    // 3. 保存token和用户信息
    saveToken(response.access_token);
    saveUserRole(response.role);
    
    // 保存用户类型到全局数据
    getApp().globalData.userType = response.role;
    return response.role;
  } catch (error) {
    throw error;
  }
};

/**
 * 检查登录状态
 * @returns Promise<boolean> 是否已登录
 */
export async function checkLoginStatus(): Promise<boolean> {
  const token = wx.getStorageSync('access_token');
  if (!token) {
    // 未登录，跳转到登录页面
    wx.redirectTo({
      url: '/common/login/login'
    });
    return false;
  }
  
  // 检查 session_key 是否过期
  try {
    await new Promise<void>((resolve, reject) => {
      wx.checkSession({
        success: () => {
          // session_key 未过期，登录态有效
          resolve();
        },
        fail: () => {
          // session_key 已过期，需要重新登录
          reject(new Error('Session expired'));
        }
      });
    });
    return true;
  } catch (error) {
    // session_key 已过期，跳转到登录页面
    wx.redirectTo({
      url: '/common/login/login'
    });
    return false;
  }
}
