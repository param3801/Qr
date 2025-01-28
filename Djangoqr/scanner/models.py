from django.db import models


class QRcode(models.Model):
  mobile_number=models.CharField(max_length=10)
  data=models.CharField(max_length=200)

  def __str__(self):
    return f"{self.mobile_number}-{self.data}"