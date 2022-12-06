import tkinter as tk
import tkinter.font
import tkinter.ttk as ttk
import tkinter.messagebox

import pymysql

# 软件界面模块
class MSWin:
    def __init__(self):
        self.CanUseSalaryDict = {}
        self.FlexibleCapitalDict = {}
        self.LockedCapitalDict = {}
        self.CurrectListBox = None
        self.CurrectData = None

        self.updwin = None

        self.CUSSum = 0
        self.FBCSum = 0
        self.LKCSum = 0


    # 创建窗口
    def CreateWin(self):
        self.mswin = tk.Tk()
        self.mswin.title('资产汇总')

        # 头部信息定义
        self.headFrame = tk.Frame(self.mswin)
        self.ConnectStateFrame = tk.Frame(self.headFrame)
        self.MysqlConnectStateLabel = tk.Label(self.ConnectStateFrame,text='ConnectState:')
        self.MysqlConnectStateInfoLabel = tk.Label(self.ConnectStateFrame,text='未连接',fg='red')
        self.CUSLabel = tk.Label(self.headFrame,text='可用资金:\t    ',font=tk.font.Font(size=13))
        self.FBCLabel = tk.Label(self.headFrame,text='灵活资金:\t    ',font=tk.font.Font(size=13))
        self.LKCLabel = tk.Label(self.headFrame,text='锁定资金:',font=tk.font.Font(size=13))

        # 资产信息定义
        self.CapitalFrame = tk.Frame(self.mswin)
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
        self.DataInfoFrame = tk.Frame(self.mswin)
        self.ALLSumLabel = tk.Label(self.DataInfoFrame,text='全部总计:',font=tk.font.Font(size=13))
        self.ALLSumInfoLabel = tk.Label(self.DataInfoFrame,text='',font=tk.font.Font(size=13))

        # 功能区
        self.FunctionFrame = tk.Frame(self.mswin)
        self.CreateNewCapitalButton = tk.Button(self.FunctionFrame,text='新建资金')
        self.UpdateCaptialButton = tk.Button(self.FunctionFrame,text='修改资金',command=self.Updatewin)


        # 显示到屏幕
        self.headFrame.grid(row=0,column=0,sticky=tk.W)
        self.CapitalFrame.grid(row=1,column=0)
        self.DataInfoFrame.grid(row=2,column=0,sticky=tk.W)
        self.FunctionFrame.grid(row=0,column=1,rowspan=3)
            # 头部信息
        self.ConnectStateFrame.grid(row=0, columnspan=3, sticky=tk.W)
        self.MysqlConnectStateLabel.grid(row=0,column=0,sticky=tk.W)
        self.MysqlConnectStateInfoLabel.grid(row=0,column=1,sticky=tk.W)
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
        self.ALLSumLabel.grid(row=0,column=0)
        self.ALLSumInfoLabel.grid(row=0,column=1)

            # 功能按钮
        fr = 0
        self.CreateNewCapitalButton.grid(row=fr,column=0)
        fr += 1
        self.UpdateCaptialButton.grid(row=fr,column=0)

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

        self.updateall()

        self.mswin.mainloop()

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
        print(self.CurrectListBox,self.CurrectData)

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
        print(self.CurrectListBox, self.CurrectData)

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
        print(self.CurrectListBox, self.CurrectData)

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

        self.tableDict = {'canusesalary':'可用资金','flexiblecapital':'灵活资金','lockedcapital':'锁定资金'}

        self.tbnameLabel = tk.Label(self.updwin,text='选中表:')
        self.tbnameInfoLabel = tk.Label(self.updwin,text=self.tableDict[self.CurrectListBox])
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

    # 单项求合
    def UpdateSum(self):
        sum = sqc.SqlSum()
        self.CUSSum = sum[0]
        self.FBCSum = sum[1]
        self.LKCSum = sum[2]
        self.CUSSumInfoLabel.configure(text="{:.2f}".format(sum[0]))
        self.FBCSumInfoLabel.configure(text="{:.2f}".format(sum[1]))
        self.LKCSumInfoLabel.configure(text="{:.2f}".format(sum[2]))

    # 修改数据
    def updatedata(self,tb,f,nm):
        if sqc.CapitalUpdata(tb,f,nm):
            self.CUSListBox.delete(0,tk.END)
            self.FBCListBox.delete(0,tk.END)
            self.LKCListBox.delete(0,tk.END)
            self.updateall()

        self.updwin.destroy()

    # 其它数据计算
    def cualall(self):
        self.allsum = self.CUSSum+self.FBCSum+self.LKCSum
        self.ALLSumInfoLabel.configure(text="{:.2f}".format(self.allsum))

    # 更新所有数据
    def updateall(self):
        sqc.InitDataFromDB()
        self.UpdateSum()
        self.cualall()

# 数据库控制模块
class SqlCtrl:
    def __init__(self):
        self.host = '1.116.154.14'
        self.user = 'root'
        self.password = 'rootroot'
        self.database = 'mysalary'
        self.charset = 'utf8'

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
            self.cursor.execute('SELECT VERSION()')
            self.data = self.cursor.fetchall()[0]
            print(self.data, '连接成功！', type(self.data))
            return True,self.data[0]
        except Exception as msg:
            print('ERROR:'+str(msg))
            return False

    # 初始化读取数据
    def InitDataFromDB(self):
        try:
            sql = "select name,capital from {0};".format('canusesalary')
            sqc.cursor.execute(sql)
            res = sqc.cursor.fetchall()
            for i in res:
                msw.CanUseSalaryDict[i[0]] = i[1]

            sql = "select name,capital from {0};".format('flexiblecapital')
            sqc.cursor.execute(sql)
            res = sqc.cursor.fetchall()
            for i in res:
                msw.FlexibleCapitalDict[i[0]] = i[1]

            sql = "select name,capital from {0};".format('lockedcapital')
            sqc.cursor.execute(sql)
            res = sqc.cursor.fetchall()
            for i in res:
                msw.LockedCapitalDict[i[0]] = i[1]
        except Exception as msg:
            print(str(msg))

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

msw = MSWin()
sqc = SqlCtrl()

msw.CreateWin()