from django.db import models
from django.contrib.auth.models import User, Group


class IAACR(models.Model):

    drug_name = models.CharField(max_length=255)
    drug_code = models.CharField(max_length=255)

    def __str__(self):
        return self.drug_name


class FacilityDropdown(models.Model):

    facility_name = models.CharField(max_length=255)
    facility_code = models.CharField(max_length=255)

    def __str__(self):
        return self.facility_name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, null=True)
    # facility = models.OneToOneField(FacilityDropdown, on_delete=models.CASCADE)
    facility = models.ForeignKey(FacilityDropdown, on_delete=models.CASCADE)
    pr_number = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.user.username


Group.add_to_class(
    "page_permission", models.CharField(max_length=180, null=True, blank=True)
)
