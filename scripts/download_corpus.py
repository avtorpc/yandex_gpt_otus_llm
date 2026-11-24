"""Download a pinned corpus snapshot and export texts for manual selection."""
import csv
import hashlib
import json
from pathlib import Path
import urllib.request
import argparse

DATASET = "TryDotAtwo/russian-legal-ner"
REVISION = "d23f5380ccbd0b14c27efb8c9b7280d13cb4b85a"
ROOT = Path("data/raw/russian-legal-ner")


def download(remote, target):
    url = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{remote}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        temporary = target.with_suffix(target.suffix + ".part")
        print(f"Downloading {remote}", flush=True)
        with urllib.request.urlopen(url, timeout=120) as response, temporary.open("wb") as out:
            while block := response.read(1024 * 1024):
                out.write(block)
        temporary.replace(target)
    digest = hashlib.sha256()
    with target.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return {"url": url, "bytes": target.stat().st_size, "sha256": digest.hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-only", action="store_true")
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {"dataset": DATASET, "revision": REVISION, "files": {}, "splits": {}}
    manifest["files"]["README.md"] = download("README.md", ROOT / "SOURCE_README.md")
    for split in ("train", "validation", "test"):
        manifest["files"][f"{split}.parquet"] = download(f"data/{split}.parquet", ROOT / f"{split}.parquet")
    if args.download_only:
        print("Original files downloaded", flush=True)
        return
    import pyarrow.parquet as pq
    with (ROOT / "catalog.csv").open("w", encoding="utf-8-sig", newline="") as catalog:
        writer = csv.writer(catalog)
        writer.writerow(["document_id", "split", "row_index", "characters", "text_path", "preview"])
        for split in ("train", "validation", "test"):
            path = ROOT / f"{split}.parquet"
            text_dir = ROOT / "texts" / split
            text_dir.mkdir(parents=True, exist_ok=True)
            count = 0
            for batch in pq.ParquetFile(path).iter_batches(batch_size=512, columns=["text"]):
                for text in batch.column(0).to_pylist():
                    if not isinstance(text, str):
                        raise ValueError(f"Invalid text at {split}:{count}")
                    doc_id = f"{split}_{count:06d}"
                    relative = Path("texts") / split / f"{doc_id}.txt"
                    (ROOT / relative).write_text(text, encoding="utf-8")
                    writer.writerow([doc_id, split, count, len(text), relative.as_posix(), " ".join(text.split())[:300]])
                    count += 1
            manifest["splits"][split] = count
            print(f"{split}: {count} texts exported", flush=True)
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Done: {ROOT / 'catalog.csv'}", flush=True)


if __name__ == "__main__":
    main()
