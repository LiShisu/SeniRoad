// record-detail.ts
import { navigationRecordApi } from '../../../api/navigation-record';

interface MapPoint {
  latitude: number;
  longitude: number;
  color: string;
  width: number;
}

interface MapMarker {
  id: number;
  latitude: number;
  longitude: number;
  iconPath: string;
  width: number;
  height: number;
  label?: { content: string; fontSize: number; color: string };
}

Page({
  data: {
    recordId: 0,
    polyline: [] as Array<{ points: MapPoint[]; color: string; width: number }>,
    markers: [] as MapMarker[],
    latitude: 36.65184,
    longitude: 117.12009,
    destName: ''
  },

  onLoad(options: any) {
    const id = options?.id;
    if (id) {
      this.setData({ recordId: parseInt(id) });
      this.loadRecordDetail(parseInt(id));
    }
  },

  async loadRecordDetail(recordId: number) {
    wx.showLoading({ title: '加载中...' });
    
    try {
      const res = await navigationRecordApi.getRecordById(recordId) as any;
      const record = res?.data || res;
      
      if (record) {
        const originLat = parseFloat(record.origin_lat || '36.65184');
        const originLng = parseFloat(record.origin_lng || '117.12009');
        const destLat = parseFloat(record.dest_lat || '36.63894');
        const destLng = parseFloat(record.dest_lng || '117.03031');
        
        const markers: MapMarker[] = [
          {
            id: 1,
            latitude: originLat,
            longitude: originLng,
            iconPath: '/assets/images/location-marker-start.png',
            width: 40,
            height: 40,
            label: { content: '起点', fontSize: 12, color: '#4B8AFF' }
          },
          {
            id: 2,
            latitude: destLat,
            longitude: destLng,
            iconPath: '/assets/images/location-marker-end.png',
            width: 40,
            height: 40,
            label: { content: '终点', fontSize: 12, color: '#FF6B6B' }
          }
        ];

        let polyline: MapPoint[] = [];
        if (record.polyline && typeof record.polyline === 'string') {
          const pointStrings = record.polyline.split(';');
          polyline = pointStrings
            .filter((pointStr: string) => pointStr.trim())
            .map((pointStr: string) => {
              const [lng, lat] = pointStr.split(',').map((val: string) => parseFloat(val.trim()));
              return {
                latitude: isNaN(lat) ? originLat : lat,
                longitude: isNaN(lng) ? originLng : lng,
                color: '#4B8AFF',
                width: 4
              };
            });
        }

        if (polyline.length === 0) {
          polyline = [
            { latitude: originLat, longitude: originLng, color: '#4B8AFF', width: 4 },
            { latitude: destLat, longitude: destLng, color: '#FF6B6B', width: 4 }
          ];
        }

        this.setData({
          polyline: [{ points: polyline, color: '#4B8AFF', width: 4 }],
          markers,
          latitude: originLat,
          longitude: originLng,
          destName: record.dest_name || '未知目的地'
        });
      }
    } catch (err) {
      console.error('获取记录详情失败:', err);
      wx.showToast({ title: '获取详情失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  },

  goBack() {
    wx.navigateBack();
  }
})