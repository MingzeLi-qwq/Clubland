from django.test import TestCase
from club_system.models import Club

class ClubModelTest(TestCase):

    def setUp(self):
        """初始化測試數據 / Initialize test data"""
        self.club1 = Club.objects.create(name="Test Club1", description="A club for Test, i am 1.")
        self.club2 = Club.objects.create(name="Test Club2", description="A club for Test, i am 2.")

    def test_club_creation(self):
        """測試社團是否正確創建 / Test whether a club is created correctly"""
        club = Club.objects.create(name="Creation Test Club", description="I am for club creation test.")
        self.assertIsInstance(club, Club)
        self.assertEqual(club.name, "Creation Test Club")
        self.assertEqual(club.description, "I am for club creation test.")

    def test_auto_increment_club_id(self):
        """測試 club_id 是否遞增 / Test whether club_id increments correctly"""
        itClub1 = Club.objects.create(name="Increasement Test Club1", description="A club for increasement test. - 1")
        itClub2 = Club.objects.create(name="Increasement Test Club2", description="A club for increasement test. - 2")
        self.assertEqual(itClub2.club_id, itClub1.club_id + 1)  # 檢查是否遞增 / Check if it increments

    def test_name_uniqueness(self):
        """測試社團名稱唯一性 / Test the uniqueness of club names"""
        with self.assertRaises(Exception):  # 期待異常 / Expect an exception
            Club.objects.create(name="Test Club1", description="Duplicate name test.")

    def test_blank_description(self):
        """測試社團簡介是否可以為空 / Test if the club description can be empty"""
        club = Club.objects.create(name="Empty Desc Club")
        self.assertEqual(club.description, None)

    def test_str_method(self):
        """測試 __str__ 方法 / Test the __str__ method"""
        self.assertEqual(str(self.club1), f"Club_id:{self.club1.club_id} - Test Club1")

