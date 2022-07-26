import subprocess
from time import sleep
from clicknium import clicknium as cc, locator, ui
from clicknium.common.enums import ClearHotKey,PreAction,InputTextBy,MouseButton,MouseActionBy,Location
from clicknium.common.models.mouselocation import MouseLocation

configPath = r'C:\test\config.txt'  # 这里是txt文本配置文件的路径，修改为你自己的
f = open(configPath, "r")
username= f.readline().strip()  # txt文本第一行为用户名
password = f.readline().strip() # txt文本第二行为密码
exePath = f.readline().strip()  # txt文本第三行为千牛的exe文件路径
groupMessage = '你好！！！'

def main():
    list_name = get_name_list()  # 获取要添加的好友名列表
    start_process()  # 启动千牛进程
    login()  # 用户名密码登录
    sleep(5) # 等待5秒进程启动完毕
    ui(locator.aliworkbench.btnIM).click()  # 点击 '接待中心 '
    cc.wait_appear(locator.aliworkbench.im.imWindow)  # 等待 '接待中心' 界面出现
    add_group()  # 添加 '测试分组'
    add_friends(list_name)  # 循环添加好友
    send_message()  # 发送消息
    sleep(5)

def get_name_list():
    return ['sfsfsfs','abcdefg','ddddd','ggggg']  # 要添加的好友

def start_process():
    path = exePath
    subprocess.Popen(path) # 通过 subprocess 库来启动千牛进程
    sleep(3)
    print('start_process end.')

def login():
    # 首先清除掉已经有的账号
    ui(locator.aliworkbench.login.username).clear_text('send-hotkey',ClearHotKey.Home_ShiftEnd_Delete,PreAction.Click)
    # 填写用户名，这里无法使用UiElement对象的set_text 方法，它不是一个标准的edit输入框，我们可以使用全局的输入文本
    cc.send_text(username)
    # 发送enter快捷键，跳转到输入密码框
    cc.send_hotkey('{enter}')
    # 点击密码框
    ui(locator.aliworkbench.login.password).click()
    # 清空密码框
    ui(locator.aliworkbench.login.password).clear_text('send-hotkey',ClearHotKey.Home_ShiftEnd_Delete,PreAction.Click)
    # 输入密码
    cc.send_text(password)
    # 点击登录
    ui(locator.aliworkbench.login.btnLogin).click()
    print('login end.')

def add_friends(list_name):
    # 循环list_name 列表，循环添加好友
    for name in list_name:
        # 点击'搜索框'，并且清空文本，通过Home ShiftEnd Delete 组合快捷键来删除已有文本
        ui(locator.aliworkbench.im.txtSearch).clear_text('send-hotkey',ClearHotKey.Home_ShiftEnd_Delete,PreAction.Click)
        # '搜索框' 输入要添加的好友名称
        ui(locator.aliworkbench.im.txtSearch).set_text(name,InputTextBy.SendKeyAfterClick)
        # 点击'在网络中查找',这里该控件是没有控件树结构的，所以只能通过图像识别先识别位置，然后来点击它，由于各个电脑大小分辨率等不同，
        # 如果这个地方没有识别通过,你可以在你的电脑上重新使用录制器图像识别的方式抓取下该控件
        ui(locator.aliworkbench.im.btnSearchOnNetwork).click()
        # 睡眠1s,等待搜索结果出现
        sleep(1)
        # 这里需要点击第一条搜索结果，然后在聊天界面中点击添加好友按钮
        # 这里同样搜索结果是没有控件树结构的，并且每次内容都是不同的（也就不能使用图像识别方式来点击）
        # 所以我们通过定位'搜索框'+向下偏移40px坐标的方式 来点击第一条搜索结果
        ui(locator.aliworkbench.im.txtSearch).click(mouse_location=MouseLocation(Location.Center,yoffset=40))
        sleep(1)
        # 判断聊天界面中间顶部是否有'加为我的好友'按钮（如果没有，说明已经是好友则跳过）
        if not (cc.is_existing(locator.aliworkbench.im.btnAdd)):
            print(f'already a friend:{name}')
            continue
        # 还不是好友，则点击'加为我的好友'
        ui(locator.aliworkbench.im.btnAdd).click()
        # 添加好友有几种结果，一种是需要对方验证的，另一种是不需要验证，直接就能添加成功的
        # 判断是否弹出了添加好友验证的提示框
        if(cc.wait_appear(locator.aliworkbench.im.addWindow,wait_timeout=5)):
            print(f'need verify:{name}')
            # 需要验证信息，点击输入框，这里同样是通过图像识别方式
            ui(locator.aliworkbench.im.inputVerifyInfo).click()
            # 填写验证信息
            cc.send_text('你好，我是小千牛。')
            # 点击'确定'按钮
            ui(locator.aliworkbench.im.btnSendVerify).click()
        else:
            # 另一种不需要验证信息，直接添加好友成功，我们这里将添加的好友加入到我们创建的'测试分组'中。
            # 这里等待'添加好友成功'页面'完成'按钮出现
            cc.wait_appear(locator.aliworkbench.im.btnComplete)
            # 点击选择组，弹出下拉框
            ui(locator.aliworkbench.im.selectGroup).click()
            # 点击下拉框中的'测试分组'
            ui(locator.aliworkbench.im.friendGroup).click(MouseButton.Left,by=MouseActionBy.MouseEmulation)
            # 点击'完成'按钮
            ui(locator.aliworkbench.im.btnComplete).click()
            print(f'does not need verify:{name}')

    print('add_friend end.')

def add_group():
    # 点击我的好友
    ui(locator.aliworkbench.im.btnMyFriend).click()
    # 判断测试分组是否已经存在，如果不存在则添加，存在则跳过
    exist = cc.is_existing(locator.aliworkbench.im.testGroup)
    if(exist):
        print('group already exist.')
        return
    # 在 我的好友 中第一个分组 右键弹出菜单
    ui(locator.aliworkbench.im.itemFriendGroup).click(MouseButton.Right)
    # 点击弹出菜单->添加组
    ui(locator.aliworkbench.im.menuAddGroup).click()
    # 输入测试分组，参数我们选择SendKeyAfterClick，意思是先点击输入框获取焦点，然后输入'测试分组'文本
    ui(locator.aliworkbench.im.txtNewGroupName).set_text('测试分组',InputTextBy.SendKeyAfterClick)
    # 通过再次点击'我的好友' 使得当前输入框丢失焦点，创建'测试分组'生效
    ui(locator.aliworkbench.im.btnMyFriend).click()
    print('add_group end.')

def send_message():
    # 点击'我的好友'
    ui(locator.aliworkbench.im.btnMyFriend).click()
    # 图像识别到定位到'测试分组'，右键点击它,弹出菜单
    ui(locator.aliworkbench.im.testGroup).click(MouseButton.Right)
    # 点击弹出菜单-> 向组员群发消息
    ui(locator.aliworkbench.im.menuSendGroupMessage).click()
    # 等待'群发即时消息'窗口出现
    cc.wait_appear(locator.aliworkbench.im.sendGroupMsgWindow)
    # 输入待发送消息内容
    ui(locator.aliworkbench.im.inputGroupMessage).set_text(groupMessage,InputTextBy.SendKeyAfterClick)
    # 点击'发送'按钮，没有控件树结构，只能图像识别
    ui(locator.aliworkbench.im.btnSendGroupMsg).click()
    # 等待消息发送完成弹窗出现
    cc.wait_appear(locator.aliworkbench.im.sendSuccessWindow)
    # 关闭弹窗
    ui(locator.aliworkbench.im.btnSendOK).click()
    # 关闭 '群发即时消息'窗口
    ui(locator.aliworkbench.im.closeSendGroupMsgWindow).click()
    print('send_message end.')

if __name__ == "__main__":
    main()
