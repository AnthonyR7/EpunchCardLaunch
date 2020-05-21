from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register', views.register),
    url(r'^login$', views.login),
    url(r'^dashboard', views.dashboard),
    url(r'^logOut', views.logOut),
    url(r'^regPg', views.regPg),
    # url(r'^pointsGraph', views.graph),
    url(r'^dailyReport', views.report),
    url(r'^submitReport', views.subReport),
    url(r'^settings', views.settings),
    url(r'^dailyUpdate', views.reportUpateViewer),
    url(r'^timer', views.clockWork),
    url(r'^search', views.searcher),
    url(r'^addDesc', views.addDesc),
    url(r'^passChange', views.changePass),
    url(r'^addPoints', views.points),
    url(r'^reportSearch', views.searchReports),
    url(r'^findCurrentData', views.currentDataFinder),
    url(r'^totalPoint', views.addExtraPointTotal),
    url(r'^add', views.createNewStaffAcc),
    url(r'^edit', views.editEmployee),
    url(r'^pointsManager', views.managerModeExtraPoints),
    url(r'^checkClockOut', views.checkClockSchedule),
    url(r'^latePunchOut', views.yesterDayPunchOut)
]