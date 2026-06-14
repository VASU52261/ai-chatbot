import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

def main():
    # Load environment variables
    load_dotenv()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set in the .env file or environment variables.")
        sys.exit(1)

    try:
        client = genai.Client(api_key=api_key)
        # Using the model specified in the new requirements
        model = "gemini-2.5-flash-lite"
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")
        sys.exit(1)

    print("Welcome to the Gemini Chatbot!")
    print("Type 'exit', 'quit', 'stop', or 'end' to terminate.\n")

    # Store the last 10 messages
    messages = []
    
    # Configure tools and system instructions
    tools = [
        types.Tool(googleSearch=types.GoogleSearch()),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
        tools=tools,
        system_instruction=[
            types.Part.from_text(text="i want the answer in 10 words"),
        ],
    )

    while True:
        try:
            user_input = input("User: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'stop', 'end']:
                print("Bot: Goodbye!\n")
                print("Application terminated successfully.")
                break
                
            # Add user message to history
            messages.append(f"User: {user_input}")
            
            # Truncate to the last 10 messages (to save memory)
            if len(messages) > 10:
                messages = messages[-10:]
                
            # Combine history into a single text prompt
            context = "\n".join(messages)
            
            # Build the types.Content object as required by the new configuration
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=context),
                    ],
                ),
            ]

            print("Bot: ", end="", flush=True)
            bot_reply = ""
            
            # Stream the response
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if text := chunk.text:
                    print(text, end="", flush=True)
                    bot_reply += text
            
            print("\n") # Add a final newline when streaming is finished
            
            # Add bot response to history
            messages.append(f"Bot: {bot_reply}")
            
            # Truncate again in case adding the bot reply exceeded 10 messages
            if len(messages) > 10:
                messages = messages[-10:]
            
        except genai_errors.APIError as e:
            print(f"\nAPI Error occurred: {e}\n")
        except ConnectionError as e:
            print(f"\nNetwork Error occurred: {e}\n")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}\n")

if __name__ == "__main__":
    main()
