from openai import OpenAI
import re

class Chatgpt:
    def __init__(self, global_config):
        # Initialize the API key from the global configuration
        self.api_key = global_config.get('OPEN_AI_API_KEY')
        if not self.api_key:
            raise ValueError("Error: OPEN_AI_API_KEY not found in global configuration.")

        # Create the OpenAI client
        self.client = OpenAI(api_key=self.api_key)

    def process(self, text, params):
        # Get the prompt template from params
        prompt_template = params.get('prompt', '')
        if not prompt_template:
            return "Error: Prompt template not provided in function configuration."

        # Recursive placeholder replacement
        prompt = self.replace_placeholders(prompt_template, text, params)

        # Get model, max_tokens, and temperature from params, with default values
        model = params.get('model', 'gpt-3.5-turbo')   # Default model
        max_tokens = params.get('max_tokens', 500)     # Default max tokens
        temperature = params.get('temperature', 0.7)   # Default temperature

        try:
            # Make the API call using client.chat.completions.create
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract the assistant's reply
            assistant_reply = response.choices[0].message.content
            return assistant_reply.strip()

        except Exception as e:
            return f"Error communicating with OpenAI API: {e}"

    def replace_placeholders(self, prompt, src_text, params):
        # Function to recursively replace placeholders within the prompt
        pattern = re.compile(r'(?<!\\)\{(.*?)(?<!\\)\}')
        iteration = 0
        max_iterations = 10  # Prevent infinite loops

        while True:
            matches = pattern.findall(prompt)
            if not matches or iteration >= max_iterations:
                break
            for match in matches:
                placeholder = f'{{{match}}}'
                replacement = ''

                if match == 'SRC_TEXT':
                    replacement = src_text.strip()
                else:
                    # If the placeholder is in params, use its value
                    replacement = params.get(match, '')

                prompt = prompt.replace(placeholder, replacement)
            iteration += 1

        # Unescape any escaped braces
        prompt = prompt.replace('\{', '{').replace('\}', '}')

        return prompt
