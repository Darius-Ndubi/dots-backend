import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import (ArrayField)
from django.utils import timezone

from tables.models import (Table,)

LAYER_TYPES = (
    ('point', 'Point'),
    ('polygon', 'Polygon')
)

AGGREGATION_CRITERIA = (
    ('sum', 'Sum'),
)


class Layer(models.Model):
    """
    Layer Model
    Information about Map Layers configured on the FE
    """
    layer_uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField('Layer Name', max_length=100,)
    table = models.ForeignKey(Table, verbose_name='Linked Table', on_delete=models.CASCADE)
    tool_tip_fields = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    geo_point_field = models.CharField(max_length=100, null=True, blank=True)
    latitude_field = models.CharField(max_length=100, null=True, blank=True)
    longitude_field = models.CharField(max_length=100, null=True, blank=True)
    data_field = models.CharField('Data Field from the Table', max_length=100, null=True, blank=True)
    boundary_field = models.CharField('Admin Boundary Field', max_length=100, null=True, blank=True)
    layer_colors = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    layer_type = models.CharField(choices=LAYER_TYPES, max_length=50)
    aggregation_criteria = models.CharField(choices=AGGREGATION_CRITERIA, max_length=50, null=True, blank=True)
    created_by = models.ForeignKey(
        get_user_model(), related_name='created_last_modified_by_user', null=True, blank=True, on_delete=models.SET_NULL
    )
    last_modified_by = models.ForeignKey(
        get_user_model(), related_name='last_modified_by_user', null=True, blank=True, on_delete=models.SET_NULL
    )
    create_date = models.DateTimeField()
    last_modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_date = timezone.now()
        self.last_modified = timezone.now()

        return super(Layer, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

