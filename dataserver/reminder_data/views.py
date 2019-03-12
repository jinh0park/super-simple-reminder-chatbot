from django.shortcuts import render
from django.views.generic import View
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import *
# Create your views here.

@csrf_exempt
def user_view(request):
    if request.method == 'GET':
        data = dict(request.GET)
        try:
            chat_id, = data.get('chat_id')
            chat_user = ChatUser.objects.get(chat_id=chat_id)
            todos = Todo.objects.filter(chat_user=chat_user, done=False)
            todos_load = list(map(lambda x:[x.id, x.title], list(todos)))
            return JsonResponse({'status':200, 'item':{'todos':todos_load}})
        except ChatUser.DoesNotExist:
            return JsonResponse({'status': 404, 'message': '아이디 등록을 먼저 진행해주세요.'})


    if request.method == 'POST':
        data = dict(request.POST)
        action, = data['action']

        if action == 'create':
            try:
                chat_id, = data.get('chat_id')
                c = ChatUser.objects.create(chat_id=chat_id)
                return JsonResponse({'status': 200, 'item':{'chat_id':chat_id, 'id':c.id,} ,'message':'아이디가 등록되었습니다.'})
            except:
                return JsonResponse({'status':400, 'message':'이미 등록되어 있는 아이디 입니다.'})

        else:
            return JsonResponse({'status': 404, 'message':'등록되지 않은 명령입니다.'})

@csrf_exempt
def todo_view(request):
    if request.method == 'POST':
        data = dict(request.POST)
        action, = data['action']

        if action == 'create':
            try:
                chat_id, = data.get('chat_id')
                title, = data.get('title')

                chat_user = ChatUser.objects.get(chat_id=chat_id)
                t = Todo.objects.create(title=title, chat_user=chat_user)
                return JsonResponse({'status': 200, 'message': '할일이 등록되었습니다.', 'item':{'title':str(title)}})

            except ChatUser.DoesNotExist:
                return JsonResponse({'status': 404, 'message': '아이디 등록을 먼저 진행해주세요.'})

        if action == 'done':
            try:
                todo_id, = data.get('todo_id')
                t = Todo.objects.get(id=todo_id)
                t.done = True
                t.save()
                return JsonResponse({'status': 200, 'message': '처리되었습니다.'})

            except Todo.DoesNotExist:
                return JsonResponse({'status': 404, 'message': '이미 삭제된 할일입니다.'})

