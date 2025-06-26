from django.shortcuts import render,redirect,get_object_or_404
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
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token as csrf
from django.http import HttpResponseForbidden
from django.utils.dateparse import parse_date


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
    if request.method == 'POST':
        name = request.POST['name']
        psw = request.POST['psw']
        user = auth.authenticate(username=name, password=psw)
        if user is not None:
            auth.login(request, user)
            if user.is_superuser:
                return redirect(adindex)
            else:
                return redirect(index)
        else:
            messages.error(request, "Invalid username or password")  # Error message
            return redirect('login')
    return render(request, 'login.html')


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



from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
import razorpay
from .models import Admission, Payment
from django.conf import settings

@csrf_protect
def admission(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if Admission.objects.filter(user=request.user).exists():
        messages.error(request, "You have already taken admission. You can't apply again.")
        # return redirect(index)  # ✅ Make sure 'index' is quoted and defined in urls

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

        adm = Admission.objects.create(
            user=request.user,
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

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': amount * 100,
            'currency': 'INR',
            'payment_capture': 1
        })

        money = Payment.objects.create(
            student=adm,
            user=request.user,
            amount=amount,
            razorpay_order_id=razorpay_order['id'],
            payment_status='pending'
        )

        callback_url = request.build_absolute_uri(reverse('payment_success'))

        context = {
            'order_id': razorpay_order['id'],
            'amount': amount * 100,
            'key_id': settings.RAZORPAY_KEY_ID,
            'callback_url': callback_url,
            'admission': adm
        }

        return render(request, 'payment.html', context)

    return render(request, 'admission.html')


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
            # vehicle_type = request.POST.get('vehicle_type')
            batch = request.POST.get('preferred_batch_time')
            # Calculate amount
            # if vehicle_type == 'car':
            #     amount = 8000
            # elif vehicle_type == 'bike':
            #     amount = 2000
            # elif vehicle_type == 'both':
            #     amount = 10000
            # else:
            #     messages.error(request, "Please select a valid vehicle type.")
        
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
            data.preferred_batch_time=batch
            
            data.save()
            return redirect(adindex)
        
        return render(request,'adupdate.html',{'data':data,'data1':data1})
# ---------delete------------
def delete(request,id):
    Admission.objects.get(id=id).delete()
    
    return redirect(adindex)

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

#  -------review page ----------------------------------
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
    
# ------------------------attendance --------------------------


@csrf_exempt
def submit_attendance(request):
    if request.method == 'POST':
        try:
            name = int(request.POST.get('student_id'))
            student = Admission.objects.get(pk=name)

            # Validate date
            input_date = parse_date(request.POST.get('date'))
            today = timezone.localdate()

            if input_date and input_date > today:
                messages.error(request, "You cannot mark attendance for a future date.")
                return redirect('submit_attendance')

            # Save attendance
            Attendance.objects.create(
                student=student,
                date=input_date,
                lesson_type=request.POST.get('lesson_type'),
                time_in=request.POST.get('time_in'),
                time_out=request.POST.get('time_out'),
                notes=request.POST.get('notes', '')
            )
            messages.success(request, "Attendance marked successfully.")
            return redirect('records')
        
        except (ValueError, Admission.DoesNotExist):
            messages.error(request, "Invalid student ID.")
            return redirect('submit_attendance')

    return render(request, 'attendanceform.html', {
        'today': timezone.localdate().isoformat()
    })



def view_records(request):
    records = Attendance.objects.all().order_by('-date')
    return render(request, 'attendancerecord.html', {'records': records})


# def delete_attendance(request, attendance_id):
#     if not request.user.is_authenticated:
#         return redirect('login')  # Redirect to login if not authenticated

#     attendance = get_object_or_404(Attendance, id=attendance_id)

    
#     if not request.user.is_superuser:
#         return HttpResponseForbidden("Only superusers can delete attendance records.")

#     attendance.delete()
#     return redirect(view_records)  # or the attendance list page


def weekly_attendance(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not Admission.objects.filter(user=request.user).exists():
        return render(request, 'user_weekly_attendance.html', {
            'error': 'Admission record not found for this user.'
        })

    admission = Admission.objects.get(user=request.user)

    today = timezone.now().date()
    start_week = today - timedelta(days=today.weekday())  # Monday
    end_week = start_week + timedelta(days=6)             # Sunday

    attendance_records = Attendance.objects.filter(
        student=admission,
        date__range=(start_week, end_week)
    ).order_by('date', 'time_in')

    return render(request, 'user_weekly_attendance.html', {
        'attendance_records': attendance_records,
        'start_week': start_week,
        'end_week': end_week,
        'today': today,
    })

#  -------------------profile -----------------------------


def view_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    admission = Admission.objects.filter(user=request.user).first()

    if not admission:
        return render(request, 'profile.html', {
            'error': 'No admission record found. Please complete your admission.'
        })

    return render(request, 'profile.html', {'admission': admission})


def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    admission = Admission.objects.filter(user=request.user).first()
    if not admission:
        # Optionally redirect to admission form or show message
        return render(request, 'edit_profile.html', {
            'error': 'No admission record found. Please complete admission first.'
        })

    if request.method == 'POST':
        admission.name = request.POST.get('name')
        admission.date_of_birth = request.POST.get('date_of_birth')
        admission.gender = request.POST.get('gender')
        admission.phone = request.POST.get('phone')
        admission.address = request.POST.get('address')
        admission.emergency_contact = request.POST.get('emergency_contact')
        admission.vehicle_type = request.POST.get('vehicle_type')
        admission.preferred_batch_time = request.POST.get('preferred_batch_time')

        if 'photo' in request.FILES:
            admission.photo = request.FILES['photo']
        if 'identity_proof_upload' in request.FILES:
            admission.identity_proof_upload = request.FILES['identity_proof_upload']

        admission.save()
        return redirect('view_profile')

    return render(request, 'edit_profile.html', {'admission': admission})


# ----------------------- test -------------------
def add_test(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers are allowed to add test details.")

    if request.method == 'POST':
        adno = request.POST.get('ad_no')
        if not adno:
            messages.error(request, "Admission number is required.")
            return redirect('add_test')

        try:
            admission = Admission.objects.get(pk=int(adno))
        except (ValueError, Admission.DoesNotExist):
            messages.error(request, "Invalid admission number.")
            return redirect('add_test')

        TestDetails.objects.create(
            admission=admission,
            test_type=request.POST.get('test_type'),
            attempt_number=request.POST.get('attempt_number'),
            test_date=request.POST.get('test_date'),
            score=request.POST.get('score'),
            passed=request.POST.get('passed') == 'true'
        )
        messages.success(request, "Test added successfully.")
        return redirect('test_list')

    return render(request, 'test_form.html', {
        'form_title': 'Add Test Details',
        'test': None
    })



def edit_test(request, test_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers are allowed to edit test details.")

    test = get_object_or_404(TestDetails, id=test_id)

    if request.method == 'POST':
        test.test_type = request.POST.get('test_type')
        test.attempt_number = request.POST.get('attempt_number')
        test.test_date = request.POST.get('test_date')
        test.score = request.POST.get('score')
        test.passed = request.POST.get('passed') == 'true'
        test.save()
        messages.success(request, "Test details updated successfully.")
        return redirect('test_list')

    return render(request, 'test_form.html', {
        'form_title': 'Edit Test Details',
        'test': test
    })



def delete_test(request, test_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_superuser:
        return HttpResponseForbidden("Only superusers are allowed to delete test details.")

    test = get_object_or_404(TestDetails, id=test_id)
    test.delete()
    messages.success(request, "Test deleted successfully.")
    return redirect('test_list')

def test_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_superuser:
        tests = TestDetails.objects.all().order_by('-test_date')
    else:
        admission = get_object_or_404(Admission, user=request.user)
        tests = admission.tests.all().order_by('-test_date')

    return render(request, 'test_list.html', {'tests': tests})

def test_details(request):
    if request.user.is_authenticated:
        try:
            admission = Admission.objects.get(user=request.user)
            print("Admission Found:", admission)

            test_results = TestDetails.objects.filter(admission=admission)
            print("Test Results Count:", test_results.count())
            for test in test_results:
                print("Test:", test.test_type, test.test_date, test.score)

        except Admission.DoesNotExist:
            print("Admission not found.")
            test_results = []

        return render(request, 'user_test_details.html', {'test_results': test_results})
    
    return redirect('login')





