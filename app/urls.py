from . import views
from django.urls import path

urlpatterns = [
    # POST /events - Create new event
    # GET /events - List all upcoming events  
    path('events/', views.EventListCreateView.as_view(), name='event-list-create'),
    
    # POST /events/{event_id}/register - Register for event
    path('events/<int:event_id>/register/', views.register_for_event, name='event-register'),
    
    # GET /events/{event_id}/attendees - Get event attendees
    path('events/<int:event_id>/attendees/', views.EventAttendeesView.as_view(), name='event-attendees'),
]