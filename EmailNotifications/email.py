import Facade_API
import urllib.request as ur
import json
from datetime import datetime, timedelta

def timeDefined(date):
    y=str(date.year)
    m=str(date.month)
    d=str(date.day)
    if len(d)==1:
        d ='0'+d
    if len(m)==1:
        m ='0'+m
    return str(y)+'-'+str(m)+'-'+str(d)

def weekDate(date):
    date_today = timeDefined(date)
    date_prev = timeDefined(date - timedelta(days=7))
    return date_prev, date_today

def isSafePSI(value):
    if value<=50:
        return "healthy"
    elif 51<value<=100:
        return "moderate"
    elif 101<value<=200:
        return "unhealthy"
    elif 201<value<=300:
        return "very unhealthy"
    else:
        return "hazardous"

def isSafePM25(value):
    if 0<value<=12:
        return "healthy"
    elif 12<value<=35.4:
        return "moderate"
    elif 35.4<value<=55.4:
        return "unhealthy for sensitive groups"
    elif 55.4<value<=150.4:
        return "unhealthy"
    elif 150.4<value<=250.4:
        return "very unhealthy"
    else:
        return "hazardous"

def getTop5Dengue():
    top5=[]
    url = 'https://api-scheduler.herokuapp.com/'
    url_parser = ur.urlopen(ur.Request(url))
    info = url_parser.read()
    json_dict = json.loads(info.decode('utf-8'))
    total_cases = json_dict['total_cases']
    data = json_dict['top5']
    for d in data:
        top5.append(d[0][:-1])
    return top5


def rangeHaze():
    date = datetime.now().date()
    API = Facade_API.FacadeAPI()
    date_str=weekDate(date)
    today_psi = API.getHaze()['psi']['national']
    today_pm25 = API.getHaze()['pm25']['national']
    prev_psi = API.haze.getJSONHazeRange(date_str[0])['psi']['national']
    prev_pm25 = API.haze.getJSONHazeRange(date_str[0])['pm25']['national']
    if today_psi<prev_psi:
        range_str_psi= str(today_psi)+'-'+str(prev_psi)
        maxm_psi = prev_psi
    else:
        range_str_psi= str(prev_psi)+'-'+str(today_psi)
        maxm_psi = today_psi
    if today_pm25<prev_pm25:
        range_str_pm25= str(today_pm25)+'-'+ str(prev_pm25)
        maxm_pm25 = prev_pm25
    else:
        range_str_pm25= str(prev_pm25)+'-'+str(today_pm25)
        maxm_pm25 = today_pm25
    psi_status = isSafePSI(maxm_psi)
    pm25_status = isSafePM25(maxm_pm25)
    top5 = getTop5Dengue()
    return {'psi':range_str_psi, 'pm25':range_str_pm25, 'psi_status': psi_status, 'pm25_status': pm25_status, 'locations': top5}

def getDengue():
    url = 'https://api-scheduler.herokuapp.com/'
    url_parser = ur.urlopen(ur.Request(url))
    info = url_parser.read()
    json_dict = json.loads(info.decode('utf-8'))
    return json_dict['total_cases']

def createMessage(date, time, haze, dengue):
    return  "To: PMO\n\nHonorable Prime Minister,\n\nWe respectfully request your attention to the Crisis Management System (CMS) status report on %s at %s which mainly focuses on the emergency situations for the dengue outbreak and haze.\n\nBased on the reported cases, there have been, in total, %s number of dengue outbreaks within Singapore, as of today with the top affected areas:\n\n%s\n%s\n%s\n%s\n%s\n\nMoreover, the psi range for haze has been: %s (%s) and pm25 range %s (%s), this week between %s to %s.\n\nWe are still monitoring the situation and will be sending an updated status report in 30 min time.\n\nRespectfully,\nCrisis Management System Team"%(date, time, dengue, haze['locations'][0], haze['locations'][1], haze['locations'][2], haze['locations'][3], haze['locations'][4], haze['psi'], haze['psi_status'], haze['pm25'], haze['pm25_status'], weekDate(date)[0], weekDate(date)[1])

def sendEmail(recipient, msg, subject):
    API = Facade_API.FacadeAPI()
    status = API.sendEmail(recipient, msg, subject)
    return status

def sendNotificationEmail(recipient):

    date = datetime.now().date()
    time = str(datetime.now().hour) + ':'+ str(datetime.now().minute)
    haze = rangeHaze()
    dengue = getDengue()

    subject = "Updated status report on "+ str(date) +" at " + str(time)
    # recipient = ['aditisaini99@gmail.com']
    msg = createMessage(date, time, haze, dengue)

    sendEmail(recipient, msg, subject)
