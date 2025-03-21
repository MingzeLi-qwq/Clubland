from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Notification

# Create your tests here.
User = get_user_model()

class NotificationTestCase(TestCase):
    def setUp(self):
        """設置測試用戶與測試數據"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.factory = RequestFactory()

        # 創建測試通知
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
        """測試 Notification 的 __str__ 方法"""
        notification = Notification.objects.create(
            user=self.user, title="Test Title", message="Test Message", notification_type='general'
        )
        expected = f"[General Messages] Notification for {self.user.username}: {notification.message}"
        self.assertEqual(str(notification), expected)

    def test_notification_auto_delete_oldest(self):
        """測試超過 2000 條通知時，是否刪除最舊的通知"""
        for i in range(2001):
            Notification.objects.create(user=self.user, title=f"Title {i}", message=f"Message {i}")

        count = Notification.objects.filter(user=self.user).count()
        self.assertEqual(count, 2000)

        # 確保第一條已被刪除
        messages = Notification.objects.filter(user=self.user).order_by('created_at').values_list('message', flat=True)
        self.assertNotIn("Message 0", list(messages))

    def test_notification_list_view(self):
        """測試通知列表"""
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification_system/notifications.html')
        self.assertIn('notifications', response.context)
        self.assertEqual(len(response.context['notifications']), 3)

    def test_notification_detail_view_marks_as_read(self):
        """測試通知詳情並標記為已讀"""
        response = self.client.get(reverse('notification_detail', args=[self.notification1.id]))
        self.assertEqual(response.status_code, 200)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    def test_mark_all_as_read_post(self):
        """測試標記所有未讀通知為已讀"""
        response = self.client.post(reverse('mark_all_as_read'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'updated_count': 2})
        self.notification1.refresh_from_db()
        self.notification2.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
        self.assertTrue(self.notification2.is_read)

    def test_mark_all_as_read_get(self):
        """測試 GET 請求標記為已讀是否失敗"""
        response = self.client.get(reverse('mark_all_as_read'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'failure'})

    def test_delete_notification_post(self):
        """測試刪除單筆通知"""
        response = self.client.post(reverse('delete_notification', args=[self.notification1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(id=self.notification1.id)

    def test_delete_notification_get(self):
        """測試 GET 請求刪除通知是否失敗"""
        response = self.client.get(reverse('delete_notification', args=[self.notification2.id]))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'error', 'message': 'Invalid request method'})

    def test_delete_all_notifications_post(self):
        """測試刪除所有通知"""
        response = self.client.post(reverse('delete_all_notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 0)

    def test_delete_all_notifications_get(self):
        """測試 GET 請求刪除所有通知是否失敗"""
        response = self.client.get(reverse('delete_all_notifications'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'error'})

    def test_base_notifications_context(self):
        """測試 base_notifications 是否正確返回未讀通知"""
        from .views import base_notifications
        request = self.factory.get('/')
        request.user = self.user
        context = base_notifications(request)
        self.assertIn('notifications', context)
        self.assertIn('unread_notifications_count', context)
        self.assertEqual(context['unread_notifications_count'], 2)
        self.assertEqual(len(context['notifications']), 2)

    def test_delete_all_notifications_auto_cleanup(self):
        """測試當通知超過 2000 條時，最舊的通知是否被刪除"""
        # 建立 2000 條通知
        for i in range(2000):
            Notification.objects.create(user=self.user, title=f"Title {i}", message=f"Message {i}")

        # 取得最舊的通知
        oldest_notification = Notification.objects.order_by('created_at').first()
        self.assertIsNotNone(oldest_notification)

        # 確保目前有 2000 條
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 2000)

        # 再新增一條通知，應該會觸發自動刪除最舊的通知
        new_notification = Notification.objects.create(user=self.user, title="Newest", message="Newest Message")

        # 確保仍然只有 2000 條（而不是 2001 條）
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 2000)

        # 確保最舊的通知已經被刪除
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(id=oldest_notification.id)

        # 執行刪除所有通知的 API
        response = self.client.post(reverse('delete_all_notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})

        # 確保刪除後的通知數量為 0
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 0)

    def test_auto_delete_only_oldest_notification(self):
        """測試當通知超過 2000 條時，只刪除最舊的一條，而不是全部刪除"""
        # 建立 2000 條通知
        for i in range(2000):
            Notification.objects.create(user=self.user, title=f"Title {i}", message=f"Message {i}")

        # 取得目前的最舊通知
        oldest_notification = Notification.objects.order_by('created_at').first()
        self.assertIsNotNone(oldest_notification)

        # 新增第 2001 條通知，應該觸發 `save()` 的自動刪除邏輯
        new_notification = Notification.objects.create(user=self.user, title="Newest", message="Newest Message")

        # **確保總數仍然是 2000（因為最舊的一條應該被刪除）**
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 2000)

        # **確保最舊的那條通知已被刪除**
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(id=oldest_notification.id)

        # **確保新通知存在**
        self.assertTrue(Notification.objects.filter(id=new_notification.id).exists())
