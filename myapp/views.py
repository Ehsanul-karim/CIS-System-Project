from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from demo import settings
from .models import UserTable, UserProfile, MapMarker, AdminProfile, victimInfo, CASE_FIR, Relation
from django.http import JsonResponse
from .forms import RegistrationForm
from .tokens import generate_token
from django.urls import reverse
from django.views.generic import TemplateView
import datetime
import os


class MapView(TemplateView):
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['markers'] = MapMarker.objects.all()
        return context

def context_date(request):
    stations = list(MapMarker.objects.values('latitude','longitude','name')[:100])
    print(stations[:2])
    context = {'stations' : stations}
    return render(request,'map.html',context)

def near_stations(request):
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    SName = request.GET.get('name')
    print(latitude,longitude,SName)
    MapMarker.objects.create(name = SName, latitude =  latitude, longitude =  longitude)
    response_data = {'message': 'Data received successfully'}
    return JsonResponse(response_data)


# Create your views here.
def home(request):
    return render(request, "Welcome_Page.html")

def users(request):
    if request.method == 'POST':
        print ('Hello', request.POST['name'])
        x = request.POST['name']
        y = request.POST['age']
        z = request.POST['status']
        w = request.FILES['image']
        UserTable.objects.create(name = x, age =  y, status =  z, image = w)
        user = UserTable.objects.all()
        return render(request, "allusers.html", {"lists": user})
    if request.method == 'GET':       
        user = UserTable.objects.all()
        return render(request, "allusers.html", {"lists": user})

def edit(request,user_id):
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        new_age = request.POST.get('new_age')
        new_status = request.POST.get('new_status')
        new_image = request.FILES.get('image')
        this_user = UserTable.objects.get(pk=user_id)
        if new_name:
            this_user.name = new_name
        if new_age:
            this_user.age = new_age
        if new_status == 'True':
            this_user.status = True
        else:
            this_user.status = False
        if new_image:
            this_user.image = new_image
        this_user.save()
    userinfo = get_object_or_404(UserTable, id=user_id)
    return render(request, 'edit.html', {'user': userinfo})

def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = UserTable.objects.get(pk=user_id)
            user.delete()
            return JsonResponse({'message': 'Record deleted successfully.'})
        except UserTable.DoesNotExist:
            return JsonResponse({'message': 'Record not found.'}, status=404)
    return JsonResponse({'message': 'Invalid request method.'}, status=400)

def myregister(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirmpassword')
            if password == confirm_password:
                form.instance.password = make_password(password)
                form.instance.confirmpassword = make_password(confirm_password)
                form.save()
                user = UserProfile.objects.get(email=form.cleaned_data.get('email'))
                user.registerlatitude = request.POST['Latitude']
                user.registerlongitude = request.POST['Longitude']
                #request.session.get('ip',0)
                messages.success(request,"New User Created. Please Confirm Your Mail to login")
                subject = "Welcome to CIS - Criminal Investication System"
                message = "Hello "+ user.name + "!! \n" + "Welcome to CIS! \n Thank you for Visiting\n We have also sent you an confirmation email. please confirm your email address to active your account\n\n Thank You\n CIS High Commesion"
                from_email = settings.EMAIL_HOST_USER
                to_list = [user.email]
                send_mail(subject, message, from_email, to_list, fail_silently=True)

                current_site = get_current_site(request)
                emailsubject = "Confirmation Email from CIS"
                emailmessage = render_to_string("email_confirmation.html",{
                    'name': user.name,
                    'domain' : current_site.domain,
                    'uid' : urlsafe_base64_encode(force_bytes(user.name)),
                    'token' : generate_token.make_token(user),
                })
                emailss = EmailMessage(
                    emailsubject,
                    emailmessage,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                emailss.fail_silently = True
                emailss.send()
                user.save()
                return render(request, "my_signup.html")
        else:
            messages.error(request, form.errors)
            print(form.errors)
            print(form.non_field_errors)
        
    return render(request, "my_signup.html")


def activatefunction(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        newuser = UserProfile.objects.get(name=uid)
    except (TypeError, ValueError,OverflowError,UserProfile.DoesNotExist):
        newuser = None

    if newuser is not None and generate_token.check_token(newuser,token):
        messages.success(request,"Registration Successful")
        newuser.varified = True
        login(request,newuser)
        return redirect('LOGIN')
    else:
        return render(request, 'activation_failed.html')
    

def mylogin(request):
    if request.method == 'POST':
        email = request.POST.get('Email')
        password = request.POST.get('PassCode')

        try:
            user = UserProfile.objects.get(email=email)
            user_type = 'user'
        except UserProfile.DoesNotExist:
            try:
                user = AdminProfile.objects.get(email=email)
                user_type = 'admin'
            except AdminProfile.DoesNotExist:
                user = None
                user_type = None

        if user is not None and check_password(password, user.password):
            if user.varified == True:
                ID = user.id
                login(request, user)
                if user_type == 'user':
                    return redirect(reverse('UserHomePage', args=[ID]))
                elif user_type == 'admin':
                    return redirect(reverse('AdminHomePage', args=[ID]))
            else:
                messages.error(request, 'Email not verified yet')
        else:
            messages.error(request, 'Invalid login credentials')
    
    return render(request, 'my_signin.html')


def UserHomePage(request,user_id):
    userinfo = get_object_or_404(UserProfile, id=user_id)
    login(request, userinfo)
    return render(request, 'userHomePage.html', {'user': userinfo})

def AdminHomePage(request,user_id):
    userinfo = get_object_or_404(AdminProfile, id=user_id)
    login(request, userinfo)
    return  render(request, 'policedashboard.html', {'user': userinfo})



def fetch_victim_data(request):
    user_id = request.GET.get('user_id')
    user_profile = get_object_or_404(victimInfo, id=user_id)
    if user_profile:
        data = {
            'email': user_profile.email,
            'fathername' : user_profile.fathername,
            'mobile': user_profile.phone,
            'victimName': user_profile.name,
            'ssn': user_profile.nid,
            'age': user_profile.age,
            'division': user_profile.division,
            'district': user_profile.district,
            'upazila': user_profile.upazila,
            'img': user_profile.profile_image.url,
        }
    else:
        data = {
            'message': 'User not found',
        }

    return JsonResponse(data)


def upload_victim_record(request):
    if request.method == 'POST':
        # Get data from the request
        name = request.POST.get('name')
        fathername = request.POST.get('fathername')
        phone = request.POST.get('phone')
        nid = request.POST.get('nid')
        email = request.POST.get('email')
        age = request.POST.get('age')
        division = request.POST.get('division')
        district = request.POST.get('district')
        upazila = request.POST.get('upazila')
        uploader_id = request.POST.get('uploader_id')
        victimImage = request.FILES.get('victimImage')
        print(f"Image: {victimImage}")
        # Print all these values
        print(f"Name: {name}")
        print(f"Father Name: {fathername}")
        print(f"Phone: {phone}")
        print(f"NID: {nid}")
        print(f"Email: {email}")
        print(f"Age: {age}")
        print(f"Division: {division}")
        print(f"District: {district}")
        print(f"Upazila: {upazila}")
        print(f"Uploader ID: {uploader_id}")

        # Process the data (for demonstration, just returning the received data)
        data = {
            'name': name,
            'fathername': fathername,
            'phone': phone,
            'nid': nid,
            'email': email,
            'age': age,
            'division': division,
            'district': district,
            'upazila': upazila,
            'uploader_id': uploader_id,
            'victimImage': victimImage,
        }

        return JsonResponse(data)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)


def fetch_user_data(request):
    user_id = request.GET.get('user_id')
    user_profile = get_object_or_404(UserProfile, id=user_id)
    if user_profile:
        data = {
            'email': user_profile.email,
            'mobile': user_profile.phone,
            'victimName': user_profile.name,
            'ssn': user_profile.nid,
            'age': user_profile.calculate_age(),
            'division': user_profile.division,
            'district': user_profile.district,
            'upazila': user_profile.upazila,
            'img': user_profile.profile_image.url,
        }
    else:
        data = {
            'message': 'User not found',
        }

    return JsonResponse(data)

def complain1(request,user_id):
    if request.method == 'POST':
        # Get data from the request
        user_type = request.POST.get('userType')
        user_id = request.POST.get('hiddenUser')
        victim_name = request.POST.get('victimName')
        father_name = request.POST.get('Fathername')
        nid = request.POST.get('ssn')
        age = request.POST.get('age')
        division = request.POST.get('division')
        district = request.POST.get('district')
        upazila = request.POST.get('upazila')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        # Handle file upload
        victim_image = request.FILES.get('victimImage')
        # name = request.POST.get('name')
        # fathername = request.POST.get('fathername')
        # phone = request.POST.get('phone')
        # nid = request.POST.get('nid')
        # email = request.POST.get('email')
        # age = request.POST.get('age')
        # division = request.POST.get('division')
        # district = request.POST.get('district')
        # upazila = request.POST.get('upazila')
        # uploader_id = request.POST.get('uploader_id')
        # victimImage = request.FILES.get('victimImage')
        print(f"Image: {victim_image}")
        # Print all these values
        print(f"Name: {victim_name}")
        print(f"Father Name: {father_name}")
        print(f"Phone: {mobile}")
        print(f"NID: {nid}")
        print(f"Email: {email}")
        print(f"Age: {age}")
        print(f"Division: {division}")
        print(f"District: {district}")
        print(f"Upazila: {upazila}")
        print(f"Uploader ID: {user_id}")
    userinfo = get_object_or_404(UserProfile, id=user_id)    
    return  render(request, 'page1Fir.html', {'user': userinfo})


def saveComplain_1(request,user_id):
    if request.method == 'POST':
        userinfo = get_object_or_404(UserProfile, id=user_id)
        print(request.POST.get('victimImage'))
        if(request.FILES.get('victimImage') == None):
            user_info = get_object_or_404(UserProfile, id=user_id)
            victim_image = user_info.profile_image
            district = user_info.district
            upazila = user_info.upazila
        else:
            victim_image = new_filepath(request.FILES.get('victimImage'))
            district = request.POST.get('district')
            upazila = request.POST.get('upazila')

        victim_name = request.POST.get('victimName')
        father_name = request.POST.get('fathername')
        ssn = request.POST.get('ssn')
        age = request.POST.get('age')
        division = request.POST.get('division')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        victim_profile = victimInfo(profile_image=victim_image,name=victim_name,fathername=father_name,nid=ssn,age=age, division=division, district=district, upazila=upazila,email=email,phone=mobile)
        victim_profile.save()
        FIR_object = CASE_FIR.objects.create(victim_name=victim_profile,case_uploader =  userinfo)
        FIR_ID = FIR_object.id
        FIR_object.save()
        return JsonResponse({
            'FIR_ID': FIR_ID,
        })

def complain2(request,user_id):
    if request.method == 'POST':
        return  render(request, 'page1Fir.html', {'user': userinfo})
    userinfo = get_object_or_404(UserProfile, id=user_id)
    relations = Relation.objects.all()
    return  render(request, 'page2Fir.html', {'user': userinfo ,  'relations': relations})

def complain3(request,user_id):
    if request.method == 'POST':
        return  render(request, 'page1Fir.html', {'user': userinfo})        
    userinfo = get_object_or_404(UserProfile, id=user_id)
    return  render(request, 'page3Fir.html', {'user': userinfo})

def complain4(request,user_id):
    if request.method == 'POST':
        return  render(request, 'page1Fir.html', {'user': userinfo})
    userinfo = get_object_or_404(UserProfile, id=user_id)
    return  render(request, 'page4Fir.html',{'user': userinfo})

def new_filepath(filename):
    old_filename = filename
    timeNow = datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
    filename = "%s%s" % (timeNow,old_filename)
    return os.path.join('uploads/',filename)

def ArrestPage(request):
        return  render(request, 'NewArrest.html')

def applyCISLoader(request):
    if request.method == 'POST':
        leftFacedImageURL = new_filepath(request.FILES.get('leftFacedImage')) 
        FrontFacedImageURL = new_filepath( request.FILES.get('FrontFacedImage'))
        RightFacedImageURL = new_filepath(request.FILES.get('RightFacedImage')) 

        print(FrontFacedImageURL)
        #model export

        new_gender = "Black"
        new_hairColor = "Black"
        new_skinTone= "Black"
        new_hairStyle= "Black"
        new_hairLength= "Black"
        new_eyeColor= "Black"
        new_faceShape = "Black"

        # Return the updated values in the JSON response
        return JsonResponse({
            'gender': new_gender,
            'hairColor': new_hairColor,
            'skinTone' :new_skinTone,
            'hairStyle' :new_hairStyle,
            'hairLength' :new_hairLength,
            'eyeColor' :new_eyeColor,
            'faceShape' :new_faceShape,
        })
    return JsonResponse({'message': 'Invalid request method'}, status=400)
        #form = FirForm(request.POST, request.FILES)
        #print(form.cleaned_data.get('criminal_id'))

def allCriminalPage(request):
        return  render(request, 'All_Criminal_Records.html')
    