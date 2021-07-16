from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

import json


class SubmitRequest(View):
    def post(self, request):
        data = json.loads(request.body)
        #code to get required params
        #do work
        return