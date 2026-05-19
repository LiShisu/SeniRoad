// 安全的存储 API 包装函数
function safeGetStorageSync(key: string): any {
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

export { safeGetStorageSync, safeSetStorageSync, safeRemoveStorageSync }
