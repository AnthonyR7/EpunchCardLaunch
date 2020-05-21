from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.urls import reverse
import re
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime, timedelta
from time import strptime
from django.core import serializers
from calendar import monthrange
import json
# collections is used to order my dictionary
def index(request):
    return render(request, "EpunchCard/index.html")

def regPg(request):
    return render(request, "EpunchCard/registerPg.html")

def register(request):
    errors = StaffMember.objects.reg_validator(request.POST)
    # print("this is the request POST data: ", request.POST)
    if len(errors):
        for words in errors:
            messages.error(request, words)
        return redirect("/regPg")
    else:
        great =[]
        great.append("Successfully Registered, Thank you")
        for good in great:
            messages.success(request, good)
        hash1 = make_password(request.POST['password'], salt = None, hasher = 'default')
        # print (hash1)
        user = StaffMember.objects.create(
            name = request.POST['name'],
            title = request.POST['title'], 
            password = hash1, 
            email = request.POST["email"]
            )
        # Assign the created user to the PunchCard
        PunchCard.objects.create(employee = user)
    return render(request, "EpunchCard/index.html")

def login(request):
    errors = StaffMember.objects.log_validator(request.POST)
    if len(errors):
        for words in errors:
            messages.error(request, words)
    else:
        conformed_user = StaffMember.objects.get(email = request.POST['confirm_email'])
        request.session['client'] = {
            "id" : conformed_user.id
        }
        return redirect("/dashboard")
    return redirect('/')

def pretty(item):
    if "-" in item:
        prettyItem = int(item.replace("-", ""))
        # print("there is a -")
        return prettyItem
    else:
        # print("no -")
        return item
        
def villageTotalPoint(allVillagers):
    total = ""
    allpoints = []
    for staff in allVillagers:
        allpoints.append(staff.total)
    
    total = sum(allpoints)
    print("This is from vaillageTotalPoint ",total)
    
    return total


def grabCurrentWeek(user):
    now = datetime.now()
    currentWeekDayNum = now.strftime("%w")
    dayOfMonth = now.strftime("%d")
    dayNum = int(currentWeekDayNum)
    firstDayOfWeek = dayNum - int(dayOfMonth)
    userClock = PunchCard.objects.get(employee = StaffMember.objects.get(name = user))
    start_day = pretty(str(firstDayOfWeek))
    # print(userClock)
    clockWeek = []
    for i in range(7):
        # print(now.strftime("%m") + "-" + str(int(start_day) + i) + "-" + now.strftime("%Y"))
        # print(date(int(now.strftime("%Y")), int(now.strftime("%m")), int(pretty(str(firstDayOfWeek))) + i ))
        for clock in userClock.clock:
            if clock["date"] == (now.strftime("%m") + "/" + str(int(start_day) + i) + "/" + now.strftime("%Y")):
                clockWeek.append(clock)
                print("yes")
    # print(clockWeek)
    # Works
    return clockWeek
# Only use runTotalPoints func for manauly applying all days points to main total
# def runTotalPoints(staffName):
#     print(staffName, "ererefsd")
#     mainModel = StaffMember.objects.get(name = staffName)
#     staffPunchCard = PunchCard.objects.get(employee = StaffMember.objects.get(name = staffName))
#     for clock in staffPunchCard.clock:
#         if "points" in clock:
#             staffPunchCard.employee.total = float(clock["points"]) + float(staffPunchCard.employee.total)
#     else:
#         print("there was an problem")
#     return staffPunchCard.employee.total
        

def dashboard(request):
    now = datetime.now()
    totalEmployees = []
    everybody = StaffMember.objects.all()
    # for person in everybody:
    #     print("Name and total: " + person.name ,""  "" ,runTotalPoints(person.name))
    #     singleStaff = StaffMember.objects.get(name = person.name)
    #     singleStaff.total = runTotalPoints(person.name)
    #     singleStaff.save()
    
    
    for staff in everybody:
        totalEmployees.append(staff)

    wholeDay = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
    # Check if there is a session
    try:
        user = StaffMember.objects.get(id = request.session['client']['id'])
    except:
        return redirect("/")

    userPunchCard = PunchCard.objects.get(employee = StaffMember.objects.get(name = user.name))
    # print(userPunchCard)
    # Incase there are no other users. Only used for new users
    try:
        otherClocks = PunchCard.objects.exclude(employee = StaffMember.objects.get(name = user.name))
        # for info in otherClocks:           
        #     print (info.employee.name, "hello")
    except:
        otherClocks = None
        # print("except was hit")

    if not userPunchCard.clock:
        # print ("Displaying Data from Completely New User")
        status = "Clock in"
        content = {
            "name" : user.name,
            "title" : user.title,
            "status" : status,
            "clocks" : otherClocks,
            "staff" : totalEmployees,
            "villagerPoints" : "0",
            "allVillagerPoints" : villageTotalPoint(totalEmployees)
        }
        return render(request, "EpunchCard/dashboard.html", content)
    else:
       
        newClocker = userPunchCard.clock.copy()

        if not any(dObj['date'] == wholeDay for dObj in userPunchCard.clock):
            for clockInfo in userPunchCard.clock:
                status = "Clock In"
                # Reverse to place latest data entry in clocks
                newClocker.reverse()
                content = {
                    "name" : user.name,
                    "title" : user.title,
                    "date" : " ",
                    "clockIn" : " ",
                    "clockOut" : " ",
                    "dbPoints" : " ",
                    "timeSpent" : " ",
                    "desc" : " ",
                    "clocks" : otherClocks,
                    "wholeClock" : newClocker,
                    "status" : status,
                    "staff" : totalEmployees,
                    "villagerPoints" : user.total,
                    "allVillagerPoints" : villageTotalPoint(totalEmployees)
                }
                print(" the clocker ",newClocker)
                return render(request, "EpunchCard/dashboard.html", content)

        else:
            # Dont want modify the orignal so, copy is used to pop(currentDate) and reverse()
            # newClocker = userPunchCard.clock.copy()

            for clockInfo in newClocker:
                if clockInfo.get("date") == wholeDay:
                    # print(clockInfo)

                    if clockInfo.get('clockOut') != None:
                        status = "Day Completed"
                        # print ("day completed")
                    else:
                        status = "Clock Out"
                        # for the sake of Day completed
                        # print ("clock out")
                    # newClocker is all the clock data from current user with current date
                    # excluded
                    
                    newClocker.pop(newClocker.index(clockInfo))
                    newClocker.reverse()

            content = {
                "name" : user.name,
                "title" : user.title,
                "date" : clockInfo.get("date"),
                "clockIn" : clockInfo.get("clockIn"),
                "clockOut" : clockInfo.get("clockOut"),
                "dbPoints" : clockInfo.get("points"),
                "timeSpent" : clockInfo.get("timeSpent"),
                "desc" : clockInfo.get("desc"),
                "clocks" : otherClocks,
                "wholeClock" : newClocker,
                "status" : status,
                "staff" : totalEmployees,
                "villagerPoints" : user.total,
                "allVillagerPoints" : villageTotalPoint(totalEmployees)
            }
            return render(request, "EpunchCard/dashboard.html", content)

    # two different returns because javascript functions make the disappearing act ugly
    try:
        address = request.META['HTTP_REFERER']
        if "dailyUpdate" in address:
            return render(request, "EpunchCard/manager.html", content)

    except:
        # this would raise a keyError when my browser opens old tabs or when shuts down becuase of no power
        return redirect("/")

    # Starts crying about (local variable 'form' referenced before assignment)(Only when there is nothing)
    status = "Clock in"
    content = {
        "name" : user.name,
        "title" : user.title,
        "status" : status
    }
    return render(request, "EpunchCard/dashboard.html", content)

def logOut(request):
    # if key not in session uses except
    try:
        del request.session['client']
        # print ("Key will be del, redirect activated")
        return redirect('/')
    except:
        # print ("except was hit")
        return redirect('/')
    return redirect('/')
    
def checkGivenPoints(num):
    try:
        float(num)
        fate = True
    except:
        fate = False
    return fate

def addExtraPointTotal(request):
    staffData = request.POST.getlist("getData[]", None)
    who = staffData[0]
    point = staffData[1]


    employee = StaffMember.objects.get(name = who)
    employee.total = employee.total + int(point)
    employee.save()
    # print("employe: " , employee.name)
    return {employee.name, employee.total}

def points(request):
    now = datetime.now()
    wholeDay = str(now.month) + "/" + str(now.day) + "/" + str(now.year)

    points = request.POST["points"]
    reason = request.POST["reason"]
    employee = request.POST["person"]
    
    dayOfInput = request.POST["staffInputDate"]
    # print(dayOfInput, "here is the date for today")
    if len(points) == 0 and len(reason) == 0:
        messages.error(request, "Form must not be empty, try again")


    else:
        if checkGivenPoints(points) == False:
            messages.error(request, "Points given must be a number, please resubmit form.")
            

        else:
            # print("Good to submit")
            chosenEmployee = PunchCard.objects.get(employee = StaffMember.objects.get(name = employee))
            goodMessage = "Successfully added more points to " + employee
            for clock in chosenEmployee.clock:
                if clock["date"] == dayOfInput:
                    clock["points"] = float(points) + float(clock["points"])
                    chosenEmployee.save()
                    # print("found the day today")
                    goodMessage = "Successfully added " + points +" more points to " + employee + " total ("+ str(clock["points"]) +") for " + dayOfInput 
                    messages.success(request, goodMessage)
                    break
            else:
                # print("There is no clock in today")
                messages.error(request, "Error: No report for date " + dayOfInput + " , please fill out your Daily Report.")
        

        # left off here 11/19/19
    return redirect("/dailyUpdate")
# def graph(request):
#     return render(request, "EpunchCard/points.html")
def settings(request):
    now = datetime.now()    
    wholeDay = str(now.month) + "/" + str(now.day) + "/" + str(now.year)

    try:
        user = StaffMember.objects.get(id = request.session['client']['id'])
    except:
        return redirect("/")

    userPunchCard = PunchCard.objects.get(employee = user)

    if not userPunchCard.clock:
        # print ("Displaying Data from Completely New User")
        status = "Clock in"
        content = {
            "name" : user.name,
            "status" : status,
        }
        return render(request, "EpunchCard/settings.html", content)
    else:
        newClocker = userPunchCard.clock.copy()

        if not any(dObj['date'] == wholeDay for dObj in userPunchCard.clock):
            for clockInfo in userPunchCard.clock:
                status = "Clock In"                
                content = {
                    "name" : user.name,
                    "status" : status,
                }
                return render(request, "EpunchCard/settings.html", content)
        else:
            for clockInfo in newClocker:
                if clockInfo.get("date") == wholeDay:
                    # print(clockInfo)

                    if clockInfo.get('clockOut') != None:
                        status = "Day Completed"
                        # print ("day completed")
                    else:
                        status = "Clock Out"
                        # for the sake of Day completed
                        # print ("clock out")

            content = {
                "name" : user.name,
                "status" : status,
            }
            return render(request, "EpunchCard/settings.html", content)

    return render(request, "EpunchCard/settings.html")

def report(request):
    now = datetime.now()    
    wholeDay = str(now.month) + "/" + str(now.day) + "/" + str(now.year)

    try:
        user = StaffMember.objects.get(id = request.session['client']['id'])
    except:
        return redirect("/")

    userPunchCard = PunchCard.objects.get(employee = user)

    if not userPunchCard.clock:
        # print ("Displaying Data from Completely New User")
        status = "Clock in"
        content = {
            "name" : user.name,
            "status" : status,
        }
        return render(request, "EpunchCard/dailyReport.html", content)
    else:
        newClocker = userPunchCard.clock.copy()

        if not any(dObj['date'] == wholeDay for dObj in userPunchCard.clock):
            for clockInfo in userPunchCard.clock:
                status = "Clock In"                
                content = {
                    "name" : user.name,
                    "status" : status,
                }
                return render(request, "EpunchCard/dailyReport.html", content)
        else:
            for clockInfo in newClocker:
                if clockInfo.get("date") == wholeDay:
                    # print(clockInfo)

                    if clockInfo.get('clockOut') != None:
                        status = "Day Completed"
                        # print ("day completed")
                    else:
                        status = "Clock Out"
                        # for the sake of Day completed
                        # print ("clock out")

            content = {
                "name" : user.name,
                "status" : status,
            }
            return render(request, "EpunchCard/dailyReport.html", content)

    return render(request, "EpunchCard/dailyReport.html")


# DailyUpdate
def reportUpateViewer(request):
    # dailyUpdate
    now = datetime.now()
    wholeDay = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
    
    everyEmployee = PunchCard.objects.all()
    everyStaff = StaffMember.objects.all()
    person = []
    everyName = []
    everyStaffMember = []
    # check for session
    try:
        user = StaffMember.objects.get(id = request.session['client']['id'])
    except:
        return redirect("/")

    for workingClass in everyStaff:
        # print(personName.name)
        everyName.append(workingClass.name)
        everyStaffMember.append(workingClass)


    for worker in everyEmployee:
        # print(worker.employee.name, "This is from report")
        for clock in worker.clock:
            if clock.get("date") == wholeDay:
                # print("This employee worked today", worker.employee.name)
                
                if "report" in clock:
                    # print("Yes here.sdfa")
                    person.append({
                        "name" : worker.employee.name,
                        "report" : json.dumps(clock["report"])
                    })

                else:
                    # print("No report here")
                    person.append({
                        "name" : worker.employee.name,
                        "report" : "No Report today"
                    })       
        else:
            print("Someone didnt, work today")
            # Only checking if any reports have been written.
        content = {
                    "currentUser" : user.name,
                    "emNames" : person,
                    "day" : wholeDay,
                    "email" : user.email,
                    "everyName" : everyName,
                    "villagerPoints" : user.total,
                    "allVillagerPoints" : villageTotalPoint(everyStaffMember)
                }
        # print(everyName)
    return render(request, "EpunchCard/dailyUpdate.html", content)

def clockWork(request):
    # Making Sure there is a zero in minutes incase there is 10
    now = datetime.now()

    if now.hour >= 12:
        newHr = now.hour - 12
        # newcase 12 -12 = 0
        if newHr == 0:
            newHr = 12
        p = "pm"
    else:
        p = "am"
        newHr = now.hour

    myMinute = ""

    if now.minute < 10:
        myMinute = "0" + str(now.minute)
    
    else: 
        myMinute = str(now.minute)

    standardTime = str(newHr) + ":" + myMinute + p
    wholeDay = str(now.month) + "/" + str(now.day) + "/" + str(now.year)

    user = StaffMember.objects.get(id = request.session['client']['id'])
    userPunchCard = PunchCard.objects.get(employee = StaffMember.objects.get(name = user.name))

    status = ""
    if not userPunchCard.clock:
        # This is for new users with no data
        print ("making a new clock in for completely new user")
        userPunchCard.clock = [
            {
                "date" : wholeDay,
                "clockIn" : standardTime,
                "clockOut" : None,
                "timeSpent" : None,
                "points" : 3.0, 
                "desc" : None
            }
            
        ]
        userPunchCard.save()
        status = "Clock out"


    else:
        # check for current date
        # else is used for when there is an object in userPunchCard.clock which happens to be an array with dicts
        # if any(item['date'] == wholeDay for item in userPunchCard.clock):
        # print ("if first else was hit, current user has data from previous days.")
        if not any(dObj['date'] == wholeDay for dObj in userPunchCard.clock):
            print("User doesnt have data for today, creating new date for today ", wholeDay)
            
            newDay = {
                "date" : wholeDay,
                "clockIn" : standardTime,
                "clockOut" : None,
                "timeSpent" : None,
                "points" : 3.0, 
                "desc" : None 
            }
            userPunchCard.clock.append(newDay)
            userPunchCard.save()
            status = "Clock out"
            # print("This is the if for if not any")
        else:
            # print("There is data, creating data for clockOut")
            for clock in userPunchCard.clock:
                if clock.get("date") == wholeDay:
                    if clock.get("clockOut") != None:
                        print("Day already Completed, No more clockins")
                        status = "Day is Completed"

                    else:
                        print("created data, Day is now completed")
                        clock['clockOut'] = standardTime

                    userPunchCard.save()
                else:
                    print("something went wrong")
    # Results for clock
    for myClock in userPunchCard.clock:
        if myClock["date"] == wholeDay:
            print(myClock)
        else:
            print("There was an error")
    return JsonResponse(myClock, safe=False)

# calculate time difference
def SpentTimeCal(num1, num2):
    hrA, minA = map(int, checkAmPm(num1).split(':'))
    hrB, minB = map(int, checkAmPm(num2).split(':'))
    finalResult = ""
    if minA > minB:
        newHrB = hrB - 1
        newMinB = 60 + minB
        resultMin = newMinB - minA
        resultHr = removeNegatives(hrA, newHrB)

    else:
        resultHr = removeNegatives(hrA, hrB)
        resultMin = minB - minA
        finalResult = str(resultHr) + "." + str(resultMin)
        # print(finalResult)
    return finalResult

def addDesc(request):
    myData = ""
    now = datetime.now()
    wholeDay = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
    moddedMinute = ""
    if now.hour >= 12:
        newTimeHr = now.hour - 12
        # newcase 12 - 12 = 0
        if newTimeHr == 0:
            newTimeHr = 12
        p = "pm"
    else:
        p = "am"
        newTimeHr = now.hour
    # need a zero infornt of minutes
    if now.minute < 10:
        moddedMinute = "0" + str(now.minute)
    else:
        moddedMinute = str(now.minute)
    
    standardTime = str(newTimeHr) + ":" + moddedMinute + p
    print("second: ", standardTime)
    
    # print(request.POST.get("myDesc", None))
    descData = request.POST.get("myDesc", None)
    user = StaffMember.objects.get(id = request.session['client']['id'])    

    EmpTimeCard = PunchCard.objects.get(employee = StaffMember.objects.get(name = user.name))
    for myCurrentClock in EmpTimeCard.clock:
        # print(wholeDay)
        # print(standardTime)
        # print("Check this out, ", user.total)
        if myCurrentClock["date"] == wholeDay:
            if myCurrentClock["clockOut"] == None:
                myCurrentClock["clockOut"] = standardTime
                myCurrentClock["desc"] = descData
                myCurrentClock["timeSpent"] = SpentTimeCal(myCurrentClock["clockIn"], standardTime)
                user.total = float(myCurrentClock["points"]) + float(user.total)
                EmpTimeCard.save()
                user.save()
                print("successfully saved description", SpentTimeCal(myCurrentClock["clockIn"], standardTime))
                myData = myCurrentClock
            else:     
                print("No more clock ins, day is completed")
        else:
            print("Error No date for today, for addDesc")
        

    return JsonResponse(myData, safe=False)
# just a function to check if pm, used by func SpentTimeCal
def checkAmPm(item):
    if "pm" in item:
        changedItem = item.replace("pm", "")
        # print(changedItem)
        hours, minutes = map(int, changedItem.split(':'))
        hr = str(12 + hours)
        modedTime = hr + ":" + str(minutes)
    else:
        modedTime = item.replace("am", "")
    return modedTime

def removeNegatives(num1, num2):
    if num1 > num2:
        result = num1 - num2
    else:
        result = num2 - num1
    return result

# previous_week_range func is used to get the previous week starting from Sunday.
def previous_week_range(day):
    start_date = day - timedelta(days=day.weekday()) + timedelta(days=-1, weeks=-1)
    return start_date

def countDays(aMonth):
    currentDate = datetime.now()
    monthrange(int(currentDate.strftime("%y")), aMonth)
    return monthrange(int(currentDate.strftime("%y")), aMonth)[1]
# When adding, eventually will get more then 12(month), this is to loop back to 1
def checkMonth(aMonth):
    if aMonth == 12:
        aMonth = 1
    else:
        return aMonth
# date in your db
def searcher(request):
    currentDate = datetime.now()
    currentWeekDayNum = currentDate.strftime("%w")
    dayOfMonth = currentDate.strftime("%d")
    monthNumber = currentDate.strftime("%m")
    year = str(20) + currentDate.strftime("%y")
    current = date(int(year), int(monthNumber), int(dayOfMonth))

    frontEndCalenderSearch = request.POST.getlist("getData[]", None)
    when = frontEndCalenderSearch[0]
    who = frontEndCalenderSearch[1]
    # print(frontEndCalenderSearch[1], "Whats going on")
    # print(request.POST.getlist("getData[]", None), "the request data")

    user = StaffMember.objects.get(id = request.session['client']['id'])
    userClock = PunchCard.objects.get(employee = StaffMember.objects.get(name = who))
    # print(dayOfMonth, "day of month")

    if when == "thisWeek":
        # print(frontEndCalenderSearch[1], "Whats going on")
        # print(grabCurrentWeek(who), "here")
        return JsonResponse(grabCurrentWeek(who), safe=False)
    
    elif when == "All":
        revClocker = userClock.clock.copy()
        revClocker.reverse()
        return JsonResponse(revClocker, safe=False)

    elif when == "lastWeek":
        previous_week_range(current)
        # print(previous_week_range(current))
        start_day = previous_week_range(current)
        # print("My start, " + str(start_day.month) + str(countDays(start_day.month)))
        lastWeek = []
        for i in range(7):
            for clock in userClock.clock:
                # This is to check if the counting goes over to next month
                # print("There are clocks last week", str(int(start_day.day + i)))
                # Only checks from starting point, not if counting goes over to next month
                if any(clock["date"] == (str(start_day.month) + "/" + str(int(start_day.day) + i) + "/" + str(start_day.year)) for clock in userClock.clock):
                    if clock["date"] == (str(start_day.month) + "/" + str(int(start_day.day) + i) + "/" + str(start_day.year)):
                        lastWeek.append(clock)
                    else:
                        print("There was an issue")

                elif (int(start_day.day) + i) > countDays(start_day.month):
                    print("This is from the if, incase days go over" , start_day.day)
                    newDay = removeNegatives((start_day.day + i), countDays(start_day.month))
                    nextMonth = checkMonth(start_day.month) + 1
                    newDate = (str(nextMonth)) + "/" + str(newDay) + "/" + str(start_day.year)
                    # print("Just checking " + newDate)
                    if clock["date"] == newDate:
                        lastWeek.append(clock)

                else:
                    print("no clocks last week")
            # print(lastWeek, "Last week.")
        return JsonResponse(lastWeek, safe=False)

    else:
        # Previous Month
        # stackOverflow

        last_month = currentDate.month-1 if currentDate.month > 1 else 12
        # print("last month, " + str(last_month))
        # previousMonthFinal = date(int(year),int(last_month),int(dayOfMonth))
        clockMonth = []
        for clock in userClock.clock:
            if last_month >= 10:
                if clock["date"][:2] == str(last_month):
                    clockMonth.append(clock)
                    print("Date is two characters long")
            else:
                if clock["date"][:1] == str(last_month):
                    clockMonth.append(clock)
                    print("Date is one character long")
        # print(clockMonth, "here is your retrived data")

        return JsonResponse(clockMonth, safe=False)

    return JsonResponse(when, safe=False)

def daysAfter(day):
    if int(day) == 0:
        numOfDaysAfter = 6
    else:
        numOfDaysAfter = 6 - int(day)
    
    return numOfDaysAfter

def passChecker(prePassword, NewPass, confirmPass):
    missing = []
    if len(prePassword) < 1:
        missing.append("Previous Password input needed")
    if len(NewPass) < 1:
        missing.append("New password input needed")
    if len(confirmPass) < 1:
        missing.append("Confirm New password input is needed")
    if confirmPass != NewPass:
        missing.append("Confirm New Password not the same as New Password")
    return missing

def changePass(request):
    prePass = request.POST["prevPass"]
    newPass = request.POST["newPass"]
    confirmNewPass = request.POST["confirmNewPass"]
    user = StaffMember.objects.get(id = request.session['client']['id'])
    # Currently creating settings checker
    if len(passChecker(prePass, newPass, confirmNewPass)):
        # print("Checker went off")
        for issues in passChecker(prePass, newPass, confirmNewPass):
            messages.error(request, issues)

    else:
        if not check_password(prePass, user.password):
            print("Passwords don't match")
            messages.error(request, "Original Password is incorrect")
        else:
            hash1 = make_password(confirmNewPass, salt = None, hasher = "default")
            user.password = hash1
            user.save()
            messages.success(request, "Password Successfuly Changed!")
    return redirect("/settings")

def reportChecker(recip, today, challenge, advice):
    missing = []
    if len(recip) < 1:
        missing.append("Atleast One recipent is needed")
    if len(today) < 1:
        missing.append("What did you do today?")
    if len(challenge) < 1:
        missing.append("What Challenges did you face?")
    if len(advice) < 1:
        missing.append("What can be done to help?")
    return missing

# DailyReport
def subReport(request):
    now = datetime.now()
    currentDay = str(now.month) + "/" + str(now.day) + "/" + str(now.year)

    recipent = request.POST["recipents"]
    Tasktoday = request.POST["today"]
    challenge = request.POST["challenges"]
    advice = request.POST["help"]
    user = StaffMember.objects.get(id = request.session['client']['id'])
    userPunchCard = PunchCard.objects.get(employee = StaffMember.objects.get(name = user.name))
    # Currently creating settings checker
    if len(reportChecker(recipent, Tasktoday, challenge, advice)):
        # print("Checker went off")
        for issues in reportChecker(recipent,Tasktoday,challenge,advice):
            messages.error(request, issues)

    else:
        for clock in userPunchCard.clock:
            # any is used to only get feed back once if date found or not.
            if any(clock['date'] == currentDay for clock in userPunchCard.clock):
                if clock["date"] == currentDay:
                    # print("found day")
                    clock["report"] = {
                            "recipent": recipent,
                            "Tasktoday" : Tasktoday,
                            "challenge" : challenge,
                            "advice" : advice
                        }
                    
                    userPunchCard.save()
                    messages.success(request, "Successfuly submitted")
                    # print("good, here you go, ", clock["report"])
                    break  
        else:
            # print("Unable to Currently Day, must clock in first")
            messages.error(request, "Unable to find Current Day, clock in first")
                
    return redirect("/dailyReport")

def reportCurrentWeek(user):
    now = datetime.now()
    currentWeekDayNum = now.strftime("%w")
    dayOfMonth = now.strftime("%d")
    dayNum = int(currentWeekDayNum)
    firstDayOfWeek = dayNum - int(dayOfMonth)
    start_day = pretty(str(firstDayOfWeek))
    clockWeek = []
    if user == "allStaff":
        for i in range(7):
            everyone = PunchCard.objects.all()
            for staff in everyone:
                for clock in staff.clock:
                    if clock["date"] == (now.strftime("%m") + "/" + str(int(start_day) + i) + "/" + now.strftime("%Y")):
                        if "report" in clock:
                            print("there is a report")
                            clockWeek.append({"name" : staff.employee.name, "reports" : clock})
                        else:
                            print("no report")
                    else:
                        print("no dates")

    else:
        for i in range(7):
            userClock = PunchCard.objects.get(employee = StaffMember.objects.get(name = user))

            # print(now.strftime("%m") + "-" + str(int(start_day) + i) + "-" + now.strftime("%Y"))
            # print(date(int(now.strftime("%Y")), int(now.strftime("%m")), int(pretty(str(firstDayOfWeek))) + i ))
            for clock in userClock.clock:
                if clock["date"] == (now.strftime("%m") + "/" + str(int(start_day) + i) + "/" + now.strftime("%Y")):
                    if "report" in clock:
                        print("there is a report")
                        clockWeek.append(clock)
                    else:
                        print("no report")
                else:
                    print("no dates")
    # print(clockWeek)
    # Works
    return clockWeek

def findReportToday(user):
    now = datetime.now()
    wholeDay = str(now.month) + "/" + str(now.day) + "/" + str(now.year)

    clockWeek = []
    if user == "allStaff":
        everyone = PunchCard.objects.all()
        for staff in everyone:
            for clock in staff.clock:
                if clock["date"] == wholeDay:
                    if "report" in clock:
                        clockWeek.append({"name" : staff.employee.name, "reports" : clock})
                    else:
                        clockWeek.append({"name" : staff.employee.name, "reports" : "No Report Today"})
                else:
                    print("no dates")

    else:
        userClock = PunchCard.objects.get(employee = StaffMember.objects.get(name = user))

        # print(date(int(now.strftime("%Y")), int(now.strftime("%m")), int(pretty(str(firstDayOfWeek))) + i ))
        for clock in userClock.clock:
            if clock["date"] == wholeDay:
                clockWeek.append(clock)
            else:
                print("no dates")
        # print(clockWeek)
    # Works
    return clockWeek
    

def searchReports(request):
    currentDate = datetime.now()
    currentWeekDayNum = currentDate.strftime("%w")
    dayOfMonth = currentDate.strftime("%d")
    monthNumber = currentDate.strftime("%m")
    year = str(20) + currentDate.strftime("%y")
    current = date(int(year), int(monthNumber), int(dayOfMonth))

    frontEndCalenderSearch = request.POST.getlist("getData[]", None)
    when = frontEndCalenderSearch[0]
    who = frontEndCalenderSearch[1]
    # print("my name:  ", who)
    # print("when: ", when)
    user = StaffMember.objects.get(id = request.session['client']['id'])
    
    # print(dayOfMonth, "day of month")

    # userClock needs to be inside the scope incase of choosing anything other then whats in the db
    if when == "today":
        # print(frontEndCalenderSearch[1], "Whats going on")
        # print(findReportToday(who), "here")
        return JsonResponse(findReportToday(who), safe=False)

    if when == "thisWeek":

        # print(frontEndCalenderSearch[1], "Whats going on")
        # print(reportCurrentWeek(who), "here")
        return JsonResponse(reportCurrentWeek(who), safe=False)
    
    elif when == "All":
        everyReport = []
        if who == "allStaff":
            everyone = PunchCard.objects.all()
            for staff in everyone:
                for clock in staff.clock:
                    if "report" in clock:
                        print("reports for everyone: ", clock["report"])
                        everyReport.append({"name": staff.employee.name, "reports": clock})
                        
                else:
                    print("no report, ticket # 45")
        else:
            userClock = PunchCard.objects.get(employee = StaffMember.objects.get(name = who))
            revClocker = userClock.clock.copy()
            revClocker.reverse()
            for clock in revClocker:
                if "report" in clock:
                    print("Heres all the reports within clock ", clock["report"])
                    everyReport.append(clock)
            else:
                print("No report, ticket # 30")
        return JsonResponse(everyReport, safe=False)

    elif when == "lastWeek":
        previous_week_range(current)
        # print(previous_week_range(current))
        start_day = previous_week_range(current)
        # print("My start, " + str(start_day.month) + str(countDays(start_day.month)))
        lastWeek = []
        if who == "allStaff":
            everyone = PunchCard.objects.all()
            for i in range(7):
                for staff in everyone:
                    for clock in staff.clock:
                        # This is to check if the counting goes over to next month
                        # print("There are clocks last week", str(int(start_day.day + i)))
                        # Only checks from starting point, not if counting goes over to next month
                        if any(clock["date"] == (str(start_day.month) + "/" + str(int(start_day.day) + i) + "/" + str(start_day.year)) for clock in staff.clock):
                            if clock["date"] == (str(start_day.month) + "/" + str(int(start_day.day) + i) + "/" + str(start_day.year)):
                                if "report" in clock:
                                    print("reports for this week")
                                    # I want the clocks with report
                                    lastWeek.append({"name" : staff.employee.name, "reports" : clock})
                            else:
                                print("No report, ticket # 20")

                        elif (int(start_day.day) + i) > countDays(start_day.month):
                            # print("This is from the if, incase days go over" , start_day.day)
                            newDay = removeNegatives((start_day.day + i), countDays(start_day.month))
                            nextMonth = checkMonth(start_day.month) + 1
                            newDate = (str(nextMonth)) + "/" + str(newDay) + "/" + str(start_day.year)
                            # print("Just checking " + newDate)
                            if clock["date"] == newDate:
                                if "report" in clock:
                                    lastWeek.append({"name" : staff.employee.name, "reports" : clock})
                            else:
                                print("No report, ticket # 27")

                        else:
                            print("no clocks last week")
                # print(lastWeek, "Last week.")
            return JsonResponse(lastWeek, safe=False)
        else:
            # if not all staff
            userClock = PunchCard.objects.get(employee = StaffMember.objects.get(name = who))
            for i in range(7):
                for clock in userClock.clock:
                    # This is to check if the counting goes over to next month
                    # print("There are clocks last week", str(int(start_day.day + i)))
                    # Only checks from starting point, not if counting goes over to next month
                    if any(clock["date"] == (str(start_day.month) + "/" + str(int(start_day.day) + i) + "/" + str(start_day.year)) for clock in userClock.clock):
                        if clock["date"] == (str(start_day.month) + "/" + str(int(start_day.day) + i) + "/" + str(start_day.year)):
                            if "report" in clock:
                                print("reports for this week")
                                # I want the clocks with report
                                lastWeek.append(clock)
                        else:
                            print("No report, ticket # 23")

                    elif (int(start_day.day) + i) > countDays(start_day.month):
                        print("This is from the if, incase days go over" , start_day.day)
                        newDay = removeNegatives((start_day.day + i), countDays(start_day.month))
                        nextMonth = checkMonth(start_day.month) + 1
                        newDate = (str(nextMonth)) + "/" + str(newDay) + "/" + str(start_day.year)
                        # print("Just checking " + newDate)
                        if clock["date"] == newDate:
                            if "report" in clock:
                                lastWeek.append(clock)
                        else:
                            print("no report, ticket # 23")

                    else:
                        print("no clocks last week")
                # print(lastWeek, "Last week.")
            return JsonResponse(lastWeek, safe=False)

    else:
        # Previous Month
        # stackOverflow

        last_month = currentDate.month-1 if currentDate.month > 1 else 12
        print("last month, " + str(last_month))
        # previousMonthFinal = date(int(year),int(last_month),int(dayOfMonth))
        clockMonth = []
        if who == "allStaff":
            everyone = PunchCard.objects.all()
            for stuff in everyone:
                for clock in stuff.clock:
                    if last_month >= 10:
                        print(clock["date"][:2], " chickehnsdfa")
                        if clock["date"][:2] == str(last_month):
                            if "report" in clock:
                                clockMonth.append({"name": stuff.employee.name, "reports" : clock})
                            # Date is two characters long
                        else:
                            print("there was an error finding a report at all Staff ticket# 1")
                    else:
                        if clock["date"][:1] == str(last_month):
                            print(clock["date"][:1], " should work, this is the month")
                            if "report" in clock:
                                clockMonth.append({"name": stuff.employee.name, "reports": clock})
                                print("Report is in clock")
                        else:
                            print("there was an error finding a report at all staff ticket # 2")

        else:
            userClock = PunchCard.objects.get(employee = StaffMember.objects.get(name = who))
            for clock in userClock.clock:
                if last_month >= 10:
                    if clock["date"][:2] == str(last_month):
                        if "report" in clock:
                            clockMonth.append(clock)
                            print("Date is two characters long")
                    else:
                        print("there was an error finding a report at single ticket # 1")

                else:
                    if clock["date"][:1] == str(last_month):
                        if "report" in clock:
                            clockMonth.append(clock)
                            print("Date is one character long")
                    else:
                        print("there was an error find a report at single ticket # 2")
                        
        
        # print(clockMonth, "here is your retrived data")
        return JsonResponse(clockMonth, safe=False)

    return JsonResponse(when, safe=False)

def currentDataFinder(request):
    staffData = request.POST.getlist("getData[]", None)
    who = staffData[0]
    when = staffData[1]
    
    userClock = PunchCard.objects.get(employee = StaffMember.objects.get(name = who))
    employeeClock = []
    noReport = "No Report Today"
    problem = "No clock in recorded today"
    for clock in userClock.clock:
        if clock["date"] == when:
            # print(clock["date"])
            if "report" in clock:
                employeeClock.append(clock)
            else:
                employeeClock.append(noReport)
                    
    else:
        employeeClock.append(problem)

    content = {
        "who" : who,
        "staffData" : employeeClock
    }
        
    
    return JsonResponse(content, safe=False)

def account_val_byAdmin(postData):
        
        errors = []
        if len(postData['name']) <1:
            errors.append('Name must be not empty!')
        if len(postData['name']) > 1:
            if (postData['name'].replace(" ","").isalpha()) != True:
                errors.append("No numbers in your name please!")

        if len(postData['title']) < 1:
            errors.append( "Title is needed.")

        if len(postData['password']) < 8:
            errors.append( "Pass word must be at least 8 characters.")
        # print("email ", postData['email'], "email with diff : ", postData["email"])
        
        if postData['password'] != postData['confirm_password']:
            errors.append("Pass words do NOT match!")


        identical = StaffMember.objects.filter(email = postData['email'])
        if identical:
            errors.append("Sorry this email name is already taken! Try a different one.")

        if len(postData['email']) > 1:
            if not EMAIL_REGEX.match(postData['email']):
                errors.append("Invalid Email Address!")

        return errors

def createNewStaffAcc(request):
    errors = ""
    staffData = request.POST.getlist("getData[]", None)
    readyStaffInputs = {"email": staffData[0], "name" : staffData[1], "password" : staffData[2], "title": staffData[3], "confirm_password" : staffData[4]}
    # print("From createNewStaffAcc, ", readyStaffInputs)
    user_id = request.session['client']['id']
    errors = account_val_byAdmin(readyStaffInputs)
    forFrontEnd = []
    if len(errors):
        for words in errors:
            forFrontEnd.append(words)
    else:
        success = ""
        success = "Successfully Registered New Staff Account"
        
        hash1 = make_password(readyStaffInputs['password'], salt = None, hasher = 'default')
        # print (hash1)
        user = StaffMember.objects.create(
            admin_id = user_id,
            name = readyStaffInputs['name'],
            title = readyStaffInputs['title'], 
            password = hash1, 
            email = readyStaffInputs['email']
            )
        # Assign the created user to the PunchCard
        PunchCard.objects.create(employee = user)
        forFrontEnd.append(success)
        # print("successfuly completed for new Account, email: ",type(readyStaffInputs["email"]), "", readyStaffInputs["email"], " name : " , readyStaffInputs["name"] )
    return JsonResponse(forFrontEnd, safe=False)

def editEmployee(request):
    staffData = request.POST.getlist("getData[]", None)
    editInput = {"title": staffData[0], "name" : staffData[1], "email" : staffData[2], "passWord": staffData[3], "confirm_password" : staffData[4]}
    print("editEmployee section: id ", editInput)
    employee = StaffMember.objects.get(id = staffData[5])
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    feedBack = []
    for word in editInput:
        if len(editInput[word]) == 0:
            # print(editInput[word], "the key", word)
            if word == "title":
                if len(editInput[word]) > 3:

                    if len(editInput[word]) > 12:
                        feedBack.append("Title must be less than 12 characters long")
                    else:
                        employee.title = editInput[word]

                else:
                    feedBack.append("Title must be more than 3 charaters long.")


            if word == "email":
                if not EMAIL_REGEX.match(editInput[word]):
                    feedBack.append("Email must be Valid")
                else:
                    employee.email = editInput[word]

            if word == "name":
                if len(editInput[word]) > 3:
                    if len(editInput[word]) > 15:
                        feedBack.append("Name must be more less then 15 characters long.")
                    else:
                        employee.name = editInput[word]

                else:
                    feedBack.append("Name must be more than 3 to charaters long.")

            if word == "passWord":
                if len(editInput[word]) > 5:
                    if editInput[word] == editInput["confirm_password"]:
                        hash1 = make_password(editInput["confirm_password"], salt = None, hasher = "default")
                        print("passwords match")
                    else:
                        feedBack.append("passwords dont match")
                else:
                    feedBack.append("Password must be more then 4 charaters long.")
    # print("here is the array for feedBack, ", feedBack)
    # Possible to keep adding Validations
    if len(feedBack) == 0:
        feedBack.append("Successfully Changed")
        employee.save()
    return JsonResponse(feedBack,safe=False)

def managerModeExtraPoints(request):
    messanger = []
    staffData = request.POST.getlist("getData[]", None)
    employee = StaffMember.objects.get(id = staffData[0])
    if len(staffData[2]) > 5:
        employee.total = employee.total + int(staffData[1])
        employee.save()
    else: 
        messanger.append("Input for Reason must be more then 5 Charaters long.")

    if len(messanger) == 0:
        messanger.append("New Total points for " + str(employee.name) + " -- (" + str(employee.total) + ")")
    managerResponse = [ messanger, employee.total]
    return JsonResponse(managerResponse, safe=False)

def checkClockSchedule(request):
    now = datetime.now()
    today = now.day
    previous_day = now.day - 1
    yesterDay = str(now.month) + "/" + str(previous_day) + "/" + str(now.year)
    exampleToday = str(now.month) + "/" + str(now.day) + "/" + str(now.year)

    conclusion = ""
    try:
        userClock = PunchCard.objects.get(employee = StaffMember.objects.get(id = request.session['client']['id']))
    except:
        return redirect("/")
    if not userClock.clock:
        # New user
        conclusion = ["No records of any clock in YesterDay or ever", None]
    else:
        for clock in userClock.clock:
            if clock["date"] == yesterDay:
                print("ISSUE here: " , clock["date"], " " , yesterDay)
                if clock["clockOut"] == None:
                    # print("Clock out is needed for YesterDay")
                    conclusion = [clock["clockIn"], True]
                else:
                    conclusion = ["You have clocked out YesterDay.", False]
                break
            else:
                # print("There is no record of a clock in Yesterday")
                conclusion = ["No Record of a clock in for " + yesterDay + " (YesterDay).", False]
            
    # Only check if False is returned, if not then cause the previous day for to open.
    # Then use the data to count an hour till you get to 8 hours
    return JsonResponse(conclusion, safe=False)

def yesterDayPunchOut(request):
    staffData = request.POST.getlist("getData[]", None)
    user = StaffMember.objects.get(id = request.session['client']['id'])
    userPunchCard = PunchCard.objects.get(employee = StaffMember.objects.get(id = request.session['client']['id']))
    now = datetime.now()
    today = now.day
    previous_day = now.day - 1
    yesterDay = str(now.month) + "/" + str(previous_day) + "/" + str(now.year)
    exampleToday = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
    responseBack = ""

    for clock in userPunchCard.clock:
        if clock["date"] == yesterDay:
            clock["clockOut"] = staffData[0]
            clock["desc"] = staffData[1]
            clock["timeSpent"] = SpentTimeCal(clock["clockIn"], staffData[0])
            user.total = float(user.total) +  3.0
            # print("My clock, ",SpentTimeCal(clock["clockIn"], staffData[0]))
            userPunchCard.save()
            responseBack = "Clock out recorded For YesterDay! Thanks"
        else:
            responseBack = "No clock In is recorded YesterDay"
        
    return JsonResponse(responseBack, safe=False)
