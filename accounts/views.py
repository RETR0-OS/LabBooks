from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from course_manager.models import Course
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)  # Generate JWT tokens
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def register_user(request):
    try:
        username = request.data.get('user')
        password = request.data.get('pwd')
        email = request.data.get('email')
        first_name = request.data.get('firstName')
        last_name = request.data.get('lastName')
        course_code = request.data.get('courseCode')
        course = Course.objects.get(code=course_code)
        role = request.data.get('role')  # Handle this in middleware as planned

        # Create user with hashed password
        user = User.objects.create_user(username=username, email=email, password=password, 
                                        first_name=first_name, last_name=last_name)
        profile = UserProfile.objects.create(user=user, role=role)
        profile.course.add(course)
        profile.save()
        
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def logout_view(request):
    if request.user.is_authenticated:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        logout(request)
    return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
