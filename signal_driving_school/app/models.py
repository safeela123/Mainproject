from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    license_applied = models.BooleanField(default=False)
    registration_date = models.DateField(auto_now_add=True)

class Vehicle(models.Model):
    vehicle_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=50)  # e.g., Car, Bike, Truck
    is_available = models.BooleanField(default=True)


class DrivingSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    session_date = models.DateField()
    session_time = models.TimeField()
    duration_minutes = models.IntegerField()
    status = models.CharField(max_length=20)


class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)  # e.g., Cash, UPI, Card
    status = models.CharField(max_length=20)

class Test(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test_date = models.DateField()
    result = models.CharField(max_length=10)
    remarks = models.TextField(blank=True)

from django.db import models

class Admission(models.Model):
    # Personal Information
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
        ('bike', 'Bike')
    ])
    # course_package = models.CharField(max_length=50, choices=[
    #     ('basic', 'Basic - 10 Sessions'),
    #     ('standard', 'Standard - 15 Sessions + Test'),
    #     ('advanced', 'Advanced - 20 Sessions + Test + Pickup')
    # ])

    # Admission Details
    admission_date = models.DateField(auto_now_add=True)
    preferred_batch_time = models.CharField(max_length=20, choices=[
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening')
    ])

    # Payment Status
    # payment_status = models.CharField(max_length=20, choices=[
    #     ('pending', 'Pending'),
    #     ('paid', 'Paid')
    # ], default='pending')

    def __str__(self):
        return self.name

from django.db import models

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
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admission_number = models.CharField(max_length=20, unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.admission_number}"
