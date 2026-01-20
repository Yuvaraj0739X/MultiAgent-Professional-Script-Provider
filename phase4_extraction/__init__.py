"""
Phase 4: Character & Environment Extraction + Storyboard Planning
Main package exports for Phase 4 workflow.
"""

from .graph import create_phase4_graph, run_phase4, save_phase4_outputs
from .state import Phase4State, get_initial_phase4_state
from .models import (
    Character,
    VoiceProfile,
    Environment,
    Scene,
    StoryboardFrame,
    StoryboardPlan,
    Phase4Output
)

__version__ = "1.0.0"

__all__ = [
    # Main workflow functions
    'create_phase4_graph',
    'run_phase4',
    'save_phase4_outputs',
    
    # State
    'Phase4State',
    'get_initial_phase4_state',
    
    # Key models
    'Character',
    'VoiceProfile',
    'Environment',
    'Scene',
    'StoryboardFrame',
    'StoryboardPlan',
    'Phase4Output'
]
