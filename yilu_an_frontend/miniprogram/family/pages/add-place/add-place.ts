// add-place.ts
import { favoritePlacesApi } from '../../../api/favorite-places';
import { getCurrentElder } from '../../storage';
import { TENCENT_MAP_KEY } from '../../../utils/config';

// TODO: 待完善，添加地图选择功能和地址详情功能
interface SearchResult {
  id: string;
  title: string;
  address: string;
  latitude: number;
  longitude: number;
}

interface Marker {
  id: number;
  latitude: number;
  longitude: number;
  width: number;
  height: number;
}

Page({
  data: {
    isEdit: false,
    placeId: null as number | null,
    placeName: '',
    searchKeyword: '',
    latitude: 36.65140539399413,
    longitude: 117.11395963744008,
    selectedAddress: '',
    detailAddress: '',
    markers: [] as Marker[],
    searchResults: [] as SearchResult[],
    showSearchResults: false,
    isSearching: false,
    isLoadingLocation: true,
    currentCity: '济南'
  },

  searchTimer: null as ReturnType<typeof setTimeout> | null,

  onLoad(options: any) {
    if (options.place_id) {
      this.setData({ isEdit: true, placeId: parseInt(options.place_id) });
      this.loadPlaceDetail(parseInt(options.place_id));
    } else {
      this.getCurrentLocation();
    }
  },

  getCurrentLocation() {
    this.setData({ isLoadingLocation: true });
    
    wx.getSetting({
      success: (settingRes) => {
        if (settingRes.authSetting['scope.userLocation'] === false) {
          wx.showModal({
            title: '需要位置权限',
            content: '请前往设置页面开启位置权限，以便获取您的当前位置',
            confirmText: '去设置',
            success: (modalRes) => {
              if (modalRes.confirm) {
                wx.openSetting({
                  success: (openSettingRes) => {
                    if (openSettingRes.authSetting['scope.userLocation']) {
                      this.doGetLocation();
                    } else {
                      this.setData({ isLoadingLocation: false });
                      this.reverseGeocode(this.data.latitude, this.data.longitude);
                    }
                  }
                });
              } else {
                this.setData({ isLoadingLocation: false });
                this.reverseGeocode(this.data.latitude, this.data.longitude);
              }
            }
          });
        } else {
          this.doGetLocation();
        }
      },
      fail: () => {
        this.doGetLocation();
      }
    });
  },

  doGetLocation() {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        this.setData({
          latitude: res.latitude,
          longitude: res.longitude,
          isLoadingLocation: false
        });
        this.reverseGeocode(res.latitude, res.longitude);
      },
      fail: (err) => {
        console.error('获取位置失败:', err);
        this.setData({ isLoadingLocation: false });
        wx.showToast({ title: '获取位置失败，将使用默认位置', icon: 'none' });
        this.reverseGeocode(this.data.latitude, this.data.longitude);
      }
    });
  },

  loadPlaceDetail(placeId: number) {
    favoritePlacesApi.getFavoritePlaceById(placeId)
      .then((res) => {
        const place = res;
        this.setData({
          placeName: place.place_name,
          latitude: place.latitude,
          longitude: place.longitude,
          selectedAddress: place.address,
          detailAddress: '',
          markers: [{
            id: 1,
            latitude: place.latitude,
            longitude: place.longitude,
            width: 30,
            height: 30
          }]
        });
        this.reverseGeocode(place.latitude, place.longitude);
      })
      .catch((err) => {
        wx.showToast({ title: '获取地点详情失败', icon: 'none' });
      });
  },

  reverseGeocode(latitude: number, longitude: number) {
    wx.request({
      url: `https://apis.map.qq.com/ws/geocoder/v1/?location=${latitude},${longitude}&key=${TENCENT_MAP_KEY}`,
      success: (res: any) => {
        if (res.data.status === 0) {
          const city = res.data.result.address_component?.city || '济南';
          this.setData({
            selectedAddress: res.data.result.address || '未知地址',
            currentCity: city
          });
        }
      },
      fail: (err) => {
        console.error('逆地理编码失败:', err);
      }
    });
  },

  goBack() {
    wx.navigateBack();
  },

  onUnload() {
    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
      this.searchTimer = null;
    }
  },

  onPlaceNameChange(e: any) {
    this.setData({ placeName: e.detail.value });
  },

  onDetailAddressChange(e: any) {
    this.setData({ detailAddress: e.detail.value });
  },

  onSearchInput(e: any) {
    const keyword = e.detail.value;
    this.setData({ searchKeyword: keyword });
    
    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
    }

    if (keyword.trim()) {
      this.searchTimer = setTimeout(() => {
        this.searchLocation(keyword);
      }, 300);
    } else {
      this.setData({ searchResults: [], showSearchResults: false });
    }
  },

  onSearchFocus() {
    if (this.data.searchKeyword) {
      this.setData({ showSearchResults: true, isSearching: true });
    }
  },

  onSearchConfirm(e: any) {
    const keyword = e.detail.value;
    if (keyword.trim()) {
      this.searchLocation(keyword);
    }
  },

  cancelSearch() {
    this.setData({
      searchKeyword: '',
      searchResults: [],
      showSearchResults: false,
      isSearching: false
    });
  },

  searchLocation(keyword: string) {
    this.setData({ isSearching: true, searchResults: [] });
    wx.request({
      url: `https://apis.map.qq.com/ws/place/v1/suggestion?keyword=${encodeURIComponent(keyword)}&region=${encodeURIComponent(this.data.currentCity)}&key=${TENCENT_MAP_KEY}`,
      success: (res: any) => {
        console.log('搜索结果:', res.data);
        if (res.data.status === 0 && res.data.data && res.data.data.length > 0) {
          const results: SearchResult[] = res.data.data.map((item: any, index: number) => ({
            id: item.id || String(index),
            title: item.title,
            address: item.address || '',
            latitude: item.location.lat,
            longitude: item.location.lng
          }));
          this.setData({
            searchResults: results,
            showSearchResults: true,
            isSearching: false
          });
        } else {
          this.setData({
            searchResults: [],
            showSearchResults: true,
            isSearching: false
          });
        }
      },
      fail: (err) => {
        console.error('搜索失败:', err);
        this.setData({
          searchResults: [],
          showSearchResults: true,
          isSearching: false
        });
      }
    });
  },

  selectSearchResult(e: any) {
    const location = e.currentTarget.dataset.location;
    this.setData({
      latitude: location.latitude,
      longitude: location.longitude,
      selectedAddress: location.address || location.title,
      searchKeyword: location.title,
      showSearchResults: false,
      isSearching: false
    });
    this.updateMarker(location.latitude, location.longitude);
  },

  onMapTap() {
    this.setData({ showSearchResults: false });
  },

  onRegionChange(e: any) {
    if (e.type === 'end') {
      const mapContext = wx.createMapContext('locationMap');
      mapContext.getCenterLocation({
        success: (res: any) => {
          this.setData({
            latitude: res.latitude,
            longitude: res.longitude,
            markers: [{
              id: 1,
              latitude: res.latitude,
              longitude: res.longitude,
              width: 30,
              height: 30
            }]
          });
          this.reverseGeocode(res.latitude, res.longitude);
        }
      });
    }
  },

  updateMarker(lat: number, lng: number) {
    this.setData({
      markers: [{
        id: 1,
        latitude: lat,
        longitude: lng,
        width: 30,
        height: 30
      }]
    });
    this.reverseGeocode(lat, lng);
  },

  submitForm() {
    if (!this.data.placeName) {
      wx.showToast({ title: '请输入地点名称', icon: 'none' });
      return;
    }

    if (!this.data.selectedAddress) {
      wx.showToast({ title: '请选择位置', icon: 'none' });
      return;
    }

    const elder = getCurrentElder();
    if (!elder) {
      wx.showToast({ title: '请选择监护老人', icon: 'none' });
      return;
    }

    const fullAddress = this.data.detailAddress 
      ? `${this.data.selectedAddress} ${this.data.detailAddress}`
      : this.data.selectedAddress;

    const params = {
      user_id: parseInt(elder.id),
      place_name: this.data.placeName,
      latitude: this.data.latitude,
      longitude: this.data.longitude,
      address: fullAddress,
      source_type: 1,
      is_active: true
    };

    if (this.data.isEdit && this.data.placeId) {
      favoritePlacesApi.updateFavoritePlace(this.data.placeId, params)
        .then(() => {
          wx.showToast({ title: '更新成功', icon: 'success' });
          setTimeout(() => wx.navigateBack(), 1500);
        })
        .catch(() => {
          wx.showToast({ title: '更新失败', icon: 'none' });
        });
    } else {
      favoritePlacesApi.createFavoritePlace(params)
        .then(() => {
          wx.showToast({ title: '保存成功', icon: 'success' });
          setTimeout(() => wx.navigateBack(), 1500);
        })
        .catch(() => {
          wx.showToast({ title: '保存失败', icon: 'none' });
        });
    }
  }
});