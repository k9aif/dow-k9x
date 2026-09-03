"""
Seeds K9Retriever's pgvector-backed knowledge corpus with synthetic,
non-sensitive DoDAF/acquisition reference material (data/synthetic_corpus/).

This closes the empty-retriever gap disclosed in the IEEE Access manuscript
(Section VI, "Context Enrichment and Retrieval"): "This proof-of-concept has
no such data sources configured... A planned next step is to populate this
retriever with synthetic, non-sensitive corpus data." Real DoW corpus data
is still not available for this proof-of-concept; every document here is
fictional (see data/synthetic_corpus/README.md).

Chunks each source file on "## " section headers (each section keeps its
own heading for retrieval context) rather than an arbitrary character
count, since these are hand-authored reference documents with meaningful
section boundaries.

Run: PYTHONPATH=src python3 experiments/seed_synthetic_corpus.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# config_loader.py's own load_dotenv() call resolves relative to wherever
# that module is defined (inside k9-aif-framework), not relative to this
# script's repo -- so it silently misses dow-k9-aif/.env when this file is
# run directly, leaving OLLAMA_HOST etc. unset and falling back to
# localhost. Load it explicitly, with an explicit path, before anything else.
from dotenv import load_dotenv
load_dotenv(dotenv_path=ROOT / ".env")

from k9_aif_abb.k9_utils.config_loader import load_yaml
from k9_aif_abb.k9_data.retrieval.k9_retriever import K9Retriever

CONFIG_PATH = ROOT / "src/k9_dow/config/config.yaml"
CORPUS_DIR = ROOT / "data/synthetic_corpus"


def chunk_by_section(text: str, filename: str) -> list[dict]:
    """Split on '## ' headers; each chunk keeps its own heading + the
    document's top-level '# ' title for context."""
    title_match = re.match(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filename

    parts = re.split(r"\n(?=##\s+)", text)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part or part.startswith("# "):
            continue
        heading_match = re.match(r"^##\s+(.+)$", part, re.MULTILINE)
        heading = heading_match.group(1).strip() if heading_match else ""
        chunks.append({
            "heading": heading,
            "text": f"[{title}] {part}",
        })
    return chunks


def main():
    cfg = load_yaml(CONFIG_PATH)
    retriever = K9Retriever(config=cfg)

    if not retriever._ensure_services():
        print("FAILED: VectorDB/embedding service not available -- check "
              "vectordb config, Postgres reachability, and Ollama reachability.")
        sys.exit(1)

    total_chunks = 0
    for md_file in sorted(CORPUS_DIR.glob("*.md")):
        if md_file.name == "README.md":
            continue
        text = md_file.read_text()
        chunks = chunk_by_section(text, md_file.stem)
        for i, chunk in enumerate(chunks):
            doc_id = f"synthetic:{md_file.stem}:{i}"
            ok = retriever.store(
                doc_id=doc_id,
                text=chunk["text"],
                metadata={
                    "text": chunk["text"],
                    "source": md_file.name,
                    "heading": chunk["heading"],
                    "synthetic": True,
                    "chunk_index": i,
                },
            )
            status = "ok" if ok else "FAILED"
            print(f"  [{status}] {doc_id} ({len(chunk['text'])} chars)")
            if ok:
                total_chunks += 1

    print(f"\nSeeded {total_chunks} chunks from "
          f"{len(list(CORPUS_DIR.glob('*.md'))) - 1} source documents.")

    print("\n--- Verification: real retrieve() call ---")
    results = retriever.retrieve(
        intent="dodaf_view_generation",
        query="DoDAF OV-1 operational capability system",
        top_k=3,
    )
    if not results:
        print("WARNING: retrieve() returned nothing after seeding.")
    for r in results:
        print(f"  score={r['score']:.3f} source={r['metadata'].get('source')} "
              f"heading={r['metadata'].get('heading')!r}")
        print(f"    text preview: {r['text'][:120]}...")


if __name__ == "__main__":
    main()
