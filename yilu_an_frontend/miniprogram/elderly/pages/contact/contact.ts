// elderly/pages/contact/contact.ts
import { bindingApi } from '../../../api/binding';

interface FamilyItem {
  family_id: number;
  family_nickname: string;
  family_phone: string | null;
}

Page({
  data: {
    families: [] as FamilyItem[]
  },

  onLoad() {
    this.fetchFamilies();
  },

  fetchFamilies() {
    bindingApi.getBindings().then((bindings: any) => {
      const families = bindings.map((binding: any) => ({
        family_id: binding.family_id,
        family_nickname: binding.family_nickname,
        family_phone: binding.family_phone
      }));
      this.setData({ families });
    }).catch((error: any) => {
      console.error('获取家属列表失败:', error);
      wx.showToast({ title: error.message || '获取家属列表失败', icon: 'none' });
    });
  },

  goBack() {
    wx.navigateBack();
  },

  callFamily(e: any) {
    const { phone } = e.currentTarget.dataset;
    if (phone) {
      wx.makePhoneCall({ phoneNumber: phone });
    }
  }
})