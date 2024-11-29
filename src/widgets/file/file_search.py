import os
import ctypes
import datetime as dt
from typing import Final, Generator, Optional
from enum import Enum, IntEnum
from ctypes.wintypes import *
from struct import calcsize, unpack

# Constants
MAX_PATH: Final = 32767


class Request(IntEnum):
    """Flags for specifying the type of data to request from Everything."""
    FileName = 0x00000001
    Path = 0x00000002
    FullPathAndFileName = 0x00000004
    Extension = 0x00000008
    Size = 0x00000010
    DateCreated = 0x00000020
    DateModified = 0x00000040
    DateAccessed = 0x00000080
    Attributes = 0x00000100
    FileListFileName = 0x00000200
    RunCount = 0x00000400
    DateRun = 0x00000800
    DateRecentlyChanged = 0x00001000
    HighlightedFileName = 0x00002000
    HighlightedPath = 0x00004000
    HighlightedFullPathAndFileName = 0x00008000
    All = 0x0000FFFF


class Error(Enum):
    """Error codes for Everything API operations."""
    Ok = 0
    Memory = 1
    IPC = 2
    RegisterClassEx = 3
    CreateWindow = 4
    CreateThread = 5
    InvalidIndex = 6
    InvalidCall = 7


class ItemIterator:
    """Iterator for handling Everything API results."""
    def __init__(self, everything, index: int) -> None:
        self.everything = everything
        self.index = index

    def __next__(self):
        self.index += 1
        if self.index < len(self.everything):
            return self
        raise StopIteration

    def __str__(self) -> str:
        return self.get_filename()

    def get_filename(self) -> Optional[str]:
        """
        Get the full path and file name of the current result.

        Returns:
            str: Full path and file name if successful, None otherwise.
        """
        filename = ctypes.create_unicode_buffer(MAX_PATH)
        if self.everything.GetResultFullPathNameW(self.index, filename, MAX_PATH):
            return filename.value
        return None

    def get_size(self) -> Optional[int]:
        """
        Get the size of the current result.

        Returns:
            int: Size in bytes if successful, None otherwise.
        """
        file_size = ULARGE_INTEGER()
        if self.everything.GetResultSize(self.index, file_size):
            return file_size.value
        return None

    def _get_result_date(self, tdate: str) -> Optional[dt.datetime]:
        """
        Get a specific date field for the current result.

        Args:
            tdate (str): Type of date to retrieve (e.g., 'Accessed').

        Returns:
            datetime: Date as a datetime object if successful, None otherwise.
        """
        filetime_date = ULARGE_INTEGER()
        if self.everything(f'GetResultDate{tdate}', self.index, filetime_date):
            winticks = int(unpack('<Q', filetime_date)[0])
            return dt.datetime.fromtimestamp((winticks - 116444736000000000) / 10000000)
        return None

    def get_date_accessed(self) -> Optional[dt.datetime]:
        """Get the accessed date of the current result."""
        return self._get_result_date('Accessed')

    def get_date_created(self) -> Optional[dt.datetime]:
        """Get the created date of the current result."""
        return self._get_result_date('Created')

    def get_date_modified(self) -> Optional[dt.datetime]:
        """Get the modified date of the current result."""
        return self._get_result_date('Modified')

    def is_file(self) -> bool:
        """Check if the current result is a file."""
        return bool(self.everything.IsFileResult(self.index))

    def is_folder(self) -> bool:
        """Check if the current result is a folder."""
        return bool(self.everything.IsFolderResult(self.index))


class Everything:
    """Wrapper for the Everything SDK."""
    def __init__(self, dll: Optional[str] = None) -> None:
        """
        Initialize and load the Everything library.

        Args:
            dll (str, optional): Path to the Everything DLL. Defaults to auto-detect.
        """
        dll = dll or rf'..\src\dll\FileSearchx{8 * calcsize("P")}.dll'
        self.dll = ctypes.WinDLL(dll)

        # Define functions
        self.func(BOOL, 'QueryW', BOOL)
        self.func(None, 'SetSearchW', LPCWSTR)
        self.func(None, 'SetRegex', BOOL)
        self.func(None, 'SetRequestFlags', DWORD)
        self.func(DWORD, 'GetResultListRequestFlags')
        self.func(DWORD, 'GetResultFullPathNameW', DWORD, LPWSTR, DWORD)
        self.func(DWORD, 'GetNumResults')
        self.func(BOOL, 'GetResultSize', DWORD, PULARGE_INTEGER)
        self.func(BOOL, 'IsFileResult', DWORD)
        self.func(BOOL, 'IsFolderResult', DWORD)
        self.func(DWORD, 'GetLastError')

    def __len__(self) -> int:
        """Get the number of visible file and folder results."""
        return self.GetNumResults()

    def __getitem__(self, item: int) -> ItemIterator:
        """Get a specific result by index."""
        if not (0 <= item < len(self)):
            raise IndexError("Index out of range")
        return ItemIterator(self, item)

    def __getattr__(self, item):
        return getattr(self.dll, f'Everything_{item}')

    def __call__(self, name: str, *args):
        return getattr(self.dll, f'Everything_{name}')(*args)

    def __iter__(self):
        return ItemIterator(self, -1)

    def func(self, restype, name: str, *argtypes) -> None:
        """Define a function from the Everything DLL."""
        func = getattr(self.dll, f'Everything_{name}')
        func.restype = restype
        func.argtypes = tuple(argtypes)

    def query(self, wait: bool = True) -> bool:
        """Execute an Everything IPC query."""
        return bool(self.QueryW(wait))

    def set_search(self, string: str) -> None:
        """Set the search string for the query."""
        self.SetSearchW(string)

    def set_regex(self, enabled: bool) -> None:
        """Enable or disable regex searching."""
        self.SetRegex(enabled)

    def set_request_flags(self, flags: Request) -> None:
        """Set the desired result data."""
        self.SetRequestFlags(flags)

    def get_last_error(self) -> Error:
        """Get the last error code."""
        return Error(self.GetLastError())


def file_search(directory: str, filename: str) -> Generator[str, None, None]:
    """
    Search for a file in a directory using the Everything SDK.

    Args:
        directory (str): Directory path to search in.
        filename (str): Filename to search for.

    Yields:
        str: Full paths of matching files.
    """
    everything = Everything()
    everything.set_search(fr"path:{directory}\ {filename}")
    everything.set_request_flags(Request.FullPathAndFileName | Request.DateModified | Request.Size)

    if not everything.query():
        raise Exception(everything.get_last_error())

    for item in everything:
        yield item.get_filename()
