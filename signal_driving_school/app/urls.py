from django.urls import path
from . import views

urlpatterns = [
    path('',views.login,name='login'),
    path('register/', views.register, name='register'),
    path('logout',views.logout),
    path('index',views.index),
    path('adindex',views.adindex),
    path('admission',views.admission),
    path('update/<int:id>',views.adupdate),
    path('delete/<int:id>',views.delete),
    path('payment-success/', views.payment_success, name='payment_success'),

    # quiz
    path('add-question', views.add_question, name='add_question'),
    path('quizlist', views.quiz_admin_list, name='question_list'),
    path('edit-question/<int:question_id>', views.edit_question, name='edit_question'),
    path('delete-question/<int:question_id>', views.delete_question, name='delete_question'),
    path('quiz/', views.quiz, name='quiz'),
    path('result', views.result_view, name='quiz_result'),
    path('email', views.send_email_view, name='send_email'),

    # reset password
     path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
#  review 
    path('reviews', views.review_page, name='review_page'),
]
