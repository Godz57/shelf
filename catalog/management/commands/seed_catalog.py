from datetime import date

from django.core.management.base import BaseCommand

from catalog.models import Author, Book, Category

# Free Unsplash photos (stable IDs). Stock imagery for fictional titles —
# not real publisher product covers.
def _cover(photo_id: str) -> str:
    return (
        f"https://images.unsplash.com/{photo_id}"
        f"?auto=format&fit=crop&w=600&h=900&q=80"
    )


COVERS = {
    "grace-and-truth": _cover("photo-1544947950-fa07a98d237f"),  # classic book
    "morning-light": _cover("photo-1470252649378-9c29740c9fa8"),  # sunrise
    "the-quiet-congregation": _cover("photo-1438032005730-c779502df39b"),  # church interior
    "letters-from-the-road": _cover("photo-1469854523086-cc02fe5d8800"),  # travel road
    "rooted-words": _cover("photo-1504052434569-70ad5836ab65"),  # open scripture-style
    "table-grace": _cover("photo-1511688878353-3a2f5be94cd7"),  # table / meal
    "under-ordinary-skies": _cover("photo-1506905925346-21bda4d32df4"),  # mountains sky
    "shepherds-among-us": _cover("photo-1529070538774-1843cb3265df"),  # gathering
    "alpha-study-notes": _cover("photo-1481627834876-b7833e8f5570"),  # library books
    "across-the-river": _cover("photo-1501785888041-af3ef285b470"),  # river landscape
    "bread-for-the-week": _cover("photo-1509440159596-0249088772ff"),  # bread
    "small-prayers": _cover("photo-1490730141103-6cac27aaab94"),  # sky light
    "field-notes-on-hope": _cover("photo-1441974231531-c6227db76b6e"),  # forest path
    "the-long-obedience": _cover("photo-1469474968028-56623f02e42e"),  # nature path
    "neighbor-love": _cover("photo-1469571486292-0ba58a3f068b"),  # community
    "songs-at-midnight": _cover("photo-1419242902214-272b3f66ee7a"),  # night sky
    "wisdom-for-work": _cover("photo-1497215728101-856f4ea42174"),  # desk work
    "a-quiet-yes": _cover("photo-1470071459604-3b5ec3a7fe05"),  # fog hills
}


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
            (
                "elena-marks",
                "Elena Marks",
                "Pastor and writer focused on grace and everyday discipleship.",
            ),
            (
                "samuel-reed",
                "Samuel Reed",
                "Teacher who writes short books for small groups.",
            ),
            (
                "mira-cole",
                "Mira Cole",
                "Author of devotionals for busy families.",
            ),
            (
                "jonah-west",
                "Jonah West",
                "Biographer of lesser-known missionaries.",
            ),
            (
                "ruth-hale",
                "Ruth Hale",
                "Writer on prayer, vocation, and ordinary faithfulness.",
            ),
            (
                "caleb-orin",
                "Caleb Orin",
                "Former campus minister; now writes for workers and students.",
            ),
        ]
        for slug, name, bio in authors_data:
            Author.objects.get_or_create(slug=slug, defaults={"name": name, "bio": bio})

        books = [
            {
                "title": "Grace and Truth",
                "slug": "grace-and-truth",
                "subtitle": "Holding both without losing either",
                "description": (
                    "A clear, pastoral look at how grace and truth belong together "
                    "in the Christian life."
                ),
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
                "description": (
                    "Brief daily reflections that point back to the gospel "
                    "without noise or hype."
                ),
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
                "description": (
                    "Encouragement for pastors and members who serve outside "
                    "the spotlight."
                ),
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
                "description": (
                    "A biographical sketch drawn from letters, journals, and the "
                    "people who walked beside him."
                ),
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
                "description": (
                    "Practical patterns for reading, memorizing, and meditating on "
                    "Scripture over years—not weeks."
                ),
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
                "description": (
                    "Simple outlines and prayers for households that want to gather "
                    "around the Word without perfectionism."
                ),
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
                "description": (
                    "A gentle book for believers walking through waiting, illness, "
                    "or unanswered prayer."
                ),
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
                "description": (
                    "A candid portrait of pastoral work—preaching, visiting, "
                    "and patient presence."
                ),
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
                "description": (
                    "Short chapters that answer first questions about the gospel, "
                    "church, and Christian hope."
                ),
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
                "description": (
                    "A dual biography of two women who served neighboring towns "
                    "with quiet courage."
                ),
                "category": "biography",
                "authors": ["jonah-west"],
                "is_featured": True,
                "published_date": date(2024, 5, 22),
                "isbn": "9780000000010",
            },
            {
                "title": "Bread for the Week",
                "slug": "bread-for-the-week",
                "subtitle": "Seven gospel meditations",
                "description": (
                    "A week of short readings that return to Christ as daily bread — "
                    "for people who open a book between tasks."
                ),
                "category": "devotional",
                "authors": ["ruth-hale"],
                "is_featured": True,
                "published_date": date(2024, 9, 3),
                "isbn": "9780000000011",
            },
            {
                "title": "Small Prayers",
                "slug": "small-prayers",
                "subtitle": "Words when you have few",
                "description": (
                    "Honest prayers for anxiety, gratitude, grief, and ordinary mornings."
                ),
                "category": "devotional",
                "authors": ["ruth-hale", "mira-cole"],
                "is_featured": False,
                "published_date": date(2023, 4, 18),
                "isbn": "9780000000012",
            },
            {
                "title": "Field Notes on Hope",
                "slug": "field-notes-on-hope",
                "subtitle": "Learning to wait well",
                "description": (
                    "Essays that refuse cheap optimism and point to a living hope."
                ),
                "category": "theology",
                "authors": ["caleb-orin"],
                "is_featured": True,
                "published_date": date(2022, 11, 8),
                "isbn": "9780000000013",
            },
            {
                "title": "The Long Obedience",
                "slug": "the-long-obedience",
                "subtitle": "Discipleship without shortcuts",
                "description": (
                    "A pastoral call to steady growth in a culture of instant results."
                ),
                "category": "theology",
                "authors": ["elena-marks", "caleb-orin"],
                "is_featured": False,
                "published_date": date(2021, 2, 14),
                "isbn": "9780000000014",
            },
            {
                "title": "Neighbor Love",
                "slug": "neighbor-love",
                "subtitle": "Mercy on your street",
                "description": (
                    "Stories and practices for churches that want to love the people "
                    "they actually live beside."
                ),
                "category": "church",
                "authors": ["samuel-reed", "ruth-hale"],
                "is_featured": False,
                "published_date": date(2020, 10, 2),
                "isbn": "9780000000015",
            },
            {
                "title": "Songs at Midnight",
                "slug": "songs-at-midnight",
                "subtitle": "Faith when joy is thin",
                "description": (
                    "A biography-shaped meditation on lament, psalms, and endurance."
                ),
                "category": "biography",
                "authors": ["jonah-west", "elena-marks"],
                "is_featured": False,
                "published_date": date(2019, 7, 30),
                "isbn": "9780000000016",
            },
            {
                "title": "Wisdom for Work",
                "slug": "wisdom-for-work",
                "subtitle": "Calling in ordinary jobs",
                "description": (
                    "For students and workers who want their weekday labor connected "
                    "to the gospel without slogans."
                ),
                "category": "theology",
                "authors": ["caleb-orin"],
                "is_featured": True,
                "published_date": date(2024, 1, 9),
                "isbn": "9780000000017",
            },
            {
                "title": "A Quiet Yes",
                "slug": "a-quiet-yes",
                "subtitle": "Saying yes to small faithfulness",
                "description": (
                    "Devotional essays for people who will never trend — and still "
                    "want to follow Christ."
                ),
                "category": "devotional",
                "authors": ["mira-cole", "ruth-hale"],
                "is_featured": False,
                "published_date": date(2025, 3, 1),
                "isbn": "9780000000018",
            },
        ]

        created = 0
        updated = 0
        for item in books:
            category = Category.objects.get(slug=item["category"])
            cover_url = COVERS.get(item["slug"], "")
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
                    "cover_url": cover_url,
                },
            )
            author_objs = [Author.objects.get(slug=s) for s in item["authors"]]
            book.authors.set(author_objs)

            # Keep seed re-runnable: refresh covers and display fields on existing rows.
            changed = False
            for field, value in {
                "title": item["title"],
                "subtitle": item["subtitle"],
                "description": item["description"],
                "category": category,
                "is_featured": item["is_featured"],
                "published_date": item["published_date"],
                "isbn": item["isbn"],
                "cover_url": cover_url,
            }.items():
                if getattr(book, field) != value:
                    setattr(book, field, value)
                    changed = True
            if changed and not was_created:
                book.save()
                updated += 1
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded catalog: {Book.objects.count()} books "
                f"({created} created, {updated} updated). "
                f"Covers set: {Book.objects.exclude(cover_url='').count()}."
            )
        )
