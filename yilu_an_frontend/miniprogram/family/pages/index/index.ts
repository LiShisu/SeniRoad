// index.ts
import { getCurrentElder } from '../../storage';
import { locationApi } from '../../../api/location';
import { navigationRecordApi } from '../../../api/navigation-record';
import { gaodeReverseGeocode } from '../../../utils/geo';

Page({
  data: {
    elderName: '请选择监护老人',
    currentLocation: '未获取到位置',
    lastUpdate: '未知',
    navigationStatus: '未出行',
    currentElderId: '',
    destName: ''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    console.log('family index load')
    // checkAndRedirect('family')
    this.loadCurrentElderInfo();
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    this.loadCurrentElderInfo();
  },

  /**
   * 加载当前监护老人信息
   */
  async loadCurrentElderInfo() {
    const currentElder = getCurrentElder();
    if (currentElder) {
      const userId = parseInt(currentElder.id);
      this.setData({
        elderName: currentElder.name,
        currentElderId: currentElder.id
      });
      await Promise.all([
        this.loadElderlyLocation(userId),
        this.loadNavigationStatus(userId)
      ]);
    }
  },

  /**
   * 加载老人实时位置
   */
  async loadElderlyLocation(userId: number) {
    try {
      const res = await locationApi.getLatest({ user_id: userId }) as any;
      const location = res?.data || res;
      if (location && location.latitude != null && location.longitude != null) {
        const updateDate = new Date(location.created_at);
        const timeStr = this.formatTime(updateDate);
        const lat = parseFloat(String(location.latitude));
        const lng = parseFloat(String(location.longitude));
        
        let address = '未知地址';
        try {
          const geocodeResult = await gaodeReverseGeocode(lat, lng);
          address = geocodeResult.address;
          console.log('逆地理编码结果:', geocodeResult);
        } catch (err) {
          console.error('逆地理编码失败:', err);
          address = `经度: ${lng.toFixed(6)} | 纬度: ${lat.toFixed(6)}`;
        }
        
        this.setData({
          currentLocation: address,
          lastUpdate: timeStr
        });
      }
    } catch (err) {
      console.error('获取老人位置失败:', err);
    }
  },

  /**
   * 加载出行状态
   */
  async loadNavigationStatus(userId: number) {
    try {
      const res = await navigationRecordApi.getActiveRecords(userId) as any;
      const records = res?.data || res;
      if (records && records.length > 0) {
        const activeRecord = records[0];
        this.setData({
          navigationStatus: '出行中',
          destName: activeRecord.dest_name || ''
        });
      } else {
        this.setData({
          navigationStatus: '未出行',
          destName: ''
        });
      }
    } catch (err) {
      console.error('获取出行状态失败:', err);
      this.setData({
        navigationStatus: '未出行',
        destName: ''
      });
    }
  },

  /**
   * 格式化时间
   */
  formatTime(date: Date): string {
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diff < 60) {
      return '刚刚';
    } else if (diff < 3600) {
      return `${Math.floor(diff / 60)}分钟前`;
    } else if (diff < 86400) {
      return `${Math.floor(diff / 3600)}小时前`;
    } else {
      return `${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
    }
  },

  /**
   * 切换老人
   */
  switchElder() {
    wx.showToast({
      title: '切换老人',
      icon: 'none'
    })
  },

  /**
   * 跳转预设常用地点
   */
  goToPlaces() {
    wx.navigateTo({
      url: '/family/pages/places/places'
    })
  },

  /**
   * 跳转出行记录
   */
  goToRecords() {
    wx.navigateTo({
      url: '/family/pages/records/records'
    })
  },

  /**
   * 跳转老人管理
   */
  goToElders() {
    wx.navigateTo({
      url: '/family/pages/elders/elders'
    })
  }
})
