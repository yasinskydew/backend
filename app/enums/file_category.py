from enum import StrEnum


class FileCategory(StrEnum):
    """Logical storage category used as the object-key prefix."""

    RECIPES = "recipes"
    AVATARS = "avatars"
    GENERAL = "general"
    CATEGORIES = "categories"
