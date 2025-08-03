"""Django management command that updates filenames of image files.

```
python manage.py update_filenames  [--dry-run]
```

* Generates canonical filenames for every `Metadata` record that has **both**
  title and author.
* Moves the underlying file in `MEDIA_ROOT/images/` (resolves name clashes by
  appending `(1)`, `(2)`, ...).
* Updates the model's `filename` field accordingly.
* Outputs a summary table.
"""
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from visor.models.metadata import Metadata

IMAGE_FOLDER = Path(settings.MEDIA_ROOT)


class Command(BaseCommand):
    help = "Rename image files according to title/author metadata."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", help="Show changes but don't move files"
        )

    @transaction.atomic
    def handle(self, *args, dry_run: bool, **options):
        moved, skipped = 0, 0
        for meta in Metadata.objects.all():
            if not (meta.title and meta.author):
                skipped += 1
                continue
            new_base = self.generate_filename(meta)
            if not new_base or new_base == meta.filename:
                skipped += 1
                continue
            old_path = IMAGE_FOLDER / meta.filename
            if not old_path.exists():
                self.stderr.write(f"⚠️  File missing: {old_path}")
                skipped += 1
                continue
            new_name = f"{self.sanitize(new_base)}{old_path.suffix}"
            counter = 1
            while (IMAGE_FOLDER / new_name).exists():
                new_name = f"{self.sanitize(new_base)} ({counter}){old_path.suffix}"
                counter += 1
            if dry_run:
                self.stdout.write(f"DRY-RUN  {meta.filename}  →  {new_name}")
            else:
                shutil.move(old_path, IMAGE_FOLDER / new_name)
                meta.filename = new_name
                meta.save(update_fields=["filename"])
                self.stdout.write(f"✅  {meta.filename}  →  {new_name}")
                moved += 1
        self.stdout.write(self.style.SUCCESS(f"Finished. Moved {moved}, skipped {skipped}."))

    def sanitize(self, s: str) -> str:
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_.,()")
        return "".join(c for c in s if c in valid_chars)

    def split_author(self, author: str) -> tuple[str, str]:
        parts = author.strip().split(" ", 1)
        return (parts[1], parts[0]) if len(parts) == 2 else (parts[0], "")

    def generate_filename(self, meta: Metadata) -> str:
        if not (meta.title and meta.author):
            return meta.filename

        surname, firstname = self.split_author(meta.author)
        base = f"{surname}, {firstname} - {meta.title}"
        if meta.year:
            base += f" ({meta.year})"
        return self.sanitize(base)
