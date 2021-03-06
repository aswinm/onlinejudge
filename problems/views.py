from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from problems.models import Problem,Submission
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from users.models import OjUser
import datetime
import json



def problems(request):
    p = Problem.objects.filter(is_active=True)
    u = None
    return render(request,'problems.html',{'p':p})

def problem(request,pid):
    p = Problem.objects.filter(pid=pid)
    if not p:
        return HttpResponseRedirect("/problems")
    p = p[0]
    return render(request,'problem.html',{'p':p})

@login_required(login_url='/login')
def submission(request):
    if request.method == "POST":
        p = Problem.objects.filter(pid= request.POST['problemid'])
        if not p:
            return HttpResponseRedirect('/problems')
        p = p[0]
        u = OjUser.objects.get(username=request.user.username)
        s = Submission.objects.create(
                                      prob = p,
                                      user=u,
                                      language=request.POST['language'],
                                      subtime = datetime.datetime.now(),
                                      )

        filename = str(s.sid)+'.'+s.language
        s.code.save(filename,ContentFile(request.POST['code']))
        s.save()
        return HttpResponseRedirect('/submissions/'+str(s.sid))
    else:
        return render(request,'submit.html')

def submit(request,sid):
    s = Submission.objects.filter(sid = sid)
    if not s:
        return HttpResponseRedirect('/problems')
    u = OjUser.objects.get(username = request.user.username)
    s = s[0]
    if s.user != u:
        return HttpResponseRedirect('/problems')
    code = s.code.read()
    return render(request,'submission.html',{'s':s,'code':code})

@login_required(login_url="/login")
def substatus(request,sid):
    s = Submission.objects.filter(sid=sid)
    if not sid:
        return HttpResponseRedirect('/problems')
    s = s[0]
    u = OjUser.objects.get(username=request.user.username)
    if request.user.username != u.username:
        return HttpResponseRedirect('/problems')
    da = {
            'status':s.status,
            'errorcode':s.errorcode,
            }
    da = json.dumps(da)
    return HttpResponse(da)

@login_required(login_url='/login')
def submissions(request):
    u = OjUser.objects.get(username=request.user.username)
    s = Submission.objects.filter(user=u)
    return render(request,'mysubmission.html',{'s':s})


def editproblem(request,pid):
    prob = Problem.objects.filter(pid=pid).first()
    if not prob:
        return HttpResponseRedirect("/problems")
    return HttpResponseRedirect("/problems/"+pid)



    
    

# Create your views here.
