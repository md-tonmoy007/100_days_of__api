from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from posts.models import Thread, UserThread, Post
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample thread data for the 100 Days system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--threads',
            type=int,
            default=5,
            help='Number of threads to create',
        )
        parser.add_argument(
            '--posts-per-user',
            type=int,
            default=10,
            help='Average number of posts per user in each thread',
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating thread data...')
        
        # Thread topics
        thread_topics = [
            'python',
            'javascript',
            'react',
            'machine-learning',
            'web-development',
            'data-science',
            'mobile-development',
            'devops',
            'cybersecurity',
            'blockchain'
        ]
        
        # Get existing users
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
        
        self.stdout.write(f'Found {len(users)} users')
        
        threads_created = 0
        posts_created = 0
        
        for i in range(options['threads']):
            if i < len(thread_topics):
                topic = thread_topics[i]
            else:
                topic = f'custom-topic-{i}'
            
            # Create thread with random creator
            creator = random.choice(users)
            thread, created = Thread.objects.get_or_create(
                topic=topic,
                defaults={
                    'description': f'Learn {topic.replace("-", " ").title()} in 100 days',
                    'created_by': creator
                }
            )
            
            if created:
                threads_created += 1
                self.stdout.write(f'Created thread: {thread.display_name}')
            
            # Add users to thread
            participants = random.sample(users, min(len(users), random.randint(2, 8)))
            
            for user in participants:
                user_thread, created = UserThread.objects.get_or_create(
                    user=user,
                    thread=thread,
                    defaults={
                        'current_day': 0
                    }
                )
                
                if created:
                    # Create some posts for this user in this thread
                    num_posts = random.randint(1, options['posts_per_user'])
                    current_day = 0
                    
                    for post_num in range(num_posts):
                        current_day += random.randint(1, 3)  # Skip some days randomly
                        if current_day > 100:
                            break
                        
                        # Sample post content
                        post_contents = [
                            f"Day {current_day}: Today I learned about {topic} basics. Excited to continue!",
                            f"Day {current_day}: Working on a {topic} project. Making good progress.",
                            f"Day {current_day}: Struggled with some concepts today, but pushed through.",
                            f"Day {current_day}: Had a breakthrough moment with {topic}! Finally understanding.",
                            f"Day {current_day}: Building a real project using {topic}. It's challenging but fun.",
                            f"Day {current_day}: Reviewing what I've learned so far in {topic}.",
                            f"Day {current_day}: Connected with other learners. Love this community!",
                            f"Day {current_day}: Taking on a more advanced {topic} challenge today.",
                        ]
                        
                        post_content = random.choice(post_contents)
                        
                        post = Post.objects.create(
                            body=post_content,
                            created_by=user,
                            user_thread=user_thread,
                            day_number=current_day,
                            created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                        )
                        posts_created += 1
                    
                    # Update user thread progress
                    user_thread.current_day = current_day
                    if current_day >= 100:
                        user_thread.is_completed = True
                        user_thread.completed_at = timezone.now()
                    user_thread.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {threads_created} threads and {posts_created} posts'
            )
        )
        
        # Update thread statistics
        for thread in Thread.objects.all():
            thread.participants_count = thread.participants.count()
            thread.posts_count = Post.objects.filter(user_thread__thread=thread).count()
            thread.save()
        
        self.stdout.write(self.style.SUCCESS('Updated thread statistics'))
