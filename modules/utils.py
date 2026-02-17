import os
import os
import google.generativeai as genai
import difflib

def generate_diff_html(original, revised):
    """
    Generates a simple HTML diff representation.
    Red background for deletions, Green background for additions.
    """
    d = difflib.Differ()
    diff = list(d.compare(original.splitlines(keepends=True), revised.splitlines(keepends=True)))
    
    html = []
    html.append('<div style="font-family: monospace; white-space: pre-wrap; background-color: #f0f0f0; padding: 10px; border-radius: 5px;">')
    
    for line in diff:
        code = line[:2]
        text = line[2:].rstrip()
        
        if code == '- ':
            html.append(f'<span style="background-color: #ffcccc; text-decoration: line-through;">{text}</span><br>')
        elif code == '+ ':
            html.append(f'<span style="background-color: #ccffcc;"><b>{text}</b></span><br>')
        elif code == '  ':
            html.append(f'<span>{text}</span><br>')
        # '?' lines are skipped (intraline diff indicators)
            
    html.append('</div>')
    return "".join(html)

def get_gemini_response(prompt, model_name="gemini-pro", temperature=0.7):
    """
    Simpler wrapper for Gemini API.
    Assumes GOOGLE_API_KEY is set in environment variables.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API Key not found")
        
    genai.configure(api_key=api_key)
    
    # Simple retry logic or error handling could go here
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature
            )
        )
        return response.text
    except Exception as e:
        return f"Error generating content: {str(e)}"
