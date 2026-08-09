import ollama
import requests
import json

# 1. Define the Tool (The Hands)
def search_local_images(search_term: str) -> str:
    """Searches the user's local computer for images matching the description."""
    print(f"\n[System: Agent is searching your files for '{search_term}'...]")
    
    try:
        # Call our FastAPI backend we built earlier
        response = requests.post(
            "http://127.0.0.1:8000/search",
            json={"text": search_term, "top_k": 2}
        )
        data = response.json()
        
        # Format the results so the AI brain can read them
        if not data.get("results"):
            return "No images found."
            
        results_formatted = [f"Found {r['file_path']} (Match score: {r['confidence_score']:.2f})" for r in data["results"]]
        return " | ".join(results_formatted)
        
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the image search server. Is main.py running?"
    except Exception as e:
        return f"Error searching images: {e}"

# 2. Define the Agent Loop (The Brain)
def run_chat():
    print("FileSearchHelper is online! (Type 'exit' to quit)")
    
    # Give the agent its personality and instructions
    messages = [{
        "role": "system", 
        "content": "You are FileSearchHelper, an offline AI assistant. If the user asks for a photo or image, use the search_local_images tool to find it. Keep your replies friendly and concise."
    }]
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
            
        messages.append({"role": "user", "content": user_input})
        
        # Send the chat history AND our tool to Llama 3.1
        response = ollama.chat(
            model='llama3.1',
            messages=messages,
            tools=[search_local_images] # Ollama automatically reads the python function!
        )
        
        # 3. Handle Tool Calls
        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                if tool_call.function.name == 'search_local_images':
                    # The AI decided to use the tool. Extract what it wants to search.
                    search_term = tool_call.function.arguments.get('search_term')
                    
                    # Actually run the python function
                    tool_result = search_local_images(search_term)
                    
                    # Add the AI's tool request and the tool's result to the history
                    messages.append(response.message) 
                    messages.append({
                        "role": "tool",
                        "content": tool_result
                    })
                    
                    # Let the AI read the results and generate a final reply to the user
                    final_response = ollama.chat(model='llama3.1', messages=messages)
                    print(f"\nAgent: {final_response.message.content}")
                    messages.append(final_response.message)
        else:
            # The AI just wanted to chat normally, no tools needed
            print(f"\nAgent: {response.message.content}")
            messages.append(response.message)

if __name__ == "__main__":
    run_chat()