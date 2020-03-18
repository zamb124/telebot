from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse
from bot_main import bot_main
from threading import Thread

def bot_start(request):
    t = Thread(target=bot_main)
    t.start()
    body = {'status': 'True'}
    return JsonResponse(body, status=200)