from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import urllib.request
import urllib.error
from .models import ChatSession, Message

def build_chat_history(chat_session, exclude_message_id=None, limit=20):
    queryset = Message.objects.filter(session=chat_session).order_by('-timestamp')
    if exclude_message_id:
        queryset = queryset.exclude(id=exclude_message_id)
    history_messages = list(reversed(queryset[:limit]))
    history = []
    for msg in history_messages:
        history.append({
            "role": "model" if msg.is_admin else "user",
            "parts": [{"text": msg.content}],
        })
    return history


def call_gemini(api_key, contents):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-1.5-flash:generateContent"
        f"?key={api_key}"
    )
    payload = json.dumps({"contents": contents}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    candidates = data.get("candidates", [])
    if not candidates:
        return ""
    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    if not parts:
        return ""
    return parts[0].get("text", "")

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
        ai_message = None
        ai_message_id = None

        if not is_admin:
            if settings.GOOGLE_API_KEY:
                history = build_chat_history(chat_session, exclude_message_id=msg.id)
                try:
                    contents = history + [{"role": "user", "parts": [{"text": content}]}]
                    ai_text = call_gemini(settings.GOOGLE_API_KEY, contents).strip()
                    if not ai_text:
                        ai_text = 'Xin lỗi, hiện tại tôi chưa thể trả lời.'
                except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
                    ai_text = 'Xin lỗi, hệ thống AI đang bận. Vui lòng thử lại sau.'
            else:
                ai_text = 'Chưa cấu hình GOOGLE_API_KEY nên không thể trả lời tự động.'

            ai_msg = Message.objects.create(
                session=chat_session,
                sender=None,
                content=ai_text,
                is_admin=True
            )
            ai_message = ai_msg.content
            ai_message_id = ai_msg.id

        return JsonResponse({
            'status': 'ok',
            'message_id': msg.id,
            'ai_message': ai_message,
            'ai_message_id': ai_message_id,
        })
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
