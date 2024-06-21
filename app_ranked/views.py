from django.core.mail import send_mail
from collections import defaultdict, Counter
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

        try:
            friends_group = FriendsGroup.objects.get(id=1)
            print('FriendsGroup found:', friends_group)
        except FriendsGroup.DoesNotExist:
            return Response({'error': 'FriendsGroup with id 1 does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        profile = Profile.objects.create(
            user=user
        )
        profile.save()

        friends_group.members.add(profile)
        friends_group.save()

        profile_serialized = ProfileSerializer(profile)
        return Response(profile_serialized.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print('Exception:', str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_friend_group(request):
    user_profile = Profile.objects.get(user=request.user)
    members = request.data.get('members', [])

    friend_group = FriendsGroup.objects.create(
        title=request.data.get('title'),
        note=request.data.get('note', '')
    )
    
    friend_group.members.add(user_profile)
    # Add members to the many-to-many field
    for member_id in members:
        profile = Profile.objects.get(id=member_id)
        friend_group.members.add(profile)
    
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_user_group(request):
    group = FriendsGroup.objects.get(id=1)
    serializers = FriendsGroupSerializer(group)
    return Response(serializers.data)


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
    vote_id = request.data.get('vote_id')
    if not vote_id:
        return Response({'error': 'vote_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    vote = get_object_or_404(Vote, id=vote_id)
    preferences = Preference.objects.filter(candidate__vote=vote).select_related('voter', 'candidate')
    
    if not preferences.exists():
        return Response({'error': 'No preferences found for this vote.'}, status=status.HTTP_400_BAD_REQUEST)

    vote_count = Counter()
    results = defaultdict(list)

    # Initialize the first round of vote counts
    for preference in preferences:
        if preference.rank == 1:
            vote_count[preference.candidate.description] += 1

    if not vote_count:
        return Response({'error': 'No votes have been cast yet.'}, status=status.HTTP_400_BAD_REQUEST)

    round_results = [dict(vote_count)]
    total_votes = sum(vote_count.values())
    majority_threshold = total_votes / 2
    round_number = 1

    while True:
        print(f"Round {round_number} processing...")
        
        # Check if any candidate has more than 50% of the votes
        for candidate, count in vote_count.items():
            if count > majority_threshold:
                return Response({
                    'winner': candidate,
                    'round': round_number,
                    'vote_counts': round_results,
                    'final_votes': vote_count
                }, status=status.HTTP_200_OK)
        
        # Find the candidate with the least votes
        if not vote_count:
            return Response({
                'result': 'No votes have been cast or all candidates have been eliminated.',
                'round': round_number,
                'vote_counts': round_results,
                'final_votes': vote_count
            }, status=status.HTTP_200_OK)

        min_votes = min(vote_count.values())
        eliminated_candidates = [candidate for candidate, count in vote_count.items() if count == min_votes]

        # Eliminate the candidate with the least votes and redistribute their votes
        for eliminated_candidate in eliminated_candidates:
            eliminated_candidate_preferences = Preference.objects.filter(candidate__description=eliminated_candidate, candidate__vote=vote)
            for preference in eliminated_candidate_preferences:
                next_preference = Preference.objects.filter(voter=preference.voter, candidate__vote=vote, rank=preference.rank + 1).first()
                if next_preference:
                    vote_count[next_preference.candidate.description] += 1

            # Remove the eliminated candidate from the count, add to the next preference before next round
            del vote_count[eliminated_candidate]

        # If all remaining candidates have the same votes, declare the candidate with the most first-round votes as the winner
        if len(eliminated_candidates) == len(vote_count):
            max_first_round_votes = max(round_results[0].values())
            winner = [candidate for candidate, count in round_results[0].items() if count == max_first_round_votes][0]
            return Response({
                'winner': winner,
                'round': round_number,
                'vote_counts': round_results,
                'final_votes': vote_count
            }, status=status.HTTP_200_OK)

        round_number += 1
        round_results.append(dict(vote_count))

    return Response({
        'result': 'No clear winner found after all rounds.',
        'round': round_number,
        'vote_counts': round_results,
        'final_votes': vote_count
    }, status=status.HTTP_200_OK)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_candidate(request):
    vote_id = request.data.get('vote_id')
    description = request.data.get('description')
    vote = get_object_or_404(Vote, id=vote_id)
    candidate = Candidate.objects.create(vote=vote, description=description)
    serializer = CandidateSerializer(candidate)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.description = request.data.get('description', candidate.description)
    candidate.save()
    serializer = CandidateSerializer(candidate)
    return Response(serializer.data, status=status.HTTP_200_OK)
    

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_profiles(request):
    profiles = Profile.objects.all()
    serializer = ProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fetch_candidates(request):
    vote_id = request.data.get('vote_id')
    if not vote_id:
        return Response({'error': 'vote_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    vote = get_object_or_404(Vote, id=vote_id)
    candidates = Candidate.objects.filter(vote=vote)
    
    if not candidates.exists():
        return Response([], status=status.HTTP_200_OK)

    serializer = CandidateSerializer(candidates, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_profiles(request):
    profiles = Profile.objects.all()
    serializer = ProfileSerializer(profiles, many=True)
    return Response(serializer.data)



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



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_enrollment(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id, author=request.user)
    vote.open_enrollment = False
    vote.save()
    return Response(VoteSerializer(vote).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_polls(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id, author=request.user)
    vote.polls_open = not vote.polls_open
    vote.save()
    return Response(VoteSerializer(vote).data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_votes(request):
    votes = Vote.objects.filter(author=request.user)
    serializer = VoteSerializer(votes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_vote(request):
    vote_id = request.data.get('vote_id')
    if not vote_id:
        return Response({'error': 'vote_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    vote = get_object_or_404(Vote, id=vote_id, author=request.user)
    vote.delete()
    return Response({'message': 'Vote deleted successfully'}, status=status.HTTP_200_OK)
