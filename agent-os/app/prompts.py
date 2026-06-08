"""
app/prompts.py
Prompt Builders for Gemini Agent OS.
Constructs system instructions and user prompt templates grounding the agent.
"""

from app import config

def build_system_instruction(global_agents: str, domain_agents: str) -> str:
    """
    Assembles the system instruction string for Gemini using global rules
    and domain-specific guidelines.
    """
    instructions = [
        "You are Gemini Agent OS, a self-hosted personal AI operating system.",
        f"Target Timezone: {config.TIMEZONE}",
        "",
        "=== GLOBAL RULES AND CORE SYSTEM BEHAVIOR ===",
        global_agents,
        ""
    ]
    
    if domain_agents:
        instructions.extend([
            "=== DOMAIN GUIDELINES ===",
            domain_agents,
            ""
        ])
        
    instructions.extend([
        "=== RESPONSE INSTRUCTIONS ===",
        "- Be direct, rigorous, and direct. Skip conversational filler.",
        "- Ground every single answer in the provided file contents.",
        "- Do not make up facts or status elements that are not present in the files.",
        "- If the request requires human intervention or approval, clearly state it."
    ])
    
    return "\n".join(instructions)