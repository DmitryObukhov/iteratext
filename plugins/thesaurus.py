import nltk
from nltk.corpus import wordnet as wn

class Thesaurus:
    def __init__(self, global_config):
        # Ensure WordNet data is loaded
        try:
            wn.ensure_loaded()
        except:
            nltk.download('wordnet')
            wn.ensure_loaded()
        pass

    def process(self, text, params):
        # Get the word from the input text
        word = text.strip()
        if not word:
            return "Error: No input text provided for thesaurus lookup."

        # Get additional parameters
        pos = params.get('part_of_speech', None)  # 'noun', 'verb', 'adj', 'adv'
        pos_mapping = {
            'noun': wn.NOUN,
            'verb': wn.VERB,
            'adj': wn.ADJ,
            'adv': wn.ADV
        }
        wn_pos = pos_mapping.get(pos, None)

        try:
            # Get synsets for the word
            synsets = wn.synsets(word, pos=wn_pos)
            if not synsets:
                return f"No entries found for '{word}'."

            definitions = []
            synonyms = set()
            antonyms = set()

            for synset in synsets:
                # Get definition
                definitions.append(f"{synset.definition()}")

                # Get synonyms and antonyms
                for lemma in synset.lemmas():
                    # Synonyms
                    synonym = lemma.name().replace('_', ' ')
                    synonyms.add(synonym)
                    # Antonyms
                    for antonym in lemma.antonyms():
                        antonym_name = antonym.name().replace('_', ' ')
                        antonyms.add(antonym_name)

            # Remove the original word from synonyms
            synonyms.discard(word)
            synonyms.discard(word.lower())
            synonyms.discard(word.capitalize())

            # Format the output
            output = f"Definitions for '{word}':\n"
            for i, definition in enumerate(definitions, 1):
                output += f"{i}. {definition}\n"

            if synonyms:
                output += f"\nSynonyms for '{word}':\n"
                output += ', '.join(sorted(synonyms))

            if antonyms:
                output += f"\n\nAntonyms for '{word}':\n"
                output += ', '.join(sorted(antonyms))

            return output

        except Exception as e:
            return f"An error occurred: {e}"
