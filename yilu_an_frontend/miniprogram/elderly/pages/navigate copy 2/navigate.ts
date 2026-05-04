import { favoritePlacesApi } from '../../../api/favorite-places';
import type { FavoritePlace } from '../../../api/favorite-places';
import { navigationApi, AddressNavigationResponse, NavigationStep } from '../../../api/navigation';
import { speechApi } from '../../../api/speech';
import { locationApi } from '../../../api/location';
import { getPlace, savePlace, getRoute, saveRoute } from '../../storage';

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
    isRerouting: false
  },

  cachedRoute: null as CachedRouteData | null,
  locationWatchId: 0,
  audioContext: null as any,
  lastLocation: null as { latitude: number; longitude: number } | null,
  deviationThreshold: 50,
  rerouteDebounceTimer: 0,
  mapCtx: null as WechatMiniprogram.MapContext | null,
  isUnloading: false,

  onLoad(options: any) {
    const placeId = options?.place_id;
    if (placeId) {
      this.setData({ placeId: parseInt(placeId) });
      this.initAudioContext();
      this.loadPlaceAndRoute();
    }
  },

  onReady() {
    this.mapCtx = wx.createMapContext('navMap');
  },

  onUnload() {
    this.endNavigation();
  },

  initAudioContext() {
    if (this.audioContext) {
      this.audioContext.destroy();
    }
    this.audioContext = wx.createInnerAudioContext();
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

  async loadPlaceAndRoute() {
    try {
      let place: FavoritePlace | null = null;

      // 尝试从本地缓存获取 place
      const cachedPlace = getPlace(this.data.placeId);
      if (cachedPlace) {
        place = cachedPlace as FavoritePlace;
        this.setData({ placeName: place.place_name });
      }

      // 没有缓存，调用后端获取
      if (!place) {
        place = await favoritePlacesApi.getFavoritePlaceById(this.data.placeId);
        savePlace(place);
        this.setData({ placeName: place.place_name });
      }

      await this.planRoute(place);
    } catch (err: any) {
      console.error('加载地点或路线失败:', err);
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    }
  },

  async planRoute(place: FavoritePlace) {
    try {
      const res = await wx.getLocation({
        type: 'gcj02'
      });

      console.log('当前定位:', res.latitude, res.longitude);
      console.log('目标地点:', place.place_id, place.place_name, place.latitude, place.longitude);

      let route: AddressNavigationResponse['route'] | null = null;

      // 尝试从本地缓存获取 route
      const cachedRoute = getRoute(place.place_id);
      if (cachedRoute) {
        console.log('使用本地缓存路线:', cachedRoute);
        route = cachedRoute as AddressNavigationResponse['route'];
      }

      // 没有缓存，调用后端获取
      if (!route) {
        const routeRes = await navigationApi.navigateByAddress({
          favorite_place_id: place.place_id,
          origin_lng: res.longitude.toString(),
          origin_lat: res.latitude.toString()
        });

        console.log('路线规划结果:', routeRes);
        route = routeRes.route;

        // 保存到本地缓存
        saveRoute(place.place_id, route);
      }

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
      console.error('规划路线失败:', err);
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
    this.locationWatchId = setInterval(() => {
      this.updateCurrentPosition();
    }, 3000);
  },

  stopLocationWatch() {
    if (this.locationWatchId) {
      clearInterval(this.locationWatchId);
      this.locationWatchId = 0;
    }
  },

  async updateCurrentPosition() {
    if (!this.cachedRoute || this.isUnloading) return;

    try {
      const res = await wx.getLocation({ type: 'gcj02' });
      const { route, allPoints, traveledPoints, currentStepIndex } = this.cachedRoute;

      if (this.lastLocation) {
        const distance = this.calculateDistance(
          this.lastLocation.latitude, this.lastLocation.longitude,
          res.latitude, res.longitude
        );

        if (distance > 2) {
          traveledPoints.push({ latitude: res.latitude, longitude: res.longitude });
          this.cachedRoute.traveledPoints = traveledPoints;
          this.updateTraveledPolyline(traveledPoints);

          locationApi.createLocation({
            latitude: res.latitude,
            longitude: res.longitude,
            accuracy: res.accuracy,
            record_id: this.cachedRoute.recordId
          }).catch((err) => {
            console.error('记录位置失败:', err);
          });
        }
      }
      this.lastLocation = { latitude: res.latitude, longitude: res.longitude };

      const newStepIndex = this.findCurrentStepIndex(res.latitude, res.longitude, route.steps || []);
      this.cachedRoute.currentStepIndex = newStepIndex;

      if (newStepIndex !== currentStepIndex) {
        const instruction = route.steps?.[newStepIndex]?.instruction || '';
        if (instruction && newStepIndex > this.cachedRoute.lastInstructionStep) {
          this.speakInstruction(instruction);
          this.cachedRoute.lastInstructionStep = newStepIndex;
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

  async reroute() {
    if (!this.cachedRoute || this.data.isRerouting || this.isUnloading) return;

    this.setData({ isRerouting: true });

    try {
      const res = await wx.getLocation({ type: 'gcj02' });

      const routeRes = await navigationApi.navigateByAddress({
        favorite_place_id: this.data.placeId,
        origin_lng: res.longitude.toString(),
        origin_lat: res.latitude.toString()
      });

      const { route } = routeRes;
      const allPoints = this.parsePolylineArray(route.polyline);

      // 更新本地缓存
      saveRoute(this.data.placeId, route);

      this.cachedRoute = {
        ...this.cachedRoute,
        route,
        recordId: route.record_id || this.cachedRoute.recordId,
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
      wx.showToast({
        title: '重新规划失败',
        icon: 'none'
      });
    }
  },

  speakInstruction(text: string) {
    if (!this.audioContext) {
      this.initAudioContext();
    }

    const speakText = text.replace(/<[^>]+>/g, '');

    if (!speakText) return;

    speechApi.textToSpeech({ text: speakText })
      .then((res) => {
        if (res.status === 'success' && res.audio_data) {
          this.audioContext.src = `data:${res.audio_type};base64,${res.audio_data}`;
          this.audioContext.play();
        }
      })
      .catch((err) => {
        console.error('TTS请求失败:', err);
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
  }
});
