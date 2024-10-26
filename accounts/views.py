from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from .models import UserProfile
from course_manager.models import Course


# Create your views here.

@api_view(['POST', 'GET'])
def login_view(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/') #FIXME: redirect to home page of frontend
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)
    return Response({"message":"ok"}) #FIXME: redirect to login page of frontend

@api_view(['POST', 'GET'])
def register_user(request):
    if request.method == 'POST':
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            course_code = request.data.get('course_code')
            course = Course.objects.get(code=course_code)
            role = request.data.get('role') #Handle the role injection within a middleware
            user = User.objects.create(username= username, email= email, password= password, first_name= first_name, last_name= last_name)
            user.save()
            profile = UserProfile.objects.create(user= user, role=role)
            profile.course.add(course)
            profile.save()
            return redirect('accounts:login')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message":"ok"}) #FIXME: redirect to register page of frontend

def logout_view(request):
    logout(request)
    return redirect('accounts:login') #FIXME: redirect to login page of frontend
