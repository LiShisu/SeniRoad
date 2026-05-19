import { favoritePlacesApi } from '../../../api/favorite-places';
import type { FavoritePlace } from '../../../api/favorite-places';
import { navigationApi, AddressNavigationResponse, NavigationStep } from '../../../api/navigation';
import { locationApi } from '../../../api/location';
import { getPlace, savePlace, getRoute, saveRoute } from '../../storage';
import { getLocation } from '../../../utils/geo';
import { playSpeech } from '../../../utils/speech-player';

interface CachedRouteData {
  route: AddressNavigationResponse['route'];
  recordId: number;
  originLat: number;
  originLng: number;
  destLat: number;
  destLng: number;
  currentStepIndex: number;
  allPoints: { latitude: number; longitude: number }[];
  traveledPoints: { latitude: number; longitude: number }[];
  lastInstructionStep: number;
}

Page({
  data: {
    placeId: 0,
    placeName: '',
    polyline: [] as any[],
    markers: [] as any[],
    mapCenter: {
      latitude: 39.9042,
      longitude: 116.4074
    },
    currentInstruction: '',
    currentStepDistance: '',
    currentStepRoad: '',
    totalDistance: '',
    totalDuration: '',
    currentStepIndex: 0,
    stepsCount: 0,
    isDeviating: false,
    isRerouting: false,
    isVoiceMode: false,

    volume: 0.8,
  },

  cachedRoute: null as CachedRouteData | null,
  locationWatchTimer: null as ReturnType<typeof setInterval> | null,
  audioContext: null as any,
  lastLocation: null as { latitude: number; longitude: number } | null,
  deviationThreshold: 50,
  rerouteDebounceTimer: null as ReturnType<typeof setTimeout> | null,
  mapCtx: null as WechatMiniprogram.MapContext | null,
  isUnloading: false,

  onLoad(options: any) {
    this.clearAudioCache();
    if (options?.voiceMode === '1') {
      this.setData({ isVoiceMode: true });
      this.loadVoiceRoute(); // 调用语音导航专属加载器
    } else if (options?.place_id) {
      this.setData({ placeId: parseInt(options.place_id) });
      this.loadPlaceAndRoute(); // 原本的收藏夹加载逻辑
    }
  },

  onReady() {
    this.mapCtx = wx.createMapContext('navMap');
    this.initAudioContext();
  },

  onUnload() {
    this.endNavigation();
    this.clearAudioCache();
  },

  initAudioContext() {
    if (this.audioContext) {
      this.audioContext.destroy();
    }
    this.audioContext = wx.createInnerAudioContext();
    this.audioContext.useWebAudioImplementation = true;
    this.audioContext.volume = this.data.volume;
    this.audioContext.onPlay(() => {
      console.log('语音播放开始');
    });
    this.audioContext.onError((err: any) => {
      console.error('音频播放失败:', err);
    });
    this.audioContext.onEnded(() => {
      console.log('语音播放完成');
    });
  },

  destroyAudioContext() {
    if (this.audioContext) {
      this.audioContext.stop();
      this.audioContext.destroy();
      this.audioContext = null;
    }
  },

  // TODO: 完善调整音量的功能
  changeVolume(volume: number) {
    this.audioContext.volume = volume;
    this.setData({ volume });
  },

  async loadPlaceAndRoute() {
    try {
      let place: FavoritePlace | null = null;
      let route: AddressNavigationResponse['route'] | null = null;

      const cachedPlace = getPlace(this.data.placeId);
      if (cachedPlace) {
        place = cachedPlace as FavoritePlace;
        this.setData({ placeName: place.place_name });
      }

      const cachedRoute = getRoute(this.data.placeId);
      if (cachedRoute) {
        route = cachedRoute as AddressNavigationResponse['route'];
      }

      if (!place || !route) {
        wx.showToast({
          title: '路线信息丢失，请重新规划',
          icon: 'none',
          duration: 2000
        });
        setTimeout(() => {
          wx.navigateBack();
        }, 2000);
        return;
      }

      const res = await getLocation();

      const allPoints = this.parsePolylineArray(route.polyline);

      this.cachedRoute = {
        route,
        recordId: route.record_id,
        originLat: res.latitude,
        originLng: res.longitude,
        destLat: place.latitude,
        destLng: place.longitude,
        currentStepIndex: 0,
        allPoints,
        traveledPoints: [{ latitude: res.latitude, longitude: res.longitude }],
        lastInstructionStep: -1
      };

      this.parseRoute(route, allPoints, res.latitude, res.longitude, place.latitude, place.longitude);
      this.startLocationWatch();
      this.speakInstruction(route.steps?.[0]?.instruction || '导航开始');
    } catch (err: any) {
      console.error('加载地点或路线失败:', err);
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    }
  },
  async loadVoiceRoute() {
    try {
      // 1. 从缓存中读取数据
      const voiceNavData = wx.getStorageSync('tempVoiceRoute');
      if (!voiceNavData || !voiceNavData.route || !voiceNavData.destInfo) {
        wx.showToast({ title: '路线数据丢失', icon: 'none' });
        setTimeout(() => wx.navigateBack(), 2000);
        return;
      }
      const { route, destInfo } = voiceNavData;
      this.setData({ placeName: destInfo.destination });
      // 2. 获取当前位置作为起点
      const res = await getLocation();
      const allPoints = this.parsePolylineArray(route.polyline);
      // 3. 构建缓存路由数据结构（对齐原本的 this.cachedRoute）
      this.cachedRoute = {
        route,
        recordId: route.record_id || Date.now(), // 如果语音接口没返回 record_id，给个临时标识
        originLat: res.latitude,
        originLng: res.longitude,
        destLat: destInfo.latitude,
        destLng: destInfo.longitude,
        currentStepIndex: 0,
        allPoints,
        traveledPoints: [{ latitude: res.latitude, longitude: res.longitude }],
        lastInstructionStep: -1
      };
      // 4. 渲染地图并开始导航监听
      this.parseRoute(route, allPoints, res.latitude, res.longitude, destInfo.latitude, destInfo.longitude);
      this.startLocationWatch();
      // 5. 播报起始语音
      this.speakInstruction(route.steps?.[0]?.instruction || `开始导航前往${destInfo.destination}`);
    } catch (err: any) {
      console.error('加载语音路线失败:', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },
  parsePolylineArray(polylineData: string | string[]): { latitude: number; longitude: number }[] {
    const allPoints: { latitude: number; longitude: number }[] = [];
    if (!polylineData) {
      return allPoints;
    }
    let segments: string[] = [];
    if (typeof polylineData === 'string') {
      segments = polylineData.split(';');
    } else if (Array.isArray(polylineData)) {
      for (const segment of polylineData) {
        if (segment && typeof segment === 'string') {
          const points = segment.split(';');
          segments.push(...points);
        }
      }
    }
    for (const point of segments) {
      if (!point || !point.includes(',')) continue;
      const [lngStr, latStr] = point.split(',');
      const lng = parseFloat(lngStr);
      const lat = parseFloat(latStr);
      if (!isNaN(lng) && !isNaN(lat)) {
        allPoints.push({ latitude: lat, longitude: lng });
      }
    }
    return allPoints;
  },
  parseRoute(route: AddressNavigationResponse['route'], allPoints: { latitude: number; longitude: number }[], originLat: number, originLng: number, destLat: number, destLng: number) {
    const markers = [
      {
        id: 0,
        latitude: originLat,
        longitude: originLng,
        iconPath: '/assets/images/location-marker-start.png',
        width: 40,
        height: 40,
        label: { content: '起点', fontSize: 20, color: '#333' }
      },
      {
        id: 1,
        latitude: destLat,
        longitude: destLng,
        iconPath: '/assets/images/location-marker-end.png',
        width: 40,
        height: 40,
        label: { content: this.data.placeName, fontSize: 20, color: '#333' }
      }
    ];

    this.setData({
      polyline: [{
        points: allPoints,
        color: '#4B8AFF',
        width: 6,
        dottedLine: false
      }],
      markers,
      mapCenter: {
        latitude: (originLat + destLat) / 2,
        longitude: (originLng + destLng) / 2
      },
      totalDistance: route.distance,
      totalDuration: route.duration,
      stepsCount: route.steps?.length || 0,
      currentInstruction: route.steps?.[0]?.instruction || '',
      currentStepDistance: route.steps?.[0]?.distance || '',
      currentStepRoad: route.steps?.[0]?.road || '',
      isDeviating: false,
      isRerouting: false
    });

    setTimeout(() => {
      this.mapCtx?.includePoints({
        points: allPoints,
        padding: [50, 50, 50, 50]
      });
    }, 100);
  },

  startLocationWatch() {
    this.locationWatchTimer = setInterval(() => {
      this.updateCurrentPosition();
    }, 3000);
  },

  stopLocationWatch() {
    if (this.locationWatchTimer) {
      clearInterval(this.locationWatchTimer);
      this.locationWatchTimer = null;
    }
  },

  async updateCurrentPosition() {
    if (!this.cachedRoute || this.isUnloading) return;

    try {
      const res = await getLocation();
      const { route, allPoints, traveledPoints, currentStepIndex } = this.cachedRoute;

      if (this.lastLocation) {
        const distance = this.calculateDistance(
          this.lastLocation.latitude, this.lastLocation.longitude,
          res.latitude, res.longitude
        );

        if (distance > 2) {
          traveledPoints.push({ latitude: res.latitude, longitude: res.longitude });
          this.cachedRoute!.traveledPoints = traveledPoints;
          this.updateTraveledPolyline(traveledPoints);

          locationApi.createLocation({
            latitude: res.latitude,
            longitude: res.longitude,
            accuracy: res.accuracy,
            record_id: this.cachedRoute!.recordId
          }).catch((err) => {
            console.error('记录位置失败:', err);
          });
        }
      }
      this.lastLocation = { latitude: res.latitude, longitude: res.longitude };

      const newStepIndex = this.findCurrentStepIndex(res.latitude, res.longitude, route.steps || []);
      this.cachedRoute!.currentStepIndex = newStepIndex;

      if (newStepIndex !== currentStepIndex) {
        const instruction = route.steps?.[newStepIndex]?.instruction || '';
        if (instruction && newStepIndex > this.cachedRoute!.lastInstructionStep) {
          this.speakInstruction(instruction);
          this.cachedRoute!.lastInstructionStep = newStepIndex;
        }
      }

      const nextStep = route.steps?.[newStepIndex + 1];

      this.setData({
        currentStepIndex: newStepIndex,
        currentInstruction: nextStep?.instruction || route.steps?.[newStepIndex]?.instruction || '到达目的地',
        currentStepDistance: nextStep?.distance || '',
        currentStepRoad: nextStep?.road || ''
      });

      this.checkDeviation(res.latitude, res.longitude, allPoints);

      console.log('当前位置:', res.latitude, res.longitude, '当前步骤:', newStepIndex);
    } catch (err: any) {
      console.error('更新位置失败:', err);
    }
  },

  updateTraveledPolyline(traveledPoints: { latitude: number; longitude: number }[]) {
    const plannedPoints = this.cachedRoute?.allPoints || [];
    this.setData({
      polyline: [
        {
          points: plannedPoints,
          color: '#4B8AFF',
          width: 6,
          dottedLine: false
        },
        {
          points: traveledPoints,
          color: '#FF6B6B',
          width: 6,
          dottedLine: false
        }
      ]
    });
  },

  checkDeviation(lat: number, lng: number, plannedPoints: { latitude: number; longitude: number }[]) {
    const minDistanceToRoute = this.getMinDistanceToPolyline(lat, lng, plannedPoints);

    const isDeviating = minDistanceToRoute > this.deviationThreshold;

    if (isDeviating !== this.data.isDeviating) {
      this.setData({ isDeviating });

      if (isDeviating) {
        this.speakInstruction('您已偏离路线，正在重新规划');
        this.debouncedReroute();
      }
    }
  },

  getMinDistanceToPolyline(lat: number, lng: number, points: { latitude: number; longitude: number }[]): number {
    let minDistance = Infinity;

    for (let i = 0; i < points.length - 1; i++) {
      const p1 = points[i];
      const p2 = points[i + 1];
      const distance = this.pointToLineSegmentDistance(lat, lng, p1.latitude, p1.longitude, p2.latitude, p2.longitude);
      minDistance = Math.min(minDistance, distance);
    }

    return minDistance === Infinity ? 0 : minDistance;
  },

  pointToLineSegmentDistance(lat: number, lng: number, lat1: number, lng1: number, lat2: number, lng2: number): number {
    const A = lng - lng1;
    const B = lat - lat1;
    const C = lng2 - lng1;
    const D = lat2 - lat1;

    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    let param = -1;

    if (lenSq !== 0) {
      param = dot / lenSq;
    }

    let xx, yy;

    if (param < 0) {
      xx = lng1;
      yy = lat1;
    } else if (param > 1) {
      xx = lng2;
      yy = lat2;
    } else {
      xx = lng1 + param * C;
      yy = lat1 + param * D;
    }

    return this.calculateDistance(lat, lng, yy, xx);
  },

  debouncedReroute() {
    if (this.rerouteDebounceTimer) {
      clearTimeout(this.rerouteDebounceTimer);
    }

    this.rerouteDebounceTimer = setTimeout(() => {
      this.reroute();
    }, 5000);
  },

  // async reroute() {
  //   if (!this.cachedRoute || this.data.isRerouting || this.isUnloading) return;

  //   this.setData({ isRerouting: true });
  //   try {
  //     const res = await getLocation();

  //     let place: FavoritePlace | null = getPlace(this.data.placeId) as FavoritePlace;
  //     if (!place) {
  //       place = await favoritePlacesApi.getFavoritePlaceById(this.data.placeId);
  //       savePlace(place);
  //     }

  //     const routeRes = await navigationApi.navigateByAddress({
  //       favorite_place_id: this.data.placeId,
  //       origin_lng: res.longitude.toString(),
  //       origin_lat: res.latitude.toString()
  //     });

  //     const { route } = routeRes;
  //     const allPoints = this.parsePolylineArray(route.polyline);

  //     saveRoute(this.data.placeId, route);

  //     this.cachedRoute = {
  //       ...this.cachedRoute,
  //       route,
  //       recordId: route.record_id || this.cachedRoute!.recordId,
  //       originLat: res.latitude,
  //       originLng: res.longitude,
  //       currentStepIndex: 0,
  //       allPoints,
  //       lastInstructionStep: -1
  //     };

  //     this.setData({
  //       polyline: [{
  //         points: allPoints,
  //         color: '#4B8AFF',
  //         width: 6,
  //         dottedLine: false
  //       }],
  //       totalDistance: route.distance,
  //       totalDuration: route.duration,
  //       stepsCount: route.steps?.length || 0,
  //       currentStepIndex: 0,
  //       isDeviating: false,
  //       isRerouting: false
  //     });

  //     this.speakInstruction('路线已重新规划，继续直行');

  //     setTimeout(() => {
  //       this.mapCtx?.includePoints({
  //         points: allPoints,
  //         padding: [50, 50, 50, 50]
  //       });
  //     }, 100);

  //     console.log('路线重新规划成功');
  //   } catch (err: any) {
  //     console.error('重新规划路线失败:', err);
  //     this.setData({ isRerouting: false });
  //     wx.showToast({
  //       title: '重新规划失败',
  //       icon: 'none'
  //     });
  //   }
  // },
  async reroute() {
    if (!this.cachedRoute || this.data.isRerouting || this.isUnloading) return;
    this.setData({ isRerouting: true });
    try {
      const res = await getLocation();
      let routeRes;

      if (this.data.isVoiceMode) {
        // 语音模式偏航重算：直接调用通过经纬度重新规划路线的接口
        routeRes = await navigationApi.navigateByCoordinates({
          origin_lng: res.longitude.toString(),
          origin_lat: res.latitude.toString(),
          dest_lng: this.cachedRoute.destLng.toString(),
          dest_lat: this.cachedRoute.destLat.toString()
        });
      } else {
        // 收藏夹模式偏航重算：保持原样
        let place: FavoritePlace | null = getPlace(this.data.placeId) as FavoritePlace;
        if (!place) {
          place = await favoritePlacesApi.getFavoritePlaceById(this.data.placeId);
          savePlace(place);
        }
        routeRes = await navigationApi.navigateByAddress({
          favorite_place_id: this.data.placeId,
          origin_lng: res.longitude.toString(),
          origin_lat: res.latitude.toString()
        });
      }
      const { route } = routeRes;
      const allPoints = this.parsePolylineArray(route.polyline);
      if (!this.data.isVoiceMode) {
        saveRoute(this.data.placeId, route);
      }
      this.cachedRoute = {
        ...this.cachedRoute,
        route,
        recordId: route.record_id || this.cachedRoute!.recordId,
        originLat: res.latitude,
        originLng: res.longitude,
        currentStepIndex: 0,
        allPoints,
        lastInstructionStep: -1
      };
      this.setData({
        polyline: [{
          points: allPoints,
          color: '#4B8AFF',
          width: 6,
          dottedLine: false
        }],
        totalDistance: route.distance,
        totalDuration: route.duration,
        stepsCount: route.steps?.length || 0,
        currentStepIndex: 0,
        isDeviating: false,
        isRerouting: false
      });

      this.speakInstruction('路线已重新规划，继续直行');

      setTimeout(() => {
        this.mapCtx?.includePoints({
          points: allPoints,
          padding: [50, 50, 50, 50]
        });
      }, 100);

      console.log('路线重新规划成功');
    } catch (err: any) {
      console.error('重新规划路线失败:', err);
      this.setData({ isRerouting: false });
    }
  },
  speakInstruction(text: string) {
    playSpeech(text, this.audioContext, () => {
      this.initAudioContext();
      return this.audioContext!;
    });
  },

  fallbackSpeak(text: string) {
    this.speakInstruction(text);
  },

  findCurrentStepIndex(lat: number, lng: number, steps: NavigationStep[]): number {
    if (!steps || steps.length === 0) return 0;

    for (let i = steps.length - 1; i >= 0; i--) {
      const stepPolyline = steps[i].polyline;
      if (stepPolyline && this.isPointNearPolyline(lat, lng, stepPolyline, 50)) {
        return i;
      }
    }

    let closestStep = 0;
    let closestDistance = Infinity;

    for (let i = 0; i < steps.length; i++) {
      const stepPolyline = steps[i].polyline;
      if (!stepPolyline) continue;

      const distance = this.getMinDistanceToPolyline(lat, lng, this.parsePolylineArray(stepPolyline));
      if (distance < closestDistance) {
        closestDistance = distance;
        closestStep = i;
      }
    }

    return closestStep;
  },

  isPointNearPolyline(lat: number, lng: number, polylineStr: string, threshold: number): boolean {
    if (!polylineStr || typeof polylineStr !== 'string') return false;

    const points = polylineStr.split(';');
    for (const point of points) {
      if (!point || !point.includes(',')) continue;
      const [lngStr, latStr] = point.split(',');
      const pLat = parseFloat(latStr);
      const pLng = parseFloat(lngStr);

      if (isNaN(pLat) || isNaN(pLng)) continue;

      const distance = this.calculateDistance(lat, lng, pLat, pLng);
      if (distance <= threshold) {
        return true;
      }
    }
    return false;
  },

  calculateDistance(lat1: number, lng1: number, lat2: number, lng2: number): number {
    const R = 6371000;
    const dLat = this.toRad(lat2 - lat1);
    const dLng = this.toRad(lng2 - lng1);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) *
      Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  },

  toRad(deg: number): number {
    return deg * (Math.PI / 180);
  },

  endNavigation() {
    this.isUnloading = true;
    this.stopLocationWatch();
    this.destroyAudioContext();
  },

  goBack() {
    wx.showModal({
      title: '退出导航',
      content: '退出该页面后将结束导航，确认退出？',
      confirmText: '确认',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          this.endNavigation();
          wx.navigateBack();
        }
      }
    });
  },
  clearAudioCache() {
    try {
      const fs = wx.getFileSystemManager();
      const dirPath = wx.env.USER_DATA_PATH;
      // 读取目录下所有文件
      const files = fs.readdirSync(dirPath);
      
      files.forEach((file) => {
        // 只要是之前生成的语音文件，统统删掉释放空间
        if (file.endsWith('.mp3') || file.includes('nav_speech_') || file.includes('temp_nav_voice')) {
          fs.unlinkSync(`${dirPath}/${file}`);
        }
      });
      console.log('历史语音缓存清理完成，空间已释放');
    } catch (err) {
      console.error('清理语音缓存失败:', err);
    }
  },
});
