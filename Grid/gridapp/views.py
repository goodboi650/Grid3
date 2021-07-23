from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.core.files import File
from gridapp.models import Response, Creds
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
    return render(request, 'gridapp/add_asset.html')


def delete_asset(request):
    return render(request, 'gridapp/delete_asset.html')


def run_item(password, username, server, port):
    command = f'sshpass -p {password} ssh {username}@{server} -p {port} python3 < ip.py'
    process = subprocess.Popen(
        f'{command}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate()
    d = {}
    if process.returncode == 0:
        sout = out.decode("utf-8")
        d = json.loads(sout)
    return d
    #d = {"IP":["IP","Hostname","Mac","OS","Status"]}


@method_decorator(csrf_exempt, name='dispatch')
class Scan(View):
    def get(self, request):
        creds = Creds.objects.all()
        page = 'gridapp/user.html'
        if(request.user.is_authenticated):
            page = 'gridapp/gridadmin.html'
        if(len(creds) == 0):
            return render(request, page, context={'error': True, 'data': {}})
        creds = creds[0]
        username = creds.Username
        password = creds.Password
        server = creds.Server
        port = creds.Port
        d = run_item(password, username, server, port)
        for key, value in d:
            obj = Response.object.query(IP=key).get()
            now = datetime.now()
            if not obj:
                Response.object.create(Hostname=value["Hostname"], MAC=value["MAC"],
                                       Status=value["Status"], OS=value["OS"], LastSeenAlive=now, LastUpdated=now)
            else:
                obj.Hostname = value["Hostname"]
                obj.MAC = value["MAC"]
                obj.OS = value["OS"]
                obj.Status = value["Status"]
                obj.LastSeenAlive = now
                obj.LastUpdated = now
                obj.save(update_fields=[
                    "Hostname", "OS", "MAC", "Status", "LastSeenAlive", "LastUpdated"])
        all_items = Response.object.all()
        for x in all_items:
            if x.IP not in d:
                obj.Status = "Down"
                obj.LastUpdated = now
                obj.save(update_fields=["Status", "LastUpdated"])
        return render(request, page, context={'error': False, 'data': d})


@method_decorator(csrf_exempt, name='dispatch')
class AddServer(View):
    def post(self, request):
        server = request.POST.get("server")
        port = request.POST.get("port")
        username = request.POST.get("username")
        password = request.POST.get("password")
        Creds.objects.all().delete()
        Response.objects.all().delete()
        Creds.objects.create(Server=server, Port=port,
                             Username=username, Password=password)


@method_decorator(csrf_exempt, name='dispatch')
class SearchDB(View):
    def get(self, request):
        item = Response.objects.all()
        dict = {}
        for x in item:
            if x.AssetName == "":
                continue
            properties = [x.OS, x.Hostname, x.MACx.IP, x.Status,
                          str(x.LastSeenAlive), str(x.LastUpdated)]
            dict[x.AssetName] = properties
        return render(request, 'ipscreen.html', {'data': dict})

    def post(self, request):
        try:
            data = json.loads(request.body)
            if 'asset_name' in data:
                items = Response.objects.filter(AssetName=data['asset_name'])
            elif 'OS' in data:
                items = Response.objects.filter(OS=data['OS'])
            dict = {}
            for x in items:
                # properties = {'OS': x.OS, 'Hostname': x.Hostname, 'MAC': x.MAC,
                # 'IP': x.IP, 'Status': x.Status,'LastSeenAlive': str(x.LastSeenAlive), 'Last Updated': str(x.LastUpdated)}
                properties = [x.OS, x.Hostname, x.MACx.IP, x.Status, str(
                    x.LastSeenAlive), str(x.LastUpdated)]
                dict[x.AssetName] = properties
            #jsr = json.loads(dict)
            return render(request, 'user.html', {'flag': True, 'data': dict, 'error': False})
            # elif AD domain
        except:
            item = Response.objects.all()
            dict = {}
            for x in item:
                if x.AssetName == "":
                    continue
                properties = [x.OS, x.Hostname, x.MACx.IP, x.Status, str(
                    x.LastSeenAlive), str(x.LastUpdated)]
                dict[x.AssetName] = properties
            # print(type(dict))
            #jsr = json.loads(dict)
            # print(type(dict))
            return render(request, 'user.html', {'flag': True, 'error': True})
