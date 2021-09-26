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
    """
    Runs the script ip.py and takes the output from that as
    input and creates a dictionary of required data
    """
    command = f'sshpass -p {password} ssh -o StrictHostKeyChecking=no {username}@{server} -p {port}  python3 < ip.py'
    command2 = f'sshpass -p {password} ssh -o StrictHostKeyChecking=no {username}@{server} -p {port} python < ip.py'

    
    process = subprocess.Popen(f'{command}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate()
    data = {}
    if process.returncode == 0:
        sout = out.decode("utf-8")
        data = json.loads(sout)

    if len(d)==0 :
        process = subprocess.Popen(f'{command2}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = process.communicate()
        data = {}
        if process.returncode == 0:
            sout = out.decode("utf-8")
            data = json.loads(sout)

    return data


@method_decorator(csrf_exempt, name='dispatch')
class Scan(View):
    #Runs a scan on demand
    def get(self, request):
        """
            Scans the remote network and finds all the hosts present on the network
        """
        creds = Creds.objects.all()
        page = 'gridapp/user.html'
        if(request.user.is_authenticated):
            page = 'gridapp/gridadmin.html'
        if(len(creds) == 0):
            return render(request, page, context={'emptyCred': True, 'scanCall': True})
        creds = creds[0]
        username = creds.Username
        password = creds.Password
        server = creds.Server
        port = creds.Port
        data = run_item(password, username, server, port)

        if(len(data) == 0):
            return render(request, page, context={'emptyCred': False, 'scanCall': True, 'emptyDB': True})
        seen = []
        for key in data:
            value = data[key]
            seen.append(key)
            now = datetime.now()
            try:
                temporaryResponse = Response.objects.get(IP=key)
                temporaryResponse.Hostname = value["Hostname"]
                temporaryResponse.MAC = value["MAC"]
                temporaryResponse.OS = value["OS"]
                temporaryResponse.Status = value["Status"]
                temporaryResponse.LastSeenAlive = now
                temporaryResponse.LastUpdated = now
                temporaryResponse.Workgroup = value["Workgroup"]
                temporaryResponse.ADDomain = value["ADDomain"]
                temporaryResponse.save(update_fields=[
                    "Hostname", "OS", "MAC", "Status", "LastSeenAlive", "LastUpdated", "Workgroup", "ADDomain"])
            except:
                Response.objects.create(IP=value["IP"], Hostname=value["Hostname"], MAC=value["MAC"],
                                        Status=value["Status"], OS=value["OS"], LastSeenAlive=now, LastUpdated=now, ADDomain=value["ADDomain"], Workgroup=value["Workgroup"])

        all_items = Response.objects.all()
        for x in all_items:
            if x.IP not in seen:
                x.Status = "down"
                x.LastUpdated = now
                x.save(update_fields=["Status", "LastUpdated"])
        return render(request, page, context={'emptyCred': False, 'scanCall': True, 'emptyDB': False})


@method_decorator(csrf_exempt, name='dispatch')
class AddServer(View):
    #Adds an entry into the credentials table
    def post(self, request):
        """
            Allows Admin user to add/update credentials of a remote network into the credentials database
        """
        page = 'gridapp/user.html'
        if(request.user.is_authenticated):
            page = 'gridapp/gridadmin.html'
        server = request.POST.get("server")
        port = request.POST.get("port")
        if port == '':
            port = 22
        try:
            port = int(port)
        except:
            return render(request, 'gridapp/add_asset.html', context={'portNAN': True})
        username = request.POST.get("username")
        password = request.POST.get("password")
        Creds.objects.all().delete()
        Response.objects.all().delete()
        Creds.objects.create(Server=server, Port=port,
                             Username=username, Password=password)
        return render(request, page, context={'updateCall': True})


@method_decorator(csrf_exempt, name='dispatch')
class SearchDB(View):
    def get(self, request):
        """
            Displays data after the previous scan.
            Displays entire database.
        """
        #Displays the entire database
        item = Response.objects.all()
        data = {}
        i = 1
        for x in item:
            properties = [x.IP, x.Hostname, x.MAC, x.OS, x.Status, x.Workgroup, x.ADDomain, str(
                x.LastSeenAlive), str(x.LastUpdated)]
            data[i] = properties
            i += 1
        return render(request, 'gridapp/ipscreen.html', {'existsDB': bool(len(data)), 'data': data})

    def post(self, request):
        """
            Displays a part of the database corresponding to the user query
        """
        # Search database based on user input parameter
        try:
            parameter = request.POST.get('parameter')
            value = request.POST.get('filter')
            page = 'gridapp/user.html'
            if(request.user.is_authenticated):
                page = 'gridapp/gridadmin.html'
            #Find the parameter based on which the search is required to be performed
            if(parameter == 'os'):
                items = Response.objects.filter(OS__iexact=value)
            elif parameter == 'workgroup':
                items = Response.objects.filter(Workgroup__iexact=value)
            else:
                items = Response.objects.filter(ADDomain__iexact=value)
            data = {}
            index = 1
            #Iterate over the database to find the entries corresponding to the search.
            for item in items:
                properties = [item.IP, item.Hostname, item.MAC, item.OS, item.Status, item.Workgroup, item.ADDomain, str(
                    item.LastSeenAlive), str(item.LastUpdated)]
                data[index] = properties
                index += 1
            return render(request, page, {'searchResults': bool(len(dict)), 'data': data, 'searchCall': True})
        except Exception as e:
            return HttpResponse("Some error occured.")
