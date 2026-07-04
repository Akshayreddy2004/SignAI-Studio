import os
import sys
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import TranslationHistory

# Base directory of blogs app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def homepage(request):
    return render(request, "index.html", {})

def registration(request):
    if request.method == "POST":
        name = request.POST.get("t1", "").strip()
        mailid = request.POST.get("t2", "").strip()
        mno = request.POST.get("t3", "").strip()
        uid = request.POST.get("t4", "").strip()
        pwd = request.POST.get("t5", "").strip()
        
        if not uid or not pwd:
            return render(request, "registration.html", {"msg": "Username and Password are required!"})
            
        if User.objects.filter(username=uid).exists():
            return render(request, "registration.html", {"msg": "Username already exists! Choose another."})
            
        user = User.objects.create_user(username=uid, email=mailid, password=pwd, first_name=name)
        user.save()
        auth_login(request, user)
        return redirect('userhome')
        
    return render(request, "registration.html", {})

def login_view(request):
    if request.method == "POST":
        uid = request.POST.get("t1", "").strip()
        pwd = request.POST.get("t2", "").strip()
        
        user = authenticate(request, username=uid, password=pwd)
        if user is not None:
            auth_login(request, user)
            return redirect('userhome')
        else:
            return render(request, "login.html", {"msg": "Invalid username or password!"})
            
    return render(request, "login.html", {})

def logout_view(request):
    auth_logout(request)
    return redirect('homepage')

def userhome(request):
    recent_logs = []
    total_audio = 0
    total_sign = 0
    if request.user.is_authenticated:
        user_logs = TranslationHistory.objects.filter(user=request.user)
        total_audio = user_logs.filter(translation_type='AUDIO_TO_SIGN').count()
        total_sign = user_logs.filter(translation_type='SIGN_TO_AUDIO').count()
        recent_logs = user_logs[:10]
    else:
        # Show global demo stats or guest logs
        total_audio = TranslationHistory.objects.filter(translation_type='AUDIO_TO_SIGN').count()
        total_sign = TranslationHistory.objects.filter(translation_type='SIGN_TO_AUDIO').count()
        recent_logs = TranslationHistory.objects.all()[:10]
        
    return render(request, "userhome.html", {
        "recent_logs": recent_logs,
        "total_audio": total_audio,
        "total_sign": total_sign,
        "total_all": total_audio + total_sign
    })

def studio(request):
    """Render the Web-Native Bidirectional AI Studio."""
    return render(request, "studio.html", {})

def dictionary(request):
    """Render the Interactive ISL Dictionary Explorer."""
    gif_dir = os.path.join(BASE_DIR, 'ISL_Gifs')
    letters_dir = os.path.join(BASE_DIR, 'letters')
    
    gifs = []
    if os.path.exists(gif_dir):
        gifs = sorted([f.replace('.gif', '') for f in os.listdir(gif_dir) if f.endswith('.gif')])
    
    letters = []
    if os.path.exists(letters_dir):
        letters = sorted([f.replace('.jpg', '') for f in os.listdir(letters_dir) if f.endswith('.jpg')])
        
    return render(request, "dictionary.html", {"gifs": gifs, "letters": letters})

@csrf_exempt
def log_translation(request):
    """JSON endpoint called by browser studio to log conversions."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            t_type = data.get("translation_type", "AUDIO_TO_SIGN")
            input_txt = data.get("input_text", "")
            output_res = data.get("output_result", "")
            
            user = request.user if request.user.is_authenticated else None
            TranslationHistory.objects.create(
                user=user,
                translation_type=t_type,
                input_text=input_txt,
                output_result=output_res
            )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "invalid method"}, status=405)

def about(request):
    return render(request, "about.html", {})

def contact(request):
    return render(request, "contact.html", {})

# Legacy Desktop execution views (backward compatibility with absolute paths)
def audio_sign(request):
    script_path = os.path.join(BASE_DIR, "main2.py")
    os.system(f'"{sys.executable}" "{script_path}"')
    return HttpResponse("Audio to Sign Executed")

def sign_audio(request):
    project_root = os.path.dirname(BASE_DIR)
    script_path = os.path.join(project_root, "detect_gesture.py")
    os.system(f'"{sys.executable}" "{script_path}"')
    return HttpResponse("Sign to Audio Executed")