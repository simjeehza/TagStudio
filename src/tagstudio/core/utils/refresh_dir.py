from datetime import datetime as dt
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from time import time
import platform

import structlog
from tagstudio.core.constants import TS_FOLDER_NAME
from tagstudio.core.library.alchemy.library import Library
from tagstudio.core.library.alchemy.models import Entry

logger = structlog.get_logger(__name__)

GLOBAL_IGNORE_SET: set[str] = set(
    [
        TS_FOLDER_NAME,
        "$RECYCLE.BIN",
        ".Trashes",
        ".Trash",
        "tagstudio_thumbs",
        ".fseventsd",
        ".Spotlight-V100",
        "System Volume Information",
        ".DS_Store",
    ]
)


@dataclass
class RefreshDirTracker:
    library: Library
    files_not_in_library: list[Path] = field(default_factory=list)

    @property
    def files_count(self) -> int:
        return len(self.files_not_in_library)

<<<<<<< HEAD:src/tagstudio/core/utils/refresh_dir.py
    # moving get_file_times to library to avoid circular import
=======
>>>>>>> 8f17c362203a368c5860599b75c2e89e6c8c1fc5:tagstudio/src/core/utils/refresh_dir.py
    def get_file_times(self, file_path: Path):
        """Get the creation and modification times of a file."""
        stat = file_path.stat()
        system = platform.system()
<<<<<<< HEAD:src/tagstudio/core/utils/refresh_dir.py

        # st_birthtime on Windows and Mac, st_ctime on Linux.
        if system in ['Windows', 'Darwin']:  # Windows & macOS
            date_created = dt.datetime.fromtimestamp(stat.st_birthtime)
        else:  # Linux
            date_created = dt.datetime.fromtimestamp(stat.st_ctime)  # Linux lacks st_birthtime

        date_modified = dt.datetime.fromtimestamp(stat.st_mtime)
=======
        if system == 'Windows':  # Windows
            date_created = dt.fromtimestamp(stat.st_ctime, dt.timezone.utc)
        elif system == 'Darwin':  # macOS
            date_created = dt.fromtimestamp(stat.st_birthtime, dt.timezone.utc)
        else:  # Linux and other systems
            try:
                date_created = dt.fromtimestamp(stat.st_birthtime, dt.timezone.utc)
            except AttributeError:
                # st_birthtime is not available on some Linux filesystems
                date_created = dt.fromtimestamp(stat.st_ctime, dt.timezone.utc)
        date_modified = dt.fromtimestamp(stat.st_mtime, dt.timezone.utc)
>>>>>>> 8f17c362203a368c5860599b75c2e89e6c8c1fc5:tagstudio/src/core/utils/refresh_dir.py
        return date_created, date_modified

    def save_new_files(self):
        """Save the list of files that are not in the library."""
        if self.files_not_in_library:
<<<<<<< HEAD:src/tagstudio/core/utils/refresh_dir.py
            entries = [
                Entry(
                    path=entry_path,
                    folder=self.library.folder,
                    fields=[],
                    date_added=dt.datetime.now(),
                    date_created=date_created,
                    date_modified=date_modified,
                )
                for entry_path in self.files_not_in_library
                if (date_created := self.get_file_times(entry_path)[0]) is not None
                and (date_modified := self.get_file_times(entry_path)[1]) is not None
            ]
=======
            entries = []
            for entry_path in self.files_not_in_library:
                date_created, date_modified = self.get_file_times(entry_path)
                if date_created is None or date_modified is None:
                    continue  # Skip files that could not be processed
                entries.append(
                    Entry(
                        path=entry_path,
                        folder=self.library.folder,
                        fields=[],
                        date_added=dt.now(),
                        date_created=dt.now(),
                        date_modified=dt.now(),
                    )
                )
>>>>>>> 8f17c362203a368c5860599b75c2e89e6c8c1fc5:tagstudio/src/core/utils/refresh_dir.py
            self.library.add_entries(entries)

        self.files_not_in_library = []

        yield

    def refresh_dir(self, lib_path: Path) -> Iterator[int]:
        """Scan a directory for files, and add those relative filenames to internal variables."""
        if self.library.library_dir is None:
            raise ValueError("No library directory set.")

        start_time_total = time()
        start_time_loop = time()

        self.files_not_in_library = []
        dir_file_count = 0

        for f in lib_path.glob("**/*"):
            end_time_loop = time()
            # Yield output every 1/30 of a second
            if (end_time_loop - start_time_loop) > 0.034:
                yield dir_file_count
                start_time_loop = time()

            # Skip if the file/path is already mapped in the Library
            if f in self.library.included_files:
                dir_file_count += 1
                continue

            # Ignore if the file is a directory
            if f.is_dir():
                continue

            # Ensure new file isn't in a globally ignored folder
            skip: bool = False
            for part in f.parts:
                # NOTE: Files starting with "._" are sometimes generated by macOS Finder.
                # More info: https://lists.apple.com/archives/applescript-users/2006/Jun/msg00180.html
                if part.startswith("._") or part in GLOBAL_IGNORE_SET:
                    skip = True
                    break
            if skip:
                continue

            dir_file_count += 1
            self.library.included_files.add(f)

            relative_path = f.relative_to(lib_path)
            # TODO - load these in batch somehow
            if not self.library.has_path_entry(relative_path):
<<<<<<< HEAD:src/tagstudio/core/utils/refresh_dir.py
                self.files_not_in_library.append(f)
=======
                self.files_not_in_library.append(relative_path)
            else:
                # Update date_modified for existing entries if it has changed
                entry = self.library.get_entry_by_path(relative_path)
                if entry:
                    date_modified = dt.fromtimestamp(f.stat().st_mtime, dt.timezone.utc)
                    if entry.date_modified != date_modified:
                        entry.date_modified = date_modified
                        self.library.update_entry(entry)
>>>>>>> 8f17c362203a368c5860599b75c2e89e6c8c1fc5:tagstudio/src/core/utils/refresh_dir.py

        end_time_total = time()
        yield dir_file_count
        logger.info(
            "Directory scan time",
            path=lib_path,
            duration=(end_time_total - start_time_total),
            files_not_in_lib=self.files_not_in_library,
            files_scanned=dir_file_count,
        )
