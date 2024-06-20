from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'

class VoteSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = '__all__'

class NestedProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

class FriendsGroupSerializer(serializers.ModelSerializer):
    members = NestedProfileSerializer(many=True, read_only=True)
    votes = VoteSerializer(many=True, read_only=True)

    class Meta:
        model = FriendsGroup
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    votes = serializers.SerializerMethodField()
    friends_group = FriendsGroupSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

    def get_votes(self, request):
        pass

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = '__all__'