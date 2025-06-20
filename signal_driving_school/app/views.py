from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.models import User,auth
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import razorpay
from django.conf import settings
from razorpay.errors import BadRequestError
import os
from django.urls import reverse
from django.template.context_processors import csrf
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator 
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.paginator import Paginator
import random
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
                return redirect(adindex)  # Redirect to superuser index page
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

def adindex(request):
    if request.user.is_authenticated:
        students=Admission.objects.all()
        payment=Payment.objects.all()
        combined=zip(payment,students)
    return render(request,'adindex.html',{'combined':combined})

def admission(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect unauthenticated users to login

    if request.method == "POST":
        name = request.POST.get('name')
        dob = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        if Admission.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect(admission)
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        emergency = request.POST.get('emergency_contact')
        aadhar = request.POST.get('aadhar_number')
        identity_proof = request.FILES.get('identity_proof_upload')
        photo = request.FILES.get('photo')
        vehicle_type = request.POST.get('vehicle_type')
        batch = request.POST.get('preferred_batch_time')

        # Calculate amount
        if vehicle_type == 'car':
            amount = 8000
        elif vehicle_type == 'bike':
            amount = 2000
        elif vehicle_type == 'both':
            amount = 10000
        else:
            messages.error(request, "Please select a valid vehicle type.")
            return redirect(admission)

        # Save admission record
        adm = Admission.objects.create(
            name=name,
            date_of_birth=dob,
            gender=gender,
            email=email,
            phone=phone,
            address=address,
            emergency_contact=emergency,
            aadhar_number=aadhar,
            identity_proof_upload=identity_proof,
            photo=photo,
            vehicle_type=vehicle_type,
            preferred_batch_time=batch
        )
        adm.save()

        # Create Razorpay Order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': amount * 100,
            'currency': 'INR',
            'payment_capture': 1
        })

        # Save payment with pending status
        money= Payment.objects.create(
            student=adm,
            user=request.user,
            amount=amount,
            razorpay_order_id=razorpay_order['id'],
            payment_status='pending'
        )
        money.save()
        # Prepare context for Razorpay checkout

        callback_url = request.build_absolute_uri(reverse('payment_success'))

        context = {
            'order_id': razorpay_order['id'],
            'amount': amount * 100,
            'key_id': settings.RAZORPAY_KEY_ID,
            'callback_url': callback_url,
            'admission': adm
        }
        
        context.update(csrf(request))  # 🔥 This adds 'csrf_token' to the context
        return render(request, 'payment.html', context)

    return render(request, 'admission.html')


#------------ payment success ---------------

@csrf_exempt
def payment_success(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
            messages.error(request, "Incomplete payment data received. Please try again.")
            return redirect(admission)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            # ✅ Signature verified
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id, user=request.user)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.payment_status = 'paid'
            payment.save()

            send_mail(
                subject='Payment Successful - Driving School Registration',
                message=f"""
                Dear {payment.student.name},

                Your payment of ₹{payment.amount} for the {payment.student.vehicle_type} course was successful.

                ✅ Admission Number: {payment.student.id}
                🕒 Batch Time: {payment.student.preferred_batch_time}

                Your admission is confirmed. Thank you!

                Regards,  
                Signal Driving School
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[payment.student.email],
                fail_silently=False,
            )

            messages.success(request, "Payment successful! Thank you for your registration.")
            return render(request, 'payment_success.html', {
                'payment': payment,
                'student': payment.student
            })

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect(admission)

        except Payment.DoesNotExist:
            messages.error(request, "Payment record not found.")
            return redirect(admission)

        except Exception as e:
            messages.error(request, f"Unexpected error: {str(e)}")
            return redirect(admission)

    return HttpResponseBadRequest("Invalid request method.")

# ---------update-------------------
def adupdate(request,id):
        data=Admission.objects.get(id=id)
        data1=Payment.objects.get(student=data)

        if not request.user.is_authenticated:
            return redirect('login')  # Redirect unauthenticated users to login

        if request.method == "POST":
            name = request.POST.get('name')
            dob = request.POST.get('date_of_birth')
            gender = request.POST.get('gender')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            emergency = request.POST.get('emergency_contact')
            aadhar = request.POST.get('aadhar_number')
            identity_proof = request.FILES.get('identity_proof_upload')
            photo = request.FILES.get('photo')
            vehicle_type = request.POST.get('vehicle_type')
            batch = request.POST.get('preferred_batch_time')
            # Calculate amount
            if vehicle_type == 'car':
                amount = 8000
            elif vehicle_type == 'bike':
                amount = 2000
            elif vehicle_type == 'both':
                amount = 10000
            else:
                messages.error(request, "Please select a valid vehicle type.")
            
            # data1.amount=amount
            # data1.save()
            # Save admission record
            # adm = Admission.objects.create(
            data.name=name
            data.date_of_birth=dob
            data.gender=gender
            data.email=email
            data.phone=phone
            data.address=address
            data.emergency_contact=emergency
            data.aadhar_number=aadhar
            data.identity_proof_upload=identity_proof
            data.photo=photo
            data.vehicle_type=vehicle_type
            data.preferred_batch_time=batch
            
            data.save()
            return redirect(adindex)
        
        return render(request,'adupdate.html',{'data':data,'data1':data1})
# ---------delete------------
def delete(request,id):
    Admission.objects.get(id=id).delete()
    
    return redirect(adindex)

# ---------------- quiz settings----------------

# -------admin quizpage -----------------

def add_question(request):
    if request.method == 'POST':
        question_text = request.POST.get('question')
        question = Question.objects.create(text=question_text)

        for i in range(1, 5):
            choice_text = request.POST.get(f'choice{i}')
            is_correct = request.POST.get('correct') == f'choice{i}'
            if choice_text:
                Choice.objects.create(question=question, text=choice_text, is_correct=is_correct)

        return redirect('question_list')

    return render(request, 'add_question.html')

# -----edit qstn------------

def edit_question(request, question_id):
    question = Question.objects.get(id=question_id)
    choices = list(question.choices.all())

    if request.method == 'POST':
        question.text = request.POST.get('question_text')
        question.save()

        correct_index = int(request.POST.get('correct_choice'))

        for i, choice in enumerate(choices):
            text = request.POST.get(f'choice_text_{i}')
            choice.text = text
            choice.is_correct = (i == correct_index)
            choice.save()

        return redirect('question_list')

    return render(request, 'edit_question.html', {
        'question': question,
        'choices': choices,
    })


def delete_question(request, question_id):
    Question.objects.get(id=question_id).delete()
    return redirect('question_list')

def quiz_admin_list(request):
    questions = Question.objects.prefetch_related('choices').all()
    return render(request, 'admin_question_list.html', {'questions': questions})

    
    # ----------user quiz page-------------

def quiz(request):
    if 'quiz_question_ids' not in request.session:
        question_ids = list(Question.objects.values_list('id', flat=True))
        selected_ids = random.sample(question_ids, min(len(question_ids), 20))
        request.session['quiz_question_ids'] = selected_ids

    selected_ids = request.session['quiz_question_ids']
    questions = Question.objects.filter(id__in=selected_ids).prefetch_related('choices')
    questions = sorted(questions, key=lambda q: selected_ids.index(q.id))

    paginator = Paginator(questions, 1)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # ✅ Handle POST: Save selected answer
    if request.method == 'POST':
        qid = request.POST.get('question_id')
        selected = request.POST.get('answer')
        if qid and selected:
            request.session.setdefault('answers', {})
            request.session['answers'][qid] = selected
            request.session.modified = True

        if page_obj.has_next():
            return redirect(f'/quiz/?page={page_obj.next_page_number()}')
        else:
            return redirect('quiz_result')

    # ✅ Shuffle choices only for GET request (display)
    choices = list(page_obj.object_list[0].choices.all())
    random.shuffle(choices)
    page_obj.object_list[0].random_choices = choices
    

    return render(request, 'quiz.html', {'page_obj': page_obj})

def result_view(request):
    answers = request.session.get('answers', {})
    question_ids = request.session.get('quiz_question_ids', [])

    questions = Question.objects.filter(id__in=question_ids).prefetch_related('choices')
    questions = sorted(questions, key=lambda q: question_ids.index(q.id))  # maintain order

    score = 0
    results = []

    for question in questions:
        selected_id = answers.get(str(question.id))
        correct_choice = question.choices.filter(is_correct=True).first()
        selected_choice = question.choices.filter(id=selected_id).first() if selected_id else None

        if selected_choice and selected_choice.is_correct:
            score += 1

        results.append({
            'question': question,
            'selected': selected_choice,
            'correct': correct_choice,
        })

    # ✅ Clear session data for next quiz
    request.session.pop('quiz_question_ids', None)
    request.session.pop('answers', None)

    return render(request, 'quiz_result.html', {
        'score': score,
        'total': len(questions),
        'results': results
    })


# -------- email ------------------------

def send_email_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject=subject,
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
            fail_silently=False,
        )
        return redirect(send_email_view)
       

    return render(request, 'contact.html')


#  password reset


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)
            if users.exists():
                for user in users:
                    # Prepare email context
                    subject = 'Password Reset Requested'
                    email_template_name = 'registration/password_reset_email.html'
                    c = {
                        'email': user.email,
                        'domain': request.get_host(),
                        'site_name': 'Your Website',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email_body = render_to_string(email_template_name, c)
                    send_mail(subject, email_body, None, [user.email], fail_silently=False)
            # Redirect no matter what (do not reveal if email exists)
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset_form.html', {'form': form})

def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')

def password_reset_confirm(request, uidb64=None, token=None):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'registration/password_reset_confirm.html', {
            'form': form,
            'validlink': True
        })
    else:
        return render(request, 'registration/password_reset_confirm.html', {
            'validlink': False
        })

def password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')

#  -------review page -----------
def review_page(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            rating = int(request.POST.get('rating', 0))
            review_text = request.POST.get('review_text', '').strip()

            if rating and review_text:
                Review.objects.create(rating=rating, review_text=review_text,user=request.user)
                return redirect('review_page')  # Prevent resubmission on refresh

        reviews = Review.objects.order_by('-created_at')
        return render(request, 'reviewpage.html', {'reviews': reviews})

#  qstn add page








