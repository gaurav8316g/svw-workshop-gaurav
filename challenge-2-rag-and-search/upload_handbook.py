"""Create a Vertex AI RAG corpus and upload the Harbor Bites handbook.

Prints the corpus resource name. Put that value in RAG_CORPUS.

    python challenge-2-rag-and-search/upload_handbook.py

Requires Application Default Credentials and:

    pip install google-cloud-aiplatform
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HANDBOOK = Path(__file__).resolve().parent / "harbor_bites_employee_handbook.md"


def main() -> None:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    if not project:
        sys.exit("Set GOOGLE_CLOUD_PROJECT before uploading the handbook.")
    if not HANDBOOK.is_file():
        sys.exit(f"Handbook file is missing: {HANDBOOK}")

    try:
        import vertexai
        from vertexai import rag
    except ImportError:
        sys.exit(
            "google-cloud-aiplatform is not installed. "
            "Run: pip install google-cloud-aiplatform"
        )

    vertexai.init(project=project, location=location)
    corpus = rag.create_corpus(display_name="harbor-bites-handbook")
    rag.upload_file(
        corpus.name,
        str(HANDBOOK),
        display_name="harbor-bites-employee-handbook",
    )
    print(corpus.name)
    print("Set RAG_CORPUS to the resource name above.")


if __name__ == "__main__":
    main()
