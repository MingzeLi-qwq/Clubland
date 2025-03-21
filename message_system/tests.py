from django.test import TestCase
from django.test import TestCase, Client
from user_system.models import User  # ✅ 导入自定义 User 模型
from message_system.models import Message

class MessageSystemTest(TestCase):
    def setUp(self):
        # ✅ 使用自定义 User 模型创建用户
        self.user1 = User.objects.create_user(username='user1', password='testpassword')
        self.user2 = User.objects.create_user(username='user2', password='testpassword')
        self.client = Client()

        # ✅ 创建消息用于测试
        Message.objects.create(sender=self.user1, receiver=self.user2, text='Hello!')
        Message.objects.create(sender=self.user2, receiver=self.user1, text='Hi!')

    def test_get_messages(self):
        self.client.login(username='user1', password='testpassword')
        response = self.client.get('/api/messages/user2/')
        data = response.json()

        print('get_messages response:', data)  # 调试输出

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['messages']), 2)
        self.assertEqual(data['messages'][0]['text'], 'Hello!')
        self.assertEqual(data['messages'][1]['text'], 'Hi!')

    def test_search_users(self):
        self.client.login(username='user1', password='testpassword')
        response = self.client.get('/api/search/?query=user')
        data = response.json()

        print('search_users response:', data)  # 调试输出

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['users']), 2)
        self.assertEqual(data['users'][0]['username'], 'user1')
        self.assertEqual(data['users'][1]['username'], 'user2')

    def test_send_message(self):
        self.client.login(username='user1', password='testpassword')
        
        response = self.client.post('/api/send/', {
            'receiver': 'user2',
            'text': 'New message!'
        })
        self.assertEqual(response.status_code, 201)

        # ✅ 验证消息存储正确
        self.assertTrue(
            Message.objects.filter(sender=self.user1, receiver=self.user2, text='New message!').exists()
        )

    def test_clear_chat(self):
        self.client.login(username='user1', password='testpassword')

        # ✅ 调用接口清除聊天记录
        response = self.client.post('/api/clear_chat/', {'receiver': 'user2'})
        self.assertEqual(response.status_code, 200)

        # ✅ 确认消息被清除
        messages = Message.objects.filter(sender=self.user1, receiver=self.user2)
        self.assertFalse(messages.exists())

    def test_clear_chat_with_nonexistent_user(self):
        self.client.login(username='user1', password='testpassword')

        # ✅ 尝试删除不存在的用户聊天记录
        response = self.client.post('/api/clear_chat/', {'receiver': 'user3'})
        data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'Receiver not found')

    def test_send_message_without_login(self):
        # ✅ 未登录状态下尝试发送消息
        response = self.client.post('/api/send/', {
            'receiver': 'user2',
            'text': 'This should fail'
        })

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['message'], 'Authentication required')

