// edit-profile.ts
import { checkAndRedirect } from '../../../utils/auth'
import { userApi } from '../../../api/user'

Page({
  data: {
    formData: {
      nickname: '',
      gender: 9, // 0-男，1-女，9-未知
      birthday: '',
      phone: '',
      avatar: ''
    },
    loading: false,
    // 性别映射
    genderMap: {
      0: '男',
      1: '女',
      9: '未知'
    },
    // 记录上次点击时间，用于双击取消
    lastGenderClickTime: 0,
    lastGenderClickValue: -1,
    // 触摸事件相关数据
    touchStartY: 0,
    touchMoveY: 0,
    // 动画相关数据
    animation: {
      headerArcHeight: 440,
      headerArcRadius: 20,
      avatarContainerTop: -50,
      avatarSize: 210,
      formCardTop: 0
    },
    // 日期选择器相关数据
    showDatePicker: false,
    birthdayDisplay: '1945年 1月 1日'
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    // 检查用户类型权限
    checkAndRedirect('elderly');
    this.getUserInfo();
  },

  // 获取用户信息
  async getUserInfo() {
    this.setData({ loading: true })
    try {
      const userInfo = await userApi.getProfile()
      this.setData({
        formData: {
          nickname: userInfo.nickname,
          phone: userInfo.phone,
          avatar: userInfo.avatar_url || '',
          gender: userInfo.gender,
          birthday: userInfo.birthday || '',
        }
      })
      this.updateBirthdayDisplay();
    } catch (error: any) {
      wx.showToast({ title: error.message || '获取用户信息失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 处理输入框变化
  onInputChange(e: any) {
    const { field } = e.currentTarget.dataset;
    this.setData({
      [`formData.${field}`]: e.detail.value
    });
  },

  // 选择性别（按钮方式），支持双击取消选择
  selectGender(e: any) {
    const gender = parseInt(e.currentTarget.dataset.gender);
    const now = Date.now();
    const lastClickTime = this.data.lastGenderClickTime;
    const lastClickValue = this.data.lastGenderClickValue;
    
    // 检测双击：300ms内点击同一按钮
    if (now - lastClickTime < 300 && lastClickValue === gender && this.data.formData.gender === gender) {
      // 双击同一按钮，取消选择（设为未知）
      this.setData({
        'formData.gender': 9,
        lastGenderClickTime: 0,
        lastGenderClickValue: -1
      });
      return;
    }
    
    // 正常点击，设置性别
    this.setData({
      'formData.gender': gender,
      lastGenderClickTime: now,
      lastGenderClickValue: gender
    });
  },

  // 处理日期选择
  onDateChange(e: any) {
    this.setData({
      'formData.birthday': e.detail.value
    });
    this.updateBirthdayDisplay();
  },

  // 显示日期选择器
  showDatePicker() {
    this.setData({
      showDatePicker: true
    });
  },

  // 确认日期选择
  onDateConfirm(e: any) {
    const { value, displayValue } = e.detail;
    this.setData({
      'formData.birthday': value,
      birthdayDisplay: displayValue,
      showDatePicker: false
    });
  },

  // 取消日期选择
  onDateCancel() {
    this.setData({
      showDatePicker: false
    });
  },

  // 更新生日显示格式
  updateBirthdayDisplay() {
    const birthday = this.data.formData.birthday;
    if (birthday) {
      const [year, month, day] = birthday.split('-').map(Number);
      this.setData({
        birthdayDisplay: `${year}年 ${month}月 ${day}日`
      });
    }
  },

  // 保存表单
  async onSave() {
    const { nickname, phone, avatar, gender, birthday } = this.data.formData;
    
    // 简单的验证
    if (!nickname.trim()) {
      wx.showToast({ title: '请输入昵称', icon: 'none' });
      return;
    }
    if (!/^1[3-9]\d{9}$/.test(phone)) {
      wx.showToast({ title: '手机号格式错误', icon: 'none' });
      return;
    }

    this.setData({ loading: true });
    try {
      // 调用更新用户信息接口
      await userApi.updateProfile({
        nickname: nickname,
        avatar_url: avatar,
        phone: phone,
        gender: gender as 0 | 1 | 9,
        birthday: birthday,
      });

      wx.showToast({ title: '保存成功', icon: 'success' });
      setTimeout(() => {
        wx.navigateBack(); // 保存成功后返回
      }, 1500);
    } catch (error: any) {
      wx.showToast({ title: error.message || '保存失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },
  
  // 返回上一页
  goBack() {
    wx.navigateBack();
  },

  // 触摸开始事件
  onTouchStart(e: any) {
    this.setData({
      touchStartY: e.touches[0].clientY
    });
  },

  // 触摸移动事件
  onTouchMove(e: any) {
    const touchStartY = this.data.touchStartY;
    const touchMoveY = e.touches[0].clientY;
    const deltaY = touchMoveY - touchStartY;

    // 只有向下滑动且滑动距离大于0时才执行动画
    if (deltaY > 0) {
      // 计算动画参数，限制最大滑动距离为100rpx
      const maxDelta = 100;
      const normalizedDelta = Math.min(deltaY * 0.5, maxDelta);

      // 更新动画数据
      this.setData({
        animation: {
          headerArcHeight: 440 + normalizedDelta,
          headerArcRadius: 20 + normalizedDelta * 0.2,
          avatarContainerTop: -50 + normalizedDelta,
          avatarSize: 210 + normalizedDelta * 0.3,
          formCardTop: normalizedDelta
        }
      });
    }
  },

  // 触摸结束事件
  onTouchEnd() {
    // 重置动画数据，使用动画效果恢复到初始状态
    this.setData({
      animation: {
        headerArcHeight: 440,
        headerArcRadius: 20,
        avatarContainerTop: -50,
        avatarSize: 210,
        formCardTop: 0
      }
    });
  },

  // 选择头像
  chooseAvatar() {
    wx.showActionSheet({
      itemList: ['拍照', '从相册选择'],
      success: (res) => {
        if (res.tapIndex === 0) {
          // 拍照
          this.takePhoto();
        } else if (res.tapIndex === 1) {
          // 从相册选择
          this.chooseImageFromAlbum();
        }
      },
      fail: (res) => {
        console.log('取消选择', res);
      }
    });
  },

  // 拍照
  takePhoto() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['camera'],
      success: () => {
        this.uploadAvatar();
      },
      fail: (res) => {
        console.log('拍照失败', res);
        if (res.errMsg !== 'chooseImage:fail cancel') {
          wx.showToast({ title: '拍照失败', icon: 'none' });
        }
      }
    });
  },

  // 从相册选择
  chooseImageFromAlbum() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album'],
      success: () => {
        this.uploadAvatar();
      },
      fail: (res) => {
        console.log('选择图片失败', res);
        if (res.errMsg !== 'chooseImage:fail cancel') {
          wx.showToast({ title: '选择图片失败', icon: 'none' });
        }
      }
    });
  },

  // 上传头像
  // TODO: 实际项目中应该调用上传接口，将图片上传到服务器
  uploadAvatar() {
    wx.showLoading({ title: '上传中...' });
    
    // 这里应该调用上传接口，将图片上传到服务器
    // 模拟上传过程
    setTimeout(() => {
      // 模拟上传成功，返回图片URL
      const avatarUrl = 'https://via.placeholder.com/150'; // 实际项目中应该使用服务器返回的URL
      
      this.setData({
        'formData.avatar': avatarUrl
      });
      
      wx.hideLoading();
      wx.showToast({ title: '头像更换成功', icon: 'success' });
    }, 1500);
  }
});