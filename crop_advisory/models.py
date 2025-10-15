from django.db import models

# Create your models here.

class crop_price(models.Model):
    s_no = models.AutoField(primary_key=True)
    state=models.CharField(max_length=40,default='')
    city=models.CharField(max_length=40,default='')
    market_name=models.CharField(max_length=50,default='')
    commodity=models.CharField(max_length=40,default='')
    variety=models.CharField(max_length=40,default='Other')
    Grade=models.CharField(max_length=15,default='Local')
    min_Price = models.DecimalField(max_digits=12, decimal_places=4)
    max_Price = models.DecimalField(max_digits=12, decimal_places=4)
    modal_Price = models.DecimalField(max_digits=12, decimal_places=4)
    date=models.DateField()

class Complaint_Box(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Under Review", "Under Review"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Sample", "Sample"),
    ]

    farmer_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    crop_type = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to="complaints/")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer_name} - {self.crop_type} ({self.status})"