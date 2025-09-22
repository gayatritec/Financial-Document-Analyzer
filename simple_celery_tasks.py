"""Simple Celery tasks for financial document analysis."""

import os
from datetime import datetime
from celery_config import celery_app
from mongo_storage import mongo_storage
from crewai import Crew, Process
from agents import financial_analyst, investment_advisor, risk_assessor, verifier
from task import (
    analyze_financial_document,
    investment_analysis,
    risk_assessment,
    verification,
)

# Ensure outputs folder exists
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)


@celery_app.task(name="simple_celery_tasks.analyze_document_task", bind=True)
def analyze_document_task(self, session_id: str, query: str, file_path: str, filename: str):
    """Analyze financial document and save result to MongoDB and Markdown file."""
    try:
        # Update task status
        self.update_state(
            state="PROGRESS",
            meta={"status": "processing", "session_id": session_id},
        )

        # Process the financial document with all analysts
        financial_crew = Crew(
            agents=[financial_analyst, investment_advisor, risk_assessor, verifier],
            tasks=[analyze_financial_document, investment_analysis, risk_assessment, verification],
            process=Process.sequential,
        )

        response = financial_crew.kickoff(inputs={"query": query, "path": file_path})
        raw_output = str(getattr(response, "raw", response))

        # Save result to MongoDB
        result_id = mongo_storage.save_result(session_id, query, raw_output, filename)

        # Save Markdown file in outputs/
        md_file = os.path.join(OUTPUTS_DIR, f"{session_id}.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# Financial Analysis Report\n\n")
            f.write(f"**Session ID:** {session_id}\n\n")
            f.write(f"**Query:** {query}\n\n")
            f.write(f"**Filename:** {filename}\n\n")
            f.write(f"**Created At:** {datetime.utcnow().isoformat()}Z\n\n")
            f.write("---\n\n")
            f.write(raw_output)

        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass  # Ignore cleanup errors

        return {
            "status": "success",
            "session_id": session_id,
            "result_id": result_id,
            "analysis": raw_output[:300] + "..." if len(raw_output) > 300 else raw_output,
            "markdown_file": md_file,
        }

    except Exception as e:
        # Save error report as Markdown
        err_file = os.path.join(OUTPUTS_DIR, f"{session_id}_error.md")
        with open(err_file, "w", encoding="utf-8") as f:
            f.write(f"# Error Report\n\n")
            f.write(f"**Session ID:** {session_id}\n\n")
            f.write(f"**Error:** {str(e)}\n\n")
            f.write(f"**Created At:** {datetime.utcnow().isoformat()}Z\n")

        # Clean up uploaded file on error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        return {
            "status": "error",
            "session_id": session_id,
            "error": str(e),
            "error_file": err_file,
        }
