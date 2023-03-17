import re
from datetime import datetime, timedelta

debug = False

# 月份转换字典
def convert_month(str, country):
    '''
    如何获得字典：
    locale.setlocale(locale.LC_ALL, "es_ES")
    for i in range(1,13):
        x=datetime.datetime(2021, i, 6, 15, 51, 27)
        print(f"\"{x.strftime('%b')}\":\"{str(i).zfill(2)}\",")
    '''
    fr_dict = {"janv":"01","févr":"02","mars":"03","avr":"04","mai":"05","juin":"06","juil":"07","août":"08","sept":"09","oct":"10","nov":"11","déc":"12"}
    it_dict = {"gen":"01","feb":"02","mar":"03","apr":"04","mag":"05","giu":"06","lug":"07","ago":"08","set":"09","ott":"10","nov":"11","dic":"12"}
    es_dict = {"ene":"01","feb":"02","mar":"03","abr":"04","may":"05","jun":"06","jul":"07","ago":"08","sep":"09","sept":"09","oct":"10","nov":"11","dic":"12"}
    en_dict = {"jan":"01","feb":"02","mar":"03","apr":"04","may":"05","jun":"06","jul":"07","aug":"08","sep":"09","sept":"09","oct":"10","nov":"11","dec":"12"}
    # 加拿大不知为何，下载下来日期会带.
    str = str.replace(".","")
    str_dict = None
    if country == "法国":
        str_dict = fr_dict
    elif country == "意大利":
        str_dict = it_dict
    elif country == "西班牙":
        str_dict = es_dict
    elif country == "英国" or country == "美国" or country == "加拿大":
        str_dict = en_dict
    else:
        raise ValueError(f"{country}未被定义")
    return str_dict.get(str.lower())

# 除去干扰符号，全部用" "间隔
def clean_time_string(before_deal):
    '''
    Jan 1, 2021 6:23:06 AM PST -> Jan 1  2021 6:23:06 AM PST
    2020/7/1 9:07 -> 2020 7 1 9:07
    May 1, 2021 12:22:44 a.m. PDT -> May 1  2021 12:22:44 a.m. PDT(这边若去除.会把am分割，故先不去除)
    '''
    after_deal = re.sub(r'[,/]'," ",before_deal)
    if debug:
        print(f"数据清洗:{before_deal} -> {after_deal}")
    return after_deal

# 分割文本，去除空值
def split_time_string(before_deal):
    '''
    Jan 1  2021 6:23:06 AM PST -> ['Jan','1','2021','6:23:06','AM','PST']
    2020 7 1 9:07 -> ['2020','7','1','9:07']
    '''
    time_list = before_deal.split(' ')
    new_list = list(filter(None, time_list))
    after_deal = new_list
    if debug:
        print(f"数据分割:{before_deal} -> {after_deal}")
    return after_deal

# 日期格式化
def format_date(date_list, country):
    year = month = day = ""
    index = list(range(0,len(date_list)))
    for i in range(0,len(date_list)):
        data = date_list[i]
        if data[:-1].isalpha():
            # 月份为字母的直接替换为数字
            month = convert_month(data, country)
            index.remove(i)
        elif len(data) > 2:
            year = data
            index.remove(i)
        elif int(data) > 12:
            day = data
            index.remove(i)
    # 若年为空，抛出异常
    if not year:
        raise ValueError(f"日期格式有误，无法解析{date_list}")
    if index:
        if len(index) == 1:
            if not month:
                month = date_list[index[0]]
            else:
                day = date_list[index[0]]
        else:
            # 默认月份在中间位置
            month = date_list[1]
            index.remove(1)
            day = date_list[index[0]]
    # 返回列表，后续需要对 month 进行判断处理
    return [year, month, day]

# 12小时制转24小时制
def convert_time(time_str, ampm):
    '''
    00:00 <-> 12:00AM, 12:00 <-> 12:00PM
    '''
    # 去除"a.m."的干扰
    if "." in ampm:
        ampm = ampm.replace(".","")
    # 时间不一定补0，所以用“：”拆分
    time_list = time_str.split(":")
    hour = time_list[0]
    if ampm.lower() == 'am':
        hour =  "00" if int(hour) == 12 else hour
    elif ampm.lower() == 'pm':
        hour = "12" if int(hour) == 12 else str(int(hour) + 12)
    time_list[0] = hour
    new_time_str= (":").join(time_list)
    if len(time_list) == 2:
        new_time_str += ":00"
    # 返回格式："23:59:59"
    return new_time_str

# 日期、时间合并
def format_datetime(date, time):
    formate = "%Y-%m-%d %H:%M:%S"
    time_str = f"{'-'.join(date)} {time}"
    new_time = datetime.strptime(time_str, formate)
    return new_time

# 分块处理
def format_time_string(before_deal, country):
    if len(before_deal) > 3:
        date = format_date(before_deal[0:3], country)
        time = convert_time(before_deal[3],before_deal[-2])
        zone = before_deal[-1] if before_deal[-1].isalpha() else ""
    else:
        _date = before_deal[0].split(".") if "." in before_deal[0] else before_deal[0]
        date = format_date(_date, country)
        time = convert_time(before_deal[1],before_deal[-2])
        zone = before_deal[-1] if before_deal[-1].isalpha() or "GMT" in before_deal[-1] else None

    after_deal = (format_datetime(date, time), zone)
    if debug:
        print(f"分块处理:{before_deal} -> {after_deal}")
    return after_deal

# 时区转换(根据所给时区转换为UTC-8)
def convert_zone(before_deal):
    date_time, time_zone= before_deal
    TIMEZONE = {"CHN" : 8,"UTC": 0,"JST" : 9,"PST": -8,"PDT": -7, "GMT+00:00": 0}

    if not time_zone:
        after_deal =  datetime.strftime(date_time, "%Y-%m-%d %H:%M:%S")
    else:
        diff_hour = TIMEZONE.get("CHN") - TIMEZONE.get(time_zone)
        new_date_time = date_time + timedelta(hours=diff_hour)
        after_deal = datetime.strftime(new_date_time, "%Y-%m-%d %H:%M:%S")

    if debug:
        print(f"时区转换:{before_deal} -> {after_deal}")
    return after_deal

def run(datestring, country = "美国"):
    if not datestring:
        raise ValueError('%s 不能为空' % datestring)
    # 清楚特殊符号，方便后续分割
    dealed_str = clean_time_string(datestring)
    # 分割，方便提取关键字段
    datetime_list = split_time_string(dealed_str)
    # 获得规范后的时间字符串和时区
    dealed_list = format_time_string(datetime_list, country)
    result_str = convert_zone(dealed_list)
    return result_str

def test(test = None):
    if not test:
        test = [
            ("5 févr. 2021 12:07:06 UTC", "法国"),
            ("6 feb. 2020 1:45:26 UTC", "西班牙"),
            ("5 mar 2020 11:24:07 UTC", "意大利"),
            ("1 Apr 2020 17:38:07 UTC", "英国"),
            ("2020/06/01 11:42:13 JST", "日本"),
            ("Jul 1, 2020 1:07:24 AM PDT", "美国"),
            ("Aug 1, 2020 11:26:31 AM PDT", "美国"),
            ("Sep. 30, 2020 2:20:55 p.m. PDT", "加拿大"),
            ("30.10.2020 22:07:38 GMT+00:00", "德国"),
            ("2020/4/1 8:50:33", "中国")
        ]
    for t in test:
        print(f"{t} ----> {run(t[0],t[1])}")

if __name__ == "__main__":
    test()
