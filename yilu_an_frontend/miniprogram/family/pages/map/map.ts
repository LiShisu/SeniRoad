// map.ts
import { locationApi } from '../../../api/location';
import { getCurrentElder } from '../../storage';
import { gaodeReverseGeocode } from '../../../utils/geo';

Page({
  data: {
    elderlyUserId: 0,
    phoneNumber: '',
    longitude: 116.397128,
    latitude: 39.907387,
    locationTitle: '加载中...',
    locationDetail: '',
    updateTime: '',
    markers: [
      {
        id: 1,
        longitude: 116.397128,
        latitude: 39.907387,
        width: 50,
        height: 50
      }
    ]
  },

  /**
   * 打电话
   */
  makeCall() {
    const phoneNumber = this.data.phoneNumber;
    if (!phoneNumber) {
      wx.showToast({ title: '暂无电话号码', icon: 'none' });
      return;
    }
    wx.makePhoneCall({
      phoneNumber: phoneNumber,
      success: () => {
        console.log('拨打电话成功')
      },
      fail: () => {
        console.log('拨打电话失败')
      }
    })
  },

  /**
   * 发消息
   */
  sendMessage() {
    wx.showToast({
      title: '发消息功能',
      icon: 'none'
    })
  },

  /**
   * 页面加载
   */
  onLoad(options: any) {
    const elderInfo = getCurrentElder();
    if (elderInfo) {
      this.setData({
        elderlyUserId: parseInt(elderInfo.id),
        phoneNumber: elderInfo.phone || ''
      });
      this.loadElderlyLocation(parseInt(elderInfo.id));
    }
  },

  /**
   * 加载老人实时位置
   */
  async loadElderlyLocation(userId: number) {
    try {
      wx.showLoading({ title: '加载位置中...' });
      
      const res = await locationApi.getLatest({ user_id: userId }) as any;
      console.log('获取老人位置:', res);
      const location = res?.data || res;
      if (location && location.latitude != null && location.longitude != null) {
        const updateDate = new Date(location.created_at);
        const timeStr = this.formatTime(updateDate);
        const lat = parseFloat(String(location.latitude));
        const lng = parseFloat(String(location.longitude));
        
        this.setData({
          latitude: lat,
          longitude: lng,
          locationDetail: `经度: ${lng.toFixed(6)} | 纬度: ${lat.toFixed(6)}`,
          updateTime: `更新于 ${timeStr}`,
          markers: [{
            id: 1,
            longitude: lng,
            latitude: lat,
            width: 50,
            height: 50
          }]
        });
        console.log('地图数据已更新:', lat, lng);
        
        gaodeReverseGeocode(lat, lng)
          .then((res) => {
            this.setData({ locationTitle: res.address });
          })
          .catch((err) => {
            console.error('逆地理编码失败:', err);
          });
      } else {
        wx.showToast({ title: '暂无位置信息', icon: 'none' });
      }
    } catch (err) {
      console.error('获取老人位置失败:', err);
      wx.showToast({
        title: '获取位置失败',
        icon: 'none'
      });
    } finally {
      wx.hideLoading();
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
  }
})
