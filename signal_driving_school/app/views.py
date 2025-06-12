from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.models import User,auth
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib import messages

# Create your views here.
# register

def register(request):
    if request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password==confirm_password:
            data=User.objects.create_user(username=name,email=email,password=password)
            data.save()
            return redirect(login)
        else:
            return redirect(register)
    return render(request,'register.html',{'error':'Passwords do not match'})
        
def login(request):
    if request.method=='POST':
        name=request.POST['name']
        psw=request.POST['psw']
        user=auth.authenticate(username=name,password=psw)
        if user is not None:
            if user.is_superuser:
                auth.login(request, user)  # Log in the superuser
                # return redirect(adindex)  # Redirect to superuser index page
            else:
                auth.login(request, user)  # Log in the regular user
                return redirect(index)  # Redirect to regular user index page
        else:
            return redirect('login')  # Redirect to login page if authentication fails
    return render(request,'login.html')

def logout(request):
 
        if request.user.is_authenticated:
            auth.logout(request)
            
            return redirect(login)
        else:
            return redirect(login)
        

def index(request):
    # if request.user.is_authenticated:
        
    return render(request,'index.html')

def admission(request):
    return render(request,'admission.html')

# admission verification 

def verify_admission_number(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You need to log in first.")
        return redirect('login')  # redirect to your login page

    profile = request.user.profile

    if profile.is_verified:
        return redirect('documents')  

    if request.method == 'POST':
        entered_number = request.POST.get('admission_number')
        if entered_number == profile.admission_number:
            profile.is_verified = True
            profile.save()
            messages.success(request, "Admission number verified successfully.")
            return redirect('documents')
        else:
            messages.error(request, "Incorrect admission number.")

    return render(request, 'verify_admission.html')


def quiz_view(request):
    questions = Question.objects.prefetch_related('choices').all()
    return render(request, 'quiz.html', {'questions': questions})

def result_view(request):
    if request.method != 'POST':
        return redirect('quiz')  # Redirect to quiz if accessed directly

    questions = Question.objects.prefetch_related('choices').all()
    score = 0
    total = questions.count()
    results = []

    for question in questions:
        selected_id = request.POST.get(f'question_{question.id}')
        correct_choice = question.choices.filter(is_correct=True).first()
        selected_choice = None

        if selected_id:
            try:
                selected_choice = Choice.objects.get(id=selected_id)
                if selected_choice.is_correct:
                    score += 1
            except Choice.DoesNotExist:
                pass

        results.append({
            'question': question,
            'selected': selected_choice,
            'correct': correct_choice,
        })

    return render(request, 'result.html', {
        'score': score,
        'total': total,
        'results': results,
    })

# email 

def send_email_view(request):
        if request.method == 'POST':
            name = request.POST.get('name')
            from_email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            full_message = f"Message from {name} <{from_email}>:\n\n{message}"

            send_mail(
                subject=subject,
                message=full_message,
                from_email='your_email@gmail.com',           # Your sender email (Gmail etc.)
                recipient_list=['your_email@gmail.com'],     # You receive the message
                fail_silently=False,
            )
            return HttpResponse("Thanks! Your message was sent.")

        return render(request, 'contact.html')

