import struct
import subprocess
import sys
import os
import glob
from multiprocessing import Process
from multiprocessing import Pool
import datetime
import argparse
assert sys.version_info[:2] == (2,7)




def HW(n): 
    '''
    count of high bits 
    '''
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32)
    
    return n



def Jaccard_index (arg):
    ''' 
    Jaccard index between binary measurements
    '''
    # 512 KiB = 512*1024 bytes = 524288 bytes = 4194304 bits = 1048576 hex numbers = 131072 * 8 hex numbers
    PUFsize=1048576/16 #
    pattern=0xffffffffffffffff #PUF initial value
    (File0_name, File1_name)=arg
    # Open input file for reading
    F_t1 = open(File0_name, "rb")
    F_t2 = open(File1_name, "rb")
    
    union=0
    intersec=0
    hw1=0
    hw2=0
    
    
    b_t1 = F_t1.read()
    b_t2 = F_t2.read()

    #print len(b_t1), len(b_t2)
    
    for i in range(0, PUFsize):
        b_tmp_t1 = b_t1[i*8:(i+1)*8] # read 8 bytes = 16 hex numbers
        b_tmp_t2 = b_t2[i*8:(i+1)*8] # read 8 bytes = 16 hex numbers
        #t1_data = int(F_t1.read(16), 16)
        #t2_data = int(F_t2.read(16), 16)
        #if (t1_data != t2_data):
        #  print format(t1_data, '#016x'), format(t2_data, '#016x')

        t1_data = struct.unpack("Q",b_tmp_t1)[0]
        t2_data = struct.unpack("Q",b_tmp_t2)[0]
    
        #print t1_data
        #hamming weight
        cmpdata = t1_data ^ pattern
        hw1+=HW(cmpdata)
        cmpdata = t2_data ^ pattern
        hw2+=HW(cmpdata)
        #intersec
        cmpdata = ((t1_data^pattern) & (t2_data^pattern)) 
        intersec+=HW(cmpdata)                
        #union
        cmpdata = ((t1_data^pattern) | (t2_data^pattern)) 
        union+=HW(cmpdata)
    
    try:
        #print  ( File0_name, File1_name, hw1, hw2, intersec, union, float(intersec)/float(union))
        F_t1.close()
        F_t2.close()
        return ( File0_name, File1_name, hw1, hw2, intersec, union, float(intersec)/float(union))
    except:
        #print ("Error!  "+File0_name+"  " + File1_name +" %d  %d  %d  %d \n"%(hw1, hw2, intersec, union))
        F_t1.close()
        F_t2.close()
        return ( File0_name, File1_name, hw1, hw2, intersec, union, 999)

def errorRate (args):
    SIZE=1048576/16 #
    pattern=0xffffffffffffffff #PUF initial value
    No_threads=64 #Number of threads to be run in parallel
    datafile = args
    #fileName_only = drams[0].split('/')[-3][:]
    #f_out = open ("ErrorRate_"+fileName_only+".txt", "w")
    #print ("Waiting time (s)\t errors\n")
    #for k in range (4):
    #    dram = drams[k]
    F_data = open(datafile, "rb")
    #print "DDR "+str(k)+ "\n"
    #f_out.write("DDR "+str(k)+ "\n")

    data = F_data.read()
    hw2 = 0
    for i in range (SIZE):
        t2_data = data[i*8:(i+1)*8]
        t2_data = struct.unpack("Q",t2_data)[0]
        if t2_data != pattern:
           #print "%x\n" % t2_data
            cmpdata = t2_data ^ pattern
            tmpmask=1
            for j in range(0,64):
                if tmpmask & cmpdata:
                    hw2 +=1            
                    #if Toprint:
                    #print i, i*32+j, j,(i*32+j) % 128,(i*32+j) % 16384
                tmpmask = tmpmask << 1
    F_data.close()
    #print datafile, hw2
    return (datafile, hw2)
    #print str(i * 60)+"\t\t\t" , hw2
    #f_out.write(str(i * 60)+"\t\t\t" + str(hw2)+"\n")
    #f_out.close()


def readDRAMData (root, slot = 0):#slot = -1 means all slots
    #root = args.dir
    DRAM_A = []
    DRAM_B = []
    DRAM_C = []
    DRAM_D = []
    startTime = []
    endTime = []
    #differentDevices = os.listdir(root)
    if (slot != -1):
        differentDevices = glob.glob((root+"*slot%d*"%slot))
    elif (slot == -1):
        differentDevices = glob.glob((root+"i-*"))
    #print differentDevices
    differentDevices.sort(key = lambda x: x.split('_')[-6] +'-'+ x.split('_')[-5])
    
    for i in range(len(differentDevices)):
        #print differentDevices[i].split('_')[-6] +'-'+ differentDevices[i].split('_')[-5]
        time = differentDevices[i].split('_')[-6] +'-'+ differentDevices[i].split('_')[-5]
        time = datetime.datetime.strptime(time, '%Y-%m-%d-%H-%M')
        startTime.append(time)
        #device_Time = os.listdir(root+str(differentDevices[i]))
        device_Time = os.listdir(str(differentDevices[i]))
        for tmp in device_Time:
            if (tmp[0:2] == "12"):
                tmp2 = tmp
        #device_120s = root+str(differentDevices[i]) + '/' + tmp2
        device_120s = str(differentDevices[i]) + '/' + tmp2
        drams = os.listdir(device_120s)
        for tmp in drams:
            if(tmp[0] == 'A'):
                dram = device_120s + '/' + tmp
                DRAM_A.append(dram)
            elif (tmp[0] == 'B'):
                dram = device_120s + '/' + tmp
                DRAM_B.append(dram)
            elif (tmp[0] == 'C'):
                dram = device_120s + '/' + tmp
                DRAM_C.append(dram)
            elif (tmp[0] == 'D'):
                if (tmp != "D.dat"):
                    time = tmp[:-4].split('_')[1] +'-'+ tmp[:-4].split('_')[2]
                    time = datetime.datetime.strptime(time, '%Y-%m-%d-%H-%M')
                endTime.append(time)
                dram = device_120s + '/' + tmp
                DRAM_D.append(dram)
    return (differentDevices, DRAM_A, DRAM_B, DRAM_C, DRAM_D, startTime, endTime)


def readDRAMData_old (root, slot = 0):#slot = -1 means all slots
    #root = args.dir
    DRAM_A = []
    DRAM_B = []
    DRAM_C = []
    DRAM_D = []
    startTime = []
    endTime = []
    #differentDevices = os.listdir(root)
    if (slot != -1):
        differentDevices = glob.glob((root+"*slot%d*"%slot))
    elif (slot == -1):
        differentDevices = glob.glob((root+"i-*"))
    #print differentDevices
    differentDevices.sort(key = lambda x: x.split('_')[-3] +'-'+ x.split('_')[-2])
    
    for i in range(len(differentDevices)):
        #print differentDevices[i].split('_')[-6] +'-'+ differentDevices[i].split('_')[-5]
        time = differentDevices[i].split('_')[-3] +'-'+ differentDevices[i].split('_')[-2]
        time = datetime.datetime.strptime(time, '%Y-%m-%d-%H-%M')
        startTime.append(time)
        #device_Time = os.listdir(root+str(differentDevices[i]))
        device_Time = os.listdir(str(differentDevices[i]))
        for tmp in device_Time:
            if (tmp[0:2] == "12"):
                tmp2 = tmp
        #device_120s = root+str(differentDevices[i]) + '/' + tmp2
        device_120s = str(differentDevices[i]) + '/' + tmp2
        drams = os.listdir(device_120s)
        for tmp in drams:
            if(tmp[0] == 'A'):
                dram = device_120s + '/' + tmp
                DRAM_A.append(dram)
            elif (tmp[0] == 'B'):
                dram = device_120s + '/' + tmp
                DRAM_B.append(dram)
            elif (tmp[0] == 'C'):
                dram = device_120s + '/' + tmp
                DRAM_C.append(dram)
            elif (tmp[0] == 'D'):
                if (tmp != "D.dat"):
                    time = tmp[:-4].split('_')[1] +'-'+ tmp[:-4].split('_')[2]
                    time = datetime.datetime.strptime(time, '%Y-%m-%d-%H-%M')
                endTime.append(time)
                dram = device_120s + '/' + tmp
                DRAM_D.append(dram)
    return (differentDevices, DRAM_A, DRAM_B, DRAM_C, DRAM_D, startTime, endTime)

def groupJaccardIndex (dramData, interval, startTime, endTime):
    arg=[]
    for i in range (len(dramData)-interval):
        j = i + interval
        file_0 = dramData[i] # directory to data files
        file_1 = dramData[j] # directory to data files
        arg.append((file_0,file_1))
    No_threads=64 #Number of threads to be run in parallel
    p = Pool(No_threads)
    out = p.map(Jaccard_index,arg)
    Count0 = 0
    Count1 = 0
    for x in out:
        #print x[6]
        if((x[2] < 100) or (x[3] < 100) ):
            Count0 = Count0 + 1
            #print ("Something wrong! Bit flips so few...\n")
        else :
            Count1 = Count1 + 1
    print ("Summary: There are %d normal comparisons, and %d abnormal results, of which the number of bitfilps is too small."%(Count1, Count0))

    jaccardIndice = []
    for i in range (len(dramData)-interval):
        j = i + interval
        jaccardIndice.append((out[i][6], (startTime[j] - endTime[i]) )) # jaccard index, time interval
    #for i in range (len(out)):
    #    jaccardIndice.append((out[i][6], (startTime[i+1] - endTime[i]) )) # jaccard index, time interval
    jaccardIndice.sort(key = lambda x: x[1])
    p.close()
    return jaccardIndice
    #for line in jaccardIndice:
    #    print ("%s, %d minutes"%(line[0], line[1].seconds/60.0))

def probabilityCalculation(jaccardIndice):
    dataAnalyzed = []
    count = 0
    num_same = 0
    #print jaccardIndice
    for i in range (len(jaccardIndice)):
        line = jaccardIndice[i]
        #print num_same, count#debug
        if(i == 0):# First
            count = 1
            if (line[0] > 0.5):
                num_same = 1
            waitingTime_ave = line[1].seconds
        elif (i == len(jaccardIndice) - 1 ): # last
            count = count + 1
            waitingTime_ave = waitingTime_ave+line[1].seconds
            if (line[0] > 0.5):
                num_same = num_same + 1
            probabil = float(num_same) / float(count)
            waitingTime_ave = (waitingTime_ave) / float(count)# in seconds
            dataAnalyzed.append((waitingTime_ave, probabil, count))
        else:#else
            count = count + 1
            waitingTime_ave = waitingTime_ave + line[1].seconds
            if (line[0] > 0.5):
                num_same = num_same + 1
    return dataAnalyzed


def calculation (root, slot, dramNum):
    (differentDevices, DRAM_A, DRAM_B, DRAM_C, DRAM_D, startTime, endTime) = readDRAMData(root=root, slot=slot)
    print ("Number of PUFs = %d"%(len(DRAM_D)))
    if (dramNum == 0):
        dramName = 'DRAM-A' # dram name to be printed
        DRAMData = DRAM_A# DRAM PUF data
    elif (dramNum == 1):
        dramName = 'DRAM-B' # dram name to be printed
        DRAMData = DRAM_B# DRAM PUF data
    elif (dramNum == 3):
        dramName = 'DRAM-D' # dram name to be printed
        DRAMData = DRAM_D# DRAM PUF data
    else:
        print ("Error! DRAM C cannot be used!")
    print ("DRAM: %s"%dramName)
    probs = []
    for i in range (len(DRAMData)-10):# maximum interval = length - 5, which means the minimum interval is 5
        interval = i + 1
        print ("Interval = %d"%interval)
        jaccardIndice = groupJaccardIndex(dramData=DRAMData, interval=interval, startTime=startTime, endTime=endTime)
        print ("Number of Comparisons = %d"%(len(jaccardIndice)))
        dataAnalyzed = probabilityCalculation(jaccardIndice)
        probs.append(dataAnalyzed)


    output_filename = "output_probability_%s_%s_slot%d.txt"%(dramName, root.split('/')[-2], slot)
    outFile = open(output_filename, "w")
    outFile.write ("Waiting Time (minutes) \t Probability to get the same board \t Number of experiments\n")

    print ('waitingTime' + '\t ' + 'prob' + '\t ' + 'num' )
    for line in probs:
        #print probs
        #print type(line), line
        #print type(line[0]), line[0]
        #print type(line[0][0]), line[0][0]
        waitingTime = "%2.2f"%(line[0][0] / 60.0)
        prob = "%2.2f"%(line[0][1])
        num = "%d"%(line[0][2])
        outFile.write(waitingTime + '\t\t\t\t ' + prob + '\t\t\t\t ' + num + '\n')
        print (waitingTime + '\t ' + prob + '\t ' + num )
    outFile.close()

def extractAllJaccardIndexWithinOneExperiment (root, slot =0, dramNum=4):
    print ("Data directory = %s , slot = %d , dramNum = %d" % (root, slot, dramNum))
    DRAM = readDRAMData(root=root, slot=slot)[dramNum]#-1 means all slots
    
    count = 0
    allOut = []
    for i in range (len(DRAM)-1):
        arg=[]
        for j in range (len(DRAM)-i-1):
            count = count + 1
            file_0 = DRAM[i] # directory to data files
            file_1 = DRAM[j+i+1] # directory to data files
            arg.append((file_0,file_1))
        No_threads=64 #Number of threads to be run in parallel
        p = Pool(No_threads)
        out = p.map(Jaccard_index,arg)
        p.close()
        allOut = allOut + out
        for k in range (len(out)):
            if ((out[k][6] > 1)):#if there is error
                print ("There is error! %d th FPGA, slot %d \n%s"%(int(k/8),int(k%8), str(out[k])))
    dataFileName = '-'.join(root.split('/')[1:])+'slot%d-DRAM%d.dat'%(slot, dramNum)
    with open(dataFileName, 'w') as file:
        file.write(str(allOut))
    print ("In total, compared %d pairs in %d instances."%(count, len(DRAM)))

def extractAllJaccardIndexWithinOneExperiment_old (root, slot =0, dramNum=4):
    print ("Data directory = %s , slot = %d , dramNum = %d" % (root, slot, dramNum))
    DRAM = readDRAMData_old(root=root, slot=slot)[dramNum]#-1 means all slots
    
    count = 0
    allOut = []
    for i in range (len(DRAM)-1):
        arg=[]
        for j in range (len(DRAM)-i-1):
            count = count + 1
            file_0 = DRAM[i] # directory to data files
            file_1 = DRAM[j+i+1] # directory to data files
            arg.append((file_0,file_1))
        No_threads=64 #Number of threads to be run in parallel
        p = Pool(No_threads)
        out = p.map(Jaccard_index,arg)
        p.close()
        allOut = allOut + out
        for k in range (len(out)):
            if ((out[k][6] > 1)):#if there is error
                print ("There is error! %d th FPGA, slot %d \n%s"%(int(k/8),int(k%8), str(out[k])))
    dataFileName = '-'.join(root.split('/')[1:])+'slot%d-DRAM%d.dat'%(slot, dramNum)
    with open(dataFileName, 'w') as file:
        file.write(str(allOut))
    print ("In total, compared %d pairs in %d instances."%(count, len(DRAM)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Probability to get the same Instance')
    parser.add_argument("-d", "--dir", type=str, required=True, help='Path to data files, including / at the end. e.g. ./binaryRawData/n_virginia_us-east-1/every5minutes_20190824/f1.2xlarge/')
    #parser.add_argument("-i", "--interval", type=int, required=False, default=1, help='Interval between two PUFs, default = 1')
    parser.add_argument("--dram", type=int, required=False, default=3, help='Which DRAM do you want to use? 0 = A, 1 = B, 3 = D')
    parser.add_argument("-s","--slot", type=int, required=False, default=0, help='Which slot? default = 0')
    args = parser.parse_args()

    print ("Root directory: %s" % args.dir)
    print ("Slot %d" % args.slot)

    #calculation(root=args.dir, slot=args.slot, dramNum=args.dram)# single slot
    #for i in range (8):
    #    calculation(root=args.dir, slot=i, dramNum=args.dram)# only on 16xlarge

    #for i in range (8):
    #    extractAllJaccardIndexWithinOneExperiment(root=args.dir, slot = (i))
    
    extractAllJaccardIndexWithinOneExperiment_old(root=args.dir, slot = -1)


