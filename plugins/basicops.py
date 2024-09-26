class Basicops:
    def __init__(self, global_config):
        # Initialize any required variables or configurations
        pass

    def process(self, text, params):
        # Get the operation from params
        operation = params.get('operation', 'uppercase')

        if operation == 'uppercase':
            return text.upper()
        elif operation == 'lowercase':
            return text.lower()
        elif operation == 'reverse':
            return text[::-1]
        else:
            return f"Unknown operation: {operation}"
