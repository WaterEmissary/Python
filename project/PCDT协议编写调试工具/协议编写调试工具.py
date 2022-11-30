import datetime
import os.path
import shutil
import tkinter as tk
import tkinter.ttk as ttk
import zipfile
from tkinter import filedialog
from tkinter import messagebox
import tkinter.font as tkFont
import socket
import threading
import time

import pymssql
import xlrd
import xlwt
import binascii
import chardet
from crcmod import mkCrcFun

"""更新日志
v1.0    发布
v1.1    添加FSU白盒化工具
v1.2    软件更名为 协议编写调试工具
        修改了部分运行逻辑
        优化了相关功能
        添加txt转datainfo代码功能
        添加一键生成固件升级包功能
            添加Fsu地址选择功能
        添加一键追加设备类型功能
        修改cfg为utf-8格式
"""

# 初始值
thinsert = []
insertinfoth = [] #添加info线程列表
trth = []   #翻译线程列表

# MODBUSTCP类
class ModbusTcp():
    # 创建TCP服务器函数
    def socket_TCPservice(self):
        ip = rootc.IpCombobox.get()
        port = int(rootc.IPPortCombobox.get())
        try:
            rootc.ShowRecvText.configure(state='normal')
            rootc.ShowRecvText.insert(tk.END,
                                      '[{0}] 正在创建服务 <{1}:{2}>...\n'.format(time.strftime('%Y-%m-%d %H:%M:%S'), ip,
                                                                                 port), 'grey')
            rootc.ShowRecvText.configure(state='disabled')
            # 创建服务器
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 防止socket server重启后端口被占用（socket.error: [Errno 98] Address already in use）
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 服务器地址及端口
            s.bind((ip, port))
            s.listen(0)
            public.tcpcconn, addr = s.accept()
            public.tth = threading.Thread(target=self.deal_data, args=(public.tcpcconn, addr))
            public.tth.daemon = True
            public.tth.start()
        except socket.error as msg:
            rootc.ShowRecvText.insert(tk.END, str(msg) + '\n')
            rootc.ShowRecvText.yview_moveto(1)
            print(msg)
        except:
            pass


    # 创建TCP服务器函数回调函数
    def socket_TCPserviceth(self):
        th = threading.Thread(target=self.socket_TCPservice, args=())
        th.daemon = True
        th.start()
        public.IfStartListen = True
        rootc.StartRecvButton.configure(text='关闭端口', command=self.close_TCPserviceth)
        rootc.ProtocolTypeCombobox.configure(state='disabled')
        rootc.IpCombobox.configure(state='disabled')
        rootc.IPPortCombobox.configure(state='disabled')

    # 关闭TCP服务器回调函数
    def close_TCPservice(self):
        public.IfStartListen = False
        public.IfGetInfo = False
        public.IfStartSmart = False
        self.smartsendinfostop()
        rootc.StartRecvButton.configure(text='请等待...', command=...)
        rootc.StartRecvButton.update()
        try:
            public.tcpcconn.close()
        except BaseException as msg:
            print(msg)
        public.tcpcconn = None
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END,
                                  '[{0}] 已断开连接...\n'.format(time.strftime('%Y-%m-%d %H:%M:%S')),
                                  'grey')
        rootc.ShowRecvText.configure(state='disabled')
        rootc.StartRecvButton.configure(text='打开端口', command=self.socket_TCPserviceth)
        rootc.ProtocolTypeCombobox.configure(state='readonly')
        rootc.IpCombobox.configure(state='state')
        rootc.IPPortCombobox.configure(state='state')

    def close_TCPserviceth(self):
        clth = threading.Thread(target=self.close_TCPservice, args=())
        clth.daemon = True
        clth.start()

    # 显示接收到的数据函数
    def deal_data(self,conn, addr):
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END, '[{2}] 已连接上设备 <{0}:{1}>\n'.format(addr[0], addr[1],
                                                                                  time.strftime('%Y-%m-%d %H:%M:%S')),
                                  'grey')
        rootc.ShowRecvText.configure(state='disabled')
        while public.IfStartListen:
            try:
                data = conn.recv(1024)
                public.IfGetInfo = False
                public.IfSendSmartInfo = False
                askcmd = public.Bytes2Str(data)
                public.recvinfo = askcmd[0]
                thinsert.append(threading.Thread(target=self.insertth, args=(askcmd, addr,)))
                thinsert[-1].daemon = True
                thinsert[-1].start()
                time.sleep(0.1)
            except ConnectionAbortedError as msg:
                print(msg)
            except ConnectionResetError:
                self.close_TCPserviceth()

    # 输出到屏幕线程
    def insertth(self,askcmd, addr):
        public.IfGetInfo = True
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END,
                                  '[{0}] # RECV HEX FROM<{1}:{2}>\n'.format(time.strftime('%Y-%m-%d %H:%M:%S'), addr[0],
                                                                            addr[1]), 'grey')
        rootc.ShowRecvText.insert(tk.END, askcmd[0] + '\n')
        rootc.ShowRecvText.yview_moveto(1)
        rootc.ShowRecvText.configure(state='disabled')

    # 发包函数
    def sendinfo(self):
        if public.tcpcconn == None:
            return
        info = rootc.SendText.get('0.0', 'end')
        b, strlist = public.Str2Bytes(info)
        public.tcpcconn.send(b)
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END, '[{0}] # SEND HEX:\n'.format(time.strftime('%Y-%m-%d %H:%M:%S')), 'grey')
        rootc.ShowRecvText.insert(tk.END, " ".join(strlist) + '\n', 'blue')
        rootc.ShowRecvText.yview_moveto(1)
        rootc.ShowRecvText.configure(state='disabled')

    def smartsendandshow(self,info):
        b, strlist = public.Str2Bytes(info)
        public.tcpcconn.send(b)
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END, '[{0}] # SEND HEX:\n'.format(time.strftime('%Y-%m-%d %H:%M:%S')), 'grey')
        rootc.ShowRecvText.insert(tk.END, " ".join(strlist) + '\n', 'blue')
        rootc.ShowRecvText.yview_moveto(1)
        rootc.ShowRecvText.configure(state='disabled')

    # 智能回包
    def smartsendinfo(self):
        if not public.tcpcconn:
            return
        public.IfStartSmart = True
        rootc.SmartSendButton.configure(text='停止', command=self.smartsendinfostop)
        rootc.SmartSendStateLabel.configure(text='状态：已开启', fg='green')
        sendth = threading.Thread(target=self.smartsendinfoth, args=())
        sendth.daemon = True
        sendth.start()

    # 智能回包线程（旧）
    # def smartsendinfoth(self):
    #     while public.IfStartSmart:
    #         if public.IfGetInfo and not public.IfSendSmartInfo:
    #             key = rootc.udpKeyEntry.get()
    #             if ("".join(key.split()) in "".join(public.recvinfo.split())):
    #                 self.sendinfo()
    #             public.IfSendSmartInfo = True
    #         else:
    #             time.sleep(0.1)

    # 智能回包线程
    def smartsendinfoth(self):
        while public.IfStartSmart:
            if public.IfGetInfo and not public.IfSendSmartInfo:
                for i in smartrole.RoleList:
                    if ("".join(i[0].split()).lower()  in "".join(public.recvinfo.split()).lower()):
                        self.smartsendandshow(public.recvinfo[:15]+i[1])
                    public.IfSendSmartInfo = True
            else:
                time.sleep(0.1)

    # 停止智能回包
    def smartsendinfostop(self):
        public.IfStartSmart = False
        rootc.SmartSendButton.configure(text='开启', command=self.smartsendinfo)
        rootc.SmartSendStateLabel.configure(text='状态：已关闭', fg='red')


# 串口调试类-针对FSU设备
class ComATcp():
    def __init__(self):
        self.ip = None
        self.port = 9000
        self.com = 0
        #[0]获取权限    [1]获取连接     [2]保持连接
        self.GetRootByte = ['03000000000000290000000000000000000000000000000d0000ffff000000000000000034550000fe',
                            '03000000000000280000000000000000000000000000002a0000ffff00000000000000003455000003000000000000280000000000000000000000000000002c0000ffff000000000000000034550000',
                            '0300000000000028000000000000000000000000000000090000ffff000000000000000034550000']
        #有效数据的标识
        self.DataId = '03 00 00 00 00 00 00 3'
        #无效数据标识尾
        self.UnuseDataID = ['01 86 A1 0A 01 2A 71','00 00']


    # 打开串口请求生成
    def comAksByte(self):
        comAstr = '0300000000000044'
        com = hex(public.ComList.index(rootc.IPPortCombobox.get()) + 1)
        if com <= hex(15):
            comAstr = comAstr + '0000000000000000'
        elif com > hex(15) and com <= hex(32):
            comAstr = comAstr + '0a012abb0a012a71'
        comAstr = comAstr + '00000000000000270000ffff0000000000000000345500000000000'
        comAstr = comAstr + com[2:]
        comAstr = comAstr + '00004b0000000008000000010000004e0000000000000300'
        return comAstr

    # 保持连接函数
    def keepcall(self):
        while public.IfStartListen:
            public.tcpcconn.send(public.Str2Bytes(self.GetRootByte[2])[0])
            time.sleep(3)
    def keepcallth(self):
        kth = threading.Thread(target=self.keepcall,args=())
        kth.daemon = True
        kth.start()

    # 创建Tcp连接
    def TcpClient(self):
        self.com = public.ComList.index(rootc.IPPortCombobox.get())+1
        self.ip = rootc.IpCombobox.get()
        ADDR = (self.ip,self.port)
        public.tcpcconn = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        try:
            public.tcpcconn.connect(ADDR)
        except ConnectionRefusedError:
            self.StopCom()
            rootc.ShowRecvText.configure(state='normal')
            rootc.ShowRecvText.insert(tk.END,
                                      '\n[{2}] 无法连接上服务 <{0}:{1}>\n'.format(self.ip, public.ComList[self.com - 1],
                                                                                time.strftime('%Y-%m-%d %H:%M:%S')),
                                      'grey')
            rootc.ShowRecvText.configure(state='disabled')
            return
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END, '\n[{2}] 已连接上设备 <{0}:{1}>\n'.format(self.ip,public.ComList[self.com-1],time.strftime('%Y-%m-%d %H:%M:%S')),'grey')
        rootc.ShowRecvText.configure(state='disabled')
        # 连接到指定串口并接收数据
        public.tcpcconn.send(public.Str2Bytes(self.GetRootByte[0])[0])
        public.tcpcconn.send(public.Str2Bytes(self.GetRootByte[1])[0])
        public.tcpcconn.send(public.Str2Bytes(self.comAksByte())[0])
        # 启动保持连接线程
        self.keepcallth()
        # 接收数据线程
        self.RecvDatath()

    # 接收数据线程
    def RecvData(self):
        while public.IfStartListen:
            try:
                Data = public.tcpcconn.recv(1024)
                Data = public.Bytes2Str(Data)
                self.insertText(Data[0])
            except ConnectionAbortedError as msg:
                print(msg)
            except ConnectionResetError:
                self.StopCom()

    def RecvDatath(self):
        rth = threading.Thread(target=self.RecvData,args=())
        rth.daemon = True
        rth.start()

    # 判断无关数据
    def checkIfuseful(self,Data):
        # print(Data)
        # print(len(Data))
        if len(Data) >= 2048:
            return True
        elif Data.find(self.DataId) != 0:
            return True
        elif Data.find('FE') == 120:
            return True
        # elif Data.rfind(self.UnuseDataID[0]) == len(Data)-20:
        #     return True
        # elif Data.rfind(self.UnuseDataID[1]) == len(Data)-5:
        #     return True
        else:
            return False
    # 排除数据标识
    def delDataId(self,Data):
        # return Data.replace(self.DataId,'')
        return Data[120:]
        # return Data
    # 插入数据函数
    def insertText(self,Data):
        # 不显示无关数据
        if self.checkIfuseful(Data):
            return
        public.IfGetInfo = True
        public.IfSendSmartInfo = False
        Data = self.delDataId(Data)
        public.recvinfo = Data
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END,'[{0}] # RECV HEX FROM<{1}:{2}>\n'.format(time.strftime('%Y-%m-%d %H:%M:%S'), self.ip,public.ComList[self.com-1]), 'grey')
        rootc.ShowRecvText.insert(tk.END,Data+'\n')
        rootc.ShowRecvText.yview_moveto(1)
        rootc.ShowRecvText.configure(state='disabled')

    # 添加发包数据标识函数
    def addDataId(self,Data):
        Data = "".join(Data)
        idlen = 80
        alllen = len(Data)+idlen
        sendData = '03000000000000'+hex(alllen//2)[2:]+'000000000000000000000000000000250000ffff0000000'+hex(self.com)[2:]+'0000000034550000'+Data
        return sendData

    # 发送文本框中的数据函数
    def senddata(self):
        data = rootc.SendText.get('0.0',tk.END)
        b, strlist = public.Str2Bytes(data)
        public.tcpcconn.send(b)

    # 发送文本框中的数据函数并显示
    def sendinfo(self):
        if public.tcpcconn == None:
            return
        info = rootc.SendText.get('0.0',tk.END)
        sendinfo = self.addDataId(info.replace(' ',''))
        # print(sendinfo)
        b, strlist = public.Str2Bytes(sendinfo)
        public.tcpcconn.send(b)
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END, '[{0}] # SEND HEX:\n'.format(time.strftime('%Y-%m-%d %H:%M:%S')), 'grey')
        rootc.ShowRecvText.insert(tk.END, info + '\n', 'blue')
        rootc.ShowRecvText.yview_moveto(1)
        rootc.ShowRecvText.configure(state='disabled')

    # 智能发送并显示
    def smartsend(self,info):
        sendinfo = self.addDataId(info.replace(' ',''))
        # print(sendinfo)
        b, strlist = public.Str2Bytes(sendinfo)
        public.tcpcconn.send(b)
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END, '[{0}] # SEND HEX:\n'.format(time.strftime('%Y-%m-%d %H:%M:%S')), 'grey')
        rootc.ShowRecvText.insert(tk.END, info + '\n', 'blue')
        rootc.ShowRecvText.yview_moveto(1)
        rootc.ShowRecvText.configure(state='disabled')

    # 开始串口调试回调函数
    def StartCom(self):
        public.IfStartListen = True
        rootc.StartRecvButton.configure(text='关闭端口',command=self.StopCom)
        rootc.ProtocolTypeCombobox.configure(state='disabled')
        rootc.IpCombobox.configure(state='disabled')
        rootc.IPPortCombobox.configure(state='disabled')
        self.TcpClient()

    # 关闭串口调试回调函数
    def StopCom(self):
        public.IfStartListen = False
        self.smartsendinfostop()
        rootc.StartRecvButton.configure(text='打开端口',command=self.StartCom)
        rootc.ProtocolTypeCombobox.configure(state='readonly')
        rootc.IpCombobox.configure(state='state')
        rootc.IPPortCombobox.configure(state='state')
        public.tcpcconn.close()
        public.tcpcconn = None

    # 智能回包
    def smartsendinfo(self):
        if not public.tcpcconn:
            return
        public.IfStartSmart = True
        rootc.SmartSendButton.configure(text='停止', command=self.smartsendinfostop)
        rootc.SmartSendStateLabel.configure(text='状态：已开启', fg='green')
        sendth = threading.Thread(target=self.smartsendinfoth, args=())
        sendth.daemon = True
        sendth.start()

    # 智能回包线程（旧）
    # def smartsendinfoth(self):
    #     while public.IfStartSmart:
    #         if public.IfGetInfo and not public.IfSendSmartInfo:
    #             key = rootc.udpKeyEntry.get()
    #             if ("".join(key.split()) in "".join(public.recvinfo.split())):
    #                 self.sendinfo()
    #             public.IfSendSmartInfo = True
    #         else:
    #             time.sleep(0.1)
    # 智能回包线程
    def smartsendinfoth(self):
        while public.IfStartSmart:
            if public.IfGetInfo and not public.IfSendSmartInfo:
                for i in smartrole.RoleList:
                    if ("".join(i[0].split()).lower() in "".join(public.recvinfo.split()).lower()):
                        self.smartsend(i[1])
                    public.IfSendSmartInfo = True
            else:
                time.sleep(0.1)

    # 停止智能回包
    def smartsendinfostop(self):
        public.IfStartSmart = False
        rootc.SmartSendButton.configure(text='开启', command=self.smartsendinfo)
        rootc.SmartSendStateLabel.configure(text='状态：已关闭', fg='red')


# UDP-打印log类
class Udplog():
    def __init__(self):
        self.ip = None
        self.port = None
        self.key = None

    # 保持在最新
    def movetonew(self):
        while public.IfStartListen:
            rootc.ShowRecvText.yview_moveto(1)
            time.sleep(0.05)

    # 向文本框写数据
    def inserttext(self,insertstr):
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END, insertstr)
        rootc.ShowRecvText.configure(state='disabled')

    # 监听函数
    def receivedatainfo(self,recv_data, key):
        try:
            charset = chardet.detect(recv_data)['encoding']
            if charset not in ['ascii', 'GB2312']:
                charset = 'GB2312'
            result_recv_data = recv_data.decode(charset)
            if key == '':
                insertinfoth.append(threading.Thread(target=self.inserttext, args=(result_recv_data,)))
                insertinfoth[-1].daemon = True
                insertinfoth[-1].start()
                # rootc.ShowRecvText.insert(END,result_recv_data)
            else:
                if key in result_recv_data:
                    insertinfoth.append(threading.Thread(target=self.inserttext, args=(result_recv_data,)))
                    insertinfoth[-1].daemon = True
                    insertinfoth[-1].start()
                    # rootc.ShowRecvText.insert(END,result_recv_data)
        except:
            insertinfoth.append(threading.Thread(target=self.inserttext, args=(str(recv_data),)))
            insertinfoth[-1].daemon = True
            insertinfoth[-1].start()
            # rootc.ShowRecvText.insert(END,str(recv_data[0]))

    # 打开端口监听回调函数
    def startIP(self):
        global th
        public.IfStartListen = True
        rootc.StartRecvButton.configure(text='关闭端口', command=self.stopIP)
        rootc.ProtocolTypeCombobox.configure(state='disabled')
        rootc.IpCombobox.configure(state='disabled')
        rootc.IPPortCombobox.configure(state='disabled')
        rootc.StartRecvButton.update()
        ip = rootc.IpCombobox.get()
        port = int(rootc.IPPortCombobox.get())
        key = rootc.udpKeyEntry.get()
        th1 = threading.Thread(target=self.th_infoprint, args=(ip, port, key,))
        th1.daemon = True
        th1.start()
        th2 = threading.Thread(target=self.movetonew, args=())
        th2.daemon = True
        th2.start()

    # 关闭端口监听回调库函数
    def stopIP(self):
        public.IfStartListen = False
        rootc.StartRecvButton.configure(text='打开端口', command=self.startIP)
        rootc.ProtocolTypeCombobox.configure(state='readonly')
        rootc.IpCombobox.configure(state='state')
        rootc.IPPortCombobox.configure(state='state')
        rootc.StartRecvButton.update()

    # 输出日志线程
    def th_infoprint(self,ip, port, key):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_addr = (ip, port)
        udp_socket.bind(local_addr)
        while public.IfStartListen:
            recv_data = udp_socket.recvfrom(1024)
            # rootc.ShowRecvText.configure(state='normal')
            insertinfoth.append(threading.Thread(target=self.receivedatainfo, args=(recv_data[0], key,)))
            insertinfoth[-1].daemon = True
            insertinfoth[-1].start()
            # rootc.ShowRecvText.configure(state='disabled')
        udp_socket.close()


# TCP客户端
class TcpCliect():
    def __init__(self):
        self.ip = None
        self.port = None

    # 创建Tcp连接
    def TcpClient(self):
        self.ip = rootc.IpCombobox.get()
        self.port = int(rootc.IPPortCombobox.get())
        ADDR = (self.ip,self.port)
        public.tcpcconn = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        try:
            public.tcpcconn.connect(ADDR)
        except ConnectionRefusedError:
            self.StopTcp()
            rootc.ShowRecvText.configure(state='normal')
            rootc.ShowRecvText.insert(tk.END, '\n[{2}] 无法创建服务 <{0}:{1}>\n'.format(self.ip, self.port,
                                                                                        time.strftime(
                                                                                            '%Y-%m-%d %H:%M:%S')),
                                      'grey')
            rootc.ShowRecvText.configure(state='disabled')
            return
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END, '\n[{2}] 已连接上设备 <{0}:{1}>\n'.format(self.ip,self.port,time.strftime('%Y-%m-%d %H:%M:%S')),'grey')
        rootc.ShowRecvText.configure(state='disabled')
        # 接收数据线程
        self.RecvDatath()

    # 接收数据线程
    def RecvData(self):
        while public.IfStartListen:
            try:
                Data = public.tcpcconn.recv(1024)
                Data = public.Bytes2Str(Data)
                self.insertText(Data[0])
            except ConnectionAbortedError as msg:
                print(msg)
            except ConnectionResetError:
                self.StopTcp()
    def RecvDatath(self):
        rth = threading.Thread(target=self.RecvData,args=())
        rth.daemon = True
        rth.start()

    # 插入数据函数
    def insertText(self,Data):
        public.IfGetInfo = True
        public.IfSendSmartInfo = False
        public.recvinfo = Data
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END,'[{0}] # RECV HEX FROM<{1}:{2}>\n'.format(time.strftime('%Y-%m-%d %H:%M:%S'), self.ip,self.port), 'grey')
        rootc.ShowRecvText.insert(tk.END,Data+'\n')
        rootc.ShowRecvText.yview_moveto(1)
        rootc.ShowRecvText.configure(state='disabled')

    # 发送文本框中的数据函数
    def senddata(self):
        data = rootc.SendText.get('0.0',tk.END)
        b, strlist = public.Str2Bytes(data)
        public.tcpcconn.send(b)

    # 发送文本框中的数据函数并显示
    def sendinfo(self):
        if public.tcpcconn == None:
            return
        info = rootc.SendText.get('0.0',tk.END)
        # print(info)
        b, strlist = public.Str2Bytes(info)
        public.tcpcconn.send(b)
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.insert(tk.END, '[{0}] # SEND HEX:\n'.format(time.strftime('%Y-%m-%d %H:%M:%S')), 'grey')
        rootc.ShowRecvText.insert(tk.END, info + '\n', 'blue')
        rootc.ShowRecvText.yview_moveto(1)
        rootc.ShowRecvText.configure(state='disabled')

    # 开启端口
    def StartTcp(self):
        public.IfStartListen = True
        rootc.StartRecvButton.configure(text='关闭端口',command=self.StopTcp)
        rootc.ProtocolTypeCombobox.configure(state='disabled')
        rootc.IpCombobox.configure(state='disabled')
        rootc.IPPortCombobox.configure(state='disabled')
        self.TcpClient()

    # 关闭端口
    def StopTcp(self):
        public.IfStartListen = False
        rootc.StartRecvButton.configure(text='打开端口',command=self.StartTcp)
        rootc.ProtocolTypeCombobox.configure(state='readonly')
        rootc.IpCombobox.configure(state='state')
        rootc.IPPortCombobox.configure(state='state')
        public.tcpcconn.close()
        public.tcpcconn = None


# txt转xlx及cfg类
class Txt2Xlx2Cfg():
    def __init__(self):
        self.txtFilepath = ''
        self.xlsFilepath = ''
        self.SmTypeCode = 0
        self.DevName = 'None'
        self.DevProductor = 'None'
        self.Yidong = False
        self.TieTa = False
        self.ifcheckinfo = False
        self.txcroot = None

    # 创建窗口
    def txt2xlx2cfgroot(self):
        try:
            if self.txcroot.state() == 'normal':
                self.txcroot.attributes('-topmost',True)
                self.txcroot.attributes('-topmost',False)
                return
        except:
            self.txcroot = tk.Toplevel(rootc.root)
            self.txcroot.title('txt转换xls及cfg')

        # 左侧窗体
        self.LeftFrame = tk.Frame(self.txcroot, width=int(self.txcroot.winfo_width() * 0.4),
                                  height=int(self.txcroot.winfo_height()), bd=10,
                                  highlightbackground='white', highlightthickness=2)
        self.DevNoLabel = tk.Label(self.LeftFrame, text='设备编号(范围:1-9999)', font=tkFont.Font(size=12))
        self.DevNoEntry = tk.Entry(self.LeftFrame, width=30)
        self.DevNameLabel = tk.Label(self.LeftFrame, text='设备名称(Name)', font=tkFont.Font(size=12))
        self.DevNameEntry = tk.Entry(self.LeftFrame, width=30)
        self.DevFactoryLabel = tk.Label(self.LeftFrame, text='设备厂家(Productor)', font=tkFont.Font(size=12))
        self.DevFactoryEntry = tk.Entry(self.LeftFrame, width=30)
        self.ProtocolVar = tk.IntVar()
        self.ProtocolVar.set(0)
        self.DevProtocolYDRadio = tk.Radiobutton(self.LeftFrame, text='移动', font=tkFont.Font(size=12),
                                                 variable=self.ProtocolVar,
                                                 value=0)
        self.DevProtocolTTRadio = tk.Radiobutton(self.LeftFrame, text='铁塔', font=tkFont.Font(size=12),
                                                 variable=self.ProtocolVar,
                                                 value=1)
        self.DevinfoButton = tk.Button(self.LeftFrame, text='确认信息', command=self.devinfocheck)
        # 右侧总窗体
        self.RightallFrame = tk.Frame(self.txcroot, width=int(self.txcroot.winfo_width() * 0.6),
                                      height=int(self.txcroot.winfo_height()), bd=10,
                                      highlightbackground='white', highlightthickness=2)
        # 右上窗体
        self.RightupFrame = tk.Frame(self.RightallFrame)
        self.temp = "设备编号:" + str(
            self.SmTypeCode) + "\t设备名称:" + self.DevName + "\t设备厂家:" + self.DevProductor + "\t" + (
                        "移动" if self.Yidong else "铁塔" if self.TieTa else "None")
        self.RuDecinfoLabel = tk.Label(self.RightupFrame, text=self.temp)
        # 右下侧窗体
        self.RightFrame = tk.Frame(self.RightallFrame)
        self.txt2xlstitleLabel = tk.Label(self.RightFrame, text='txt文档转xls', font=tkFont.Font(size=12))
        self.txt2xlswarnLabel = tk.Label(self.RightFrame,text='注:此步后需要手动更改遥控和遥调的Attrib,并添加Unit,NodeDesc',fg='red')
        self.OpentxtButton = tk.Button(self.RightFrame, text='打开txt', command=self.opentxt,state='disabled')
        self.txtpathEntry = tk.Entry(self.RightFrame, state='disabled', width=55)
        self.txt2xlsButton = tk.Button(self.RightFrame, text='开始转换', command=self.createexcel,state='disabled')
        self.xls2cfgLabel = tk.Label(self.RightFrame, text='xls表格转cfg\n', font=tkFont.Font(size=12))
        self.OpenxlsButton = tk.Button(self.RightFrame, text='打开xls', command=self.openxls,state='disabled')
        self.xlspathEntry = tk.Entry(self.RightFrame, state='disabled', width=55)
        self.xls2cfgButton = tk.Button(self.RightFrame, text='开始转换', command=self.xls2cfg,state='disabled')
        self.LeftFrame.grid(row=0, column=0)
        self.DevNoLabel.grid(row=1, column=1)
        self.DevNoEntry.grid(row=2, column=1)
        self.DevNameLabel.grid(row=3, column=1)
        self.DevNameEntry.grid(row=4, column=1)
        self.DevFactoryLabel.grid(row=5, column=1)
        self.DevFactoryEntry.grid(row=6, column=1)
        self.DevProtocolYDRadio.grid(row=7, column=1)
        self.DevProtocolTTRadio.grid(row=8, column=1)
        self.DevinfoButton.grid(row=9, column=1)
        self.RightallFrame.grid(row=0, column=1)
        self.RightupFrame.grid(row=0, column=1)
        self.RuDecinfoLabel.pack()
        self.RightFrame.grid(row=1, column=1)
        self.txt2xlstitleLabel.grid(row=0, column=0)
        self.txt2xlswarnLabel.grid(row=0,column=1,sticky=tk.S)
        self.OpentxtButton.grid(row=1, column=0)
        self.txtpathEntry.grid(row=1, column=1)
        self.txt2xlsButton.grid(row=2, column=1)
        self.xls2cfgLabel.grid(row=3, column=0)
        self.OpenxlsButton.grid(row=4, column=0)
        self.xlspathEntry.grid(row=4, column=1)
        self.xls2cfgButton.grid(row=5, column=1)

    # 更新设备信息
    def updatedecinfo(self):
        temp = "设备编号:" + str(self.SmTypeCode) + "\t设备名称:" + self.DevName + "\t设备厂家:" + self.DevProductor + "\t" + (
            "移动" if self.Yidong else "铁塔" if self.TieTa else "None")
        self.RuDecinfoLabel.configure(text=temp)

    # 确认设备信息
    def devinfocheck(self):
        try:
            self.SmTypeCode = int(self.DevNoEntry.get())
            self.DevName = self.DevNameEntry.get()
            self.DevProductor = self.DevFactoryEntry.get()
            if self.ProtocolVar.get() == 0:
                self.Yidong = True
                self.TieTa = False
            elif self.ProtocolVar.get() == 1:
                self.Yidong = False
                self.TieTa = True
            self.updatedecinfo()
            self.OpentxtButton.configure(state='normal')
            self.OpenxlsButton.configure(state='normal')
        except:
            pass
        finally:
            self.txcroot.attributes("-topmost", 0)
            if self.SmTypeCode != 0 and self.DevName != None and self.DevProductor != None:
                self.ifcheckinfo = True
            else:
                tk.messagebox.showinfo(title="设备信息错误！",
                                       message="请确认：\n1.设备编号在1-9999之间\n2.输入正确的设备名称和厂家")
            self.txcroot.attributes("-topmost", 1)

    # 打开txt文档
    def opentxt(self):
        self.txcroot.attributes("-topmost", 0)
        self.txtFilepath = filedialog.askopenfilename(filetypes=[('txt File','txt')])  # 获取文件地址
        self.txtpathEntry.configure(state='normal')
        temp = tk.StringVar()
        temp.set(self.txtFilepath)
        self.txtpathEntry.configure(textvariable=temp)
        self.txtpathEntry.configure(state='disabled')
        while self.txtFilepath[-4:] != '.txt' and self.txtFilepath[-4:] != '.TXT':
            if self.txtFilepath == '':  # 如果点击了取消，或者打开了名字为空的文件
                self.txcroot.attributes("-topmost", 1)
                self.txcroot.attributes("-topmost", 0)
                return
            tk.messagebox.showinfo(title="文件格式异常!", message="请打开格式类似TXT_SQL中的“.txt”文本文件！")
            self.txtFilepath = ''
            root = tk.Tk()
            root.withdraw()
            self.Filepath = filedialog.askopenfilename()  # 获得选择好的文件
            self.txtpathEntry.configure(state='normal')
            temp = tk.StringVar()
            temp.set(self.Filepath)
            self.txtpathEntry.configure(textvariable=temp)
            self.txtpathEntry.configure(state='disabled')
        self.txt2xlsButton.configure(state='normal')
        self.txcroot.attributes("-topmost", 1)
        self.txcroot.attributes("-topmost", 0)

    # 打开xls表格
    def openxls(self):
        self.txcroot.attributes("-topmost", 0)
        self.xlsFilepath = filedialog.askopenfilename(filetypes=[('xls File','xls')])  # 获取文件地址
        self.xlspathEntry.configure(state='normal')
        temp = tk.StringVar()
        temp.set(self.xlsFilepath)
        self.xlspathEntry.configure(textvariable=temp)
        self.xlspathEntry.configure(state='disabled')
        while self.xlsFilepath[-4:] != '.xls' and self.xlsFilepath[-4:] != '.XLS':
            if self.xlsFilepath == '':  # 如果点击了取消，或者打开了名字为空的文件
                self.txcroot.attributes("-topmost", 1)
                self.txcroot.attributes("-topmost", 0)
                return
            tk.messagebox.showinfo(title="文件格式异常!", message="请打开确认修改后的“.xls”表格文件！")
            self.xlsFilepath = ''
            root = tk.Tk()
            root.withdraw()
            self.Filepath = filedialog.askopenfilename()  # 获得选择好的文件
            self.xlspathEntry.configure(state='normal')
            temp = tk.StringVar()
            temp.set(self.Filepath)
            self.xlspathEntry.configure(textvariable=temp)
            self.xlspathEntry.configure(state='disabled')
        self.xls2cfgButton.configure(state='normal')
        self.txcroot.attributes("-topmost", 1)
        self.txcroot.attributes("-topmost", 0)

    # 从txt里读取数据
    def readtxt(self):
        filestr = []
        ovsrstr = []

        # 打开成功，开始读取文件
        with open(self.txtFilepath, 'r') as fp:
            while True:
                line = fp.readline()
                if not line:
                    break
                filestr.append(line.split())

        # 过滤，取出有用点位
        for i in filestr:
            if len(i) == 5:
                if i[2].isdigit() and i[2] != '0':
                    ovsrstr.append(i)

        # 返回处理完的列表
        return ovsrstr

    # 创建xls表格部分
    def createexcel(self):
        if (not self.ifcheckinfo) or self.txtFilepath == '':
            self.txcroot.attributes("-topmost",False)
            tk.messagebox.showinfo(title="警告!", message="请确认设备信息并打开一个.txt文档！")
            self.txcroot.attributes("-topmost", True)
            return
        textstr = self.readtxt()
        # 999监控设备通信状态
        if self.Yidong:  # 是移动移动的写在最后，GroupID为最后一个点
            textstr.append([str(textstr[-1][0]), str(textstr[-1][0]), '999', '监控设备通信状态', '1'])
        else:  # 是铁塔-铁塔的一般写在中间
            insertpos = 0
            if textstr[-1][0] == '2':  # 有parainfo的情况,写中间，GroupID为1
                for i in range(len(textstr)):
                    if textstr[i][0] == '2':
                        insertpos = i + 1
                        break
                textstr.insert(insertpos, ['1', '1', '999', '监控设备通信状态', '1'])
            else:  # 无parainfo的情况，写最后
                textstr.append(['1', '1', '999', '监控设备通信状态', '1'])
        # 创建表格
        wb = xlwt.Workbook(encoding='gbk')
        ws1 = wb.add_sheet("设备描述", cell_overwrite_ok=True)
        ws2 = wb.add_sheet("节点描述", cell_overwrite_ok=True)
        font = xlwt.Font()
        font.name = '宋体'
        font.height = 20 * 11
        sfont = xlwt.XFStyle()
        sfont.font = font

        # 表格固定内容初始化
        ws1deslist = ["SmTypeCode", "Name", "Address", "CommFormat", "PollingTime", "Timeout", "GroupCount", "ExParam",
                      "ProtocolFile",
                      "NodeDesc", "Productor", "Version", "DeviceModel", "ExParamDesc", "GetinTime", "Remark"]
        ws1chdeslist = ['；设备类型编号', '设备名', '地址', "", '轮询时间', '超时时间', '轮巡组数', '扩展参数',
                        '解析文件名',
                        '设备描述',
                        '生产厂家', '版本描述', '设备型号', '扩展参数描述', '接入时间', '备注']
        ws2deslist = ['GroupID', 'NodeNo', 'Command', 'SubCommand', 'NodeID', 'NodeName', 'ModeNo', 'Attrib',
                      'NodeLength',
                      'Offset', 'Precision', 'Unit', 'NodeDesc']
        for ws1column in range(len(ws1deslist)):
            ws1.write(0, ws1column, ws1deslist[ws1column], sfont)

        for ws1column in range(len(ws1chdeslist)):
            ws1.write(16, ws1column, ws1chdeslist[ws1column], sfont)

        for ws2column in range(len(ws2deslist)):
            ws2.write(0, ws2column, ws2deslist[ws2column], sfont)

        # 设备描述表生成
        ws1inputlist = []
        ws1inputlist.append(self.SmTypeCode)
        ws1inputlist.append(self.DevName)
        ws1inputlist.append(1)
        ws1inputlist.append('9600_N_8_2')
        ws1inputlist.append(1000)
        ws1inputlist.append(7500)
        ws1inputlist.append(1 if textstr[-1][0] == '1' else 2)  # 判断有几个info
        ws1inputlist.append('')  # 空
        ws1inputlist.append(str(self.SmTypeCode) + '_TT.cfg')
        ws1inputlist.append('')
        ws1inputlist.append(self.DevProductor)
        ws1inputlist.append('V1.0')
        ws1inputlist.append('H')
        ws1inputlist.append('')
        ws1inputlist.append(time.strftime("%Y/%m/%d"))
        ws1inputlist.append('')
        for ws1column in range(len(ws1inputlist)):
            ws1.write(1, ws1column, ws1inputlist[ws1column], sfont)

        ws1.col(0).width = 256 * 16
        ws1.col(1).width = 256 * 30
        ws1.col(3).width = 256 * 20
        ws1.col(8).width = 256 * 14
        ws1.col(10).width = 256 * 12
        ws1.col(14).width = 256 * 12

        # 节点描述生成
        for i in range(len(textstr)):
            ws2.write(i + 1, 0, int(textstr[i][0]), sfont)  # GroupID
            ws2.write(i + 1, 1, int(textstr[i][2]), sfont)  # NodeNo
            ws2.write(i + 1, 4, int(textstr[i][2]), sfont)  # NodeID
            ws2.write(i + 1, 5, textstr[i][3], sfont)  # NodeName
            ws2.write(i + 1, 6,
                      int(''.join(list(filter(str.isdigit, textstr[i][3])))) if textstr[i][3][-1].isdigit() else 0,
                      sfont)  # ModNo
            ws2.write(i + 1, 7, 33 if textstr[i][4] == '1' else 17, sfont)  # Attrib(需手动修改可写点的值)
            ws2.write(i + 1, 8, int(textstr[i][4]), sfont)  # NodeLength
            ws2.write(i + 1, 9, 1, sfont)  # Offset
            ws2.write(i + 1, 10, 0 if textstr[i][4] == '1' else 2, sfont)  # Precision
            ws2.write(i + 1, 11, '', sfont)  # Unit
            if textstr[i][2] == '999':
                ws2.write(i + 1, 12, '0 正常\\1 中断\\', sfont)

        ws2.write(1, 2, int(208), sfont)
        ws2.write(1, 3, int(65), sfont)
        ws2.col(5).width = 256 * 22
        # 生成表格文件
        try:
            self.txcroot.attributes("-topmost", False)
            self.saveXlspath = filedialog.asksaveasfilename(initialdir='', title='保存xls',
                                                             filetypes=[("Xls File", 'xls')],
                                                             initialfile=self.DevName + '.xls')  # 获取文件地址
            if self.saveXlspath == '':
                return
            wb.save(self.saveXlspath)
            self.txcroot.attributes("-topmost", False)
            tlen = len(textstr)
            t = "共 "+str(tlen)+ " 个点"
            tk.messagebox.showinfo(title="成功！",
                                   message=t+"转换成功！\n请手动修改“Attrib”中可写点的值后再转换成cfg文件！")
        except PermissionError:
            self.txcroot.attributes("-topmost", False)
            tk.messagebox.showinfo(title="错误！",
                                   message="生成文件失败！\n请检查文件是否被占用！")
        except:
            self.txcroot.attributes("-topmost", False)
            tk.messagebox.showinfo(title="错误！",
                                   message="请检查设备信息和txt文档是否正确！")
        finally:
            self.txcroot.attributes("-topmost", True)


    # xls表格转cfg
    def xls2cfg(self):
        if (not self.ifcheckinfo) or self.xlsFilepath == '':
            self.txcroot.attributes("-topmost",False)
            tk.messagebox.showinfo(title="警告!", message="请确认设备信息并打开一个.xls表格！")
            self.txcroot.attributes("-topmost",True)
            return
        excel = xlrd.open_workbook_xls(self.xlsFilepath)
        try:
            table = excel.sheet_by_name('节点描述')
        except:
            table = excel.sheet_by_index(-1)
        tableinfo = []
        tableinfo1 = [[],[],[]]
        tableinfo2 = [[],[],[]]
        tableinfo.append(table.col_values(0))
        tableinfo.append(table.col_values(4))
        tableinfo.append(table.col_values(7))
        tableinfo.append(table.col_values(8))
        tableinfo[0].pop(0)
        tableinfo[1].pop(0)
        tableinfo[2].pop(0)
        tableinfo[3].pop(0)
        for i in range(len(tableinfo[0])):
            if int(tableinfo[0][i]) == 1:
                tableinfo1[0].append(tableinfo[1][i])
                tableinfo1[1].append(tableinfo[2][i])
                tableinfo1[2].append(tableinfo[3][i])
            elif int(tableinfo[0][i]) == 2:
                tableinfo2[0].append(tableinfo[1][i])
                tableinfo2[1].append(tableinfo[2][i])
                tableinfo2[2].append(tableinfo[3][i])
        tableinfo1[0] = list(map(int, tableinfo1[0]))
        tableinfo1[1] = list(map(int, tableinfo1[1]))
        tableinfo1[2] = list(map(int, tableinfo1[2]))
        tableinfo2[0] = list(map(int, tableinfo2[0]))
        tableinfo2[1] = list(map(int, tableinfo2[1]))
        tableinfo2[2] = list(map(int, tableinfo2[2]))

        try:
            self.txcroot.attributes("-topmost", False)
            self.saveCfgpath = filedialog.asksaveasfilename(initialdir='', title='保存cfg',
                                                             filetypes=[("CFG File", 'cfg')],
                                                             initialfile=str(self.SmTypeCode) + '_TT.cfg')  # 获取文件地址
            if self.saveCfgpath == '':
                return
            with open(self.saveCfgpath, "w", encoding='utf-8') as cfg:
                #第一行生成
                cfg.write(";SmType\tSmSubType\tProtocol\tTimeout\tPollingTime\tSmName\n")
                #第二部分头数据
                temp = hex(self.SmTypeCode)[
                       2:] + "\t\t1\t\tYDN\t\t7500\t\t1000\t\t" + self.DevName + '\n' \
                       + '{\n'
                #DataInfo头数据
                temp1 =  ';\t\tGroupType\tCommand\tSubCommand\n' + \
                       '\t\t1\t\t2\t\t1\n' +\
                       '\t  {\n' +\
                       ';\t\tNodeId\tNodeType\tByteLength\tByteOffSet\n'
                #ParaInfo头数据
                temp2 = ';\t\tGroupType\tCommand\tSubCommand\n' + \
                        '\t\t2\t\t2\t\t1\n' + \
                        '\t  {\n' + \
                        ';\t\tNodeId\tNodeType\tByteLength\tByteOffSet\n'
                cfg.write(temp)
                cfg.write(temp1)
                #DataInfo数据
                for i in range(len(tableinfo1[0])):
                    temp = '\t\t' + str(tableinfo1[0][i]) + ',' + str(hex(tableinfo1[1][i])[2:]) + ',' + str(
                        tableinfo1[2][i]) + ',' \
                           + str(tableinfo1[2][i]) + '\n'
                    cfg.write(temp)
                cfg.write('\t}\n')
                #ParaInfo数据
                if len(tableinfo2[0]) != 0:
                    cfg.write(temp2)
                    for i in range(len(tableinfo2[0])):
                        temp = '\t\t' + str(tableinfo2[0][i]) + ',' + str(hex(tableinfo2[1][i])[2:]) + ',' + str(
                            tableinfo2[2][i]) + ',' \
                               + str(tableinfo2[2][i]) + '\n'
                        cfg.write(temp)
                    cfg.write('\t}')
                cfg.write('\n}')
            self.txcroot.attributes("-topmost", False)
            tk.messagebox.showinfo(title="成功！",
                                   message="xls转换cfg成功！请检查数据是否正确！")
        except:
            self.txcroot.attributes("-topmost", False)
            tk.messagebox.showinfo(title="错误！",
                                   message="请检查设备信息和xls表格是否正确！")
        finally:
            self.txcroot.attributes("-topmost", True)

# txt转DATAINFO类
class Txt2NodeCode():
    def __init__(self):
        self.t2nwin = None

    # 创建窗口函数
    def CreateWin(self):
        try:
            if self.t2nwin.state() == 'normal':
                self.t2nwin.attributes('-topmost',True)
                self.t2nwin.attributes('-topmost',False)
                return
        except:
            self.t2nwin = tk.Toplevel(rootc.root)
            self.t2nwin.title('txt转DATAINFO代码--该功能目前尚未完善')

        # 主窗口部分
        self.LeftFrame = tk.Frame(self.t2nwin,bd=10)
        self.RightFrame = tk.Frame(self.t2nwin)
        self.LeftFunctionFrame = tk.Frame(self.LeftFrame)
        self.RightTextFrame = tk.Frame(self.RightFrame)

        self.OpentxtButton = tk.Button(self.LeftFunctionFrame,text='打开txt',width=12,command=self.ReadTxt,font=tkFont.Font(size=12))
        self.CopyToPlateButton = tk.Button(self.LeftFunctionFrame,text='复制到剪切板',width=12,font=tkFont.Font(size=12),command=lambda :public.copytoplate(self.CodeText))
        self.CodeText = tk.Text(self.RightTextFrame,wrap='word', spacing3=5, width=105, height=25,font=tkFont.Font(size=12),state='disabled')


        # 主窗口Frame添加
        self.LeftFrame.grid(row=0,column=0)
        self.RightFrame.grid(row=0,column=1)
        self.LeftFunctionFrame.grid(row=0,column=0)
        self.RightTextFrame.grid(row=0,column=0)
        # 功能区添加
        r=0
        self.OpentxtButton.grid(row=r,column=0)
        r+=1
        self.CopyToPlateButton.grid(row=r,column=0)

        #文本区添加
        self.CodeText.grid(row=0,column=0)

    # 读取txt到列表
    def ReadTxt(self):
        self.txtFilepath = filedialog.askopenfilename(filetypes=[('txt File', 'txt')])  # 获取文件地址
        while self.txtFilepath[-4:] != '.txt' and self.txtFilepath[-4:] != '.TXT':
            if self.txtFilepath == '':  # 如果点击了取消，或者打开了名字为空的文件
                return
            tk.messagebox.showinfo(title="文件格式异常!", message="请打开格式类似TXT_SQL中的“.txt”文本文件！")
            self.txtFilepath = ''
        filestr = []
        self.ovsrstr = []
        # 打开成功，开始读取文件
        with open(self.txtFilepath, 'r') as fp:
            while True:
                line = fp.readline()
                if not line:
                    break
                filestr.append(line.split())

        # 过滤，取出有用点位
        for i in filestr:
            if len(i) == 5:
                if i[2].isdigit() and i[2] != '0':
                    self.ovsrstr.append(i)

        self.Node2Code()
    # 实现点位转代码
    def Node2Code(self):
        self.CodeText.configure(state='normal')
        for i in self.ovsrstr:
            if i[4] == '1':
                self.CodeText.insert(tk.END,'{0:20s}{1:20}\t//{2}\n'.format('PM5K_U8',i[3]+';',i[3]))
            elif i[4] == '4':
                self.CodeText.insert(tk.END,'{0:20s}{1:20}\t//{2}\n'.format('PM5K_F32',i[3]+';',i[3]))
        self.CodeText.configure(state='disabled')
        self.t2nwin.attributes('-topmost', True)
        self.t2nwin.attributes('-topmost', False)

# 智能发包规则类
class SmartRole():
    def __init__(self):
        self.RoleList = []
        self.win = None
        self.cwin = None
        self.mwin = None
    # 创建窗口函数
    def CreateWindow(self):
        try:
            if self.win.state() == 'normal':
                self.win.attributes('-topmost',True)
                self.win.attributes('-topmost',False)
                return
        except:
            self.win = tk.Toplevel(rootc.root)
            self.win.title('智能发包规则')
        #Frame定义
        self.LeftFrame = tk.Frame(self.win,bd=10)
        self.RightFrame = tk.Frame(self.win,padx=10)

        self.RoleListBox = tk.Listbox(self.LeftFrame,width=60,height=20,font=tkFont.Font(size=13),selectbackground='cornflowerblue')
        self.RoleListBoxScr = tk.Scrollbar(self.LeftFrame)
        self.RoleListBox.configure(yscrollcommand=self.RoleListBoxScr.set)
        self.RoleListBoxScr.config(command=self.RoleListBox.yview)
        self.RoleListBoxXScr = tk.Scrollbar(self.LeftFrame,orient=tk.HORIZONTAL)
        self.RoleListBox.configure(xscrollcommand=self.RoleListBoxXScr.set)
        self.RoleListBoxXScr.configure(command=self.RoleListBox.xview)
        self.CreateRoleButton = tk.Button(self.RightFrame,text='新建规则',font=tkFont.Font(size=13),command=self.CreateRole)
        self.ModiFyRoleButton = tk.Button(self.RightFrame,text='修改规则',font=tkFont.Font(size=13),command=self.ModiFyRole)
        self.DelRoleButton = tk.Button(self.RightFrame,text='删除规则',font=tkFont.Font(size=13),command=lambda:self.DelRole(self.RoleListBox.curselection()))
        self.OpenRoleButton = tk.Button(self.RightFrame,text='导入规则',font=tkFont.Font(size=13),command=self.openRole)
        self.SaveRoleButton = tk.Button(self.RightFrame,text='保存规则',font=tkFont.Font(size=13),command=self.saveRole)
        self.CleanRoleButton = tk.Button(self.RightFrame,text='清空规则',font=tkFont.Font(size=13),command=self.cleanRole)

        self.LeftFrame.grid(row=0,column=0)
        self.RightFrame.grid(row=0,column=1)
        self.RoleListBoxScr.pack(side=tk.RIGHT, fill=tk.Y)
        self.RoleListBoxXScr.pack(side=tk.BOTTOM, fill=tk.X)
        self.RoleListBox.pack(fill=tk.X)

        self.CreateRoleButton.grid(row=0,column=0)
        self.ModiFyRoleButton.grid(row=1,column=0)
        self.DelRoleButton.grid(row=2,column=0)
        self.OpenRoleButton.grid(row=3,column=0)
        self.SaveRoleButton.grid(row=4,column=0)
        self.CleanRoleButton.grid(row=5,column=0)

        self.RoleListBox.bind('<<ListboxSelect>>', self.ListBoxFakeWarp)
        self.showRoleFromList()

    # 新建规则函数
    def CreateRole(self):
        try:
            if self.cwin.state() == 'normal':
                self.cwin.attributes('-topmost',True)
                self.cwin.attributes('-topmost',False)
                return
        except:
            self.cwin = tk.Toplevel()
            self.cwin.title('新建规则')

        self.mainFrame = tk.Frame(self.cwin,bd=15,pady=5)
        self.CTrackInfoLabel = tk.Label(self.mainFrame,text='要追踪的包:',font=tkFont.Font(size=14))
        self.CTrackTipsLabel = tk.Label(self.mainFrame,text='(注：MODBUS-TCP无需填报文头，回包内容同前)',fg='red')
        self.CTrackInfoText = tk.Text(self.mainFrame,wrap='word', spacing3=5, width=60, height=3,font=tkFont.Font(size=12))
        self.CSendInfoLabel = tk.Label(self.mainFrame,text='回包的内容:',font=tkFont.Font(size=14))
        self.CSendInfoText = tk.Text(self.mainFrame,wrap='word', spacing3=5, width=60, height=3,font=tkFont.Font(size=12))

        self.CSureButton = tk.Button(self.mainFrame,text='确认',font=tkFont.Font(size=12),width=15,command=self.SureCreateRole)
        self.CCancelButton = tk.Button(self.mainFrame,text='取消',font=tkFont.Font(size=12),width=15,command=self.cancelCreateRole)

        self.mainFrame.pack()
        self.CTrackInfoLabel.grid(row=0,column=0)
        self.CTrackTipsLabel.grid(row=0,column=1)
        self.CTrackInfoText.grid(row=1,column=0,columnspan=3)
        self.CSendInfoLabel.grid(row=2,column=0)
        self.CSendInfoText.grid(row=3,column=0,columnspan=3)
        self.CSureButton.grid(row=4,column=0)
        self.CCancelButton.grid(row=4,column=1)
    # 确认新建规则并添加
    def SureCreateRole(self):
        TrackInfo = self.CTrackInfoText.get('0.0',tk.END)
        SendInfo = self.CSendInfoText.get('0.0',tk.END)
        TrackInfo = TrackInfo.replace('\n','')
        TrackInfo = TrackInfo.replace(',',' ')
        SendInfo = SendInfo.replace('\n','')
        SendInfo = SendInfo.replace(',',' ')
        self.RoleList.append((TrackInfo,SendInfo))
        self.showRole(self.RoleList[-1])
        self.RoleListBox.yview_moveto(1)
        # self.cwin.destroy()
    # 取消新建规则
    def cancelCreateRole(self):
        self.cwin.destroy()


    # 修改规则
    def ModiFyRole(self):
        try:
            if self.mwin.state() == 'normal':
                self.mwin.attributes('-topmost',True)
                self.mwin.attributes('-topmost',False)
                return
        except:
            self.mwin = tk.Toplevel()
            self.mwin.title('修改规则')


        try:
            current = self.Currentset(self.RoleListBox.curselection())
        except:
            print('未选择规则')
            self.mwin.destroy()
            return

        self.mainFrame = tk.Frame(self.mwin, bd=15, pady=5)
        self.CTrackInfoLabel = tk.Label(self.mainFrame, text='要追踪的包:', font=tkFont.Font(size=14))
        self.CTrackTipsLabel = tk.Label(self.mainFrame, text='(注：MODBUS-TCP无需填报文头，回包内容同前)', fg='red')
        self.CTrackInfoText = tk.Text(self.mainFrame, wrap='word', spacing3=5, width=60, height=3,
                                      font=tkFont.Font(size=12))
        self.CSendInfoLabel = tk.Label(self.mainFrame, text='回包的内容:', font=tkFont.Font(size=14))
        self.CSendInfoText = tk.Text(self.mainFrame, wrap='word', spacing3=5, width=60, height=3,
                                     font=tkFont.Font(size=12))

        self.CSureButton = tk.Button(self.mainFrame, text='确认',width=15, font=tkFont.Font(size=12),
                                     command=lambda:self.SureModiFyRole(current))
        self.CCancelButton = tk.Button(self.mainFrame, text='取消',width=15, font=tkFont.Font(size=12),command=self.cancelModfineRole)
        self.mainFrame.pack()
        self.CTrackInfoLabel.grid(row=0, column=0)
        self.CTrackTipsLabel.grid(row=0,column=1)
        self.CTrackInfoText.grid(row=1, column=0, columnspan=3)
        self.CSendInfoLabel.grid(row=2, column=0)
        self.CSendInfoText.grid(row=3, column=0, columnspan=3)
        self.CSureButton.grid(row=4, column=0)
        self.CCancelButton.grid(row=4, column=1)

        self.CTrackInfoText.insert(tk.END,self.RoleList[current[1]][0])
        self.CSendInfoText.insert(tk.END,self.RoleList[current[1]][1])
    #修改并添加
    def SureModiFyRole(self,current):
        TrackInfo = self.CTrackInfoText.get('0.0', tk.END)
        SendInfo = self.CSendInfoText.get('0.0', tk.END)
        TrackInfo = TrackInfo.replace('\n', '')
        TrackInfo = TrackInfo.replace(',', ' ')
        SendInfo = SendInfo.replace('\n', '')
        SendInfo = SendInfo.replace(',', ' ')
        cur,lcur,first, last = self.Currentset(current)
        self.RoleList[lcur] = (TrackInfo,SendInfo)
        self.RoleListBox.delete(first,last)
        self.showRole(self.RoleList[lcur],first)
        self.mwin.destroy()
    # 取消修改规则
    def cancelModfineRole(self):
        self.mwin.destroy()


    # 删除规则
    def DelRole(self,current):
        c,lc,f,l = self.Currentset(current)
        self.RoleListBox.delete(f,l)
        self.RoleList.pop(lc)


    # 保存规则
    def saveRole(self):
        self.win.attributes("-topmost",0)
        self.saveFilepath = filedialog.asksaveasfilename(initialdir='./src/rule/',title='保存规则',filetypes=[("Rule file",'rul')],initialfile='Rule.rul')  # 获取文件地址
        if self.saveFilepath == '':
            self.win.attributes("-topmost", 1)
            self.win.attributes("-topmost", 0)
            return
        if self.saveFilepath.rfind('.rul') != len(self.saveFilepath)-4:
            self.saveFilepath = self.saveFilepath+'.rul'
        with open(self.saveFilepath,'w') as f:
            for i in self.RoleList:
                f.write(i[0]+'\n')
                f.write(i[1]+'\n')
        self.win.attributes("-topmost", 1)
        self.win.attributes("-topmost", 0)

    # 导入规则
    def openRole(self):
        self.win.attributes("-topmost",0)
        self.openRolepath = filedialog.askopenfilename(initialfile='./src/rule',title='导入规则',filetypes=[("Rule file",'rul')])
        self.win.attributes("-topmost", 1)
        self.win.attributes("-topmost", 0)
        if self.openRolepath == '':
            self.win.attributes("-topmost", 1)
            self.win.attributes("-topmost", 0)
            return
        with open(self.openRolepath,'r') as f:
            while True:
                line1 = f.readline()
                line2 = f.readline()
                if not line1 and not line2:
                    break
                self.RoleList.append((line1.strip('\n'),line2.strip('\n')))
                self.showRole(self.RoleList[-1])
                self.RoleListBox.yview_moveto(1)

    # 清空规则
    def cleanRole(self):
        self.win.attributes("-topmost",0)
        sure = tk.messagebox.askyesno(title="警告!",
                               message="该操作不可逆!请确保重要规则已保存!\n是否要清空所有规则？")
        if sure:
            self.RoleList = []
            self.RoleListBox.delete(0,tk.END)
            self.win.attributes("-topmost", 1)
            self.win.attributes("-topmost", 0)
        else:
            self.win.attributes("-topmost", 1)
            self.win.attributes("-topmost", 0)
            return
    # 显示规则函数
    def showRole(self,oRole,pos=tk.END):
        if pos == tk.END:
            self.RoleListBox.insert(pos, '·要追踪的包: ')
            self.RoleListBox.insert(pos, '  '+oRole[0])
            self.RoleListBox.insert(pos, '·要回复的内容: ')
            self.RoleListBox.insert(pos, '  '+oRole[1])
            self.RoleListBox.insert(pos, '----------------------------')
        else:
            pos = int(pos)
            self.RoleListBox.insert(pos, '·要追踪的包: ')
            self.RoleListBox.insert(pos+1, oRole[0])
            self.RoleListBox.insert(pos+2, '·要回复的内容: ')
            self.RoleListBox.insert(pos+3, oRole[1])
            self.RoleListBox.insert(pos+4, '----------------------------')

    # 根据规则表显示规则
    def showRoleFromList(self):
        if self.RoleList != []:
            for i in self.RoleList:
                self.showRole(i)

    # 返回当前位置组
    def Currentset(self,current):
        c = current[0]
        cl = current[0]//5
        f = (current[0]//5)*5
        l = (current[0]//5)*5+4
        return c,cl,f,l

    # 列表框伪换行
    def ListBoxFakeWarp(self,event):
        try:
            current = self.RoleListBox.curselection()
            t,c,first,last = self.Currentset(current)
            self.RoleListBox.select_set(first,last)
        except:
            pass


# Crc16校验类
class CrcCheck():
    def __init__(self):
        self.CheckAogoComboBoxList = ['CRC-16/MODBUS']
        self.CheckAlgoList = [[16,'0x18005','0xFFFF','0x0000',True]]
        self.window = None
    # 创建窗口函数
    def createwindos(self):
        try:
            if self.window.state() == 'normal':
                self.window.attributes('-topmost',True)
                self.window.attributes('-topmost',False)
                return
        except:
            self.window = tk.Toplevel(rootc.root)
            self.window.title('CRC校验工具')

        self.mainFrame = tk.Frame(self.window,bd=15,pady=5)
        # 数据类型部件
        self.DataTypeLabel =tk.Label(self.mainFrame,text='数据类型:',font=tkFont.Font(size=13))
        self.DataTypeV = tk.IntVar()
        self.DataTypeV.set(0)
        self.DataTypeHexRadio = tk.Radiobutton(self.mainFrame,text='Hex',variable=self.DataTypeV,value=0,font=tkFont.Font(size=13))
        self.DataTypeAsciiRadio = tk.Radiobutton(self.mainFrame,text='Ascii',variable=self.DataTypeV,value=1,font=tkFont.Font(size=13))

        #校验算法部件
        self.CheckAlgoLabel = tk.Label(self.mainFrame,text='校验算法:',font=tkFont.Font(size=13))
        self.CheckAlgoComboBox = ttk.Combobox(self.mainFrame)
        self.CheckAlgoComboBox['value'] = self.CheckAogoComboBoxList
        self.CheckAlgoComboBox.current(0)

        # 固定数据部分
        self.WidthLabel = tk.Label(self.mainFrame,text='宽度WIDTH:',font=tkFont.Font(size=10))
        self.WidthEntry = tk.Entry(self.mainFrame,width=20)
        self.PolyLabel = tk.Label(self.mainFrame,text='多项式POLY:',font=tkFont.Font(size=10))
        self.PolyEntry = tk.Entry(self.mainFrame,width=20)
        self.InitLabel = tk.Label(self.mainFrame,text='初始值INIT:',font=tkFont.Font(size=10))
        self.InitEntry = tk.Entry(self.mainFrame,width=20)
        self.XoroutLabel = tk.Label(self.mainFrame,text='异或值XOROUT:',font=tkFont.Font(size=10))
        self.XoroutEntry = tk.Entry(self.mainFrame,width=20)
        self.REFINLabel = tk.Label(self.mainFrame,text='输入数据反转',font=tkFont.Font(size=10))
        self.REFINEntry = tk.Entry(self.mainFrame,width=20)
        self.REFOUTLabel = tk.Label(self.mainFrame,text='输出数据反转',font=tkFont.Font(size=10))
        self.REFOUTEntry = tk.Entry(self.mainFrame,width=20)

        # 要校验的数据部分
        self.CheckDataLabel = tk.Label(self.mainFrame,text='要校验的数据:',font=tkFont.Font(size=13))
        self.CheckDataText = tk.Text(self.mainFrame,wrap='word',spacing3=5, width=75, height=5,font=tkFont.Font(size=12))
        self.CrcCheckButton = tk.Button(self.mainFrame,text='crc校验',font=tkFont.Font(size=13),width=20,height=2,command=self.CalcCrc)
        self.CheckResultLabel = tk.Label(self.mainFrame,text='校验计算结果:',font=tkFont.Font(size=13))
        self.CheckResultEntry = tk.Entry(self.mainFrame)

        # 校验后数据部分
        self.CheckResultOutLabel = tk.Label(self.mainFrame,text='加上校验位后的数据:',font=tkFont.Font(size=13))
        self.CheckResultOutText = tk.Text(self.mainFrame,wrap='word',spacing3=5, width=75, height=3,font=tkFont.Font(size=12),state='disabled')
        self.CodeResultOutLabel = tk.Label(self.mainFrame,text='C语言代码格式：',font=tkFont.Font(size=13))
        self.CodeResultOutText = tk.Text(self.mainFrame,wrap='word',spacing3=5, width=75, height=3,font=tkFont.Font(size=12),state='disabled')

        # 添加物件到窗口
        self.r = 0
        self.c = 0

        self.mainFrame.pack()

        self.DataTypeLabel.grid(row=self.r,column=0)
        self.DataTypeHexRadio.grid(row=self.r,column=1)
        # self.DataTypeAsciiRadio.grid(row=self.r,column=2)
        self.r = self.r + 1

        self.CheckAlgoLabel.grid(row=self.r,column=0)
        self.CheckAlgoComboBox.grid(row=self.r,column=1)
        self.r = self.r+1

        self.SpaceLabel1 = tk.Label(self.mainFrame,height=1)
        self.SpaceLabel1.grid(row=self.r,column=0)
        self.r += 1

        self.WidthLabel.grid(row=self.r,column=0)
        self.WidthEntry.grid(row=self.r,column=1)
        self.PolyLabel.grid(row=self.r,column=2)
        self.PolyEntry.grid(row=self.r,column=3)
        self.r = self.r + 1

        self.InitLabel.grid(row=self.r,column=0)
        self.InitEntry.grid(row=self.r,column=1)
        self.XoroutLabel.grid(row=self.r,column=2)
        self.XoroutEntry.grid(row=self.r,column=3)
        self.r = self.r + 1

        self.REFINLabel.grid(row=self.r,column=0)
        self.REFINEntry.grid(row=self.r,column=1)
        self.REFOUTLabel.grid(row=self.r,column=2)
        self.REFOUTEntry.grid(row=self.r,column=3)
        self.r += 1

        self.SpaceLabel2 = tk.Label(self.mainFrame, height=1)
        self.SpaceLabel2.grid(row=self.r, column=0)
        self.r += 1

        self.CheckDataLabel.grid(row=self.r,column=0)
        self.r = self.r + 1
        self.CheckDataText.grid(row=self.r,column=0,columnspan=5)
        self.r = self.r + 1

        self.CrcCheckButton.grid(row=self.r,column=0,columnspan=2)
        self.CheckResultLabel.grid(row=self.r,column=2)
        self.CheckResultEntry.grid(row=self.r,column=3)
        self.r = self.r + 1

        self.SpaceLabel2 = tk.Label(self.mainFrame, height=1)
        self.SpaceLabel2.grid(row=self.r, column=0)
        self.r += 1

        self.CheckResultOutLabel.grid(row=self.r,column=0)
        self.r = self.r + 1
        self.CheckResultOutText.grid(row=self.r,column=0,columnspan=5)
        self.r += 1
        self.CodeResultOutLabel.grid(row=self.r,column=0,sticky=tk.W)
        self.r += 1
        self.CodeResultOutText.grid(row=self.r,column=0,columnspan=5)

        self.setWPIX(event=None)
        self.CheckAlgoComboBox.bind('<<ComboboxSelected>>', self.setWPIX)

    # 算法关联设置
    def setWPIX(self,event):
        algo = self.CheckAlgoComboBox.get()
        CList = self.CheckAlgoList[self.CheckAogoComboBoxList.index(algo)]
        self.WidthEntry.configure(state='normal')
        self.PolyEntry.configure(state='normal')
        self.InitEntry.configure(state='normal')
        self.XoroutEntry.configure(state='normal')
        self.REFINEntry.configure(state='normal')
        self.REFOUTEntry.configure(state='normal')
        temp = []
        for i in CList:
            temp.append(tk.StringVar())
            temp[-1].set(str(i))
        self.WidthEntry.configure(textvariable=temp[0])
        self.PolyEntry.configure(textvariable=temp[1])
        self.InitEntry.configure(textvariable=temp[2])
        self.XoroutEntry.configure(textvariable=temp[3])
        self.REFINEntry.configure(textvariable=temp[4])
        self.REFOUTEntry.configure(textvariable=temp[4])
        self.WidthEntry.configure(state='disabled')
        self.PolyEntry.configure(state='disabled')
        self.InitEntry.configure(state='disabled')
        self.XoroutEntry.configure(state='disabled')
        self.REFINEntry.configure(state='disabled')
        self.REFOUTEntry.configure(state='disabled')

    # CRC16函数
    def CRC16(self,s,CList):
        crc16 = mkCrcFun(eval(CList[1]),rev=CList[4],initCrc=eval(CList[2]),xorOut=eval(CList[3]))
        data = s.replace(' ','')
        data = data.replace(',','')
        data = data.strip('\n')
        crc_out = hex(crc16(binascii.unhexlify(data))).upper()
        str_list = list(crc_out)
        while len(str_list) < 6:
            str_list.insert(2, '0')  # 位数不足补0，因为一般最少是5个
        crc_data = "".join(str_list)  # 用""把数组的每一位结合起来  组成新的字符串
        s = s.strip().replace(',',' ') + ' ' + crc_data[4:] + ' ' + crc_data[2:4]  # 把源代码和crc校验码连接起来
        return s,crc_data

    # CRC校验按钮回调函数
    def CalcCrc(self):
        algo = self.CheckAlgoList[self.CheckAogoComboBoxList.index(self.CheckAlgoComboBox.get())]
        needcheck = self.CheckDataText.get('0.0',tk.END)
        needcheck = needcheck.replace('0x','')
        needcheck = needcheck.replace(',',' ')
        needcheck = needcheck.replace('，', ' ')
        result = self.CRC16(needcheck,algo)
        coder = result[0].split(' ')
        for i in range(len(coder)):
            coder[i] = '0x'+coder[i]+','
        coder[-1] = coder[-1][:-1]
        t = "".join(coder)
        temp = tk.StringVar()
        temp.set(str(result[1])[2:])
        self.CheckResultEntry.configure(state='normal')
        self.CheckResultEntry.configure(textvariable=temp)
        self.CheckResultEntry.configure(state='disabled')
        self.CheckResultOutText.configure(state='normal')
        self.CodeResultOutText.configure(state='normal')
        self.CheckResultOutText.delete('0.0',tk.END)
        self.CheckResultOutText.insert('0.0',result[0])
        self.CodeResultOutText.delete(0.0,tk.END)
        self.CodeResultOutText.insert(0.0,t)
        self.CheckResultOutText.configure(state='disabled')
        self.CodeResultOutText.configure(state='disabled')


# 设置常用IP地址类
class ConfigCFGC():
    def __init__(self):
        self.win = None
    def CreateWin(self):
        try:
            if self.win.state() == 'normal':
                self.win.attributes('-topmost',True)
                self.win.attributes('-topmost',False)
                return
        except:
            self.win = tk.Toplevel()
            self.win.title('设置常用IP地址')

        self.mainFrame = tk.Frame(self.win,bd=5)
        self.IPFrame = tk.Frame(self.mainFrame,bd=5)
        self.PortFrame = tk.Frame(self.mainFrame,bd=5)

        self.IPLabel = tk.Label(self.mainFrame,text='IP地址',font=tkFont.Font(size=13))
        self.TipLabel = tk.Label(self.mainFrame,text='(注:一行一个，无需间隔符)',fg='red')
        self.IPText = tk.Text(self.IPFrame,wrap='word', spacing3=5, width=60, height=5,font=tkFont.Font(size=12))
        self.IPTextScr = tk.Scrollbar(self.IPFrame)
        self.IPText.configure(yscrollcommand=self.IPTextScr.set)
        self.IPTextScr.configure(command=self.IPText.yview)
        self.PortLabel = tk.Label(self.mainFrame,text='端口',font=tkFont.Font(size=13))
        self.PortText = tk.Text(self.PortFrame,wrap='word', spacing3=5, width=60, height=5,font=tkFont.Font(size=12))
        self.PortTextScr = tk.Scrollbar(self.PortFrame)
        self.PortText.configure(yscrollcommand=self.PortTextScr.set)
        self.PortTextScr.configure(command=self.PortText.yview)
        self.SureButton = tk.Button(self.mainFrame,text='确认',width=10,font=tkFont.Font(size=13),command=self.SureIPPort)
        self.CancelButton = tk.Button(self.mainFrame,text='取消',width=10,font=tkFont.Font(size=13),command=self.win.destroy)

        self.mainFrame.grid(row=0,column=0)
        self.IPLabel.grid(row=0,column=0,sticky=tk.W)
        self.TipLabel.grid(row=0,column=1)
        self.IPFrame.grid(row=1,column=0,columnspan=2)
        self.IPTextScr.pack(side=tk.RIGHT, fill=tk.Y)
        self.IPText.pack(fill=tk.X)
        self.PortLabel.grid(row=2,column=0,sticky=tk.W)
        self.PortFrame.grid(row=3,column=0,columnspan=2)
        self.PortTextScr.pack(fill=tk.Y,side=tk.RIGHT)
        self.PortText.pack(fill=tk.X)
        self.SureButton.grid(row=4,column=0)
        self.CancelButton.grid(row=4,column=1,sticky=tk.W)

        for i in public.localIPList:
            self.IPText.insert(tk.END,i+'\n')
        for i in public.PortList:
            self.PortText.insert(tk.END,str(i)+'\n')

    # 确认修改并生成cfg
    def SureIPPort(self):
        IPList = self.IPText.get(0.0,tk.END).split()
        PortList = self.PortText.get(0.0,tk.END).split()
        with open("./src/config.cfg","w") as f:
            f.write('[IP]\n')
            for i in IPList:
                f.write(i+'\n')
            f.write('[Port]\n')
            for i in PortList:
                f.write(i+'\n')
        public.initCFG()
        rootc.IpCombobox['value'] = public.localIPList
        rootc.IpCombobox.current(len(public.localIPList)-1)
        if not rootc.ProtocolTypeCombobox.get() == public.ProtocolTypeList[1]:
            rootc.IPPortCombobox['value'] = public.PortList
            rootc.IPPortCombobox.current(len(public.PortList)-1)
        self.win.destroy()


# 白盒Lua类
class WbLuaTool():
    def __init__(self):
        self.defaultList = ['[DevType]', '406-开关电源', '407-蓄电池组', '408-UPS设备', '415-普通空调', '416-智能电表(交流)', '418-机房/基站环境', '432-铁锂电池', '444-室外配电设备', '445-分路计量设备', '447-梯级电池', '451-微站监控设备', '455-智能备电控制单元', '自定义-自定义', '[MODEL]', '空调-kt', '电源-power', '电表-ammeter', '油机-yj', '读卡器-card reader', '自定义-自定义']
        self.DevModelList = []
        self.ProtocolTypeList = ['电总(gmoe)','Modbus(modbus)','私有协议']
        self.DevTypeCodeList = []
        self.DBADataBaseList = []
        self.DataBaseIP = '10.1.40.88'
        self.DataBaseUser = 'sa'
        self.DataBasePass = 'password'
        self.DB_AInterFace_Code = ''
        self.CName = None
        self.DevTypeCode = None
        self.DevFactory = None
        self.DevName = None
        self.DevFactory_2 = None
        self.DevModel = None
        self.ProtocolType = None
        self.LuaName = None
        self.SoName = None
        self.win = None
        self.C2Lwin = None
        self.DBAwin = None
        self.ESRwin = None
        self.udtwin = None
        self.umwin = None

    # 创建窗口函数
    def CreateWin(self):
        try:
            if self.win.state() == 'normal':
                self.win.attributes('-topmost',True)
                self.win.attributes('-topmost',False)
                return
        except:
            self.win = tk.Toplevel()
            self.win.title("白盒化Lua工具")


        self.menubar = tk.Menu(self.win,fg='red')
        self.win.configure(menu=self.menubar)
        self.menubar.add_command(label='配置字典表',command=self.UpdateDictTable)
        self.menubar.add_command(label='配置MODEL',command=self.UpdateMODEL)
        self.menubar.add_command(label='初始化配置',command=lambda:self.LuaTypeModelInit(True))

        self.LeftUpFrame = tk.Frame(self.win,bd=20,highlightbackground='white', highlightthickness=2)
        self.LeftDownFrame = tk.Frame(self.win)
        self.RightUpFrame = tk.Frame(self.win,bd=5)
        self.RightDownFrame = tk.Frame(self.win)

        self.DevCNameLabel = tk.Label(self.LeftUpFrame,text='设备中文名',font=tkFont.Font(size=12,weight='bold'))
        self.DevCNameEntry = tk.Entry(self.LeftUpFrame,width=25,font=tkFont.Font(size=13))
        self.DevCNameExLabel = tk.Label(self.LeftUpFrame, text='例：亚奥PM5000CM',fg='grey')
        self.DevTypeCodeLabel = tk.Label(self.LeftUpFrame,text='设备编码',font=tkFont.Font(size=12,weight='bold'),fg='red',pady=10)
        self.DevTypeCodeCombobox = ttk.Combobox(self.LeftUpFrame,width=25,font=tkFont.Font(size=12))
        self.DevTypeCodeExLabel = tk.Label(self.LeftUpFrame, text='例：1234',fg='grey')
        self.DevFactoryLabel = tk.Label(self.LeftUpFrame,text='协议厂家',font=tkFont.Font(size=12,weight='bold'),fg='red',pady=10)
        self.DevFactoryEntry = tk.Entry(self.LeftUpFrame,width=25,font=tkFont.Font(size=13))
        self.DevFactoryExLabel = tk.Label(self.LeftUpFrame,text='例：YaAo',fg='grey')
        self.DevNameLabel = tk.Label(self.LeftUpFrame,text='设备型号',font=tkFont.Font(size=12,weight='bold'),fg='red',pady=10)
        self.DevNameEntry = tk.Entry(self.LeftUpFrame,width=25,font=tkFont.Font(size=13))
        self.DevNameExLabel = tk.Label(self.LeftUpFrame,text='例：PM5000',fg='grey')
        self.DevFactory_2Label = tk.Label(self.LeftUpFrame,text='厂家名字缩写',font=tkFont.Font(size=12,weight='bold'),pady=10)
        self.DevFactory_2Entry = tk.Entry(self.LeftUpFrame,width=25,font=tkFont.Font(size=13))
        self.DevFactory_2ExLabel = tk.Label(self.LeftUpFrame,text='例：YA(可省略)',fg='grey')
        self.DevModelLabel = tk.Label(self.LeftUpFrame,text='MODEL',font=tkFont.Font(size=12,weight='bold'),pady=10)
        self.DevModelCombobox = ttk.Combobox(self.LeftUpFrame,width=22,font=tkFont.Font(size=13))


        self.DevModelExLabel = tk.Label(self.LeftUpFrame,text='例：电源-power',fg='grey')
        self.ProtocolTypeLabel = tk.Label(self.LeftUpFrame,text='协议类型',font=tkFont.Font(size=12,weight='bold'),pady=10)
        self.ProtocolTypeCombobox = ttk.Combobox(self.LeftUpFrame,width=22,font=tkFont.Font(size=13),state='readonly')
        self.ProtocolTypeCombobox['value'] = self.ProtocolTypeList
        self.ProtocolTypeCombobox.current(0)
        self.ProtocolExLabel = tk.Label(self.LeftUpFrame,text='例：电总(gmoe)',fg='grey')
        self.SureInfoButton = tk.Button(self.LeftUpFrame,text='确认信息',command=self.SureInfo)
        self.CleanInfoButton = tk.Button(self.LeftUpFrame,text='清空信息',command=self.CleanInfo)

        self.ShowDevCnameLabel = tk.Label(self.RightUpFrame,text='设备中文名:')
        self.ShowDevCnameInfoLabel = tk.Label(self.RightUpFrame,text='')
        self.ShowDevTypeCodeLabel = tk.Label(self.RightUpFrame,text='设备类型编码:')
        self.ShowDevTypeCodeInfoLabel = tk.Label(self.RightUpFrame,text='')
        self.ShowDevFactoryLabel = tk.Label(self.RightUpFrame,text='协议厂家:')
        self.ShowDevFactoryInfoLabel = tk.Label(self.RightUpFrame,text='')
        self.ShowDevNameLabel = tk.Label(self.RightUpFrame,text='设备型号:')
        self.ShowDevNameInfoLabel = tk.Label(self.RightUpFrame,text='')
        self.ShowDevFactory_2Label = tk.Label(self.RightUpFrame,text='厂家名缩写:')
        self.ShowDevFactory_2InfoLabel = tk.Label(self.RightUpFrame,text='')
        self.ShowDevModelLabel = tk.Label(self.RightUpFrame,text='MODEL类型：')
        self.ShowDevModelInfoLabel = tk.Label(self.RightUpFrame,text='')
        self.ShowProtocolTypeLabel = tk.Label(self.RightUpFrame,text='协议类型:')
        self.ShowProtocolTypeInfoLabel = tk.Label(self.RightUpFrame,text='')
        self.ShowLuaNameLabel = tk.Label(self.RightUpFrame,text='.lua文件名:')
        self.ShowLuaNameInfoLabel = tk.Label(self.RightUpFrame,text='')
        self.ShowSoNameLabel = tk.Label(self.RightUpFrame,text='.so文件名:')
        self.ShowSoNameInfoLabel = tk.Label(self.RightUpFrame,text='',takefocus=True)
        self.ShowDevTTIdLabel = tk.Label(self.RightUpFrame,text='设备ID:')
        self.ShowDevTTIdInfoLabel = tk.Label(self.RightUpFrame,text='')

        self.Step1Label = tk.Label(self.RightDownFrame,text='Step1==>创建一个白盒模版(需先确认信息)',fg='grey')
        self.Step2Label = tk.Label(self.RightDownFrame,text='Step2==>C语言数组’{}‘、备注//转换成Lua语言',fg='grey')
        self.Step3Label = tk.Label(self.RightDownFrame,text='Step3==>直接生成数据库A接口关联代码',fg='grey')
        self.Step4Label = tk.Label(self.RightDownFrame,text='Step4==>将已有的TT.cfg转换成白盒Lua的GroupType代码',fg='grey')
        self.Step5Label = tk.Label(self.RightDownFrame,text='Step5==>自行完成收发数据函数',fg='grey')
        self.CreateStandardLuaFolderButton = tk.Button(self.RightDownFrame,text='生成白盒模版文件夹',font=tkFont.Font(size=12),width=25,state='disabled',command=self.CreateLuaExample)
        self.CCmdCode2LuaCmdCodeButton = tk.Button(self.RightDownFrame,text='C语言命令转Lua命令',font=tkFont.Font(size=12),width=25,command=self.CCmd2LuaCmd)
        self.DB_AInterfaceRelationCodeCreateButton = tk.Button(self.RightDownFrame,text='获取数据库A接口关联代码',command=self.DB_AInterfaceCodeCreate,font=tkFont.Font(size=12),width=25)
        self.TTCfg2LuaCodeButton = tk.Button(self.RightDownFrame,text='TT.cfg转Lua.GroupType代码',font=tkFont.Font(size=12),width=25,command=self.TTCfg2LuaGroup)
        self.EasySeeRelationIDButton = tk.Button(self.RightDownFrame,text='关联ID简视化',font=tkFont.Font(size=12),width=25,command=self.EasySeeRelationID)

        # 界面生成部分
        self.LeftUpFrame.grid(row=0,column=0,rowspan=2)
        self.LeftDownFrame.grid(row=1,column=0)
        self.RightUpFrame.grid(row=0,column=1)
        self.RightDownFrame.grid(row=1,column=1,sticky=tk.N)

        self.row = -1
        self.DevCNameLabel.grid(row= self.r(),column=0,columnspan=2,sticky=tk.W)
        self.DevCNameExLabel.grid(row=self.r(0), column=0, columnspan=2, sticky=tk.NE)
        self.DevCNameEntry.grid(row=self.r(),column=0,columnspan=2)
        self.DevTypeCodeLabel.grid(row=self.r(),column=0,columnspan=2,sticky=tk.W)
        self.DevTypeCodeExLabel.grid(row=self.r(0), column=0, columnspan=2, sticky=tk.SE)
        self.DevTypeCodeCombobox.grid(row=self.r(),column=0,columnspan=2)
        self.DevFactoryLabel.grid(row=self.r(),column=0,columnspan=2,sticky=tk.W)
        self.DevFactoryExLabel.grid(row=self.r(0), column=0, columnspan=2, sticky=tk.SE)
        self.DevFactoryEntry.grid(row=self.r(),column=0,columnspan=2)
        self.DevNameLabel.grid(row=self.r(),column=0,columnspan=2,sticky=tk.W)
        self.DevNameExLabel.grid(row=self.r(0), column=0, columnspan=2, sticky=tk.SE)
        self.DevNameEntry.grid(row=self.r(),column=0,columnspan=2)
        self.DevFactory_2Label.grid(row=self.r(),column=0,columnspan=2,sticky=tk.W)
        self.DevFactory_2ExLabel.grid(row=self.r(0), column=0, columnspan=2, sticky=tk.SE)
        self.DevFactory_2Entry.grid(row=self.r(),column=0,columnspan=2)
        self.DevModelLabel.grid(row=self.r(),column=0,columnspan=2,sticky=tk.W)
        # self.DevModelExLabel.grid(row=self.r(), column=0, columnspan=2, sticky=tk.E)
        self.DevModelCombobox.grid(row=self.r(),column=0,columnspan=2)
        self.ProtocolTypeLabel.grid(row=self.r(),column=0,columnspan=2,sticky=tk.W)
        # self.ProtocolExLabel.grid(row=self.r(), column=0, columnspan=2, sticky=tk.E)
        self.ProtocolTypeCombobox.grid(row=self.r(),column=0,columnspan=2)
        self.SpaceLabel = tk.Label(self.LeftUpFrame,text='',height=1)
        self.SpaceLabel.grid(row=self.r(),column=0)
        self.SureInfoButton.grid(row=self.r(),column=0)
        self.CleanInfoButton.grid(row=self.r(0),column=1)

        # 信息展示区
        self.row = -1
        self.LineLabel1 = tk.Label(self.RightUpFrame,text='-------------------------------------------------------------------------')
        self.LineLabel1.grid(row=self.r(),column=0,columnspan=2)
        self.ShowDevCnameLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.ShowDevCnameInfoLabel.grid(row=self.r(0),column=1,sticky=tk.W)
        self.ShowDevTypeCodeLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.ShowDevTypeCodeInfoLabel.grid(row=self.r(0),column=1,sticky=tk.W)
        self.ShowDevFactoryLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.ShowDevFactoryInfoLabel.grid(row=self.r(0),column=1,sticky=tk.W)
        self.ShowDevNameLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.ShowDevNameInfoLabel.grid(row=self.r(0),column=1,sticky=tk.W)
        self.ShowDevFactory_2Label.grid(row=self.r(),column=0,sticky=tk.W)
        self.ShowDevFactory_2InfoLabel.grid(row=self.r(0),column=1,sticky=tk.W)
        self.ShowDevModelLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.ShowDevModelInfoLabel.grid(row=self.r(0),column=1,sticky=tk.W)
        self.ShowProtocolTypeLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.ShowProtocolTypeInfoLabel.grid(row=self.r(0),column=1,sticky=tk.W)
        self.ShowLuaNameLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.ShowLuaNameInfoLabel.grid(row=self.r(0),column=1,sticky=tk.W)
        self.ShowSoNameLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.ShowSoNameInfoLabel.grid(row=self.r(0),column=1,sticky=tk.W)
        self.ShowDevTTIdLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.ShowDevTTIdInfoLabel.grid(row=self.r(0),column=1,sticky=tk.W)
        self.LineLabel2 = tk.Label(self.RightUpFrame,
                                   text='-------------------------------------------------------------------------')
        self.LineLabel2.grid(row=self.r(), column=0,columnspan=2)
        # 功能区
        self.row = -1
        self.Step1Label.grid(row=self.r(),column=0,sticky=tk.W)
        self.CreateStandardLuaFolderButton.grid(row=self.r(),column=0,columnspan=2)
        self.Step2Label.grid(row=self.r(), column=0,sticky=tk.W)
        self.CCmdCode2LuaCmdCodeButton.grid(row=self.r(),column=0,columnspan=2)
        self.Step3Label.grid(row=self.r(), column=0,sticky=tk.W)
        self.DB_AInterfaceRelationCodeCreateButton.grid(row=self.r(),column=0,columnspan=2)
        self.Step4Label.grid(row=self.r(), column=0,sticky=tk.W)
        self.TTCfg2LuaCodeButton.grid(row=self.r(),column=0,columnspan=2)
        self.Step5Label.grid(row=self.r(), column=0,sticky=tk.W)
        self.EasySeeRelationIDButton.grid(row=self.r(),column=0)

        # 数据初始化
        self.DevTypeCodeList = []
        self.DevModelList = []
        with open('./src/luaconfig.cfg','r',encoding='utf-8') as f:
            line = f.readline()
            if line == '[DevType]\n':
                line = f.readline()
                while line != '[MODEL]\n':
                    self.DevTypeCodeList.append(line.replace('\n',''))
                    line = f.readline()
                line = f.readline()
                while line != '':
                    self.DevModelList.append(line.replace('\n',''))
                    line = f.readline()
        try:
            self.DevTypeCodeCombobox['value'] = self.DevTypeCodeList
            self.DevModelCombobox['value'] = self.DevModelList
            self.DevTypeCodeCombobox.current(0)
            self.DevModelCombobox.current(0)
        except:
            self.LuaTypeModelInit()
            self.DevTypeCodeCombobox['value'] = self.DevTypeCodeList
            self.DevModelCombobox['value'] = self.DevModelList
            self.DevTypeCodeCombobox.current(0)
            self.DevModelCombobox.current(0)
        # self.Test()

    # 行row函数
    def r(self,a=1):
        if a == 0:
            return self.row
        self.row += 1
        return self.row
    # 判断是否有中文
    def is_chinese(self, string):
        for ch in string:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True

        return False

    # 修改字典表函数窗口
    def UpdateDictTable(self):
        try:
            if self.udtwin.state() == 'normal':
                self.udtwin.attributes('-topmost',True)
                self.udtwin.attributes('-topmost',False)
                return
        except:
            self.udtwin = tk.Toplevel()
            self.udtwin.title('修改字典表')

        self.mainFrame = tk.Frame(self.udtwin)
        self.udtTextFrame = tk.Frame(self.mainFrame)

        self.udtText = tk.Text(self.udtTextFrame,wrap='none',spacing3=5, width=45, height=15,font=tkFont.Font(size=12))
        self.udtTextXScr = tk.Scrollbar(self.udtTextFrame,orient=tk.HORIZONTAL)
        self.udtTextYScr = tk.Scrollbar(self.udtTextFrame)
        self.udtText.configure(xscrollcommand=self.udtTextXScr.set,yscrollcommand=self.udtTextYScr.set)
        self.udtTextXScr.configure(command=self.udtText.xview)
        self.udtTextYScr.configure(command=self.udtText.yview)
        self.udtsureButton = tk.Button(self.mainFrame,text='确认',width=10,command=self.SureUpdateDictTable)

        self.mainFrame.grid(row=0,column=0)
        self.udtTextFrame.grid(row=0,column=0)

        self.udtTextXScr.pack(fill=tk.X,side=tk.BOTTOM)
        self.udtTextYScr.pack(fill=tk.Y,side=tk.RIGHT)
        self.udtText.pack()

        self.udtsureButton.grid(row=1,column=0)
        # 数据初始化
        self.udtText.delete(0.0,tk.END)
        for i in self.DevTypeCodeList:
            self.udtText.insert(tk.END,i+'\n')
    # 修改字典表
    def SureUpdateDictTable(self):
        t = self.udtText.get(0.0,tk.END).split('\n')
        while '[DevType]' in t:
            t.pop(t.index('[DevType]'))
        while '' in t:
            t.pop(t.index(''))
        mt = []
        self.DevTypeCodeList = t
        self.DevTypeCodeCombobox['value'] = self.DevTypeCodeList
        self.DevTypeCodeCombobox.current(0)

        with open('./src/luaconfig.cfg','r',encoding='utf-8') as f:
            line = f.readline()
            while line != '[MODEL]\n':
                line = f.readline()
            while line !='':
                line = f.readline()
                mt.append(line.replace('\n',''))
        while mt[-1] == '':
            mt.pop()
        with open('./src/luaconfig.cfg','w',encoding='utf-8') as f:
            f.write('[DevType]\n')
            for i in t:
                f.write(i+'\n')
            f.write('[MODEL]\n')
            for i in mt:
                f.write(i+'\n')
        self.udtwin.destroy()

    # 修改MODEL函数窗口
    def UpdateMODEL(self):
        try:
            if self.umwin.state() == 'normal':
                self.umwin.attributes('-topmost',True)
                self.umwin.attributes('-topmost',False)
                return
        except:
            self.umwin = tk.Toplevel()
            self.umwin.title('修改MODEL')

        self.mainFrame = tk.Frame(self.umwin)
        self.umTextFrame = tk.Frame(self.mainFrame)

        self.umText = tk.Text(self.umTextFrame,wrap='none',spacing3=5, width=45, height=15,font=tkFont.Font(size=12))
        self.umTextXScr = tk.Scrollbar(self.umTextFrame,orient=tk.HORIZONTAL)
        self.umTextYScr = tk.Scrollbar(self.umTextFrame)
        self.umText.configure(xscrollcommand=self.umTextXScr.set,yscrollcommand=self.umTextYScr.set)
        self.umTextXScr.configure(command=self.umText.xview)
        self.umTextYScr.configure(command=self.umText.yview)
        self.umsureButton = tk.Button(self.mainFrame,text='确认',width=10,command=self.SureUpdateMODEL)

        self.mainFrame.grid(row=0,column=0)
        self.umTextFrame.grid(row=0,column=0)

        self.umTextXScr.pack(fill=tk.X,side=tk.BOTTOM)
        self.umTextYScr.pack(fill=tk.Y,side=tk.RIGHT)
        self.umText.pack()

        self.umsureButton.grid(row=1,column=0)
        # 数据初始化
        self.umText.delete(0.0,tk.END)
        for i in self.DevModelList:
            self.umText.insert(tk.END,i+'\n')
    # 修改MODEL
    def SureUpdateMODEL(self):
        t = self.umText.get(0.0, tk.END).split('\n')
        while '[MODEL]' in t:
            t.pop(t.index('[MODEL]'))
        while '' in t:
            t.pop(t.index(''))
        dt = []
        self.DevModelList = t
        self.DevModelCombobox['value'] = self.DevModelList
        self.DevModelCombobox.current(0)

        with open('./src/luaconfig.cfg', 'r', encoding='utf-8') as f:
            line = f.readline()
            if line == '[DevType]\n':
                line = f.readline()
            while line != '[MODEL]\n':
                dt.append(line.replace('\n',''))
                line = f.readline()
        while dt[-1] == '':
            dt.pop()
        with open('./src/luaconfig.cfg', 'w', encoding='utf-8') as f:
            f.write('[DevType]\n')
            for i in dt:
                f.write(i + '\n')
            f.write('[MODEL]\n')
            for i in t:
                f.write(i + '\n')
        self.umwin.destroy()

    # 配置初始化
    def LuaTypeModelInit(self,i = False):
        if i == True:
            ask = tk.messagebox.askyesno(title='是否初始化配置？',message='将丢失所有已配置的内容，是否继续？')
            if ask == False:
                return
        self.DevTypeCodeList = []
        self.DevModelList = []
        with open('./src/luaconfig.cfg','w',encoding='utf-8') as f:
            for i in self.defaultList:
                f.write(i+'\n')
        with open('./src/luaconfig.cfg','r',encoding='utf-8') as f:
            line = f.readline()
            if line == '[DevType]\n':
                line = f.readline()
                while line != '[MODEL]\n':
                    self.DevTypeCodeList.append(line.replace('\n',''))
                    line = f.readline()
                line = f.readline()
                while line != '':
                    self.DevModelList.append(line.replace('\n',''))
                    line = f.readline()
        while self.DevTypeCodeList[-1] == '':
            self.DevTypeCodeList.pop()
        while self.DevModelList[-1] == '':
            self.DevModelList.pop()
        self.DevTypeCodeCombobox['value'] = self.DevTypeCodeList
        self.DevTypeCodeCombobox.current(0)
        self.DevModelCombobox['value'] = self.DevModelList
        self.DevModelCombobox.current(0)
        if i:
            tk.messagebox.showinfo(title='配置已初始化！',message='已初始化成功！')
        self.win.attributes('-topmost',True)
        self.win.attributes('-topmost',False)

    # 确认信息函数
    def SureInfo(self):
        self.CName = self.DevCNameEntry.get()
        self.DevTypeCode = self.DevTypeCodeCombobox.get()[:self.DevTypeCodeCombobox.get().find('-')]
        self.DevFactory = self.DevFactoryEntry.get()
        self.DevName = self.DevNameEntry.get()
        self.DevFactory_2 = self.DevFactory_2Entry.get()
        self.DevModel = self.DevModelCombobox.get()
        if '-' in self.DevModel and not self.is_chinese(self.DevModel[self.DevModel.index('-')+1:]):
            self.DevModel = self.DevModel[self.DevModel.index('-')+1:]
        elif self.DevModel.replace(' ','').isalnum() and not self.is_chinese(self.DevModel):
            pass
        else:
            self.win.attributes('-topmost', False)
            tk.messagebox.showwarning(title='请检查MODEL是否输入正确！', message='MODEL中不能出现英文数字以外的字符！')
            self.win.attributes('-topmost',True)
            self.win.attributes('-topmost', False)
            return

        self.ProtocolType = self.ProtocolTypeCombobox.get()

        if self.CName == '':
            self.win.attributes('-topmost', False)
            tk.messagebox.showwarning(title='请输入设备中文名！', message='请输入设备中文名！')
            self.win.attributes('-topmost', True)
            self.win.attributes('-topmost', False)
            return
        if self.DevTypeCode.isdigit():# 设备编码只能为数字
            if self.DevFactory.isalpha() and not self.is_chinese(self.DevFactory):# 协议厂家只能为英文
                if self.DevName.isalnum() and not self.is_chinese(self.DevName):# 设备型号只能为英文或数字
                    self.ShowDevCnameInfoLabel.configure(text=self.CName)
                    self.ShowDevTypeCodeInfoLabel.configure(text=self.DevTypeCode)
                    self.ShowDevFactoryInfoLabel.configure(text=self.DevFactory)
                    self.ShowDevNameInfoLabel.configure(text=self.DevName)
                    self.ShowDevFactory_2InfoLabel.configure(text=self.DevFactory_2)
                    self.ShowDevModelInfoLabel.configure(text=self.DevModel)
                    self.ShowProtocolTypeInfoLabel.configure(text=self.ProtocolType)
                    #lib_<设备类型编码>_<协议厂家编码>_<设备型号>
                    self.LuaName = 'lib_'+self.DevTypeCode+'_'+self.DevFactory+'_'+self.DevName+'.lua'
                    self.ShowLuaNameInfoLabel.configure(text=self.LuaName)
                    #lib_<设备类型编码，即信号字典表中的 设备编码>_<协议厂家编码，不允许汉字>_<设备型号，不允许汉字>-<厂家名2字缩写>.so，
                    self.SoName = 'lib_'+self.DevTypeCode+'_'+self.DevFactory+'_'+self.DevName
                    #431281+***+10660
                    self.ShowDevTTIdInfoLabel.configure(text='431281'+self.DevTypeCode+'10660')
                    if self.DevFactory_2 == '':
                        self.SoName = self.SoName+'.so'
                    else:
                        self.SoName = self.SoName+'-'+self.DevFactory_2+'.so'
                    self.ShowSoNameInfoLabel.configure(text=self.SoName)
                    self.CreateStandardLuaFolderButton.configure(state='normal')
                else:
                    self.win.attributes('-topmost', False)
                    tk.messagebox.showwarning(title='请检查设备型号！',message='设备型号只能为英文或数字！')
                    self.win.attributes('-topmost', True)
                    self.win.attributes('-topmost', False)
            else:
                self.win.attributes('-topmost', False)
                tk.messagebox.showwarning(title='请检查协议厂家！',message='协议厂家中只能为纯英文！')
                self.win.attributes('-topmost', True)
                self.win.attributes('-topmost', False)
        else:
            self.win.attributes('-topmost', False)
            tk.messagebox.showwarning(title='请检查设备编码！',message='设备编码只能为1~9999的十进制整数！')
            self.win.attributes('-topmost', True)
            self.win.attributes('-topmost', False)

    # 清空信息
    def CleanInfo(self):
        self.ShowDevCnameInfoLabel.configure(text='')
        self.ShowDevTypeCodeInfoLabel.configure(text='')
        self.ShowDevFactoryInfoLabel.configure(text='')
        self.ShowDevNameInfoLabel.configure(text='')
        self.ShowDevFactory_2InfoLabel.configure(text='')
        self.ShowDevModelInfoLabel.configure(text='')
        self.ShowProtocolTypeInfoLabel.configure(text='')
        self.ShowLuaNameInfoLabel.configure(text='')
        self.ShowSoNameInfoLabel.configure(text='')
        self.ShowDevTTIdInfoLabel.configure(text='')

        self.DevCNameEntry.delete(0,tk.END)
        self.DevTypeCodeCombobox.current(0)
        self.DevFactoryEntry.delete(0,tk.END)
        self.DevNameEntry.delete(0,tk.END)
        self.DevFactory_2Entry.delete(0,tk.END)
        self.DevModelCombobox.current(0)
        self.ProtocolTypeCombobox.current(0)
        self.CreateStandardLuaFolderButton.configure(state='disabled')

    # 测试信息
    def Test(self):
        self.DevCNameEntry.insert(0,'亚奥PM5000CM')
        self.DevFactoryEntry.insert(0,'YaAo')
        self.DevNameEntry.insert(0,'PM5000')

    # 创建白盒模版
    def CreateLuaExample(self):
        self.win.attributes('-topmost', False)
        self.LuaDirectory = tk.filedialog.askdirectory(title='选择模版保存路径')
        self.LuaDirectory = self.LuaDirectory+'/'+self.CName
        if os.path.exists(self.LuaDirectory):
            tk.messagebox.showwarning(title='路径已存在！',message='路径已存在！请重新选择路径！')
            self.win.attributes('-topmost', True)
            self.win.attributes('-topmost', False)
        else:
            os.mkdir(self.LuaDirectory)
            os.mkdir(self.LuaDirectory+'/'+self.LuaName[:-4]+'_lua')
            os.mkdir(self.LuaDirectory+'/参考文献')
            os.mkdir(self.LuaDirectory+'/源码')
            self.LualuaName = self.LuaDirectory+'/'+self.LuaName[:-4]+'_lua/'+self.LuaName
            if self.ProtocolType == self.ProtocolTypeList[0]:#电总
                self.Expath = './src/code/dzluaexample.lua'
            elif self.ProtocolType == self.ProtocolTypeList[1]:#Modbus
                self.Expath = './src/code/modbusexample.lua'
            elif self.ProtocolType == self.ProtocolTypeList[2]:#私有协议
                self.Expath = './src/code/syluaexample.lua'
            with open(self.LualuaName,'w',encoding='utf-8') as fw:
                with open(self.Expath,'r',encoding='utf-8') as fr:
                    # 创建头部分
                    readline = fr.readline()
                    for i in range(10):
                        fw.write(readline)
                        readline = fr.readline()

                    fw.write('\nDEV_NAME = "'+self.CName+'"\n')
                    fw.write('VERSION	 = "1.0.0"\n')
                    fw.write('MODEL = "'+self.DevModel+'"\n\n')

                    readline = fr.readline()
                    while readline != '-- Lua模版结束\n':
                        fw.write(readline)
                        readline = fr.readline()
        rootc.root.attributes('-topmost',True)
        self.win.attributes('-topmost',True)
        rootc.root.attributes('-topmost',False)
        self.win.attributes('-topmost',False)
        os.startfile(self.LuaDirectory.replace(self.CName, ''))

    # 复制到剪切板
    def copytoplate(self,obj,str1=None):
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        if str1 == None:
            t = obj.get(0.0,tk.END)
        else:
            t = str1
        root.clipboard_append(t)
        root.destroy()


    # C语言命令转Lua命令界面
    def CCmd2LuaCmd(self):
        # 窗口创建
        try:
            if self.C2Lwin.state() == 'normal':
                self.C2Lwin.attributes('-topmost', True)
                self.C2Lwin.attributes('-topmost', False)
                return
        except:
            self.C2Lwin = tk.Toplevel()
            self.C2Lwin.title('C语言命令转Lua命令')
            self.C2Lwin.attributes('-topmost',True)
            self.C2Lwin.attributes('-topmost',False)

        self.C2LUpFrame = tk.Frame(self.C2Lwin,bd=5,width=800,height=80)
        self.C2LDownFrame = tk.Frame(self.C2Lwin,bd=5)
        self.C2LDLTextFrame = tk.Frame(self.C2LDownFrame,bd=5)
        self.C2LDRTextFrame = tk.Frame(self.C2LDownFrame,bd=5,padx=15)

        self.C2LExLabel = tk.Label(self.C2LUpFrame,text='例：',fg='grey')
        self.C2LCExLabel = tk.Label(self.C2LUpFrame,text='C语言代码：\n'
                                                         '{0x01,0x01,0x20,0x01,0x00,0x28},    //  0x01读线圈\n'
                                                         '{0x01,0x03,0x00,0x01,0x00,0x04},    //  0x03读寄存器\n'
                                                         '...\n',justify=tk.LEFT,fg='grey')
        self.C2L2Label = tk.Label(self.C2LUpFrame,text='        ===转换==>       ',fg='grey')
        self.C2LLExLabel = tk.Label(self.C2LUpFrame,text='Lua代码：\n'
                                                         '"0x01,0x01,0x20,0x01,0x00,0x28",    -- 0x01读线圈\n'
                                                         '"0x01,0x03,0x00,0x01,0x00,0x04",    -- 0x03读寄存器     \n'
                                                         '...\n',justify=tk.LEFT,fg='grey')

        self.C2LCCodeText = tk.Text(self.C2LDLTextFrame, wrap='none', spacing3=5, width=40, height=20,font=tkFont.Font(size=12))
        self.C2LCCodeYScr = tk.Scrollbar(self.C2LDLTextFrame)
        self.C2LCCodeXScr = tk.Scrollbar(self.C2LDLTextFrame)
        self.C2LCCodeText.configure(yscrollcommand=self.C2LCCodeYScr.set,xscrollcommand=self.C2LCCodeXScr.set)
        self.C2LCCodeYScr.configure(command=self.C2LCCodeText.yview)
        self.C2LCCodeXScr.configure(command=self.C2LCCodeText.xview,orient=tk.HORIZONTAL)

        self.C2LStartButton = tk.Button(self.C2LDownFrame,text='开始转换',command=self.C2L,width=15)
        self.C2LCleanButton = tk.Button(self.C2LDownFrame, text='全部清空',command=self.CleanC2L,width=15)
        self.C2LPasteButton = tk.Button(self.C2LDownFrame, text='粘贴到C代码',command=lambda :self.C2LCCodeText.event_generate('<<Paste>>'),width=15)
        self.C2LCopyButton = tk.Button(self.C2LDownFrame, text='复制Lua代码',command=lambda: self.copytoplate(self.C2LLCodeText),width=15)
        self.C2LLCodeText = tk.Text(self.C2LDRTextFrame, wrap='none', spacing3=5, width=40, height=20,font=tkFont.Font(size=12))
        self.C2LLCodeYScr = tk.Scrollbar(self.C2LDRTextFrame)
        self.C2LLCodeXScr = tk.Scrollbar(self.C2LDRTextFrame,orient=tk.HORIZONTAL)
        self.C2LLCodeText.configure(yscrollcommand=self.C2LLCodeYScr.set,xscrollcommand=self.C2LLCodeXScr.set)
        self.C2LLCodeYScr.configure(command=self.C2LLCodeText.yview)
        self.C2LLCodeXScr.configure(command=self.C2LLCodeText.xview)

        self.C2LUpFrame.grid(row=0,column=0)
        self.C2LDownFrame.grid(row=1,column=0)

        self.C2LDLTextFrame.grid(row=0,column=0,rowspan=6)
        self.C2LStartButton.grid(row=2,column=1,sticky=tk.N)
        self.C2LCleanButton.grid(row=4,column=1,sticky=tk.N)
        self.C2LPasteButton.grid(row=1,column=1,sticky=tk.N)
        self.C2LCopyButton.grid(row=3,column=1,sticky=tk.N)
        self.C2LDRTextFrame.grid(row=0,column=2,rowspan=6)

        # self.C2LExLabel.grid(row=0,column=0,sticky=tk.W)
        self.C2LCExLabel.grid(row=1,column=0,sticky=tk.NW)
        self.C2LCExLabel.grid(row=1,column=1)
        self.C2L2Label.grid(row=1,column=2,sticky=tk.W)
        self.C2LLExLabel.grid(row=1,column=3,sticky=tk.W)

        self.C2LCCodeYScr.pack(side=tk.RIGHT, fill=tk.Y)
        self.C2LCCodeXScr.pack(side=tk.BOTTOM, fill=tk.X)
        self.C2LCCodeText.pack()

        self.C2LLCodeYScr.pack(side=tk.RIGHT, fill=tk.Y)
        self.C2LLCodeXScr.pack(side=tk.BOTTOM, fill=tk.X)
        self.C2LLCodeText.pack()

    # C语言命令转Lua函数
    def C2L(self):
        temp = self.C2LCCodeText.get(0.0,tk.END)
        temp = temp.replace(' ', '')
        temp = temp.replace('\t', '')
        temp = temp.replace('{','\t"')
        temp = temp.replace('}','"')
        temp = temp.replace('//','\t\t-- ')

        self.C2LLCodeText.insert(0.0,temp)

    # 清空C2L函数
    def CleanC2L(self):
        self.C2LCCodeText.delete(0.0,tk.END)
        self.C2LLCodeText.delete(0.0,tk.END)

    # 数据库A接口关联代码生成
    def DB_AInterfaceCodeCreate(self):
        try:
            if self.DBAwin.state() == 'normal':
                self.DBAwin.attributes('-topmost', True)
                self.DBAwin.attributes('-topmost', False)
                return
        except:
            self.DBAwin = tk.Toplevel()
            self.DBAwin.title('数据库A接口关联代码生成')
            self.DBAwin.attributes('-topmost',True)
            self.DBAwin.attributes('-topmost',False)

        self.DBConnectFrame = tk.Frame(self.DBAwin,bd=15)
        self.DBAUpFrame = tk.Frame(self.DBAwin)
        self.DBADownFrame = tk.Frame(self.DBAwin,bd=5)

        #登录数据库
        self.DBACIpLabel = tk.Label(self.DBConnectFrame,text='数据库地址:',font=tkFont.Font(size=13))
        self.DBACIpEntry = tk.Entry(self.DBConnectFrame,font=tkFont.Font(size=13),width=16)
        self.DBACUserLabel = tk.Label(self.DBConnectFrame,text='用户名:',font=tkFont.Font(size=13))
        self.DBACUserEntry = tk.Entry(self.DBConnectFrame,font=tkFont.Font(size=13),show='●',width=16)
        self.DBACPassLabel = tk.Label(self.DBConnectFrame,text='密码:',font=tkFont.Font(size=13))
        self.DBACPassEntry = tk.Entry(self.DBConnectFrame,font=tkFont.Font(size=13),show='*',width=16)
        self.DBAConnectButton = tk.Button(self.DBConnectFrame,text='连接',font=tkFont.Font(size=13),width=15,command=self.GetDBADatabase)

        self.DBACDatabaseLabel = tk.Label(self.DBAUpFrame, text='数据库:', font=tkFont.Font(size=13))
        self.DBACDatabaseComBobbox = ttk.Combobox(self.DBAUpFrame, font=tkFont.Font(size=13),width=18,state='readonly')
        self.DBACDatabaseComBobbox['value'] = self.DBADataBaseList
        self.DBACSpaceLabel = tk.Label(self.DBAUpFrame,text=' ')
        self.DBACSpaceLabel1 = tk.Label(self.DBAUpFrame, text=' ')
        self.DBADevCodeLabel = tk.Label(self.DBAUpFrame,text='设备编码:',font=tkFont.Font(size=13))
        self.DBADevCodeEntry = tk.Entry(self.DBAUpFrame,font=tkFont.Font(size=13))
        self.DBADevCodeSureButton = tk.Button(self.DBAUpFrame,text='获取A接口关联代码',command=self.GetA_InterfaceCode,width=18,font=tkFont.Font(size=13))
        self.DBACopyButton = tk.Button(self.DBAUpFrame,text='复制到剪切板',width=15,font=tkFont.Font(size=13),command=lambda :self.copytoplate(self.DBAText))
        self.DBAText = tk.Text(self.DBADownFrame, wrap='none', spacing3=5, width=85, height=20,font=tkFont.Font(size=12),state='disabled')
        self.DBATextScr = tk.Scrollbar(self.DBADownFrame)
        self.DBAText.configure(yscrollcommand=self.DBATextScr.set)
        self.DBATextScr.configure(command=self.DBAText.yview)

        #Frame添加
        self.DBConnectFrame.grid(row=0,column=0,rowspan=2)
        self.DBAUpFrame.grid(row=0,column=1)
        self.DBADownFrame.grid(row=1,column=1)

        #数据库登录添加
        self.row = -1
        self.DBACIpLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.DBACIpEntry.grid(row=self.r(),column=0)
        self.DBACUserLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.DBACUserEntry.grid(row=self.r(),column=0,sticky=tk.W)
        self.DBACPassLabel.grid(row=self.r(),column=0,sticky=tk.W)
        self.DBACPassEntry.grid(row=self.r(),column=0,sticky=tk.W)
        self.DBAConnectButton.grid(row=self.r(),column=0)

        #获取数据添加
        self.DBACDatabaseLabel.grid(row=0, column=0, sticky=tk.W)
        self.DBACSpaceLabel.grid(row=0,column=1)
        self.DBADevCodeLabel.grid(row=0, column=2, sticky=tk.W)
        self.DBACSpaceLabel1.grid(row=0, column=3)
        self.DBACDatabaseComBobbox.grid(row=1, column=0, sticky=tk.W)
        self.DBADevCodeEntry.grid(row=1,column=2,sticky=tk.W)
        self.DBADevCodeSureButton.grid(row=1,column=4)
        self.DBACopyButton.grid(row=1,column=5)
        self.DBATextScr.pack(side=tk.RIGHT,fill=tk.Y)
        self.DBAText.pack()

        # 数据初始化
        self.DBACIpEntry.insert(0,self.DataBaseIP)
        self.DBACUserEntry.insert(0,self.DataBaseUser)
        self.DBACPassEntry.insert(0,self.DataBasePass)
        for i in rootc.colorlist:
            # luaA接口关联代码颜色
            luabox.DBAText.tag_add(i, 1.0, 1.999)
            luabox.DBAText.tag_config(i, foreground=i)

    # 获取数据库
    def GetDBADatabase(self):
        # 打开数据库连接
        db = pymssql.connect(server=self.DBACIpEntry.get(), user=self.DBACUserEntry.get(), password=self.DBACPassEntry.get())
        # 创建游标对象,并设置返回数据的类型为字典
        cursor = db.cursor(as_dict=True)
        # 设置立即操作
        db.autocommit(True)
        # 查看现有数据库
        sql = "SELECT * FROM SYSDATABASES"
        cursor.execute(sql)
        while True:
            msg = cursor.fetchone()
            if msg is None:
                break
            self.DBADataBaseList.append(msg['name'])
        self.DBACDatabaseComBobbox['value'] = self.DBADataBaseList
        self.DBACDatabaseComBobbox.current(0)
        db.close()

    # 获取A接口关联代码
    def GetA_InterfaceCode(self):
        # 打开数据库连接
        db = pymssql.connect(server=self.DBACIpEntry.get(), user=self.DBACUserEntry.get(),
                             password=self.DBACPassEntry.get(),database=self.DBACDatabaseComBobbox.get(),charset="GBK")
        # 创建游标对象,并设置返回数据的类型为字典
        cursor = db.cursor()
        # 设置立即操作
        db.autocommit(True)
        normalsql = r'''DECLARE @smtypecode INT, @sotype INT ,@sosubtype INT
        DECLARE @Cnt INT

        SET @smtypecode = ****

        SELECT @cnt = count(*) FROM SoFormatTable WHERE SmTypeCode = @smtypecode

        IF(@cnt <> 1)
        BEGIN
        	PRINT '存在多个监控对象实例，请手动确认'
        	RETURN
        END

        PRINT 'CONTINUE'

        SELECT @sotype= SoType, @sosubtype = SoSubType FROM SoFormatTable WHERE SmTypeCode = @smtypecode


        CREATE TABLE #WhiteID(StandardID VARCHAR (20) NULL,Cnt INT NULL,NodeIDStr VARCHAR (255) NULL,StandardName	VARCHAR(255) NULL)

        SELECT S.StandardID,T.NodeID,S.StandardName INTO #node FROM StandardDictTable AS S LEFT JOIN (
        SELECT A.SoType,LEFT(StandardID,7) AS TID ,A.NodeID,SensorName AS StandardName,NodeName FROM SensorFormatTable AS A INNER JOIN NodeFormatTable AS B ON
        A.NodeId=B.NodeID WHERE A.SoType=@sotype AND A.SoSubType=@sosubtype AND B.SmTypeCode=@smtypecode AND StandardID IS NOT NULL) AS T
        ON LEFT(S.StandardID,7)= T.TID WHERE S.DeviceType=@sotype ORDER BY S.StandardID

        INSERT INTO #WhiteID SELECT DISTINCT StandardID,0,'',StandardName FROM #node


        UPDATE #WhiteID SET Cnt = b.cnt FROM #WhiteID AS a INNER JOIN
        (SELECT  StandardID,count(*) AS cnt FROM #node WHERE NodeID IS NOT NULL GROUP BY  StandardID) AS b ON a.standardid = b.standardid



        DECLARE @SID varchar(20),@Nid SMALLINT ,@OldSid INT

        SET @OldSid = 0

        DECLARE curID CURSOR FOR
        	SELECT StandardID,NodeID FROM #node WHERE NodeID IS NOT NULL ORDER BY StandardID

        OPEN curID
        FETCH NEXT FROM curID INTO  @SID,@Nid
        WHILE @@FETCH_STATUS = 0
            BEGIN

           		IF @OldSid <> @SID
        	    	UPDATE #WhiteID SET NodeIDStr = NodeIDStr + LTRIM(RTRIM(STR(@Nid)))  WHERE StandardID = @SID
        	    ELSE
        		    UPDATE #WhiteID SET NodeIDStr = NodeIDStr +','+ LTRIM(RTRIM(STR(@Nid)))  WHERE StandardID = @SID

            	SET @OldSid = @SID

                FETCH NEXT FROM curID INTO  @SID,@Nid
            END
        CLOSE curID
        DEALLOCATE curID


        UPDATE #WhiteID SET NodeIDStr = '0' WHERE NodeIDStr = '';
        SELECT '{'+StandardID+','+LTRIM(RTRIM(STR(Cnt)))+',{'+NodeIDStr+'}},			-- '+StandardName FROM  #WhiteID

        GO
        DROP TABLE #node
        DROP TABLE #WhiteID

        '''
        chsql = normalsql.replace('****',self.DBADevCodeEntry.get())
        try:
            cursor.execute(chsql)
            self.DBAText.configure(state='normal')
            self.DBAText.delete(0.0, tk.END)
            while True:
                msg = cursor.fetchone()
                if msg is None:
                    break
                t = msg[0]
                t = '\t"' + t
                t = t.replace('}},', '}}",')
                self.DBAText.insert(tk.END, t + '\n')
            self.DBAText.configure(state='disabled')
            db.close()
        except:
            self.DBAText.configure(state='normal')
            self.DBAText.insert(tk.END,'拉取数据时出错！请检查 数据库 与 设备编码 是否正确！','red')
            self.DBAText.configure(state='disabled')
            db.close()

    # TT.cfg转Lua.GroupType代码
    def TTCfg2LuaGroup(self):
        self.win.attributes('-topmost', False)
        try:
            self.cfgpath = tk.filedialog.askopenfilename(title='打开cfg文件',filetypes=[('cfg File','cfg')])
        except FileNotFoundError as msg:
            print(msg)
        if self.cfgpath == '':
            self.win.attributes('-topmost', True)
            self.win.attributes('-topmost', False)
            return
        cfglist = []
        usecfglist = []
        luagrouptype = ''
        try:
            with open(self.cfgpath,'r',encoding='utf-8') as f:
                line = f.readline()
                while line != '':
                    line = line.replace(' ', '')
                    line = line.replace('\n', '')
                    line = line.replace('\t', '')
                    cfglist.append(line.split(','))
                    line = f.readline()
        except UnicodeDecodeError:
            with open(self.cfgpath,'r',encoding='gbk') as f:
                line = f.readline()
                while line != '':
                    line = line.replace(' ', '')
                    line = line.replace('\n', '')
                    line = line.replace('\t', '')
                    cfglist.append(line.split(','))
                    line = f.readline()
        for i in cfglist:
            if len(i) == 4:
                usecfglist.append(i)
        for i in usecfglist:
            luagrouptype = luagrouptype + '\t"{'+i[0]+','+i[1]+','+i[2]+','+i[3]+',0}",\n'
        self.copytoplate(obj=None,str1=luagrouptype)
        tk.messagebox.showinfo(title='转换成功！',message='转换成功！共 '+str(len(usecfglist))+' 个点'+'\nLua的GroupType代码已经复制到剪切板，请直接前往粘贴！')
        self.win.attributes('-topmost', True)
        self.win.attributes('-topmost', False)

    # 关联ID简视化窗口
    def EasySeeRelationID(self):
        try:
            if self.ESRwin.state() == 'normal':
                self.ESRwin.attributes('-topmost',True)
                self.ESRwin.attributes('-topmost',False)
                return
        except:
            self.ESRwin = tk.Toplevel()
            self.ESRwin.title('关联ID简视化')
            self.ESRwin.attributes('-topmost', True)
            self.ESRwin.attributes('-topmost', False)

        self.ESRUPFrame = tk.Frame(self.ESRwin)
        self.ESRDownFrame = tk.Frame(self.ESRwin)
        self.ESRDownLeftFrame = tk.Frame(self.ESRDownFrame)
        self.ESRDownRightFrame = tk.Frame(self.ESRDownFrame)

        self.RelationIDLabel = tk.Label(self.ESRUPFrame,text='关联ID:\n'
                                                             '"{0416111001,4,{20,40,60,80}}", -- 第XX路A相有功功率Pa\n'
                                                             '"{0416112001,4,{21,41,61,81}}", -- 第XX路B相有功功率Pb\n',
                                        fg='grey')
        self.ESRSpace = tk.Label(self.ESRUPFrame,text='                                                                                      ')
        self.ChangeIDLabel = tk.Label(self.ESRUPFrame,text='转换后：\n先选中所需的ID\n右键复制为备注或复制为代码\n',fg='red',font=tkFont.Font(size=14))

        self.ESRText = tk.Text(self.ESRDownLeftFrame,wrap='none', spacing3=5, width=40, height=20,font=tkFont.Font(size=12))
        self.ESRTExtXScr = tk.Scrollbar(self.ESRDownLeftFrame,orient=tk.HORIZONTAL)
        self.ESRTextYScr = tk.Scrollbar(self.ESRDownLeftFrame)
        self.ESRText.configure(xscrollcommand=self.ESRTExtXScr.set)
        self.ESRText.configure(yscrollcommand=self.ESRTextYScr.set)
        self.ESRTExtXScr.configure(command=self.ESRText.xview)
        self.ESRTextYScr.configure(command=self.ESRText.yview)
        self.ESRPasteButton = tk.Button(self.ESRDownFrame,text='粘贴',font=tkFont.Font(size=12),width=6,command=lambda:self.ESRText.event_generate('<<Paste>>'))
        self.ESRButton = tk.Button(self.ESRDownFrame,text='转换',font=tkFont.Font(size=12),width=6,command=self.EasySeeRelationChange)
        self.ESRCleanButton = tk.Button(self.ESRDownFrame,text='清空',font=tkFont.Font(size=12),width=6,command=self.EasySeeClean)
        self.ESRListBox = tk.Listbox(self.ESRDownRightFrame,width=40,height=23,font=tkFont.Font(size=13),selectbackground='cornflowerblue')
        self.ESRListBoxXScr = tk.Scrollbar(self.ESRDownRightFrame,orient=tk.HORIZONTAL)
        self.ESRListBoxYScr = tk.Scrollbar(self.ESRDownRightFrame)
        self.ESRListBox.configure(xscrollcommand=self.ESRListBoxXScr.set,yscrollcommand=self.ESRListBoxYScr.set)
        self.ESRListBoxYScr.configure(command=self.ESRListBox.yview)
        self.ESRListBoxXScr.configure(command=self.ESRListBox.xview)

        self.ESRUPFrame.grid(row=0,column=0)
        self.ESRDownFrame.grid(row=1,column=0)
        self.ESRDownLeftFrame.grid(row=0,column=0,rowspan=3)
        self.ESRDownRightFrame.grid(row=0,column=2,rowspan=3)

        self.RelationIDLabel.grid(row=0,column=0,sticky=tk.W)
        self.ESRSpace.grid(row=0,column=1,columnspan=3)
        self.ChangeIDLabel.grid(row=0,column=2,sticky=tk.W)

        self.ESRTExtXScr.pack(fill=tk.X,side=tk.BOTTOM)
        self.ESRTextYScr.pack(fill=tk.Y,side=tk.RIGHT)
        self.ESRText.pack()
        self.ESRPasteButton.grid(row=0,column=1,sticky=tk.S)
        self.ESRButton.grid(row=1,column=1)
        self.ESRCleanButton.grid(row=2,column=1,sticky=tk.N)
        self.ESRListBoxXScr.pack(fill=tk.X,side=tk.BOTTOM)
        self.ESRListBoxYScr.pack(fill=tk.Y,side=tk.RIGHT)
        self.ESRListBox.pack()

        self.menu = tk.Menu(self.ESRListBox,tearoff=False)
        self.menu.add_command(label="复制为备注",command=self.CopyIDTip)
        self.menu.add_command(label="复制为PCM_DEV_Get_U8",command=lambda :self.CopyIDTip(type='PCM_DEV_Get_U8'))
        self.menu.add_command(label="复制为PCM_DEV_Get_U16",command=lambda :self.CopyIDTip(type='PCM_DEV_Get_U16'))
        self.menu.add_command(label="复制为PCM_DEV_Get_U32",command=lambda :self.CopyIDTip(type='PCM_DEV_Get_U32'))
        self.menu.add_command(label="复制为PCM_DEV_Get_F32",command=lambda :self.CopyIDTip(type='PCM_DEV_Get_F32'))
        self.menu.add_command(label="复制为PCM_DEV_Get_String",command=lambda :self.CopyIDTip(type='PCM_DEV_Get_String'))
        self.menu.add_command(label="复制为PCM_DEV_Get_SysTime",command=lambda :self.CopyIDTip(type='PCM_DEV_Get_SysTime'))
        self.ESRListBox.bind("<Button-3>",self.ESRPopUp)

    # 关联ID简视化
    def EasySeeRelationChange(self):
        templist = self.ESRText.get(0.0,tk.END).split('\n')
        self.ESRList = []
        for i in range(len(templist)):
            templist[i] = templist[i].split()
        while len(templist[-1]) == 0:
            templist.pop()
        for i in range(len(templist)):
            temp = templist[i][0]
            temp = temp[temp.find(',')+1:]
            temp = temp[temp.find(',')+1:]
            temp = temp.replace('{','')
            temp = temp.replace('}','')
            temp = temp.replace('"','')
            temp = temp.split(',')
            temp.pop()
            for j in temp:
                if j != '0':
                    self.ESRList.append([int(j),templist[i][-1]])
        self.ESRList.sort()
        for i in range(len(self.ESRList)):
            self.ESRList[i][0] = str(self.ESRList[i][0])
        self.ESRListBox.delete(0, tk.END)
        for i in self.ESRList:
            self.ESRListBox.insert(tk.END,"    ".join(i))

    # 关联ID清空
    def EasySeeClean(self):
        self.ESRText.delete(0.0,tk.END)
        self.ESRListBox.delete(0,tk.END)

    # 复制ID备注
    def CopyIDTip(self,type = ''):
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        if type != '':
            temp = 'GroupType['+self.ESRList[self.ESRListBox.curselection()[0]][0]+'] = '\
                   + type+ '(GroupType['+self.ESRList[self.ESRListBox.curselection()[0]][0]+']'\
            +', recvBuf, recvBufLen, DataOffset, RecvData)'
            root.clipboard_append(temp)
        root.clipboard_append('\t-- '+self.ESRList[self.ESRListBox.curselection()[0]][-1])
        root.destroy()

    # 右键弹出
    def ESRPopUp(self,event):
        self.menu.post(event.x_root,event.y_root)

# 一键替换固件升级包类
class OneKeyUpdateSO():
    def __init__(self):
        self.okwin = None
        self.adtwin = None
        self.acwin = None
        self.DevTypeList = ['1  空调','2  电源','3  油机','4  电表','5  其余','6  读卡器']
        self.PathDict = {}
        self.SoPath = ''
        self.FsuPath = ''
        self.Dnum = ''
        self.DName = ''
        self.DType = ''
        self.Other = ''

    # 创建窗口类
    def CreateWin(self):
        try:
            if self.okwin.state() == 'normal':
                self.okwin.attributes('-topmost',True)
                self.okwin.attributes('-topmost',False)
                return
        except:
            self.okwin = tk.Toplevel(rootc.root)
            self.okwin.title('一键替换固件升级包')

        self.okwin.configure(bd=10)

        self.SoFsuFrame = tk.Frame(self.okwin)
        self.SoFsuCCfgLabel = tk.Label(self.SoFsuFrame,text='配置列表:',font=tkFont.Font(size=13))
        self.SoFsuCfgCombobox = ttk.Combobox(self.SoFsuFrame,font=tkFont.Font(size=13),width=25,state='readonly')
        self.SoFsuCfgAddButton = tk.Button(self.SoFsuFrame,text='新增配置',font=tkFont.Font(size=13),command=self.AddFsuSoCFG)
        self.SoFsuCfgDelButton = tk.Button(self.SoFsuFrame,text='删除配置',font=tkFont.Font(size=13),command=self.DelFsuSoCFG)

        self.SoPromptLabel = tk.Label(self.okwin,text='目标文件应为\App\libpm5kpcm.so',fg='red')
        self.SoPathLabel = tk.Label(self.okwin,text='.so文件地址:',font=tkFont.Font(size=13))
        self.SoPathEntry = tk.Entry(self.okwin,width=70,font=tkFont.Font(size=13),state='disabled')
        # self.FindSoPathButton = tk.Button(self.okwin,text='选择文件',width=15,font=tkFont.Font(size=12),command=self.FindSoPath)

        self.FsuPromptLabel = tk.Label(self.okwin,text='\n目标文件夹应包含FsuUpdate、FsuUpdate_old、FsuFirmwareUpdate.sh',fg='red')
        self.FsuPathLabel = tk.Label(self.okwin,text='固件升级包地址:',font=tkFont.Font(size=13))
        self.FsuPathEntry = tk.Entry(self.okwin,width=70,font=tkFont.Font(size=13),state='disabled')
        # self.FindFsuPathButton = tk.Button(self.okwin,text='选择路径',width=15,font=tkFont.Font(size=12),command=self.FindFsuPath)

        self.StateText = tk.Text(self.okwin,width=95,height=7,state='disabled',spacing3=5,bg='whitesmoke',font=tkFont.Font(size=12))

        self.ExecuteFsuButton = tk.Button(self.okwin,text='替换',width=15,font=tkFont.Font(size=12),state='disabled',command=self.ExcuteSOFsu)
        self.AddDeviceTypeButton = tk.Button(self.okwin,text='追加IntelligentDeviceType.txt',font=tkFont.Font(size=12),command=self.AddDeviceType,state='disabled')


        r = 0
        self.SoFsuFrame.grid(row=r,column=0,columnspan=3)

        self.SoFsuCCfgLabel.grid(row=0,column=0)
        self.SoFsuCfgCombobox.grid(row=1, column=0)
        self.SoFsuCfgAddButton.grid(row=1, column=1, sticky=tk.W)
        self.SoFsuCfgDelButton.grid(row=1, column=2, sticky=tk.W)

        r+=1
        self.SoPromptLabel.grid(row=r,column=0,columnspan=3)
        r+=1
        self.SoPathLabel.grid(row=r,column=0)
        self.SoPathEntry.grid(row=r,column=1,columnspan=2,sticky=tk.W)
        # r+=1
        # self.FindSoPathButton.grid(row=r,column=1,sticky=tk.W,pady=10,padx=120)
        r+=1
        self.FsuPromptLabel.grid(row=r,column=0,columnspan=3)
        r+=1
        self.FsuPathLabel.grid(row=r,column=0)
        self.FsuPathEntry.grid(row=r,column=1,columnspan=2,sticky=tk.W)
        # r+=1
        # self.FindFsuPathButton.grid(row=r,column=1,sticky=tk.W,pady=10,padx=120)
        r+=1
        self.StateText.grid(row=r,column=0,columnspan=3)
        r+=1
        self.ExecuteFsuButton.grid(row=r,column=1,sticky=tk.W,pady=10,padx=120)
        r += 1
        self.AddDeviceTypeButton.grid(row=r, column=2, sticky=tk.E)


        # Text框文本插入格式
        self.colorlist = ["red", "green"]
        for i in self.colorlist:
            # 主窗口Text部件颜色
            self.StateText.tag_add(i, 1.0, 1.999)
            self.StateText.tag_config(i, foreground=i)

        # 路径初始化
        if os.path.exists('./src/fsupath.cfg'):
            with open('./src/fsupath.cfg','r',encoding='utf-8') as f:
                while True:
                    cfgname = f.readline().replace('\n','')
                    if cfgname == '':
                        break
                    cfgsopath = f.readline().replace('\n','')
                    cfgfsupath = f.readline().replace('\n','')
                    self.PathDict[cfgname] = [cfgsopath,cfgfsupath]
        self.SoFsuCfgCombobox['value'] = list(self.PathDict.keys())

        self.SoFsuCfgCombobox.bind('<<ComboboxSelected>>',self.ChoiceCfg)
    # 选择配置
    def ChoiceCfg(self,event):
        c = self.SoFsuCfgCombobox.get()
        self.SoPath = self.PathDict[c][0]
        self.FsuPath = self.PathDict[c][1]
        self.FindSoPath(obj=self.SoPathEntry,pt=True)
        self.FindFsuPath(obj=self.FsuPathEntry,pt=True)

    # 新增FSU配置
    def AddFsuSoCFG(self):
        try:
            if self.acwin.state() == 'normal':
                self.acwin.attributes('-topmost',True)
                self.acwin.attributes('-topmost',False)
                return
        except:
            self.acwin = tk.Toplevel(rootc.root)
            self.acwin.title('新增路径配置')

        self.CfgNameLabel = tk.Label(self.acwin,text='配置名称:',font=tkFont.Font(size=13))
        self.CfgNameEntry = tk.Entry(self.acwin,font=tkFont.Font(size=13),width=25)
        self.CfgSoPromptLabel = tk.Label(self.acwin, text='目标文件应为\App\libpm5kpcm.so', fg='red')
        self.CfgSoPathLabel = tk.Label(self.acwin, text='.so文件地址:', font=tkFont.Font(size=13))
        self.CfgSoPathEntry = tk.Entry(self.acwin, width=70, font=tkFont.Font(size=13), state='disabled')
        self.CfgFindSoPathButton = tk.Button(self.acwin,text='选择文件',width=15,font=tkFont.Font(size=12),command= lambda:self.FindSoPath(obj=self.CfgSoPathEntry))
        self.CfgFsuPromptLabel = tk.Label(self.acwin,
                                       text='\n目标文件夹应包含FsuUpdate、FsuUpdate_old、FsuFirmwareUpdate.sh', fg='red')
        self.CfgFsuPathLabel = tk.Label(self.acwin, text='固件升级包地址:', font=tkFont.Font(size=13))
        self.CfgFsuPathEntry = tk.Entry(self.acwin, width=70, font=tkFont.Font(size=13), state='disabled')
        self.CfgFindFsuPathButton = tk.Button(self.acwin,text='选择路径',width=15,font=tkFont.Font(size=12),command= lambda:self.FindFsuPath(obj=self.CfgFsuPathEntry))
        self.CfgSureAddButton = tk.Button(self.acwin,text='确认添加',width=15,font=tkFont.Font(size=12),command=self.SureAddCfg)

        cr = 0
        self.CfgNameLabel.grid(row=cr,column=0)
        self.CfgNameEntry.grid(row=cr,column=1,sticky=tk.W)
        self.CfgSureAddButton.grid(row=cr, column=2)
        cr += 1
        self.CfgSoPromptLabel.grid(row=cr,column=0,columnspan=3)
        cr +=1
        self.CfgSoPathLabel.grid(row=cr,column=0)
        self.CfgSoPathEntry.grid(row=cr,column=1,columnspan=2)
        cr += 1
        self.CfgFindSoPathButton.grid(row=cr,column=1,sticky=tk.W,pady=10,padx=120)
        cr += 1
        self.CfgFsuPromptLabel.grid(row=cr,column=0,columnspan=3)
        cr += 1
        self.CfgFsuPathLabel.grid(row=cr,column=0)
        self.CfgFsuPathEntry.grid(row=cr,column=1,columnspan=2)
        cr += 1
        self.CfgFindFsuPathButton.grid(row=cr,column=1,sticky=tk.W,pady=10,padx=120)

    # 删除FSU配置
    def DelFsuSoCFG(self):
        c = self.SoFsuCfgCombobox.get()
        try:
            self.PathDict.pop(c)
            self.savePath()
            self.SoFsuCfgCombobox['value'] = list(self.PathDict.keys())
            if len(self.PathDict) != 0:
                self.SoFsuCfgCombobox.current(0)
        except:
            pass

    # 确认添加配置
    def SureAddCfg(self):
        CfgName = self.CfgNameEntry.get()
        DevSoPath = self.CfgSoPathEntry.get()
        DevFsuPath = self.CfgFsuPathEntry.get()
        self.PathDict[CfgName] = [DevSoPath,DevFsuPath]
        self.acwin.destroy()
        self.savePath()
        self.SoFsuCfgCombobox['value'] = list(self.PathDict.keys())
        self.SoFsuCfgCombobox.current(0)
        self.okwin.attributes('-topmost',True)
        self.okwin.attributes('-topmost',False)

    # 选择so路径
    def FindSoPath(self,obj,pt=None):
        if pt == None:
            self.SoPath = filedialog.askopenfilename(title='请打开\App\libpm5kpcm.so文件',filetypes=[("SO文件",".so")])
        if self.SoPath[-13:] == 'libpm5kpcm.so':
            obj.configure(state='normal')
            obj.delete(0,tk.END)
            obj.insert(0,self.SoPath)
            obj.configure(state='disabled')
            self.savePath()
        elif self.SoPath == '':
            self.SoPath = ''
            obj.configure(state='normal')
            obj.delete(0, tk.END)
            obj.configure(state='disabled')
        if self.SoPath !='' and self.FsuPath != '':
            self.ExecuteFsuButton.configure(state='normal')
            self.AddDeviceTypeButton.configure(state='normal')
        else:
            self.ExecuteFsuButton.configure(state='disabled')
            self.AddDeviceTypeButton.configure(state='disabled')
        self.okwin.attributes('-topmost', True)
        self.okwin.attributes('-topmost', False)
        if pt == None:
            self.acwin.attributes('-topmost',True)
            self.acwin.attributes('-topmost',False)

    # 选择FsuUpdate路径
    def FindFsuPath(self,obj,pt=None):
        if pt == None:
            self.FsuPath = filedialog.askdirectory(title='请打开FsuFirmwareUpdate.sh所在目录')
        if self.FsuPath != '':
            if os.path.exists(self.FsuPath+'\FsuUpdate'):
                if os.path.exists(self.FsuPath+'\FsuUpdate_old'):
                    if os.path.exists(self.FsuPath+'\FsuFirmwareUpdate.sh'):
                        obj.configure(state='normal')
                        obj.delete(0,tk.END)
                        obj.insert(0,self.FsuPath)
                        obj.configure(state='disabled')
                        self.savePath()
                    else:
                        messagebox.showerror(title='找不到FsuFirmwareUpdate.sh', message='目录中没有FsuFirmwareUpdate.sh!\n请重新选择！')
                else:
                    messagebox.showerror(title='找不到FsuUpdate_old', message='目录中没有FsuUpdate_old!\n请重新选择！')
            else:
                messagebox.showerror(title='找不到FsuUpdate',message='目录中没有FsuUpdate!\n请重新选择！')
        else:
            self.FsuPath = ''
            obj.configure(state='normal')
            obj.delete(0, tk.END)
            obj.configure(state='disabled')
        if self.SoPath != '' and self.FsuPath != '':
            self.ExecuteFsuButton.configure(state='normal')
            self.AddDeviceTypeButton.configure(state='normal')
        else:
            self.ExecuteFsuButton.configure(state='disabled')
            self.AddDeviceTypeButton.configure(state='disabled')
        self.okwin.attributes('-topmost', True)
        self.okwin.attributes('-topmost', False)
        if pt == None:
            self.acwin.attributes('-topmost',True)
            self.acwin.attributes('-topmost',False)

    # 压缩文件
    def do_zip_compress(self,dirpath,lastpath):
        output_name = f"{lastpath}.zip"
        parent_name = os.path.dirname(dirpath)
        zip = zipfile.ZipFile(output_name, "w", zipfile.ZIP_DEFLATED)
        # 多层级压缩
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                if str(file).startswith("~$"):
                    continue
                filepath = os.path.join(root, file)
                writepath = os.path.relpath(filepath, parent_name)
                zip.write(filepath, writepath)
        zip.close()

    # 执行移动操作
    def ExcuteSOFsu(self):
        self.FsuUpdatePath = self.FsuPath
        self.FsuUpdate_oldPath = self.FsuPath
        self.TrueFsuUpdate = ''
        self.TrueFsuUpdate_old = ''
        if os.path.exists(self.FsuUpdatePath+'\FsuUpdate\FsuUpdate'):
            self.FsuUpdatePath = self.FsuUpdatePath+'\FsuUpdate\FsuUpdate\FsuFirmwareUpdate'
            self.TrueFsuUpdate = '\FsuUpdate\FsuUpdate'
        else:
            self.FsuUpdatePath = self.FsuUpdatePath+'\FsuUpdate\FsuFirmwareUpdate'
            self.TrueFsuUpdate = '\FsuUpdate'
        if os.path.exists(self.FsuUpdate_oldPath+'\FsuUpdate_old\FsuUpdate_old'):
            self.FsuUpdate_oldPath = self.FsuUpdate_oldPath+'\FsuUpdate_old\FsuUpdate_old\FsuFirmwareUpdate'
            self.TrueFsuUpdate_old = '\FsuUpdate_old\FsuUpdate_old'
        else:
            self.FsuUpdate_oldPath = self.FsuUpdate_oldPath+'\FsuUpdate_old\FsuFirmwareUpdate'
            self.TrueFsuUpdate_old = '\FsuUpdate_old'
        # 替换
        t = os.path.getmtime(self.SoPath)
        t = time.localtime(t)
        t = time.strftime('%Y-%m-%d %H:%M:%S',t)
        self.StateText.configure(state='normal')
        self.StateText.delete(0.0,tk.END)
        self.StateText.insert(tk.END,'libpm5kpcm.so  最后修改时间:   '+t+'\n','green')
        try:
            shutil.copy(self.SoPath,self.FsuUpdatePath)
            self.StateText.insert(tk.END,self.FsuUpdatePath+'\n\t 替换成功!\n','green')
        except:
            self.StateText.insert(tk.END,self.FsuUpdatePath+'\n\t 替换失败!\n','red')
        try:
            shutil.copy(self.SoPath,self.FsuUpdate_oldPath)
            self.StateText.insert(tk.END, self.FsuUpdate_oldPath + '\n\t 替换成功!\n','green')
        except:
            self.StateText.insert(tk.END,self.FsuUpdate_oldPath+'\n\t 替换失败!\n','red')
        try:
            self.do_zip_compress(self.FsuPath+self.TrueFsuUpdate,self.FsuPath+'\FsuUpdate')
            self.StateText.insert(tk.END, 'FsuUpdate 压缩成功!\n', 'green')
        except:
            self.StateText.insert(tk.END,'FsuUpdate 压缩失败!\n','red')
        try:
            self.do_zip_compress(self.FsuPath+self.TrueFsuUpdate_old,self.FsuPath+'\FsuUpdate_old')
            self.StateText.insert(tk.END, 'FsuUpdate_old 压缩成功!\n','green')
        except:
            self.StateText.insert(tk.END,'FsuUpdate_old 压缩失败!\n','red')

        self.StateText.configure(state='disabled')

    # 保存操作路径到文本中
    def savePath(self):
        with open('./src/fsupath.cfg', 'w', encoding='utf-8') as f:
            for i in self.PathDict.keys():
                f.write(i+'\n')
                f.write(self.PathDict[i][0] + '\n')
                f.write(self.PathDict[i][1] + '\n')

    # 追加IntelligentDeviceType.txt
    def AddDeviceType(self):
        try:
            if self.adtwin.state() == 'normal':
                self.adtwin.attributes('-topmost',True)
                self.adtwin.attributes('-topmost',False)
                return
        except:
            self.adtwin = tk.Toplevel(rootc.root)
            self.adtwin.title('追加IntelligentDeviceType.txt')

        self.adtwin.configure(bd=10)

        self.DevNumLabel = tk.Label(self.adtwin,text='设备编号:',font=tkFont.Font(size=12))
        self.DevNameLabel = tk.Label(self.adtwin,text='设备名称:',font=tkFont.Font(size=12))
        self.DevTypeLabel = tk.Label(self.adtwin,text='设备类型:',font=tkFont.Font(size=12))

        self.DevNumEntry = tk.Entry(self.adtwin,font=tkFont.Font(size=12),width=15)
        self.DevNameEntry = tk.Entry(self.adtwin,font=tkFont.Font(size=12),width=25)
        self.DevTypeCombobox = ttk.Combobox(self.adtwin,state='readonly',font=tkFont.Font(size=12),width=20)
        self.DevTypeCombobox['value'] = self.DevTypeList
        self.DevTypeCombobox.current(0)

        self.OtherLabel = tk.Label(self.adtwin,text='PollTime,PollTimeOut,DownAddr,PortConfig,SpecialOption(逗号间隔，一般不做修改)',font=tkFont.Font(size=12))
        self.OtherEntry = tk.Entry(self.adtwin,font=tkFont.Font(size=12),width=40)

        self.ShowAddCodeLabel = tk.Label(self.adtwin,text='生成语句预览:',font=tkFont.Font(size=12))
        self.ShowAddTitleLabel = tk.Label(self.adtwin,text="Type\tDescription\tClass\t其它参数",font=tkFont.Font(size=12))
        self.ShowAddCodeText = tk.Text(self.adtwin,width=80,height=2,wrap='none',font=tkFont.Font(size=12),bg='whitesmoke',state='disabled')
        self.SureAddButton = tk.Button(self.adtwin, text='一键追加',font=tkFont.Font(size=12),command=self.AddToTxt)

        rb = 0
        self.DevNumLabel.grid(row=rb,column=0,sticky=tk.W)
        self.DevNameLabel.grid(row=rb,column=1,sticky=tk.W)
        self.DevTypeLabel.grid(row=rb,column=2,sticky=tk.W)
        rb += 1
        self.DevNumEntry.grid(row=rb,column=0,sticky=tk.W)
        self.DevNameEntry.grid(row=rb,column=1,sticky=tk.W)
        self.DevTypeCombobox.grid(row=rb,column=2,sticky=tk.W)
        rb += 1
        self.OtherLabel.grid(row=rb,column=0,columnspan=3,sticky=tk.W)
        rb += 1
        self.OtherEntry.grid(row=rb,column=0,columnspan=3,sticky=tk.W)
        rb += 1
        self.ShowAddCodeLabel.grid(row=rb,column=0,sticky=tk.W)
        rb += 1
        self.ShowAddTitleLabel.grid(row=rb, column=0, columnspan=3,sticky=tk.W)
        rb += 1
        self.ShowAddCodeText.grid(row=rb,column=0,columnspan=3)
        rb += 1
        self.SureAddButton.grid(row=rb,column=1)

        # 信息初始化
        self.OtherEntry.insert(0,'1000,7500,1,4,NULL')

        # 添加动态显示线程
        dth = threading.Thread(target=self.DynamicShow,args=())
        dth.daemon = True
        dth.start()

    # 追加到文本中
    def AddToTxt(self):
        self.FsuUpdatePath = self.FsuPath
        self.FsuUpdate_oldPath = self.FsuPath

        if os.path.exists(self.FsuUpdatePath + '\FsuUpdate\FsuUpdate'):
            self.FsuUpdatePath = self.FsuUpdatePath + '\FsuUpdate\FsuUpdate\FsuFirmwareUpdate'
        else:
            self.FsuUpdatePath = self.FsuUpdatePath + '\FsuUpdate\FsuFirmwareUpdate'
        if os.path.exists(self.FsuUpdate_oldPath + '\FsuUpdate_old\FsuUpdate_old'):
            self.FsuUpdate_oldPath = self.FsuUpdate_oldPath + '\FsuUpdate_old\FsuUpdate_old\FsuFirmwareUpdate'
        else:
            self.FsuUpdate_oldPath = self.FsuUpdate_oldPath + '\FsuUpdate_old\FsuFirmwareUpdate'

        self.adtwin.destroy()
        self.StateText.configure(state='normal')
        self.StateText.delete(0.0, tk.END)
        try:
            with open(self.FsuUpdatePath+'\IntelligentDeviceType.txt','a',encoding='gbk') as f:
                f.write('\n'+self.dyst)
            self.StateText.insert(tk.END,'FsuUpdate\IntelligentDeviceType.txt 追加设备成功! \n','green')
        except:
            self.StateText.insert(tk.END, 'FsuUpdate\IntelligentDeviceType.txt 追加设备失败! \n', 'red')
        try:
            with open(self.FsuUpdate_oldPath+'\IntelligentDeviceType.txt','a',encoding='gbk') as f:
                f.write('\n'+self.dyst)
            self.StateText.insert(tk.END,'FsuUpdate_old\IntelligentDeviceType.txt 追加设备成功! ','green')
        except:
            self.StateText.insert(tk.END, 'FsuUpdate_old\IntelligentDeviceType.txt 追加设备失败! ', 'red')
        self.StateText.configure(state='disabled')

    # 动态显示
    def DynamicShow(self):
        try:
            while self.adtwin.state() == 'normal':
                self.Dnum = self.DevNumEntry.get()
                self.DName = self.DevNameEntry.get()
                if self.Dnum != '' and self.DName != '':
                    self.DType = self.DevTypeCombobox.get()[:1]
                    self.Other = self.OtherEntry.get().split(',')
                    self.dyst = "{0}\t{1}\t\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(self.Dnum,self.DName,self.DType,self.Other[0],self.Other[1],self.Other[2],self.Other[3],self.Other[4])
                    self.ShowAddCodeText.configure(state='normal')
                    self.ShowAddCodeText.delete(0.0,tk.END)
                    self.ShowAddCodeText.insert(tk.END,self.dyst)
                    self.ShowAddCodeText.configure(state='disabled')
                else:
                    time.sleep(1)
                    continue
                time.sleep(1)
        except:
            pass

# 主窗口类
class Root():
    def __init__(self):
        # 初始化
        public.initCFG()
        self.root = tk.Tk()
        self.LeftFrame = tk.Frame(self.root, highlightthickness=2, bd=5, padx=20)
        self.RightFrame = tk.Frame(self.root, highlightbackground='white', highlightthickness=2)
        self.RightFrame_Up = tk.Frame( self.RightFrame, highlightthickness=2, bd=5)
        self.RightFrame_Down = tk.Frame( self.RightFrame, highlightthickness=2, bd=5)

        self.ProtocolTypeLabel = tk.Label( self.LeftFrame, text='协议类型', font=tkFont.Font(size=13,weight='bold'))
        self.ProtocolTypeCombobox = ttk.Combobox( self.LeftFrame, width=22,state='readonly')
        self.ProtocolTypeCombobox['value'] = public.ProtocolTypeList
        self.ProtocolTypeCombobox.current(0)
        self.IPAddressLabel = tk.Label( self.LeftFrame, text='IP地址', font=tkFont.Font(size=13,weight='bold'))
        self.IpCombobox = ttk.Combobox( self.LeftFrame, width=22)
        self.IpCombobox['value'] = public.localIPList
        self.IpCombobox.current(len(public.localIPList) - 1)
        self.IPPortLabel = tk.Label( self.LeftFrame, text='服务端口', font=tkFont.Font(size=13,weight='bold'))
        self.IPPortCombobox = ttk.Combobox( self.LeftFrame, width=22)
        self.IPPortCombobox['value'] = public.PortList
        self.IPPortCombobox.current(len(public.PortList) - 1)

        self.StartRecvButton = tk.Button( self.LeftFrame, text='打开端口',command=modbustcp.socket_TCPserviceth)
        self.CleanRecvButton = tk.Button( self.LeftFrame, text='清空数据',command=public.cleanRecvinfoth)

        self.KeyLabel = tk.Label(self.LeftFrame,text='日志关键字',font=tkFont.Font(size=13,weight='bold'),fg='darkmagenta')
        self.udpKeyEntry = tk.Entry(self.LeftFrame,width=25)
        self.SmartSendLabel = tk.Label( self.LeftFrame, text='智能回包', font=tkFont.Font(size=13,weight='bold'),fg='green')
        self.SmartsendRoleButton = tk.Button(self.LeftFrame, text='智能回包规则', font=tkFont.Font(size=13),width=15,command=smartrole.CreateWindow)
        self.SmartSendStateLabel = tk.Label( self.LeftFrame, text='状态：未启用', font=tkFont.Font(size=10),fg='red')
        self.SmartSendButton = tk.Button( self.LeftFrame, text='开启', width=10,command=modbustcp.smartsendinfo)

        self.FunctionLabel = tk.Label(self.LeftFrame,text='扩展功能',font=tkFont.Font(size=13,weight='bold'),fg='royalblue')
        self.CRCButton = tk.Button(self.LeftFrame, text='CRC校验', width=17, font=tkFont.Font(size=13),command=crc.createwindos)
        self.Txt2NodeCodeButton = tk.Button(self.LeftFrame,text='txt转DATAINFO',width=17, font=tkFont.Font(size=13),command=t2n.CreateWin)
        self.Txt2Xlx2CfgButton = tk.Button(self.LeftFrame, text='txt转xlx及cfg', width=17, font=tkFont.Font(size=13),
                                           command=t2x2c.txt2xlx2cfgroot)
        self.ConfigCFG = tk.Button(self.LeftFrame, text='设置常用IP地址',width=17,font=tkFont.Font(size=13),command=cfgc.CreateWin)
        self.LuaWhiteBoxButton = tk.Button(self.LeftFrame,text='白盒化Lua工具',width=17,font=tkFont.Font(size=13),command=luabox.CreateWin)
        self.OneKeyUpdateButton = tk.Button(self.LeftFrame, text='一键替换固件升级包', width=17, font=tkFont.Font(size=13),command=okupdt.CreateWin)


        self.Version = tk.Label(self.LeftFrame,text=public.Auther,fg='grey')

        self.ShowRecvText = tk.Text(self.RightFrame_Up, wrap='word', spacing3=5, width=105, height=25,font=tkFont.Font(size=12),state='disabled')
        self.ShowRecvTextsbar = tk.Scrollbar(self.RightFrame_Up)
        self.ShowRecvText.configure(yscrollcommand=self.ShowRecvTextsbar.set)
        self.ShowRecvTextsbar.config(command=self.ShowRecvText.yview)
        self.SendText = tk.Text(self.RightFrame_Down, wrap='word', spacing3=5, width=96, height=5,font=tkFont.Font(size=12))
        self.SendTextButton = tk.Button(self.RightFrame_Down, text='发送', width=10, height=3,command=modbustcp.sendinfo)
        self.CleanTextButton = tk.Button(self.RightFrame_Down, text='清空', width=10,command=public.cleanSendinfoth)

    def CreateWindows(self):
        self.root.title('协议编写调试工具')


        srow = 0
        # Frame
        self.LeftFrame.grid(row=0, column=0,sticky=tk.N)
        self.RightFrame.grid(row=0, column=1)
        self.RightFrame_Up.grid(row=0, column=0)
        self.RightFrame_Down.grid(row=1, column=0)

        self.SpaceLabelTop = tk.Label(self.LeftFrame, text='-------------------------------------', height=1, fg='grey')
        self.SpaceLabelTop.grid(row=srow, column=0, columnspan=3)
        # 左上选择框
        srow += 1
        self.ProtocolTypeLabel.grid(row=srow, column=0)
        srow+=1
        self.ProtocolTypeCombobox.grid(row=srow, column=0, columnspan=2)
        srow+=1
        self.IPAddressLabel.grid(row=srow, column=0)
        srow+=1
        self.IpCombobox.grid(row=srow, column=0, columnspan=2)
        srow+=1
        self.IPPortLabel.grid(row=srow, column=0)
        srow+=1
        self.IPPortCombobox.grid(row=srow, column=0, columnspan=2)
        srow+=1
        self.StartRecvButton.grid(row=srow, column=0)
        self.CleanRecvButton.grid(row=srow, column=1)
        srow += 1
        self.SpaceLabel1 = tk.Label(self.LeftFrame, text='-------------------------------------', height=1, fg='grey')
        self.SpaceLabel1.grid(row=srow, column=0, columnspan=3)

        # 关键字
        srow += 1
        self.KeyLabel.grid(row=srow, column=0,sticky=tk.W)
        srow += 1
        self.udpKeyEntry.grid(row=srow, column=0, columnspan=2)
        srow += 1
        self.SpaceLabel2 = tk.Label(self.LeftFrame,text='-------------------------------------', height=1,fg='grey')
        self.SpaceLabel2.grid(row=srow, column=0,columnspan=3)
        srow += 1
        # 智能回包
        srow+=1
        self.SmartSendLabel.grid(row=srow, column=0,sticky=tk.W)
        srow+=1
        self.SmartsendRoleButton.grid(row=srow,column=0,columnspan=2)
        srow+=1
        self.SmartSendStateLabel.grid(row=srow, column=0)
        srow+=1
        self.SmartSendButton.grid(row=srow, column=0, columnspan=2)
        srow+=1
        self.SpaceLabel3 = tk.Label(self.LeftFrame,text='-------------------------------------', height=1,fg='grey')
        self.SpaceLabel3.grid(row=srow, column=0,columnspan=3)
        # 功能扩展区
        srow+=1
        self.FunctionLabel.grid(row=srow,column=0,sticky=tk.W)
        srow+=1
        self.CRCButton.grid(row=srow, column=0, columnspan=2)
        srow+=1
        self.Txt2NodeCodeButton.grid(row=srow,column=0,columnspan=2)
        srow += 1
        self.Txt2Xlx2CfgButton.grid(row=srow,column=0,columnspan=2)
        srow += 1
        self.LuaWhiteBoxButton.grid(row=srow, column=0, columnspan=2)
        srow += 1
        self.OneKeyUpdateButton.grid(row=srow, column=0, columnspan=2)
        srow+=1
        self.ConfigCFG.grid(row=srow, column=0, columnspan=2)
        srow+=1
        self.SpaceLabel4 = tk.Label(self.LeftFrame, text='-------------------------------------', height=1, fg='grey')
        self.SpaceLabel4.grid(row=srow, column=0, columnspan=3)

        srow+=1
        self.Version.grid(row=srow,column=0,columnspan=3,sticky=tk.E)


        self.ShowRecvTextsbar.grid(row=0, column=1)
        self.ShowRecvTextsbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ShowRecvText.pack(fill=tk.X)
        self.SendText.grid(row=1, column=1, rowspan=4)
        self.SendTextButton.grid(row=1, column=2, rowspan=2)
        self.CleanTextButton.grid(row=3, column=2)

        # 绑定下拉框动作
        self.ProtocolTypeCombobox.bind('<<ComboboxSelected>>', public.protocoltypechange)
        # 初始不能使用udp关键字窗口
        rootc.udpKeyEntry.configure(state='disabled')

        # Text框文本插入格式
        self.colorlist = ["red", "grey", "blue"]
        for i in self.colorlist:
            # 主窗口Text部件颜色
            self.ShowRecvText.tag_add(i,1.0,1.999)
            self.ShowRecvText.tag_config(i,foreground=i)


#公用类
class Public():
    def __init__(self):
        self.tcpcconn = None
        self.tth = None
        self.recvinfo = None
        self.CurrentProtocol = None
        self.ComList = ['COM1','COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9','COM10','COM11','COM12','COM13',
                        'COM14','COM15','COM16','COM17','COM18','COM19','COM20','COM21','COM22','COM23','COM24','COM25',
                        'COM26','COM27','COM28','COM29','COM30','COM31','COM32']
        self.PortList = []
        self.ProtocolTypeList = ['TCP服务器(MODBUS-TCP)','网络串口调试(电总,MODBUS)','设备日志(UDP)','TCP客户端']
        self.localIPList = []    #本机ip
        self.IfStartListen = False
        self.IfStartSmart = False
        self.IfGetInfo = False
        self.IfSendSmartInfo = False

        self.Auther = 'V1.2\tAuther by Zx'

    # 初始化常用List
    def initCFG(self):
        ifinit = os.path.isfile('./src/config.cfg')
        self.localIPList = []
        self.PortList = []
        if not ifinit:
            with open("./src/config.cfg","w") as f:
                f.write("[IP]\n")
                temp = socket.gethostbyname_ex(socket.gethostname())[2]
                for i in temp:
                    f.write(i+'\n')
                f.write("[Port]\n")
                f.write('502'+'\n')
        with open("./src/config.cfg","r") as f:
            line = f.readline().strip()
            if line == '[IP]':
                while line != '':
                    line = f.readline().strip()
                    if line == '[Port]':
                        break
                    self.localIPList.append(line)
                while line != '':
                    if line == '[Port]':
                        line = f.readline().strip()
                    self.PortList.append(int(line))
                    line = f.readline().strip()

    # 协议类型下拉框回调函数
    def protocoltypechange(self,event):
        if rootc.ProtocolTypeCombobox.get() == public.ProtocolTypeList[0]:#TCP服务器
            #端口
            rootc.IPPortCombobox['value'] = self.PortList
            rootc.IPPortCombobox.current(len(self.PortList) - 1)
            #按钮
            rootc.StartRecvButton.configure(command=modbustcp.socket_TCPserviceth)
            rootc.SendTextButton.configure(command=modbustcp.sendinfo)
            rootc.SmartSendButton.configure(command=modbustcp.smartsendinfo)
            #输入
            rootc.udpKeyEntry.configure(state='disabled')
            rootc.SmartSendButton.configure(state='normal')
        elif rootc.ProtocolTypeCombobox.get() == public.ProtocolTypeList[1]:#串口工具
            #串口
            rootc.IPPortCombobox['value'] = self.ComList
            rootc.IPPortCombobox.current(2)
            #按钮
            rootc.StartRecvButton.configure(command=com.StartCom)
            rootc.SendTextButton.configure(command=com.sendinfo)
            rootc.SmartSendButton.configure(command=com.smartsendinfo)
            #输入
            rootc.udpKeyEntry.configure(state='disabled')
            rootc.SmartSendButton.configure(state='normal')
        elif rootc.ProtocolTypeCombobox.get() == public.ProtocolTypeList[2]:#udp
            #端口
            rootc.IPPortCombobox['value'] = self.PortList
            rootc.IPPortCombobox.current(len(self.PortList) - 1)
            #按钮
            rootc.StartRecvButton.configure(command=udplog.startIP)
            rootc.SendTextButton.configure(command=...)
            rootc.SmartSendButton.configure(command=...)
            #输入
            rootc.udpKeyEntry.configure(state='normal')
            rootc.SmartSendButton.configure(state='disabled')

        elif rootc.ProtocolTypeCombobox.get() == public.ProtocolTypeList[3]:#tcp客户端
            #端口
            rootc.IPPortCombobox['value'] = self.PortList
            rootc.IPPortCombobox.current(len(self.PortList) - 1)
            #按钮
            rootc.StartRecvButton.configure(command=tcpcliect.StartTcp)
            rootc.SendTextButton.configure(command=tcpcliect.sendinfo)
            rootc.SmartSendButton.configure(command=...)
            #输入
            rootc.udpKeyEntry.configure(state='disabled')
            rootc.SmartSendButton.configure(state='disabled')

    # Bytes转成文本列表
    def Bytes2Str(self, bytes):
        str1 = bytes.hex()
        cmdlist = []
        for i in range(0, len(str1), 2):
            if i < len(str1):
                cmdlist.append((str1[i] + str1[i + 1]).upper())
        # 返回文本和列表
        return " ".join(cmdlist), cmdlist

    # 文本转Bytes
    def Str2Bytes(self, str1):
        if ',' in str1:
            str2 = str1.split(',')
        else:
            str2 = str1.split()
        str3 = "".join(str2)
        b = binascii.a2b_hex(str3)
        # 返回发包和包列表
        return b, str2

    # 清空输出区的数据
    def cleanRecvinfoth(self):
        rootc.ShowRecvText.configure(state='normal')
        rootc.ShowRecvText.delete(0.0, tk.END)
        rootc.ShowRecvText.configure(state='disabled')

    # 清空输入区的数据
    def cleanSendinfoth(self):
        rootc.SendText.configure(state='normal')
        rootc.SendText.delete(0.0,tk.END)
        rootc.ShowRecvText.configure(state='disabled')

    # 复制到剪切板
    def copytoplate(self,obj,str1=None):
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        if str1 == None:
            t = obj.get(0.0,tk.END)
        else:
            t = str1
        root.clipboard_append(t)
        root.destroy()

public = Public()
udplog = Udplog()
modbustcp = ModbusTcp()
tcpcliect = TcpCliect()
smartrole = SmartRole()
crc = CrcCheck()
t2x2c = Txt2Xlx2Cfg()
t2n = Txt2NodeCode()
com = ComATcp()
cfgc = ConfigCFGC()
luabox = WbLuaTool()
okupdt = OneKeyUpdateSO()
rootc = Root()
rootc.CreateWindows()
rootc.root.mainloop()


