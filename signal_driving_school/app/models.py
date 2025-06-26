from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Admission(models.Model):
    # Personal Information
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to auth user
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    photo = models.FileField(upload_to='student_photos/', blank=True, null=True)

    # Contact Details
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15, blank=True)

    # Identification
    aadhar_number = models.CharField(max_length=12, unique=True)
    identity_proof_upload = models.FileField(upload_to='documents/', blank=True, null=True)

    # Course / Vehicle Type Selection
    vehicle_type = models.CharField(max_length=20, choices=[
        ('car', 'Car'),
        ('bike', 'Bike'),
        ('both','Both')
    ])
    # Admission Details
    admission_date = models.DateField(auto_now_add=True)
    preferred_batch_time = models.CharField(max_length=20, choices=[
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening')
    ])

    def __str__(self):
        return self.name
    
class Attendance(models.Model):
    student = models.ForeignKey(Admission,on_delete=models.CASCADE)
    date = models.DateField()
    lesson_type = models.CharField(max_length=50, choices=[
        ('Classroom', 'Classroom'),
        ('Behind the Wheel', 'Behind the Wheel')
    ])
    
    time_in = models.TimeField()
    time_out = models.TimeField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student_name} - {self.date}"
    
class Payment(models.Model):
    student = models.ForeignKey(Admission, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid')],
        default='pending'
    )

    def __str__(self):
        return f"{self.user.username} - {self.course} - {self.payment_status}"
        

class Question(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} stars - {self.review_text[:30]}..."
    
class TestDetails(models.Model):
    admission = models.ForeignKey('Admission', on_delete=models.CASCADE, related_name='tests')
    test_type = models.CharField(max_length=50, choices=[
        ('theory', 'Theory Test'),
        ('practical', 'Practical Test'),
    ])
    test_date = models.DateField()
    score = models.PositiveIntegerField()
    passed = models.BooleanField(default=False)
    attempt_number = models.PositiveIntegerField(default=1)  # Added field

    def __str__(self):
        return f"{self.get_test_type_display()} - Attempt {self.attempt_number} on {self.test_date} ({'Passed' if self.passed else 'Failed'})"
