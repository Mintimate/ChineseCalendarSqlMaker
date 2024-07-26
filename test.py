# -*- coding: utf-8 -*
import datetime
import chinese_calendar as calendar

if __name__ == '__main__':
    dateTest = datetime.date(2023, 5, 3)
    print(calendar.get_holiday_detail(dateTest))
