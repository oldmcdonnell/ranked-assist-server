from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, FriendsGroup, Vote, Candidate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'

class CandidateSerializer(serializers.ModelSerializer):
    profile = serializers.StringRelatedField()
    vote = serializers.StringRelatedField()

    class Meta:
        model = Candidate
        fields = '__all__'

class NestedProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

class FriendsGroupSerializer(serializers.ModelSerializer):
    members = NestedProfileSerializer(many=True, read_only=True)

    class Meta:
        model = FriendsGroup
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    votes = serializers.SerializerMethodField()
    friends = NestedProfileSerializer(source='friends_group.members', many=True, read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

    def get_votes(self, obj):
        votes = Vote.objects.filter(candidates__profile=obj)
        return VoteSerializer(votes, many=True).data
