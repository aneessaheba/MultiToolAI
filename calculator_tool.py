def calculator_tool(expression):
    """
    A simple calculator tool that evaluates mathematical expressions.
    
    Args:
        expression (str): Mathematical expression like "5 + 3"
    
    Returns:
        dict: Result or error message
    """
    try:
        # Safety check: only allow numbers and basic operators
        allowed_chars = set('0123456789+-*/.(). ')
        if not all(c in allowed_chars for c in expression):
            return {
                "success": False,
                "error": "Invalid characters in expression"
            }
        
        # Evaluate the expression
        result = eval(expression)
        
        return {
            "success": True,
            "result": result
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    print("Simple Calculator Tool")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("Calculate: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_input:
            continue
        
        result = calculator_tool(user_input)
        
        if result["success"]:
            print(f"Result: {result['result']}\n")
        else:
            print(f"Error: {result['error']}\n")


if __name__ == "__main__":
    main()