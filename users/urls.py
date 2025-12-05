from django.urls import path
from users.views import sign_up, sign_in, sign_out,admin_dashboard, assign_role, create_group,show_groups,activate_user,no_permission,user_dashboard




urlpatterns = [
    path('sign_up/',sign_up, name='sign-up'),
    path('activate/<int:user_id>/<str:token>/', activate_user, name='activate_user'),
    path('sign_in/',sign_in, name='sign-in'),
    path('logout/', sign_out, name='logout'),
    path('no_permission/', no_permission, name='no_permission'),


    #For Admin path
    path('admin_dashboard/', admin_dashboard, name='admin-dashboard'),
    path('assign_role/<int:user_id>/', assign_role, name='assign-role'),
    path('create_group/', create_group, name='create-group'),
    path('show_groups/', show_groups, name='show-groups'),


    #For User path
    path("dashboard/", user_dashboard, name="dashboard"),





]