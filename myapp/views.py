from django.shortcuts import render, get_object_or_404, redirect
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
from .models import UserTable, UserProfile, MapMarker, AdminProfile, victimInfo, CASE_FIR, Relation,witnessInfo,Crimetype,PhysicalStructure,UserNotificationPanel
from django.http import JsonResponse
from .forms import RegistrationForm
from .tokens import generate_token
from django.urls import reverse
from django.views.generic import TemplateView
import datetime
from django.template.defaultfilters import time
import os
from django.db.models import Q
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from xhtml2pdf import pisa
from .forms import FilterForm
import io
from datetime import datetime



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
    #write here
    try:
        case_records = CASE_FIR.objects.filter(case_uploader=userinfo)
    except:
        case_records = None
    try:
        noti_records = UserNotificationPanel.objects.filter(for_user=userinfo)
    except:
        noti_records = None

    return render(request, 'userHomePage.html', {'user': userinfo, 'case_records': case_records, 'noti_records':noti_records})

def AdminHomePage(request,user_id):
    userinfo = get_object_or_404(AdminProfile, id=user_id)
    try:
        case_records = CASE_FIR.objects.filter(
            Q(occuranced_division__iexact=userinfo.Allocated_Thana) |
            Q(occuranced_district__iexact=userinfo.Allocated_Thana) |
            Q(occuranced_upazila__iexact=userinfo.Allocated_Thana)
        )
    except CASE_FIR.DoesNotExist:
        case_records = None
    login(request, userinfo)
    return  render(request, 'policedashboard.html', {'user': userinfo,'case_records':case_records})


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
            'userName': user_profile.name,
            'ssn': user_profile.nid,
            'age': user_profile.calculate_age(),
            'division': user_profile.division,
            'district': user_profile.district,
            'upazila': user_profile.upazila,
            'img': user_profile.profile_image.url,
            'user_victim_id': user_profile.victim_id,
        }
    else:
        data = {
            'message': 'User not found',
        }

    return JsonResponse(data)
    

def complain1(request,user_id,FIR_id):
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
            existUserId = request.POST.get('User')
            existVictimId = request.POST.get('VICTIMID')
            victim_image = request.FILES.get('victimImage')
            
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                user_id = None  # Set to None if the conversion is not possible

            try:
                existUserId = int(existUserId)
            except (ValueError, TypeError):
                existUserId = None  # Set to None if the conversion is not possible

            try:
                existVictimId = int(existVictimId)
            except (ValueError, TypeError):
                existVictimId = None  # Set to None if the conversion is not possible
            
            uploader_userinfo = get_object_or_404(UserProfile, id=user_id)

            if FIR_id == 0:    
                if existVictimId:
                    exist_victim_obj = get_object_or_404(victimInfo, id=existVictimId)
                    FIR_object = CASE_FIR.objects.create(case_uploader =  uploader_userinfo)  
                    FIR_object.victim_name = exist_victim_obj
                    FIR_object.save()
                else:
                    if existUserId:
                        exist_userinfo = get_object_or_404(UserProfile, id=existUserId) 
                        exist_division = exist_userinfo.division
                        exist_district = exist_userinfo.district
                        exist_upazila = exist_userinfo.upazila
                        exist_victim_image = exist_userinfo.profile_image
                        user_victim_obj = victimInfo.objects.create(
                            name=victim_name,
                            fathername=father_name,
                            phone=mobile,
                            nid=nid,
                            email=email,
                            age=age,
                            division=exist_division,
                            district=exist_district,
                            upazila=exist_upazila,
                            profile_image=exist_victim_image,
                        )
                        FIR_object = CASE_FIR.objects.create(case_uploader =  uploader_userinfo)
                        FIR_object.victim_name = user_victim_obj
                        FIR_object.save()
                        if user_type == "selfCheckbox":
                            uploader_userinfo.victim_id = user_victim_obj
                    else:
                        new_victim_obj = victimInfo.objects.create(
                            name=victim_name,
                            fathername=father_name,
                            phone=mobile,
                            nid=nid,
                            email=email,
                            age=age,
                            division=division,
                            district=district,
                            upazila=upazila,
                            profile_image=victim_image,
                        )
                        FIR_object = CASE_FIR.objects.create(case_uploader =  uploader_userinfo)
                        FIR_object.victim_name = new_victim_obj
                        FIR_object.save()
      
                FIR_ID = FIR_object.id
                return redirect(reverse('UseComplainPage2', args=[user_id,FIR_ID]))
            else:
                old_Case_details = get_object_or_404(CASE_FIR, id=FIR_id)
                old_victimInfo = old_Case_details.victim_name

                old_victimInfo.name=victim_name
                old_victimInfo.fathername=father_name
                old_victimInfo.phone=mobile
                old_victimInfo.nid=nid
                old_victimInfo.email=email
                old_victimInfo.age=age
                if division:
                    old_victimInfo.division=division
                if district:
                    old_victimInfo.district=district
                if upazila:
                    old_victimInfo.upazila=upazila
                if victim_image:
                    old_victimInfo.profile_image=victim_image
                old_victimInfo.save()  
                return redirect(reverse('UseComplainPage2', args=[user_id,FIR_id]))     
    if FIR_id!=0:
        Case_details = get_object_or_404(CASE_FIR, id=FIR_id)
        victimInfoss = Case_details.victim_name
    else:
        Case_details = None
        victimInfoss=None
    #print(victimInfo.name)
    userinfo = get_object_or_404(UserProfile, id=user_id)    
    return  render(request, 'page1Fir.html', {'user': userinfo, 'victim':victimInfoss})


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

def complain2(request,user_id,FIR_id):
    if request.method == 'POST':
        print("Hello")
    userinfo = get_object_or_404(UserProfile, id=user_id)
    relations = Relation.objects.all()
    witness_info_list = witnessInfo.objects.filter(fir_id=FIR_id)
    print(witness_info_list)
    return  render(request, 'page2Fir.html', {'user': userinfo ,'FIR_ID':FIR_id,  'relations': relations , 'witness_info_list':witness_info_list})

def upload_witeness_record(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        User = request.POST.get('User')
        try:
            User = int(User)
        except (ValueError, TypeError):
                User = None  # Set to None if the conversion is not possible
        if User is not None:
            User_obj = get_object_or_404(UserProfile, id=User)
        else:
            User_obj = None
        relation = request.POST.get('Relation')
        relation_obj = get_object_or_404(Relation, typeOfRelations=relation)
        ssn = request.POST.get('ssn')
        mobile = request.POST.get('mobile')
        FIR_ID = request.POST.get('FIR_ID')
        FIR_obj = get_object_or_404(CASE_FIR, id=FIR_ID)
        Brief = request.POST.get('Brief')

        user_witness_obj = witnessInfo.objects.create(
            name=name,
            relationWithVictim=relation_obj,
            phone=mobile,
            nid=ssn,
            fir_id=FIR_obj,
            user_id=User_obj,
            brief=Brief,
        )
        data2 = {
            'name': name,
        }
        print(name)
        return JsonResponse(data2)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)

def complain3(request,user_id,FIR_id):
    if request.method == 'POST':
        crime_type = request.POST.get('crime_type')
        Case_type_obj = get_object_or_404(Crimetype, crime_name=crime_type)
        date= request.POST.get('date')
        timess= request.POST.get('time')
        division= request.POST.get('division')
        district= request.POST.get('district')
        upazila= request.POST.get('upazila')
        brief= request.POST.get('brief')
        brief_metal= request.POST.get('brief_metal')
        Case_details_new = get_object_or_404(CASE_FIR, id=FIR_id)
        Case_details_new.crime_type =Case_type_obj
        Case_details_new.occurance_date=date
        if timess:
            Case_details_new.occurance_time=timess
        if division:
            Case_details_new.occuranced_division=division
        if district:  
            Case_details_new.occuranced_district=district
        if upazila:         
            Case_details_new.occuranced_upazila=upazila
        Case_details_new.brief=brief
        Case_details_new.brief_material=brief_metal
        Case_details_new.save()
        return redirect(reverse('UseComplainPage4', args=[user_id,FIR_id]))        
    if FIR_id!=0:
        Case_details = get_object_or_404(CASE_FIR, id=FIR_id)
    else:
        Case_details = None       
    userinfo = get_object_or_404(UserProfile, id=user_id)
    Crime_Types = Crimetype.objects.all()
    return  render(request, 'page3Fir.html', {'user': userinfo , 'FIR_id':FIR_id,'Case_details':Case_details, 'Crime_Types':Crime_Types})

def generate_pdf_data(name, age, weight, height, gender, facial_hair, face_shape,
                      hair_style, hair_length, color, skin_tone, selected_value, text_value):
    template_path = 'pdfView.html'  # Replace with the path to your HTML template
    context = {
        'name': name,
        'age': age,
        'weight': weight,
        'height': height,
        'gender': gender,
        'facial_hair': facial_hair,
        'face_shape': face_shape,
        'hair_style': hair_style,
        'hair_length': hair_length,
        'color': color,
        'skin_tone': skin_tone,
        'selected_value': selected_value,
        'text_value': text_value,
    }

    template = get_template(template_path)
    html = template.render(context)

    response_data = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), response_data)

    if not pdf.err:
        return response_data.getvalue()
    return HttpResponse('Error during PDF generation: {}'.format(pdf.err), status=500)

def complain4(request,user_id,FIR_id):
    if request.method == 'POST':
        name = request.POST.get('susName1')
        age = request.POST.get('susage1')
        weight = request.POST.get('susweight1')
        height = request.POST.get('susheight1')
        gender = request.POST.get('hiddenGender1')
        facial_hair = request.POST.get('hiddenfacialHai1r')
        face_shape = request.POST.get('hiddenfaceShape1')
        hair_style = request.POST.get('hiddenhairStyle1')
        hair_length = request.POST.get('hiddenhairlength1')
        color = request.POST.get('hiddencolor1')
        skin_tone = request.POST.get('skinToneofoffender1')
        selectedValue = request.POST.get('Type_of_distinguishing_marks1')
        textValue = request.POST.get('Description_distinguishing_marks1')
        Case_obj = get_object_or_404(CASE_FIR, id=FIR_id)
        physical_structure_instance = PhysicalStructure.objects.create(
            name=name,
            gender=gender,
            hairColor=color,  # Assuming color corresponds to hair color
            skinTone=skin_tone,
            hairStyle=hair_style,
            hairLength=hair_length,
            facialHair=facial_hair,
            faceShape=face_shape,
            age=age,
            height=height,
            weight=weight,
            fir_id=Case_obj,
            dis_guis_mark =selectedValue,
            dis_guis_mark_brief =textValue,
        )        
        pdf_data = generate_pdf_data(name, age, weight, height, gender, facial_hair, face_shape,hair_style, hair_length, color, skin_tone, selectedValue, textValue)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="complaint_form.pdf"'

        response.write(pdf_data)

        noti_user = get_object_or_404(UserProfile, id=user_id)

        noti_obj = UserNotificationPanel.objects.create(
            for_user = noti_user,
            Title = "New Fir Submitted",
            noti_image = Case_obj.victim_name.profile_image,
        )  


        return response
        #return redirect(reverse('UserHomePage', args=[user_id]))  
        #write code to generate a pdf containg the information (here) of the form and then view the pdf in another window 
        #return redirect(reverse('UserHomePage', args=[user_id]))    
    userinfo = get_object_or_404(UserProfile, id=user_id)
    return  render(request, 'page4Fir.html',{'user': userinfo, 'FIR_id':FIR_id})

def pdf_view(request):
    return  render(request, 'pdfView.html')

def upload_offender_record(request):
    if request.method == 'POST':
        # Get data from the request Fir_id
        name = request.POST.get('susName')
        Fir_id = request.POST.get('Fir_id')
        Case_obj = get_object_or_404(CASE_FIR, id=Fir_id)
        age = request.POST.get('susage')
        weight = request.POST.get('susweight')
        height = request.POST.get('susheight')
        gender = request.POST.get('hiddenGender')
        facial_hair = request.POST.get('hiddenfacialHair')
        face_shape = request.POST.get('hiddenfaceShape')
        hair_style = request.POST.get('hiddenhairStyle')
        hair_length = request.POST.get('hiddenhairlength')
        color = request.POST.get('hiddencolor')
        skin_tone = request.POST.get('skinToneofoffender')
        selectedValue = request.POST.get('selectedValue')
        textValue = request.POST.get('textValue')

        # Print the received data (for demonstration)
        physical_structure_instance = PhysicalStructure.objects.create(
            name=name,
            gender=gender,
            hairColor=color,  # Assuming color corresponds to hair color
            skinTone=skin_tone,
            hairStyle=hair_style,
            hairLength=hair_length,
            facialHair=facial_hair,
            faceShape=face_shape,
            age=age,
            height=height,
            weight=weight,
            fir_id=Case_obj,
            dis_guis_mark =selectedValue,
            dis_guis_mark_brief =textValue,
        )
        data = {
            'name': name,
        }

        return JsonResponse(data)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)

def new_filepath(filename):
    old_filename = filename
    timeNow = datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
    filename = "%s%s" % (timeNow,old_filename)
    return os.path.join('uploads/',filename)

def ArrestPage(request,admin_id):
        admin = AdminProfile.objects.get(id=admin_id)
        return  render(request, 'NewArrest.html',{'user': admin })

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

def allCriminalPage(request,admin_id):
        admin = AdminProfile.objects.get(id=admin_id)
        return  render(request, 'All_Criminal_Records.html',{'user': admin })

def goto_search_page(request,user_id):
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            selected_fields = [field for field, value in form.cleaned_data.items() if value]
            text = request.POST.get('searchTerms')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            occ_from_date =  request.POST.get('occ_from_date')
            occ_to_date = request.POST.get('occ_to_date')

            statusofCase = request.POST.get('statusofCase')
            print(from_date)
            print(to_date)
            user_profile = get_object_or_404(UserProfile, id=user_id)
            found_by_uploader_case_records = CASE_FIR.objects.filter(case_uploader=user_profile)
            if 'firnumber' in selected_fields:
                integer = int(text)
                temp = found_by_uploader_case_records.filter(id = integer)
                found_by_uploader_case_records = temp
            if 'victim_name' in selected_fields:
                temporary = victimInfo.objects.filter(name__icontains=text)
                index = 0
                temp = found_by_uploader_case_records.filter(victim_name = temporary[index])
                index += 1
                while index < len(temporary):
                    temp = temp | found_by_uploader_case_records.filter(victim_name = temporary[index])
                    index += 1
                found_by_uploader_case_records = temp
            if 'submissiondate' in selected_fields:
                temp = found_by_uploader_case_records.filter(file_report_date__range=(from_date, to_date))
                found_by_uploader_case_records = temp
            if 'occurance_date' in selected_fields:
                temp = found_by_uploader_case_records.filter(occurance_date__range=(occ_from_date, occ_to_date))
                found_by_uploader_case_records = temp
            if 'crimeType' in selected_fields:
                crime_type = Crimetype.objects.filter(crime_name__icontains=text)
                temp = found_by_uploader_case_records.filter(crime_type = crime_type)
                found_by_uploader_case_records = temp
            if 'status' in selected_fields:
                temp = found_by_uploader_case_records.filter(case_status = statusofCase)
                found_by_uploader_case_records = temp
            userinfo = get_object_or_404(UserProfile, id=user_id)
            form = FilterForm()
            return render(request, 'search_page_user.html', {'user': userinfo , 'form': form,'results':found_by_uploader_case_records})
    userinfo = get_object_or_404(UserProfile, id=user_id)
    form = FilterForm()
    return render(request, 'search_page_user.html', {'user': userinfo , 'form': form})
    
def searchbar_from_advance_search(request):
    search_term = request.GET.get('search_term')
    user_id = request.GET.get('user_id')
    user_profile = get_object_or_404(UserProfile, id=user_id)
    found_by_uploader_case_records = CASE_FIR.objects.filter(case_uploader=user_profile)
    integer = int(search_term)
    print(integer)
    temp = found_by_uploader_case_records.filter(id = integer)
    found_by_uploader_case_records = temp
    data = []
    for case in found_by_uploader_case_records:
        data.append({
            'id': case.id,
            'name': case.victim_name.name,
            'email': case.victim_name.email,
            'crime_type': case.crime_type,
            'case_status': case.case_status,
            'file_report_date': case.file_report_date.strftime('%Y-%m-%d'),
        })
    print(found_by_uploader_case_records)
    form = FilterForm()
    return render(request, 'search_page_user.html', {'user': user_profile , 'form': form,'results':found_by_uploader_case_records})