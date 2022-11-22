import os

import pymysql
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter import filedialog
from tkinter import messagebox

from pymysql.cursors import DictCursor


class win():
    def __init__(self):
        self.win = None
        self.sql = None
        self.sqlTypeList = ['mysql']
    def CreateWin(self):
        self.win = tk.Tk()
        self.win.title('数据库查询转换工具')
        self.win.resizable(width=False, height=False)

        # Frame定义
        self.LeftFrame = tk.Frame(self.win,bd=10)
        self.LeftStateFrame = tk.Frame(self.LeftFrame)
        self.LeftRegisterFrame = tk.Frame(self.LeftFrame)
        self.LeftSelectDBFrame = tk.Frame(self.LeftFrame)

        self.RightFrame = tk.Frame(self.win)
        self.RightUpFrame = tk.Frame(self.RightFrame)
        self.RightMidFrame = tk.Frame(self.RightFrame)
        self.RightDownFrame = tk.Frame(self.RightFrame)
        self.RightUpSQLFrame = tk.Frame(self.RightUpFrame)
        self.RightMidRecvFrame = tk.Frame(self.RightMidFrame)
        self.RightDownJSONFrame = tk.Frame(self.RightDownFrame)

        # 状态定义
        self.ConnectStateLabel = tk.Label(self.LeftStateFrame, text='当前状态:')
        self.ConnectStateInfoLabel = tk.Label(self.LeftStateFrame, text='未连接',fg='red')
        self.IPStateLabel = tk.Label(self.LeftStateFrame,text='数据库地址:')
        self.IPStateInfoLabel = tk.Label(self.LeftStateFrame,text='   <请先连接数据库>',fg='grey')
        self.DBVersionLabel = tk.Label(self.LeftStateFrame,text='数据库版本:')
        self.DBVersionInfoLabel = tk.Label(self.LeftStateFrame,text='   <请先连接数据库>',fg='grey')
        self.CurrentDBLabel = tk.Label(self.LeftStateFrame,text='当前数据库:')
        self.CurrentDBInfoLabel = tk.Label(self.LeftStateFrame,text='   未选择',fg='grey')
        self.StateLineLabel = tk.Label(self.LeftStateFrame,text='--------------------------------')

        # 登录区定义
        self.DBTypeLabel = tk.Label(self.LeftRegisterFrame,text='数据库类型:')
        self.DBTypeCocombox = ttk.Combobox(self.LeftRegisterFrame,state='readonly',width=18)
        self.DBTypeCocombox['value'] = self.sqlTypeList
        self.DBTypeCocombox.current(0)
        self.DBIpLabel = tk.Label(self.LeftRegisterFrame,text='IP地址:')
        self.DBIpEntry = tk.Entry(self.LeftRegisterFrame)
        self.DBUserLabel = tk.Label(self.LeftRegisterFrame,text='用户名:')
        self.DBUserEntry = tk.Entry(self.LeftRegisterFrame)
        self.DBPasswordLabel = tk.Label(self.LeftRegisterFrame,text='密码:')
        self.DBPasswordEntry = tk.Entry(self.LeftRegisterFrame,show='●')
        self.RegisterLineLabel = tk.Label(self.LeftRegisterFrame,text='--------------------------------')

        # 选择数据库区
        self.DBConnectButton = tk.Button(self.LeftRegisterFrame,text='连接数据库',width=10,command=mydb.Connectsql)
        self.DBClosetButton = tk.Button(self.LeftRegisterFrame,text='断开',width=8,command=mydb.CloseSql,state='disabled')
        self.SelectDBLabel = tk.Label(self.LeftSelectDBFrame,text='选择数据库')
        self.SelectDBCocombox = ttk.Combobox(self.LeftSelectDBFrame)
        self.SelectDBSureButton = tk.Button(self.LeftSelectDBFrame,text='确认',width=10,command=mydb.SelectDB)

        # 数据库发送定义
        self.mysqlLabel = tk.Label(self.RightUpFrame,text='SQL语句:')
        self.DBSendSqlText = tk.Text(self.RightUpSQLFrame,wrap='word',spacing3=5, width=90, height=5)
        self.DBSendSqlTextYScr = tk.Scrollbar(self.RightUpSQLFrame)
        self.DBSendSqlText.configure(yscrollcommand=self.DBSendSqlTextYScr.set)
        self.DBSendSqlTextYScr.configure(command=self.DBSendSqlText.yview)
        self.DBSendSqlButton = tk.Button(self.RightUpFrame, text='执行',width=10,command=mydb.SendSql,font=tkFont.Font(size=13))
        self.DBCleanSqlButton = tk.Button(self.RightUpFrame,text='清空',width=10,command=self.CleanSql)
        self.DBPasteFromPlateButton = tk.Button(self.RightUpFrame,text='粘贴',width=10,command=self.CleanAndPaste)

        # 数据库返回定义
        self.RevcLabel = tk.Label(self.RightMidFrame,text='查询结果:')
        self.DBRecvSqlText = tk.Text(self.RightMidRecvFrame,wrap='word',spacing3=5, width=90, height=8,state='disabled',background='black')
        self.DBRecvSqlTextYScr = tk.Scrollbar(self.RightMidRecvFrame)
        self.DBRecvSqlText.configure(yscrollcommand=self.DBRecvSqlTextYScr.set)
        self.DBRecvSqlTextYScr.configure(command=self.DBRecvSqlText.yview)

        #  JSON转换定义
        self.JsonLabel = tk.Label(self.RightDownFrame,text='JSON语句:')
        self.JsonText = tk.Text(self.RightDownJSONFrame,wrap='word',spacing3=5, width=90, height=8,state='disabled')
        self.JsonTextYScr = tk.Scrollbar(self.RightDownJSONFrame)
        self.JsonText.configure(yscrollcommand=self.JsonTextYScr.set)
        self.JsonTextYScr.configure(command=self.JsonText.yview)
        self.JsonCopyButton = tk.Button(self.RightDownFrame,text='复制',width=10,command=lambda:self.copytoplate(self.JsonText))
        self.JsonSaveAsjsonButton = tk.Button(self.RightDownFrame,text='保存为.json文件',width=15,command=mydb.SaveAsJson)

        # Frame添加
        self.LeftFrame.grid(row=0,column=0)
        self.LeftStateFrame.grid(row=1,column=0)
        self.LeftRegisterFrame.grid(row=2,column=0)
        self.LeftSelectDBFrame.grid(row=3,column=0)
        self.RightFrame.grid(row=0,column=1)
        self.RightUpFrame.grid(row=0, column=0)
        self.RightMidFrame.grid(row=1, column=0)
        self.RightDownFrame.grid(row=2, column=0)



        self.RightDownJSONFrame.grid(row=0,column=0)

        # 状态区块
        r = 0
        self.ConnectStateLabel.grid(row=r,column=0,sticky=tk.W)
        self.ConnectStateInfoLabel.grid(row=r,column=1,sticky=tk.W)
        r += 1
        self.IPStateLabel.grid(row=r,column=0,columnspan=2,sticky=tk.W)
        r += 1
        self.IPStateInfoLabel.grid(row=r,column=0,columnspan=2,sticky=tk.W)
        r += 1
        self.DBVersionLabel.grid(row=r,column=0,columnspan=2,sticky=tk.W)
        r += 1
        self.DBVersionInfoLabel.grid(row=r,column=0,columnspan=2,sticky=tk.W)
        r += 1
        self.CurrentDBLabel.grid(row=r,column=0,columnspan=2,sticky=tk.W)
        r += 1
        self.CurrentDBInfoLabel.grid(row=r,column=0,columnspan=2,sticky=tk.W)
        r += 1
        self.StateLineLabel.grid(row=r,column=0,columnspan=2)

        # 登录区块
        self.DBTypeLabel.grid(row=0,column=0,sticky=tk.W)
        self.DBTypeCocombox.grid(row=1,column=0)
        self.DBIpLabel.grid(row=2,column=0,sticky=tk.W)
        self.DBIpEntry.grid(row=3,column=0)
        self.DBUserLabel.grid(row=4,column=0,sticky=tk.W)
        self.DBUserEntry.grid(row=5,column=0)
        self.DBPasswordLabel.grid(row=6,column=0,sticky=tk.W)
        self.DBPasswordEntry.grid(row=7,column=0)
        self.DBConnectButton.grid(row=8,column=0)
        self.DBClosetButton.grid(row=9,column=0)
        self.DBSendSqlButton.grid(row=10,column=0)
        self.RegisterLineLabel.grid(row=11,column=0)

        #选择数据库区块
        self.SelectDBLabel.grid(row=0,column=0)
        self.SelectDBCocombox.grid(row=1,column=0)
        self.SelectDBSureButton.grid(row=2,column=0)

        # 数据库发送区
        self.mysqlLabel.grid(row=0,column=0,sticky=tk.NW)
        self.RightUpSQLFrame.grid(row=1, column=0,columnspan=10)
        self.DBSendSqlTextYScr.pack(fill=tk.Y,side=tk.RIGHT)
        self.DBSendSqlText.pack()
        self.DBCleanSqlButton.grid(row=2, column=7, sticky=tk.E)
        self.DBPasteFromPlateButton.grid(row=2,column=8,sticky=tk.E)
        self.DBSendSqlButton.grid(row=2,column=9,sticky=tk.E)


        # 数据库接收区
        self.RevcLabel.grid(row=0,column=0,sticky=tk.W)
        self.RightMidRecvFrame.grid(row=1, column=0)
        self.DBRecvSqlTextYScr.pack(fill=tk.Y,side=tk.RIGHT)
        self.DBRecvSqlText.pack()

        # JSON转换区
        self.JsonLabel.grid(row=0,column=0,sticky=tk.W)
        self.RightDownJSONFrame.grid(row=1,column=0,columnspan=8)
        self.JsonTextYScr.pack(fill=tk.Y,side=tk.RIGHT)
        self.JsonText.pack()
        self.JsonCopyButton.grid(row=2,column=6,sticky=tk.E)
        self.JsonSaveAsjsonButton.grid(row=2,column=7,sticky=tk.E)

        # 数据初始化
        self.ReadSession()
        self.Initinfo()
        # Text框文本插入格式
        self.colorlist = ["red", "grey", "blue","black","white"]
        for i in self.colorlist:
            # 主窗口Text部件颜色
            self.DBRecvSqlText.tag_add(i, 1.0, 1.999)
            self.DBRecvSqlText.tag_config(i, foreground=i)
        self.win.mainloop()

    # 读取上一次登录的记录
    def ReadSession(self):
        if os.path.exists('../临时程序/config'):
            with open('../临时程序/config', 'rb') as f:
                line = f.readline()
                self.DBTypeCocombox.current(self.sqlTypeList.index(str(line.decode().replace('\n',''))))
                line = f.readline()
                mydb.host = str(line.decode().replace('\n',''))
                line = f.readline()
                mydb.user = str(line.decode().replace('\n',''))
                line = f.readline()
                mydb.password = str(line.decode().replace('\n',''))

    # 保存这次的登录记录
    def SaveSession(self):
        with open('../临时程序/config', 'wb') as f:
            f.write(bytes((self.DBTypeCocombox.get()+'\n').encode()))
            f.write((self.DBIpEntry.get()+'\n').encode())
            f.write((self.DBUserEntry.get()+'\n').encode())
            f.write((self.DBPasswordEntry.get()).encode())

    # 数据初始化
    def Initinfo(self):
        self.DBIpEntry.delete(0,tk.END)
        self.DBUserEntry.delete(0,tk.END)
        self.DBPasswordEntry.delete(0,tk.END)
        self.DBIpEntry.insert(0, mydb.host)
        self.DBUserEntry.insert(0, mydb.user)
        self.DBPasswordEntry.insert(0, mydb.password)
        self.SelectDBCocombox.configure(state='disabled')
        self.SelectDBSureButton.configure(state='disabled')
        self.DBConnectButton.configure(state='normal')
        self.DBClosetButton.configure(state='disabled')
        self.DBSendSqlButton.configure(state='disabled')
        self.SelectDBCocombox['value'] = ['']
        self.SelectDBCocombox.current(0)
        self.SelectDBCocombox.update()
        self.ConnectStateInfoLabel.configure(text='未连接', fg='red')
        self.IPStateInfoLabel.configure(text='   <请先连接数据库>', fg='grey')
        self.DBVersionInfoLabel.configure(text='   <请先连接数据库>', fg='grey')
        self.CurrentDBInfoLabel.configure(text='   未选择', fg='grey')


    # 获取sql语句
    def GetSql(self):
        self.sql = self.DBSendSqlText.get(0.0,tk.END)

    # 输出到RevcText
    def WinPrintRecv(self,obj,str,c,n):
        obj.configure(state='normal')
        if n:
            obj.delete(0.0,tk.END)
        obj.insert(tk.END,str,c)
        obj.configure(state='disabled')

    # 清空sql语句
    def CleanSql(self):
        self.DBSendSqlText.delete(0.0,tk.END)

    # 先清空再粘贴
    def CleanAndPaste(self):
        self.CleanSql()
        self.DBSendSqlText.event_generate('<<Paste>>')


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


class mysql():
    def __init__(self):
        self.db = None
        self.dbtype = None
        self.host = ''
        self.user = ''
        self.password = ''
        self.char = 'utf8'
        self.DB = []
    def Connectsql(self):
        self.host = sqlwin.DBIpEntry.get()
        self.user = sqlwin.DBUserEntry.get()
        self.password = sqlwin.DBPasswordEntry.get()
        self.dbtype = sqlwin.DBTypeCocombox.get()
        try:
            self.db = pymysql.connect(host=self.host,
                                      user=self.user,
                                      password=self.password,
                                      charset=self.char,
                                      cursorclass=DictCursor)
            self.cursor = self.db.cursor()
            self.cursor.execute('SELECT VERSION()')
            self.data = self.cursor.fetchall()[0]
            print(self.data,'连接成功！',type(self.data))
            sqlwin.SaveSession()

            sqlwin.DBConnectButton.configure(state='disabled')
            sqlwin.DBClosetButton.configure(state='normal')
            sqlwin.DBSendSqlButton.configure(state='normal')
            # 信息初始化
            sqlwin.ConnectStateInfoLabel.configure(text='已连接',fg='green')
            sqlwin.IPStateInfoLabel.configure(text='   '+sqlwin.DBIpEntry.get(),fg='black')
            for key in self.data:
                self.keyname = key
            sqlwin.DBVersionInfoLabel.configure(text='   '+sqlwin.DBTypeCocombox.get()+'  '+str(self.data[self.keyname]),fg='black')
            self.cursor.execute('SHOW DATABASES;')
            self.data = self.cursor.fetchall()
            print(self.data)
            for key in self.data[0]:
                self.keyname = key
            for i in self.data:
                self.DB.append(i[self.keyname])
            sqlwin.SelectDBCocombox.configure(state='readonly')
            sqlwin.SelectDBCocombox['value'] = self.DB
            sqlwin.SelectDBCocombox.current(0)
            sqlwin.SelectDBSureButton.configure(state='normal')
        except Exception as msg:
            sqlwin.WinPrintRecv(sqlwin.DBRecvSqlText,str(msg),'black',True)
            print(str(msg))

    # 选择数据库函数
    def SelectDB(self):
        try:
            self.cursor = self.db.cursor()
            sqlwin.WinPrintRecv(sqlwin.DBSendSqlText,'use '+sqlwin.SelectDBCocombox.get()+';','black',True)
            sqlwin.DBSendSqlText.configure(state='normal')
            self.SendSql()
                # 数据库列表
            sqlwin.CurrentDBInfoLabel.configure(text='   '+sqlwin.SelectDBCocombox.get(),fg='black')
            # print(str(self.data))
        except Exception as msg:
            sqlwin.WinPrintRecv(sqlwin.DBRecvSqlText,str(msg)+'\n','red',True)
            print(str(msg))

    # 发送SQL语句
    def SendSql(self):
        sqlwin.GetSql()
        sqlwin.WinPrintRecv(sqlwin.DBRecvSqlText,'','black',True)
        self.sqllist = sqlwin.sql.split('\n')
        while '' in self.sqllist:
            self.sqllist.pop(self.sqllist.index(''))
        print(self.sqllist)
        for sql in self.sqllist:
            print(sql)
            try:
                self.cursor.execute(sql)
                # 如果是查询语句
                if 'select' in str(sql).lower():
                    self.data = mydb.cursor.fetchall()
                    print(self.data)
                    self.keyList = []
                    self.ddata = []
                    count = 0
                    # 录入数据
                    for result in self.data[0]:
                        self.keyList.append(result)
                    for result in self.data:
                        print('sql', count, result)
                        self.ddata.append([])
                        for key in self.keyList:
                            self.ddata[count].append(result[key])
                        count += 1
                    # 输出查询
                    recvstr = self.dbtype+'>'+str(sql)+'\n'
                    sqlwin.WinPrintRecv(sqlwin.DBRecvSqlText, recvstr, 'white', False)
                    recvstr = ''
                    for sql in self.keyList:
                        recvstr = recvstr + str(sql) + '\t'
                    recvstr += '\n'
                    for sql in self.ddata:
                        for j in sql:
                            recvstr = recvstr + str(j) + '\t'
                        recvstr += '\n'
                    sqlwin.WinPrintRecv(sqlwin.DBRecvSqlText, recvstr,'white',False)

                    # 转换为JSON
                    self.JsonStr = ''
                    for i in self.data:
                        self.JsonStr += str(i)
                        self.JsonStr += ',\n'
                    self.JsonStr = self.JsonStr[:-2]
                    sqlwin.WinPrintRecv(sqlwin.JsonText, self.JsonStr,'black',True)
                # show语句
                elif 'show' in str(sql).lower():
                    self.showList = []
                    self.data = mydb.cursor.fetchall()
                    for key in self.data[0]:
                        self.keyname = key
                    for i in self.data:
                        self.showList.append(i[self.keyname])
                    self.recvstr = self.dbtype+'>'+ sql + '\n'
                    sqlwin.WinPrintRecv(sqlwin.DBRecvSqlText, self.recvstr, 'white', False)
                    self.recvstr = ''
                    for i in self.showList:
                        self.recvstr += '\t'+i+'\n'
                    sqlwin.WinPrintRecv(sqlwin.DBRecvSqlText, self.recvstr,'white', False)
                # 非查询语句
                else:
                    if 'use' in str(sql).lower():
                        sqlwin.CurrentDBInfoLabel.configure(text='   '+sql[4:-1],fg='black')
                    self.recvstr = self.dbtype+'>'+ sql + '\n'
                    self.recvstr += '   Query OK, ' + str(self.cursor.rowcount) + ' rows affected;\n'
                    sqlwin.WinPrintRecv(sqlwin.DBRecvSqlText, self.recvstr, 'white', False)
            except Exception as msg:
                sqlwin.WinPrintRecv(sqlwin.DBRecvSqlText,str(msg)+'\n','red',False)
                print(msg)

    def SaveAsJson(self):
        self.savepath = filedialog.asksaveasfilename(initialdir='', title='保存Json',
                                                             filetypes=[("JSON File", 'json')],
                                                             initialfile='sql select' + '.json')
        if self.savepath == '':
            return
        try:
            with open(self.savepath,'w',encoding='utf-8') as op:
                op.write(sqlwin.JsonText.get(0.0,tk.END))
            tk.messagebox.showinfo(title='保存成功!',message='已保存到'+self.savepath)
        except Exception as msg:
            tk.messagebox.showerror(title='error!',message=str(msg))


    # 断开数据库
    def CloseSql(self):
        self.cursor.close()
        self.db.close()
        self.DB = []
        sqlwin.Initinfo()
        sqlwin.DBSendSqlText.delete(0.0,tk.END)


sqlwin = win()
mydb = mysql()
sqlwin.CreateWin()