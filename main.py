import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import TeacherInfo

import os

from dataclasses import dataclass

"""
Program is almost perfect unforunatley I am an impulisve thinker and didnt think twice when setting up a proxy
essentially im retarded and could of literally downloaded proton vpn to get away with it but I wanted to be fancy and use a stupid little free
proxy which arent even safe in the first place and are slower also they almost never work.

PROTON VPN

Im very dissapointed in myself. I havent learned a single lesson as I would do it again if I could. All that I have learned is my brain is not as
good as I thought it was. Everyone makes mistakes but this is just stupid and dissapointing. Nothing about this was impressive if I got caught. 

No point in robbing a bank if you got caught (slighty different situaion but point is clear). 

Why would I make an assumption that the proxy would just immediatley work in the code if I activated it on my system.
I aways extesnivley test program but not in time when it really mattered. I am now suspended for 5 days which I dont care it dosent affect me.
My pride is just hurt because I got caught doing a cool thing in a stupid way.

Also the whole idea of the program was testing my abilities and staying anonymous is a big part of it. I could of used this as an oppertunity 
to learn proxy chains (proxys connecting to other proxies before connecting to the actual request).
"""

login_url = r"https://sisssrsb.ednet.ns.ca/subs/home.html" # subsitute portal
main_url = r"https://sisssrsb.ednet.ns.ca"
logout_url = r"https://sisssrsb.ednet.ns.ca/~loff"


@dataclass
class Attendance_Info:
    section_id: str
    frn: str
    att_period: str
    att_date: str
    Att_Mode_Code: str
    pagetype: str
    ATT_Source_Code: str
    Period_ID: str
    url: str


def main():   
    for e in range(len(TeacherInfo.teacher_ids)):
        print(f"Teacher {TeacherInfo.teacher_ids[e]}:")
        with requests.Session() as s:
            login = s.post(login_url,login_info(e), allow_redirects=True) # login through subsitute portal
            cookie_string = "; ".join([str(x)+"="+str(y) for x,y in s.cookies.items()]) # convert cookies to string

            data = create_post_json(s, login.text)
            for i in range(len(data[0])): # loop every class

                post_headers = { # not sure if all this is needed but it works so why change it.
                "Cookie" : (cookie_string), # very nececcary
                "Host" : "sisssrsb.ednet.ns.ca",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Length": "42612",
                "orgin" : "https://sisssrsb.ednet.ns.ca",
                "Connection": "keep-alive",
                "Referer": main_url + str(data[1][i]),
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-orgin",
                "Sec-Fetch-User": "?1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
                "Content-Type" : "application/x-www-form-urlencoded"
                }

                e = s.post(login_url, data[0][i], headers=post_headers) # posting absence to current class in loop
                print(f"Class {i} post {'success' if e.status_code == 200 else 'fail'}")

            s.get(logout_url) # signout
            s.close()

        
    
def create_post_json(s: requests.Session(), login_page): # creates list that has all the post request data needed for current login
    url_info = get_url_information(s,login_page)
    post_list = [[], []]

    for a in range(len(url_info)):
        cur_info = url_info[a] # data for current attendance link
        student_codes = get_student_codes(main_url + cur_info.url, a, s) # gets student codes used in the post
        json = {}

        for i in range(len(student_codes[0])): # loop amount of classes with attendace which is available to change
            json.update({student_codes[0][i]: "A", student_codes[1][i]: ""}) # Absent, no comment

        json.update({ # post data
            "savecomments": "0",
            "Att_Mode_Code": cur_info.Att_Mode_Code,
            "Start_date": cur_info.att_date,
            "end_date": cur_info.att_date,
            "sectionid" : cur_info.section_id,
            "period_id": cur_info.Period_ID,
            "att_period": cur_info.att_period,
            "ATT_Source_Code": cur_info.ATT_Source_Code,
            "ac": "ATT_RecordMeetingTeacher"
        })
        post_list[0].append(json) # post data
        post_list[1].append(cur_info.url) # url for headers
    return post_list




def get_url_information(s: requests.Session(), login_page): # returns disected data from within the url which is needed for the post request
    url_information = []
    soup = BeautifulSoup(login_page, features='html.parser') # Create BeatifulSoup object for websites html code
    for a in soup.findAll("a", href=True, title="Take Attendance"): # find all buttons (a) that have an href and the title "Take Attendance"
        url = a['href'] # get href
        split_url = url.replace("?", "&").split("&") # split up the url so I can disect data from it
        values = list(dict(x.split("=") for x in split_url[1:]).values()) # format data
        values.append(url) # add url

        url_information.append(Attendance_Info(*values)) # enter it into easy to read dataclass
    return url_information


def get_student_codes(url, index, s:requests.Session()): # returns codes that match with student for post
    student_codes = [[], []] # codes that corolate to all present students
    page = s.get(url)

    soup = BeautifulSoup(page.text, features="html.parser") # open page for parsing

    table = soup.find('table', attrs={"id" : "attendance-table"}) # get attendance table
    att_input = table.findAllNext("input", attrs={"type": "text"}) # input ids for post that is inside site input. 
    att_comment = table.findAllNext("input", attrs={"type": "hidden", 'name': lambda x: x != "studentTrack"} ) # comment ids (student track leads to sum else)
    for a,b in zip(att_input, att_comment): 
       student_codes[0].append(a['name']) # student 
       student_codes[1].append(b['name']) # comment
     
    return student_codes

def login_info(index: int): # returns login info of chosen teacher
    return{
        "schoolid": "Park+View+Education+Centre",
	    "teacher": TeacherInfo.teacher_ids[index],
	    "pw": "PVEC",
	    "teacherid": TeacherInfo.teacher_ids[index]
    }

if __name__ == "__main__":
    os.system("clear")
    print("\n\n\n\n\-------------------------------\n\n\n\n")
    main()
    