from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import get_user_model

from .models import StaffProfile

User = get_user_model()


@dataclass(frozen=True)
class StaffAccess:
    can_manage_books: bool = False
    can_manage_authors: bool = False
    can_manage_categories: bool = False
    can_view_saved: bool = False
    can_manage_team: bool = False

    @property
    def can_open_manage(self) -> bool:
        return any(
            (
                self.can_manage_books,
                self.can_manage_authors,
                self.can_manage_categories,
                self.can_view_saved,
                self.can_manage_team,
            )
        )


def ensure_staff_profile(user) -> StaffProfile:
    profile, _ = StaffProfile.objects.get_or_create(
        user=user,
        defaults={
            "can_manage_books": True,
            "can_manage_authors": True,
            "can_manage_categories": True,
            "can_view_saved": True,
            "can_manage_team": user.is_superuser,
        },
    )
    return profile


def get_staff_access(user) -> StaffAccess:
    if not user.is_authenticated or not user.is_staff:
        return StaffAccess()
    if user.is_superuser:
        return StaffAccess(
            can_manage_books=True,
            can_manage_authors=True,
            can_manage_categories=True,
            can_view_saved=True,
            can_manage_team=True,
        )
    profile = ensure_staff_profile(user)
    return StaffAccess(
        can_manage_books=profile.can_manage_books,
        can_manage_authors=profile.can_manage_authors,
        can_manage_categories=profile.can_manage_categories,
        can_view_saved=profile.can_view_saved,
        can_manage_team=profile.can_manage_team,
    )
