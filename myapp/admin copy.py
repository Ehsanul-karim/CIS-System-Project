from django.contrib import admin
from .models import UserTable, UserProfile, MapMarker, AdminProfile, DistrictNames,  victimInfo,witnessInfo,Case_related,PhysicalStructure, CASE_FIR,Crimetype,Relation
# Register your models here.

admin.site.register(UserTable)
admin.site.register(UserProfile)
admin.site.register(AdminProfile)
admin.site.register(MapMarker)
admin.site.register(DistrictNames)
admin.site.register(victimInfo)
admin.site.register(witnessInfo)
admin.site.register(Case_related)
admin.site.register(PhysicalStructure)
admin.site.register(CASE_FIR)
admin.site.register(Crimetype)
admin.site.register(Relation)