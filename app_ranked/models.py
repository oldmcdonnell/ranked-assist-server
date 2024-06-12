from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    friends_group = models.ForeignKey('FriendsGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')

    def __str__(self):
        return self.user.username

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
    friends_group = models.ForeignKey('FriendsGroup', on_delete=models.CASCADE, related_name='votes')

    def __str__(self):
        return f'Vote {self.title} for {self.friends_group.title}'
    
    # def save(self, *args, **kwargs):
    #     if self.polls_close:
    #         # Make sure polls_close is timezone-aware
    #         if timezone.is_naive(self.polls_close):
    #             self.polls_close = timezone.make_aware(self.polls_close, timezone.get_current_timezone())

    #         # Check if the current time is past the polls_close time
    #         if timezone.now() > self.polls_close:
    #             self.polls_open = False

    #     super().save(*args, **kwargs)

class Candidate(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='candidates')
    description = models.TextField()

    def __str__(self):
        return f'Candidate {self.description} for Vote {self.vote.title}'
    
    @property
    def vote_info(self):
        return {
            'vote_round': self.vote.round,
            'vote_count': self.vote.count
        }

class FriendsGroup(models.Model):
    title = models.CharField(max_length=100, default="Old Profile")
    members = models.ManyToManyField(Profile, related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Group {self.title} created at {self.created_at}'
