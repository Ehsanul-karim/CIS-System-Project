from django.db import models
from django.contrib.auth.hashers import make_password
import datetime
from django.core.mail import EmailMessage, send_mail
from demo import settings
from django.utils import timezone
from datetime import date
import os

def filepath(request,filename):
    old_filename = filename
    timeNow = datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
    filename = "%s%s" % (timeNow,old_filename)
    return os.path.join('uploads/',filename)

# Create your models here.


class UserTable(models.Model):
    name = models.CharField(max_length=200)
    age = models.IntegerField(null=True, blank=True)
    status = models.BooleanField(default=True)
    image = models.ImageField(upload_to=filepath, null=True, blank=True)

    def __str__(self):
        return self.name
    
class victimInfo(models.Model):
    name = models.CharField(max_length=255,null=True)
    fathername = models.CharField(max_length=255,null=True)
    phone = models.CharField(max_length=15,null=True)
    nid = models.CharField(max_length=20,null=True)
    email = models.EmailField(null=True)
    age = models.CharField(max_length=20,null=True)
    division = models.CharField(max_length=50,null=True)
    district = models.CharField(max_length=50,null=True)
    upazila = models.CharField(max_length=50,null=True)
    profile_image = models.ImageField(upload_to=filepath, null=True, blank=True)

class UserProfile(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # You should hash passwords
    confirmpassword = models.CharField(max_length=128, null=True)  # You should hash passwords
    nid = models.CharField(max_length=20,unique=True) # Number of
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=15,unique=True)
    division = models.CharField(max_length=50,null=True)
    district = models.CharField(max_length=50,null=True)
    upazila = models.CharField(max_length=50,null=True)
    profile_image = models.ImageField(upload_to=filepath, null=True, blank=True)
    varified = models.BooleanField(default=False, null=True)
    last_login = models.CharField(max_length=1000,null=True)
    registerIP = models.CharField(max_length=1000,null=True)
    registerLocation = models.TextField(default="", null = True)
    loginIP = models.CharField(max_length=1000,null=True)
    loginLocation = models.TextField(default="", null = True)
    registerlatitude = models.FloatField(null=True)
    registerlongitude = models.FloatField(null=True)
    victim_id = models.ForeignKey(
        victimInfo, 
        null=True,
        on_delete=models.SET_NULL,
        blank=True
    )
    def calculate_age(self):
        today = date.today()
        birth_date = self.date_of_birth
        age = today.year - birth_date.year 
        return age
    
    def __str__(self):
        return self.name

class UserNotificationPanel(models.Model):
    for_user = models.ForeignKey(
        UserProfile, 
        null=True,
        on_delete=models.CASCADE,
        blank=True,
    )
    Title = models.CharField(max_length=50,null=True)
    noti_image = models.ImageField(upload_to=filepath, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def time_expiredd(self):
        time_difference = timezone.now() - self.created_at
        days, seconds = divmod(time_difference.seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds Ago"
    
class Crimetype(models.Model):
    crime_name = models.CharField(max_length=50,null=True)
    def __str__(self):
        return self.crime_name

class CASE_FIR(models.Model):
    Status_CHOICES = [
        ('Pending', 'Pending'),
        ('On Going', 'On Going'),
        ('Completed', 'Completed'),
    ]
    case_status = models.CharField(max_length=255,choices=Status_CHOICES,default='Pending')
    victim_name = models.ForeignKey(
        victimInfo, 
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )
    case_uploader = models.ForeignKey(
        UserProfile, 
        null=True,
        on_delete=models.CASCADE,
        blank=True
    )
    crime_type = models.ForeignKey(
        Crimetype, 
        null=True,
        on_delete=models.CASCADE,
        blank=True
    )
    occurance_date = models.DateField(null=True)
    occurance_time = models.TimeField(null=True)
    file_report_date = models.DateField(null=True,default=timezone.now)
    occuranced_division = models.CharField(max_length=50,null=True)
    occuranced_district = models.CharField(max_length=50,null=True)
    occuranced_upazila = models.CharField(max_length=50,null=True)
    brief = models.TextField(null = True)
    brief_material = models.TextField(null = True)


class Case_related(models.Model):
    item = models.FileField(upload_to=filepath, null=True, blank=True)
    for_case = models.ForeignKey(
        CASE_FIR,
        on_delete=models.PROTECT,  # You can choose the appropriate behavior for deletion
        null=True,
    )

class Relation(models.Model):
    typeOfRelations = models.CharField(max_length=25,null=True)
    def __str__(self):
        return self.typeOfRelations

class witnessInfo(models.Model):
    name = models.CharField(max_length=255,null=True)
    relationWithVictim = models.ForeignKey(
        Relation,
        on_delete=models.PROTECT,
        null=True,
    )
    phone = models.CharField(max_length=15,null=True)
    nid = models.CharField(max_length=20,null=True)
    user_id = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    brief = models.TextField(null = True)
    fir_id = models.ForeignKey(
        CASE_FIR, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

class PhysicalStructure(models.Model):

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHERS', 'Others'),
    ]
    HAIR_COLOR_CHOICES = [
        ('BLACK', 'Black'),
        ('BROWN', 'Brown'),
        ('BLONDE', 'Blonde'),
    ]
    HAIR_LENGTH_CHOICES = [
        ('SHORT', 'Short'),
        ('LONG', 'Long'),
        ('MEDIUM', 'Medium'),
    ]
    AGE_CATEGORY_CHOICES = [
        ('MINOR', 'Minor'),
        ('YOUNG', 'Young'),
        ('ADULT', 'Adult'),
        ('AGED', 'Aged'),
    ]
    HAIR_TYPE_CHOICES = [
        ('CURLY', 'Curly'),
        ('STRAIGHT', 'Straight'),
        ('BALD', 'Bald'),
    ]
    SKIN_TONE_CHOICES = [
        ('BROWNY', 'Browny'),
        ('BLACKY', 'Black'),
        ('WHITEY', 'White'),
    ]
    FACE_SHAPE_CHOICES = [
        ('OVAL', 'Oval'),
        ('ROUND', 'Round'),
        ('SQUARE', 'Square'),
        ('HEART', 'Heart'),
        ('OBLONG', 'Oblong'),
    ]
    FACIAL_HAIR_CHOICES = [
        ('BEARD', 'Beard'),
        ('MUSTACHE', 'Mustache'),
        ('SHAVED', 'Shaved'),
    ]
    name = models.CharField(max_length=255,null=True)
    gender = models.CharField(max_length=255,choices=GENDER_CHOICES,null=True)
    hairColor = models.CharField(max_length=255,choices=HAIR_COLOR_CHOICES,null=True)
    skinTone = models.CharField(max_length=255,choices=SKIN_TONE_CHOICES,null=True)
    hairStyle = models.CharField(max_length=255,choices=HAIR_TYPE_CHOICES,null=True)
    hairLength = models.CharField(max_length=255,choices=HAIR_LENGTH_CHOICES,null=True)
    facialHair = models.CharField(max_length=255,choices=FACIAL_HAIR_CHOICES,null=True)
    faceShape = models.CharField(max_length=255,choices=FACE_SHAPE_CHOICES,null=True)
    age = models.CharField(max_length=255,choices=AGE_CATEGORY_CHOICES,null=True)
    height = models.CharField(max_length=255,null=True)  # Adjust the max_digits and decimal_places as needed
    weight = models.CharField(max_length=255,null=True)  # Adjust the max_digits and decimal_places as needed
    fir_id = models.ForeignKey(
        CASE_FIR, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
    )
    dis_guis_mark = models.CharField(max_length=255,null=True)  # Adjust the max_digits and decimal_places as needed
    dis_guis_mark_brief = models.CharField(max_length=255,null=True)


class DistrictNames(models.Model):
    district = models.CharField(max_length=255)

    def __str__(self):
        return self.district

class AdminProfile(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    Allocated_Thana = models.ForeignKey(
        DistrictNames,
        on_delete=models.PROTECT,  # You can choose the appropriate behavior for deletion
        null=True,
    )
    last_login = models.CharField(max_length=1000,null=True)
    loginIP = models.CharField(max_length=1000,null=True)
    loginLocation = models.TextField(default="", null = True)
    varified = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Check if the password has been changed
        if self._state.adding:
            subject = "Welcome to CIS - Criminal Investication System"
            message = "Hello Mr."+ self.name + "!! \n" + "You are an officer of CIS Team! \n" + "Your Password is " + self.password + "\n" + "Please Change your password after login. \n"
            self.password = make_password(self.password)
            from_email = settings.EMAIL_HOST_USER
            to_list = [self.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
        super(AdminProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class MapMarker(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    def __str__(self):
        return self.name
    

