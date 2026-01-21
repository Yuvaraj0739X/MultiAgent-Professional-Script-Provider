"""
Configuration for Multi-Agent Screenplay Generator
Model and temperature settings for all phases.
"""

# Model selection per phase and node
MODELS = {
    "phase1": {
        "intake": "gpt-4o-mini",
        "clarification": "gpt-4o-mini",
        "integration": "gpt-4o-mini",
        "re_intake": "gpt-4o-mini",
        "summary": "gpt-4o-mini",
    },
    "phase2": {
        "research_strategy": "gpt-4o-mini",
        "fact_extraction": "gpt-4o-mini",
        "fact_validation": "gpt-4o-mini",
        "timeline_build": "gpt-4o-mini",
    },
    "phase3": {
        "scene_breakdown": "gpt-4o-mini",              # Premium for creative structure
        "screenplay_generation": "gpt-4o-mini",        # Premium for creative writing
        "validation": "gpt-4o-mini",              # Basic for validation
    },
    "phase4": {
        "character_extraction": "gpt-4o-mini",         # Premium for detailed extraction
        "voice_extraction": "gpt-4o-mini",             # Premium for voice analysis
        "environment_extraction": "gpt-4o-mini",       # Premium for detailed extraction
        "scene_analysis": "gpt-4o-mini",               # Premium for complex analysis
        "storyboard_planning": "gpt-4o-mini",          # Premium for creative planning
    },
}

# Temperature settings by task type
TEMPERATURES = {
    "analysis": 0.2,           # Factual analysis
    "creative_low": 0.5,       # Low creativity
    "creative_medium": 0.6,    # Medium creativity
    "creative_high": 0.7,      # High creativity
    "structured": 0.3,         # Structured extraction
    "factual": 0.1,           # Pure facts
}

# Temperature mapping per phase/node
TEMPERATURE_MAP = {
    "phase1": {
        "intake": "analysis",
        "clarification": "structured",
        "integration": "creative_low",
        "re_intake": "analysis",
        "summary": "creative_medium",
    },
    "phase2": {
        "research_strategy": "structured",
        "fact_extraction": "factual",
        "fact_validation": "factual",
        "timeline_build": "structured",
    },
    "phase3": {
        "scene_breakdown": "creative_medium",
        "screenplay_generation": "creative_high",
        "validation": "factual",
    },
    "phase4": {
        "character_extraction": "structured",
        "voice_extraction": "creative_low",
        "environment_extraction": "structured",
        "scene_analysis": "creative_low",
        "storyboard_planning": "creative_medium",
    },
}


def get_model_for_node(phase: str, node_name: str) -> str:
    """
    Get model name for specific phase and node.
    
    Args:
        phase: Phase name (e.g., "phase4")
        node_name: Node name (e.g., "character_extraction")
    
    Returns:
        Model name (e.g., "gpt-4o")
    """
    return MODELS.get(phase, {}).get(node_name, "gpt-4o-mini")


def get_temperature_for_node(phase: str, node_name: str) -> float:
    """
    Get temperature setting for specific phase and node.
    
    Args:
        phase: Phase name (e.g., "phase4")
        node_name: Node name (e.g., "character_extraction")
    
    Returns:
        Temperature value (0.0-1.0)
    """
    temp_key = TEMPERATURE_MAP.get(phase, {}).get(node_name, "structured")
    return TEMPERATURES.get(temp_key, 0.3)


def get_llm_config(phase: str, node_name: str) -> dict:
    """
    Get complete LLM configuration for a node.
    
    Args:
        phase: Phase name (e.g., "phase4")
        node_name: Node name (e.g., "character_extraction")
    
    Returns:
        Dict with model and temperature: {'model': 'gpt-4o', 'temperature': 0.3}
    """
    return {
        "model": get_model_for_node(phase, node_name),
        "temperature": get_temperature_for_node(phase, node_name)
    }


# Cost estimates (USD per 1M tokens)
COST_ESTIMATES = {
    "gpt-4o": {
        "input": 2.50,
        "output": 10.00
    },
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60
    }
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Estimate cost for API call.
    
    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
    
    Returns:
        Estimated cost in USD
    """
    costs = COST_ESTIMATES.get(model, COST_ESTIMATES["gpt-4o-mini"])
    
    input_cost = (input_tokens / 1_000_000) * costs["input"]
    output_cost = (output_tokens / 1_000_000) * costs["output"]
    
    return input_cost + output_cost