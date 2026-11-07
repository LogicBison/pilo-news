"""Write the committed OpenAPI snapshot used by the contract CI gate."""

from __future__ import annotations

import json
import os
from pathlib import Path

from news_api.main import app

_HERE = Path(__file__).resolve()
# In the container the app is mounted at /app, so the repo root is not three
# levels up; CI and the host checkout are. OPENAPI_OUTPUT wins when set, which
# is how the container writes the snapshot back to the mount.
REPO_ROOT = _HERE.parents[3] if len(_HERE.parents) > 3 else _HERE.parents[1]
OUTPUT = Path(os.environ.get("OPENAPI_OUTPUT") or REPO_ROOT / "docs" / "api" / "openapi.v1.json")


def main() -> None:
    schema = app.openapi()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
