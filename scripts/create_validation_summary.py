"""Create comprehensive validation summary report."""
import json
from pathlib import Path

def create_summary():
    """Create validation summary."""
    
    validation_report = Path('data/repairs/VALIDATION_REPORT.json')
    cross_validation_report = Path('data/repairs/CROSS_VALIDATION_REPORT.json')
    
    summary = {
        'validation_date': '2025-11-29',
        'overall_status': 'GOOD',
        'completeness': {},
        'structure_validation': {},
        'content_validation': {},
        'issues_summary': {},
        'recommendations': []
    }
    
    # Load validation reports
    if validation_report.exists():
        with open(validation_report, 'r', encoding='utf-8') as f:
            struct_data = json.load(f)
            struct_summary = struct_data.get('summary', {})
            
            summary['completeness'] = {
                'total_dialogues': struct_summary.get('total_dialogues', 0),
                'with_repair_files': struct_summary.get('with_repair_files', 0),
                'missing_repair_files': struct_summary.get('missing_repair_files', 0),
                'completion_rate': f"{(struct_summary.get('with_repair_files', 0) / struct_summary.get('total_dialogues', 1)) * 100:.1f}%"
            }
            
            summary['structure_validation'] = {
                'total_repairs': struct_summary.get('total_repairs', 0),
                'valid_repairs': struct_summary.get('valid_repairs', 0),
                'invalid_repairs': struct_summary.get('invalid_repairs', 0),
                'validity_rate': f"{(struct_summary.get('valid_repairs', 0) / struct_summary.get('total_repairs', 1)) * 100:.1f}%" if struct_summary.get('total_repairs', 0) > 0 else "N/A"
            }
    
    if cross_validation_report.exists():
        with open(cross_validation_report, 'r', encoding='utf-8') as f:
            content_data = json.load(f)
            content_summary = content_data.get('summary', {})
            
            summary['content_validation'] = {
                'dialogues_validated': content_summary.get('dialogues_with_repairs', 0),
                'total_repairs': content_summary.get('total_repairs', 0),
                'issues_found': content_summary.get('total_issues', 0),
                'warnings': content_summary.get('total_warnings', 0),
                'validation_score': f"{content_summary.get('average_validation_score', 0) * 100:.2f}%"
            }
            
            summary['overall_status'] = 'EXCELLENT' if content_summary.get('average_validation_score', 0) > 0.95 else 'GOOD'
    
    # Get issues
    if validation_report.exists():
        with open(validation_report, 'r', encoding='utf-8') as f:
            data = json.load(f)
            files_with_issues = data.get('files_with_issues', [])
            
            summary['issues_summary'] = {
                'critical_files': len([f for f in files_with_issues if any('Turn index' in issue for issue in f.get('issues', []))]),
                'minor_files': len([f for f in files_with_issues if all('Turn index' not in issue for issue in f.get('issues', []))]),
                'total_files_with_issues': len(files_with_issues)
            }
    
    # Recommendations
    if summary['issues_summary'].get('critical_files', 0) > 0:
        summary['recommendations'].append("Fix turn index errors in repair files")
    
    if summary['completeness'].get('missing_repair_files', 0) == 0:
        summary['recommendations'].append("✅ All dialogues have repair files - ready for analysis")
    
    # Save summary
    output_file = Path('data/repairs/VALIDATION_SUMMARY.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Overall Status: {summary['overall_status']}")
    print()
    print("Completeness:")
    print(f"  Total dialogues: {summary['completeness'].get('total_dialogues', 'N/A')}")
    print(f"  With repair files: {summary['completeness'].get('with_repair_files', 'N/A')} ({summary['completeness'].get('completion_rate', 'N/A')})")
    print(f"  Missing: {summary['completeness'].get('missing_repair_files', 'N/A')}")
    print()
    print("Structure Validation:")
    print(f"  Valid repairs: {summary['structure_validation'].get('validity_rate', 'N/A')}")
    print()
    print("Content Validation:")
    print(f"  Validation score: {summary['content_validation'].get('validation_score', 'N/A')}")
    print(f"  Issues: {summary['content_validation'].get('issues_found', 'N/A')}")
    print(f"  Warnings: {summary['content_validation'].get('warnings', 'N/A')}")
    print()
    print("Issues:")
    print(f"  Critical files: {summary['issues_summary'].get('critical_files', 'N/A')}")
    print(f"  Minor issues: {summary['issues_summary'].get('minor_files', 'N/A')}")
    print()
    print("Recommendations:")
    for rec in summary['recommendations']:
        print(f"  - {rec}")
    print()
    print(f"✅ Summary saved to: {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    create_summary()

