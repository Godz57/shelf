from rest_framework.routers import DefaultRouter

from .api import BookViewSet

router = DefaultRouter()
router.register("books", BookViewSet, basename="api-book")

urlpatterns = router.urls
