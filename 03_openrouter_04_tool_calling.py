import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is missing. Please add it to your .env file.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "OpenRouter Tool Calling Tutorial"
    }
)


# ---------------------------------------------------------
# 1. Real Python function that your application controls
# ---------------------------------------------------------
def calculate_total_price(quantity: int, unit_price: float, tax_rate: float = 0.0) -> dict:
    """
    Calculate subtotal, tax, and final total.
    """

    subtotal = quantity * unit_price
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    return {
        "quantity": quantity,
        "unit_price": unit_price,
        "tax_rate": tax_rate,
        "subtotal": round(subtotal, 2),
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2)
    }


# ---------------------------------------------------------
# 2. Tool schema shown to the model
# ---------------------------------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_total_price",
            "description": "Calculate the total price based on quantity, unit price, and optional tax rate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "quantity": {
                        "type": "integer",
                        "description": "Number of items being purchased."
                    },
                    "unit_price": {
                        "type": "number",
                        "description": "Price of one item."
                    },
                    "tax_rate": {
                        "type": "number",
                        "description": "Tax rate as a decimal. Example: 0.13 for 13% tax."
                    }
                },
                "required": ["quantity", "unit_price"],
                "additionalProperties": False
            }
        }
    }
]


# ---------------------------------------------------------
# 3. Map tool name to actual Python function
# ---------------------------------------------------------
available_functions = {
    "calculate_total_price": calculate_total_price
}


def ask_with_tool_calling(user_prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "Use tools when calculation is needed. "
                "Do not do arithmetic manually if a calculation tool is available."
            )
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    # -----------------------------------------------------
    # First model call: model decides whether it needs a tool
    # -----------------------------------------------------
    first_response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.2,
        max_tokens=500
    )

    assistant_message = first_response.choices[0].message

    print("\nFirst model response:")
    print(assistant_message)

    # -----------------------------------------------------
    # If no tool call is needed, return normal answer
    # -----------------------------------------------------
    if not assistant_message.tool_calls:
        return assistant_message.content

    # Add assistant message with tool call to conversation
    messages.append(assistant_message)

    # -----------------------------------------------------
    # Execute each tool call locally in Python
    # -----------------------------------------------------
    for tool_call in assistant_message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        print("\nTool requested by model:")
        print("Function:", function_name)
        print("Arguments:", function_args)

        if function_name not in available_functions:
            raise ValueError(f"Function {function_name} is not available.")

        function_to_call = available_functions[function_name]
        function_result = function_to_call(**function_args)

        print("\nPython function result:")
        print(function_result)

        # Send tool result back to the model
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(function_result)
            }
        )

    # -----------------------------------------------------
    # Second model call: model uses tool result to answer user
    # -----------------------------------------------------
    final_response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages,
        temperature=0.2,
        max_tokens=500
    )

    return final_response.choices[0].message.content


if __name__ == "__main__":
    prompt = "I bought 3 items at $19.99 each. Tax is 13%. What is my final total?"

    try:
        answer = ask_with_tool_calling(prompt)

        print("\nFinal Answer:\n")
        print(answer)

    except Exception as e:
        print("\nTool calling failed.")
        print("Error:")
        print(e)