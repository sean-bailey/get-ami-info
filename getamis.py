import boto3
import re
ec2=boto3.client('ec2')
regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
myamis={}
def generatereturndict():
    for region in regions:
        windowsdict={}
        linuxdict={}
        sparkbeyonddict={}

        ec2loop=boto3.client('ec2',region_name=region)
        windowsamis=[]
        linuxamis=[]
        sparkbeyondamis=[]
        imagesinregion=ec2loop.describe_images(
            Owners=[
                '482826897061'
            ]
        )
        for thing in imagesinregion['Images']:
            if 'Name' in thing.keys():
                if not re.search("LINUX",thing['Name'].upper()) and re.search("AUTO",thing['Name'].upper()):
                    windowsamis.append({thing['ImageId']:thing['Name']})
                if re.search("LINUX",thing['Name'].upper()) and re.search("AUTO",thing['Name'].upper()):
                    linuxamis.append({thing['ImageId']:thing['Name']})
                if (re.search('SB',thing['Name'].upper()) and re.search('AMI',thing['Name'].upper())) or re.search('BEYOND',thing['Name'].upper()):
                    sparkbeyondamis.append({thing['ImageId']:thing['Name']})
        #now we have the filled ami list. Time to find the images associated with it.
        #the final dictionaries need to be like this: {imageid:[imageidname,totalimages,{instancetype:number},{InstanceName:{InstanceType:number}}]}
        amilists=[windowsamis,linuxamis,sparkbeyondamis]
        for amitype in amilists:
            for amilist in amitype:
                for i in range(len(amilist)):
                    numberofinstances=0
                    instancetypedict={}
                    instancenamedict={}
                    nametotypedict={}
                    bundledlist=[]
                    imageid=list(amilist.keys())[0]
                    ec2instances=ec2.describe_instances(
                        Filters=[
                            {
                                'Name': 'image-id',
                                'Values': [
                                    imageid
                                ]
                            }
                        ]
                    )
                    #first get number of matching images
                    numberofinstances=len(ec2instances['Reservations'])
                    #now for the number of instancetypes
                    for j in range(len(ec2instances['Reservations'])):
                        ec2reservations=ec2instances['Reservations'][j]
                        if ec2reservations['Instances'][0]['InstanceType'] in instancetypedict.keys():
                            instancetypedict[ec2reservations['Instances'][0]['InstanceType']]+=1
                        else:
                            print(ec2reservations['Instances'][0]['InstanceType'])
                            instancetypedict[ec2reservations['Instances'][0]['InstanceType']]=1
                        #since we're iterating through the list anyways...
                        tags=ec2reservations['Instances'][0]['Tags']
                        for k in range(len(tags)):
                            if tags[i]['Key']=='Name':
                                if not tags[i]['Value'] in instancenamedict.keys():
                                    instancenamedict[tags[i]['Value']]={}

                                if ec2reservations['Instances'][0]['InstanceType'] in instancenamedict[tags[i]['Value']]:
                                    instancenamedict[tags[i]['Value']][ec2reservations['Instances'][0]['InstanceType']]+=1
                                else:
                                    instancenamedict[tags[i]['Value']][
                                        ec2reservations['Instances'][0]['InstanceType']] = 1
                    bundledlist.append(amilist[imageid])
                    bundledlist.append(numberofinstances)
                    bundledlist.append(instancetypedict)
                    bundledlist.append(instancenamedict)
                    if amitype==windowsamis:
                        windowsdict[imageid]=bundledlist
                    if amitype==linuxamis:
                        linuxdict[imageid]=bundledlist
                    if amitype==sparkbeyondamis:
                        sparkbeyonddict[imageid]=bundledlist






        myamis[region] = {'Windows': windowsdict, 'Linux': linuxdict, 'SparkBeyond': sparkbeyonddict}
        #myamis['help'] = {'AMI Category (Windows Linux Sparkbeyond)':
        #                      {'imageid':
        #                           ['ID Name',
        #                            'Number of Instances running AMI',
        #                            {'instance type':
        #                                 'number of instances of that instance type'
        #                             },
        #                            {'Name tag on instance':
        #                                 {'Instance Type':'Number of Instance Type'}
        #                             }]
        #                       }
        #                  }
    return myamis


def parsetocsv(amidictionary):
    import csv
    #{region:{'Windows':{imageid: [imageidname, totalimages, {instancetype: number}, {InstanceName: {InstanceType: number}}]},'Linux':{imageid: [imageidname, totalimages, {instancetype: number}, {InstanceName: {InstanceType: number}}]}, 'SparkBeyond':{imageid: [imageidname, totalimages, {instancetype: number}, {InstanceName: {InstanceType: number}}]}}
    with open('outputfile.csv', 'a',newline='') as f:
        w = csv.writer(f)
        starter=['Region','AMI Type','AMI ID','AMI Name', 'Number of times AMI Occurs', '{instance types for AMI:count}','{Name Of instances:{instance Types for that AMI:count}}]']
        w.writerow(starter)
        writeout=[]
        for region in amidictionary.keys():






            testdict=amidictionary[region]
            mylist=list(testdict.items())

            for i in range(3):

                for mykey in mylist[i][1]:
                    writeout = []
                    writeout.append(region)
                    writeout.append(mylist[i][0])
                    writeout.append(mykey)
                    writeout.append(mylist[i][1][mykey][0])
                    writeout.append(mylist[i][1][mykey][1])
                    writeout.append(mylist[i][1][mykey][2])
                    writeout.append(mylist[i][1][mykey][3])
                    w.writerow(writeout)

            #w.write(mykey)
            #w.writerow([testdict])
            #for key, value in testdict.items():
            #    ln = [key]
            #    #w.writerow([key,value])
            #    for ik, iv in value.items():
            #        ln.append([ik,iv])
            #    #    ln.extend([v for v in iv])
            #    w.writerow(ln)
    '''
    with open('mycsvfile.csv','w') as f:
        w= csv.writer(f)
        w.writerows(amidictionary['us-east-1'])
    #with open('mycsvfile.csv','a') as f:
    #    w = csv.writer(f)
    #    w.writerows(amidictionary.items())
    '''

mydict=generatereturndict()
parsetocsv(mydict)


