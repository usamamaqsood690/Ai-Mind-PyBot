# chatbot/views.py

import os
import json
import google.generativeai as genai
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Configure the generative AI model
genai.configure(api_key=settings.GEMINI_API_KEY)

generation_config = {
    "temperature": 0.5,
    "top_p": 0.85,
    "top_k": 40,
    "max_output_tokens": 300,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

initial_system_prompt = (
     "You are a friendly assistant helping students kids learn only Python not support any other language and is specfic to python related queries."
     "Provide python specfic responses that are clear, explained in 9-10 lines, using simple language and relevant emojis to make explanations engaging and fun for kids."
     "When asking for any code dont give programs in which user should enter input. "
     "When explaining code, provide explanations in separate lines, and wrap code in triple backticks (```) to indicate code blocks. Before code block add Code heading in bold"
     "Use simple language, emojis, and bold keywords like `input` and `print` to make responses engaging and clear. "
     "We're getting an error because of how the `input` is used. Let's fix it!\n\n"
     "Add a positive encouragement message at the end, like 'Give it a shot and hit Run again"
     "Structure your responses with headings, bullet points, and numbered lists for clarity when needed. "
     "Bold headings with <strong>, bullet points, and numbered lists for clarity when needed. "
     "For any text that should be bold, replace the asterisks (`**`) with `<strong>` tags and avoid displaying the asterisks themselves. "
     "For example, if you need to display the word **Methods**, it should appear as <strong>Methods</strong>, without any asterisks appearing in the output. "
     "Avoid asterisks (`*`, `**`, `***`) or backticks (`) for emphasis and always use `<strong>` tags to indicate bold text."
     "You are a friendly Python tutor for kids, focused on providing explained answers that are clear and fun. "
     "Remove asterisks (`*`, `**`, `***`) or backticks (`) "
     "Use positive and motivational expressions like 'You're doing great!' to encourage learners. Add emoji as well "
     "Provide medium level explanations or unnecessary details—stick to the essentials.\n\n"
     "Response structure in Code related prompts:\n"
     "Example response format:\n\n"
     "Use a cheerful tone with relevant emojis to keep responses engaging and simple. "
     "Keep explanations brief (1-2 sentences) and focus only on Python concepts. "
     "Next step:\nTo display 'Hello', use `print` without `input`.\n\n"
     "Code:\n```\nprint(\"Hello\")\n```\n\n."
     "Response structure in Execution success and Execution failed:\n"
     "- Start with a friendly, expressive tone (e.g., 'Uh oh, looks like a small mistake'). Bold this tone and add emoji as well\n"
     "- Provide a **short explanation** (1-2 sentences). But not add explanation heading\n"
     "- Bold this next step \n\n. Give a simple **next step** to fix the issue.\n"
     "- Add a relevant **Python code snippet** wrapped in triple backticks (```).\n"
     "- End with a positive encouragement message like 'You got this'. Add emoji as well\n\n"
 )
chat_session.send_message(initial_system_prompt)

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
            user_input = request_data.get('input', '')

            if not user_input.strip():
                return JsonResponse({"response": "No input provided"}, status=400)

            # Check if the input is code for execution
            if user_input.startswith("Code Execution:"):
                code = user_input.replace("Code Execution:", "").strip()
                response = chat_session.send_message(
                    f"Execute and explain the following Python code:\n{code}"
                )
            else:
                # Handle as a regular chatbot message
                response = chat_session.send_message(user_input)

            return JsonResponse({"response": response.text})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chat_response(request):
    if request.method == "POST":
        # Sample structured HTML response
        response_text = """
            <strong>Error Analysis:</strong>
            <ul>
                <li><strong>Issue:</strong> <code>SyntaxError: unterminated string literal</code></li>
                <li><strong>Explanation:</strong> You've opened a string literal with a double quote <code>"</code> but haven't closed it with another double quote.</li>
            </ul>

            <strong>Solution:</strong>
            <pre class="code-block">
            print("hello")
            </pre>

            <strong>Explanation:</strong> To correct the code, ensure that every opening quote has a corresponding closing quote. The correct syntax is shown above, which will correctly print the string "hello" to the console.
        """

        response_data = {
            'response': response_text
        }

        return JsonResponse(response_data)



# compiler/views.py

import subprocess
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
import requests

def python_editor_view(request):
    return render(request, 'index.html')

def run_python_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
    
    # Check if the code contains 'input()' and return an error message if it does
        if 'input(' in code:
            return JsonResponse({'output': "I/O Error: user interaction 'input()' is not handled"})
       
        cleaned_code = "\n".join(line.rstrip() for line in code.splitlines())

        # Save the code to a temporary Python file
        with open('temp_code.py', 'w') as f:
            f.write(cleaned_code)

        # Run the code and capture output
        try:
            output = subprocess.check_output(['python', 'temp_code.py'], stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
       # Extract only the last line of the error message
            output = e.output.strip().splitlines()[-1]

        # Format code with "Code Execution:" prefix to indicate it's a code block for the chatbot
        formatted_code = f"Code Execution: {code}"

        # Send code directly to the chatbot to request execution and explanation
        chatbot_url = request.build_absolute_uri(reverse('chat'))
        chatbot_response = requests.post(chatbot_url, json={"input": formatted_code}).json().get("response", "Error getting chatbot response.")

        return JsonResponse({'output': output, 'chatbot_response': chatbot_response})

    return JsonResponse({'output': 'Invalid request'}, status=400)

