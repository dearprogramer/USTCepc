# coding=utf-8
import urllib.request
import urllib
import gzip
import http.cookiejar
from bs4 import BeautifulSoup
from tkinter import *
from PIL import Image, ImageTk
import re
import time
from html5lib import *
from pandas import *
class webSearch:
    def __init__(self,baseurl,head,coding):
        self.baseurl=baseurl
        self.head=head
        self.coding=coding
        self.getOpener(head)



    def getOpener(self,head):
        # deal with the Cookies
        cj = http.cookiejar.CookieJar()
        pro = urllib.request.HTTPCookieProcessor(cj)
        self.opener = urllib.request.build_opener(pro)
        header = []
        for key, value in head.items():
            elem = (key, value)
            header.append(elem)
        self.opener.addheaders = header
        return self.opener

    # 定义一个方法来解压返回信息
    def ungzip(self,data):
        try:  # 尝试解压
            print('正在解压.....')
            data = gzip.decompress(data)
            print('解压完毕!')
        except:
            print('未经压缩, 无需解压')
        return data

    def findAll(self,html,tagname,reps=None):
        self.bs4=BeautifulSoup(html,"html5lib")
        if reps is None:
            sb = self.bs4.find_all(tagname)
        else:
            sb=self.bs4.find_all(tagname,attrs=reps)
        return sb

    def getHtml(self,dir):
        url=self.baseurl+dir
        req=urllib.request.Request(self.baseurl+dir)
        page = self.opener.open(req).read()
        page = page.decode(self.coding)
        return page

    def postRequest(self,dir,postDict):
        url=self.baseurl+dir
        postData = urllib.parse.urlencode(postDict).encode()
        op = self.opener.open(url, postData)
        data = op.read()
        data =self.ungzip(data)
        data=data.decode("gb2312")
        print("response data:"+data)
        return data


    def saveImgs(self,prefix,imgUrls):
        size=len(imgUrls)
        timeStr= time.strftime("%m-%d-%H-%M-%S", time.localtime())
        imgList=list()
        for i in range(size):
            imgurl = "%s.bmp" % i
            imgurl=prefix+timeStr+imgurl
            tempurl=imgUrls[i]
            captchadata = self.opener.open(tempurl).read()
            with open(imgurl, 'wb') as file:
                file.write(captchadata)
            imgList.append(imgurl)
        return imgList

class dataTransform:
    def __init__(self):
        self.weekdic = {"周一": 1, "周二": 2, "周三": 3, "周四": 4, "周五": 5, "周六": 6, "周日": 7}
        self.Tweekdic = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五", 6: "周六", 7: "周日"}
        self.courseState={"预 约":1,"已达预约上限":2,"取 消":3,"您已经预约过该时间段的课程":4}
        self.reserveState={"已刷卡上课":1,"预约中":2}

    @staticmethod
    def extractNum(datalist):
        partern=re.compile("\d+")
        result=list()
        for it in datalist:
            temps=partern.findall(it)
            if len(temps)>0:
                value=int(temps[0])
                result.append(value)
        return result

    @staticmethod
    def getNumsFromString(s):
        partern = re.compile("\d+")
        result = list()
        temps = partern.findall(s)
        for it in temps:
            result.append(int(it))
        return result


    def getReserveTime(self,datalist):
        partern = re.compile(r"\d\d:\d\d:\d\d")
        result=list()
        for it in datalist:
            temps=partern.findall(it)
            if len(temps)>0:
                value=temps[0]
                date =it.replace(value, "", 1)
                datetime = date + "-" + value
                t1=pandas.to_datetime(datetime,format="%Y/%m/%d-%H:%M:%S")
                result.append(t1)
        return result

    def getDayTimeStr(self,datalist):
        partern_sub = re.compile(r"\d\d:\d\d")
        BeginTime=list()
        for it in datalist:
            temps = partern_sub.findall(it)
            if len(temps) > 0:
                temp1 = partern_sub.findall(it)
                if len(temp1) > 0:
                    BeginTime.append(temp1[0])
        return BeginTime

    def getCourseTime(self,datalist):
        partern = re.compile(r"\d\d:\d\d-\d\d:\d\d")
        partern_sub = re.compile(r"\d\d:\d\d")
        BeginTime=list()
        EndTime=list()
        for it in datalist:
            temps = partern.findall(it)
            if len(temps) > 0:
                temp1 = partern.findall(it)
                v0 = ""
                v1 = ""
                v2 = ""
                if len(temp1) > 0:
                    v0 = temp1[0]
                dates = it.replace(v0, "", 1)
                temp2 = partern_sub.findall(v0)
                if len(temp2) > 0:
                    v1 = temp2[0]
                    v2 = temp2[1]
                stime1 = dates + "-" + v1
                stime2 = dates + "-" + v2
                time1=pandas.to_datetime(stime1, format="%Y/%m/%d-%H:%M")
                time2 =pandas.to_datetime(stime2, format="%Y/%m/%d-%H:%M")
                BeginTime.append(time1)
                EndTime.append(time2)
        return BeginTime,EndTime

    def getweekday(self,datalist):
        result=list()
        for it in datalist:
            value=self.weekdic[it]
            result.append(value)
        return result

    def getCouserState(self,datalist):
        result = list()
        value=None
        for it in datalist:
            if it in self.courseState.keys():
                value=self.courseState[it]
            else:
                tl=len(self.courseState)+1
                self.courseState.__setitem__(value,tl)
                value=tl
            result.append(value)
        return result

    def getReserveState(self,datalist):
        result = list()
        for it in datalist:
            value=self.reserveState[it]
            result.append(value)
        return result

    @staticmethod
    def decoupleHeader(header):
        properdic = dict()
        tempresult = str.split(header, "?", 1)
        url = tempresult[0]
        propers = tempresult[1].split("&")
        properdic.__setitem__("url", url)
        for it in propers:
            tv = it.split("=")
            if len(tv) > 1:
                properdic.__setitem__(tv[0], tv[1])
            else:
                properdic.__setitem__(tv[0], "")
        return properdic

class dataDeal:
    def __init__(self):
        self.header={1:"title",2:"weekNo",3:"day",4:"teacher",5:"hours",6:"scheduled",7:"address",8:"reserveBegin",9:"reserveEnd",
                           10:"avaluable",11:"nownum",12:"coursefile",14:"action",13:"state"}
        self.reservationHeader={0:"title",1:"teacher",2:"hours",3:"semeter",4:"weekNo",5:"day",6:"scheduled",7:"address",8:"seat",9:"state"
            ,10:"action"}
        self.df=DataFrame()
        self.dataTrans = dataTransform()

    def getCourseData(self,data):
        df=DataFrame()
        df["title"]=data[1]
        df[self.header[2]]=self.dataTrans.extractNum(data[2])
        df[self.header[3]] = self.dataTrans.getweekday(data[3])
        df[self.header[4]] = data[4]
        df[self.header[5]] = self.dataTrans.extractNum(data[5])
        beginT=self.dataTrans.getDayTimeStr(data[6])
        df["begintime"]=beginT
       # df["endtime"]=endT
        df[self.header[7]]=data[7]
        df[self.header[8]] = self.dataTrans.getReserveTime(data[8])
        #df[self.header[9]] = self.dataTrans.getReserveTime(data[9])
        #df[self.header[10]] = self.dataTrans.extractNum(data[10])
        #df[self.header[11]] = self.dataTrans.extractNum(data[11])
        df[self.header[13]] = self.dataTrans.getCouserState(data[13])
        df[self.header[14]] = data[14]
        print(df)
        return df

    def getReservationData(self,data):
        df=DataFrame()
        df[self.reservationHeader[0]]=data[0]
        df[self.reservationHeader[1]] = data[1]
        df[self.reservationHeader[2]] = self.dataTrans.extractNum(data[2])
       # df[self.reservationHeader[3]] = data[3]
        df[self.reservationHeader[4]] = self.dataTrans.extractNum(data[4])
        df[self.reservationHeader[5]] = self.dataTrans.getweekday(data[5])
        beginT, endT = self.dataTrans.getCourseTime(data[6])
        df["begintime"] = beginT
        df[self.reservationHeader[7]] = data[7]
        df[self.reservationHeader[9]] = data[9]
        df[self.reservationHeader[10]] = data[10]
        print(df)
        return df

class ImfoProcess:
    def __init__(self):
        self.header = {
    'Connection': 'Keep-Alive',
    'Accept-Language': 'zh-Hans-CN,zh-Hans;q=0.5',
    'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest',
    'Host': 'http://epc.ustc.edu.cn',}
        self.coding="gb2312"
        self.baseurl='http://epc.ustc.edu.cn/'
        self.courseEn={1:"title",2:"weekNo",3:"day",4:"teacher",5:"hours",6:"scheduled",7:"address",8:"reserveBegin",9:"reserveEnd",
                           10:"avaluable",11:"nownum",12:"coursefile",14:"action",13:"state"}
        self.courseCn={1:"课题",2:"周数",3:"星期",4:"老师",5:"课时",6:"上课时间",7:"地点",8:"开始预定时间",9:"结束预定时间",
                           10:"可预约",11:"已预约",12:"课件",14:"预定",13:"状态"}
        self.resevationCn={0:"title",1:"teacher",2:"hours",3:"semeter",4:"weekNo",5:"day",6:"scheduled",7:"address",8:"seat",9:"state"
            ,10:"action"}
        self.webdeal = webSearch(self.baseurl, self.header, self.coding)

    def cancelReservation(self,url):
        tempdic={"submit_type":"book_cancel","截止日期" :"end_date"}
        data=self.webdeal.postRequest(url,tempdic)

    def reserve(self,url):
        tempdic={"submit_type":"book_submit"}
        data=self.webdeal.postRequest(url,tempdic)

    def getloginImg(self):
        content = self.webdeal.getHtml("n_left.asp")
        imgs = self.webdeal.findAll(content, "img", {"src": re.compile(r'^checkcode')})
        imgurls = list()
        size = len(imgs)
        for i in range(size):
            txt = imgs[i].attrs["src"].split(" ")
            tempurl = self.baseurl + txt[0] + "%" + txt[1]
            imgurls.append(tempurl)
        imgdirs = self.webdeal.saveImgs("epc", imgurls)
        tempurl = imgdirs[0]
        return tempurl

    def logout(self):
        dir="main.asp?exit=Y"
        data=self.webdeal.getHtml(dir)
        print(data)

    def login(self,id,password,code):
        formdir="n_left.asp"
        postDict = {
            'name': id,
            'pass': password,
            "submit_type": "user_login",
            "user_type":2,
            "Submit":"LOG IN",
            "txt_check":code
        }
        self.webdeal.postRequest(formdir,postDict)

    def displayleft(self,n,m):
        dir="n_left.asp?base_id="+str(n)+"&second_id="+str(m)
        page=self.webdeal.getHtml(dir)
        linklist=self.webdeal.findAll(page,"a",{"href": re.compile('second_id')})
        courseclass=dict()
        for tl in linklist:
            print(tl.text+":"+tl.attrs["href"])
            courseclass.__setitem__(tl.text,tl.attrs["href"])
        return courseclass

    def getCourseInfo(self,secondid,maxpage=10):
        dir="m_practice.asp?second_id="+str(secondid)
        page=self.webdeal.getHtml(dir)
        bs=BeautifulSoup(page)
        pageno=0
        datadic=dict()
        pageset=set()
        firstpage=bs.find("a",attrs={"title":"上一页"}).attrs["href"]
        pageset.add(firstpage)
        iscontinue=1
        rows=0
        for i in range(14):
            datadic.__setitem__(i+1,list())
        print(datadic.keys())
        while iscontinue:
            table = bs.find("table", attrs={"style": re.compile('TABLE-LAYOUT')})
            nextpage = bs.find("a", attrs={"title": "下一页"}).attrs["href"]
            nextpage=str.strip(nextpage)
            print("nextpage:"+self.baseurl+nextpage)
            tempno=int(dataTransform.decoupleHeader(nextpage)["page"])
            iscontinue=(pageno<tempno) and (pageno<maxpage)
            pageno=tempno
            if table is not None:
                for idx, tr in enumerate(table.find_all('tr')):
                    if idx != 0:
                        for idy,it in enumerate(tr.find_all('td')):
                            txt=it.text
                            if txt is not None:
                               datadic[idy+1].append(str.strip(txt))
                            else:
                                datadic[idy+1].append("None")
                   # datadic[13].append(tr.attrs["action"])
                        inputs=tr.find_all("input",attrs={"type":"submit"})
                        if len(inputs)>0:
                            datadic[13][rows]=datadic[13][rows]+inputs[0].attrs["value"]
                        rows=rows+1
            for form in table.find_all('form'):
                    datadic[14].append(form.attrs["action"])
            page=self.webdeal.getHtml(nextpage)
            bs=BeautifulSoup(page)

        dd=dataDeal()
        rs=dd.getCourseData(datadic)
        return rs

    def getReservationInfo(self):
        dir="record_book.asp"
        postdic={"querytype":"all"}
        html=self.webdeal.postRequest(dir, postdic)
        bs=BeautifulSoup(html)
        datadic=dict()
        infos=list
        table = bs.find("table", attrs={"cellspacing":"2"})
        for i in range(11):
            datadic.__setitem__(i,list())
        if table is not None:
            for idx, tr in enumerate(table.find_all('tr',attrs={"bgcolor":"#ffe6ff"})):
                for idy, it in enumerate(tr.find_all('td')):
                    txt = it.text
                    if txt is not None:
                        datadic[idy].append(str.strip(txt))
                    else:
                        datadic[idy].append("None")
            for idz , form in enumerate(table.find_all('form')):
                    datadic[10][idz]=datadic[10][idz]+form.attrs["action"]
            infodic=dict()
            dd=dataDeal()
            rs=dd.getReservationData(datadic)
            grouped=rs.groupby(["state"]).sum()
            print("data size:"+str(len(grouped)))
            for i in range(len(grouped)):
                infodic.__setitem__(grouped.iloc[i].name,grouped.iloc[i,0])
            print(infodic)
        return infodic,rs

    def Search(self,searchdic):
        pddic=dict()
        resultpd=None
        for key,value in searchdic.items():
            #print("condition:"+value)
            couseid=value[0]
            week=value[1]
            day=value[2]
            ctime=value[3]
            print("ctime:"+ctime)
            pd=DataFrame
            result=list()
            if couseid not in pddic.keys():
                pd=self.getCourseInfo(couseid,4)
                pddic.__setitem__(couseid,pd)
            else:
                pd=pddic[couseid]
            temppd=pd[((pd["state"]<=2))& (pd["begintime"]==ctime)]
            if week!=0:
                temppd=temppd[temppd["weekNo"]==week]
            if day!=0:
                temppd = temppd[temppd["day"] == day]

            temppd.sort_values(by="weekNo")
            print("here")
            print(temppd)
            if len(temppd)>0:
                resultpd=temppd.values[0]
                result.append(resultpd)
        return result



class Display:
    def __init__(self):
        self.infp=ImfoProcess()
        self.islogin=0
        tempurl=self.infp.getloginImg()
        master = Tk()
        master.title("中科大epc登陆")
        img = Image.open(tempurl)  # 打开图片
        photo = ImageTk.PhotoImage(img)  # 用PIL模块的PhotoImage打开
        Label(master, text="学号：").grid(row=0, sticky=W)
        Label(master, text="密码：").grid(row=1, sticky=W)
        Label(master, image=photo).grid(row=2, sticky=W)
        self.studentid = StringVar()
        self.studentpassword = StringVar()
        self.nums = StringVar()
        e1 = Entry(master, textvariable=self.studentid)
        e2 = Entry(master, textvariable=self.studentpassword, show="*")
        e3 = Entry(master, textvariable=self.nums)
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        e3.grid(row=2, column=1)
        button1 = Button(master, text="登陆", command=self.commit)
        button1.grid(row=0, column=2, columnspan=2, rowspan=2, padx=5,
                    pady=5, sticky=W + E + N + S)
        mainloop()

    def commit(self):
        self.infp.login(self.studentid.get(),self.studentpassword.get(),self.nums.get())
        begintime="2018-05-07 14:30:00"
        #self.infp.login("SA17168009", "WWHFLQ", self.nums.get())
        self.islogin=1
        #self.infp.displayleft(2,0)
        pdr=self.infp.getCourseInfo(2001,1)
        pdrs=pdr[(pdr["begintime"]==begintime)]
        print("this:")
        #self.infp.getReservationInfo()
        print(pdrs)

    def __del__(self):
        if self.islogin:
            self.infp.logout()
        print("log out!")

