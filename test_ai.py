from ai_planner.src.agents.parser import extract_schedule_goals

if __name__ == "__main__":
    print("🤖 Sending request to local Llama 3 via Ollama...")
    
    test_prompt = "I want to run tomorrow at 9 AM and eat breakfast at 11 AM. For breakfast I want syrnyky."
    
    try:
        extracted_data = extract_schedule_goals(test_prompt)
        print("\n🎉 Success! Extracted Goals:")
        print(extracted_data.model_dump_json(indent=2))
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
