import { safeGetStorageSync, safeSetStorageSync, safeRemoveStorageSync } from './storage';

export const ACCESS_TOKEN_KEY = 'access_token'
export const USER_TYPE_KEY = 'userType'

// 获取token
export const getToken = (): string | null => {
  return safeGetStorageSync(ACCESS_TOKEN_KEY) || null;
};

// 获取用户类型
export const getUserRole = (): string | null => {
  return safeGetStorageSync(USER_TYPE_KEY) || null;
};

// 保存token
export const saveToken = (token: string): void => {
  safeSetStorageSync(ACCESS_TOKEN_KEY, token);
};

// 保存用户类型
export const saveUserRole = (role: string): void => {
  safeSetStorageSync(USER_TYPE_KEY, role);
};

// 删除token
export const removeToken = (): void => {
  safeRemoveStorageSync(ACCESS_TOKEN_KEY);
};

// 删除用户类型
export const removeUserRole = (): void => {
  safeRemoveStorageSync(USER_TYPE_KEY);
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

    console.log('微信登录结果:', wxLoginResult);
    console.log('选择的身份:', role);
    
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
// TODO: 以下函数待与app.ts去重
/**
 * 检查登录状态
 * @returns Promise<boolean> 是否已登录
 */
export async function checkLoginStatus(): Promise<boolean> {
  const token = getToken();
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
/**
 * 检查用户是否有权限访问当前页面
 * @param requiredType 需要的用户类型 ('elderly' 或 'family')
 * @returns 是否有权限
 */
export function checkPermission(requiredType: 'elderly' | 'family'): boolean {
  const app = getApp()
  let userType = app.globalData?.userType || ''

  if (!userType) {
    userType = safeGetStorageSync(USER_TYPE_KEY) || ''
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
    const userType = app.globalData?.userType || safeGetStorageSync(USER_TYPE_KEY) || ''

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