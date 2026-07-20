from datetime import date

from django.core.management.base import BaseCommand

from catalog.models import Author, Book, Category


class Command(BaseCommand):
    help = "Seed fictional catalog data for local demos and portfolio screenshots."

    def handle(self, *args, **options):
        categories = {
            "theology": "Theology",
            "devotional": "Devotional",
            "biography": "Biography",
            "church": "Church Life",
        }
        for slug, name in categories.items():
            Category.objects.get_or_create(slug=slug, defaults={"name": name})

        authors_data = [
            ("elena-marks", "Elena Marks", "Pastor and writer focused on grace and everyday discipleship."),
            ("samuel-reed", "Samuel Reed", "Teacher who writes short books for small groups."),
            ("mira-cole", "Mira Cole", "Author of devotionals for busy families."),
            ("jonah-west", "Jonah West", "Biographer of lesser-known missionaries."),
        ]
        for slug, name, bio in authors_data:
            Author.objects.get_or_create(slug=slug, defaults={"name": name, "bio": bio})

        books = [
            {
                "title": "Grace and Truth",
                "slug": "grace-and-truth",
                "subtitle": "Holding both without losing either",
                "description": "A clear, pastoral look at how grace and truth belong together in the Christian life.",
                "category": "theology",
                "authors": ["elena-marks"],
                "is_featured": True,
                "published_date": date(2022, 3, 1),
                "isbn": "9780000000001",
            },
            {
                "title": "Morning Light",
                "slug": "morning-light",
                "subtitle": "Thirty short readings for ordinary days",
                "description": "Brief daily reflections that point back to the gospel without noise or hype.",
                "category": "devotional",
                "authors": ["mira-cole"],
                "is_featured": True,
                "published_date": date(2023, 1, 15),
                "isbn": "9780000000002",
            },
            {
                "title": "The Quiet Congregation",
                "slug": "the-quiet-congregation",
                "subtitle": "Faithfulness in small churches",
                "description": "Encouragement for pastors and members who serve outside the spotlight.",
                "category": "church",
                "authors": ["samuel-reed"],
                "is_featured": True,
                "published_date": date(2021, 9, 10),
                "isbn": "9780000000003",
            },
            {
                "title": "Letters from the Road",
                "slug": "letters-from-the-road",
                "subtitle": "A missionary’s unfinished story",
                "description": "A biographical sketch drawn from letters, journals, and the people who walked beside him.",
                "category": "biography",
                "authors": ["jonah-west"],
                "is_featured": False,
                "published_date": date(2020, 6, 20),
                "isbn": "9780000000004",
            },
            {
                "title": "Rooted Words",
                "slug": "rooted-words",
                "subtitle": "Scripture habits that last",
                "description": "Practical patterns for reading, memorizing, and meditating on Scripture over years—not weeks.",
                "category": "theology",
                "authors": ["elena-marks", "samuel-reed"],
                "is_featured": False,
                "published_date": date(2024, 2, 5),
                "isbn": "9780000000005",
            },
            {
                "title": "Table Grace",
                "slug": "table-grace",
                "subtitle": "Family worship for real kitchens",
                "description": "Simple outlines and prayers for households that want to gather around the Word without perfectionism.",
                "category": "devotional",
                "authors": ["mira-cole"],
                "is_featured": True,
                "published_date": date(2023, 11, 1),
                "isbn": "9780000000006",
            },
            {
                "title": "Under Ordinary Skies",
                "slug": "under-ordinary-skies",
                "subtitle": "Hope for long seasons",
                "description": "A gentle book for believers walking through waiting, illness, or unanswered prayer.",
                "category": "devotional",
                "authors": ["elena-marks"],
                "is_featured": False,
                "published_date": date(2019, 4, 12),
                "isbn": "9780000000007",
            },
            {
                "title": "Shepherds Among Us",
                "slug": "shepherds-among-us",
                "subtitle": "What local pastors actually do",
                "description": "A candid portrait of pastoral work—preaching, visiting, and patient presence.",
                "category": "church",
                "authors": ["samuel-reed", "jonah-west"],
                "is_featured": False,
                "published_date": date(2022, 8, 18),
                "isbn": "9780000000008",
            },
            {
                "title": "Alpha",
                "slug": "alpha-study-notes",
                "subtitle": "Starter notes for new believers",
                "description": "Short chapters that answer first questions about the gospel, church, and Christian hope.",
                "category": "theology",
                "authors": ["samuel-reed"],
                "is_featured": False,
                "published_date": date(2018, 1, 1),
                "isbn": "9780000000009",
            },
            {
                "title": "Across the River",
                "slug": "across-the-river",
                "subtitle": "Two sisters, one calling",
                "description": "A dual biography of two women who served neighboring towns with quiet courage.",
                "category": "biography",
                "authors": ["jonah-west"],
                "is_featured": True,
                "published_date": date(2024, 5, 22),
                "isbn": "9780000000010",
            },
        ]

        created = 0
        for item in books:
            category = Category.objects.get(slug=item["category"])
            book, was_created = Book.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "subtitle": item["subtitle"],
                    "description": item["description"],
                    "category": category,
                    "is_featured": item["is_featured"],
                    "published_date": item["published_date"],
                    "isbn": item["isbn"],
                },
            )
            author_objs = [Author.objects.get(slug=s) for s in item["authors"]]
            book.authors.set(author_objs)
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded catalog: {Book.objects.count()} books "
                f"({created} newly created)."
            )
        )
