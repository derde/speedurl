#! /usr/bin/python

"This works okay, provided the URL downloads for more than 1 second"

''' apt -y install python-requests '''

import sys
import time
try:
    from urllib.request import Request,urlopen
except ImportError:
    from urllib2 import Request,urlopen
import signal

total_bytes=0
signalled=False
original_sigint_handler = signal.getsignal(signal.SIGINT)

def sigint(a,b):
    global signalled
    signalled=True
    signal.signal(signal.SIGINT,original_sigint_handler)

def timechunks(response, timediff=1.0):
    global signalled
    downloaded=0
    chunk=131072
    squeaked=False
    time0=time.time()
    while not signalled:
        datalen = len(response.read(chunk)) # 1Mbps chunks

        downloaded+=datalen
        time1=time.time()
        if (time1-time0) > timediff:
            squeaked=True
            yield (downloaded,time1-time0)
            downloaded=0
            time0=time1
        if datalen < chunk:
            break
    dtime=time1-time0
    if ((downloaded > 0) and dtime > (timediff/2)) or (dtime>0.0 and not squeaked):
        yield (downloaded,dtime)
    
def speedtest(url, max_time=10, min_time=2, verbose=1, drops=1, headers={}, divisor=1.0, format='%7.3f', unit="mbps"):
    global total_bytes 
    try:
        lrate = None
        maxrate = 0
        bps = None
        # response = requests.get(url, stream=True)
        if url and url.find(':')<0: url='http://'+url;
        request = Request(url, headers=headers)
        response = urlopen(request,timeout=2)
        alltime=0
        rates=[]
        dropcount=0
        for downloaded,dtime in timechunks(response):
            total_bytes+=downloaded
            bps = (downloaded*8*1500/dtime/1460)
            rates.append(bps)
            if verbose:
                # sys.stderr.write( ('%0.3fs\t%dkB\t%0.3f '+unit+' %s\n') % ( dtime, downloaded/1024, bps/divisor, url ))
                sys.stderr.write( (format+unit+'\t%dkB\t%0.3fs\t%s\n') % ( bps/divisor, downloaded/1024, dtime, url ))
                sys.stderr.flush()
            maxrate=max(bps,maxrate)
            alltime+=dtime
            if (bps<maxrate and alltime>min_time) or alltime>max_time:
                # sys.stderr.write('\n')
                sys.stderr.flush()
                response.close()
                i=rates.index(maxrate)
                smooth=[]
                if i>0: smooth.append(rates[i-1])
                if i+1<len(rates): smooth.append(rates[i+1])
                if len(smooth):
                    return (max(smooth) + maxrate)/2.0
                return maxrate
            lrate=bps
        if bps:
            # sys.stderr.write('\n')   # if \r ...
            sys.stderr.flush()
        response.close()
        return bps
    except IOError as e:
        sys.stderr.write("%s: %s\n" % (url,str(e)))

from math import sqrt 
def mean(data):
    if len(data):
        return float(sum(data) / len(data))

def variance(data):
    if len(data):
        mu = mean(data)
        return mean([(x - mu) ** 2 for x in data])

def stddev(data):
    if len(data):
        return sqrt(variance(data))

def hostname():
    import socket
    return ''.join( socket.gethostname().split('.')[0:1] )

if __name__=="__main__":
    import optparse
    parser=optparse.OptionParser()
    parser.add_option("-H","--header",  dest="headers" , action="append", default=[], help="HTTP headers")
    parser.add_option("-q","--quiet",  dest="quiet" , action="store_true", default=False, help="Don't show progress during tests")
    parser.add_option("-b","--bps",   dest="bps" , action="store_true", default=False, help="use bps as unit")
    parser.add_option("-n","--repeat",  dest="repeat" , action="store", type='int', default=0, help="repeat this many times per url")
    #parser.add_option("-s","--stats",  dest="stats" , action="store_true", default=True, help="Show stats")
    (options,args) = parser.parse_args()
    headers={}
    time0=time.time()
    for line in options.headers: 
        bits=line.split(':',1)
        if not bits[0] in headers:
            headers[bits[0]]=bits[1].lstrip(' ')
        else:
            if type(headers[bits[0]]) is str: 
                headers[bits[0]] = [ headers[bits[0]], ]
            headers[bits[0]].append( bits[1].lstrip(' ') )
    if options.bps:
        divisor=1.0
        format='%0.0f'
        unit='bps'
    else:
        divisor=1000000.0
        format='%0.3f'
        unit='Mbps'
    signal.signal(signal.SIGINT,sigint)
    all_results=[]
    for index in range(0,len(args)):
        all_results.append([])
    for repeat in range(0,max(options.repeat,1)):
        for index in range(0,len(args)):
            url=args[index]
            results=all_results[index]
            bps = speedtest(url,headers=headers,verbose=not options.quiet,divisor=divisor, unit=unit, format=format)
            if bps!=None:
                comment=''
                if signalled:
                    comment='\t(interrupted)'
                if not signalled or len(results)==0:
                    results.append(bps/divisor)
                sys.stdout.write ( (format+comment) % (bps/divisor) )
            else:
                sys.stdout.write ( '*' )
            eol='\n'
            if options.quiet and index<len(args)-1:
                eol='\t'
            sys.stdout.write(eol)
            if not options.quiet: # write terse output
                sys.stdout.write('\n')
            
            sys.stdout.flush()
            if signalled:
                break
        if signalled:
            break

    aggregate_result=[]
    results=[]
    for index in range(0,len(args)+1):
        aggregate_result.extend(results) # add results from last loop to aggregate
        if index==len(args):
            url='aggregate'
            results=aggregate_result
            if len(args)==1:
                continue
        else:
            url=args[index]
            results=all_results[index]
        if len(results) and options.repeat:
            # leading tab means you can cut -f 1 on the results
            stats = ( min(results),mean(results),max(results),stddev(results) )
            if index>0:
                sys.stdout.write( '\n')
            if index!=len(args):
                sys.stdout.write( '\t--- '+ (' %d test%s to ' % (len(results), {True:'',False:'s'}[ (len(results)==1) ]) ) + url+' on ' + hostname()+' ---\n' )
            else:
                sys.stdout.write( '\t--- aggregate ---\n' )
            if index==len(args) or len(args)==1:
                sys.stdout.write('\t%d bytes over %0.3fs at %s\n' %  ( total_bytes, time.time()-time0, time.strftime('%Y-%m-%d %H:%M:%S %Z')) )
            sys.stdout.write( ('\t'+unit+' min/avg/max/stddev = '+format+'/'+format+'/'+format+'/'+format+'\n') % stats )
            sys.stdout.flush()
