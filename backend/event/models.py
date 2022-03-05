from django.db import models
from localflavor.us.forms import USStateSelect, USZipCodeField
from register.models import HOST

# Create your models here.
class Location(models.Model):
    LocationId = models.AutoField(primary_key=True)
    City = models.CharField(max_length=64, default="Bloomington")
    State = models.CharField(max_length=50,  default="IN")
    def __str__(self) -> str:
        return self.LocationId

class Event(models.Model):
    # Each attribute of the model represents a database field.
    EventId = models.AutoField(primary_key=True)
    EventName = models.CharField(max_length=50)
    EventDescription = models.CharField(max_length=300, default="")
    EventGenre = models.CharField(max_length=50)
    EventType = models.CharField(max_length=50)
    EventDate = models.DateField()
    EventStartTime = models.TimeField(max_length=50)
    EventEndTime = models.TimeField(max_length=50)
    Performer = models.CharField(max_length=50)
    MaxNoOfSeats = models.IntegerField()
    SeatsAvailable = models.IntegerField()
    Price = models.IntegerField()
    HostId = models.ForeignKey(HOST, on_delete=models.CASCADE)
    Address = models.CharField(max_length=100, default="")
    ZipCode = models.CharField(max_length=5,  default="47401")
    LocationId = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.EventId



