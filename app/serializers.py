from .models import Event, Registration


class EventSerializer(serializers.ModelSerializer):
    current_attendees_count = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'location', 'start_time', 'end_time', 
            'max_capacity', 'current_attendees_count', 'available_spots',
            'is_full', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("Start time must be before end time")
        
        if data.get('start_time') and data['start_time'] <= timezone.now():
            raise serializers.ValidationError("Start time must be in the future")
            
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'name', 'email', 'event_name', 'registered_at']
        read_only_fields = ['registered_at']


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ['name', 'email']

    def validate(self, data):
        event = self.context['event']
        
        # Check if event is full
        if event.is_full:
            raise serializers.ValidationError(
                f"Event is full. Maximum capacity: {event.max_capacity}"
            )
        
        # Check for duplicate registration
        if Registration.objects.filter(event=event, email=data['email']).exists():
            raise serializers.ValidationError(
                "This email is already registered for this event"
            )
        
        return data