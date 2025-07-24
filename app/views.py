from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from .models import Event, Registration
from .serializers import (
    EventSerializer, 
    RegistrationSerializer, 
    EventRegistrationSerializer
)


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    
    def get_queryset(self):
        # Only return upcoming events for GET requests
        if self.request.method == 'GET':
            return Event.objects.filter(start_time__gt=timezone.now())
        return Event.objects.all()


@api_view(['POST'])
def register_for_event(request, event_id):
    """
    Register an attendee for a specific event
    """
    event = get_object_or_404(Event, id=event_id)
    
    # Check if event has already started
    if event.start_time <= timezone.now():
        return Response(
            {"error": "Cannot register for events that have already started"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = EventRegistrationSerializer(
        data=request.data, 
        context={'event': event}
    )
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # Double-check capacity within transaction
                if event.is_full:
                    return Response(
                        {"error": f"Event is full. Maximum capacity: {event.max_capacity}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                registration = serializer.save(event=event)
                return Response(
                    {
                        "message": "Successfully registered for event",
                        "registration": RegistrationSerializer(registration).data
                    },
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(
                {"error": "Registration failed. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventAttendeesView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    
    def get_queryset(self):
        event_id = self.kwargs['event_id']
        event = get_object_or_404(Event, id=event_id)
        return Registration.objects.filter(event=event)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        event_id = self.kwargs['event_id']
        event = get_object_or_404(Event, id=event_id)
        
        return Response({
            'event': {
                'id': event.id,
                'name': event.name,
                'max_capacity': event.max_capacity,
                'current_attendees_count': event.current_attendees_count,
                'available_spots': event.available_spots
            },
            'attendees': serializer.data
        })