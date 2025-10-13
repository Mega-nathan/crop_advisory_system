#API-1 AIzaSyBe2HCiWw66iyKzuyj-io2mJCvXE66Yr3c
#API-2 AIzaSyB9SdQO_f4O_wBnhhYiEBjYc5pXaRLhlz4

from google import genai
import re

# Initialize the Gemini client with your API key
client = genai.Client(api_key="AIzaSyCyF6PwqDrwuP92-JBPQ2tBdnhjm_fEWvg")


def get_bot_response(user_input):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_input
    )
    return response.text

def preprocess_bot_response(text):
    """
    Preprocesses the bot response to make it suitable for front-end display.
    """
    # 1. Replace Markdown headings with simple bold text
    text = re.sub(r'##\s*(.+)', r'<b>\1</b>', text)
    
    # 2. Replace numbered lists with HTML <ol><li>
    # Matches lines starting with "1. ", "2. ", etc.
    lines = text.split('\n')
    formatted_lines = []
    in_list = False

    for line in lines:
        line = line.strip()
        if re.match(r'^\d+\.\s', line):
            if not in_list:
                formatted_lines.append('<ol>')
                in_list = True
            item = re.sub(r'^\d+\.\s', '', line)
            formatted_lines.append(f'<li>{item}</li>')
        else:
            if in_list:
                formatted_lines.append('</ol>')
                in_list = False
            if line:  # Avoid adding empty lines
                formatted_lines.append(f'<p>{line}</p>')

    if in_list:
        formatted_lines.append('</ol>')

    # Join all together
    return '\n'.join(formatted_lines)