import os
import json
import google.generativeai as genai
from calculator_tool import calculator_tool


class CalculatorAgent:
    """
    An agent that uses Gemini 3 Pro to understand natural language
    and decides when to use the calculator tool
    """
    
    def __init__(self, api_key=None):
        """Initialize the agent with Google API"""
        genai.configure(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-3-pro-preview')
    
    def run(self, user_question):
        """
        Main agent loop:
        1. Send question to Gemini
        2. Gemini decides if it needs the calculator tool
        3. If yes, extract expression and use tool
        4. Return result to user
        """
        
        print(f"\n{'='*50}")
        print(f"Question: {user_question}")
        print(f"{'='*50}\n")
        
        # Step 1: Ask Gemini to analyze the question
        print("🤔 Agent thinking...")
        
        system_prompt = """You are a calculator agent. Your job is to:
1. Determine if the user's question is a math calculation
2. If yes, extract the mathematical expression
3. Respond with JSON only

Response format:
- If it's math: {"action": "calculate", "expression": "the math expression"}
- If not math: {"action": "cannot_help", "reason": "why you can't help"}

Examples:
- "What is 5 + 3?" → {"action": "calculate", "expression": "5 + 3"}
- "Calculate 100 times 4" → {"action": "calculate", "expression": "100 * 4"}
- "What's the weather?" → {"action": "cannot_help", "reason": "Not a math question"}

Important: 
- Use * for multiplication (not x or times)
- Use / for division
- Only respond with JSON, nothing else"""

        # Create the full prompt
        full_prompt = f"{system_prompt}\n\nUser question: {user_question}"
        
        # Call Gemini
        response = self.model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        print(f"💭 Agent decision: {response_text}\n")
        
        # Step 2: Parse Gemini's decision
        try:
            decision = json.loads(response_text)
        except json.JSONDecodeError:
            return "Error: Agent returned invalid response"
        
        # Step 3: Execute based on decision
        if decision["action"] == "calculate":
            expression = decision["expression"]
            print(f"🔧 Using calculator tool with: {expression}")
            
            result = calculator_tool(expression)
            
            if result["success"]:
                return f"✓ Answer: {result['result']}"
            else:
                return f"✗ Calculator error: {result['error']}"
        
        elif decision["action"] == "cannot_help":
            return f"✗ {decision['reason']}"
        
        else:
            return "Error: Unknown action from agent"


def main():
    """Run the calculator agent"""
    
    print("\n" + "="*50)
    print("CALCULATOR AGENT - Step 2")
    print("Using Gemini 3 Pro Preview")
    print("Agent can understand natural language!")
    print("="*50)
    
    # Check for API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("\n⚠️  Error: GOOGLE_API_KEY not found in environment variables")
        print("Please set it with: export GOOGLE_API_KEY='your-key-here'")
        return
    
    # Initialize agent
    agent = CalculatorAgent()
    
    print("\nType 'quit' to exit")
    print("\nTry asking in natural language:")
    print("  - 'What is 25 times 4?'")
    print("  - 'Calculate 100 divided by 5'")
    print("  - 'What's 50 plus 30?'")
    print()
    
    # Interactive loop
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        # Run the agent
        result = agent.run(user_input)
        print(f"\n{result}")


if __name__ == "__main__":
    main()