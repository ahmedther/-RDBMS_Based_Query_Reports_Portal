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


class NavigationHeaders(models.Model):
    headings = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.headings




class QueryReports(models.Model):
    report_heading = models.ForeignKey(
        NavigationHeaders,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="reports_heading",
    )

    report_name = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="report_name",
    )
    report_sql_query = models.TextField(null=False, blank=False)

    sub_sql_query = models.TextField(null=True, blank=True)

    dropdown_option_value = models.IntegerField(null=True, blank=True)
    dropdown_option_name1 = models.IntegerField(null=True, blank=True)
    dropdown_option_name2 = models.IntegerField(null=True, blank=True)

    facility_template = models.BooleanField(
        verbose_name="Facility Template", default=False, blank=True
    )

    date_template = models.BooleanField(
        verbose_name="Date Template", default=False, blank=True
    )
    pharmacy_iaarc = models.BooleanField(
        verbose_name="Pharmacy IAARC Dropdown", default=False, blank=True
    )

    time_template = models.BooleanField(
        verbose_name="Time Template", default=False, blank=True
    )

    dropdown_options_value = models.TextField(
        verbose_name="Custom Dropdown Options's value",  # Human-readable name for the field (optional)
        null=True,  # Whether the field can be null (optional)
        blank=True,  # Whether the field can be blank (optional)
    )

    dropdown_options_name = models.TextField(
        verbose_name="Custom Dropdown Options's Name",  # Human-readable name for the field (optional)
        null=True,  # Whether the field can be null (optional)
        blank=True,  # Whether the field can be blank (optional)
    )
    input_tags = models.TextField(
        verbose_name="Input Tags",  # Human-readable name for the field (optional)
        null=True,  # Whether the field can be null (optional)
        blank=True,  # Whether the field can be blank (optional)
    )
    textbox = models.TextField(
        verbose_name="TextBox Tags",  # Human-readable name for the field (optional)
        null=True,  # Whether the field can be null (optional)
        blank=True,  # Whether the field can be blank (optional)
    )
    http_response = models.BooleanField(
        verbose_name="Display Within Browser (No Download Option)",
        default=False,
        blank=True,
    )

    def __str__(self):
        return self.report_name.name


Group.add_to_class(
    "page_permission", models.CharField(max_length=180, null=True, blank=True)
)
