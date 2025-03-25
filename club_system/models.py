from django.db import models
from user_system.models import User
from django.utils import timezone

class Club(models.Model):
    club_id = models.PositiveIntegerField(primary_key=True, unique=True, editable=False)  # Plain numeric numbering in ascending order from 1
    name = models.CharField(max_length=50, unique=True, blank=False)  # Name of the organization, can not be empty, allow spaces, can not be repeated
    description = models.TextField(default="This Club hasn't added a Description yet", blank=True, null=True)  # Society profile, no length limit, default content
    members = models.ManyToManyField(
        User,
        through='Membership',
        related_name='clubs_joined'
    )
    background_image = models.ImageField(upload_to='backgrounds/', null=True, blank=True)

    

    """This section is used to implement the logic for incrementing association IDs"""
    def save(self, *args, **kwargs):
        if not self.club_id:  # When club_id is not assigned
            last_club = Club.objects.order_by('-club_id').first()
            if last_club:
                self.club_id = last_club.club_id + 1
            else:
                self.club_id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Club_id:{self.club_id} - {self.name}"
    

"""
The Membership model is used to represent the many-to-many relationship between users and organizations, 
and contains additional fields to store the user's role in the organization and the date of joining.
"""
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    is_manager = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'club')]  # Ensure that users cannot join the same association repeatedly



"""
This section is used to hold user requests to create new clubs
"""
class NewClubRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'pending'),
        (STATUS_APPROVED, 'approved'),
        (STATUS_REJECTED, 'rejected'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_requests')
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_club_requests')
    review = models.TextField(null=True, blank=True)
    request_id = models.PositiveIntegerField(primary_key=True, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.request_id:
            last_request = NewClubRequest.objects.order_by('-request_id').first()
            if last_request:
                self.request_id = last_request.request_id + 1
            else:
                self.request_id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Club Request: {self.request_id} - {self.name} (Status: {self.status})"
    def approve(self, admin_user):
        if self.status == self.STATUS_PENDING:
            new_club = Club.objects.create(
                name=self.name,
                description=self.description
            )
            Membership.objects.create(
                user=self.creator,
                club=new_club,
                is_manager=True
            )
            self.status = self.STATUS_APPROVED
            self.reviewed_at = timezone.now()
            self.reviewed_by = admin_user
            self.save()
            return new_club
        return None

    def reject(self, admin_user):
        if self.status == self.STATUS_PENDING:
            self.status = self.STATUS_REJECTED
            self.reviewed_at = timezone.now()
            self.reviewed_by = admin_user
            self.save()

