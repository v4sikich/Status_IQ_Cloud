#!/usr/bin/env python3
"""
Project-Specific Pipeline Runner

This script simplifies running the pipeline for a specific project.
It automatically handles project folder structure and puts results in the right place.

Usage:
  python run_project_pipeline.py --project-name stephenson_rife

Or with custom files:
  python run_project_pipeline.py \
    --project-name my_project \
    --transcript projects/my_project/input/custom_transcript.txt \
    --metadata projects/my_project/input/custom_metadata.json
"""

import sys
import os
from pathlib import Path
import json
import argparse

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from run_pipeline import PipelineOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Run pipeline for a specific project (with automatic folder handling)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Run with default files (input/transcript.txt + input/metadata.json)
  python run_project_pipeline.py --project-name stephenson_rife

  # Run with custom transcript file
  python run_project_pipeline.py \
    --project-name stephenson_rife \
    --transcript projects/stephenson_rife/input/custom_transcript.txt

  # Results will appear in:
  # projects/stephenson_rife/
  #   ├── Stephenson_Rife_Status_Report.html   (final report)
  #   ├── Stephenson_Rife_Status_Report.pptx   (final report, PPTX)
  #   └── workflow_execution/                  (intermediate working data)
  #       ├── 01_flattened/
  #       ├── 02_intake_output.json
  #       └── 03_prioritized_output.json
        """)

    parser.add_argument("--project-name", required=True,
                        help="Project name (folder in projects/ directory)")
    parser.add_argument("--transcript",
                        help="Custom transcript file (default: projects/[name]/input/transcript.txt)")
    parser.add_argument("--metadata",
                        help="Custom metadata file (default: projects/[name]/input/metadata.json)")
    parser.add_argument("--excel",
                        help="Excel file (Smartsheet export, budget tracking, etc)")
    parser.add_argument("--practice", default="PMO",
                        help="Practice (PMO, QMS, ITQC, etc) - default: PMO")

    args = parser.parse_args()

    # Construct project directory path
    project_name = args.project_name
    project_dir = Path("projects") / project_name

    if not project_dir.exists():
        print(f"❌ Project folder not found: {project_dir}")
        print(f"\nCreate project folder first:")
        print(f"  cp -r projects/_template_project projects/{project_name}")
        sys.exit(1)

    # Determine input file paths
    transcript_file = args.transcript or str(project_dir / "input" / "transcript.txt")
    metadata_file = args.metadata or str(project_dir / "input" / "metadata.json")

    # Verify files exist
    if not Path(transcript_file).exists():
        print(f"❌ Transcript not found: {transcript_file}")
        print(f"\nAdd transcript to: {project_dir}/input/transcript.txt")
        sys.exit(1)

    if not Path(metadata_file).exists():
        print(f"❌ Metadata not found: {metadata_file}")
        print(f"\nAdd metadata to: {project_dir}/input/metadata.json")
        sys.exit(1)

    # Load project metadata to get friendly name
    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        project_display_name = metadata.get('project_name', project_name)
    except:
        project_display_name = project_name

    print(f"\n{'='*80}")
    print(f"🚀 Running Pipeline for Project: {project_display_name}")
    print(f"{'='*80}")
    print(f"📁 Project Folder: {project_dir}")
    print(f"📄 Transcript: {transcript_file}")
    print(f"📋 Metadata: {metadata_file}")
    print(f"📊 Results will be saved to: {project_dir}/\n")

    # Run pipeline
    orchestrator = PipelineOrchestrator()
    results = orchestrator.run(
        transcript_path=transcript_file,
        metadata_path=metadata_file,
        project_name=project_display_name,
        practice=args.practice,
        excel_path=args.excel,
        project_dir=str(project_dir),  # This puts results in workflow_execution/
    )

    if results:
        # Print results summary
        html_path = Path(results['status_report']['file'])
        pptx_path = Path(results['pptx_report']['file'])

        print(f"\n{'='*80}")
        print(f"✅ PIPELINE COMPLETE!")
        print(f"{'='*80}")
        print(f"\n📁 Results Location: {project_dir}/")
        print(f"\n📄 Generated Files:")
        print(f"   ✅ {html_path.name}       (Final report, HTML)")
        print(f"   ✅ {pptx_path.name}       (Final report, PPTX)")
        print(f"   ✅ workflow_execution/    (flattened data, extracted KPIs, ranked data)")

        print(f"\n🌐 View Report:")
        print(f"   file://{html_path.absolute()}")

        return 0
    else:
        print(f"\n❌ Pipeline failed. Check error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
