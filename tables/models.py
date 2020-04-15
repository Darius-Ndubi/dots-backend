import uuid
from django.db import models
from django.contrib.auth import get_user_model


TABLE_SOURCES = (
    ('csv', 'csv'),
    ('kobo', 'kobo'),
    ('surveycto', 'surveycto'),
    ('ona', 'ona')
)


class Table(models.Model):
    """
    Table Model: A table corresponds to a dataset Metadata
    stores information about imported table(dataset)
    """
    table_uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=150)
    source = models.CharField(max_length=20, choices=TABLE_SOURCES)
    owner = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'
