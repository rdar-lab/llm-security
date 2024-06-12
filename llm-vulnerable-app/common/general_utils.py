import os
from typing import Optional

_project_root = None


def get_project_root():
    global _project_root
    if _project_root is None:
        curr: Optional[str] = os.getcwd()
        while curr is not None and not os.path.exists(os.path.join(curr, "ROOT")):
            parent = os.path.dirname(curr)
            if parent == curr:
                curr = None
            else:
                curr = parent

        if curr is None:
            raise Exception("Was unable to detect project root")
        _project_root = curr

    return _project_root
