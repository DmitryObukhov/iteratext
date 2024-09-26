import wikipedia

class Wiki:
    def __init__(self, global_config):
        pass  # No global configuration needed for this plugin

    def process(self, text, params):
        # Get the query from the input text
        query = text.strip()
        if not query:
            return "Error: No input text provided for Wikipedia search."

        # Get additional parameters
        sentences = params.get('sentences', 2)  # Default to 2 sentences

        try:
            # Search for the query on Wikipedia
            summary = wikipedia.summary(query, sentences=sentences)
            return summary
        except wikipedia.DisambiguationError as e:
            # If multiple pages match the query
            options = ', '.join(e.options[:5])  # Show first 5 options
            return f"Multiple entries found for '{query}': {options}"
        except wikipedia.PageError:
            # If no page matches the query
            return f"No Wikipedia page found for '{query}'."
        except Exception as e:
            # Handle other exceptions
            return f"An error occurred: {e}"
