from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import *
from .serializers import *


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    print("user************************ ", user)
    profile = get_object_or_404(Profile, user=user)
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    user = User.objects.create(
        username=request.data['username']
    )
    user.set_password(request.data['password'])
    user.save()
    profile = Profile.objects.create(
        user=user,
        first_name=request.data['first_name'],
        last_name=request.data['last_name'],
        email=request.data['email'],
    )
    profile.save()
    profile_serialized = ProfileSerializer(profile)
    return Response(profile_serialized.data)

@api_view(['POST']) 
@permission_classes([IsAuthenticated])
def create_friend_group(request):
    friend_group = FriendsGroup.objects.create(
        note=request.data.get('note', '')
    )
    friend_group.save()
    serializer = FriendsGroupSerializer(friend_group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_profile_to_group(request, group_id):
    group = get_object_or_404(FriendsGroup, id=group_id)
    profile = get_object_or_404(Profile, user=request.user)
    group.members.add(profile)
    group.save()
    return Response({'status': 'profile added to group'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friend_groups(request):
    groups = FriendsGroup.objects.all()
    serializer = FriendsGroupSerializer(groups, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vote(request):
    vote = Vote.objects.create(
        rounds=request.data.get('rounds', 1)
    )
    vote.save()
    serializer = VoteSerializer(vote)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_candidates(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    candidates = Candidate.objects.filter(vote=vote)
    serializer = CandidateSerializer(candidates, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_candidate_to_vote(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    profile = get_object_or_404(Profile, id=request.data['profile_id'])
    candidate = Candidate.objects.create(
        profile=profile,
        vote=vote,
        description=request.data.get('description', '')
    )
    candidate.save()
    serializer = CandidateSerializer(candidate)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)