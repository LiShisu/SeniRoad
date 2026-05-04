const AVATAR_COLORS = ['#4B8AFF', '#FF8C42', '#52C41A', '#FF4D4F', '#722ED1', '#1890FF'];

function getLuminance(hex: string): number {
  const rgb = parseInt(hex.slice(1), 16);
  const r = (rgb >> 16) & 0xFF;
  const g = (rgb >> 8) & 0xFF;
  const b = rgb & 0xFF;
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255;
}

Component({
  properties: {
    avatarUrl: {
      type: String,
      value: ''
    },
    nickname: {
      type: String,
      value: ''
    },
    backgroundColor: {
      type: String,
      value: ''
    },
    textColor: {
      type: String,
      value: '#FFFFFF'
    },
    index: {
      type: Number,
      value: -1
    }
  },
  data: {
    computedBgColor: '',
    computedTextColor: ''
  },
  lifetimes: {
    attached() {
      this.updateColors();
    }
  },
  observers: {
    'backgroundColor, index': function() {
      this.updateColors();
    }
  },
  methods: {
    updateColors() {
      let bgColor = this.data.backgroundColor;
      if (!bgColor && this.data.index >= 0) {
        bgColor = AVATAR_COLORS[this.data.index % AVATAR_COLORS.length];
      }
      if (!bgColor) {
        bgColor = '#FF8C42';
      }
      
      let textColor = this.data.textColor;
      if (!this.data.textColor) {
        textColor = getLuminance(bgColor) < 0.6 ? '#FFFFFF' : '#000000';
      }
      
      this.setData({
        computedBgColor: bgColor,
        computedTextColor: textColor
      });
    }
  }
})