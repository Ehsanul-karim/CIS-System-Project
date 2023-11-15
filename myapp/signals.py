from django.contrib.auth.signals import user_logged_in
from .models import UserTable, UserProfile,AdminProfile
from django.dispatch import receiver
from ip2geotools.databases.noncommercial import DbIpCity
from ipware import get_client_ip

ip = None
adminip = None

@receiver(user_logged_in, sender=UserProfile)
def login_success(sender, request, user, **kwargs):
    global ip
    ip = request.META.get('REMOTE_ADDR')
    print("CLIENT IP: ",ip)
    #request.session['ip'] = ip
    if user.registerIP is None:
        user.registerIP = ip
        print("Unable ")
        ipp, is_routable = get_client_ip(request)
        if ipp is None:
            print("Unable to find CLIENT IP ")
        else:
            if is_routable:
                 print("CLIENT IP PUBLIC :",ipp)
            else:
                print("CLIENT IP PRIVATE :",ipp)
        response = DbIpCity.get(ipp,api_key='free')
        if response.country and response.city:
            country = response.country + " | " + response.city
        elif response.country:
            country = response.country
        elif response.city:
            country = response.city
        else:
            country = "Unknown"
        if country == "ZZ":
            country = "Private Client Ip. unable to rounting"
        user.registerLocation = country
        user.save()
    else:
        user.loginIP = ip
        print("Unable 2")
        ipp, is_routable = get_client_ip(request)     
        response = DbIpCity.get(ipp,api_key='free')
        if response.country and response.city:
            country = response.country + " | " + response.city
        elif response.country:
            country = response.country
        elif response.city:
            country = response.city
        else:
            country = "Unknown"
        if country == "ZZ":
            country = "Private Client Ip. unable to rounting"
        user.loginLocation = country
        user.save()
        

@receiver(user_logged_in, sender=AdminProfile)
def login_successes(sender, request, user, **kwargs):
        global adminip
        ip = request.META.get('REMOTE_ADDR')
        print("CLIENT IP: ",adminip)
        user.loginIP = adminip
        ipp, is_routable = get_client_ip(request)     
        response = DbIpCity.get(ipp,api_key='free')
        if response.country and response.city:
            country = response.country + " | " + response.city
        elif response.country:
            country = response.country
        elif response.city:
            country = response.city
        else:
            country = "Unknown"
        if country == "ZZ":
            country = "Private Client Ip. unable to rounting"
        user.loginLocation = country
        user.save()
