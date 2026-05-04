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
      const userInfo = await userApi.getProfile();

      const res = await favoritePlacesApi.getFavoritePlaces({
        user_id: userInfo.id,
        active_only: true
      });

      this.setData({
        places: res || []
      });
      console.log('常用地点列表:', res || []);
    } catch (err) {
      console.error('获取常用地点失败:', err);
      wx.showToast({
        title: '获取地点失败',
        icon: 'none'
      });
    }
  },

  goBack() {
    wx.navigateBack();
  },

  navigateToPlace(e: any) {
    const place = e.currentTarget.dataset.place;
    const url = `/elderly/pages/navigate/navigate?place_id=${place.place_id}`;
    wx.navigateTo({ url });
  }
});