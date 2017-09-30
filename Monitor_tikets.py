# 对某个日期的某列火车某个席别进行监控
# 一旦发现有票，则发送邮件
import requests
import json
from tkinter import *
import time
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

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

class Query(ParseStationName):   #继承查询城市代号类，便于修改url
    def __init__(self, from_city, to_city, date, way_of_train, train):
        self.from_city = self.parse(from_city)
        self.to_city = self.parse(to_city)
        self.date = date         #这里date的格式为2017-09-19
        self.way = self.way_of_trains(way_of_train)       #席别
        self.train = train

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
        result = self.result()
        train_infor = ''
        while train_infor == '':
            print('\r开始监控啦，每3s发送一次查票请求，请耐心等待，当前时间{}'.format(time.ctime()), end='')
            for car in result:
                cars = car.split('|')
                # 如果这趟车的这个席位存在，则打印信息发送邮件并退出监控循环
                if cars[self.way] != '无' and cars[self.way] != '' and cars[-33] == self.train:
                    print("\n有票啦有票啦\n车次余票信息：")
                    print(cars[-33] + ':' + cars[self.way])
                    train_infor = '车次：' + cars[-33] + '\n' + '余票：' + cars[self.way]
                    break
            time.sleep(3)
        return train_infor

# 发送邮件
class Email_train():
    def __init__(self, text):
        self.my_sender = '1248703394@qq.com'  # 发件人邮箱账号
        self.my_pass = '*****'  # 发件人邮箱密码(当时申请smtp给的口令)
        self.my_user = '********'  # 收件人邮箱账号，我这边发送给自己
        self.text = text + '\n有票啦有票啦！\n不客气！'

    def mail(self):
        ret = True
        try:
            msg = MIMEText(self.text, 'plain', 'utf-8')  # 对应的是邮件内容
            msg['From'] = formataddr(["来自我的QQ", self.my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(["我的outlook", self.my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "邮件主题-测试"  # 邮件的主题，也可以说是标题

            server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login(self.my_sender, self.my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.my_sender, [self.my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
            print('邮件发送成功！')
        except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            ret = False
            print(e)
        return ret


if __name__ == "__main__":
    from_city = '长沙'
    to_city = '徐州'
    date = '2017-10-18'
    way_of_train = '软卧'          
    train = 'Z168'
    q = Query(from_city, to_city, date, way_of_train, train)
    info = q.search()
    email = Email_train(info)
    email.mail()
