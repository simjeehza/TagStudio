from pathlib import Path

from tagstudio.core.library.alchemy.models import Entry
from tagstudio.core.utils.dupe_files import DupeRegistry

CWD = Path(__file__).parent


def test_refresh_dupe_files(library):
    library.library_dir = "/tmp/"
    entry = Entry(
        folder=library.folder,
        path=Path("bar/foo.txt"),
        fields=library.default_fields,
    )

    entry2 = Entry(
        folder=library.folder,
        path=Path("foo/foo.txt"),
        fields=library.default_fields,
    )

    library.add_entries([entry, entry2])

    registry = DupeRegistry(library=library)

    dupe_file_path = CWD.parent / "fixtures" / "result.dupeguru"
    registry.refresh_dupe_files(dupe_file_path)

    assert len(registry.groups) == 1
    paths = [entry.path for entry in registry.groups[0]]
    assert paths == [
        Path("bar/foo.txt"),
        Path("foo.txt"),
        Path("foo/foo.txt"),
    ]
