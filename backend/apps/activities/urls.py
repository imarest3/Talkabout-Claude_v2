from django.urls import path
from .views import (
    ActivityListView,
    ActivityCreateView,
    ActivityDetailView,
    ActivityUpdateView,
    ActivityDeleteView,
    upload_activity_file,
    delete_activity_file,
    activity_statistics,
    activity_export_csv,
)

app_name = 'activities'

urlpatterns = [
    # Activity CRUD
    path('', ActivityListView.as_view(), name='activity_list'),
    path('create/', ActivityCreateView.as_view(), name='activity_create'),
    
    # Needs to be before <str:code>/ to avoid being caught by detail view
    path('<str:code>/export-csv/', activity_export_csv, name='activity_export_csv'),
    path('<str:code>/statistics/', activity_statistics, name='activity_statistics'),
    path('<str:code>/update/', ActivityUpdateView.as_view(), name='activity_update'),
    path('<str:code>/delete/', ActivityDeleteView.as_view(), name='activity_delete'),
    
    # File management
    path('<str:code>/files/upload/', upload_activity_file, name='upload_file'),
    path('<str:code>/files/<uuid:file_id>/delete/', delete_activity_file, name='delete_file'),

    # Detail view should be last of the <str:code>/ patterns
    path('<str:code>/', ActivityDetailView.as_view(), name='activity_detail'),
]
