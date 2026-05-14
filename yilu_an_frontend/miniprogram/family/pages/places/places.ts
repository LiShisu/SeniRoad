import { favoritePlacesApi } from '../../../api/favorite-places';
import type { FavoritePlace } from '../../../api/favorite-places';
import { getCurrentElder } from '../../storage';

Page({
  data: {
    isManage: false,
    places: [] as FavoritePlace[]
  },

  /**
   * 页面加载
   */
  onLoad() {
    this.loadFavoritePlaces();
  },

  /**
   * 页面显示
   */
  onShow() {
    this.loadFavoritePlaces();
  },

  /**
   * 加载常用地点列表
   */
  async loadFavoritePlaces() {
    const elder = getCurrentElder();
    if (!elder) {
      wx.showToast({
        title: '请选择监护老人',
        icon: 'none'
      });
      return;
    }
    
    try {
      // 家属端必须传入 user_id，后端根据此 ID 过滤数据
      const res = await favoritePlacesApi.getFavoritePlaces({ 
        user_id: parseInt(elder.id),
        active_only: true 
      });
      
      this.setData({
        places: res || []
      });
    } catch (err) {
      console.error('获取常用地点失败:', err);
      // 错误提示由 request.ts 拦截器统一接管，这里静默处理即可
    }
  },

  /**
   * 返回上一页
   */
  goBack() {
    wx.navigateBack();
  },

  /**
   * 切换管理模式
   */
  toggleManage() {
    this.setData({
      isManage: !this.data.isManage
    });
  },

  /**
   * 添加地点
   */
  addPlace() {
    wx.navigateTo({
      url: '/family/pages/add-place/add-place'
    });
  },

  /**
   * 查看地点详情
   */
  goToDetail(e: any) {
    if (this.data.isManage) return;
    const place = e.currentTarget.dataset.place;
    wx.showToast({
      title: `查看${place.place_name}`,
      icon: 'none'
    });
  },

  /**
   * 编辑地点
   */
  editPlace(e: any) {
    const place = e.currentTarget.dataset.place;
    wx.navigateTo({
      url: `/family/pages/add-place/add-place?place_id=${place.place_id}`
    });
  },

  /**
   * 删除地点
   */
  deletePlace(e: any) {
    const place = e.currentTarget.dataset.place;
    wx.showModal({
      title: '确认删除',
      content: `确定要删除"${place.place_name}"吗？`,
      success: async (res) => {
        if (res.confirm) {
          await favoritePlacesApi.deleteFavoritePlace(place.place_id)
            .then(() => {
              // wx.showToast({
              //   title: '已删除',
              //   icon: 'success'
              // });
              this.loadFavoritePlaces();
            })
            .catch((err) => {
              console.error('删除地点失败:', err);
              wx.showToast({
                title: '删除失败',
                icon: 'none'
              });
            });
        }
      }
    });
  }
});