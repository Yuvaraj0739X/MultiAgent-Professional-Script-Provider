"""
Session Management for Multi-Phase Pipeline
Handles data persistence and transitions between phases
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class SessionManager:
    """Manages session data across all phases"""
    
    def __init__(self, session_id: str):
        """
        Initialize session manager.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.outputs_dir = Path("outputs") / session_id
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
    
    def save_phase_output(self, phase_number: int, data: Dict[str, Any], format: str = "json"):
        """
        Save phase output to session directory.
        
        Args:
            phase_number: Phase number (1, 2, 3, 4)
            data: Data to save
            format: Output format ('json' or 'md')
        """
        phase_names = {
            1: "phase1_brief",
            2: "phase2_research" if format == "json" else "phase2_summary",
            3: "phase3_screenplay",
            4: "phase4_extraction"
        }
        
        filename = f"{phase_names[phase_number]}.{format}"
        filepath = self.outputs_dir / filename
        
        if format == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:  # markdown or text
            with open(filepath, 'w', encoding='utf-8') as f:
                if isinstance(data, dict):
                    f.write(data.get('content', str(data)))
                else:
                    f.write(str(data))
        
        print(f"💾 Phase {phase_number} output saved: {filepath}")
        return str(filepath)
    
    def load_phase_output(self, phase_number: int, format: str = "json") -> Optional[Dict]:
        """
        Load phase output from session directory.
        
        Args:
            phase_number: Phase number to load
            format: Expected format
        
        Returns:
            Loaded data or None if not found
        """
        phase_names = {
            1: "phase1_brief",
            2: "phase2_research",
            3: "phase3_screenplay",
            4: "phase4_extraction"
        }
        
        filename = f"{phase_names[phase_number]}.{format}"
        filepath = self.outputs_dir / filename
        
        if not filepath.exists():
            return None
        
        if format == "json":
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                return {"content": f.read()}
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of session progress"""
        phase3_dir = self.outputs_dir / "phase3_screenplay"
        phase3_complete = (phase3_dir / "screenplay.fountain").exists() if phase3_dir.exists() else False
        
        phase4_dir = self.outputs_dir / "phase4_extraction"
        phase4_complete = (phase4_dir / "characters_database.json").exists() if phase4_dir.exists() else False
        
        return {
            "session_id": self.session_id,
            "outputs_dir": str(self.outputs_dir),
            "phase1_complete": (self.outputs_dir / "phase1_brief.md").exists(),
            "phase2_complete": (self.outputs_dir / "phase2_research.json").exists() or (self.outputs_dir / "phase2_summary.md").exists(),
            "phase3_complete": phase3_complete,
            "phase4_complete": phase4_complete,
        }
    
    def create_phase_transition_state(self, from_phase: int, phase_state: Dict) -> Dict:
        """
        Extract necessary data for next phase.
        
        Args:
            from_phase: Source phase number
            phase_state: Complete state from source phase
        
        Returns:
            Data needed for next phase
        """
        if from_phase == 1:
            # Phase 1 → Phase 2 (Research) or Phase 3 (Screenplay)
            return {
                "phase1_brief": phase_state.get("final_brief", ""),
                "classification": phase_state.get("classification", "unknown"),
                "research_required": phase_state.get("research_required", False),
                "detected_entities": phase_state.get("detected_elements", {}),
                "user_input_refined": phase_state.get("user_input_refined", ""),
                "session_id": phase_state.get("session_id", self.session_id)
            }
        
        elif from_phase == 2:
            # Phase 2 → Phase 3 (Screenplay)
            return {
                "verified_facts": phase_state.get("verified_facts", []),
                "timeline": phase_state.get("timeline", []),
                "key_figures": phase_state.get("key_figures", []),
                "key_locations": phase_state.get("key_locations", []),
                "research_summary": phase_state.get("research_summary", ""),
                "phase1_brief": phase_state.get("phase1_brief", ""),
                "session_id": phase_state.get("session_id", self.session_id)
            }
        
        elif from_phase == 3:
            # Phase 3 → Phase 4 (Extraction & Storyboards)
            return {
                "screenplay_text": phase_state.get("screenplay_text", ""),
                "screenplay_metadata": phase_state.get("screenplay_metadata", {}),
                "scene_breakdown": phase_state.get("scene_breakdown", []),
                "session_id": phase_state.get("session_id", self.session_id)
            }
        
        elif from_phase == 4:
            # Phase 4 → Phase 5 (Image/Video Generation)
            return {
                "characters_database": phase_state.get("characters_database", []),
                "environments_database": phase_state.get("environments_database", []),
                "scenes": phase_state.get("scenes", []),
                "extraction_metadata": phase_state.get("extraction_metadata", {}),
                "session_id": phase_state.get("session_id", self.session_id)
            }
        
        return {}


def generate_session_id() -> str:
    """Generate unique session identifier"""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"