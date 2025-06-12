from django.urls import path
from . import views

urlpatterns = [
    path('',views.login),
    path('register/', views.register, name='register'),
    path('logout',views.logout),
    path('index',views.index),
    path('admission',views.admission),
    path('verify-admission', views.verify_admission_number, name='verify_admission'),
    path('quizview', views.quiz_view, name='quiz'),
    path('result', views.result_view, name='quiz_result'),
    path('email', views.send_email_view, name='send_email'),

]
