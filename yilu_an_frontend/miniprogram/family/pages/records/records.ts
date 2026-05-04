// records.ts
import { navigationRecordApi } from '../../../api/navigation-record';
import { getCurrentElder } from '../../storage';

interface RecordItem {
  id: number;
  time: string;
  path: string;
  destName: string;
  distance: string;
  duration: string;
  status: number;
  statusText: string;
}

Page({
  data: {
    currentTab: 'all',
    stats: {
      trips: '0'
    },
    records: [] as RecordItem[]
  },

  onLoad() {
    this.loadRecords();
  },

  onShow() {
    this.loadRecords();
  },

  goBack() {
    wx.navigateBack();
  },

  onTabChange(e: any) {
    const tab = e.detail.value;
    this.setData({
      currentTab: tab
    });
    this.loadRecords();
  },

  async loadRecords() {
    const elder = getCurrentElder();
    if (!elder) {
      wx.showToast({ title: '请先选择老人', icon: 'none' });
      return;
    }

    const userId = parseInt(elder.id);
    wx.showLoading({ title: '加载中...' });

    try {
      const res = await navigationRecordApi.getRecords(userId) as any;
      console.log('获取到的记录:', res);

      const filteredRecords = this.filterByTab(res);
      const formattedRecords = this.formatRecords(filteredRecords);
      const stats = this.calculateStats(res);

      this.setData({
        records: formattedRecords,
        stats
      });
    } catch (err) {
      console.error('获取出行记录失败:', err);
      wx.showToast({ title: '获取记录失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  },

  filterByTab(records: any[]): any[] {
    const now = new Date();
    const currentTab = this.data.currentTab;

    if (currentTab === 'all') {
      return records;
    }

    return records.filter((record: any) => {
      const recordDate = new Date(record.start_time);

      switch (currentTab) {
        case 'today':
          return this.isSameDay(recordDate, now);
        case 'week':
          return this.isSameWeek(recordDate, now);
        case 'month':
          return recordDate.getMonth() === now.getMonth() && recordDate.getFullYear() === now.getFullYear();
        default:
          return true;
      }
    });
  },

  isSameDay(date1: Date, date2: Date): boolean {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  },

  isSameWeek(date1: Date, date2: Date): boolean {
    const startOfWeek = new Date(date2);
    startOfWeek.setDate(date2.getDate() - date2.getDay());
    startOfWeek.setHours(0, 0, 0, 0);

    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 7);

    return date1 >= startOfWeek && date1 < endOfWeek;
  },

  formatRecords(records: any[]): RecordItem[] {
    return records.map((record: any) => {
      const startDate = new Date(record.start_time);
      const timeStr = this.formatDate(startDate);
      const path = record.dest_name || '未知';
      const status = record.status;

      let statusText = '';
      if (status === 1) statusText = '进行中';
      else if (status === 2) statusText = '已完成';
      else if (status === 3) statusText = '已取消';

      return {
        id: record.record_id,
        time: timeStr,
        path: path,
        destName: record.dest_name || '',
        distance: '-',
        duration: '-',
        status,
        statusText
      };
    });
  },

  formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    const weekday = weekdays[date.getDay()];

    return `${year}-${month}-${day} ${weekday} ${hours}:${minutes}`;
  },

  calculateStats(records: any[]): { trips: string } {
    const count = records.length;

    return {
      trips: String(count)
    };
  },

  viewDetail(e: any) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/family/pages/record-detail/record-detail?id=${id}`
    });
  }
})