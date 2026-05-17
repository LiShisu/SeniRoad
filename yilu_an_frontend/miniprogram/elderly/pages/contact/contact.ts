// elderly/pages/contact/contact.ts
import { bindingApi, type Binding } from '../../../api/binding';

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

  async fetchFamilies() {
    try {
      const bindings = await bindingApi.getBindings();
      console.log('获取家属列表成功:', bindings);
      
      const families: FamilyItem[] = bindings
        .filter((binding: Binding) => binding.family !== null) // 只保留有家属信息的
        .map((binding: Binding) => ({
          family_id: binding.family!.user_id, // family 不为 null，所以用 !断言
          family_nickname: binding.family!.nickname || '未知家属',
          family_phone: binding.family!.phone || null
        }));
      
      this.setData({ families });
    } catch (error: any) {
      console.error('获取家属列表失败:', error);
      wx.showToast({ title: error.message || '获取家属列表失败', icon: 'none' });
    }
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
