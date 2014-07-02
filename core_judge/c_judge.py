import os, subprocess, datetime, time
import signal
import sys
import filecmp





base_dir = '/home/aswin/Documents/Aptana/judge'
media_dir = base_dir + '/media'

sub_files = media_dir + '/submissions/'
in_files = media_dir + '/infiles/'
out_files = media_dir + '/outfiles/'

sys.path.append(base_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'judge.settings'


from problems.models import Submission

while True:
    sub_list = Submission.objects.filter(status='waiting',language='c')
    if not sub_list:
        time.sleep(1)
        continue

    for a in sub_list: 
	a.status = 'Processing'
	a.save()

	code_file = sub_files+ str(a.sid)+'.c'
	cmd = 'cc ' + code_file
        outf = open('out.txt','w+')
	pr = subprocess.Popen([cmd],stdin=None,stdout=outf,stderr=outf,shell=True)
        while pr.poll() is None:
            continue
        outf.close()
        outf = open('out.txt','r')
        out = outf.read()
        a.errorcode = out
        a.save()
        
        os.remove('out.txt')
        if pr.returncode:
                 a.status = "Compilation Error"
                 a.extime = .2
                 a.save()
                 a.prob.details.total += 1
                 a.prob.details.ce += 1
	         a.prob.details.accuracy = round(float(a.prob.details.acc)/a.prob.details.total,3)
                 a.prob.details.save()
                 x = Submission.objects.filter(user = a.user,status = "Accepted",prob=a.prob)
                 a.user.tot_sub += 1
                 a.user.save()
                 if not x:
                    a.user.ex_time += .2
                    a.user.save()
                 continue
                    
        i = 0
        while i < a.prob.testfiles:
                i += 1
		in_file = in_files + a.prob.pid + str(i) + '.txt'
		inf = open(in_file,'r')
		outf = open('out.txt','w+')
		errf = open('err.txt','w+')
		p = subprocess.Popen(['./a.out'],stdin=inf,stdout=outf,stderr=errf,shell=True)
                time_taken = 0.0
       	        while p.poll() is None:
		    time.sleep(0.01)
		    time_taken += 0.01
		    if time_taken > a.prob.time_limit:
		    	os.kill(p.pid,signal.SIGKILL)
			os.waitpid(-1,os.WNOHANG)
			os.remove('out.txt')
                        os.remove('err.txt')
			a.status = "Time Limit Exceeded"
                        a.extime += .2
			a.save()
			a.prob.details.total += 1
			a.prob.details.tle += 1
			a.prob.details.accuracy = round(float(a.prob.details.acc)/a.prob.details.total,3)
			a.prob.details.save()
			a.user.tot_sub += 1
			a.user.save()
			break

	        if a.status == "Time Limit Exceeded":
	            break
	        if p.returncode:
                    outf.close()
                    outf = open('err.txt','r')
                    a.errorcode = outf.read()
		    a.status = "Run Time Error"
                    a.extime += .2
		    a.save()
		    a.prob.details.total += 1
		    a.prob.details.rte += 1
		    a.prob.details.accuracy = round(float(a.prob.details.acc)/a.prob.details.total,3)
		    a.prob.details.save()
		    a.user.tot_sub += 1
		    a.user.save()
                    os.remove('out.txt')
                    os.remove('err.txt')
                    break
	        out_file = out_files + a.prob.pid + str(i) + '.txt'
                out_file_p = open(out_file,'r')
                out_template = out_file_p.read()
                sub_out = open('out.txt','r').read()
                if out_template == sub_out :

                    os.remove('out.txt')
                    os.remove('err.txt')
                    continue
                else:
                    print outf.read()
                    os.remove('out.txt')
                    os.remove('err.txt')
                    a.status = "Wrong Answer"
                    a.extime += .2
                    a.save()
                    a.prob.details.total += 1
                    a.prob.details.wa += 1
                    a.prob.details.accuracy = round(float(a.prob.details.acc)/a.prob.details.total,3)
                    a.prob.details.save()
                    a.user.tot_sub += 1
                    a.user.save()
                    break
        ac_flag = 0
        if i == a.prob.testfiles:
                a.prob.details.total += 1
                a.prob.details.acc += 1
                a.prob.details.accuracy = round(float(a.prob.details.acc)/a.prob.details.total,3)
                a.prob.details.save()
                x = Submission.objects.filter(user = a.user,status = "Accepted",prob=a.prob).order_by('extime')
                if not x:
                    a.user.points += 1
                    a.user.ex_time = time_taken
                    ac_flag = 1
                else:
                    x = x[0]
                    if x.extime > time_taken:
                        a.user.ex_time -= x.extime
                        a.user.ex_time += time_taken

                a.user.tot_sub += 1
                a.user.succ_sub += 1
                a.user.save()
                a.status = "Accepted"
                a.extime = time_taken
                a.save()
                continue

        else:
                x = Submission.objects.filter(user = a.user,status = "Accepted",prob=a.prob)
                if not x:
                    a.user.ex_time += .2
                    a.user.save()
                continue
       


	
	
		






