from .models import USER, HOST
from event.models import Event, Bookings
from .serializers import RegisterSerializer, PasswordRecoverySerializer, \
    UpdatePasswordSerializer, ProfileSerializer, ResetPasswordSerializer, \
    UpdateProfileSerializer
from rest_framework import generics, permissions, status
from django.http import JsonResponse
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from django.forms.models import model_to_dict
from datetime import date
import json, sys
from rest_framework.renderers import JSONRenderer

# Mail
from django.conf import settings
from django.core.mail import send_mail


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    model = USER

    def post(self, request):
        serializer_class = RegisterSerializer(data=request.data)
        if serializer_class.is_valid():
            if request.data['Type'].lower() == 'User'.lower():
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
                )
                user.save()
                return JsonResponse({"status": "success", "data": serializer_class.data}, status=status.HTTP_200_OK)
            except:
                return JsonResponse({"status": "error", "data": serializer_class.errors,
                                     "message": "User account associated with the provided Email already exists"},
                                    status=status.HTTP_200_OK)
        else:
            return JsonResponse({"status": "error", "data": serializer_class.errors}, status=status.HTTP_200_OK)


class RecoverPasswordView(APIView):
    """ An endpoint for recovering the password. Given a username, send an email with an update password link"""

    model = USER
    serializer_class = PasswordRecoverySerializer

    def post(self, request):
        serializer_class = PasswordRecoverySerializer(data=request.data)
        if serializer_class.is_valid():
            try:
                db_table = USER
                user_details = db_table.objects.get(Email=request.data['Email'])
            except:
                try:
                    db_table = HOST
                    user_details = db_table.objects.get(Email=request.data['Email'])
                except:
                    return Response({'status': 'error',
                                     "message": "User account associated with the Email doesnot exist"},
                                    status=status.HTTP_400_BAD_REQUEST)

        # Send Mail    
        subject = 'GigsNChill password reset'
        import random
        from datetime import datetime
        verification_code = (''.join([str(random.randint(0,9)) for _ in range(6)]))
        message = f'Hi {user_details.FirstName}, reset your password at the following' \
                  f' link: https://gigsnchill-events.web.app/resetpassword ' \
                  f'and your verification code is ' + str(verification_code)
        user_details.VerificationCode = verification_code
        user_details.CodeCreationTime = datetime.now().time()
        user_details.save()
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.data['Email']]
        send_mail(subject, message, email_from, recipient_list)

        response = {
            'status': 'success',
            'code': status.HTTP_200_OK,
            'message': 'Password reset email sent',
            'data': [],
        }
        return Response(response, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """ Replaces the password, follows after a recover password step """
    model = USER
    queryset = USER.objects.all()
    serializer_class = ResetPasswordSerializer

    def put(self, request):
        serializer_class = ResetPasswordSerializer(data=request.data)
        if serializer_class.is_valid():
            try:
                db_table = USER
                user_details = db_table.objects.get(Email=request.data['Email'])
            except:
                try:
                    db_table = HOST
                    user_details = db_table.objects.get(Email=request.data['Email'])
                except:
                    return Response({'status': 'error',
                                     "message": "User account associated with the Email doesnot exist"},
                                    status=status.HTTP_400_BAD_REQUEST)
            if request.data['VerificationCode'] == user_details.VerificationCode:
                # make_password also hashes the password that the user will get
                user_details.Password = make_password(request.data['Password'])
                user_details.save()
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password resetted successfully',
                    'data': []
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Incorrect Verification Code',
                    'data': []
                }
                return Response(response, status=status.HTTP_200_OK)

        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    """ An endpoint for updating the password """
    model = USER
    queryset = USER.objects.all()
    serializer_class = UpdatePasswordSerializer

    def put(self, request):
        if request.data['Type'].lower() == 'User'.lower():
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


class ProfileView(generics.ListAPIView):
    """
    This view should return a list of all the Booked/Hosted Events for
    the user as determined by the Email and Type portion of the URL.
    """
    serializer_class = ProfileSerializer
    renderer_classes = (JSONRenderer,)
    model = [USER, HOST, Event]

    def get(self, request, Email, Type="user"):
        try:
            if Type.lower() == 'user':
                db_table = USER
                # get all the events registered(booked) by a user
                data = model_to_dict(db_table.objects.get(Email=Email))
                data["FutureEvents"], data["PastEvents"], data["CancelledEvents"] = [], [], []
                User_Events = [model_to_dict(book) for book in
                               Bookings.objects.filter(UserId=Email)]
                for book in User_Events:
                    # Get the Event details from the Event db based on the booking by Specified User
                    registered_event = model_to_dict(Event.objects.get(EventId=book['EventId']))
                    # Verify the date of the event and update in the Future/Past Event
                    # in the data to be sent as response
                    book.update(registered_event)
                    if book['BookingStatus'].lower() == 'cancelled':
                        data["CancelledEvents"].append(book)
                    elif registered_event['EventDate'] < date.today():
                        data["PastEvents"].append(book)
                    else:
                        data["FutureEvents"].append(book)
                del data["Password"]
            else:
                db_table = HOST
                data = model_to_dict(db_table.objects.get(Email=Email))
                del data["Password"]
                data["FutureEvents"], data["PastEvents"], data["CancelledEvents"] = [], [], []
                for eve in Event.objects.filter(HostId=Email):
                    eve = model_to_dict(eve)
                    if eve['EventStatus'].lower() == 'cancelled':
                        data["CancelledEvents"].append(eve)
                    elif eve['EventDate'] < date.today():
                        data["PastEvents"].append(eve)
                    else:
                        data["FutureEvents"].append(eve)
                '''data["FutureEvents"] = [model_to_dict(eve)
                                        for eve in Event.objects.filter(HostId=Email,
                                                                        EventDate__gte=date.today())]
                data["PastEvents"] = [model_to_dict(eve)
                                      for eve in Event.objects.filter(HostId=Email,
                                                                      EventDate__lt=date.today())]
                print(data["FutureEvents"], data["PastEvents"])'''
            return Response({"status": "success", 'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": "username does not exist" + str(request.data) + str(e)},
                            status=status.HTTP_200_OK)


class UpdateProfileView(APIView):
    serializer_class = UpdateProfileSerializer
    def put(self, request):
        if request.data['Type'].lower() == 'User'.lower():
            db_table = USER
        else:
            db_table = HOST
        serializer_class = UpdateProfileSerializer(data=request.data)
        if serializer_class.is_valid():
            try:
                try:
                    user_info = db_table.objects.get(Email=request.data['Email'])
                except:
                    return Response({'status': 'error',
                                     "message": "User account associated with the Email doesnot exist"},
                                    status=status.HTTP_400_BAD_REQUEST)
                if 'FirstName' in request.data and request.data['FirstName'] != '':
                    user_info.FirstName = request.data['FirstName']
                if 'LastName' in request.data and request.data['LastName'] != '':
                    user_info.LastName = request.data['LastName']
                if 'Mobile' in request.data and request.data['Mobile'] != '':
                    user_info.Mobile = request.data['Mobile']
                if 'Password' in request.data and request.data['Password'] != '':
                    user_info.Password = make_password(request.data['Password'])
                user_info.save()
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Profile Updated successfully'
                }
                return Response(response, status=status.HTTP_200_OK)
            except:
                return Response({"status": "error",
                                 'message': 'Profile update failed'},
                                status=status.HTTP_200_OK)
        return Response({"status": "error", "data": serializer_class.errors,
                         'message': 'Profile update failed'}, status=status.HTTP_200_OK)
