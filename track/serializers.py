from rest_framework import serializers

from models import Beacon, Vehicle, Spot


class BeaconSerializer(serializers.ModelSerializer):
    """
    Serializer for Beacon model of track app
    """
    class Meta:
        model = Beacon
        fields = ('id', 'namespace_id', 'instance_id', 'lat', 'lng', 'last_seen_timestamp')


class VehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for Vehicle model of track app
    """
    beacon = serializers.StringRelatedField(
        # view_name='beacon-detail',
        # queryset=Beacon.objects.all(),
    )

    class Meta:
        model = Vehicle
        fields = ('serial_number', 'is_beaconed', 'is_live', 'beacon')


class SpotSerializer(serializers.ModelSerializer):
    """
    Serializer for Spot model of track app
    """
    beacon = serializers.StringRelatedField(
        # view_name='beacon-detail',
        # queryset=Beacon.objects.all(),
    )

    class Meta:
        model = Spot
        fields = ('id', 'user', 'spot_timestamp', 'lat', 'lng', 'beacon')
