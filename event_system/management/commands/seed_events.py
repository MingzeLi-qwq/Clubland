# events/management/commands/seed_events.py
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from club_system.models import Club
from faker import Faker
from user_system.models import User
from event_system.models import Event, Category


fake = Faker()

# 预定义活动分类
event_categories = [
    "Workshop", "Sports", "Social", "Tech", "Arts",
    "Academic", "Music", "Outdoor", "Career", "Cultural"
]

# 预定义活动地点关键词
locations = [
    "Main Hall", "Room 302", "Sports Complex", "Campus Lawn",
    "Auditorium", "Online", "Conference Room", "Student Center"
]

class Command(BaseCommand):
    help = '为每个社团创建10个随机活动 / Create 10 random events for each club'

    def handle(self, *args, **options):
        self.create_categories()
        self.create_events_for_each_club()
        
    def create_categories(self):
        """创建分类数据（如果不存在）"""
        for name in event_categories:
            Category.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("✅ 成功创建/验证分类数据"))

    def create_events_for_each_club(self):
        """为每个社团创建活动数据"""
        clubs = Club.objects.all()
        users = User.objects.all()
        categories = Category.objects.all()

        if not users.exists():
            self.stdout.write(self.style.ERROR("❌ 错误：没有可用用户，请先创建用户"))
            return
        if not clubs.exists():
            self.stdout.write(self.style.ERROR("❌ 错误：没有可用社团，请先创建社团"))
            return
        
        start_time = timezone.now() + timedelta(days=random.randint(5, 30)),

        for club in clubs:
            if club.name == "AI Club":
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 6))
                event = Event.objects.create(
                    name="AI Hackathon",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="All club members interested in Artificial Intelligence are welcome to participate in the AI Club Hackathon! In this 24-hour programming challenge, teams will collaborate to solve real-world AI problems, using techniques such as machine learning, computer vision, or natural language processing to develop innovative solutions. Whether you're a novice or an experienced developer, this is a great opportunity to learn and practice. The winning team will receive prizes and have the opportunity to present their project to industry experts!",
                )
                tech_category, created = Category.objects.get_or_create(name="Tech")
                event.categories.add(tech_category)
                tech_category, created = Category.objects.get_or_create(name="Workshop")
                event.categories.add(tech_category)
                self.stdout.write(f"Create Event:{event.name}  For Club: {club.name}")

                
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 6))
                event = Event.objects.create(
                    name="AI Ethics & Future Panel Discussion",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="What will the future of Artificial Intelligence look like?Will AI replace human jobs? How should we deal with the ethical issues brought by AI development? This symposium invites researchers in the field of AI, representatives of enterprises and experts in ethics to discuss the trend of AI development, social impact and potential risks. All community members are welcome to actively participate, put forward their questions and opinions, and have in-depth exchanges with the guests!"
                )
                tech_category, created = Category.objects.get_or_create(name="Tech")
                event.categories.add(tech_category)
                self.stdout.write(f"Create Event:{event.name}  For Club: {club.name}")


            elif club.name == "Photography Club":
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 6))
                event = Event.objects.create(
                    name="Urban Exploration Photography Tour",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Want to capture some of the city's most unique landscapes and human moments? Photography Club invites you to join us on an urban exploration photography tour! Together, we'll head to local hidden corners, street markets, historic buildings and nighttime best spots to learn how to use light, composition and color to tell the city's story. Whether you're a cell phone photographer or a DSLR enthusiast, this event is sure to be a rewarding experience!"
                )
                tech_category, created = Category.objects.get_or_create(name="Arts")
                event.categories.add(tech_category)
                self.stdout.write(f"Create Event:{event.name}  For Club: {club.name}")

                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 6))
                event= Event.objects.create(
                    name="Light & Composition Workshop",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="The charm of photography lies in the use of light and shadow and composition. This workshop will be guided by an experienced photographer who will take you deep into the basic techniques of photography, including golden section, leading line, diagonal composition, color matching and so on. We will also help you improve your photography skills through hands-on exercises and critiques of your work, making every shutter click more artistic! Come join us and discover the infinite possibilities of photography!"
                )
                tech_category, created = Category.objects.get_or_create(name="Arts")
                event.categories.add(tech_category)
                self.stdout.write(f"Create Event:{event.name}  For Club: {club.name}")

            elif club.name == "Music Club":
                # Event 1: Concert
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 3))
                event1 = Event.objects.create(
                    name="Spring Musical Showcase",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Join us for an evening of musical excellence! Our talented members will perform a diverse repertoire ranging from classical to contemporary pieces. The showcase will feature solo performances, ensemble pieces, and our club band. Come support your fellow students and enjoy an unforgettable night of music."
                )
                music_category, created = Category.objects.get_or_create(name="Music")
                cultural_category, created = Category.objects.get_or_create(name="Cultural")
                event1.categories.add(music_category, cultural_category)
                self.stdout.write(f"Create Event:{event1.name}  For Club: {club.name}")

                # Event 2: Workshop
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 3))
                event2 = Event.objects.create(
                    name="Music Production Workshop",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Learn the basics of music production in this hands-on workshop! We'll cover digital audio workstations, recording techniques, mixing, and mastering. Bring your laptop and headphones to get practical experience with industry-standard software. Perfect for beginners interested in music production."
                )
                music_category, created = Category.objects.get_or_create(name="Music")
                workshop_category, created = Category.objects.get_or_create(name="Workshop")
                event2.categories.add(music_category, workshop_category)
                self.stdout.write(f"Create Event:{event2.name}  For Club: {club.name}")

            elif club.name == "Chess Club":
                # Event 1: Tournament
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(4, 6))
                event1 = Event.objects.create(
                    name="Annual Chess Championship",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Compete in our annual chess championship! This tournament is open to players of all skill levels. The event will follow Swiss-system tournament rules with multiple rounds. Prizes will be awarded to top performers. Come test your skills and strategy against fellow chess enthusiasts!"
                )
                academic_category, created = Category.objects.get_or_create(name="Academic")
                event1.categories.add(academic_category)
                self.stdout.write(f"Create Event:{event1.name}  For Club: {club.name}")

                # Event 2: Training
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 3))
                event2 = Event.objects.create(
                    name="Chess Strategy Masterclass",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Improve your chess game with our strategy masterclass! Learn advanced tactics, opening strategies, and endgame techniques from experienced players. The session will include analysis of famous games, practice exercises, and one-on-one coaching. Suitable for intermediate players looking to enhance their skills."
                )
                academic_category, created = Category.objects.get_or_create(name="Academic")
                workshop_category, created = Category.objects.get_or_create(name="Workshop")
                event2.categories.add(academic_category, workshop_category)
                self.stdout.write(f"Create Event:{event2.name}  For Club: {club.name}")

            elif club.name == "Drama Club":
                # Event 1: Performance
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 3))
                event1 = Event.objects.create(
                    name="Spring Theater Production",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Join us for our spring theater production! Our talented cast and crew have been working hard to bring you an unforgettable performance. This year's production promises to be an exciting blend of drama, comedy, and musical elements. Don't miss this spectacular showcase of student talent!"
                )
                arts_category, created = Category.objects.get_or_create(name="Arts")
                cultural_category, created = Category.objects.get_or_create(name="Cultural")
                event1.categories.add(arts_category, cultural_category)
                self.stdout.write(f"Create Event:{event1.name}  For Club: {club.name}")

                # Event 2: Workshop
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 3))
                event2 = Event.objects.create(
                    name="Acting Workshop Series",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Develop your acting skills in our comprehensive workshop series! Learn about character development, stage presence, voice projection, and improvisation techniques. Led by experienced theater professionals, this workshop is perfect for both beginners and intermediate actors."
                )
                arts_category, created = Category.objects.get_or_create(name="Arts")
                workshop_category, created = Category.objects.get_or_create(name="Workshop")
                event2.categories.add(arts_category, workshop_category)
                self.stdout.write(f"Create Event:{event2.name}  For Club: {club.name}")

            elif club.name == "Sports Club":
                # Event 1: Tournament
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(4, 6))
                event1 = Event.objects.create(
                    name="Inter-College Sports Tournament",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Join our biggest sports event of the year! Compete in multiple sports including basketball, volleyball, and badminton. Teams from different colleges will participate in this exciting tournament. Great prizes for winning teams and a chance to represent our college in regional championships!"
                )
                sports_category, created = Category.objects.get_or_create(name="Sports")
                event1.categories.add(sports_category)
                self.stdout.write(f"Create Event:{event1.name}  For Club: {club.name}")

                # Event 2: Fitness Workshop
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 3))
                event2 = Event.objects.create(
                    name="Fitness and Nutrition Workshop",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Learn about sports nutrition and fitness training in this comprehensive workshop. Professional trainers will share tips on workout routines, injury prevention, and proper nutrition for athletes. Includes practical sessions and personalized advice. Perfect for both beginners and experienced athletes!"
                )
                sports_category, created = Category.objects.get_or_create(name="Sports")
                workshop_category, created = Category.objects.get_or_create(name="Workshop")
                event2.categories.add(sports_category, workshop_category)
                self.stdout.write(f"Create Event:{event2.name}  For Club: {club.name}")

            elif club.name == "Coding Club":
                # Event 1: Hackathon
                
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(8, 12))
                event1 = Event.objects.create(
                    name="24-Hour Code Challenge",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Challenge yourself in our 24-hour coding competition! Work individually or in teams to build innovative solutions to real-world problems. Prizes for best projects, networking opportunities with tech companies, and great learning experience. All skill levels welcome!"
                )
                tech_category, created = Category.objects.get_or_create(name="Tech")
                event1.categories.add(tech_category)
                self.stdout.write(f"Create Event:{event1.name}  For Club: {club.name}")

                # Event 2: Workshop
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 3))
                event2 = Event.objects.create(
                    name="Web Development Bootcamp",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Get started with web development in this hands-on bootcamp! Learn HTML, CSS, and JavaScript basics. Build your first website from scratch and understand modern web development practices. Bring your laptop and get ready to code!"
                )
                tech_category, created = Category.objects.get_or_create(name="Tech")
                workshop_category, created = Category.objects.get_or_create(name="Workshop")
                event2.categories.add(tech_category, workshop_category)
                self.stdout.write(f"Create Event:{event2.name}  For Club: {club.name}")

            elif club.name == "Astronomy Club":
                # Event 1: Star Gazing
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(3, 4))
                event1 = Event.objects.create(
                    name="Night Sky Observation Event",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Join us for an evening of stargazing! Observe planets, stars, and constellations through our telescopes. Expert astronomers will guide you through the night sky, sharing fascinating facts about celestial objects. Hot beverages provided. Weather permitting."
                )
                academic_category, created = Category.objects.get_or_create(name="Academic")
                outdoor_category, created = Category.objects.get_or_create(name="Outdoor")
                event1.categories.add(academic_category, outdoor_category)
                self.stdout.write(f"Create Event:{event1.name}  For Club: {club.name}")

                # Event 2: Lecture
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 3))
                event2 = Event.objects.create(
                    name="Introduction to Astrophysics",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Explore the fascinating world of astrophysics! This lecture covers basic concepts of celestial mechanics, stellar evolution, and recent discoveries in space exploration. Perfect for anyone interested in understanding the universe better. Q&A session included."
                )
                academic_category, created = Category.objects.get_or_create(name="Academic")
                event2.categories.add(academic_category)
                self.stdout.write(f"Create Event:{event2.name}  For Club: {club.name}")

            elif club.name == "Gaming Club":
                # Event 1: Tournament
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(6, 8))
                event1 = Event.objects.create(
                    name="E-Sports Championship",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Compete in our biggest gaming event of the year! Multiple game tournaments including League of Legends, Valorant, and Super Smash Bros. Great prizes for winners, live streaming of matches, and exciting commentary. Register your team now!"
                )
                tech_category, created = Category.objects.get_or_create(name="Tech")
                social_category, created = Category.objects.get_or_create(name="Social")
                event1.categories.add(tech_category, social_category)
                self.stdout.write(f"Create Event:{event1.name}  For Club: {club.name}")

                # Event 2: Social Gaming
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(3, 4))
                event2 = Event.objects.create(
                    name="Board Game Night",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Take a break from video games and join us for a night of board games! We'll have various classic and modern board games available. Great opportunity to meet fellow gamers and enjoy some offline gaming fun. Snacks and refreshments provided!"
                )
                social_category, created = Category.objects.get_or_create(name="Social")
                event2.categories.add(social_category)
                self.stdout.write(f"Create Event:{event2.name}  For Club: {club.name}")

            elif club.name == "Book Club":
                # Event 1: Book Discussion
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 3))
                event1 = Event.objects.create(
                    name="Monthly Book Discussion",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Join our monthly book discussion! We'll be analyzing and discussing this month's selected book, sharing perspectives and insights. Open to all readers, whether you've finished the book or not. Light refreshments provided."
                )
                cultural_category, created = Category.objects.get_or_create(name="Cultural")
                social_category, created = Category.objects.get_or_create(name="Social")
                event1.categories.add(cultural_category, social_category)
                self.stdout.write(f"Create Event:{event1.name}  For Club: {club.name}")

                # Event 2: Writing Workshop
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 3))
                event2 = Event.objects.create(
                    name="Creative Writing Workshop",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="Explore your creative writing potential! This workshop covers storytelling techniques, character development, and writing exercises. Perfect for aspiring writers and anyone interested in improving their writing skills. Bring your notebook and creativity!"
                )
                workshop_category, created = Category.objects.get_or_create(name="Workshop")
                cultural_category, created = Category.objects.get_or_create(name="Cultural")
                event2.categories.add(workshop_category, cultural_category)
                self.stdout.write(f"Create Event:{event2.name}  For Club: {club.name}")
