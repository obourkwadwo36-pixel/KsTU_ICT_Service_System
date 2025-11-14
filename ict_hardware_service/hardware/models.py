from django.db import models
from django.contrib.auth.models import User

class ICTOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.get_full_name()

from django.db import models
from django.contrib.auth.models import User

class Technician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, blank=True)

    def __str__(self):
        # Try to use full_name field first (if your User model has it)
        full_name = getattr(self.user, 'fullname', None)

        # Fallbacks
        if not full_name:
            full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        if not full_name:
            full_name = self.user.username  # usually email

        return full_name




class ServiceRequest(models.Model):
    CATEGORY_CHOICES = [
        ('Desktop', 'Desktop'),
        ('Laptop', 'Laptop'),
        ('Printer', 'Printer'),
        ('Photocopier', 'Photocopier'),
        ('UPS', 'UPS'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_requests')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_to = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.category} - {self.staff.username}"

class JobUpdate(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='updates')
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE)
    update_text = models.TextField()
    date_updated = models.DateTimeField(auto_now_add=True, db_column='timestamp')

    def __str__(self):
        return f"Update on {self.request.id} by {self.technician}"
