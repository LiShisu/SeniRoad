import { favoritePlacesApi } from '../../../api/favorite-places';
import type { FavoritePlace } from '../../../api/favorite-places';
import { userApi } from '../../../api/user';

Page({
  data: {
    places: [] as FavoritePlace[],
  },

  onLoad() {
    this.loadFavoritePlaces();
  },

  onShow() {
    this.loadFavoritePlaces();
  },

  async loadFavoritePlaces() {
    try {
      // 优化：不再需要请求个人信息，直接通过后端的 Token 智能识别老人身份
      const res = await favoritePlacesApi.getFavoritePlaces({
        active_only: true // 仅查询这个条件即可
      });

      this.setData({
        places: res || []
      });
      console.log('常用地点列表:', res || []);
    } catch (err) {
      console.error('获取常用地点失败:', err);
      // wx.showToast({
      //   title: '获取地点失败',
      //   icon: 'none'
      // });
    }
  },

  goBack() {
    wx.navigateBack();
  },

  navigateToPlace(e: any) {
    const place = e.currentTarget.dataset.place;
    const url = `/elderly/pages/plan/plan?place_id=${place.place_id}`;
    wx.navigateTo({ url });
  }
});