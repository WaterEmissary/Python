import pymysql
import tkinter as tk

class win():
    def __init__(self):
        self.win = None
        self.sql = None
    def CreateWin(self):
        self.win = tk.Tk()
        self.win.title('mysql测试')

        self.LeftFrame = tk.Frame(self.win)
        self.RightUpFrame = tk.Frame(self.win)
        self.RightDownFrame = tk.Frame(self.win)

        self.DBIpLabel = tk.Label(self.LeftFrame,text='IP地址:')
        self.DBIpEntry = tk.Entry(self.LeftFrame)
        self.DBUserLabel = tk.Label(self.LeftFrame,text='用户名:')
        self.DBUserEntry = tk.Entry(self.LeftFrame)
        self.DBPasswordLabel = tk.Label(self.LeftFrame,text='密码:')
        self.DBPasswordEntry = tk.Entry(self.LeftFrame)

        self.DBConnectButton = tk.Button(self.LeftFrame,text='连接数据库',command=mydb.Connectsql)
        self.DBSendSqlButton = tk.Button(self.LeftFrame,text='发送',command=self.SendSql)

        self.DBSendSqlText = tk.Text(self.RightUpFrame,wrap='word')
        self.DBSendSqlTextYScr = tk.Scrollbar(self.RightUpFrame)
        self.DBSendSqlText.configure(yscrollcommand=self.DBSendSqlTextYScr.set)
        self.DBSendSqlTextYScr.configure(command=self.DBSendSqlText.yview)

        self.DBRecvSqlText = tk.Text(self.RightDownFrame,wrap='word')
        self.DBRecvSqlTextYScr = tk.Scrollbar(self.RightDownFrame)
        self.DBRecvSqlText.configure(yscrollcommand=self.DBRecvSqlTextYScr.set)
        self.DBRecvSqlTextYScr.configure(command=self.DBRecvSqlText.yview)

        self.LeftFrame.grid(row=0,column=0)
        self.RightUpFrame.grid(row=0,column=1)
        self.RightDownFrame.grid(row=1,column=1)

        self.DBIpLabel.grid(row=0,column=0)
        self.DBIpEntry.grid(row=1,column=0)
        self.DBUserLabel.grid(row=2,column=0)
        self.DBUserEntry.grid(row=3,column=0)
        self.DBPasswordLabel.grid(row=4,column=0)
        self.DBPasswordEntry.grid(row=5,column=0)
        self.DBConnectButton.grid(row=6,column=0)
        self.DBSendSqlButton.grid(row=7,column=0)

        self.DBSendSqlTextYScr.pack(fill=tk.Y,side=tk.RIGHT)
        self.DBSendSqlText.pack()
        self.DBRecvSqlTextYScr.pack(fill=tk.Y,side=tk.RIGHT)
        self.DBRecvSqlText.pack()

        self.DBIpEntry.insert(0,mydb.host)
        self.DBUserEntry.insert(0,mydb.user)
        self.DBPasswordEntry.insert(0,mydb.password)

        self.win.mainloop()

    def GetSql(self):
        self.sql = self.DBSendSqlText.get(0.0,tk.END)

    def SendSql(self):
        self.GetSql()
        self.DBRecvSqlText.delete(0.0, tk.END)
        try:
            mydb.cursor.execute(self.sql)

            mydb.data = mydb.cursor.fetchall()
            for i in mydb.data:
                self.DBRecvSqlText.insert(tk.END,str(i))
                print(str(i))
        except Exception as msg:
            self.DBRecvSqlText.insert(tk.END,str(msg))
            print(msg)


class mysql():
    def __init__(self):
        self.db = None
        self.host = '42.192.223.183'
        self.user = 'user'
        self.password = 'user'
        self.char = 'utf8'
    def Connectsql(self):
        self.host = sqlwin.DBIpEntry.get()
        self.user = sqlwin.DBUserEntry.get()
        self.password = sqlwin.DBPasswordEntry.get()
        self.db = pymysql.connect(host=self.host,
                                  user=self.user,
                                  password=self.password,
                                  charset = self.char)
        self.cursor = self.db.cursor()
        self.cursor.execute('SELECT VERSION()')
        self.data = self.cursor.fetchall()
        sqlwin.DBRecvSqlText.insert(0.0,str(self.data)+'连接成功！')
        print(self.data,'连接成功！')

sqlwin = win()
mydb = mysql()
sqlwin.CreateWin()