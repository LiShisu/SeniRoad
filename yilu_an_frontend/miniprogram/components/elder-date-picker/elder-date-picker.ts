// elderly-date-picker.ts
Component({
  properties: {
    visible: {
      type: Boolean,
      value: false
    },
    value: {
      type: String,
      value: '1945-01-01'
    }
  },

  data: {
    selectedYear: 1945,
    selectedMonth: 1,
    selectedDay: 1,
    currentYear: new Date().getFullYear(),
    currentMonth: new Date().getMonth() + 1,
    currentDay: new Date().getDate(),
    inputMode: false,
    inputDate: '',
    inputError: ''
  },

  observers: {
    'value': function(value: string) {
      if (value) {
        const [year, month, day] = value.split('-').map(Number);
        this.setData({
          selectedYear: year,
          selectedMonth: month,
          selectedDay: day,
          inputDate: value
        });
      }
    }
  },

  methods: {
    // 切换输入模式
    toggleInputMode() {
      this.setData({
        inputMode: !this.data.inputMode,
        inputError: ''
      });
    },

    // 处理输入变化
    onInputChange(e: any) {
      const inputValue = e.detail.value;
      this.setData({
        inputDate: inputValue,
        inputError: ''
      });

      // 实时验证日期格式
      if (inputValue) {
        const error = this.validateDateFormat(inputValue);
        if (error) {
          this.setData({
            inputError: error
          });
        } else {
          // 格式正确，验证日期合法性
          const [year, month, day] = inputValue.split('-').map(Number);
          if (!this.isDateValid(year, month, day)) {
            this.setData({
              inputError: '日期不能超过当前日期'
            });
          }
        }
      }
    },

    // 验证日期格式
    validateDateFormat(dateString: string): string {
      const regex = /^\d{4}-\d{2}-\d{2}$/;
      if (!regex.test(dateString)) {
        return '日期格式不正确，请输入 YYYY-MM-DD';
      }

      const [year, month, day] = dateString.split('-').map(Number);
      if (month < 1 || month > 12) {
        return '月份必须在 1-12 之间';
      }

      const daysInMonth = this.getDaysInMonth(year, month);
      if (day < 1 || day > daysInMonth) {
        return `日期必须在 1-${daysInMonth} 之间`;
      }

      return '';
    },

    // 获取某个月的天数
    getDaysInMonth(year: number, month: number): number {
      return new Date(year, month, 0).getDate();
    },

    // 检查日期是否超过当前日期
    isDateValid(year: number, month: number, day: number): boolean {
      const { currentYear, currentMonth, currentDay } = this.data;
      if (year > currentYear) return false;
      if (year === currentYear && month > currentMonth) return false;
      if (year === currentYear && month === currentMonth && day > currentDay) return false;
      return true;
    },

    // 年份变化
    onYearChange(e: any) {
      const delta = parseInt(e.currentTarget.dataset.delta);
      let newYear = this.data.selectedYear + delta;

      // 限制年份范围：1900-当前年份
      if (newYear < 1900) newYear = 1900;
      if (newYear > this.data.currentYear) newYear = this.data.currentYear;

      // 如果新日期超过当前日期，调整到当前日期
      if (!this.isDateValid(newYear, this.data.selectedMonth, this.data.selectedDay)) {
        const { currentMonth, currentDay } = this.data;
        this.setData({
          selectedYear: newYear,
          selectedMonth: currentMonth,
          selectedDay: currentDay
        });
        return;
      }

      // 调整日期，确保不超出当月天数
      const daysInMonth = this.getDaysInMonth(newYear, this.data.selectedMonth);
      let newDay = this.data.selectedDay;
      if (newDay > daysInMonth) {
        newDay = daysInMonth;
      }

      this.setData({
        selectedYear: newYear,
        selectedDay: newDay
      });
    },

    // 月份变化
    onMonthChange(e: any) {
      const delta = parseInt(e.currentTarget.dataset.delta);
      let newMonth = this.data.selectedMonth + delta;
      let newYear = this.data.selectedYear;

      // 限制月份范围：1-12
      if (newMonth < 1) {
        newMonth = 12;
        // 如果月份减少到12，年份也减少
        if (this.data.selectedYear > 1900) {
          newYear = this.data.selectedYear - 1;
        }
      } else if (newMonth > 12) {
        newMonth = 1;
        // 如果月份增加到1，年份也增加
        if (this.data.selectedYear < this.data.currentYear) {
          newYear = this.data.selectedYear + 1;
        }
      }

      // 如果新日期超过当前日期，调整到当前日期
      if (!this.isDateValid(newYear, newMonth, this.data.selectedDay)) {
        const { currentYear, currentMonth, currentDay } = this.data;
        this.setData({
          selectedYear: currentYear,
          selectedMonth: currentMonth,
          selectedDay: currentDay
        });
        return;
      }

      // 调整日期，确保不超出当月天数
      const daysInMonth = this.getDaysInMonth(newYear, newMonth);
      let newDay = this.data.selectedDay;
      if (newDay > daysInMonth) {
        newDay = daysInMonth;
      }

      this.setData({
        selectedYear: newYear,
        selectedMonth: newMonth,
        selectedDay: newDay
      });
    },

    // 日期变化
    onDayChange(e: any) {
      const delta = parseInt(e.currentTarget.dataset.delta);
      let newDay = this.data.selectedDay + delta;
      let newMonth = this.data.selectedMonth;
      let newYear = this.data.selectedYear;

      // 限制日期范围：1-当月天数
      if (newDay < 1) {
        // 如果日期减少到小于1，月份也减少，并设置为新月份的最后一天
        if (this.data.selectedMonth > 1) {
          newMonth = this.data.selectedMonth - 1;
          newDay = this.getDaysInMonth(newYear, newMonth);
        } else if (this.data.selectedYear > 1900) {
          newMonth = 12;
          newYear = this.data.selectedYear - 1;
          newDay = this.getDaysInMonth(newYear, newMonth);
        } else {
          newDay = 1;
        }
      } else {
        const daysInMonth = this.getDaysInMonth(this.data.selectedYear, this.data.selectedMonth);
        if (newDay > daysInMonth) {
          newDay = 1;
          // 如果日期增加到1，月份也增加
          if (this.data.selectedMonth < 12) {
            newMonth = this.data.selectedMonth + 1;
          } else if (this.data.selectedYear < this.data.currentYear) {
            newMonth = 1;
            newYear = this.data.selectedYear + 1;
          }
        }
      }

      // 如果新日期超过当前日期，阻止变化
      if (!this.isDateValid(newYear, newMonth, newDay)) {
        return;
      }

      this.setData({
        selectedYear: newYear,
        selectedMonth: newMonth,
        selectedDay: newDay
      });
    },

    // 确认选择
    onConfirm() {
      let selectedYear = this.data.selectedYear;
      let selectedMonth = this.data.selectedMonth;
      let selectedDay = this.data.selectedDay;

      // 如果是输入模式，处理输入的日期
      if (this.data.inputMode && this.data.inputDate) {
        const error = this.validateDateFormat(this.data.inputDate);
        if (error) {
          this.setData({
            inputError: error
          });
          return;
        }

        const [year, month, day] = this.data.inputDate.split('-').map(Number);
        if (!this.isDateValid(year, month, day)) {
          this.setData({
            inputError: '日期不能超过当前日期'
          });
          return;
        }

        selectedYear = year;
        selectedMonth = month;
        selectedDay = day;

        // 更新选择器的状态
        this.setData({
          selectedYear: year,
          selectedMonth: month,
          selectedDay: day
        });
      }

      // 格式化日期为 YYYY-MM-DD
      const formattedDate = `${String(selectedYear).padStart(4, '0')}-${String(selectedMonth).padStart(2, '0')}-${String(selectedDay).padStart(2, '0')}`;

      // 格式化显示日期为 XXXX年X月X日
      const displayDate = `${selectedYear}年 ${selectedMonth}月 ${selectedDay}日`;

      // 触发确认事件
      this.triggerEvent('confirm', {
        value: formattedDate,
        displayValue: displayDate
      });
    },

    // 取消选择
    onCancel() {
      this.triggerEvent('cancel');
    }
  }
});