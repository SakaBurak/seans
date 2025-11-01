from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('psychologist-dashboard/', views.psychologist_dashboard, name='psychologist_dashboard'),
    path('assistant-dashboard/', views.assistant_dashboard, name='assistant_dashboard'),
    path('manage-psychologists/', views.manage_psychologists, name='manage_psychologists'),
    path('manage-extra-commission/', views.manage_extra_commission, name='manage_extra_commission'),
    path('my-sessions/', views.my_sessions, name='my_sessions'),
    path('change-password/', views.change_password, name='change_password'),
    path('manage-sessions/', views.manage_sessions, name='manage_sessions'),
    path('assistant-manage-sessions/', views.assistant_manage_sessions, name='assistant_manage_sessions'),
    path('add-session/', views.add_session, name='add_session'),
    path('assistant-add-session/', views.assistant_add_session, name='assistant_add_session'),
    path('edit-session/<int:session_id>/', views.edit_session, name='edit_session'),
    path('assistant-edit-session/<int:session_id>/', views.assistant_edit_session, name='assistant_edit_session'),
    path('delete-session/<int:session_id>/', views.delete_session, name='delete_session'),
    path('assistant-delete-session/<int:session_id>/', views.assistant_delete_session, name='assistant_delete_session'),
    path('add-assistant/', views.add_assistant, name='add_assistant'),
]
