// 权限检查工具
let isStorageReady = false;

// 安全的存储 API 包装函数
function safeGetStorageSync(key: string): any {
  if (!isStorageReady) {
    return '';
  }
  try {
    return wx.getStorageSync(key);
  } catch (error) {
    console.warn(`安全获取存储失败: ${key}`, error);
    return '';
  }
}

function safeSetStorageSync(key: string, value: any): void {
  try {
    wx.setStorageSync(key, value);
  } catch (error) {
    console.warn(`安全设置存储失败: ${key}`, error);
  }
}

function safeRemoveStorageSync(key: string): void {
  try {
    wx.removeStorageSync(key);
  } catch (error) {
    console.warn(`安全删除存储失败: ${key}`, error);
  }
}

// 初始化存储系统准备状态
export function initStorage() {
  setTimeout(() => {
    isStorageReady = true;
  }, 200);
}

/**
 * 检查用户是否有权限访问当前页面
 * @param requiredType 需要的用户类型 ('elderly' 或 'family')
 * @returns 是否有权限
 */
export function checkPermission(requiredType: 'elderly' | 'family'): boolean {
  const app = getApp()
  let userType = app.globalData?.userType || ''

  if (!userType) {
    userType = safeGetStorageSync('userType') || ''
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
    const userType = app.globalData?.userType || safeGetStorageSync('userType') || ''

    if (userType) {
      const homeUrl = userType === 'elderly'
        ? '/elderly/pages/index/index'
        : '/family/pages/index/index'

      wx.redirectTo({
        url: homeUrl
      })
    } else {
      wx.redirectTo({
        url: '/common/login/login'
      })
    }
  }
}

// 获取token
export const getToken = (): string | null => {
  return safeGetStorageSync('access_token') || null;
};

// 保存token
export const saveToken = (token: string): void => {
  safeSetStorageSync('access_token', token);
};

// 保存用户类型
export const saveUserRole = (role: string): void => {
  safeSetStorageSync('userType', role);
};

// 删除token
export const removeToken = (): void => {
  safeRemoveStorageSync('access_token');
};

// 删除用户类型
export const removeUserRole = (): void => {
  safeRemoveStorageSync('userType');
};

// 微信登录并获取token
export const wechatLogin = async (role?: 'elderly' | 'family'): Promise<'elderly' | 'family'> => {

  try {
    const wxLoginResult = await new Promise<any>((resolve, reject) => {
      wx.login({
        success: resolve,
        fail: reject,
      });
    });

    const authApi = require('../api/auth').authApi;
    const response = await authApi.wechatLogin(wxLoginResult.code, role);

    console.log('登录成功:', response);
    saveToken(response.access_token);
    saveUserRole(response.role);

    const app = getApp();
    if (app && app.globalData) {
      app.globalData.userType = response.role;
    }
    return response.role;
  } catch (error) {
    console.error('登录失败:', error);
    throw error;
  }
};

// 手机号登录并获取token
export const phoneLogin = async (phone: string): Promise<'elderly' | 'family'> => {

  try {
    const authApi = require('../api/auth').authApi;
    const response = await authApi.phoneLogin(phone);

    console.log('手机号登录成功:', response);
    saveToken(response.access_token);
    saveUserRole(response.role);

    const app = getApp();
    if (app && app.globalData) {
      app.globalData.userType = response.role;
    }
    return response.role;
  } catch (error) {
    console.error('手机号登录失败:', error);
    throw error;
  }
};

/**
 * 检查登录状态
 * @returns Promise<boolean> 是否已登录
 */
export async function checkLoginStatus(): Promise<boolean> {
  const token = safeGetStorageSync('access_token');
  if (!token) {
    wx.redirectTo({
      url: '/common/login/login'
    });
    return false;
  }

  try {
    await new Promise<void>((resolve, reject) => {
      wx.checkSession({
        success: () => {
          resolve();
        },
        fail: () => {
          reject(new Error('Session expired'));
        }
      });
    });
    return true;
  } catch (error) {
    wx.redirectTo({
      url: '/common/login/login'
    });
    return false;
  }
}
