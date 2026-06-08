"""
app/main.py
FastAPI Web Application Entrypoint for Gemini Agent OS.
Exposes endpoints for API health, grounded chat, morning briefs, and skill execution.
"""

import uuid
import datetime
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.schemas.agent_response import ChatRequest, AgentResponse
from app.schemas.skill import SkillRequest, SkillResult
from app.context import load_context, build_context_prompt
from app.prompts import build_system_instruction
from app.agent import generate_response

from app.workflows.morning_brief import run_morning_brief
from app.workflows.update_tasks import run_update_tasks
from app.workflows.deploy_check import run_deploy_check
from app.tools.filesystem import read_file, write_file

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gemini Agent OS API", version="0.1.0")

# Mount dashboard static files
@app.get("/dashboard/dashboard.json")
def get_dashboard_data():
    """
    Dynamically refreshes and returns the dashboard JSON state.
    """
    from app.tools.dashboard import refresh_dashboard_json
    from fastapi.responses import JSONResponse
    import json
    
    try:
        # Re-aggregate and write the file
        refresh_dashboard_json(domain="personal-os", request_id="dashboard-api")
    except Exception as e:
        logger.error(f"Error auto-refreshing dashboard: {e}")
        
    try:
        from app.tools.filesystem import read_file
        content = read_file("dashboard/dashboard.json", request_id="dashboard-api")
        return JSONResponse(
            content=json.loads(content),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read dashboard state: {str(e)}")

app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

@app.get("/health")
def health():
    """
    Returns API health status.
    """
    return {
        "status": "ok",
        "health_endpoint": "ok",
        "version": "0.1.0"
    }

@app.post("/chat", response_model=AgentResponse)
def chat_endpoint(request: ChatRequest):
    """
    Runs a grounded Gemini query against the current domain context.
    """
    request_id = f"req_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    logger.info(f"Processing chat request {request_id} for domain: {request.domain}")
    
    try:
        # 1. Load domain-specific and global file context map
        context_map = load_context(request.domain)
        
        # 2. Extract agent instructions for system prompt
        global_agents = context_map.get("AGENTS.md", "")
        domain_agents = context_map.get(f"domains/{request.domain}/AGENTS.md", "")
        
        # 3. Assemble grounding system instructions
        system_instruction = build_system_instruction(global_agents, domain_agents)
        
        # 4. Assemble user context prompt representing current file state
        context_prompt = build_context_prompt(request.domain)
        
        # 5. Formulate prompt package
        final_prompt = f"{context_prompt}\n\n### USER REQUEST\n{request.message}"
        
        # 6. Call the Gemini model runtime
        answer = generate_response(
            system_instruction=system_instruction,
            prompt=final_prompt
        )
        
        # 7. Collect list of files loaded to construct prompt
        files_read = list(context_map.keys())
        
        # Return structured AgentResponse
        return AgentResponse(
            request_id=request_id,
            answer=answer,
            actions_taken=[],
            actions_requiring_approval=[],
            files_read=files_read,
            files_written=[]
        )
        
    except Exception as e:
        logger.exception(f"Unhandled error in chat endpoint for request {request_id}")
        raise HTTPException(status_code=500, detail=f"Agent OS Chat execution failed: {str(e)}")

@app.post("/brief/morning")
def manual_morning_brief():
    """
    Manually triggers the morning brief generation workflow.
    """
    try:
        result = run_morning_brief(domain="personal-os")
        return {"status": "success", "message": result}
    except Exception as e:
        logger.exception("Error executing manual morning brief workflow")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-skill", response_model=SkillResult)
def run_skill_endpoint(request: SkillRequest):
    """
    Executes a skill specified in toolbox/ and returns the execution result.
    """
    request_id = f"req_skill_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    skill = request.skill_name.lower().strip()
    logger.info(f"Executing skill '{skill}' for request {request_id}")
    
    try:
        if skill == "morning-brief":
            result = run_morning_brief(domain=request.domain, request_id=request_id)
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")
            archive_file = f"briefs/archive/brief-{today_date}.md"
            return SkillResult(
                skill_name=skill,
                success=True,
                actions_taken=[{"action": "morning_brief_workflow"}],
                files_written=["briefs/latest.md", archive_file, f"domains/{request.domain}/data/brief-state.json"],
                output_summary=result
            )
            
        elif skill == "update-tasks":
            approval_token = request.inputs.get("approval_token")
            result = run_update_tasks(domain=request.domain, approval_token=approval_token, request_id=request_id)
            files = [f"domains/{request.domain}/data/tasks.json", "dashboard/dashboard.json"]
            if approval_token == "proceed":
                files.append("TASKS.md")
            return SkillResult(
                skill_name=skill,
                success=True,
                actions_taken=[{"action": "update_tasks_workflow"}],
                files_written=files,
                output_summary=result
            )
            
        elif skill == "deploy-check" or skill == "system-status":
            result = run_deploy_check(domain=request.domain, request_id=request_id)
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            report_path = f"domains/{request.domain}/outputs/reports/deploy-check-{today_str}.md"
            return SkillResult(
                skill_name=skill,
                success=True,
                actions_taken=[{"action": "deploy_check_workflow"}],
                files_written=[f"domains/{request.domain}/data/system-health.json", report_path],
                output_summary=result
            )
            
        elif skill in ["create-prd", "plan-project"]:
            slug = request.inputs.get("slug")
            if not slug:
                return SkillResult(
                    skill_name=skill,
                    success=False,
                    output_summary="Failed: Missing required input 'slug'",
                    error="Missing input: 'slug'"
                )
                
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            if skill == "create-prd":
                spec_path = "toolbox/create-prd.md"
                output_path = f"domains/{request.domain}/outputs/prds/PRD-{slug}-{today_str}.md"
                required_inputs = ["idea"]
            else:
                spec_path = "toolbox/plan-project.md"
                output_path = f"domains/{request.domain}/outputs/plans/plan-{slug}-{today_str}.md"
                required_inputs = ["goal"]
                
            # Validate required inputs
            missing = [k for k in required_inputs if not request.inputs.get(k)]
            if missing:
                return SkillResult(
                    skill_name=skill,
                    success=False,
                    output_summary=f"Failed: Missing required inputs: {', '.join(missing)}",
                    error=f"Missing inputs: {', '.join(missing)}"
                )
                
            # Read instructions from skill specification file
            spec_instructions = read_file(spec_path, request_id=request_id)
            
            # Load context prompt
            context_prompt = build_context_prompt(request.domain)
            
            # Formulate user prompt
            inputs_str = "\n".join([f"- {k}: {v}" for k, v in request.inputs.items()])
            prompt = (
                f"{context_prompt}\n\n"
                f"### INPUTS CONTEXT:\n{inputs_str}\n\n"
                "Execute the skill defined in your instructions. Output ONLY the completed markdown document."
            )
            
            # Call Gemini
            answer = generate_response(
                system_instruction=spec_instructions,
                prompt=prompt
            )
            
            # Write to output file
            write_file(
                path=output_path,
                content=answer,
                allow_writes=True,
                request_id=request_id
            )
            
            return SkillResult(
                skill_name=skill,
                success=True,
                actions_taken=[{"action": f"generate_{skill}"}],
                files_written=[output_path],
                output_summary=f"Successfully executed generative skill. Saved to {output_path}."
            )
            
        else:
            return SkillResult(
                skill_name=skill,
                success=False,
                output_summary=f"Failed: Unknown skill '{skill}'",
                error=f"Unknown skill: {skill}"
            )
            
    except Exception as e:
        logger.exception(f"Error running skill '{skill}'")
        return SkillResult(
            skill_name=skill,
            success=False,
            output_summary=f"Failed: Exception during execution: {str(e)}",
            error=str(e)
        )