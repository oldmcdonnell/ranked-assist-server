from django.contrib import admin
from app_ranked.models import *


class ProfileAdmin(admin.ModelAdmin):
  pass

class FriendsGroupAdmin(admin.ModelAdmin):
  pass


admin.site.register(Profile, ProfileAdmin)
admin.site.register(FriendsGroup, FriendsGroupAdmin)
