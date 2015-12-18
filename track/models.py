from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Beacon(models.Model):
    """
    model to store beacon objects
    """
    namespace_id = models.CharField('namespace id', max_length=22)
    instance_id = models.CharField('instance id', max_length=14)
    lat = models.FloatField('latitude')
    lng = models.FloatField('longitude')
    last_seen_timestamp = models.IntegerField('last seen timestamp')

    class Meta:
        verbose_name = 'beacon'
        verbose_name_plural = 'beacons'

    def __str__(self):
        return self.namespace_id+'-'+self.instance_id

    def _set_live(self, timestamp=None, lat=0, lng=0):
        """
        sets is_live = True,
        sets last_seen_timestamp,
        sets lat, lng
        saves object,
        sets vehicle is_live = True
        """
        self.last_seen_timestamp = timestamp
        self.is_live = True
        self.lat = lat
        self.lng = lng
        self.save()
        self.vehicle._set_live()


class Vehicle(models.Model):
    """
    model to store base vehicle objects
    """
    serial_number = models.IntegerField('serial number', primary_key=True)
    is_beaconed = models.BooleanField('true if attached beacon confirmed')
    is_live = models.BooleanField('true if vehicle is live')
    beacon = models.OneToOneField(Beacon, related_name='vehicle')

    class Meta:
        verbose_name = 'vehicle'
        verbose_name_plural = 'vehicles'

    def __str__(self):
        return str(self.serial_number)

    def _set_live(self):
        """
        sets is_live = True,
        saves object
        """
        self.is_live = True
        self.save()


class Spot(models.Model):
    """
    model to store beacon spots
    """
    user = models.CharField('user', max_length=50)
    spot_timestamp = models.IntegerField('timestamp of spot')
    lat = models.FloatField('latitude')
    lng = models.FloatField('longitude')
    beacon = models.ForeignKey(Beacon)

    class Meta:
        verbose_name = 'spot'
        verbose_name_plural = 'spots'

    def __str__(self):
        return self.user+'@'+str(self.spot_timestamp)

    def save(self, namespace_id=None, instance_id=None, *args, **kwargs):
        """
        sets beacon
        saves spot
        sets beacon is_live = True
        sets beacon last_seen_timestamp
        """
        if namespace_id is not None and instance_id is not None:
            try:
                beacon = Beacon.objects.get(namespace_id=namespace_id, instance_id=instance_id)
                self.beacon = beacon
            except Beacon.DoesNotExist:
                '''handle error'''
                return
        super(Spot, self).save(*args, **kwargs)
        self.beacon._set_live(timestamp=self.spot_timestamp, lat=self.lat, lng=self.lng)
