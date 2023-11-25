from django.urls import path
from . import views
from .views import MapView

urlpatterns = [
    path('', views.home, name = "HOME"),
    #path('newPage/', views.users, name = "USER"),
    #path('editPage/<int:user_id>/', views.edit, name = "EDIT"),
    #path('delete/<int:user_id>/', views.delete_user, name='DELETE'),
    path('mysignup/', views.myregister, name = "REGISTER"),
    path('mylogin/', views.mylogin, name = "LOGIN"),
    path('userhome/<int:user_id>/', views.UserHomePage, name = "UserHomePage"),
    path('adminhome/<int:user_id>/', views.AdminHomePage, name = "AdminHomePage"),
    path('arrest/<int:admin_id>/', views.ArrestPage, name = "ArrestPage"),
    path('applyCIS/', views.applyCISLoader, name = "applyCISLoad"),
    path('criminalpage/<int:admin_id>', views.allCriminalPage, name = "CriminalPage"),
    path('p1complain/<int:user_id>/<int:FIR_id>', views.complain1, name = "UseComplainPage1"),
    path('p2complain/<int:user_id>/<int:FIR_id>', views.complain2, name = "UseComplainPage2"),
    path('p3complain/<int:user_id>/<int:FIR_id>', views.complain3, name = "UseComplainPage3"),
    path('p4complain/<int:user_id>/<int:FIR_id>', views.complain4, name = "UseComplainPage4"),
    path('saveContents/<int:user_id>/', views.saveComplain_1, name = "SAVE1"),
    path('search_req_user/<int:user_id>/', views.goto_search_page, name = "Search_Page"),
    path('activate/<uidb64>/<token>',views.activatefunction, name="ACTIVATE"),
    path('fetch_user_data/',views.fetch_user_data, name="fetch_user_data"),
    path('fetch_victim_data/',views.fetch_victim_data, name="fetch_victim_data"),
    path('Upload_Victim_Record/',views.upload_victim_record, name="upload_victim_record"),
    path('Upload_WITHNESS_Record/',views.upload_witeness_record, name="upload_witeness_record"),
    path('Upload_Offender_Record/',views.upload_offender_record, name="upload_offender_record"),
    path('your_complaint_view/',views.pdf_view, name="pdf_view"),
    #path('map/', MapView.as_view(), name='map-view'),

    path('map/', views.context_date, name='map-view'),
    path('get-station/', views.near_stations),
]
