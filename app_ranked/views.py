from collections import defaultdict
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
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


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
    required_fields = ['username', 'password', 'first_name', 'last_name', 'email']
    
    for field in required_fields:
        if field not in request.data:
            return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.create(
            username=request.data['username'],
            email=request.data['email'],
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
        )
        user.set_password(request.data['password'])
        user.save()

        profile = Profile.objects.create(
            user=user,
        )
        profile.save()

        profile_serialized = ProfileSerializer(profile)
        return Response(profile_serialized.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST']) 
@permission_classes([IsAuthenticated])
def create_friend_group(request):
    friend_group = FriendsGroup.objects.create(
        title=request.data.get('title'),
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_groups(request):
    profile = request.user.profile
    groups = FriendsGroup.objects.filter(members=profile)
    serializer = FriendsGroupSerializer(groups, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vote(request):
    title = request.data.get('title')
    details = request.data.get('details')
    friends_group = FriendsGroup.objects.get(id=request.data['friends_group'])
    author = request.user
    vote = Vote.objects.create(
        title=title,
        details=details,
        friends_group=friends_group,
        author=author,
    )
    serializer = VoteSerializer(vote)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vote_results(request):
    vote = get_object_or_404(Vote, id=request.data['vote_id'])
    candidates = Candidate.objects.filter(vote=vote)
    
    # Initial vote count
    vote_count = defaultdict(int)
    for candidate in candidates:
        vote_count[candidate.id] = candidate.votes

    total_votes = sum(vote_count.values())
    majority_threshold = total_votes / 2

    # Round-based elimination
    round_number = 1
    while True:
        print(f"Round {round_number} processing...")
        
        # Check if any candidate has more than 50% of the votes
        for candidate_id, count in vote_count.items():
            if count > majority_threshold:
                winner = Candidate.objects.get(id=candidate_id)
                return Response({'winner': winner.description, 'round': round_number, 'votes': count})
        
        # Find the candidate with the least votes
        min_votes = min(vote_count.values())
        eliminated_candidates = [candidate_id for candidate_id, count in vote_count.items() if count == min_votes]
        
        # If all candidates have the same votes, it's a tie
        if len(eliminated_candidates) == len(candidates):
            return Response({'result': 'tie', 'round': round_number})
        
        # Eliminate the candidate with the least votes and redistribute their votes
        for candidate_id in eliminated_candidates:
            eliminated_candidate = Candidate.objects.get(id=candidate_id)
            redistributed_votes = vote_count[candidate_id]
            
            # Redistribute votes to the remaining candidates based on the next preferences
            for voter in eliminated_candidate.voters.all():
                next_choice = get_next_choice(voter, eliminated_candidates)
                if next_choice:
                    vote_count[next_choice] += 1
            
            # Remove the eliminated candidate from the count
            del vote_count[candidate_id]
        
        round_number += 1

def get_next_choice(voter, eliminated_candidates):
    preferences = voter.preferences.order_by('rank')
    for preference in preferences:
        if preference.candidate.id not in eliminated_candidates:
            return preference.candidate.id
    return None

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def create_candidate(request):
    vote = get_object_or_404(Vote, id=request.data['vote_id'])
    print('vote ID ', request.data['vote_id'])
    if 'candidates' in request.data:
        new_candidates = request.data['candidates']
        updated_candidates = []
        for candidate_data in new_candidates:
            candidate, created = Candidate.objects.update_or_create(
                vote=vote,
                id=candidate_data.get('id'),
                defaults={'description': candidate_data['description']}
            )
            updated_candidates.append(candidate)
        
        serializer = CandidateSerializer(updated_candidates, many=True)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    elif 'vote_id' in request.data and 'description' in request.data:
        candidate = Candidate.objects.create(
            vote=vote,
            description=request.data['description']
        )
        serializer = CandidateSerializer(candidate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Invalid data provided'}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_candidate(request):
#     print('test')
#     vote = get_object_or_404(Vote, id=request.data['vote_id'])
#     print('vote ID ', request.data['vote_id'])
#     description = request.data['description']
#     new_candidate = Candidate.objects.create(
#         vote = vote,
#         description = description,
#     )
#     serializers = CandidateSerializer(data = new_candidate)
#     if serializers.is_valid():
#         serializers.save()
#         return Response(serializers.data, status=status.HTTP_201_CREATED)
#     else:
#         return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fetch_candidates(request):
    vote_id = request.data.get('vote_id')
    print('*****************************************************', request.data['vote_id'])
    try:
        vote = get_object_or_404(Vote, id=vote_id)
        candidates = Candidate.objects.filter(vote=vote)
        print('**************************************************************', candidates)
        serializers = CandidateSerializer(candidates, many=True)
        return Response(serializers.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_profiles(request):
    profiles = Profile.objects.all()
    serializer = ProfileSerializer(profiles, many=True)
    return Response(serializer.data)


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Vote, Candidate
from .serializers import VoteSerializer, CandidateSerializer



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Vote, Candidate, Preference, Voter
from .serializers import PreferenceSerializer
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_preference(request):
    vote_id = request.data.get('vote_id')
    if not vote_id:
        return Response({'error': 'vote_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    vote = get_object_or_404(Vote, id=vote_id)
    voter, created = Voter.objects.get_or_create(user=request.user, vote=vote)
    
    if 'rank' in request.data:
        rank_data = request.data['rank']
        updated_rank = []
        
        for preference_data in rank_data:
            print('*************************preference data******************', preference_data)
            candidate_id = preference_data.get('candidate_id')
            rank = preference_data.get('rank')
            
            if not candidate_id or not rank:
                return Response({'error': 'candidate_id and rank are required for each preference'}, status=status.HTTP_400_BAD_REQUEST)
            
            candidate = get_object_or_404(Candidate, id=candidate_id, vote=vote)
            print('****************various opbjects********', voter, candidate, vote, rank)
            preference, created = Preference.objects.update_or_create(
                voter=voter,
                candidate=candidate,
                vote=vote,
                rank = rank,
            )
            updated_rank.append(preference)
        
        serializer = PreferenceSerializer(updated_rank, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'No rank data provided'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_vote(request):
    vote_id = request.data.get('vote_id')
    vote = get_object_or_404(Vote, id=vote_id)

    candidates_data = request.data.get('candidates', [])
    updated_candidates = []

    for candidate_data in candidates_data:
        candidate_id = candidate_data.get('id')
        candidate = get_object_or_404(Candidate, id=candidate_id)
        candidate.count = candidate_data.get('count', candidate.count)
        candidate.round = candidate_data.get('round', candidate.round)
        candidate.save()
        updated_candidates.append(candidate)

    vote.round = request.data.get('round', vote.round)
    vote.count = request.data.get('count', vote.count)
    vote.save()

    vote_serializer = VoteSerializer(vote)
    candidates_serializer = CandidateSerializer(updated_candidates, many=True)

    response_data = {
        'vote': vote_serializer.data,
        'candidates': candidates_serializer.data
    }

    return Response(response_data, status=status.HTTP_202_ACCEPTED)