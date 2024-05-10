#!python3
# -*- coding:utf-8 -*-
# this script only works with Win32 notepad.exe
# if you notepad.exe is the Windows Store version in Windows 11, you need to uninstall it.
import subprocess
import uiautomation as auto
auto.uiautomation.SetGlobalSearchTimeout(15)  # 设置全局搜索超时 15


def main():
    subprocess.Popen('notepad.exe', shell=True)
    window = auto.WindowControl(searchDepth=1, ClassName='Notepad')
    # 或者使用Compare自定义搜索条件
    # window = auto.WindowControl(searchDepth=1, ClassName='Notepad', Compare=lambda control,depth:control.ProcessId==100)
    edit = window.EditControl()
    # 当第一次调用SendKeys时, uiautomation开始在15秒内搜索控件window和edit
    # 因为SendKeys内部会间接调用Control.Element并且Control.Element值是None
    # 如果在15秒内找不到window和edit，会抛出LookupError异常
    try:
        edit.SendKeys('first notepad')
    except LookupError as ex:
        print("The first notepad doesn't exist in 15 seconds")
        return
    # 第二次调用SendKeys不会触发搜索, 之前的调用保证Control.Element有效
    edit.SendKeys('{Ctrl}a{Del}')
    window.GetWindowPattern().Close()  # 关闭第一个Notepad, window和edit的Element虽然有值，但是无效了

    subprocess.Popen('notepad.exe')  # 运行第二个Notepad
    window.Refind()  # 必须重新搜索
    edit.Refind()  # 必须重新搜索
    edit.SendKeys('second notepad')
    edit.SendKeys('{Ctrl}a{Del}')
    window.GetWindowPattern().Close()  # 关闭第二个Notepad, window和edit的Element虽然有值，但是再次无效了

    subprocess.Popen('notepad.exe')  # 运行第三个Notepad
    if window.Exists(3, 1): # 触发重新搜索
        if edit.Exists(3):  # 触发重新搜索
            edit.SendKeys('third notepad')  # 之前的Exists保证edit.Element有效
            edit.SendKeys('{Ctrl}a{Del}')
        window.GetWindowPattern().Close()
    else:
        print("The third notepad doesn't exist in 3 seconds")


if __name__ == '__main__':
    main()
    