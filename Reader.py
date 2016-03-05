import urllib.request
from html.parser import HTMLParser
import re


class MyHTMLParser(HTMLParser):
    # def handle_starttag(self, tag, attrs):
    #     print("Encountered a start tag:", tag)
    # def handle_endtag(self, tag):
    #     print("Encountered an end tag :", tag)

    found_classes = False
    lines = []

    def handle_data(self, data):
        data = str(data).replace('\\n','')
        if data:
            self.lines.append(data)


class scheduledClass:
    def __init__(self,name,code,dates,classTimes,crosslist):
        self.name = name
        self.code = code
        self.dates = dates
        self.classTimes = classTimes
        self.crosslist = crosslist


class classTime:
    def __init__(self,crn,section,type,days,time,place,percent_full,prof,note):
        self.crn = crn
        self.section = section
        self.type = type
        self.days = days
        self.time = time
        self.place = place
        self.percent_full = percent_full
        self.prof = prof
        self.note = note


def get_data(year, terms, subject, district):
    # Terms are second of the two years, and 10, 20 or 30 based on semester
    # Fall 2015/2016 -> 201610
    # Subject is the code for the course
    # Computer Science -> CSCI
    # District is the location for the classes
    # All -> All
    # Halifax -> 100
    # Truro -> 200
    # Distance -> 300
    # Other -> 400
    # Place and Distance -> {{number}}D
    url = "https://dalonline.dal.ca/PROD/fysktime.P_DisplaySchedule?s_term=" + year + terms + "&s_subj=" + subject + "&s_district=" + district
    print(url)
    with urllib.request.urlopen(url) as response:
        return str(response.read())


def isInt(data):
    try:
        int(data)
        return True
    except ValueError:
        return False


def parse_classes(data):
    i = 0
    classes = []
    while (i < len(data)):
        class_row = data[i:i+5]
        i+=6
        name_arr = class_row[0].split()
        code = name_arr[0] + name_arr[1]
        name = ""
        for j in range(len(name_arr)-2):
            name = name + name_arr[2+j] + " "
        name = name.strip()
        crosslist = []
        if class_row[2] == 'Crosslisted with ':
            i-=3
            pattern = re.compile("\w{4} \d{4}")
            while pattern.match(data[i]):
                crosslist.append(str(data[i]).replace(" ",""))
                i+=2
            else:
                class_row = data[i-3:i+2]
                i+=2+len(crosslist)
        dates_raw = class_row[4].split()
        dates = []
        dates.append(dates_raw[1])
        dates.append(dates_raw[3])
        classTimes = []
        while isInt(data[i]):
            time_row = data[i:i+22]
            i+=22
            crn = time_row[0]
            section = time_row[1]
            type = time_row[2]
            days = []
            for j in range(5):
                if time_row[5+j] != ' ':
                    days.append(time_row[5+j])
            time = time_row[10]
            place = time_row[11]
            percent_full = str(time_row[16]).strip()
            prof = str(time_row[20]).strip()
            note = ""
            if (data[i] == "NOTE"):
                note = data[i+1]
                i+=2
            classTimes.append(classTime(crn,section,type,days,time,place,percent_full,prof,note))
            i+=1
        else:
            i-=1
        classes.append(scheduledClass(name,code,dates,classTimes,crosslist))
    return classes


content = get_data("2016","10","CSCI","100")
parser = MyHTMLParser()
parser.feed(content)
lines = parser.lines

start_ind = lines.index("BHrs") + 1
end_ind = lines[start_ind:len(lines)].index("Page ") + start_ind
classes_data = lines[start_ind:end_ind]

start_ind = lines.index("Page ") + 1
end_ind = lines[start_ind:len(lines)].index("next 20 CSCI classes >>") + start_ind
pages = lines[start_ind:end_ind]

# print(lines)
# print(classes_data)
# print(pages)

classes = parse_classes(classes_data)
print(classes)