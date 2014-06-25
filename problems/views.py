from django.shortcuts import render
from django.http import HttpResponseRedirect
from problems.models import Problem,Submission
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from users.models import OjUser
import datetime



def problems(request):
    p = Problem.objects.filter(is_active=True)
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
        s.save()
        filename = str(s.sid)+'.'+s.language
        s.code.save(filename,ContentFile(request.POST['code']))
        return HttpResponseRedirect('/submissions/'+str(s.sid))
    else:
        return render(request,'submit.html')


    
    

# Create your views here.