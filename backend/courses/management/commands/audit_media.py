"""Report missing and unreferenced media without deleting anything."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from scenarios.models import Step

from courses.models import Course, Material


class Command(BaseCommand):
    help = "Report missing and unreferenced files in private storage (read-only)."

    def handle(self, *args, **options):
        referenced = set()
        for model, field in [(Course, "cover"), (Material, "file"), (Step, "image")]:
            referenced.update(name for name in model.objects.values_list(field, flat=True) if name)
        media_root = Path(settings.MEDIA_ROOT)
        missing = [name for name in referenced if not (media_root / name).is_file()]
        expected = set(referenced)
        for name in referenced:
            if name.endswith(".mp4"):
                expected.add(str(Path(name).with_suffix(".vtt")))
        files = {
            str(path.relative_to(media_root)) for path in media_root.rglob("*") if path.is_file()
        }
        unused = sorted(files - expected - {"legacy/web.config"})
        self.stdout.write(
            f"Referenced files: {len(referenced)}; missing: {len(missing)}; unreferenced: {len(unused)}"
        )
        for name in sorted(missing):
            self.stdout.write(f"MISSING: {name}")
        for name in unused:
            self.stdout.write(f"UNREFERENCED: {name}")
