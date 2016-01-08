from models import Beacon, Vehicle, Spot
from rest_framework import viewsets
from serializers import BeaconSerializer, VehicleSerializer, SpotSerializer
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
import json
# from rest_framework.permissions import AllowAny


class BeaconViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows beacons to be viewed or edited.
    """
    queryset = Beacon.objects.all().order_by('-last_seen_timestamp')
    serializer_class = BeaconSerializer

    @list_route()
    def beacon_by_uuid(self, request):
        """
        Returns response with beacon object in db corresponding to uuid in request
        """
        try:
            uuid = str(request.GET.get('uuid'))
        except (TypeError, ValueError):
            return return_bad_request('uuid parameter missing or incorrect')

        beacon = self.get_beacon_by_uuid(uuid)

        if beacon is not None:
            serializer = self.get_serializer(beacon)
            return Response(serializer.data)
        else:
            return return_bad_request('uuid not in database')

    def get_beacon_by_uuid(self, uuid):
        """
        Returns beacon object in db corresponding to uuid
        """
        print uuid
        namespace_id = '0x'+uuid[0:20]
        instance_id = '0x'+uuid[20:]
        print namespace_id
        print instance_id
        try:
            beacon = Beacon.objects.get(namespace_id=namespace_id, instance_id=instance_id)
        except Beacon.DoesNotExist:
            beacon = None
        return beacon


class VehicleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows vehicles to be viewed or edited.
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    @list_route()
    def live_vehicles(self, request):
        """
        Returns all live vehicles as response
        """
        live_vehicles = self.get_live_vehicles()
        page = self.paginate_queryset(live_vehicles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(live_vehicles, many=True)
        return Response(serializer.data)

    def get_live_vehicles(self):
        """
        Returns queryset containing all live vehicles
        """
        live_vehicles = Vehicle.objects.filter(beacon__is_live=True)
        return live_vehicles

    @list_route()
    def vehicle_by_uuid(self, request):
        """
        Returns registration_number of vehicle attached to beacon
        """
        try:
            uuid = str(request.GET.get('uuid'))
        except (TypeError, ValueError):
            return return_bad_request('uuid parameter missing or incorrect')

        vehicle = self.get_vehicle_by_uuid(uuid)

        if vehicle is not None:
            serializer = self.get_serializer(vehicle)
            return Response(serializer.data)
        else:
            return return_bad_request('uuid not in database')

    @detail_route(methods=['post'])
    def set_route(self, request, pk=None):
        """
        sets route to vehicle based on request
        """
        request_dict = json.loads(request.body)[0]
        try:
            route_name = str(request_dict['route_name'])
        except (KeyError, TypeError):
            return return_bad_request('parameter route_name missing or incorrect', request_dict)

        try:
            registration_number = str(request_dict['registration_number'])
        except (KeyError, TypeError):
            return return_bad_request('parameter registration_number missing or incorrect', request_dict)
        if self.set_route_from_registration_number(registration_number, route_name):
            return return_request_ok()
        else:
            return return_bad_request()

    def get_vehicle_by_uuid(self, uuid):
        """
        Returns beacon object in db corresponding to uuid
        """
        print uuid
        namespace_id = '0x'+uuid[0:20]
        instance_id = '0x'+uuid[20:]
        print namespace_id
        print instance_id
        try:
            beacon = Beacon.objects.get(namespace_id=namespace_id, instance_id=instance_id)
            vehicle = beacon.vehicle
        except Beacon.DoesNotExist:
            vehicle = None
        return vehicle

    def set_route_from_registration_number(self, registration_number, route_name):
        """
        returns true if route set, else false
        """
        try:
            vehicle = Vehicle.objects.get(registration_number=registration_number)
        except (Vehicle.DoesNotExist):
            return False
        vehicle.route_name = route_name
        vehicle.save()
        return True


class SpotViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows beacons to be viewed or edited.
    """
    queryset = Spot.objects.all().order_by('-spot_timestamp')
    serializer_class = SpotSerializer

    @detail_route(methods=['post'])
    def spot_with_id(self, request, pk=None):
        """
        Creates spot with beacon id
        POST params - user, spot_timestamp, lat, lng, namespace_id, instance_id
        """
        request_dict = json.loads(request.body)[0]
        try:
            user = str(request_dict['user'])
        except (KeyError, TypeError):
            return return_bad_request('parameter user missing or incorrect', request_dict)

        try:
            spot_timestamp = int(request_dict['spot_timestamp'])
        except (KeyError, TypeError):
            return return_bad_request('parameter spot_timestamp missing or incorrect', request_dict)

        try:
            lat = float(request_dict['lat'])
        except (KeyError, TypeError):
            return return_bad_request('parameter lat missing or incorrect', request_dict)

        try:
            lng = float(request_dict['lng'])
        except (KeyError, TypeError):
            return return_bad_request('parameter lng missing or incorrect', request_dict)

        try:
            namespace_id = str(request_dict['namespace_id'])
        except (KeyError, TypeError):
            return return_bad_request('parameter namespace_id missing or incorrect', request_dict)

        try:
            instance_id = str(request_dict['instance_id'])
        except (KeyError, TypeError):
            return return_bad_request('parameter instance_id missing or incorrect', request_dict)

        values = {
            'user': user,
            'spot_timestamp': spot_timestamp,
            'lat': lat,
            'lng': lng,
        }
        spot = Spot(**values)
        spot.save(namespace_id=namespace_id, instance_id=instance_id)
        return return_request_ok()


def return_bad_request(message='Bad request', request_dict=None):
    """
    helper method for bad request response
    """
    res = [{"code": 400, "message": "Bad Request: "+message, "request_dict": str(request_dict)}]
    return Response(data=res)


def return_request_ok():
    """
    helper method for generic request ok response
    """
    res = [{"code": 200, "message": "Request ok"}]
    return Response(data=res)
