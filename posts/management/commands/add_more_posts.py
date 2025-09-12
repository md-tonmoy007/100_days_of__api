from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from posts.models import Post, Project
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Add more posts to existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of additional posts to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(self.style.SUCCESS(f'Adding {count} more posts...'))
        
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
        
        # Extended post templates for variety
        post_templates = [
            "Day {day}: Deep diving into {topic} today. The more I learn, the more I realize how much I don't know! 🤯",
            "Just had a breakthrough moment with {technology}! Sometimes stepping away and coming back fresh works wonders. ✨",
            "Weekend coding session: Working on {project}. Nothing beats the satisfaction of clean, working code! 💻",
            "Mentor session today was incredible! Got some great insights on {subject}. Grateful for the guidance! 🙏",
            "Failed fast, learned faster! Today's {mistake} taught me more than any tutorial could. Embrace the bugs! 🐛",
            "Code review feedback: {feedback}. Constructive criticism is a gift! Time to refactor and improve. 🔧",
            "Pair programming session with {partner} was amazing! Two minds definitely better than one. 🧠+🧠",
            "Today I discovered {discovery}. It's like finding a secret weapon in your coding toolkit! ⚔️",
            "Debugging marathon: 4 hours, 1 semicolon. Why do we do this to ourselves? 😅 #DeveloperLife",
            "Just published my {creation} on GitHub! Open source contribution feels so rewarding! 🌟",
            "Morning motivation: {motivation}. Starting the day with purpose and passion! ☀️",
            "Late night coding session yielded {result}. Sometimes the best ideas come after midnight! 🌙",
            "Team standup update: {update}. Love how we support each other through challenges! 👥",
            "Learning {skill} is like solving a puzzle. Each piece makes the whole picture clearer! 🧩",
            "Refactoring old code is therapeutic. Making messy code beautiful one function at a time! ✨",
            "Conference takeaway: {takeaway}. The tech community never stops inspiring me! 🎤",
            "Side project update: {progress}. Slow and steady wins the race! 🐢",
            "Today's win: {win}. Celebrating small victories keeps the momentum going! 🏆",
            "Challenge accepted: {challenge}. Growth happens outside the comfort zone! 💪",
            "Documentation day! Future me will thank present me for these detailed comments. 📝",
            "Testing, testing, 1-2-3! Writing tests isn't glamorous but it's essential. Quality matters! ✅",
            "Performance optimization session: Made the app {improvement}! Every millisecond counts. ⚡",
            "Open source contribution merged! Contributing back to the community feels amazing! 🤝",
            "Learning from failure: {lesson}. Every setback is a setup for a comeback! 🚀",
            "Collaboration win: {collaboration}. Teamwork makes the dream work! 🤜🤛",
            "New tool discovery: {tool}. Always excited to add new weapons to the arsenal! 🛠️",
            "Code kata completed: {kata}. Practice makes perfect, and perfect practice makes permanent! 🥋",
            "Architecture discussion: {discussion}. Love geeking out about system design! 🏗️",
            "Problem-solving mode: {problem}. Breaking down complex issues into manageable chunks! 🧠",
            "Inspiration strikes: {inspiration}. Sometimes the best ideas come from unexpected places! 💡"
        ]
        
        # Enhanced data for more variety
        topics = [
            'microservices architecture', 'GraphQL queries', 'Docker containerization', 
            'Kubernetes orchestration', 'serverless functions', 'database indexing',
            'caching strategies', 'API rate limiting', 'security best practices',
            'performance monitoring', 'CI/CD pipelines', 'infrastructure as code'
        ]
        
        technologies = [
            'React Suspense', 'Vue 3 Composition API', 'Angular Universal', 'Svelte',
            'Next.js', 'Nuxt.js', 'Gatsby', 'FastAPI', 'Express.js', 'Spring Boot',
            'Redis', 'MongoDB', 'PostgreSQL', 'Elasticsearch', 'Terraform', 'Ansible'
        ]
        
        projects = [
            'real-time chat application', 'expense tracking app', 'recipe sharing platform',
            'job board application', 'fitness tracking dashboard', 'event management system',
            'content management system', 'e-learning platform', 'inventory management tool',
            'social media analytics dashboard', 'project management tool', 'booking system'
        ]
        
        subjects = [
            'system design', 'database optimization', 'frontend architecture',
            'backend scalability', 'DevOps practices', 'security protocols',
            'user experience design', 'data structures', 'algorithms',
            'clean code principles', 'testing strategies', 'deployment patterns'
        ]
        
        mistakes = [
            'infinite loop', 'memory leak', 'SQL injection vulnerability',
            'race condition', 'null pointer exception', 'circular dependency',
            'improper error handling', 'performance bottleneck', 'security oversight'
        ]
        
        feedback_items = [
            'Extract this into smaller functions', 'Add error handling here',
            'Consider using design patterns', 'Improve variable naming',
            'Add unit tests for edge cases', 'Optimize this query',
            'Follow single responsibility principle', 'Add proper documentation'
        ]
        
        partners = ['Sarah', 'Mike', 'Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan']
        
        discoveries = [
            'an amazing VS Code extension', 'a powerful debugging technique',
            'a performance optimization trick', 'a useful design pattern',
            'an elegant algorithm', 'a productivity hack', 'a testing framework'
        ]
        
        creations = [
            'utility library', 'React component', 'API wrapper', 'CLI tool',
            'browser extension', 'mobile app', 'web scraper', 'automation script'
        ]
        
        motivations = [
            'Code is poetry in motion', 'Every expert was once a beginner',
            'Progress over perfection', 'Learn, build, repeat',
            'Embrace the journey', 'Code with purpose', 'Innovation through iteration'
        ]
        
        results = [
            'a working prototype', 'a performance breakthrough', 'a clean solution',
            'an elegant algorithm', 'a scalable architecture', 'a bug-free feature'
        ]
        
        updates = [
            'crushed yesterday\'s sprint goals', 'identified a critical bug',
            'completed the integration testing', 'deployed to staging environment',
            'finished the code review', 'updated the documentation'
        ]
        
        skills = [
            'TypeScript', 'Python', 'Go', 'Rust', 'Kotlin', 'Swift',
            'machine learning', 'blockchain development', 'cloud architecture'
        ]
        
        takeaways = [
            'AI is transforming development', 'Community over competition',
            'Accessibility should be a priority', 'Performance matters more than ever',
            'Security is everyone\'s responsibility', 'Documentation is code\'s best friend'
        ]
        
        progress_items = [
            'UI is 80% complete', 'backend API is functional', 'database design is finalized',
            'testing suite is comprehensive', 'deployment pipeline is ready'
        ]
        
        wins = [
            'zero downtime deployment', 'passing all tests', 'positive user feedback',
            'performance improvements', 'successful code review', 'bug-free release'
        ]
        
        challenges = [
            'building without frameworks', 'optimizing for mobile', 'implementing real-time features',
            'scaling to 1M users', 'zero-downtime deployment', 'cross-platform compatibility'
        ]
        
        improvements = [
            '50% faster', '30% more efficient', '90% more reliable',
            '2x more responsive', 'significantly more scalable'
        ]
        
        lessons = [
            'always backup before major changes', 'read error messages carefully',
            'test early and often', 'ask for help sooner', 'document as you go'
        ]
        
        collaborations = [
            'cross-team integration success', 'knowledge sharing session',
            'mentoring junior developers', 'successful project handoff'
        ]
        
        tools = [
            'GitHub Copilot', 'Postman', 'Figma', 'Notion', 'Linear', 'Vercel'
        ]
        
        katas = [
            'FizzBuzz variations', 'Binary search implementation', 'Sorting algorithms',
            'Data structure exercises', 'Algorithm challenges'
        ]
        
        discussions = [
            'monolith vs microservices', 'REST vs GraphQL', 'SQL vs NoSQL',
            'client-side vs server-side rendering', 'stateful vs stateless design'
        ]
        
        problems = [
            'optimizing database queries', 'reducing API response times',
            'improving user experience', 'scaling the architecture'
        ]
        
        inspirations = [
            'a nature walk', 'a conversation with a user', 'a random blog post',
            'a conference talk', 'a coding podcast', 'a team brainstorm'
        ]
        
        posts_created = 0
        
        for i in range(count):
            user = random.choice(users)
            template = random.choice(post_templates)
            
            # Fill template with random data
            post_body = template.format(
                day=random.randint(1, 100),
                topic=random.choice(topics),
                technology=random.choice(technologies),
                project=random.choice(projects),
                subject=random.choice(subjects),
                mistake=random.choice(mistakes),
                feedback=random.choice(feedback_items),
                partner=random.choice(partners),
                discovery=random.choice(discoveries),
                creation=random.choice(creations),
                motivation=random.choice(motivations),
                result=random.choice(results),
                update=random.choice(updates),
                skill=random.choice(skills),
                takeaway=random.choice(takeaways),
                progress=random.choice(progress_items),
                win=random.choice(wins),
                challenge=random.choice(challenges),
                improvement=random.choice(improvements),
                lesson=random.choice(lessons),
                collaboration=random.choice(collaborations),
                tool=random.choice(tools),
                kata=random.choice(katas),
                discussion=random.choice(discussions),
                problem=random.choice(problems),
                inspiration=random.choice(inspirations)
            )
            
            # Create post with random timestamp in the last 7 days for freshness
            random_date = timezone.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            post = Post.objects.create(
                body=post_body,
                created_by=user,
                likes_count=random.randint(0, 10),  # Start with some likes
                comments_count=0
            )
            
            # Update the created_at field manually
            post.created_at = random_date
            post.save()
            
            # Update user's post count
            user.posts_count += 1
            user.save()
            
            posts_created += 1
            
            if posts_created % 10 == 0:
                self.stdout.write(f'Created {posts_created} additional posts...')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {posts_created} new posts!')
        )
