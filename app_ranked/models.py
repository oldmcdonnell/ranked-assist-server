from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    friends_group = models.ForeignKey('FriendsGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')

    def __str__(self):
        return self.user.username

class FriendsGroup(models.Model):
    title = models.CharField(max_length=100, default="Group")
    members = models.ManyToManyField(Profile, related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Group {self.title}'

class Vote(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    round = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    polls_close = models.DateTimeField(blank=True, null=True)
    open_enrollment = models.BooleanField(default=True)
    polls_open = models.BooleanField(default=True)
    friends_group = models.ForeignKey(FriendsGroup, on_delete=models.CASCADE, related_name='votes')

    def __str__(self):
        return f'Vote {self.title} for {self.friends_group.title}'

class Candidate(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='candidates')
    description = models.TextField()
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.description
    
    @property
    def vote_info(self):
        return {
            'vote_round': self.vote.round,
            'vote_count': self.vote.count
        }

class Voter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voter')
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='voters')

    def __str__(self):
        return f'Voter {self.user.username} for {self.vote.title}'

class Preference(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='preferences')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='preferences')
    rank = models.IntegerField()

    class Meta:
        unique_together = ('voter', 'rank')

    def __str__(self):
        return f'{self.voter.user.username} ranks {self.candidate.description} as {self.rank}'
