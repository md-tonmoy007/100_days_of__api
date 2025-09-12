from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from posts.models import Post, Project, Comment, Like
from account.models import FriendshipRequest
import random
from datetime import datetime, timedelta
from django.utils import timezone
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for posts, users, projects, and interactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of users to create'
        )
        parser.add_argument(
            '--posts',
            type=int,
            default=100,
            help='Number of posts to create'
        )
        parser.add_argument(
            '--projects',
            type=int,
            default=15,
            help='Number of projects to create'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to create sample data...'))
        
        # Create sample projects
        self.create_projects(options['projects'])
        
        # Create sample users
        self.create_users(options['users'])
        
        # Create sample posts
        self.create_posts(options['posts'])
        
        # Create friendships and interactions
        self.create_friendships()
        self.create_likes_and_comments()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_projects(self, count):
        self.stdout.write(f'Creating {count} projects...')
        
        project_names = [
            'Web Development Bootcamp',
            'Machine Learning Journey',
            'Mobile App Development',
            'Data Science Fundamentals',
            'DevOps Mastery',
            'UI/UX Design Challenge',
            'Python Programming',
            'JavaScript Mastery',
            'Cloud Computing',
            'Cybersecurity Basics',
            'React Development',
            'Django Framework',
            'API Development',
            'Database Design',
            'Game Development',
            'Blockchain Technology',
            'Artificial Intelligence',
            'Frontend Development',
            'Backend Development',
            'Full Stack Journey'
        ]
        
        projects = []
        for i, name in enumerate(project_names[:count]):
            project, created = Project.objects.get_or_create(
                name=name,
                defaults={'number': random.randint(1, 100)}
            )
            projects.append(project)
            if created:
                self.stdout.write(f'Created project: {name}')
        
        return projects

    def create_users(self, count):
        self.stdout.write(f'Creating {count} users...')
        
        first_names = [
            'Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Riley', 'Jamie', 'Avery',
            'Quinn', 'Sage', 'River', 'Phoenix', 'Skylar', 'Rowan', 'Finley', 'Emery',
            'Dakota', 'Sage', 'Blake', 'Cameron', 'Hayden', 'Peyton', 'Reese', 'Drew'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White'
        ]
        
        projects = list(Project.objects.all())
        users = []
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
            
            # Skip if user already exists
            if User.objects.filter(email=email).exists():
                continue
                
            user = User.objects.create_user(
                name=name,
                email=email,
                password='password123',
                is_verified=True,
                posts_count=0,
                friends_count=0
            )
            
            # Assign random project
            if projects:
                user.project = random.choice(projects)
                user.save()
            
            users.append(user)
            self.stdout.write(f'Created user: {name} ({email})')
        
        return users

    def create_posts(self, count):
        self.stdout.write(f'Creating {count} posts...')
        
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Create users first.'))
            return
        
        post_templates = [
            "Just completed day {day} of my coding journey! 🚀 Working on {skill} today and feeling great about the progress.",
            "Today I learned about {topic}. It's amazing how much you can accomplish in just one day! #100DaysOfCode",
            "Struggling with {challenge} but not giving up! Every error is a learning opportunity. 💪",
            "Built my first {project_type} today! The feeling of seeing your code come to life is incredible. ✨",
            "Day {day}: Diving deep into {technology}. The learning curve is steep but so rewarding!",
            "Solved a really tricky {problem_type} problem today. Persistence pays off! 🎯",
            "Working on a {project_name} project. Can't wait to share the results with everyone!",
            "Today's focus: {focus_area}. Breaking down complex problems into smaller, manageable pieces.",
            "Collaborating with other developers is the best part of this journey. Thanks to everyone for the support! 🙏",
            "Day {day} update: {achievement}. Every small win counts in this marathon!",
            "Debugging session successful! Found the issue in my {code_area} after 2 hours. Worth every minute! 🐛",
            "Just deployed my latest {deployment_type}. The excitement never gets old! 🚀",
            "Learning {new_concept} is challenging but fascinating. Love how everything connects!",
            "Code review session today helped me improve my {improvement_area}. Feedback is invaluable!",
            "Working late tonight on {night_project}. When you love what you do, time flies! ⏰",
            "Attended a great {event_type} today. The developer community is amazing! 🌟",
            "Refactored old code today. Clean code is so satisfying to read and maintain! ✨",
            "Day {day}: Experimenting with {experiment}. Not all experiments work, but all teach something!",
            "Just finished reading about {reading_topic}. Theory and practice go hand in hand! 📚",
            "Proud moment: My {creation} is working flawlessly! Small steps lead to big achievements! 🏆"
        ]
        
        # Template variables
        skills = ['React', 'Python', 'JavaScript', 'CSS', 'Node.js', 'Django', 'SQL', 'Git', 'API design']
        topics = ['async/await', 'REST APIs', 'database optimization', 'responsive design', 'testing', 'deployment']
        challenges = ['async programming', 'CSS Grid', 'state management', 'database queries', 'performance issues']
        project_types = ['web app', 'mobile app', 'API', 'dashboard', 'portfolio site', 'blog', 'e-commerce site']
        technologies = ['React Hooks', 'Django REST', 'PostgreSQL', 'Docker', 'AWS', 'TypeScript', 'GraphQL']
        problem_types = ['algorithm', 'database', 'frontend', 'backend', 'performance', 'security']
        project_names = ['social media', 'task management', 'weather', 'chat', 'portfolio', 'blog', 'e-learning']
        focus_areas = ['data structures', 'system design', 'user experience', 'performance optimization', 'security']
        achievements = ['completed a tutorial', 'built a feature', 'fixed 5 bugs', 'learned a new concept', 'helped a teammate']
        code_areas = ['React component', 'API endpoint', 'database query', 'CSS animation', 'JavaScript function']
        deployment_types = ['web app', 'API', 'mobile app', 'microservice', 'static site']
        new_concepts = ['microservices', 'containerization', 'CI/CD', 'cloud architecture', 'machine learning']
        improvement_areas = ['code structure', 'error handling', 'documentation', 'testing', 'performance']
        night_projects = ['personal website', 'side project', 'open source contribution', 'learning project']
        event_types = ['webinar', 'conference', 'meetup', 'workshop', 'hackathon']
        experiments = ['new framework', 'design pattern', 'algorithm', 'library', 'architecture']
        reading_topics = ['clean code', 'system design', 'algorithms', 'best practices', 'new technology']
        creations = ['component', 'API', 'feature', 'app', 'website', 'tool', 'script']
        
        posts = []
        for i in range(count):
            user = random.choice(users)
            template = random.choice(post_templates)
            
            # Fill template with random data
            post_body = template.format(
                day=random.randint(1, 100),
                skill=random.choice(skills),
                topic=random.choice(topics),
                challenge=random.choice(challenges),
                project_type=random.choice(project_types),
                technology=random.choice(technologies),
                problem_type=random.choice(problem_types),
                project_name=random.choice(project_names),
                focus_area=random.choice(focus_areas),
                achievement=random.choice(achievements),
                code_area=random.choice(code_areas),
                deployment_type=random.choice(deployment_types),
                new_concept=random.choice(new_concepts),
                improvement_area=random.choice(improvement_areas),
                night_project=random.choice(night_projects),
                event_type=random.choice(event_types),
                experiment=random.choice(experiments),
                reading_topic=random.choice(reading_topics),
                creation=random.choice(creations)
            )
            
            # Create post with random timestamp in the last 30 days
            random_date = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            post = Post.objects.create(
                body=post_body,
                created_by=user,
                likes_count=0,
                comments_count=0
            )
            
            # Update the created_at field manually
            post.created_at = random_date
            post.save()
            
            # Update user's post count
            user.posts_count += 1
            user.save()
            
            posts.append(post)
            
            if i % 10 == 0:
                self.stdout.write(f'Created {i+1} posts...')
        
        self.stdout.write(f'Created {len(posts)} posts successfully!')
        return posts

    def create_friendships(self):
        self.stdout.write('Creating friendships...')
        
        users = list(User.objects.all())
        if len(users) < 2:
            self.stdout.write(self.style.WARNING('Not enough users to create friendships'))
            return
        
        # Create random friendships
        for user in users:
            # Each user gets 3-8 friends
            num_friends = random.randint(3, min(8, len(users) - 1))
            potential_friends = [u for u in users if u != user and u not in user.friends.all()]
            
            if potential_friends:
                friends = random.sample(potential_friends, min(num_friends, len(potential_friends)))
                
                for friend in friends:
                    # Add bidirectional friendship
                    user.friends.add(friend)
                    friend.friends.add(user)
                    
                    # Update friend counts
                    user.friends_count = user.friends.count()
                    friend.friends_count = friend.friends.count()
                    user.save()
                    friend.save()
        
        # Create some pending friend requests
        for _ in range(20):
            sender = random.choice(users)
            potential_recipients = [u for u in users if u != sender and u not in sender.friends.all()]
            
            if potential_recipients:
                recipient = random.choice(potential_recipients)
                
                # Check if request already exists
                existing_request = FriendshipRequest.objects.filter(
                    created_by=sender,
                    created_for=recipient
                ).first()
                
                if not existing_request:
                    FriendshipRequest.objects.create(
                        created_by=sender,
                        created_for=recipient,
                        status=FriendshipRequest.SENT
                    )
        
        self.stdout.write('Friendships created successfully!')

    def create_likes_and_comments(self):
        self.stdout.write('Creating likes and comments...')
        
        users = list(User.objects.all())
        posts = list(Post.objects.all())
        
        if not users or not posts:
            self.stdout.write(self.style.WARNING('No users or posts found'))
            return
        
        comment_templates = [
            "Great work! Keep it up! 👏",
            "This is really inspiring! Thanks for sharing.",
            "I struggled with this too! Your solution helped a lot.",
            "Amazing progress! Can't wait to see what's next.",
            "This is exactly what I needed to see today! 🙌",
            "Your dedication is motivating! Keep going!",
            "Love seeing the journey unfold! Great job!",
            "This is so cool! How long did it take you?",
            "Thanks for sharing your experience! Very helpful.",
            "Impressive work! The community is lucky to have you.",
            "This gave me some great ideas for my own project!",
            "Your persistence is paying off! Well done! 💪",
            "Really appreciate you documenting this journey!",
            "This is the kind of content I love to see! 🔥",
            "Your approach to this problem is brilliant!",
            "Keep pushing forward! You're doing amazing!",
            "This resonates with me so much! Thanks for sharing.",
            "Your posts always brighten my day! 😊",
            "Love the positivity and determination!",
            "This is why I love the developer community! 🚀"
        ]
        
        # Add likes to posts
        for post in posts:
            # Each post gets 0-15 likes
            num_likes = random.randint(0, 15)
            likers = random.sample(users, min(num_likes, len(users)))
            
            for liker in likers:
                like = Like.objects.create(created_by=liker)
                post.likes.add(like)
            
            post.likes_count = post.likes.count()
            post.save()
        
        # Add comments to posts
        for post in posts:
            # Each post gets 0-5 comments
            num_comments = random.randint(0, 5)
            commenters = random.sample(users, min(num_comments, len(users)))
            
            for commenter in commenters:
                comment_body = random.choice(comment_templates)
                
                # Create comment with random timestamp after post creation
                comment_date = post.created_at + timedelta(
                    hours=random.randint(1, 48),
                    minutes=random.randint(0, 59)
                )
                
                comment = Comment.objects.create(
                    body=comment_body,
                    created_by=commenter
                )
                
                # Update created_at manually
                comment.created_at = comment_date
                comment.save()
                
                post.comments.add(comment)
            
            post.comments_count = post.comments.count()
            post.save()
        
        self.stdout.write('Likes and comments created successfully!')
