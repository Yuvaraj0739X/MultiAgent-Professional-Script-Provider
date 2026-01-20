import os
import sys
from dotenv import load_dotenv

load_dotenv()

from graph import run_phase1_workflow
from utils import generate_session_id


def print_banner():
    """Print welcome banner"""
    print("\n" + "╔" * 70)
    print("║" + " " * 68 + "║")
    print("║" + " " * 20 + "PHASE 1: STORY INTAKE & CLARIFICATION" + " " * 11 + "║")
    print("║" + " " * 68 + "║")
    print("╚" * 70)
    print("\n🎬 Transform your vague story idea into a production-ready brief!")
    print("─" * 70 + "\n")


def get_user_story_input():
    """Get story idea from user"""
    print("📝 Enter your story idea:")
    print("   (Can be as vague as 'two brothers' or as detailed as you like)\n")
    
    print("Type your story idea and press Enter twice when done:")
    print("─" * 70)
    
    lines = []
    empty_count = 0
    
    while True:
        try:
            line = input()
            if line.strip() == "":
                empty_count += 1
                if empty_count >= 2 or (len(lines) > 0 and empty_count >= 1):
                    break
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled by user.\n")
            sys.exit(0)
    
    story_input = " ".join(lines).strip()
    
    if not story_input:
        print("\n⚠️  No input provided. Please try again.\n")
        sys.exit(1)
    
    print("─" * 70 + "\n")
    return story_input


def main():
    """Main execution function"""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY not found!")
        print("   Please create a .env file with your OpenAI API key.\n")
        print("   Example .env file:")
        print("   OPENAI_API_KEY=sk-your-key-here\n")
        sys.exit(1)
    
    print_banner()
    
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        print(f"📝 Story idea (from command line):\n   {user_input}\n")
        print("─" * 70 + "\n")
    else:
        user_input = get_user_story_input()
    
    session_id = generate_session_id()
    print(f"🆔 Session ID: {session_id}")
    print(f"📁 Checkpoints will be saved to: checkpoints/\n")
    
    print("▶️  Starting workflow...\n")
    input("Press ENTER to begin (or Ctrl+C to cancel)...\n")
    
    try:
        final_state = run_phase1_workflow(user_input, session_id)
        
        print("\n" + "╔" * 70)
        print("║" + " " * 68 + "║")
        print("║" + " " * 25 + "WORKFLOW COMPLETE!" + " " * 26 + "║")
        print("║" + " " * 68 + "║")
        print("╚" * 70)
        
        print(f"\n✅ Your story brief is ready!")
        print(f"📄 Word count: {final_state.get('brief_metadata', {}).get('word_count', 'N/A')}")
        print(f"🎯 Final clarity: {final_state.get('clarity_score', 0)}/100")
        print(f"🔄 Iterations: {final_state.get('clarification_iteration', 0)}")
        
        print(f"\n📁 All checkpoints saved to: checkpoints/")
        print(f"🔍 Session: {session_id}")
        
        print("\n" + "─" * 70)
        save_choice = input("\n💾 Save final brief to a separate file? (y/n): ").strip().lower()
        
        if save_choice in ['y', 'yes']:
            filename = f"brief_{session_id}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(final_state.get('final_brief', ''))
            print(f"\n✅ Brief saved to: {filename}\n")
        else:
            print("\n📋 Brief is available in the final checkpoint file.\n")
        
        print("=" * 70)
        print("\n🎉 Thank you for using Phase 1 Story Development!")
        print("   Next: Phase 2 (Research & Fact Verification) - Coming soon\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user.")
        print(f"💾 Progress saved in checkpoints/ with session: {session_id}")
        print("   You can resume later by loading the checkpoint.\n")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n\n❌ Workflow failed with error:")
        print(f"   {str(e)}\n")
        print(f"💾 Partial progress saved in: checkpoints/")
        print(f"🔍 Session ID: {session_id}")
        print("\n🐛 For debugging, check the checkpoint files.\n")
        
        import traceback
        if input("Show full error trace? (y/n): ").strip().lower() in ['y', 'yes']:
            print("\n" + "─" * 70)
            traceback.print_exc()
            print("─" * 70 + "\n")
        
        sys.exit(1)


if __name__ == "__main__":
    main()