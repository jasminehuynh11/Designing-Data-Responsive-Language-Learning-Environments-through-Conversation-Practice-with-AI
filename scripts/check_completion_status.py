"""Check completion status of repair detection for all dialogues."""
from pathlib import Path
import json

# Get all dialogue files
processed_dir = Path('data/processed')
new_files = set([f.stem for f in processed_dir.glob('S*_W*_T*.json')])
legacy_files = set([f.stem for f in processed_dir.glob('W*_T*.json')])
all_dialogue_files = new_files | legacy_files

print(f"Total dialogue files: {len(all_dialogue_files)}")
print(f"  New format (S*_W*_T*): {len(new_files)}")
print(f"  Legacy format (W*_T*): {len(legacy_files)}")

# Get all repair files across all batches
repairs_dir = Path('data/repairs')
all_repair_files = set()

for batch_dir in repairs_dir.iterdir():
    if batch_dir.is_dir() and batch_dir.name != 'production':
        for repair_file in batch_dir.glob("*_repairs.json"):
            dialogue_name = repair_file.stem.replace("_repairs", "")
            all_repair_files.add(dialogue_name)

# Get production repair files separately
production_files = set()
production_dir = repairs_dir / 'production'
if production_dir.exists():
    for repair_file in production_dir.glob("*_repairs.json"):
        if 'batch_summary' not in repair_file.name:
            dialogue_name = repair_file.stem.replace("_repairs", "")
            production_files.add(dialogue_name)

print(f"\nRepair files found:")
print(f"  Pilot/Validation batches: {len(all_repair_files)}")
print(f"  Production batch: {len(production_files)}")

# Combine all
all_repair_files = all_repair_files | production_files
print(f"  Total unique: {len(all_repair_files)}")

# Find missing
missing = sorted(all_dialogue_files - all_repair_files)
extra = sorted(all_repair_files - all_dialogue_files)

print(f"\nStatus:")
print(f"  ✅ Processed: {len(all_dialogue_files & all_repair_files)}")
print(f"  ❌ Missing: {len(missing)}")
if missing:
    print(f"\nMissing files:")
    for m in missing[:10]:
        print(f"    {m}.json")
    if len(missing) > 10:
        print(f"    ... and {len(missing) - 10} more")

if extra:
    print(f"\n⚠️  Extra repair files (not matching dialogues): {len(extra)}")
    for e in extra[:5]:
        print(f"    {e}_repairs.json")

print(f"\n{'='*70}")
if not missing:
    print("✅ ALL DIALOGUE FILES HAVE REPAIR ANNOTATIONS!")
else:
    print(f"⚠️  {len(missing)} files still need processing")

