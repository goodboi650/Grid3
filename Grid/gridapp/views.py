from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from gridapp.models import Response
from datetime import datetime

import json
import subprocess
import sys


def user(request):
    return render(request, 'gridapp/user.html')


def login(request):
    return render(request, 'gridapp/login.html')


def gridadmin(request):
    return render(request, 'gridapp/gridadmin.html')


def ipscreen(request):
    return render(request, 'gridapp/ipscreen.html')


def run_item(password, username, server, port):
    command = f'sshpass -p {password} ssh {username}@{server} -p {port} python < script.py'
    process = subprocess.Popen(
        f'{command}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    (out, err) = process.communicate()
    if process.returncode == 0:
        sout = out.decode("utf-8")
        d = json.loads(sout)
        d["Asset_Name"] = server
        d["Status"] = "UP"
        print(json.dumps(d))
        return d
    else:
        errd = {'Asset_Name': server, 'IP': '',
                'MAC': '', 'Hostname': '', 'OS': ''}
        serr = err.decode("utf-8")
        index = serr.rfind(":")
        errd['Status'] = serr[index+2:-2]
        print(json.dumps(errd))
        return errd

    print('\n')


@method_decorator(csrf_exempt, name='dispatch')
class SubmitOneRequest(View):
    def post(self, request):
        data = json.loads(request.body)
        server = data['server']
        #username = data['username']
        #password = data['password']
        #port = data['port']
        try:
            obj = Response.objects.get(AssetName=server)
            dict = run_item(obj.Password, obj.Username, obj.Server, obj.Port)
            # TODO: check if error
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
        return HttpResponse("Success")


@method_decorator(csrf_exempt, name='dispatch')
class SubmitAllRequest(View):
    def post(self, request):
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
            obj = Response.objects.get(Username=username, Password=password)
            dict = run_item(password, username, server, port)
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
                obj.LastUpdated = datetime.now()
                obj.save(update_fields=['IP', 'MAC', 'OS',
                         'Hostname', 'Status', 'LastUpdated'])
            else:
                obj.Status = dict['Status']
                obj.LastUpdated = datetime.now()
                obj.save(update_fields=['Status', 'LastUpdated'])
            count = count+1
        return HttpResponse("Success")


@method_decorator(csrf_exempt, name='dispatch')
class CreateResponse(View):
    def post(self, request):
        data = json.loads(request.body)
        server = data['server']
        username = data['username']
        password = data['password']
        port = data['port']
        try:
            Response.objects.create(
                AssetName=server, Server=server, Username=username, Password=password, Port=port)
            return HttpResponse({"Yelluru Pilega"})
        except:
            return HttpResponse({"Muku Pilega"})


@method_decorator(csrf_exempt, name='dispatch')
class DeleteResponse(View):
    def post(self, request):
        data = json.loads(request.body)
        server = data['asset_name']
        Response.objects.filter(AssetName=server).delete()


@method_decorator(csrf_exempt, name='dispatch')
class SearchResponse(View):
    def get(self, request):
        data = json.loads(request.body)
        if 'asset_name' in data:
            items = Response.objects.filter(AssetName=data['asset_name']).get()
            dict = {}
            for x in items:
                properties = {'OS': x.OS, 'Hostname': x.Hostname, 'MAC': x.MAC,
                              'IP': x.IP, 'Status': x.Status, 'Last Updated': x.LastUpdated}
                dict[x.AssetName] = properties
            jsr = json.loads(dict)
            return JsonResponse(jsr)
        elif 'OS' in data:
            items = Response.objects.filter(OS=data['OS']).get()
            dict = {}
            for x in items:
                properties = {'OS': x.OS, 'Hostname': x.Hostname, 'MAC': x.MAC,
                              'IP': x.IP, 'Status': x.Status, 'Last Updated': x.LastUpdated}
                dict[x.AssetName] = properties
            jsr = json.loads(dict)
            return JsonResponse(jsr)
