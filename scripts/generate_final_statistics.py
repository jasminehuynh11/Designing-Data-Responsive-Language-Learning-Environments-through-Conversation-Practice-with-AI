"""Generate comprehensive final statistics for all repair detection batches."""
from pathlib import Path
import json
from collections import defaultdict

def load_repairs(repair_file: Path) -> list:
    """Load repair annotations."""
    if not repair_file.exists():
        return []
    try:
        with open(repair_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def aggregate_statistics():
    """Aggregate statistics from all batches."""
    repairs_dir = Path('data/repairs')
    
    stats = {
        'total_files': 0,
        'files_with_repairs': 0,
        'files_without_repairs': 0,
        'total_repairs': 0,
        'initiation_distribution': defaultdict(int),
        'resolution_distribution': defaultdict(int),
        'trigger_categories': defaultdict(int),
        'batches': {}
    }
    
    # Process each batch
    for batch_dir in repairs_dir.iterdir():
        if not batch_dir.is_dir():
            continue
        
        batch_name = batch_dir.name
        if batch_name == 'production' and (batch_dir / 'batch_summary.json').exists():
            # Use existing review report if available
            review_report = batch_dir / 'review_report.json'
            if review_report.exists():
                with open(review_report, 'r', encoding='utf-8') as f:
                    batch_stats = json.load(f)
                    stats['batches'][batch_name] = batch_stats
                    stats['total_files'] += batch_stats.get('total_files', 0)
                    stats['files_with_repairs'] += batch_stats.get('files_with_repairs', 0)
                    stats['files_without_repairs'] += batch_stats.get('files_without_repairs', 0)
                    stats['total_repairs'] += batch_stats.get('total_repairs', 0)
                    continue
        
        # Process repair files
        batch_stats = {
            'total_files': 0,
            'files_with_repairs': 0,
            'files_without_repairs': 0,
            'total_repairs': 0,
            'initiation_distribution': defaultdict(int),
            'resolution_distribution': defaultdict(int),
            'trigger_categories': defaultdict(int),
        }
        
        repair_files = list(batch_dir.glob("*_repairs.json"))
        batch_stats['total_files'] = len(repair_files)
        
        for repair_file in repair_files:
            if 'batch_summary' in repair_file.name or 'review_report' in repair_file.name:
                continue
            
            repairs = load_repairs(repair_file)
            
            if repairs:
                batch_stats['files_with_repairs'] += 1
                batch_stats['total_repairs'] += len(repairs)
                
                for repair in repairs:
                    batch_stats['initiation_distribution'][repair.get('initiation', 'unknown')] += 1
                    batch_stats['resolution_distribution'][repair.get('resolution', 'unknown')] += 1
                    
                    trigger = repair.get('trigger', 'other')
                    trigger_cat = trigger.split('–')[0].strip() if '–' in trigger else trigger.split(':')[0].strip() if ':' in trigger else 'other'
                    batch_stats['trigger_categories'][trigger_cat.lower()] += 1
            else:
                batch_stats['files_without_repairs'] += 1
        
        # Aggregate to main stats
        stats['total_files'] += batch_stats['total_files']
        stats['files_with_repairs'] += batch_stats['files_with_repairs']
        stats['files_without_repairs'] += batch_stats['files_without_repairs']
        stats['total_repairs'] += batch_stats['total_repairs']
        
        for k, v in batch_stats['initiation_distribution'].items():
            stats['initiation_distribution'][k] += v
        for k, v in batch_stats['resolution_distribution'].items():
            stats['resolution_distribution'][k] += v
        for k, v in batch_stats['trigger_categories'].items():
            stats['trigger_categories'][k] += v
        
        stats['batches'][batch_name] = {
            'total_files': batch_stats['total_files'],
            'files_with_repairs': batch_stats['files_with_repairs'],
            'files_without_repairs': batch_stats['files_without_repairs'],
            'total_repairs': batch_stats['total_repairs']
        }
    
    # Convert defaultdicts to regular dicts
    stats['initiation_distribution'] = dict(stats['initiation_distribution'])
    stats['resolution_distribution'] = dict(stats['resolution_distribution'])
    stats['trigger_categories'] = dict(stats['trigger_categories'])
    
    return stats

def main():
    """Generate and display final statistics."""
    print("=" * 80)
    print("PHASE 2: FINAL STATISTICS")
    print("=" * 80)
    print()
    
    stats = aggregate_statistics()
    
    print(f"Total Files Processed: {stats['total_files']}")
    print(f"Files with Repairs: {stats['files_with_repairs']}")
    print(f"Files without Repairs: {stats['files_without_repairs']}")
    print(f"Total Repairs Detected: {stats['total_repairs']}")
    print()
    
    print("Initiation Distribution:")
    for k, v in sorted(stats['initiation_distribution'].items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print()
    
    print("Resolution Distribution:")
    for k, v in sorted(stats['resolution_distribution'].items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print()
    
    print("Top Trigger Categories:")
    for k, v in sorted(stats['trigger_categories'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {k}: {v}")
    print()
    
    print("Batch Breakdown:")
    for batch_name, batch_stats in stats['batches'].items():
        print(f"  {batch_name}:")
        print(f"    Files: {batch_stats['total_files']}")
        print(f"    With Repairs: {batch_stats['files_with_repairs']}")
        print(f"    Total Repairs: {batch_stats['total_repairs']}")
    print()
    
    # Save to file
    output_file = Path('data/repairs/FINAL_STATISTICS.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Statistics saved to: {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()

