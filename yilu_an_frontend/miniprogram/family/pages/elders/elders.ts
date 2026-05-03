// elders.ts
import { bindingApi } from '../../../api/binding';
import { saveCurrentElder, getCurrentElder } from '../../storage';

const AVATAR_COLORS = ['#4B8AFF', '#FF8C42', '#52C41A', '#FF4D4F', '#722ED1', '#1890FF'];

function getLuminance(hex: string): number {
  const rgb = parseInt(hex.slice(1), 16);
  const r = (rgb >> 16) & 0xFF;
  const g = (rgb >> 8) & 0xFF;
  const b = rgb & 0xFF;
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255;
}

function getAvatarConfig(index: number) {
  const bgColor = AVATAR_COLORS[index % AVATAR_COLORS.length];
  const textColor = getLuminance(bgColor) < 0.6 ? '#FFFFFF' : '#000000';
  return { bgColor, textColor };
}

Page({
  data: {
    elders: [] as Array<{ id: string; name: string; isCurrent: boolean; avatarConfig: { bgColor: string; textColor: string } }>,
    showAddModal: false,
    inputPhone: ''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    this.fetchBindings();
  },

  /**
   * 获取绑定列表
   */
  fetchBindings() {
    bindingApi.getBindings().then((bindings: any) => {
      const currentElder = getCurrentElder();
      const elders = bindings.map((binding: any, index: number) => {
        const elderId = String(binding.elderly_id);
        const isCurrent = currentElder ? elderId === currentElder.id : index === 0;
        return {
          id: elderId,
          name: binding.elderly_nickname,
          isCurrent,
          avatarConfig: getAvatarConfig(index)
        };
      });
      this.setData({ elders });
      if (elders.length > 0 && !currentElder) {
        saveCurrentElder({ id: elders[0].id, name: elders[0].name });
      }
    }).catch((error: any) => {
      console.error('获取绑定列表失败:', error);
      wx.showToast({ title: error.message || '获取绑定列表失败', icon: 'none' });
    });
  },

  /**
   * 返回上一页
   */
  goBack() {
    wx.navigateBack()
  },

  /**
   * 切换当前监护
   */
  switchCurrent(e: any) {
    const { id } = e.currentTarget.dataset
    const elders = this.data.elders.map(elder => ({
      ...elder,
      isCurrent: elder.id === id
    }))
    this.setData({ elders })
    const currentElder = elders.find(elder => elder.isCurrent);
    if (currentElder) {
      saveCurrentElder({ id: currentElder.id, name: currentElder.name });
    }
    wx.showToast({
      title: '已切换监护对象',
      icon: 'success'
    })
  },

  /**
   * 解绑老人
   */
  deleteElder(e: any) {
    const { id } = e.currentTarget.dataset
    wx.showModal({
      title: '确认解绑',
      content: '确定要解除与该老人的监护关系吗？',
      success: (res) => {
        if (res.confirm) {
          const elders = this.data.elders.filter(elder => elder.id !== id)
          this.setData({ elders })
          wx.showToast({
            title: '已解绑',
            icon: 'success'
          })
        }
      }
    })
  },

  /**
   * 显示添加弹窗
   */
  showAddModal() {
    this.setData({ showAddModal: true, inputPhone: '' });
  },

  /**
   * 隐藏添加弹窗
   */
  hideAddModal() {
    this.setData({ showAddModal: false, inputPhone: '' });
  },

  /**
   * 阻止事件冒泡
   */
  stopPropagation() {},

  /**
   * 手机号输入
   */
  onPhoneInput(e: any) {
    this.setData({ inputPhone: e.detail.value });
  },

  /**
   * 确认添加绑定
   */
  confirmAdd() {
    const phone = this.data.inputPhone.trim();
    const phoneRegex = /^1[3-9]\d{9}$/;

    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' });
      return;
    }

    if (!phoneRegex.test(phone)) {
      wx.showToast({ title: '手机号格式不正确', icon: 'none' });
      return;
    }

    bindingApi.createBinding({ elderly_phone: phone }).then((binding: any) => {
      wx.showToast({ title: '绑定成功', icon: 'success' });
      this.hideAddModal();
      this.fetchBindings();
    }).catch((error: any) => {
      console.error('绑定失败:', error);
      wx.showToast({ title: error.message || '绑定失败', icon: 'none' });
    });
  }
})
