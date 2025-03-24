from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Notification

# Create your tests here.
User = get_user_model()

class NotificationTestCase(TestCase):
    def setUp(self):
        """Set up test user and test data"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.factory = RequestFactory()

        # Create test notifications
        self.notification1 = Notification.objects.create(
            user=self.user, title="Title1", message="Message1", is_read=False
        )
        self.notification2 = Notification.objects.create(
            user=self.user, title="Title2", message="Message2", is_read=False
        )
        self.notification3 = Notification.objects.create(
            user=self.user, title="Title3", message="Message3", is_read=True
        )

    def test_notification_str(self):
        """Test __str__ method of Notification"""
        notification = Notification.objects.create(
            user=self.user, title="Test Title", message="Test Message", notification_type='general'
        )
        expected = f"[General Messages] Notification for {self.user.username}: {notification.message}"
        self.assertEqual(str(notification), expected)

    def test_notification_auto_delete_oldest(self):
        """Test whether the oldest notification is deleted when exceeding 2000 notifications"""
        for i in range(2001):
            Notification.objects.create(user=self.user, title=f"Title {i}", message=f"Message {i}")

        count = Notification.objects.filter(user=self.user).count()
        self.assertEqual(count, 2000)

        # Ensure the first message has been deleted
        messages = Notification.objects.filter(user=self.user).order_by('created_at').values_list('message', flat=True)
        self.assertNotIn("Message 0", list(messages))

    def test_notification_list_view(self):
        """Test notification list view"""
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification_system/notifications.html')
        self.assertIn('notifications', response.context)
        self.assertEqual(len(response.context['notifications']), 3)

    def test_notification_detail_view_marks_as_read(self):
        """Test notification detail view and mark as read"""
        response = self.client.get(reverse('notification_detail', args=[self.notification1.id]))
        self.assertEqual(response.status_code, 200)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    def test_mark_all_as_read_post(self):
        """Test marking all unread notifications as read"""
        response = self.client.post(reverse('mark_all_as_read'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'updated_count': 2})
        self.notification1.refresh_from_db()
        self.notification2.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
        self.assertTrue(self.notification2.is_read)

    def test_mark_all_as_read_get(self):
        """Test failure when using GET request to mark as read"""
        response = self.client.get(reverse('mark_all_as_read'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'failure'})

    def test_delete_notification_post(self):
        """Test deleting a single notification"""
        response = self.client.post(reverse('delete_notification', args=[self.notification1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(id=self.notification1.id)

    def test_delete_notification_get(self):
        """Test failure when using GET request to delete notification"""
        response = self.client.get(reverse('delete_notification', args=[self.notification2.id]))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'error', 'message': 'Invalid request method'})

    def test_delete_all_notifications_post(self):
        """Test deleting all notifications"""
        response = self.client.post(reverse('delete_all_notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 0)

    def test_delete_all_notifications_get(self):
        """Test failure when using GET request to delete all notifications"""
        response = self.client.get(reverse('delete_all_notifications'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'error'})

    def test_base_notifications_context(self):
        """Test whether base_notifications correctly returns unread notifications"""
        from .views import base_notifications
        request = self.factory.get('/')
        request.user = self.user
        context = base_notifications(request)
        self.assertIn('notifications', context)
        self.assertIn('unread_notifications_count', context)
        self.assertEqual(context['unread_notifications_count'], 2)
        self.assertEqual(len(context['notifications']), 2)

    def test_delete_all_notifications_auto_cleanup(self):
        """Test whether the oldest notification is deleted when exceeding 2000 notifications"""
        # Create 2000 notifications
        for i in range(2000):
            Notification.objects.create(user=self.user, title=f"Title {i}", message=f"Message {i}")

        # Get the oldest notification
        oldest_notification = Notification.objects.order_by('created_at').first()
        self.assertIsNotNone(oldest_notification)

        # Ensure there are 2000 notifications
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 2000)

        # Create one more notification, which should trigger auto-deletion of the oldest
        new_notification = Notification.objects.create(user=self.user, title="Newest", message="Newest Message")

        # Ensure the count remains at 2000 (not 2001)
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 2000)

        # Ensure the oldest notification was deleted
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(id=oldest_notification.id)

        # Call the delete all API
        response = self.client.post(reverse('delete_all_notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})

        # Ensure notifications are deleted
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 0)

    def test_auto_delete_only_oldest_notification(self):
        """Test that only the oldest notification is deleted when exceeding 2000 notifications"""
        # Create 2000 notifications
        for i in range(2000):
            Notification.objects.create(user=self.user, title=f"Title {i}", message=f"Message {i}")

        # Get the current oldest notification
        oldest_notification = Notification.objects.order_by('created_at').first()
        self.assertIsNotNone(oldest_notification)

        # Add the 2001st notification, should trigger auto-delete in save()
        new_notification = Notification.objects.create(user=self.user, title="Newest", message="Newest Message")

        # Ensure total is still 2000 (oldest should be deleted)
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 2000)

        # Ensure the oldest was deleted
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(id=oldest_notification.id)

        # Ensure new notification exists
        self.assertTrue(Notification.objects.filter(id=new_notification.id).exists())