import requests
import re
import wx
from urllib.parse import quote

class ErrorDialog(wx.Dialog):
    def __init__(self, error_message, parent, title):
        super().__init__(parent, title=title, size=(400, 300))
        self.error_message = error_message
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        self.text_ctrl.SetValue(self.error_message)
        self.text_ctrl.SetMinSize((600, 300))  # 设置一个更大的初始大小
        #self.text_ctrl.Hide()  # 默认折叠错误信息

        self.toggle_btn = wx.Button(panel, label="折叠错误详情")
        self.toggle_btn.Bind(wx.EVT_BUTTON, self.on_toggle)
        vbox.Add(self.toggle_btn, 0, wx.ALL | wx.CENTER, 5)

        self.retry_btn = wx.Button(panel, label="重试")
        self.retry_btn.Bind(wx.EVT_BUTTON, self.on_retry)
        vbox.Add(self.retry_btn, 0, wx.ALL | wx.CENTER, 5)

        self.close_btn = wx.Button(panel, label="关闭")
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        vbox.Add(self.close_btn, 0, wx.ALL | wx.CENTER, 5)

        vbox.Add(self.text_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(vbox)
        self.Centre()

    def on_toggle(self, event):
        if self.text_ctrl.IsShown():
            self.text_ctrl.Hide()
            self.toggle_btn.SetLabel("展开错误详情")
        else:
            self.text_ctrl.Show()
            self.toggle_btn.SetLabel("折叠错误详情")

    def on_retry(self, event):
        self.EndModal(wx.ID_OK)  # 用户选择重试，返回wx.ID_OK

    def on_close(self, event):
        self.EndModal(wx.ID_CANCEL)  # 用户选择关闭，返回wx.ID_CANCEL

def check_balance(user, mode, value, url, password, retry=False):
    session = requests.Session()
    try:
        login_url = f"{url}/Ajax/UserLogin.ashx?username={quote(user)}&password={quote(password)}"
        response = session.get(login_url)  # 登录
        if response.status_code == 200:
            if response.text == "成功":
                response = session.get(f"{url}/Ajax/CheckUserLogin.ashx?Id=2")

                # 正则宿舍号
                shop_number_match = re.search(r'>商铺号(.*?)</p>', response.text)
                if shop_number_match:
                    shop_number = shop_number_match.group(1).strip()
                else:
                    raise ValueError("无法匹配到商铺号")

                # 正则余额
                overage_match = re.search(r'>剩余金额：(.*?)</p>', response.text)
                if overage_match:
                    overage = float(overage_match.group(1).strip())
                else:
                    raise ValueError("无法匹配到剩余金额")

                if mode:
                    wx.MessageBox(f"{shop_number}剩余{overage}", "提示", wx.ICON_INFORMATION)
                elif overage <= value:
                    wx.MessageBox(f"{shop_number}剩余{overage}请尽快充值", "警告", wx.ICON_ERROR)
            else:
                wx.MessageBox(response.text, "错误", wx.ICON_ERROR)
        else:
            error_dialog = ErrorDialog(f"服务器连接失败:{response.status_code}", None, "错误信息")
            response = error_dialog.ShowModal()
            error_dialog.Destroy()
            if response == wx.ID_OK:
                if retry:
                    wx.MessageBox("已经达到最大重试次数，程序将退出。", "错误", wx.ICON_ERROR)
                else:
                    check_balance(user, mode, value, url, password, retry=True)  # 递归调用以再次尝试
    except Exception as e:
        error_dialog = ErrorDialog(f"{e}", None, "错误信息")
        response = error_dialog.ShowModal()
        error_dialog.Destroy()
        if response == wx.ID_OK:
            if retry:
                wx.MessageBox("已经达到最大重试次数，程序将退出。", "错误", wx.ICON_ERROR)
            else:
                check_balance(user, mode, value, url, password, retry=True)  # 递归调用以再次尝试

# 使用函数
user = "2#-303"  # 填寝室账号
mode = True  # True:每次都提醒 False：低于value提醒
value = 5.0  # 提醒阈值，mode为1不运作
url = "http://jxgsxy.acrel-eem.com"  # 网址
password = "gs@1998_XY."  # 默认密码

if __name__ == "__main__":
    app = wx.App()
    check_balance(user, mode, value, url, password)
    app.MainLoop()
