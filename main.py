from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from celery.result import AsyncResult
import os
import uuid
from crewai import Crew, Process
from agents import financial_analyst, investment_advisor, risk_assessor, verifier
from task import analyze_financial_document, investment_analysis, risk_assessment, verification
from simple_celery_tasks import analyze_document_task
from celery_config import celery_app
from mongo_storage import mongo_storage

app = FastAPI(title="Financial Document Analyzer")


def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """To run the whole crew synchronously (debugging)"""
    financial_crew = Crew(
        agents=[financial_analyst, investment_advisor, risk_assessor, verifier],
        tasks=[analyze_financial_document, investment_analysis, risk_assessment, verification],
        process=Process.sequential,
    )

    inputs = {
        'query': query,
        'file_path': file_path
    }

    result = financial_crew.kickoff(inputs=inputs)
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze_financial_documents(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze financial document and provide comprehensive investment recommendations"""
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        if not query:
            query = "Analyze this financial document for investment insights"

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Submit Celery task
        task = analyze_document_task.delay(session_id, query.strip(), file_path, file.filename)

        return {
            "status": "processing",
            "task_id": task.id,
            "session_id": session_id,
            "query": query,
            "file_processed": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")


@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and results."""
    try:
        task = AsyncResult(task_id, app=celery_app)

        if task.state == 'PENDING':
            return {"state": task.state, "status": "Task is pending..."}
        elif task.state == 'PROGRESS':
            return {
                "state": task.state,
                "status": task.info.get('status', 'Processing...'),
                "session_id": task.info.get('session_id')
            }
        elif task.state == 'SUCCESS':
            return {"state": task.state, "status": "Task completed successfully", "result": task.info}
        else:  # FAILURE
            return {"state": task.state, "status": "Task failed", "error": str(task.info)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task status: {str(e)}")


@app.get("/results")
async def get_all_results():
    """Get all analysis results from MongoDB."""
    try:
        results = list(mongo_storage.collection.find({}).sort('created_at', -1))
        for result in results:
            result['_id'] = str(result['_id'])
        return {"status": "success", "count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting results: {str(e)}")


@app.get("/results/{session_id}")
async def get_result_by_session(session_id: str):
    """Get analysis result by session ID."""
    try:
        result = mongo_storage.get_result(session_id)
        if result:
            return {"status": "success", "result": result}
        else:
            raise HTTPException(status_code=404, detail="Result not found for this session ID")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting result: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
