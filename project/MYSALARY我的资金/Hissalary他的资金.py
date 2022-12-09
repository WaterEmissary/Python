import tkinter as tk
import tkinter.font
import tkinter.ttk as ttk
import tkinter.messagebox
import threading
from time import sleep

import pymysql

# 软件界面模块
class MSWin:
    def __init__(self):
        # 数据记录
        self.CanUseSalaryDict = {}
        self.FlexibleCapitalDict = {}
        self.LockedCapitalDict = {}
        # 操作记录
        self.CanUseHisDict = {}
        self.FlexibleHisDict = {}
        self.LockedHisDict = {}
        # 历史记录汇总
        self.CanUseGetDict = {}
        self.FlexibleGetDict = {}
        self.LockedGetDict = {}


        self.CurrectListBox = None
        self.CurrectData = None

        self.updwin = None
        self.addwin = None

        self.CUSSum = 0
        self.FBCSum = 0
        self.LKCSum = 0

        self.tableDict = {'canusesalary': ['可用资金','canusehistory'], 'flexiblecapital': ['灵活资金','flexiblehistory'], 'lockedcapital': ['锁定资金','lockedhistory']}


    # 创建窗口
    def CreateWin(self):
        self.mswin = tk.Tk()
        self.mswin.title('资产汇总')

        # 头部信息定义
        self.headFrame = tk.Frame(self.mswin)
        self.ConnectStateFrame = tk.Frame(self.headFrame,bd=5)
        self.MysqlConnectStateLabel = tk.Label(self.ConnectStateFrame,text='ConnectState:')
        self.MysqlConnectStateInfoLabel = tk.Label(self.ConnectStateFrame,text='未连接',fg='red')
        self.InitOpStateLabel = tk.Label(self.ConnectStateFrame,text='\tInitState:')
        self.InitOpInfoLabel = tk.Label(self.ConnectStateFrame,text='未完成',fg='red')
        self.CaluHisLabel = tk.Label(self.ConnectStateFrame,text='\tCaluState:')
        self.CaluHisInfoLabel = tk.Label(self.ConnectStateFrame,text='未完成',fg='red')
        self.CUSLabel = tk.Label(self.headFrame,text='可用资金:\t    ',font=tk.font.Font(size=13))
        self.FBCLabel = tk.Label(self.headFrame,text='灵活资金:\t    ',font=tk.font.Font(size=13))
        self.LKCLabel = tk.Label(self.headFrame,text='锁定资金:',font=tk.font.Font(size=13))

        # 资产信息定义
        self.CapitalFrame = tk.Frame(self.mswin,bd=5)
        self.CUSListBoxFrame = tk.Frame(self.CapitalFrame)
        self.FBCListBoxFrame = tk.Frame(self.CapitalFrame)
        self.LKCListBoxFrame = tk.Frame(self.CapitalFrame)

        self.CUSListBox = tk.Listbox(self.CUSListBoxFrame,font=tk.font.Font(size=13),selectbackground='slateblue')
        self.FBCListBox = tk.Listbox(self.FBCListBoxFrame,font=tk.font.Font(size=13),selectbackground='slateblue')
        self.LKCListBox = tk.Listbox(self.LKCListBoxFrame,font=tk.font.Font(size=13),selectbackground='slateblue')

        self.CUSSumLabel = tk.Label(self.CapitalFrame,text='总计:',font=tk.font.Font(size=13))
        self.CUSSumInfoLabel = tk.Label(self.CapitalFrame,text='',font=tk.font.Font(size=13))
        self.FBCSumLabel = tk.Label(self.CapitalFrame, text='总计:',font=tk.font.Font(size=13))
        self.FBCSumInfoLabel = tk.Label(self.CapitalFrame, text='',font=tk.font.Font(size=13))
        self.LKCSumLabel = tk.Label(self.CapitalFrame, text='总计:',font=tk.font.Font(size=13))
        self.LKCSumInfoLabel = tk.Label(self.CapitalFrame, text='',font=tk.font.Font(size=13))

        # 其它信息定义
        self.DataInfoFrame = tk.Frame(self.mswin,bd=5)
        self.CurrentTableLabel = tk.Label(self.DataInfoFrame,text='当前选中表:',font=tk.font.Font(size=13),fg='blue')
        self.CurrentTableInfoLabel = tk.Label(self.DataInfoFrame,text='未选择',font=tk.font.Font(size=13),fg='blue')
        self.CurrentDataLabel = tk.Label(self.DataInfoFrame,text='当前选中数据:',font=tk.font.Font(size=13),fg='cornflowerblue')
        self.CurrentDataInfoLabel = tk.Label(self.DataInfoFrame,text='未选择',font=tk.font.Font(size=13),fg='cornflowerblue')
        self.ALLSumLabel = tk.Label(self.DataInfoFrame,text='全部总计:',font=tk.font.Font(size=13),fg='lightcoral')
        self.ALLSumInfoLabel = tk.Label(self.DataInfoFrame,text='',font=tk.font.Font(size=13),fg='lightcoral')
        self.CanUseSumLabel = tk.Label(self.DataInfoFrame,text='可用总计:',font=tk.font.Font(size=13),fg='indianred')
        self.CanUseSumInfoLabel = tk.Label(self.DataInfoFrame,text='',font=tk.font.Font(size=13),fg='indianred')

        self.CurrentTableS7Label = tk.Label(self.DataInfoFrame,text='选中表7天收入:',font=tk.font.Font(size=13),fg='red')
        self.CurrentTablleS7InfoLabel = tk.Label(self.DataInfoFrame,text='',font=tk.font.Font(size=13),fg='red')
        self.CurrentTableM7Label = tk.Label(self.DataInfoFrame, text='选中表7天支出:', font=tk.font.Font(size=13),fg='green')
        self.CurrentTablleM7InfoLabel = tk.Label(self.DataInfoFrame, text='',font=tk.font.Font(size=13),fg='green')
        self.CurrentTable7Label = tk.Label(self.DataInfoFrame,text='选中表7天净值:',font=tk.font.Font(size=13),fg='slateblue')
        self.CurrentTable7InfoLabel = tk.Label(self.DataInfoFrame,text='',font=tk.font.Font(size=13),fg='slateblue')
        self.CurrentTableS30Label = tk.Label(self.DataInfoFrame, text='选中表30天收入:', font=tk.font.Font(size=13),fg='red')
        self.CurrentTablleS30InfoLabel = tk.Label(self.DataInfoFrame, text='', font=tk.font.Font(size=13),fg='red')
        self.CurrentTableM30Label = tk.Label(self.DataInfoFrame, text='选中表30天支出:', font=tk.font.Font(size=13),fg='green')
        self.CurrentTablleM30InfoLabel = tk.Label(self.DataInfoFrame, text='', font=tk.font.Font(size=13),fg='green')
        self.CurrentTable30Label = tk.Label(self.DataInfoFrame, text='选中表30天净值:', font=tk.font.Font(size=13),fg='slateblue')
        self.CurrentTable30InfoLabel = tk.Label(self.DataInfoFrame, text='', font=tk.font.Font(size=13),fg='slateblue')


        self.CurrentDataS7Label = tk.Label(self.DataInfoFrame, text='选中项7天收入:', font=tk.font.Font(size=13),fg='red')
        self.CurrentDataS7InfoLabel = tk.Label(self.DataInfoFrame, text='', font=tk.font.Font(size=13),fg='red')
        self.CurrentDataM7Label = tk.Label(self.DataInfoFrame, text='选中项7天支出:', font=tk.font.Font(size=13),fg='green')
        self.CurrentDataM7InfoLabel = tk.Label(self.DataInfoFrame, text='', font=tk.font.Font(size=13),fg='green')
        self.CurrentData7Label = tk.Label(self.DataInfoFrame, text='选中项7天净值:', font=tk.font.Font(size=13),fg='slateblue')
        self.CurrentData7InfoLabel = tk.Label(self.DataInfoFrame, text='', font=tk.font.Font(size=13),fg='slateblue')
        self.CurrentDataS30Label = tk.Label(self.DataInfoFrame, text='选中项30天收入:', font=tk.font.Font(size=13),fg='red')
        self.CurrentDataS30InfoLabel = tk.Label(self.DataInfoFrame, text='', font=tk.font.Font(size=13),fg='red')
        self.CurrentDataM30Label = tk.Label(self.DataInfoFrame, text='选中项30天支出:', font=tk.font.Font(size=13),fg='green')
        self.CurrentDataM30InfoLabel = tk.Label(self.DataInfoFrame, text='', font=tk.font.Font(size=13),fg='green')
        self.CurrentData30Label = tk.Label(self.DataInfoFrame, text='选中项30天净值:', font=tk.font.Font(size=13),fg='slateblue')
        self.CurrentData30InfoLabel = tk.Label(self.DataInfoFrame, text='', font=tk.font.Font(size=13),fg='slateblue')

        # 功能区
        self.FunctionFrame = tk.Frame(self.mswin,bd=5)
        self.CreateNewCapitalButton = tk.Button(self.FunctionFrame,text='新建资金',command=self.Addwin, font=tk.font.Font(size=13),width=15)
        self.UpdateCaptialButton = tk.Button(self.FunctionFrame,text='修改资金',command=self.Updatewin, font=tk.font.Font(size=13),width=15)
        self.DelCaptialButton = tk.Button(self.FunctionFrame,text='删除资金',command=self.DelC, font=tk.font.Font(size=13),width=15)


        # 显示到屏幕
        self.headFrame.grid(row=0,column=0,sticky=tk.W)
        self.CapitalFrame.grid(row=1,column=0)
        self.DataInfoFrame.grid(row=2,column=0,columnspan=2,sticky=tk.W)
        self.FunctionFrame.grid(row=0,column=1,rowspan=2)
            # 头部信息
        self.ConnectStateFrame.grid(row=0, columnspan=3, sticky=tk.W)
        self.MysqlConnectStateLabel.grid(row=0,column=0,sticky=tk.W)
        self.MysqlConnectStateInfoLabel.grid(row=0,column=1,sticky=tk.W)
        self.InitOpStateLabel.grid(row=0,column=2,sticky=tk.W)
        self.InitOpInfoLabel.grid(row=0,column=3,sticky=tk.W)
        self.CaluHisLabel.grid(row=0,column=4,sticky=tk.W)
        self.CaluHisInfoLabel.grid(row=0,column=5,sticky=tk.W)
        self.CUSLabel.grid(row=1,column=0,sticky=tk.W)
        self.FBCLabel.grid(row=1,column=1,sticky=tk.W)
        self.LKCLabel.grid(row=1,column=2,sticky=tk.W)
            # 资产信息
        self.CUSListBoxFrame.grid(row=0,column=0,columnspan=2)
        self.FBCListBoxFrame.grid(row=0,column=2,columnspan=2)
        self.LKCListBoxFrame.grid(row=0,column=4,columnspan=2)

        self.CUSListBox.pack()
        self.FBCListBox.pack()
        self.LKCListBox.pack()

        self.CUSSumLabel.grid(row=1,column=0,sticky=tk.W)
        self.CUSSumInfoLabel.grid(row=1,column=1,sticky=tk.W)
        self.FBCSumLabel.grid(row=1,column=2,sticky=tk.W)
        self.FBCSumInfoLabel.grid(row=1,column=3,sticky=tk.W)
        self.LKCSumLabel.grid(row=1,column=4,sticky=tk.W)
        self.LKCSumInfoLabel.grid(row=1,column=5,sticky=tk.W)

            # 其它信息
        ro = 0
        self.CurrentTableLabel.grid(row=ro,column=0,sticky=tk.W,pady=10)
        self.CurrentTableInfoLabel.grid(row=ro,column=1,sticky=tk.W)
        self.CurrentDataLabel.grid(row=ro,column=2,sticky=tk.W)
        self.CurrentDataInfoLabel.grid(row=ro,column=3,sticky=tk.W)
        ro += 1
        self.ALLSumLabel.grid(row=ro,column=0,sticky=tk.W)
        self.ALLSumInfoLabel.grid(row=ro,column=1,sticky=tk.W)
        # tk.Label(self.DataInfoFrame,text='\t\t').grid(row=ro,column=2)
        self.CanUseSumLabel.grid(row=ro,column=2,sticky=tk.W)
        self.CanUseSumInfoLabel.grid(row=ro,column=3,sticky=tk.W)
        ro += 1
        self.CurrentTableS7Label.grid(row=ro,column=0,sticky=tk.W)
        self.CurrentTablleS7InfoLabel.grid(row=ro,column=1,sticky=tk.W)
        self.CurrentTableM7Label.grid(row=ro, column=2,sticky=tk.W)
        self.CurrentTablleM7InfoLabel.grid(row=ro, column=3,sticky=tk.W)
        self.CurrentTable7Label.grid(row=ro,column=4,sticky=tk.W)
        self.CurrentTable7InfoLabel.grid(row=ro,column=5,sticky=tk.W)
        ro += 1
        self.CurrentTableS30Label.grid(row=ro, column=0,sticky=tk.W)
        self.CurrentTablleS30InfoLabel.grid(row=ro, column=1,sticky=tk.W)
        self.CurrentTableM30Label.grid(row=ro, column=2,sticky=tk.W)
        self.CurrentTablleM30InfoLabel.grid(row=ro, column=3,sticky=tk.W)
        self.CurrentTable30Label.grid(row=ro, column=4, sticky=tk.W)
        self.CurrentTable30InfoLabel.grid(row=ro, column=5, sticky=tk.W)
        ro += 1
        self.CurrentDataS7Label.grid(row=ro, column=0,sticky=tk.W)
        self.CurrentDataS7InfoLabel.grid(row=ro, column=1,sticky=tk.W)
        self.CurrentDataM7Label.grid(row=ro, column=2,sticky=tk.W)
        self.CurrentDataM7InfoLabel.grid(row=ro, column=3,sticky=tk.W)
        self.CurrentData7Label.grid(row=ro, column=4, sticky=tk.W)
        self.CurrentData7InfoLabel.grid(row=ro, column=5, sticky=tk.W)
        ro += 1
        self.CurrentDataS30Label.grid(row=ro, column=0,sticky=tk.W)
        self.CurrentDataS30InfoLabel.grid(row=ro, column=1,sticky=tk.W)
        self.CurrentDataM30Label.grid(row=ro, column=2,sticky=tk.W)
        self.CurrentDataM30InfoLabel.grid(row=ro, column=3,sticky=tk.W)
        self.CurrentData30Label.grid(row=ro, column=4, sticky=tk.W)
        self.CurrentData30InfoLabel.grid(row=ro, column=5, sticky=tk.W)

            # 功能按钮
        fr = 0
        self.CreateNewCapitalButton.grid(row=fr,column=0)
        fr += 1
        self.UpdateCaptialButton.grid(row=fr,column=0)
        fr += 1
        self.DelCaptialButton.grid(row=fr,column=0)

        #数据初始化
        # 绑定选中函数到列表
        self.CUSListBox.bind('<<ListboxSelect>>', self.SelectCUS)
        self.FBCListBox.bind('<<ListboxSelect>>', self.SelectFBC)
        self.LKCListBox.bind('<<ListboxSelect>>', self.SelectLKC)



        ver = sqc.Connect2Sql()
        if ver[0]:
            self.MysqlConnectStateInfoLabel.configure(text='已连接 '+'Mysql'+ver[1],fg='green')
        else:
            self.MysqlConnectStateInfoLabel.configure(text='连接失败',fg='red')
            return
            # 更新所有信息
        self.updateall()
            # 初始化操作记录
        InitOpHistoryth = threading.Thread(target=self.InitOpHistory(),args=())
        InitOpHistoryth.daemon = True
        InitOpHistoryth.start()
            # 计算历史信息
        CaluHisth = threading.Thread(target=self.CaluHistoryInformation(),args=())
        CaluHisth.daemon =True
        CaluHisth.start()
            # 计算730天信息
        self.CaluTable730()
        ll.login.destroy()
        self.mswin.mainloop()



    # 删除资金
    def DelC(self):
        if sqc.DelCapital(self.CurrectListBox,self.CurrectData):
            self.CUSListBox.delete(0, tk.END)
            self.FBCListBox.delete(0, tk.END)
            self.LKCListBox.delete(0, tk.END)

            self.updateall()
    # 初始化操作记录字典
    def InitOpHistory(self):
        sql = "select name from {0}".format('canusesalary')
        res = sqc.Select(sql)
        if res != False:
            for i in res:
                self.CanUseHisDict[i[0]] = 0

        sql = "select name from {0}".format('flexiblecapital')
        res = sqc.Select(sql)
        if res != False:
            for i in res:
                self.FlexibleHisDict[i[0]] = 0

        sql = "select name from {0}".format('lockedcapital')
        res = sqc.Select(sql)
        if res != False:
            for i in res:
                self.LockedHisDict[i[0]] = 0
        self.InitOpInfoLabel.configure(text='已完成',fg='green')
    # 选中可用资金
    def SelectCUS(self,event):
        CUS_t = self.CUSListBox.curselection()
        if len(CUS_t) == 0:
            return
        self.CurrectListBox = 'canusesalary'
        CUS_tkey = list(self.CanUseSalaryDict.keys())
        self.CurrectData = CUS_tkey[CUS_t[0]]
        self.CUSLabel.configure(fg='blue')
        self.FBCLabel.configure(fg='black')
        self.LKCLabel.configure(fg='black')
        # print(self.CurrectListBox,self.CurrectData)
        self.CurrentTableInfoLabel.configure(text='可用资金')
        self.CurrentDataInfoLabel.configure(text=self.CurrectData)
        self.CaluTable730()




    # 选中灵活资金
    def SelectFBC(self,event):
        FBC_t = self.FBCListBox.curselection()
        if len(FBC_t) == 0:
            return
        self.CurrectListBox = 'flexiblecapital'
        FBC_key = list(self.FlexibleCapitalDict.keys())
        self.CurrectData = FBC_key[FBC_t[0]]
        self.CUSLabel.configure(fg='black')
        self.FBCLabel.configure(fg='blue')
        self.LKCLabel.configure(fg='black')
        self.CurrentTableInfoLabel.configure(text='灵活资金')
        self.CurrentDataInfoLabel.configure(text=self.CurrectData)
        self.CaluTable730()

    # 选中锁定资金
    def SelectLKC(self,event):
        LKC_t = self.LKCListBox.curselection()
        if len(LKC_t) == 0:
            return
        self.CurrectListBox = 'lockedcapital'
        LKC_key = list(self.LockedCapitalDict.keys())
        self.CurrectData = LKC_key[LKC_t[0]]
        self.CUSLabel.configure(fg='black')
        self.FBCLabel.configure(fg='black')
        self.LKCLabel.configure(fg='blue')
        # print(self.CurrectListBox, self.CurrectData)
        self.CurrentTableInfoLabel.configure(text='锁定资金')
        self.CurrentDataInfoLabel.configure(text=self.CurrectData)
        self.CaluTable730()

    # 修改选中的数据窗口
    def Updatewin(self):
        if self.CurrectData == None or self.CurrectListBox == None:
            tk.messagebox.showinfo(title='未选择数据', message='请选择要修改的数据:')
            return
        try:
            if self.updwin.state() == 'normal':
                self.updwin.attributes('-topmost',True)
                self.updwin.attributes('-topmost',False)
                return
        except:
            self.updwin = tk.Toplevel()
            self.updwin.title('更新数据')
        tb = self.CurrectListBox
        nm = self.CurrectData



        self.tbnameLabel = tk.Label(self.updwin,text='选中表:')
        self.tbnameInfoLabel = tk.Label(self.updwin,text=self.tableDict[self.CurrectListBox][0])
        self.datanameLabel = tk.Label(self.updwin,text='要修改的数据:')
        self.datanameInfoLabel = tk.Label(self.updwin,text=self.CurrectData)

        self.dataLabel = tk.Label(self.updwin,text='值:')
        self.dataEnrty = tk.Entry(self.updwin)

        self.upsureButton = tk.Button(self.updwin,text='确认',command=lambda :self.updatedata(tb,self.dataEnrty.get(),nm))
        self.upcancelButton = tk.Button(self.updwin,text='取消',command=lambda :self.updwin.destroy())

        self.tbnameLabel.grid(row=0,column=0,sticky=tk.W)
        self.tbnameInfoLabel.grid(row=0,column=1,sticky=tk.W)
        self.datanameLabel.grid(row=1,column=0,sticky=tk.W)
        self.datanameInfoLabel.grid(row=1,column=1,sticky=tk.W)
        self.dataLabel.grid(row=2,column=0,sticky=tk.W)
        self.dataEnrty.grid(row=2,column=1,sticky=tk.W)
        self.upsureButton.grid(row=3,column=0)
        self.upcancelButton.grid(row=3,column=1)

    # 添加数据窗口
    def Addwin(self):
        try:
            if self.addwin.state() == 'normal':
                self.addwin.attributes('-topmost', True)
                self.addwin.attributes('-topmost', False)
                return
        except:
            self.addwin = tk.Toplevel()
            self.addwin.title('新增数据')
        tb = self.CurrectListBox
        nm = self.CurrectData

        self.tbnameLabel = tk.Label(self.addwin, text='选中表:')
        self.tbnameInfoCombobox = ttk.Combobox(self.addwin,state='readonly')
        self.tbnameInfoCombobox['values'] = ['可用资金','灵活资金','锁定资金']
        self.tbnameInfoCombobox.current(0)
        self.datanameLabel = tk.Label(self.addwin, text='要添加的数据:')


        self.dataLabel = tk.Label(self.addwin, text='数据名称:')
        self.dataEnrty = tk.Entry(self.addwin)
        self.datavLabel = tk.Label(self.addwin,text='资金量:')
        self.datavEntry = tk.Entry(self.addwin)


        self.upsureButton = tk.Button(self.addwin, text='确认',
                                      command=lambda: sqc.AddNewCapital(self.tbnameInfoCombobox.get(),self.dataEnrty.get(),self.datavEntry.get()))
        self.upcancelButton = tk.Button(self.addwin, text='取消', command=lambda: self.addwin.destroy())

        self.tbnameLabel.grid(row=0, column=0, sticky=tk.W)
        self.tbnameInfoCombobox.grid(row=0, column=1, sticky=tk.W)
        self.datanameLabel.grid(row=1, column=0, sticky=tk.W)
        self.dataLabel.grid(row=2, column=0, sticky=tk.W)
        self.dataEnrty.grid(row=2, column=1, sticky=tk.W)
        self.datavLabel.grid(row=3,column=0,sticky=tk.W)
        self.datavEntry.grid(row=3,column=1,sticky=tk.W)
        self.upsureButton.grid(row=4, column=0)
        self.upcancelButton.grid(row=4, column=1)

    # 单项求合
    def UpdateSum(self):
        try:
            sum = sqc.SqlSum()
            while None in sum:
                sum[sum.index(None)] = 0
            self.CUSSum = sum[0]
            self.FBCSum = sum[1]
            self.LKCSum = sum[2]
            self.CUSSumInfoLabel.configure(text="{:.2f}".format(sum[0]))
            self.FBCSumInfoLabel.configure(text="{:.2f}".format(sum[1]))
            self.LKCSumInfoLabel.configure(text="{:.2f}".format(sum[2]))

        except Exception as msg:
            print('UpdateSum'+str(msg))


    # 修改数据
    def updatedata(self,tb,f,nm):
        if sqc.CapitalUpdata(tb,f,nm):
            if self.CurrectListBox == 'canusesalary':
                self.before = self.CanUseSalaryDict[self.CurrectData]
                self.CanUseHisDict[self.CurrectData] += float(f)-self.before
            elif self.CurrectListBox == 'flexiblecapital':
                self.before = self.FlexibleCapitalDict[self.CurrectData]
                self.FlexibleHisDict[self.CurrectData] += float(f)-self.before
            elif self.CurrectListBox == list(self.tableDict.keys())[2]:
                self.before = self.LockedCapitalDict[self.CurrectData]
                self.LockedHisDict[self.CurrectData] += float(f) - self.before
            self.CUSListBox.delete(0,tk.END)
            self.FBCListBox.delete(0,tk.END)
            self.LKCListBox.delete(0,tk.END)
            self.updateall()

        self.updwin.destroy()

    # 其它数据计算
    def cualall(self):
        try:
            if not str(self.CUSSum).isdigit():
                self.CUSSum = 0
            if not str(self.FBCSum).isdigit():
                self.CUSSum = 0
            if not str(self.LKCSum).isdigit():
                self.CUSSum = 0
            self.allsum = self.CUSSum+self.FBCSum+self.LKCSum
            self.ALLSumInfoLabel.configure(text="{:.2f}".format(self.allsum))
            self.canusesum = self.CUSSum + self.FBCSum
            self.CanUseSumInfoLabel.configure(text="{:.2f}".format(self.canusesum))
        except Exception as msg:
            print('cualall'+str(msg))

    # 更新所有数据
    def updateall(self):
        # 更新ListBox信息
        sqc.InitDataFromDB()
        # 单项求合
        self.UpdateSum()
        #
        self.cualall()

    # 查询历史变动
    def CaluHistoryInformation(self):
        try:
            # 遍历所有的历史数据
            for tbname in list(self.tableDict.values()):
                if tbname[1] == 'canusehistory':
                    self.keys = list(self.CanUseSalaryDict.keys())
                elif tbname[1] == 'flexiblehistory':
                    self.keys = list(self.FlexibleCapitalDict)
                elif tbname[1] == 'lockedhistory':
                    self.keys = list(self.LockedCapitalDict)
                for dataname in self.keys:
                    self.re730 = []
                    for limit in [7,30]:
                        sql = '''
                        select sum({0}) z,
                        (select sum({0}) from {1} where DATEDIFF(now(),odate) <= {2} and {0} <0) f
                                         from {1} where DATEDIFF(now(),odate) <= {2} and {0} >=0;'''.format(dataname,tbname[1],limit)
                        sqc.cursor.execute(sql)
                        res = list(sqc.cursor.fetchone())
                        while None in res:
                            res[res.index(None)] = 0
                        self.re730.append(res[0])
                        self.re730.append(res[1])
                    # 写入获取数据字典 '数据名':[7天内正收入，7天内负收入，30天内正收入，30天内负收入]
                    if tbname[1] == 'canusehistory':
                        self.CanUseGetDict[dataname] = self.re730
                    elif tbname[1] == 'flexiblehistory':
                        self.FlexibleGetDict[dataname] = self.re730
                    elif tbname[1] == 'lockedhistory':
                        self.LockedGetDict[dataname] = self.re730
            # print(self.CanUseGetDict,self.FlexibleGetDict,self.LockedGetDict,sep='\n')
            self.CaluHisInfoLabel.configure(text='已完成',fg='green')
        except Exception as msg:
            print('CaluHistoryInformation'+str(msg))

    # 计算表7、30天数据
    def CaluTable730(self):
        self.TS7 = 0
        self.TM7 = 0
        self.TS30 = 0
        self.TM30 = 0
        try:
            if self.CurrectListBox == list(self.tableDict.keys())[0]:
                self.gd = self.CanUseGetDict
            elif self.CurrectListBox == list(self.tableDict.keys())[1]:
                self.gd = self.FlexibleGetDict
            elif self.CurrectListBox == list(self.tableDict.keys())[2]:
                self.gd = self.LockedGetDict
            for i in list( self.gd.values()):
                self.TS7 += i[0]
                self.TM7 += i[1]
                self.TS30 += i[2]
                self.TM30 += i[3]
            self.CurrentTableS7Label.configure(text=self.tableDict[self.CurrectListBox][0]+'7天收入:')
            self.CurrentTableM7Label.configure(text=self.tableDict[self.CurrectListBox][0] + '7天支出:')
            self.CurrentTable7Label.configure(text=self.tableDict[self.CurrectListBox][0] + '7天净值:')
            self.CurrentTableM30Label.configure(text=self.tableDict[self.CurrectListBox][0] + '30天支出:')
            self.CurrentTableS30Label.configure(text=self.tableDict[self.CurrectListBox][0] + '30天收入:')
            self.CurrentTable30Label.configure(text=self.tableDict[self.CurrectListBox][0] + '30天净值:')
            self.CurrentTablleS7InfoLabel.configure(text="{:.2f}".format(self.TS7))
            self.CurrentTablleM7InfoLabel.configure(text="{:.2f}".format(self.TM7))
            self.CurrentTable7InfoLabel.configure(text="{:.2f}".format(self.TM7+self.TS7))
            self.CurrentTablleS30InfoLabel.configure(text="{:.2f}".format(self.TS30))
            self.CurrentTablleM30InfoLabel.configure(text="{:.2f}".format(self.TM30))
            self.CurrentTable30InfoLabel.configure(text="{:.2f}".format(self.TS30+self.TM30))
            self.CurrentDataS7InfoLabel.configure(text="{:.2f}".format(self.gd[self.CurrectData][0]))
            self.CurrentDataM7InfoLabel.configure(text="{:.2f}".format(self.gd[self.CurrectData][1]))
            self.CurrentData7InfoLabel.configure(text="{:.2f}".format(self.gd[self.CurrectData][1]+self.gd[self.CurrectData][0]))
            self.CurrentDataS30InfoLabel.configure(text="{:.2f}".format(self.gd[self.CurrectData][2]))
            self.CurrentDataM30InfoLabel.configure(text="{:.2f}".format(self.gd[self.CurrectData][3]))
            self.CurrentData30InfoLabel.configure(text="{:.2f}".format(self.gd[self.CurrectData][2] + self.gd[self.CurrectData][3]))
            self.CurrentDataS7Label.configure(text=self.CurrectData + '7天收入:')
            self.CurrentDataM7Label.configure(text=self.CurrectData + '7天支出:')
            self.CurrentData7Label.configure(text=self.CurrectData + '7天净值:')
            self.CurrentDataM30Label.configure(text=self.CurrectData + '30天支出:')
            self.CurrentDataS30Label.configure(text=self.CurrectData + '30天收入:')
            self.CurrentData30Label.configure(text=self.CurrectData + '30天净值:')

        except Exception as msg:
            print('CaluTable730' + str(msg))

# 数据库控制模块
class SqlCtrl:
    def __init__(self):
        self.host = '1.116.154.14'
        self.user = 'root'
        self.password = 'rootroot'
        self.database = 'mydb'
        self.charset = 'utf8'
        self.userdb = 'testtest'
    # 连接到数据库
    def Connect2Sql(self):
        try:
            self.conn = pymysql.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.database,
                charset = self.charset
            )
            self.cursor = self.conn.cursor()
            self.CheckDBIFE()

            self.cursor.execute('SELECT VERSION()')
            self.data = self.cursor.fetchall()[0]
            print(self.data, '连接成功！', type(self.data))
            return True,self.data[0]
        except Exception as msg:
            print('ERROR:'+str(msg))
            return False

    # 获取用户名
    def logindb(self,nm):
        self.userdb = nm
        msw.CreateWin()


    # 检查数据库是否存在
    def CheckDBIFE(self):
        self.cursor.execute("show databases like '{}';".format(self.userdb))
        res = self.cursor.fetchall()
        if len(res) == 0:
            # 数据库不存在，先创建数据库
            self.cursor.execute("create database {};".format(self.userdb))
            self.cursor.execute("use {};".format(self.userdb))
            # 创建表
            self.CreateTable()
            self.cursor.execute('commit;')
        else:
            self.cursor.execute("use {};".format(self.userdb))

    # 新建数据
    def AddNewCapital(self,tb,nm,d):
        self.tbn = {'可用资金':['canusesalary','canusehistory'],'灵活资金':['flexiblecapital','flexiblehistory'],'锁定资金':['lockedcapital','lockedhistory']}
        try:
            sql = '''
                    insert into {} values(null,'{}',{});
                    '''.format(self.tbn[tb][0], nm, float(d))
            self.cursor.execute(sql)
            sql = '''
                alter table {} add {} float;
                '''.format(self.tbn[tb][1],nm)
            self.cursor.execute(sql)
            self.cursor.execute('commit;')
            msw.CUSListBox.delete(0, tk.END)
            msw.FBCListBox.delete(0, tk.END)
            msw.LKCListBox.delete(0, tk.END)
            msw.updateall()
            msw.addwin.destroy()
        except Exception as msg:
            print('AddNewCapital'+str(msg))

    # 删除数据
    def DelCapital(self,tb,nm):
        try:
            sql = '''
                delete from {} where name = '{}';
            '''.format(tb,nm)
            print(sql)
            self.cursor.execute(sql)
            sql = '''
                alter table {} drop {};
            '''.format(msw.tableDict[tb][1],nm)
            print(sql)
            self.cursor.execute(sql)
            self.cursor.execute('commit;')
            return True
        except Exception as msg:
            print('DelCapital'+str(msg))
            return False


    # 创建数据表
    def CreateTable(self):
        for i in msw.tableDict.keys():
            sql = '''
            create table {}
                (
                    id      int         null,
                    name    varchar(20) null,
                    capital float       null
                );
            '''.format(i)
            self.cursor.execute(sql)
        for i in msw.tableDict.values():
            sql = '''
            create table {}
                (
                    id     int auto_increment primary key,
                    odate  datetime null)
            '''.format(i[1])
            self.cursor.execute(sql)

    # 初始化读取数据
    def InitDataFromDB(self):
        try:
            sql = "select name,capital from {0};".format('canusesalary')
            sqc.cursor.execute(sql)
            res = sqc.cursor.fetchall()
            if len(res) == 0:
                msw.CanUseSalaryDict = {}
            for i in res:
                msw.CanUseSalaryDict[i[0]] = i[1]

            sql = "select name,capital from {0};".format('flexiblecapital')
            sqc.cursor.execute(sql)
            res = sqc.cursor.fetchall()
            if len(res) == 0:
                msw.FlexibleCapitalDict = {}
            for i in res:
                msw.FlexibleCapitalDict[i[0]] = i[1]

            sql = "select name,capital from {0};".format('lockedcapital')
            sqc.cursor.execute(sql)
            res = sqc.cursor.fetchall()
            if len(res) == 0:
                msw.LockedCapitalDict = {}
            for i in res:
                msw.LockedCapitalDict[i[0]] = i[1]

        except Exception as msg:
            print('InitDataFromDB'+str(msg))

        for i in msw.CanUseSalaryDict.keys():
            msw.CUSListBox.insert(tk.END,"{0}: {1:.2f}".format(i,msw.CanUseSalaryDict[i]))
        for i in msw.FlexibleCapitalDict.keys():
            msw.FBCListBox.insert(tk.END,"{0}: {1:.2f}".format(i,msw.FlexibleCapitalDict[i]))
        for i in msw.LockedCapitalDict.keys():
            msw.LKCListBox.insert(tk.END,"{0}: {1:.2f}".format(i,msw.LockedCapitalDict[i]))

    # 更新信息
    def CapitalUpdata(self,tb,f,nm,becall = False):
        sql = "update {0} set capital = {1} where name = '{2}';".format(tb,float(f),nm)
        print(sql)
        try:
            self.cursor.execute(sql)
            self.cursor.execute('commit;')
            return True
        except Exception as msg:
            tk.messagebox.showinfo(title='Error',message=str(msg))
            return False

    # 三项求合
    def SqlSum(self):
        sum = []
        for i in ['canusesalary','flexiblecapital','lockedcapital']:
            sql = "select sum(capital) from {0};".format(i)
            self.cursor.execute(sql)
            sum.append(self.cursor.fetchone()[0])
        return sum

    # 查询语句
    def Select(self,sql):
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            return data
        except Exception as msg:
            print('Select'+str(msg))
            return False

    # 上传修改后的数据
    def UpdateHistory(self):
        try:
            if list(msw.CanUseHisDict.values()).count(0) != 4:
                sql = '''
                insert into {} value(null,now(),{:.2f},{:.2f},{:.2f},{:.2f});'''.format('canusehistory',*msw.CanUseHisDict.values())
                print(sql)
                self.cursor.execute(sql)
            if list(msw.FlexibleHisDict.values()).count(0) != 3:
                sql = '''
                            insert into {} value(null,now(),{:.2f},{:.2f},{:.2f});'''.format('flexiblehistory',
                                                                                    *msw.FlexibleHisDict.values())
                print(sql)
                self.cursor.execute(sql)
            if list(msw.LockedHisDict.values()).count(0) != 4:
                sql = '''
                            insert into {} value(null,now(),{:.2f},{:.2f},{:.2f},{:.2f});'''.format('lockedhistory',
                                                                                    *msw.LockedHisDict.values())
                print(sql)
                self.cursor.execute(sql)
            self.cursor.execute('commit;')
        except Exception as msg:
            print(str(msg))

class Login():
    def __init__(self):
        ...
    def Createlogin(self):
        self.login = tk.Tk()
        self.login.title('登录界面')
        self.loginLabel = tk.Label(self.login, text='用户名:                                             ')
        self.loginEntry = tk.Entry(self.login)
        self.loginButton = tk.Button(self.login, text='登录', command=lambda:sqc.logindb(self.loginEntry.get()))
        self.loginLabel.grid(row=0, column=0)
        self.loginEntry.grid(row=1, column=0)
        self.loginButton.grid(row=2, column=0)
        self.login.mainloop()


msw = MSWin()
sqc = SqlCtrl()
ll = Login()
ll.Createlogin()


# 关闭程序后记录变化
sqc.UpdateHistory()
