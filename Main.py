import requests
import re
import wx
from urllib.parse import quote

user = "2#-303" #填寝室账号
mode = False #True:每次都提醒 False：低于value提醒
value = 5.0 #提醒阈值，mode为1不运作

url = "http://jxgsxy.acrel-eem.com" #网址
password = "gs@1998_XY."  # 默认密码
session = requests.Session()
app = wx.App()
try:
    login = f"{url}/Ajax/UserLogin.ashx?username={quote(user)}&password={quote(password)}"
    response = session.get(login) #登陆
    if response.status_code == 200:
        if response.text == "成功":
            response = session.get(f"{url}/Ajax/CheckUserLogin.ashx?Id=2")

            #正则宿舍号
            shop_number = re.search(r'>商铺号(.*?)</p>', response.text).group(1).strip()

            #正则余额
            overage = float(re.search(r'>剩余金额：(.*?)</p>', response.text).group(1).strip())

            if mode:
                wx.MessageBox(f"{shop_number}剩余{overage}", "提示", wx.ICON_INFORMATION)
            elif overage <= value:
                wx.MessageBox(f"{shop_number}剩余{overage}请尽快充值", "警告", wx.ICON_ERROR)
        else:
            wx.MessageBox(response.text, "错误", wx.ICON_ERROR)
    else:
        wx.MessageBox(f"服务器连接失败:{response.status_code}", "错误", wx.ICON_ERROR)
except requests.RequestException as e:
    wx.MessageBox(f"网络请求错误: {e}", "错误", wx.ICON_ERROR)