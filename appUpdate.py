import requests
import json
from tkinter import *
import time

class ParseStationName():
    def get_html(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }
        url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9025'
        r = requests.get(url, headers=headers, verify = False)
        return r.text

    #该方法将城市名称转换成代号
    def parse(self, name):
        html = self.get_html()
        pattern = u'([\u4e00-\u9fa5]+)\|([A-Z]+)'
        result = re.findall(pattern, html)
        ids = dict(result)
        return ids[name]

    #该方法返回席别对应的代号
    def way_of_trains(self, way):
        dict = {
            '一等座':-5,
            '二等座':-6,
            '软卧':-13,
            '硬卧':-8,
            '软座':-11,
            '硬座':-7,
            '无座':-10,
        }
        return dict[way]


class Query(ParseStationName):  #继承查询城市代号类，便于修改url
    def __init__(self, from_city, to_city, date, way_of_train):
        self.from_city = self.parse(from_city)
        self.to_city = self.parse(to_city)
        self.date = date         #这里date的格式为2017-09-19
        self.way = self.way_of_trains(way_of_train)

    #解析12306的异步加载，拿到关键信息
    def result(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
        }
        url= 'https://kyfw.12306.cn/otn/leftTicket/queryx?leftTicketDTO.' \
                    'train_date={}&leftTicketDTO.' \
                    'from_station={}&leftTicketDTO.' \
                    'to_station={}&purpose_codes=ADULT'.format(self.date, self.from_city, self.to_city)
        html = requests.get(url, verify = False, headers=headers).text
        js = json.loads(html)
        return js['data']['result']

        # 根据信息查找到对应的车次，保存信息
    def search(self):
        list_car_info = []
        result = self.result()
        for car in result:
            cars = car.split('|')
            if cars[self.way] != '无' and cars[self.way] != '':  # 如果查找的席位存在，则收录这趟车的信息
                print(cars[-33] + ':' + cars[-10])
                list_car_info.append([cars[-33], cars[self.way], cars[-28], cars[-27], cars[-26]])
        return list_car_info


class Input(object):
    def __init__(self):
        self.tk = Tk()
        self.label1 = Label(self.tk, text="出发地").grid(row=0, column=0)
        self.label2 = Label(self.tk, text="目的地").grid(row=1, column=0)
        self.label3 = Label(self.tk, text="出发日").grid(row=2, column=0)
        self.label4 = Label(self.tk, text="　席别").grid(row=3, column=0)
        t1= StringVar()
        t2 = StringVar()
        t3 = StringVar()
        t4 = StringVar()
        t1.set('石家庄')
        t2.set('长沙')
        t3.set('2017-10-18')
        t4.set('硬卧')
        self.entry1 = Entry(self.tk, textvariable=t1)
        self.entry2 = Entry(self.tk, textvariable=t2)
        self.entry3 = Entry(self.tk, textvariable=t3)
        self.entry4 = Entry(self.tk, textvariable=t4)
        self.entry1.grid(row=0, column=1)
        self.entry2.grid(row=1, column=1)
        self.entry3.grid(row=2, column=1)
        self.entry4.grid(row=3, column=1)
        self.button = Button(self.tk, text="确定", command=self.yeah).grid(row=5,column=1)

    def yeah(self):
        tk = Tk()
        from_city = self.entry1.get()
        to_city = self.entry2.get()
        date = self.entry3.get()
        way = self.entry4.get()
        tk.title("{}-{} by {}".format(from_city, to_city, way))
        start_time = time.time()
        q = Query(from_city, to_city, date, way)
        list = []
        try:
            list = q.search()
            if len(list) > 0:
                t = Text(tk, width=50, height=45)
                tpl = "{:^6}\t{:^6}\t{:^10}\t{:^8}\t{:^8}\n"
                t.grid(row=0)
                t.insert(INSERT, "日期：{}\n\n 车次\t余票情况\t出发时间\t到达时间\t  历时\n".format(date))
                end_time = time.time()
                dur = end_time - start_time
                for car in list:
                    t.insert(INSERT, tpl.format(car[0], car[1], car[2], car[3], car[4]))
                t.insert(END, "\n查询时间为{:.2f}秒".format(dur))
            else:
                end_time = time.time()
                dur = end_time - start_time
                Message(tk, width=100, text="没有票哎！\n查询时间为{:.2f}秒".format(dur)).pack()
        except:
            Message(tk, width=300, text="错误原因，ip访问次数过多，稍等即可\n请重试！").pack()

    def run(self):
        self.tk.mainloop()

app = Input()
app.run()