from django.contrib import admin
from app_ranked.models import *


class ProfileAdmin(admin.ModelAdmin):
  pass

class FriendsGroupAdmin(admin.ModelAdmin):
  pass

class CandidateAdmin(admin.ModelAdmin):
  pass

class VoteAdmin(admin.ModelAdmin):
  pass


class PreferenceGroupAdmin(admin.ModelAdmin):
  pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(FriendsGroup, FriendsGroupAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Preference, PreferenceGroupAdmin)