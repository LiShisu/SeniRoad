import { favoritePlacesApi } from '../../../api/favorite-places';
import type { FavoritePlace } from '../../../api/favorite-places';
import { navigationApi, AddressNavigationResponse, NavigationStep } from '../../../api/navigation';
import { locationApi } from '../../../api/location';
import { getPlace, savePlace, getRoute, saveRoute } from '../../storage';
import { getLocation } from '../../../utils/geo';
import { playSpeech } from '../../../utils/speech-player';

interface CachedRouteData {
  route: any; // 改为 any，以便后续强行注入压平后的 steps 数组，兼容双模
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
    // 接住从 plan.ts 传过来的模式和城市状态
    travelMode: 'walking', 
    city: '济南市'
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
    // 核心修改：接住传过来的参数并保存到 data，偏航重算时必须靠它们
    if (options?.travelMode) {
      this.setData({ 
        travelMode: options.travelMode,
        city: options.city || '济南市'
      });
    }
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
// 核心新增：数据压平适配器，把公交换乘图网变成一条直线
normalizeRouteSteps(route: any): NavigationStep[] {
  // 1. 如果是标准的步行（自身带有 steps 数组），直接原样返回
  if (route.steps && route.steps.length > 0) {
    return route.steps;
  }
  
  // 2. 如果是公交模式 (含有高德 segments)
  const normalizedSteps: NavigationStep[] = [];
  if (route.segments) {
    route.segments.forEach((seg: any) => {
      // A. 提取“步行前往车站”的段落
      if (seg.walking && seg.walking.steps) {
        normalizedSteps.push(...seg.walking.steps);
      }
      // B. 提取“乘坐公交车/地铁”，并将其伪装成一个普通 Step！
      if (seg.bus && seg.bus.name) {
        // 🌟【核心修复点】：智能清洗高德的“中间过0站”反人类文案
        const rawViaNum = parseInt(seg.bus.via_num);
        let busStationInstruction = '';

        if (isNaN(rawViaNum) || rawViaNum === 0) {
          // A. 如果中间经过 0 站，说明一上一下就到了，大白话就是“坐 1 站”
          busStationInstruction = `乘坐 ${seg.bus.name}，从 [${seg.bus.departure_stop}] 上车，坐 1 站，在 [${seg.bus.arrival_stop}] 下车`;
        } else {
          // B. 如果有中间站，更符合老人的大白话是告诉他“总共要坐几站路”，而不是“中间经过几站”
          const totalStations = rawViaNum + 1;
          busStationInstruction = `乘坐 ${seg.bus.name}，从 [${seg.bus.departure_stop}] 上车，总共坐 ${totalStations} 站，在 [${seg.bus.arrival_stop}] 下车`;
        }

        normalizedSteps.push({
          instruction: busStationInstruction, // 喂入符合老一辈语言习惯的完美文案
          distance: seg.bus.distance || '0', 
          duration: seg.bus.duration || '0',
          road: seg.bus.name,
          polyline: seg.bus.polyline
        });
      }
    });
  }
  return normalizedSteps;
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

    // 1. 读取对应出行模式下的路线缓存
    const cachedRoute = getRoute(this.data.placeId, this.data.travelMode);
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

    // 🌟 【核心修改点 1】：在所有渲染和赋值操作之前，“强行提前”执行压平清洗！
    // 这样能百分百保证后面所有地方（无论是画地图、更新进度、还是初始语音）拿到的都是干净的一维公交步骤。
    const activeSteps = this.normalizeRouteSteps(route);
    route.steps = activeSteps; // 强行洗白成一维结构

    const res = await getLocation();
    const allPoints = this.parsePolylineArray(route.polyline);

    // 2. 构建全局缓存路由数据（此时里面的 route 已经是被我们洗过 steps 的安全对象了）
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

    // 3. 渲染地图要素
    this.parseRoute(route, allPoints, res.latitude, res.longitude, place.latitude, place.longitude);
    
    // 4. 开启位置追踪
    this.startLocationWatch();
    
    // 5. 记录位置日志到后端
    locationApi.createLocation({
      latitude: res.latitude,
      longitude: res.longitude,
      accuracy: res.accuracy,
      record_id: route.record_id
    }).catch((err) => {
      console.error('初始化位置记录失败:', err);
    });

    // 🌟 【核心修改点 2】：直接使用我们提前锁死并压平的变量，精准播报首站
    // 绝对不会存在任何异步 race condition 导致读到旧步行数据的可能！
    const firstInstruction = activeSteps[0]?.instruction || '导航开始，请跟随蓝色路线指引前行';
    this.speakInstruction(firstInstruction);

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

    // 🌟【核心修改点 1】：在所有赋值、渲染前，强行提早将语音路线进行压平清洗
    // 这样能百分百保证后面构建 cachedRoute 和 parseRoute 拿到的都是洗干净的一维公交/步行步骤
    const activeSteps = this.normalizeRouteSteps(route);
    route.steps = activeSteps; // 强行洗白覆盖结构

    // 2. 获取当前位置作为起点
    const res = await getLocation();
    const allPoints = this.parsePolylineArray(route.polyline);

    // 3. 构建缓存路由数据结构（对齐原本的 this.cachedRoute，此时里面的 route 已经安全了）
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

    locationApi.createLocation({
      latitude: res.latitude,
      longitude: res.longitude,
      accuracy: res.accuracy,
      record_id: route.record_id
    }).catch((err) => {
      console.error('初始化位置记录失败:', err);
    });

    // 🌟【核心修改点 2】：直接使用我们提前锁死并压平的局部变量变量，精准播报首站
    // 避开了原本异步操作带来的时序差，100% 播报正确的公交/步行导航词
    const firstInstruction = activeSteps[0]?.instruction || `开始导航前往 ${destInfo.destination}`;
    this.speakInstruction(firstInstruction);

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
  parseRoute(route: any, allPoints: { latitude: number; longitude: number }[], originLat: number, originLng: number, destLat: number, destLng: number) {
    // 1. 强行提早执行数据压平清洗（前面几步我们已经改过这里了）
    const activeSteps = this.normalizeRouteSteps(route);
    route.steps = activeSteps;

    // 🌟【核心修复点】：智能全路段轨迹缝合
    let finalPoints = allPoints;
    
    if (this.data.travelMode === 'transit' && activeSteps.length > 0) {
      console.log('🗺️ 正在为长辈缝合“步行段+公交段”的完整全生命周期全景路线图...');
      const combinedPolylineSegments: string[] = [];
      
      activeSteps.forEach(step => {
        if (step.polyline) {
          combinedPolylineSegments.push(step.polyline);
        }
      });
      
      if (combinedPolylineSegments.length > 0) {
        // 把所有的 步行小段、公交大段的经纬度字符串用分号牢牢缝合在一起！
        const fullCombinedPolylineStr = combinedPolylineSegments.join(';');
        // 重新解析出包含下车后步行 500 米的完整全景坐标数组
        finalPoints = this.parsePolylineArray(fullCombinedPolylineStr);
      }
    }

    const markers = [
      {
        id: 0, latitude: originLat, longitude: originLng,
        iconPath: '/assets/images/location-marker-start.png', width: 40, height: 40,
        label: { content: '起点', fontSize: 20, color: '#333' }
      },
      {
        id: 1, latitude: destLat, longitude: destLng,
        iconPath: '/assets/images/location-marker-end.png', width: 40, height: 40,
        label: { content: this.data.placeName, fontSize: 20, color: '#333' }
      }
    ];

    this.setData({
      // 🌟 核心修改 2：把缝合后绝对饱满、直达终点的 finalPoints 塞给地图组件画线
      polyline: [{
        points: finalPoints,
        color: '#4B8AFF',
        width: 6,
        dottedLine: false
      }],
      markers,
      mapCenter: {
        latitude: (originLat + destLat) / 2,
        longitude: (originLng + destLng) / 2
      },
      
      // 耗时单位清洗（保持前面修改好的不变）
      totalDistance: route.distance,
      totalDuration: this.data.travelMode === 'transit' 
        ? `${Math.round(parseInt(route.duration) / 60)}分钟` 
        : `${Math.round(parseInt(route.duration) / 60)}分钟`,
        
      stepsCount: activeSteps.length,
      currentInstruction: activeSteps[0]?.instruction || '',
      currentStepDistance: activeSteps[0]?.distance || '',
      currentStepRoad: activeSteps[0]?.road || '',
      isDeviating: false,
      isRerouting: false
    });

    // 🌟 核心修改 3：更新全局 cachedRoute 里的全路径点集，防止位置更新时算偏航算错
    if (this.cachedRoute) {
      this.cachedRoute.allPoints = finalPoints;
    }

    setTimeout(() => {
      // 确保缩放视野时能把整条全景线全部安全包裹进来
      this.mapCtx?.includePoints({
        points: finalPoints,
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

      // 🌟 核心修复 1：强行带上当前的 travelMode 和 city 传给后端
      const currentMode = this.data.travelMode || 'walking';
      const currentCity = this.data.city || '济南市';

      if (this.data.isVoiceMode) {
        routeRes = await navigationApi.navigateByCoordinates({
          origin_lng: res.longitude.toString(),
          origin_lat: res.latitude.toString(),
          dest_lng: this.cachedRoute.destLng.toString(),
          dest_lat: this.cachedRoute.destLat.toString(),
          travel_mode: currentMode as any, 
          city: currentCity                
        });
      } else {
        let place: FavoritePlace | null = getPlace(this.data.placeId) as FavoritePlace;
        if (!place) {
          place = await favoritePlacesApi.getFavoritePlaceById(this.data.placeId);
          savePlace(place);
        }
        routeRes = await navigationApi.navigateByAddress({
          favorite_place_id: this.data.placeId,
          origin_lng: res.longitude.toString(),
          origin_lat: res.latitude.toString(),
          travel_mode: currentMode as any, // 👈 确保请求带上 mode
          city: currentCity                // 👈 确保请求带上 city
        });
      }

      const { route } = routeRes;
      const allPoints = this.parsePolylineArray(route.polyline);

      // 🌟 核心修复 2：保存重算路线时，必须把 currentMode 传进去！否则会覆盖默认步行缓存！
      if (!this.data.isVoiceMode) {
        saveRoute(this.data.placeId, route, currentMode); 
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
        isDeviating: false,
        isRerouting: false
      });

      // 🌟 核心修复 3：由于公交路线的第一步往往是走去车站，我们需要在进入 parseRoute 之前
      // 把偏航阈值动态调整。如果是公交，调大到 150 米（无障碍防抖）；如果是步行，恢复 50 米。
      if (currentMode === 'transit') {
        this.deviationThreshold = 150; // 公交容错率提高，防止起点秒偏航
      } else {
        this.deviationThreshold = 50;  // 步行依然保持严格
      }

      // 重算后再次调用 parseRoute 压平数据并播报
      this.parseRoute(route, allPoints, res.latitude, res.longitude, this.cachedRoute.destLat, this.cachedRoute.destLng);
      this.speakInstruction('路线已重新规划，继续前行');

      setTimeout(() => {
        this.mapCtx?.includePoints({
          points: allPoints,
          padding: [50, 50, 50, 50]
        });
      }, 100);
      console.log(`[${currentMode}] 路线偏航重新规划成功`);
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
