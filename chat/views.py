from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatSession, Message

def get_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key

def get_or_create_chat_session(request):
    session_key = get_session_key(request)
    user = request.user if request.user.is_authenticated else None
    
    if user:
        chat_session, _ = ChatSession.objects.get_or_create(user=user)
    else:
        chat_session, _ = ChatSession.objects.get_or_create(session_key=session_key)
    return chat_session

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        content = request.POST.get('message')
        if not content:
            return JsonResponse({'status': 'error', 'msg': 'Empty message'})
        
        chat_session = get_or_create_chat_session(request)
        is_admin = request.user.is_staff
        sender = request.user if request.user.is_authenticated else None
        
        msg = Message.objects.create(
            session=chat_session, 
            sender=sender, 
            content=content, 
            is_admin=is_admin
        )
        return JsonResponse({'status': 'ok', 'message_id': msg.id})
    return JsonResponse({'status': 'error'})

def get_messages(request):
    chat_session = get_or_create_chat_session(request)
    # Check if a last_msg_id was provided to fetch only new messages (polling optimization)
    last_id = request.GET.get('last_id', 0)
    messages = Message.objects.filter(session=chat_session, id__gt=last_id).order_by('timestamp')
    
    data = []
    for msg in messages:
        data.append({
            'id': msg.id,
            'content': msg.content,
            'is_admin': msg.is_admin,
            'time': msg.timestamp.strftime('%H:%M'),
        })
    return JsonResponse({'messages': data})
