// elders.ts
import { bindingApi,Binding } from '../../../api/binding';
import { saveCurrentElder, getCurrentElder } from '../../storage';

Page({
  data: {
    // 扩展数据结构，必须包含 bindingId，这是后续发起解绑请求的凭证
    elders: [] as Array<{ bindingId: number; id: string; name: string; phone: string; isCurrent: boolean; status: string }>,
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
    bindingApi.getBindings().then((bindings: Binding[]) => {
      const currentElder = getCurrentElder();
      const elders = bindings.map((binding: any, index: number) => {
        const elderId = String(binding.elderly?.user_id || '');
        const isCurrent = currentElder ? elderId === currentElder.id : index === 0;
        return {
          bindingId: binding.binding_id, // 核心：保存这层关系的 ID
          id: elderId,
          name: binding.elderly?.nickname || '未命名老人',
          phone: binding.elderly?.phone || '',
          status: binding.status, // 保存状态（pending/accepted），前端 WXML 可据此展示不同 UI
          isCurrent
        };
      });
      this.setData({ elders });
      if (elders.length > 0 && !currentElder) {
        saveCurrentElder({ id: elders[0].id, name: elders[0].name, phone: elders[0].phone || '' });
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
      saveCurrentElder({ id: currentElder.id, name: currentElder.name, phone: currentElder.phone || '' });
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
    // 注意：这里的 dataset 需要拿到 binding_id 而不是 elder_id
    // 前端 WXML 中按钮需要写成：data-binding-id="{{item.bindingId}}"
    const bindingId = e.currentTarget.dataset.bindingId; 

    if (!bindingId) return;

    wx.showModal({
      title: '确认解绑',
      content: '确定要解除与该老人的监护关系吗？',
      success: (res) => {
        if (res.confirm) {
          // 调用真正的解绑 API
          bindingApi.deleteBinding(bindingId).then(() => {
            wx.showToast({ title: '已解绑', icon: 'success' });
            // 解绑成功后，重新从后端拉取最新列表，保证数据绝对一致
            this.fetchBindings();
          }).catch(err => {
            console.error("解绑失败", err);
          });
        }
      }
    });
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

    bindingApi.createBinding({ elderly_phone: phone }).then((binding: Binding) => {
      wx.showToast({ title: '绑定成功', icon: 'success' });
      // wx.showToast({ title: '申请已发送，等待老人同意', icon: 'none', duration: 2000 });后续优化
      this.hideAddModal();
      this.fetchBindings();
    }).catch((error: any) => {
      console.error('绑定失败:', error);
      wx.showToast({ title: error.message || '绑定失败', icon: 'none' });
    });
  }
})
