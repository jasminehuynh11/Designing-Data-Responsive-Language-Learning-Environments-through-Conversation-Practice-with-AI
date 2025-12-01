"""Monitor progress of production batch processing."""
from pathlib import Path
import json
import time
from datetime import datetime

def monitor_batch():
    """Monitor production batch progress."""
    production_dir = Path('data/repairs/production')
    batch_summary_file = production_dir / 'batch_summary.json'
    
    total_files = 156  # Remaining files to process
    
    print("=" * 70)
    print("PRODUCTION BATCH MONITOR")
    print("=" * 70)
    print(f"Total files to process: {total_files}")
    print()
    
    # Check if batch summary exists
    if batch_summary_file.exists():
        with open(batch_summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        successful = summary.get('successful', 0)
        failed = summary.get('failed', 0)
        skipped = summary.get('skipped', 0)
        total_processed = successful + failed
        
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📊 Progress: {total_processed}/{total_files} ({total_processed/total_files*100:.1f}%)")
        
        # Show latest results
        results = summary.get('results', [])
        if results:
            print(f"\nLatest processed files:")
            for result in results[-5:]:
                status = "✓" if result.get('success') else "✗"
                repairs = result.get('repairs_count', 0)
                print(f"  {status} {result.get('file')} - {repairs} repairs")
    else:
        # Count files directly
        if production_dir.exists():
            files = list(production_dir.glob('*_repairs.json'))
            count = len(files)
            print(f"📁 Files processed: {count}/{total_files} ({count/total_files*100:.1f}%)")
            
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                print(f"Latest: {latest.name}")
        else:
            print("⏳ Batch not started yet or no files processed")
    
    print()
    print("=" * 70)
    print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    monitor_batch()

