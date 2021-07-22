from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.core.files import File
from gridapp.models import Response
from datetime import datetime

import json
import subprocess
import sys


def user(request):
    return render(request, 'gridapp/user.html')

def gridadmin(request):
    return render(request, 'gridapp/gridadmin.html')


def ipscreen(request):
    return render(request, 'gridapp/ipscreen.html')

def singlescan(request):
    return render(request, 'gridapp/singlescan.html')

def add_asset(request):
    return render(request,'gridapp/add_asset.html')

def delete_asset(request):
    return render(request, 'gridapp/delete_asset.html')




def run_item(password, username, server, port, no):
    command = f'sshpass -p {password} ssh {username}@{server} -p {port} python3 < script{no}.py'
    process = subprocess.Popen(
        f'{command}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    d = {}
    (out, err) = process.communicate()
    if process.returncode == 0:
        sout = out.decode("utf-8")
        d = json.loads(sout)
        d["Asset_Name"] = server
        d["Status"] = "UP"
        # print(json.dumps(d))
        # return d
    else:
        d = {'Asset_Name': server, 'IP': '',
             'MAC': '', 'Hostname': '', 'OS': ''}
        serr = err.decode("utf-8")
        index = serr.rfind(":")
        d['Status'] = serr[index+2:-2]
        # print(json.dumps(errd))
        # return errd

    if d['Status'] != 'UP':
        command = f'sshpass -p {password} ssh {username}@{server} -p {port} python3 < script{no}.py'
        process = subprocess.Popen(
            f'{command}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = process.communicate()
        if process.returncode == 0:
            sout = out.decode("utf-8")
            d = json.loads(sout)
            d['Asset_Name'] = server
            d['Status'] = "UP"
            # print(json.dumps(d))
        else:
            d = {'Asset_Name': server, 'IP': '',
                 'MAC': '', 'Hostname': '', 'OS': ''}
            serr = err.decode("utf-8")
            index = serr.rfind(":")
            d['Status'] = serr[index+2:-2]
            # print(json.dumps(d))

    # print(json.dumps(d))
    return d

    print('\n')


@method_decorator(csrf_exempt, name='dispatch')
class SubmitOneRequest(View):
    def post(self, request):
        server = request.POST.get("server")
        
        #username = data['username']
        #password = data['password']
        #port = data['port']
        try:
            obj = Response.objects.get(AssetName=server)
            no = 2
            if obj.DomainInfo is None:
                no = 1
            dict = run_item(obj.Password, obj.Username, obj.Server, obj.Port, no)
            # TODO: check if error
            print(dict)
            if dict['Status'] == 'UP':
                #Assetname = dict['Asset_name'],
                ip = dict['IP']
                mac = dict['MAC']
                os = dict['OS']
                hostname = dict['Hostname']
                #obj.AssetName = Assetname
                obj.IP = ip
                obj.MAC = mac
                obj.OS = os
                obj.Hostname = hostname
                obj.Status = dict['Status']
                dom = dict['Domain Info']
                if obj.Domaininfo is None:
                    with open (f'./media/{server}','w') as f:
                        Dfile = File(f)
                        Dfile.write(dom)
                        obj.DomainInfo = Dfile
                    f.close()
                obj.LastSeenAlive = datetime.now()
                obj.LastUpdated = datetime.now()
                obj.save(update_fields=['IP', 'MAC', 'OS',
                         'Hostname', 'Status', 'LastUpdated'])
            else:
                obj.Status = dict['Status']
                obj.LastUpdated = datetime.now()
                obj.save(update_fields=['Status', 'LastUpdated'])
        except Exception as e:
            print(e)
            return HttpResponse("Yellubhai tu galat search karra")
        
        return JsonResponse(dict)


@method_decorator(csrf_exempt, name='dispatch')
class SubmitAllRequest(View):
    def get(self, request):
        lines = []
        count = 1
        all_items = Response.objects.all()
        for item in all_items:
            print(f"Asset {count}\n")
            if item.Port is None:
                port = 22
            else:
                port = item.Port
            server = item.Server
            username = item.Username
            password = item.Password
            no = 2
            if item.DomainInfo is None:
                no = 1
            #obj = Response.objects.get(AssetName=server,Username=username, Password=password)
            dict = run_item(password, username, server, port, no)
            # TODO: check if error
            print(dict)
            if dict['Status'] == 'UP':
                #Assetname = dict['Asset_name'],
                ip = dict['IP']
                mac = dict['MAC']
                os = dict['OS']
                hostname = dict['Hostname']
                #obj.AssetName = Assetname
                item.IP = ip
                item.MAC = mac
                item.OS = os
                item.Hostname = hostname
                item.Status = dict['Status']
                item.LastSeenAlive = datetime.now()
                item.LastUpdated = datetime.now()
                item.save(update_fields=['IP', 'MAC', 'OS',
                                         'Hostname', 'Status', 'LastUpdated'])
            else:
                item.Status = dict['Status']
                item.LastUpdated = datetime.now()
                item.save(update_fields=['Status', 'LastUpdated'])
            count = count+1
        return HttpResponse("Success")


@method_decorator(csrf_exempt, name='dispatch')
class CreateResponse(View):
    def post(self, request):
        #data = json.loads(request.body)
        #server = data['server']
        #username = data['username']
        #password = data['password']
        #port = data['port']
        server = request.POST.get("server")
        username = request.POST.get("username")
        password = request.POST.get("password")
        port = request.POST.get("port")

        try:
            Response.objects.create(
                AssetName=server, Server=server, Username=username, Password=password, Port=port)
            return HttpResponse({"Yelluru Pilega"})
        except:
            return HttpResponse({"Muku Pilega"})


@method_decorator(csrf_exempt, name='dispatch')
class DeleteResponse(View):
    def post(self, request):
        #data = json.loads(request.body)
        server = request.POST.get("server")
        Response.objects.filter(AssetName=server).delete()
        return HttpResponse("Success")


@method_decorator(csrf_exempt, name='dispatch')
class SearchResponse(View):
    def get(self,request):
        item = Response.objects.all()
        dict = {}
        for x in item:
            if x.AssetName == "":
                continue
            properties = {'OS': x.OS, 'Hostname': x.Hostname, 'MAC': x.MAC,
                            'IP': x.IP, 'Status': x.Status,'LastSeenAlive': str(x.LastSeenAlive), 'Last Updated': str(x.LastUpdated)}
            dict[x.AssetName] = properties
        # print(type(dict))
        #jsr = json.loads(dict)
        # print(type(dict))
        return JsonResponse(dict)

    def post(self, request):
        try:
            #print("Hello bocha")
            data = json.loads(request.body)

            #print("mukund here")
            if 'asset_name' in data:
                items = Response.objects.filter(AssetName=data['asset_name'])
                dict = {}
                for x in items:
                    properties = {'OS': x.OS, 'Hostname': x.Hostname, 'MAC': x.MAC,
                            'IP': x.IP, 'Status': x.Status,'LastSeenAlive': str(x.LastSeenAlive), 'Last Updated': str(x.LastUpdated)}
                    dict[x.AssetName] = properties
                #jsr = json.loads(dict)
                return JsonResponse(dict)
            elif 'OS' in data:
                items = Response.objects.filter(OS=data['OS'])
                dict = {}
                for x in items:
                    properties = {'OS': x.OS, 'Hostname': x.Hostname, 'MAC': x.MAC,
                            'IP': x.IP, 'Status': x.Status,'LastSeenAlive': str(x.LastSeenAlive), 'Last Updated': str(x.LastUpdated)}
                    dict[x.AssetName] = properties
                #jsr = json.loads(dict)
                return JsonResponse(dict)
        except:
            item = Response.objects.all()
            dict = {}
            for x in item:
                if x.AssetName == "":
                    continue
                properties = {'OS': x.OS, 'Hostname': x.Hostname, 'MAC': x.MAC,
                            'IP': x.IP, 'Status': x.Status,'LastSeenAlive': str(x.LastSeenAlive), 'Last Updated': str(x.LastUpdated)}
                dict[x.AssetName] = properties
            # print(type(dict))
            #jsr = json.loads(dict)
            # print(type(dict))
            return JsonResponse(dict)
