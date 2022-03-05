from .models import USER, HOST
from .serializers import RegisterSerializer, PasswordRecoverySerializer, UpdatePasswordSerializer, ProfileSerializer
from rest_framework import generics, permissions, status
from django.http import JsonResponse
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from django.forms.models import model_to_dict
import json, sys

class RegisterView(APIView):
    #permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
    model = USER
    #def create(self, request):
    #    pass
    '''def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_200_OK)'''

    def post(self, request):
        serializer_class = RegisterSerializer(data=request.data)
        if serializer_class.is_valid():
            if request.data['Type'] ==  'User':
                db_table = USER
            else:
                db_table = HOST
            if request.data['Password1'] != request.data['Password2']:
                return JsonResponse({"status": "error", "message": "Password fields didn't match.",
                                     "data": serializer_class.errors}, status=status.HTTP_200_OK)
            try:
                user = db_table.objects.create(
                    Email=request.data['Email'],
                    FirstName=request.data['FirstName'],
                    LastName=request.data['LastName'],
                    Mobile=request.data['Mobile'],
                    Password=make_password(request.data['Password1']),
                    #DateCreated = timezone.now(),
                    #DateModified = timezone.now(),
                    #mobile=validated_data['mobile']
                )

                user.save()

                return JsonResponse({"status": "success", "data": serializer_class.data}, status=status.HTTP_200_OK)
            except:
                return JsonResponse({"status": "error", "data": serializer_class.errors,
                                     "message": "User account associated with the provided Email already exists"},
                                    status=status.HTTP_200_OK)
        else:
            return JsonResponse({"status": "error", "data": serializer_class.errors}, status=status.HTTP_200_OK)

'''class LoginClsView(APIView):
    serializer_class = LoginClsSerializer
    queryset = USER.objects.all()
    def get(self, data):
        username = data.get('Email')
        password = data.get('Password')
        try:
            user = USER.objects.get(Email__exact=username)
        except:
            msg = "Account does not exist"
            raise serializers.ValidationError(msg, code='authorization')
        if username and password:
            if not check_password(password, user.Password):
                msg = ('Unable to log in with provided credentials.'+ str(user.Password) + str(password))
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = ('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        data['Email'] = user
        return data
    def create(self, data):
        username = data.get('Email')
        return USER.objects.get(Email__exact=username)'''

class RecoverPasswordView(APIView):

    #permission_classes = (permissions.AllowAny,)
    """
    An endpoint for changing password.
    """
    model = USER
    queryset = USER.objects.all()
    serializer_class = PasswordRecoverySerializer

    '''def get_object(self, request, **kwargs):
        with open("readme.txt", "w") as f:
            f.write(str(request.data))
            f.close()
        accounts = USER.objects.get(Email=request.data['Email'])
        return accounts'''
    def put(self, request):
        #self.lookup_field = 'pk'
        if request.data['Type'] == 'User':
            db_table = USER
        else:
            db_table = HOST
        serializer_class = PasswordRecoverySerializer(data=request.data)
        if serializer_class.is_valid():
            try:
                self.object = db_table.objects.get(Email=request.data['Email'])
            except:
                return Response({'status': 'error',
                                     "message": "User account associated with the Email doesnot exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            if request.data['Password1'] != request.data['Password2']:
                return Response({'status': 'error',
                                 "message": "Password fields didn't match."},
                                status=status.HTTP_400_BAD_REQUEST)
            # make_password also hashes the password that the user will get
            self.object.Password = make_password(request.data['Password1'])
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password resetted successfully',
                'data': []
            }
            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdatePasswordView(APIView):
    """
    An endpoint for changing password.
    """
    model = USER
    queryset = USER.objects.all()
    serializer_class = UpdatePasswordSerializer
    def put(self, request):
        #self.lookup_field = 'pk'
        if request.data['Type'] ==  'User':
            db_table = USER
        else:
            db_table = HOST
        serializer_class = UpdatePasswordSerializer(data=request.data)
        if serializer_class.is_valid():
            try:
                self.object = db_table.objects.get(Email=request.data['Email'])
            except:
                return Response({'status': 'error',
                                 "message": "User account associated with the Email doesnot exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not check_password(request.data['OldPassword'], self.object.Password):
                return Response({'status': 'error', "message": "Incorrect old password"},
                                status=status.HTTP_400_BAD_REQUEST)
            if request.data['Password1'] != request.data['Password2']:
                return Response({'status': 'error',
                                 "message": "Password fields didn't match."},
                                status=status.HTTP_400_BAD_REQUEST)
            # make_password also hashes the password that the user will get
            self.object.Password = make_password(request.data['Password1'])
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password resetted successfully',
                'data': []
            }
            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    def get(self, request):
        if request.data['Type'] ==  'User':
            db_table = USER
        else:
            db_table = HOST
        try:
            item = db_table.objects.get(Email=request.data['Email'])
            return Response({"status": "success", "data": item}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"status": "error", "data": "username does not exist"}, status=status.HTTP_200_OK)

    '''def get(self, request):
        serializer_class = ProfileSerializer(data=request.data)
        if serializer_class.is_valid():
            try:
                self.object = USER.objects.get(Email=request.data['Email'])
            except:
                return Response({'status': 'error',
                                 "message": "User account associated with the Email doesnot exist"},
                                status=status.HTTP_400_BAD_REQUEST)
            response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'data': [self.object],
                }
            return Response(response, status=status.HTTP_200_OK)
        return Response({'status': 'error'},
                                status=status.HTTP_400_BAD_REQUEST)'''
