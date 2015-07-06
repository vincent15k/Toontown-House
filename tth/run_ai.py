import subprocess, time, os, sys

def getRunningProcesses(pattern):
    p = subprocess.Popen("ps -A | grep %s" % pattern, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    plist = p.communicate()[0].split('\n')
    res = []
    for x in plist:
        if x:
            pid, _, _, name = x.split()
            res.append((int(pid), name))
        
    return res
            
def killProcess(pid, name="???"):
    subprocess.call("kill %d" % pid, shell=True)
    print 'Killed', name, pid

def killShards():
    shards = getRunningProcesses("shard")
    for pid, name in shards:
        killProcess(pid, name)
        
def newLog(pattern):
    name = "databases/air_logs/%s_%s.log" % (pattern, time.time())
    return name, open(name, "wb")
        
shards = (("Sunny Summit", 401000000), ("Pielantis", 402000000), ("Toony Way", 403000000), ("Nutty Nation", 404000000), ("Wacky Waters", 405000000))
        
cmd = sys.argv[1]
if cmd == 'ks':
    print 'Killing shards'
    killShards()
    
elif cmd == 'ku':
    print 'Killing UD'
    prs = getRunningProcesses("ud")
    for pid, proc in prs:
        if proc == "ud":
            killProcess(pid, proc)
            
elif cmd == 'killall':
    print 'Killing all!'
    prs = getRunningProcesses("ka")
    for pid, proc in prs:
        if proc.startswith("ka"):
            killProcess(pid, proc)
            
    killShards()
    prs = getRunningProcesses("ud")
    for pid, proc in prs:
        if proc == "ud":
            killProcess(pid, proc)
            
elif cmd == 'ls':
    print 'Shard list'
    prs = getRunningProcesses("shard")
    for pid, name in prs:
        print name, pid
        
elif cmd == 'lu':
    print 'Is UD running?', "ud" in [x[1] for x in getRunningProcesses("ud")]
        
elif cmd == 'r':
    arg = sys.argv[2]
    if arg == 'u':
        print 'Running UD'
        while True:
            log, f = newLog("uberdog")
            print log
            subprocess.Popen("./ud -m toontown.uberdog.ServiceStart --config server.prc", stdout=f, stderr=f, shell=True).wait()
            
    elif arg == 's':
        index = int(sys.argv[3])
        name, channel = shards[index - 1]
        pattern = "shard%d" % index
        
        print 'Running shard'
        while True:
            log, f = newLog(pattern)
            print log
            subprocess.Popen('./%s -m toontown.ai.ServiceStart --config server.prc --base-channel %s --district-name "%s"' % (pattern, channel, name),
                             stdout=f, stderr=f, shell=True).wait()
                             
            
else:
    print 'Unknown command!'
    