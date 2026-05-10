# test_ai.py
from ai_planner.src.agents.parser import extract_schedule_goals
from ai_planner.src.tools.scheduler import calculate_backward_schedule
from shared.models.schemas import ProposedTimelineResponse
from datetime import datetime, timedelta, timezone
import uuid
import json

if __name__ == "__main__":
    print("🤖 Step 1: Sending request to local Llama 3 via Ollama...")
    
    test_prompt = "I want to run tomorrow at 9 AM and eat breakfast at 11 AM. For breakfast I want syrnyky."
    
    try:
        # 1. Run LLM parsing
        extracted_goals = extract_schedule_goals(test_prompt)
        print("🎉 Success! Extracted Goals from text.")
        
        print("\n🧮 Step 2: Running Backward Scheduling Engine...")
        # 2. Compute timeline math
        tomorrow = datetime.now() + timedelta(days=1)
        computed_tasks = calculate_backward_schedule(extracted_goals, target_date=tomorrow)
        
        # 3. Build final contract response
        final_response = ProposedTimelineResponse(
            request_id=str(uuid.uuid4()),
            status="success",
            calculated_at=datetime.now(timezone.utc),
            timeline=computed_tasks
        )
        
        print("\n🏆 Final Calculated Day Plan:")
        # We use json.loads & dumps just to print the Pydantic model with beautiful indentation
        print(json.dumps(json.loads(final_response.model_dump_json()), indent=2))
        
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")