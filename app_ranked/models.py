from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    friends_group = models.ForeignKey('FriendsGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')

    def __str__(self):
        return self.user.username

class FriendsGroup(models.Model):
    members = models.ManyToManyField(Profile, related_name='group')
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Friends Group {self.id} created at {self.created_at}'

class Vote(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    rounds = models.IntegerField(default=0 )
    count = models.IntegerField(default=0)

    def __str__(self):
        return f'Vote created at {self.created_at} with {self.rounds} rounds'

class Candidate(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='candidates')
    votes = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='candidates')
    description = models.TextField()

    def __str__(self):
        return f'Candidate {self.profile.user.username} for Vote {self.vote.id}'
