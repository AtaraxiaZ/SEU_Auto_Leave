# coding: utf-8
# Author：quzard
import datetime
import json
import re
from urllib import parse

import execjs
import requests

class Leave(object):
    def __init__(self, uname, pwd, path):

        self.uname = uname
        self.pwd = pwd
        self.path = path
        if self.uname[:3] == "213":
            self.undergraduate = True
            self.urlBegin = 'http://ehall.seu.edu.cn/xsfw/sys/xsqjapp/'
            self.cookie_url = 'http://ehall.seu.edu.cn/xsfw/sys/swpubapp/indexmenu/getAppConfig.do?appId=4810794463325921&appName=xsqjapp'

        else:
            self.undergraduate = False
            self.urlBegin = 'http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/'
            self.cookie_url = 'http://ehall.seu.edu.cn/ygfw/sys/swpubapp/indexmenu/getAppConfig.do?appId=5869188708264821&appName=xsqjappseuyangong&v=06154290794922301'


    # 登陆
    def login(self):
        login_url = self.urlBegin + '*default/index.do'
        get_login = self.sess.get(login_url)

        get_login.encoding = 'utf-8'
        lt = re.search('name="lt" value="(.*?)"', get_login.text).group(1)
        salt = re.search('id="pwdDefaultEncryptSalt" value="(.*?)"', get_login.text).group(1)
        execution = re.search('name="execution" value="(.*?)"', get_login.text).group(1)

        f = open(self.path + "/encrypt.js", 'r', encoding='UTF-8')
        line = f.readline()
        js = ''
        while line:
            js = js + line
            line = f.readline()
        ctx = execjs.compile(js)
        password = ctx.call('_ep', self.pwd, salt)

        login_post_url = 'https://newids.seu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.seu.edu.cn%2Fygfw%2Fsys%2Fxsqjappseuyangong%2F*default%2Findex.do'
        personal_info = {'username': self.uname,
                         'password': password,
                         'lt': lt,
                         'dllt': 'userNamePasswordLogin',
                         'execution': execution,
                         '_eventId': 'submit',
                         'rmShown': '1'}
        post_login = self.sess.post(login_post_url, personal_info)
        post_login.encoding = 'utf-8'
        if re.search("出校登记审批", post_login.text):
            return "登陆成功!"
        else:
            print(post_login.text)
            return "登陆失败!"


    # 设置self.header
    def getheader(self):
        get_cookie = self.sess.get(self.cookie_url)
        cookie = requests.utils.dict_from_cookiejar(self.sess.cookies)
        c = ""
        for key, value in cookie.items():
            c += key + "=" + value + "; "
        self.header = {'Referer': self.urlBegin + '*default/index.do',
                  'Cookie': c}
    # 获取之前信息
    def get_info(self):
        personal_info_url = self.urlBegin + 'modules/wdqj/wdqjbg.do'
        get_personal_info = self.sess.post(personal_info_url, data={'XSBH': str(self.uname), 'pageSize': '100', 'pageNumber': '1'},
                                      headers=self.header)
        return get_personal_info


    def get_info_2(self, SQBH):
        url = self.urlBegin + 'modules/wdqj/qjxqbd.do'
        self.header['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
        FormData = {'SQBH': SQBH}
        data = parse.urlencode(FormData)

        get_personal_info = self.sess.post(url, data=data,
                                  headers=self.header)
        get_personal_info = json.loads(get_personal_info.text)['datas']['qjxqbd']['rows']
        get_personal_info = get_personal_info[0]
        return get_personal_info


    # 获取未销假
    def getAllNoRemoveLeave(self):
        if self.undergraduate:
            url = self.urlBegin + 'modules/leaveApply/getNoRemoveLeave.do'
            self.header['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
            FormData = {"requestParamStr": {}}
            data = parse.urlencode(FormData)
        else:
            url = self.urlBegin + 'modules/leaveApply/getAllNoRemoveLeave.do'
            self.header['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
            FormData = {"requestParamStr": {'XSBH': str(self.uname)}}
            data = parse.urlencode(FormData)

        get_personal_info = self.sess.post(url, data=data, headers=self.header)
        if "data" in get_personal_info.text:
            datas = json.loads(get_personal_info.text)['data']
            return self.addXjApply(datas)
        return False


    # 销假
    def addXjApply(self, datas):
        if self.undergraduate:
            url = self.urlBegin + 'modules/xjset/xjshApply.do'
            self.header['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
            now_time = datetime.datetime.now()
            data = datas
            if now_time.strftime("%Y-%m-%d") not in data['QJKSRQ'] and (now_time + datetime.timedelta(days=+1)).strftime(
                    "%Y-%m-%d") not in data['QJKSRQ']:
                print("销假: ", data["QJKSRQ"])
                post_info = {"requestParamStr": {"SQBH": data["SQBH"]}}
                data = parse.urlencode(post_info)
                get_personal_info = self.sess.post(url, data=data, headers=self.header)
            else:
                if (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d") in data['QJKSRQ']:
                    return True
            return False
        else:
            url = self.urlBegin + 'modules/leaveApply/addXjApply.do'
            self.header['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
            for data in datas:
                now_time = datetime.datetime.now()
                if now_time.strftime("%Y-%m-%d") not in data['QJKSRQ'] and (now_time + datetime.timedelta(days=+1)).strftime(
                        "%Y-%m-%d") not in data['QJKSRQ']:
                    print("销假: ", data["QJKSRQ"])
                    post_info = {
                        "data": {"SQBH": "", "XSBH": 0, "SHZT": "20", "XJFS": "2",
                                "XJSJ": "", "XJRQ": "", "SQR": "", "SQRXM": "",
                                "THZT": "0"}}
                    post_info["data"]["SQBH"] = data["SQBH"]
                    post_info["data"]["XSBH"] = int(data["XSBH"])
                    post_info["data"]["XJSJ"] = now_time.strftime("%Y-%m-%d %H:%M:%S")
                    post_info["data"]["XJRQ"] = now_time.strftime("%Y-%m-%d")
                    post_info["data"]["SQR"] = data["XSBH"]
                    post_info["data"]["SQRXM"] = data["XM"]
                    data = parse.urlencode(post_info)
                    get_personal_info = self.sess.post(url, data=data, headers=self.header)
                else:
                    if (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d") in data['QJKSRQ']:
                        return True
            return False


    # 获取未审批
    def getAllApplyedLeave(self):
        url = self.urlBegin + 'modules/leaveApply/getAllApplyedLeave.do'
        self.header['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
        FormData = {"requestParamStr": {'XSBH': str(self.uname)}}
        data = parse.urlencode(FormData)

        get_personal_info = self.sess.post(url, data=data, headers=self.header)
        if "data" in get_personal_info.text:
            datas = json.loads(get_personal_info.text)['data']
            return self.backleaveApply(datas)
        return False


    # 撤回
    def backleaveApply(self, datas):
        url = self.urlBegin + 'modules/leaveApply/backleaveApply.do'
        self.header['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
        for data in datas:
            now_time = datetime.datetime.now()
            # 未审批的今天和明天的不撤回
            if now_time.strftime("%Y-%m-%d") not in data['QJKSRQ'] and (now_time + datetime.timedelta(days=+1)).strftime(
                    "%Y-%m-%d") not in data['QJKSRQ']:
                print("撤回: ", data["QJKSRQ"])
                post_info = {"requestParamStr": {"SQBH": data["SQBH"]}}
                data = parse.urlencode(post_info)
                get_personal_info = self.sess.post(url, data=data, headers=self.header)
            else:
                return True
        return False


    # 删除草稿
    def delleaveApply(self, datas):
        url = self.urlBegin + 'modules/leaveApply/delleaveApply.do'
        self.header['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
        for data in datas:
            if data["SHZT_DISPLAY"] == "草稿":
                if self.undergraduate == False:
                    print("状态: ",data["SHZT_DISPALY_DISPLAY"])
                print("删除草稿: ", data["QJKSRQ"])
                post_info = {"requestParamStr": {"SQBH": data["SQBH"]}}
                data = parse.urlencode(post_info)
                get_personal_info = self.sess.post(url, data=data, headers=self.header)


    def askForLeave(self):
        # 设置header
        self.getheader()

        # 获取未销假
        r = self.getAllNoRemoveLeave()
        if r:
            return "请假成功!  已经存在未销假的请假"

        # 获取未审批
        r = self.getAllApplyedLeave()
        if r:
            return "请假成功!  已经存在未审批的请假"
        # 删除草稿
        get_personal_info = self.get_info()
        raw_personal_info = json.loads(get_personal_info.text)['datas']['wdqjbg']['rows']
        self.delleaveApply(raw_personal_info)

        get_personal_info = self.get_info()
        if get_personal_info.status_code == 200:
            print('获取前一日信息成功!')
        else:
            print("获取信息失败!")
            return "获取信息失败!"

        raw_personal_info = json.loads(get_personal_info.text)['datas']['wdqjbg']['rows'][0]
        raw_personal_info = self.get_info_2(raw_personal_info["SQBH"])

        datas = {"QJLX_DISPLAY": "不涉及职能部门", "QJLX": "3bc0d68330fd4d869152238251b867ee", "DZQJSY_DISPLAY": "因事出校（当天往返）",
                 "DZQJSY": "763ec35f8f5545c0aa245e8fbc20adb2", "QJXZ_DISPLAY": "因公", "QJXZ": "2", "QJFS_DISPLAY": "请假",
                 "QJFS": "1", "YGLX_DISPLAY": "实验", "YGLX": "3", "SQSM": "", "QJKSRQ": "",
                 "QJJSRQ": "", "QJTS": "1", "QJSY": "去无线谷科研", "ZMCL": "", "SJH": "",
                 "DZSFLX_DISPLAY": "是", "DZSFLX": "1", "HDXQ_DISPLAY": "九龙湖校区", "HDXQ": "1", "DZSFLN_DISPLAY": "否",
                 "DZSFLN": "0", "DZSFLKJSS_DISPLAY": "", "DZSFLKJSS": "", "DZ_SFCGJ_DISPLAY": "", "DZ_SFCGJ": "",
                 "DZ_GJDQ_DISPLAY": "", "DZ_GJDQ": "", "QXSHEN_DISPLAY": "", "QXSHEN": "", "QXSHI_DISPLAY": "", "QXSHI": "",
                 "QXQ_DISPLAY": "", "QXQ": "", "QXJD": "", "XXDZ": "无线谷", "JTGJ_DISPLAY": "", "JTGJ": "", "CCHBH": "",
                 "SQBH": "", "XSBH": "", "JJLXR": "", "JJLXRDH": "",
                 "JZXM": "", "JZLXDH": "", "DSXM": "", "DSDH": "", "FDYXM": "",
                 "FDYDH": "", "SFDSQ": "0"}
        post_info = {}
        for key, value in datas.items():
            if key in raw_personal_info:
                if raw_personal_info[key] == 'null' or raw_personal_info[key] == None:
                    post_info[key] = ''
                else:
                    post_info[key] = raw_personal_info[key]
            else:
                post_info[key] = value
        if post_info['QJSY'] == '':
            post_info['QJSY'] = "去无线谷科研"
        if post_info['XXDZ'] == '':
            post_info['XXDZ'] = "去无线谷科研"
        post_info['SQBH'] = ''
        now_time = datetime.datetime.now()
        post_info["QJKSRQ"] = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d 06:00")
        post_info["QJJSRQ"] = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d 23:59")

        save_url = self.urlBegin + 'modules/leaveApply/addLeaveApply.do'
        self.header['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
        FormData = {'data': post_info}
        data = parse.urlencode(FormData)
        save = self.sess.post(save_url, data=data, headers=self.header)

        if "成功" in save.text:
            print('请假成功!')
            return '请假成功!'
        else:
            print("请假失败!")
            return "请假失败!"


    def do_report(self):
        self.sess = requests.session()

        if self.login() == "登陆失败!":
            return "登陆失败!"

        msg = self.askForLeave()
        self.sess.close()
        return msg
