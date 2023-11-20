from django.shortcuts import render,redirect
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import pyotp
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from .models import Room,Topic,Message,User,OTP
from .forms import RoomForm,UserForm,MyUserCreationForm,OTPCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()




# Create your views here.

'''rooms = [
    {'id':1,'name':"lets learn python"},
    {'id':2,'name':"lets learn django"},
]'''
# def resend_otp(request):
#     if request.method == "POST":
#         email = request.session.get('email')
#         print(email)
#         username = request.session.get('username')
#         print(username)

#         try:
#             user = User.objects.get(email=email)

#             # Generate a new OTP
#             otp_secret_key = 'ljauvdhsnuzozcov'  # Replace with your actual secret key
#             totp = pyotp.TOTP(otp_secret_key)
#             otp_code = totp.now()
#             print("Generated OTP:", otp_code)

#             # Send the new OTP code via email (you need to implement this part)
#             send_otp_email(email, otp_code)

#             # Update the OTP record
#             otp = OTP.objects.get(email=email)
#             otp.code = otp_code
#             otp.is_verified = False
#             otp.created_at = datetime.now(timezone.utc)
#             otp.save()
#             messages.success(request, 'New OTP sent to your email.')

#             # Redirect to the OTP verification page
#             return redirect('login_otp_verification')
            
#         except User.DoesNotExist:
#             messages.error(request, 'User not found.')

#     return render(request, 'base/login_otp_verification.html')

def resend_otp(request):
    if request.method == "POST":
        email = request.session.get('email')
        username = request.session.get('username')

        try:
            user = User.objects.get(email=email)

            # Get the most recent unverified OTP for the user
            otp = OTP.objects.filter(email=email, is_verified=False).order_by('-created_at').first()

            if otp:
                # Generate a new OTP
                otp_secret_key = 'ljauvdhsnuzozcov'  # Replace with your actual secret key
                totp = pyotp.TOTP(otp_secret_key)
                otp_code = totp.now()
                print("Generated OTP:", otp_code)

                # Send the new OTP code via email (you need to implement this part)
                send_otp_email(email, otp_code)

                # Update the OTP record
                otp.code = otp_code
                otp.created_at = timezone.now()
                otp.save()
                messages.success(request, 'New OTP sent to your email.')
            else:
                messages.error(request, 'No unverified OTP found.')

        except User.DoesNotExist:
            messages.error(request, 'User not found.')

    return redirect('login_otp_verification')

def login_otp_verification(request):
    if request.method == "POST":
        entered_otp_code = request.POST.get('otp_code')
        email = request.session.get('email')
        username = request.session.get('username')

        try:
            otp = OTP.objects.get(email=email, code=entered_otp_code, is_verified=False)

            # Check OTP expiration
            current_time = datetime.now(timezone.utc)  
            otp_expiration_time = otp.created_at + timedelta(minutes=1)  # Adjust the expiration time as needed

            if current_time <= otp_expiration_time:
                # Mark the OTP code as verified
                otp.is_verified = True
                otp.save()

                # Get the user by email or username
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        user = None

                if user:
                    # Log in the user
                    login(request, user)
                    messages.success(request, 'Login successful. You are now logged in.')
                    return redirect('home')
                else:
                    messages.error(request, 'User not found.')
            else:
                messages.error(request, 'OTP has expired. Please request a new one.')

        except ObjectDoesNotExist:
            messages.error(request, 'Invalid OTP. Please try again.')

    context = {'otp_sent': True}
    return render(request, 'base/login_otp_verification.html', context)


def loginPage(request):
    page= 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        username=request.POST.get('username')
        email=request.POST.get('email')

        try:
            user=User.objects.get(username=username,email=email)
        except:
            messages.error(request,'User not found.')
            return redirect('login')

        # user = authenticate(request,username=username ,email=email)
        if user is not None:
            email = user.email
            username = user.username
            print(email)
            request.session['email'] = email
            request.session['username'] = username
            otp_secret_key = 'ljauvdhsnuzozcov'  # Replace with your actual secret key
            totp = pyotp.TOTP(otp_secret_key)
            otp_code = totp.now()
            print("Generated OTP:", otp_code)

            # Send the OTP code via email
            

            # Create an OTP record for later verification
            
            send_otp_email(email, otp_code)
            otp = OTP.objects.create(email=email, code=otp_code)
           
            return redirect('login_otp_verification')
            
            
        else:
            messages.error(request,'Either the username or the password is not correct.')
            

    context={'page':page}
    return render(request,'base/login_register.html',context)

# def loginPage(request):
#     page= 'login'
#     if request.user.is_authenticated:
#         return redirect('home')
#     if request.method=="POST":
#         username=request.POST.get('username')
#         email=request.POST.get('email')

#         try:
#             user=User.objects.get(username=username,email=email)
#         except:
#             messages.error(request,'User not found.')

#         user = authenticate(request,username=username ,email=email)
#         if user is not None:
#             login(request,user)
#             return redirect('home')
#         else:
#             messages.error(request,'Either the username or the password is not correct.')
            

#     context={'page':page}
#     return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')



#   
    


def send_otp_email(email, otp_code):
    print('////////////')
    # Define email subject and message
    subject = 'Your OTP for Registration'
    message = f'Your OTP code is: {otp_code}'

    print(subject,"subject=======================================")
    print(message,"messsage****************************************")

    # Define sender and recipient email addresses
    from_email = 'punitk.brainerhub@gmail.com'  # Replace with your email address
    recipient_list = [email]

    # Send the email using send_mail
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    
     
def otp_verification(request):
    if request.method == "POST":
        entered_otp_code = request.POST.get('otp_code')
        email = request.session.get('email')
        username = request.session.get('username')

        try:
            otp = OTP.objects.get(email=email, code=entered_otp_code, is_verified=False)

            # Check OTP expiration
            current_time = datetime.now(timezone.utc)  # Make current_time timezone-aware
            otp_expiration_time = otp.created_at + timedelta(minutes=1)  # Adjust the expiration time as needed

            if current_time <= otp_expiration_time:
                # Mark the OTP code as verified
                otp.is_verified = True
                otp.save()

                # Create a new user account (only if OTP is verified and user doesn't exist)
                user, created = User.objects.get_or_create(username=username, email=email)

                if created:
                    # User is registered only if OTP is verified and user doesn't exist
                    login(request, user)
                    messages.success(request, 'Registration successful. You are now logged in.')
                    return redirect('home')  # Redirect to the home page or another appropriate page
                else:
                    messages.error(request, 'User with this email already exists.')
            else:
                messages.error(request, 'OTP has expired. Please request a new one.')

        except ObjectDoesNotExist:
            messages.error(request, 'Invalid OTP. Please try again.')

    context = {'otp_sent': True}
    return render(request, 'base/otp_verification.html', context)


# def otp_verification(request):
#     if request.method == "POST":
#         entered_otp_code = request.POST.get('otp_code')
        
        
#         print('entered otp:',entered_otp_code)
#         email = request.session.get('email')
#         username = request.session.get('username')
#         print('email:',email)
#         otp = OTP.objects.filter(email=email, code=entered_otp_code, is_verified=False).first()
        
#         if otp and otp.code == entered_otp_code:              # Mark the OTP code as verified
#             otp.is_verified = True
#             otp.save()

#             # Create a new user account
#             user, created = User.objects.get_or_create(username=username, email=email)

#             if created:
#                 # User is registered only if OTP is verified and user doesn't exist
#                 login(request, user)
#                 messages.success(request, 'Registration successful. You are now logged in.')
#                 return redirect('home')  # Redirect to the home page or another appropriate page
#             else:
#                 messages.error(request, 'User with this email already exists.')
#         else:
#             messages.error(request, 'Invalid OTP. Please try again.')

#     context = {'otp_sent': True}
#     return render(request, 'base/otp_verification.html', context)

def registerPage(request):
    form = MyUserCreationForm()
    otp_form = OTPCreationForm()

    print('****************')

    if request.method == "POST":
        print("inside post request")
        form = MyUserCreationForm(request.POST)
        
        otp_form = OTPCreationForm(request.POST)
        print(form,"form---------------------------------------")

        if form.is_valid() :
            
            print(form)
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            print(email)
            request.session['email'] = email
            request.session['username'] = username
            otp_secret_key = 'ljauvdhsnuzozcov'  # Replace with your actual secret key
            totp = pyotp.TOTP(otp_secret_key)
            otp_code = totp.now()
            print("Generated OTP:", otp_code)

            # Send the OTP code via email
            

            # Create an OTP record for later verification
            
            send_otp_email(email, otp_code)
            otp = OTP.objects.create(email=email, code=otp_code)
           
            return redirect('otp_verification')

    context = {'form': form, }
    return render(request, 'base/login_register.html', context)


# def registerPage(request):
    
#     form=MyUserCreationForm()

#     if request.method == "POST":
#         form=MyUserCreationForm(request.POST)
#         if form.is_valid():
#             user=form.save(commit=False)
#             user.username = user.username.lower()
#             user.save()
#             login(request,user)
#             return redirect('home')
#         else:
#             messages.error(request,'An error occurred during registration.')


    
#     context={'form':form}
#     return render(request,'base/login_register.html',context)
    
@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') !=None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)

    )
    topics=Topic.objects.all()[0:5]
    room_count=rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context={
        'rooms':rooms,
        'topics':topics,
        'room_count':room_count,
        'room_messages':room_messages,
    }
    return render(request,'base/home.html',context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method =="POST":
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)

    context={
        'room':room,
        'room_messages':room_messages,
        'participants' : participants,
    }
    
    return render(request,'base/room.html',context)


def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()

    context={'user':user,
             'rooms':rooms,
             'room_messages':room_messages,
             'topics':topics,
            }
    return render(request,'base/profile.html',context)
    
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics= Topic.objects.all()
    if request.method == "POST":
       topic_name=request.POST.get('topic')
       topic,created =Topic.objects.get_or_create(name=topic_name)

       Room.objects.create(
           host=request.user,
           topic=topic, 
           name=request.POST.get('name'),
           description=request.POST.get('description'),
       )


     
       return redirect('home')
    context={'form':form,
             'topics':topics,}
    return render (request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form= RoomForm(instance=room)
    topics= Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    if request.method == "POST":
        topic_name=request.POST.get('topic')
        topic,created =Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        
    context={'form':form,'room':room,'topics':topics,}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    if request.method=="POST":
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})


@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    if request.method=="POST":
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})


@login_required(login_url='login')
def updateUser(request):
    user=request.user
    form = UserForm(instance=user)
    if request.method=='POST':
        form= UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)

    context={'form':form,}

    return render(request,"base/update-user.html",context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') !=None else ''
    topics=Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topics':topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request,'base/activity.html',{})