import os
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import calendar
import datetime

class OverTimeCalendar():
    def __init__(self):
        self.MonthList = ['1','2','3','4','5','6','7','8','9','10','11','12']
        self.YearList = [x for x in range(2020,2030)]
        self.WeekTableList = ['Mo','Tu','We','Th','Fr','Sa','Su']
        self.color = {'ot7bg':'lightskyblue','ot8bg':'lightcoral','leave0.5fg':'slateblue','leave1fg':'darkorchid','ill0.5fg':'seagreen','ill1fg':'darkgreen'}
        self.ListBoxList = []
        self.NowChoice = None
        self.NowChoiceInfo = None
        self.NowMonthData = {}
        self.allday = 0
        self.ot7day = 0
        self.ot8day = 0
        self.leave1day = 0
        self.leave2day = 0
        self.ill1day = 0
        self.ill2day = 0
        self.basesalary = 5800
        self.illcut = 38
        self.leavecut = 97
        self.otadd = 75
        self.tax = int(self.basesalary * 0.185 + 10)

    # 右键菜单弹出
    def popup(self,event):
        for i in range(len(self.ListBoxList)):
            for j in range(len(self.ListBoxList[i])):
                if len(self.ListBoxList[i][j].curselection()) != 0:
                    self.NowChoice = (self.ListBoxList[i][j].get(0),i,j)
                    break
        self.menu.post(event.x_root,event.y_root)

    # 点击显示信息
    def showinfo(self,event):
        for i in range(len(self.ListBoxList)):
            for j in range(len(self.ListBoxList[i])):
                if len(self.ListBoxList[i][j].curselection()) != 0:
                    self.NowChoice = (self.ListBoxList[i][j].get(0),i,j)
                    break
        try:
            t = self.NowChoice[0] + "号\t"
            temp = self.NowMonthData[self.NowChoice[0]]
            if temp[2] == 7:
                t = t + "临工到7点\t"
            elif temp[2] == 8:
                t = t + "临工到8点\t"
            if temp[3] == -1:
                t = t + "请假半天\t"
            elif temp[3] == -2:
                t = t + "请假一天\t"
            elif temp[3] == -3:
                t = t + "病假半天\t"
            elif temp[3] == -4:
                t = t + "病假一天\t"
            self.selectDayInfoLabel.configure(text=t)
        except Exception as msg:
            print(msg)

    # 创建窗口
    def CreateMainWin(self):
        self.win = tk.Tk()
        self.win.title('临时工作日历')

        # 框架定义
        self.UpFrame = tk.Frame(self.win)
        self.CalendarFrame = tk.Frame(self.win)
        self.InfoFrame = tk.Frame(self.win)

        # 选择时间定义
        self.SelectYearCombobox = ttk.Combobox(self.UpFrame,state='readonly')
        self.SelectYearCombobox['value'] = self.YearList
        self.SelectYearCombobox.current(datetime.datetime.now().year-2020)
        self.SelectMonthCombobox = ttk.Combobox(self.UpFrame,state='readonly')
        self.SelectMonthCombobox['value'] = self.MonthList
        self.SelectMonthCombobox.current(datetime.datetime.now().month-1)
        self.SelectMonthCombobox.bind('<<ComboboxSelected>>',self.SureDate)

        # 日历格生成
        for i in range(7):
            self.ListBoxList.append([])
            for j in range(7):
                if j in [5,6]:
                    self.ListBoxList[i].append(tk.Listbox(self.CalendarFrame, width=3, height=1, font=tkFont.Font(size=15),fg='grey',selectbackground='blue'))
                else:
                    self.ListBoxList[i].append(tk.Listbox(self.CalendarFrame, width=3, height=1, font=tkFont.Font(size=15),selectbackground='blue'))
                self.ListBoxList[i][j].bind('<Button-3>',lambda event:self.popup(event))
                # self.ListBoxList[i][j].bind('<Button-1>',lambda event:self.showinfo(event))
                self.ListBoxList[i][j].bind('<<ListboxSelect>>',self.showinfo)
        # 第一行写入周几
        for j in range(len(self.WeekTableList)):
            self.ListBoxList[0][j].insert(tk.END,self.WeekTableList[j])

        # 信息
        self.selectDayLabel = tk.Label(self.InfoFrame,text='选中信息：',font=tkFont.Font(size=12))
        self.selectDayInfoLabel = tk.Label(self.InfoFrame,font=tkFont.Font(size=12))
        self.basesalaryLabel = tk.Label(self.InfoFrame,text='基础工资: ',fg='dodgerblue',font=tkFont.Font(size=12))
        self.basesalaryInfoLabel = tk.Label(self.InfoFrame,fg='dodgerblue',font=tkFont.Font(size=12))
        self.taxLabel = tk.Label(self.InfoFrame,text='税: ',fg='crimson',font=tkFont.Font(size=12))
        self.taxInfoLabel = tk.Label(self.InfoFrame,fg='crimson',font=tkFont.Font(size=12))
        self.allDayLabel = tk.Label(self.InfoFrame,text='本月总计临工:',fg='lightcoral',font=tkFont.Font(size=12))
        self.allDayInfoLabel = tk.Label(self.InfoFrame,fg='lightcoral',font=tkFont.Font(size=12))
        self.allLDayLabel = tk.Label(self.InfoFrame,text='本月总计请假:',fg='seagreen',font=tkFont.Font(size=12))
        self.allLDayInfoLabel = tk.Label(self.InfoFrame,fg='seagreen',font=tkFont.Font(size=12))
        self.OT7DayLabel = tk.Label(self.InfoFrame,text='其中临工到7点:',fg='lightcoral',font=tkFont.Font(size=12))
        self.OT7DayInfoLabel = tk.Label(self.InfoFrame,fg='lightcoral',font=tkFont.Font(size=12))
        self.OT8DayLabel = tk.Label(self.InfoFrame,text='其中临工到8点:',fg='lightcoral',font=tkFont.Font(size=12))
        self.OT8DayInfoLabel = tk.Label(self.InfoFrame,fg='lightcoral',font=tkFont.Font(size=12))
        self.Leave1Label = tk.Label(self.InfoFrame,text='其中请假0.5天:',fg='teal',font=tkFont.Font(size=12))
        self.Leave1InfoLabel = tk.Label(self.InfoFrame,fg='teal',font=tkFont.Font(size=12))
        self.Leave2Label = tk.Label(self.InfoFrame,text='其中请假1天:',fg='teal',font=tkFont.Font(size=12))
        self.Leave2InfoLabel = tk.Label(self.InfoFrame,fg='teal',font=tkFont.Font(size=12))
        self.Ill1Label = tk.Label(self.InfoFrame,text='其中病假0.5天:',fg='seagreen',font=tkFont.Font(size=12))
        self.Ill1InfoLabel = tk.Label(self.InfoFrame,fg='seagreen',font=tkFont.Font(size=12))
        self.Ill2Label = tk.Label(self.InfoFrame,text='其中病假1天:',fg='seagreen',font=tkFont.Font(size=12))
        self.Ill2InfoLabel = tk.Label(self.InfoFrame,fg='seagreen',font=tkFont.Font(size=12))
        self.caluLabel = tk.Label(self.InfoFrame,text='本月临工工资:',fg='indianred',font=tkFont.Font(size=12))
        self.caluInfoLabel = tk.Label(self.InfoFrame,fg='indianred',font=tkFont.Font(size=12))
        self.decuctLabel = tk.Label(self.InfoFrame,text='本月扣除工资:',fg='darkgreen',font=tkFont.Font(size=12))
        self.decuctInfoLabel = tk.Label(self.InfoFrame,fg='darkgreen',font=tkFont.Font(size=12))
        self.calugetLabel = tk.Label(self.InfoFrame,text='本月预估到手工资:',fg='darkorange',font=tkFont.Font(size=12))
        self.calugetInfoLabel = tk.Label(self.InfoFrame,fg='darkorange',font=tkFont.Font(size=12))
        self.calumaxgetLabel = tk.Label(self.InfoFrame,text='本月预估最高工资:',fg='blueviolet',font=tkFont.Font(size=12))
        self.calumaxgetInfoLabel = tk.Label(self.InfoFrame,fg='blueviolet',font=tkFont.Font(size=12))


        # 界面绑定
        self.UpFrame.grid(row=0,column=0)
        self.CalendarFrame.grid(row=2,column=0)
        self.InfoFrame.grid(row=3,column=0)

        self.SelectYearCombobox.grid(row=0,column=0)
        self.SelectMonthCombobox.grid(row=0,column=1)

        for i in range(7):
            for j in range(7):
                self.ListBoxList[i][j].grid(row=i,column=j)

        r = 0
        self.selectDayLabel.grid(row=r,column=0)
        self.selectDayInfoLabel.grid(row=r,column=1,columnspan=3,sticky=tk.W)
        r = r + 1
        self.basesalaryLabel.grid(row=r,column=0)
        self.basesalaryInfoLabel.grid(row=r,column=1)
        self.taxLabel.grid(row=r,column=2)
        self.taxInfoLabel.grid(row=r,column=3)
        r = r+1
        self.allDayLabel.grid(row=r,column=0)
        self.allDayInfoLabel.grid(row=r,column=1)
        self.allLDayLabel.grid(row=r,column=2)
        self.allLDayInfoLabel.grid(row=r,column=3)
        r = r + 1
        self.OT7DayLabel.grid(row=r,column=0)
        self.OT7DayInfoLabel.grid(row=r,column=1)
        self.OT8DayLabel.grid(row=r,column=2)
        self.OT8DayInfoLabel.grid(row=r,column=3)
        r = r + 1
        self.Leave1Label.grid(row=r,column=0)
        self.Leave1InfoLabel.grid(row=r,column=1)
        self.Leave2Label.grid(row=r,column=2)
        self.Leave2InfoLabel.grid(row=r,column=3)
        r = r + 1
        self.Ill1Label.grid(row=r,column=0)
        self.Ill1InfoLabel.grid(row=r,column=1)
        self.Ill2Label.grid(row=r,column=2)
        self.Ill2InfoLabel.grid(row=r,column=3)
        r = r + 1
        self.caluLabel.grid(row=r,column=0)
        self.caluInfoLabel.grid(row=r,column=1,columnspan=3)
        r = r + 1
        self.decuctLabel.grid(row=r,column=0)
        self.decuctInfoLabel.grid(row=r,column=1,columnspan=3)
        r = r + 1
        self.calumaxgetLabel.grid(row=r, column=0)
        self.calumaxgetInfoLabel.grid(row=r, column=1, columnspan=3)
        r = r + 1
        self.calugetLabel.grid(row=r,column=0)
        self.calugetInfoLabel.grid(row=r,column=1,columnspan=3)


        # init
        # 创建右键菜单
        # 0:无   7,8:临工   -1,-2:请假   -3,-4:病假
        self.menu = tk.Menu(self.win, tearoff=False)
        self.menu.add_command(label='清空', command=lambda :self.OverTimeSet(0))
        self.menu.add_command(label='临工到7点', command=lambda :self.OverTimeSet(7))
        self.menu.add_command(label='临工到8点', command=lambda :self.OverTimeSet(8))
        self.menu.add_command(label='请假0.5天', command=lambda :self.OverTimeSet(-1))
        self.menu.add_command(label='请假1天', command=lambda :self.OverTimeSet(-2))
        self.menu.add_command(label='病假0.5天', command=lambda :self.OverTimeSet(-3))
        self.menu.add_command(label='病假1天', command=lambda :self.OverTimeSet(-4))

        self.SureDate(event=None)

    # 临工按钮
    def OverTimeSet(self,T):
        if T == 7: # 临工到7点
            self.ListBoxList[self.NowChoice[1]][self.NowChoice[2]].configure(bg=self.color['ot7bg'])
            self.NowMonthData[self.NowChoice[0]][2] = 7
        elif T == 8:   #临工到8点
            self.ListBoxList[self.NowChoice[1]][self.NowChoice[2]].configure(bg=self.color['ot8bg'])
            self.NowMonthData[self.NowChoice[0]][2] = 8
        elif T == 0: # 没有临工
            self.ListBoxList[self.NowChoice[1]][self.NowChoice[2]].configure(bg='white')
            self.ListBoxList[self.NowChoice[1]][self.NowChoice[2]].configure(fg='black')
            self.NowMonthData[self.NowChoice[0]][2] = 0
            self.NowMonthData[self.NowChoice[0]][3] = 0
        elif T == -1:#请假半天
            self.ListBoxList[self.NowChoice[1]][self.NowChoice[2]].configure(fg=self.color['leave0.5fg'])
            self.NowMonthData[self.NowChoice[0]][3] = -1
        elif T == -2:  # 请假一天
            self.ListBoxList[self.NowChoice[1]][self.NowChoice[2]].configure(fg=self.color['leave1fg'])
            self.NowMonthData[self.NowChoice[0]][3] = -2
        elif T == -3: # 病假半天
            self.ListBoxList[self.NowChoice[1]][self.NowChoice[2]].configure(fg=self.color['ill0.5fg'])
            self.NowMonthData[self.NowChoice[0]][3] = -3
        elif T == -4:# 病假一天
            self.ListBoxList[self.NowChoice[1]][self.NowChoice[2]].configure(fg=self.color['ill1fg'])
            self.NowMonthData[self.NowChoice[0]][3] = -4
        self.SaveData()

    # 确认时间函数
    def SureDate(self,event):
        # 显示格全部初始化
        for i in range(len(self.ListBoxList)):
            for j in range(len(self.ListBoxList[i])):
                self.ListBoxList[i][j].configure(bg='white')
                if j < 5:
                    self.ListBoxList[i][j].configure(fg='black')
        yearlist = []
        self.NowMonthData = {}
        yearstr = calendar.month(int(self.SelectYearCombobox.get()),int(self.SelectMonthCombobox.get()))
        yearstr = yearstr.split('\n')[2:]
        for i in yearstr:
            yearlist.append(i.split(' '))
            while '' in yearlist[-1]:
                yearlist[-1].pop(yearlist[-1].index(''))
        while [] in yearlist:
            yearlist.pop(yearlist.index([]))

        # 清空显示列表
        for i in range(1,len(self.ListBoxList)):
            for j in range(len(self.ListBoxList[i])):
                self.ListBoxList[i][j].delete(0,tk.END)
        # 添加日期到显示
        for i in range(len(yearlist)):
            # 带1的一周
            if '1' in yearlist[i]:
                j = len(yearlist[i])-1
                k = 6
                while j >= 0:
                    self.ListBoxList[i+1][k].insert(tk.END,yearlist[i][j])
                    self.NowMonthData[yearlist[i][j]]=[i,k,0,0]
                    j = j-1
                    k = k-1
            # 最后一周
            elif max(yearlist[i]) >= '28':
                for j in range(len(yearlist[i])):
                    self.ListBoxList[i+1][j].insert(tk.END,yearlist[i][j])
                    self.NowMonthData[yearlist[i][j]]=[i, j, 0, 0]
            # 其余周
            else:
                for j in range(7):
                    self.ListBoxList[i+1][j].insert(tk.END,yearlist[i][j])
                    self.NowMonthData[yearlist[i][j]]=[i, j, 0, 0]

        #判断是否有当月数据
            # 如果有,读入显示
        if os.path.exists(self.SelectYearCombobox.get()+self.SelectMonthCombobox.get()+'.txt'):
            self.NowMonthData = {}
            with open(self.SelectYearCombobox.get() + self.SelectMonthCombobox.get() + '.txt', 'r', encoding='utf-8') as f:
                line = f.readline().split(',')
                while line != ['']:
                    self.NowMonthData[line[0]] = [int(line[1]),int(line[2]),int(line[3]),int(line[4])]
                    line = f.readline().split(',')
            for i in self.NowMonthData:
                if self.NowMonthData[i][2] == 0:
                    pass
                elif self.NowMonthData[i][2] == 7:
                    self.ListBoxList[self.NowMonthData[i][0]+1][self.NowMonthData[i][1]].configure(bg=self.color['ot7bg'])
                elif self.NowMonthData[i][2] == 8:
                    self.ListBoxList[self.NowMonthData[i][0]+1][self.NowMonthData[i][1]].configure(bg=self.color['ot8bg'])
                if self.NowMonthData[i][3] == -1:
                    self.ListBoxList[self.NowMonthData[i][0] + 1][self.NowMonthData[i][1]].configure(fg=self.color['leave0.5fg'])
                elif self.NowMonthData[i][3] == -2:
                    self.ListBoxList[self.NowMonthData[i][0] + 1][self.NowMonthData[i][1]].configure(fg=self.color['leave1fg'])
                elif self.NowMonthData[i][3] == -3:
                    self.ListBoxList[self.NowMonthData[i][0] + 1][self.NowMonthData[i][1]].configure(fg=self.color['ill0.5fg'])
                elif self.NowMonthData[i][3] == -4:
                    self.ListBoxList[self.NowMonthData[i][0] + 1][self.NowMonthData[i][1]].configure(fg=self.color['ill1fg'])
            print(self.NowMonthData)
            # 如果没有,创建新数据
        else:
            self.SaveData()
        updateth = threading.Thread(target=self.UpdateInfo,args=())
        updateth.daemon = True
        updateth.start()

    # 保存数据
    def SaveData(self):
        with open(self.SelectYearCombobox.get() + self.SelectMonthCombobox.get() + '.txt', 'w', encoding='utf-8') as f:
            for i in self.NowMonthData:
                f.write(i + ',' + str(self.NowMonthData[i][0]) + ',' + str(self.NowMonthData[i][1]) + ',' + str(self.NowMonthData[i][2]) +
                        ',' + str(self.NowMonthData[i][3]) +'\n')

    # 计算本月预估最高工资
    def CaluMaxGet(self):
        monthday = [0,31,28,31,30,31,30,31,31,30,31,30,31]
        today = str(datetime.date.today()).split('-')
        year = int(today[0])
        month = int(today[1])
        day = int(today[2])
        if((year%4==0 or year%100 !=0)or year % 400 == 0):
            monthday[2] += 1
        # 如果选中的是本月
        if int(self.SelectMonthCombobox.get()) == int(today[1]):
            count = 0
            # 如果当天有数据，不进入计算
            if self.NowMonthData[str(day)][2] != 0:
                j = day + 1
            else:
                j = day
            for i in range(j,monthday[int(today[1])]+1):
                # 如果最后一天有数据，不进行计算
                if self.NowMonthData[str(monthday[int(today[1])])][2] != 0:
                    return count
                wd = calendar.weekday(year,month,i)
                if wd < 5:
                    count += 150
            # 返回能获得的最高工资
            return count
        # 如果是已经过去的月份
        elif int(self.SelectMonthCombobox.get()) < int(today[1]):
            return 0
        # 未来的月份
        else:
            count = 0
            for i in range(1,monthday[int(today[1])]+1):
                wd = calendar.weekday(year, month, i)
                if wd < 5:
                    count += 150
            return count

    # 更新信息函数
    def UpdateInfo(self):
        while True:
            self.allday = 0
            self.ot7day = 0
            self.ot8day = 0
            self.leave1day = 0
            self.leave2day = 0
            self.ill1day = 0
            self.ill2day = 0
            for i in self.NowMonthData:
                if self.NowMonthData[i][2] == 7:
                    self.allday += 1
                    self.ot7day += 1
                elif self.NowMonthData[i][2] == 8:
                    self.allday += 1
                    self.ot8day += 1
                if self.NowMonthData[i][3] == -1:
                    self.leave1day += 1
                elif self.NowMonthData[i][3] == -2:
                    self.leave2day += 1
                elif self.NowMonthData[i][3] == -3:
                    self.ill1day += 1
                elif self.NowMonthData[i][3] == -4:
                    self.ill2day += 1
            self.basesalaryInfoLabel.configure(text=str(self.basesalary))
            self.taxInfoLabel.configure(text=str(self.tax))
            self.allDayInfoLabel.configure(text=str(self.allday)+' 天')
            self.allLDayInfoLabel.configure(text=str(self.leave1day+self.leave2day+self.ill1day+self.ill2day)+' 天')
            self.OT7DayInfoLabel.configure(text=str(self.ot7day)+' 次')
            self.OT8DayInfoLabel.configure(text=str(self.ot8day)+' 次')
            self.Leave1InfoLabel.configure(text=str(self.leave1day)+ ' 次')
            self.Leave2InfoLabel.configure(text=str(self.leave2day)+ ' 次')
            self.Ill1InfoLabel.configure(text=str(self.ill1day)+ ' 次')
            self.Ill2InfoLabel.configure(text=str(self.ill2day)+ ' 次')
            # 计算临工工资
            t = str(self.otadd) + "*( "+ str(self.ot7day) + " + "+str(self.ot8day)+ " * 2 ) = " \
                + str(self.otadd*(self.ot7day+self.ot8day*2))
            self.caluInfoLabel.configure(text=t)

            # 计算扣除工资
            tt = "- ( " + str(self.leave1day) + " + " + str(self.leave2day) + " * 2 )*"+str(self.leavecut)+" + " \
                "( " + str(self.ill1day) + " + " + str(self.ill2day) + " * 2 )*"+str(self.illcut)+" = -" \
                +str((self.leave1day+self.leave2day*2)*(self.leavecut)+((self.ill1day+self.ill2day*2)*(self.illcut)))
            self.decuctInfoLabel.configure(text = tt)

            # 预估到手工资
            te = str(self.basesalary) + ' - ' + str(self.tax) + ' + '+\
                 str((self.ot7day+self.ot8day*2)*(self.otadd))+ " - " + \
                 str((self.leave1day+self.leave2day*2)*(self.leavecut)) + " - " +\
                 str(40*(self.ill1day+self.ill2day*2))+" = " +\
                 str(self.basesalary-self.tax+self.otadd*(self.ot7day+self.ot8day*2)-
                     (self.leave1day+self.leave2day*2)*(self.leavecut)-
                     ((self.ill1day+self.ill2day*2)*(self.illcut)))
            self.calugetInfoLabel.configure(text=te)

            # 预估最高到手工资
            willget = self.CaluMaxGet()
            haveget = self.basesalary-\
                      self.tax+self.otadd*(self.ot7day+self.ot8day*2)-\
                      (self.leave1day+self.leave2day*2)*(self.leavecut)-\
                      (self.ill1day+self.ill2day*2)*(self.illcut)
            tm = str(haveget) +' + ' + str(willget) + ' = ' + str(haveget+willget)
            self.calumaxgetInfoLabel.configure(text=tm)

            time.sleep(0.1)

otc = OverTimeCalendar()
otc.CreateMainWin()
otc.CaluMaxGet()
otc.win.mainloop()