"""
URL configuration for project_ranked project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from app_ranked.views import *
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [

    #AUTH AND ADMIN
    path('admin/', admin.site.urls),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    #CANDIDATES
    path('add-candidate-to-vote/<int:vote_id>/', add_candidate_to_vote, name='add_candidate_to_vote'),
    path('fetch-candidates/', fetch_candidates, name='fetch_candidates'),
    path('create-candidate/', create_candidate, name='create_candidate'),
    path('update-candidate/<int:candidate_id>/', update_candidate, name='update_candidate'),
    

    # GROUPS
    path('create-friend-group/', create_friend_group, name='create_friend_group'),
    path('add-profile-to-group/<int:group_id>/', add_profile_to_group, name='add_profile_to_group'),
    path('list-friend-groups/', list_friend_groups, name='list_friend_groups'),
    path('list-my-groups/', list_my_groups, name='list_my_groups'),
    path('all-user-group/', all_user_group, name='all_user_group'),

    #PROFILES
    path('profile/', get_profile, name='get_profile'),
    path('fetch-profiles/', fetch_profiles, name='fetch_profiles'),
        
    #USER
    path('create-user/', create_user, name='create_user'),
    path('list-users/', list_users, name='list_users'),

    #VOTE
    path('update-vote/', update_vote),
    path('create-vote/', create_vote, name='create_vote'),
    path('vote-results/', vote_results, name='vote_results'),
    path('create-preference/', create_preference, name='create_preference'),
    path('close-enrollment/<int:vote_id>/', close_enrollment, name='close_enrollment'),
    path('toggle-polls/<int:vote_id>/', toggle_polls, name='toggle_polls'),
    path('my-votes/', my_votes, name='my_votes'),
    path('delete-vote/', delete_vote, name='delete_vote'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
