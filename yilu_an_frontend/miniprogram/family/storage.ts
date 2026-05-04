const CURRENT_ELDER_KEY = 'current_elder_info';

export interface CurrentElderInfo {
  id: string;
  name: string;
  phone: string;
}

export function saveCurrentElder(elder: CurrentElderInfo): void {
  try {
    wx.setStorageSync(CURRENT_ELDER_KEY, JSON.stringify(elder));
  } catch (error) {
    console.error('保存当前监护老人信息失败:', error);
  }
}

export function getCurrentElder(): CurrentElderInfo | null {
  try {
    const data = wx.getStorageSync(CURRENT_ELDER_KEY);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('获取当前监护老人信息失败:', error);
    return null;
  }
}