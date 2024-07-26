# -*- coding: utf-8 -*
"""
使用chinese_calendar对一年的日期进行标识
需要注意：新的一年需要前一年的11月才会更新（如：2023年的数据，需要在2022年11月以后才可获取到）

@Author: Mintimate
@Date: 20240726
"""
import datetime
import os
from enum import Enum
import re
import chinese_calendar as calendar
import pandas as pd

# 生成SQL脚本的目标数据库
TARGET_TABLE = "WORK_CALENDAR"
# 脚本生成的目标年份
TARGET_YEAR = 2023
# 生成代码的位置
TARGET_SAVE_PATH = "work_calendar.csv"


class DATATYPE(Enum):
    """
    日期类型枚举类
    """
    普通工作日 = "0"
    普通周末 = "3"
    节日假期 = "1"
    节日补班 = "2"


def check_dir_exist(dir_path):
    """
    判断目录是否存在，不存在则创建并返回绝对路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    if not os.path.isabs(dir_path):
        # 目录为相对路径，那么转换为绝对路径
        dir_path = os.path.abspath(dir_path)
    return dir_path


# 得到一年中所有的日期
def get_whole_year(year=TARGET_YEAR):
    """
    获取一年内所有的日期
    :param year: 获取的年
    :return: 日期数组
    """
    begin = datetime.date(year, 1, 1)
    now = begin
    end = datetime.date(year, 12, 31)
    delta = datetime.timedelta(days=1)
    days = []
    while now <= end:
        days.append(now.strftime("%Y-%m-%d"))
        now += delta
    return days


# 判断日期
def judge_date_type(judge_date):
    """
    判断日期的类型
    :param judge_date:
    :return: 判断的类型；如果是假期有关，附带假期备注
    """
    date = datetime.datetime.strptime(judge_date, '%Y-%m-%d').date()
    if calendar.is_holiday(date):
        print("%s是节假日" % judge_date)
        on_holiday, holiday_name = calendar.get_holiday_detail(date)
        # 判断是否为节日（否：周末；是：节日）
        if holiday_name is not None:
            return DATATYPE.节日假期.value + "-" + str(holiday_name)
        else:
            return DATATYPE.普通周末.value
    elif calendar.is_workday(date):
        on_holiday, holiday_name = calendar.get_holiday_detail(date)
        if holiday_name is not None:
            print("%s是补班日" % judge_date)
            return DATATYPE.节日补班.value + "-" + str(holiday_name)
        else:
            return DATATYPE.普通工作日.value
    else:
        print("%s没有匹配" % judge_date)
        return "NULL"


def write_sql_file(parma0, parma1, parma2, parma3):
    file_path_saver = "{FATHER_PATH}}.sql".format(parma0, parma1)
    f = open('./2023Day.sql', 'a', encoding='utf-8')
    parma3 = re.sub(r"\'", "\'\'", parma3)
    # 追加内容
    f.write("INSERT INTO " + TARGET_TABLE + " VALUES(\'%s\',\'%s\',\'%s\',\'%s\');" % (parma0, parma1, parma2, parma3))
    f.write("\n")
    f.close()


if __name__ == "__main__":
    dataf = pd.DataFrame(columns=['YEAR', 'CALENDAR_DATE', 'DATE_TYPE', 'COMMENTS'])
    for index, one_date in enumerate(get_whole_year()):
        type = judge_date_type(one_date).split('-')
        if len(type) > 1:
            write_sql_file(TARGET_YEAR, one_date, type[0], type[1])
            dataf.loc[index] = [TARGET_YEAR, one_date, type[0], type[1]]
        else:
            write_sql_file(TARGET_YEAR, one_date, type[0], "")
            dataf.loc[index] = [TARGET_YEAR, one_date, type[0], ""]
    dataf.to_csv("./2023Day.csv", index=False)
    print(dataf)
