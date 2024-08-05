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
TARGET_YEAR = 2024
# 生成代码的位置
TARGET_SAVE_PATH = "work_calendar"


class DATATYPE(Enum):
    """
    日期类型枚举类
    """
    WORKDAY = ("0", "普通工作日")
    WEEKEND = ("3", "普通周末")
    HOLIDAY = ("1", "节日假期")
    WORKING_HOLIDAY = ("2", "节日补班")

    def __init__(self, code: str, description: str):
        self.code = code
        self.description = description

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str):
        self._code = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value


def check_dir_exist(dir_path, file_name=None):
    """
    判断目录是否存在，不存在则创建并返回绝对路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    if not os.path.isabs(dir_path):
        # 目录为相对路径，那么转换为绝对路径
        dir_path = os.path.abspath(dir_path)
    if file_name is not None:
        dir_path = os.path.join(dir_path, file_name)
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
        print("{}是节假日".format(judge_date))
        on_holiday, holiday_name = calendar.get_holiday_detail(date)
        # 判断是否为节日（否：周末；是：节日）
        if holiday_name is not None:
            return DATATYPE.HOLIDAY.code + "-" + str(holiday_name)
        else:
            return DATATYPE.WEEKEND.code
    elif calendar.is_workday(date):
        on_holiday, holiday_name = calendar.get_holiday_detail(date)
        if holiday_name is not None:
            # 节日名称为非空，说明是补班，否则就是普通工作日
            print("{}是补班日".format(judge_date))
            return DATATYPE.WORKING_HOLIDAY.code + "-" + str(holiday_name)
        else:
            return DATATYPE.WORKDAY.code
    else:
        # 理论上不存在没有匹配的情况
        print("{}没有匹配" .format(judge_date))
        assert False


def combine_sql(current_year, current_date, current_date_type, date_remark):
    date_remark = re.sub(r"\'", "\'\'", date_remark)
    # 构建SQL语句
    sql = (
        f"INSERT INTO {TARGET_TABLE} VALUES ("
        f"'{current_year}', "
        f"'{current_date}', "
        f"'{current_date_type}', "
        f"'{date_remark}'"
        f");\n"
    )
    return sql


if __name__ == "__main__":
    dataf = pd.DataFrame(columns=['YEAR', 'CALENDAR_DATE', 'DATE_TYPE', 'COMMENTS'])
    save_sql = ""
    for index, one_date in enumerate(get_whole_year()):
        data_param = judge_date_type(one_date).split('-')
        if len(data_param) > 1:
            save_sql = save_sql + combine_sql(TARGET_YEAR, one_date, data_param[0], data_param[1])
            dataf.loc[index] = [TARGET_YEAR, one_date, data_param[0], data_param[1]]
        else:
            save_sql = save_sql + combine_sql(TARGET_YEAR, one_date, data_param[0], "")
            dataf.loc[index] = [TARGET_YEAR, one_date, data_param[0], ""]
    file_path_saver = "{FILE_FULL_PATH}".format(
        FILE_FULL_PATH=check_dir_exist(TARGET_SAVE_PATH, "{}Day".format(TARGET_YEAR)))
    with open("{}.sql".format(file_path_saver), 'w') as f:
        f.write(save_sql)
    dataf.to_csv("{}.csv".format(file_path_saver), index=False)
    print(dataf)
