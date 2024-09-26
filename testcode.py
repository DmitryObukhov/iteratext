# simple_pydictionary_example.py

from PyDictionary import PyDictionary

# Initialize the PyDictionary object
dictionary = PyDictionary()

# Prompt the user for a word
word = 'test'

if word:
    # Get synonyms
    synonyms = dictionary.synonym(word)
    if synonyms:
        print(f"\nSynonyms for '{word}':")
        print(', '.join(synonyms))
    else:
        print(f"\nNo synonyms found for '{word}'.")

    # Get antonyms
    antonyms = dictionary.antonym(word)
    if antonyms:
        print(f"\nAntonyms for '{word}':")
        print(', '.join(antonyms))
    else:
        print(f"\nNo antonyms found for '{word}'.")

    # Get definitions
    definitions = dictionary.meaning(word)
    if definitions:
        print(f"\nDefinitions for '{word}':")
        for part_of_speech, defs in definitions.items():
            print(f"{part_of_speech}:")
            for d in defs:
                print(f" - {d}")
    else:
        print(f"\nNo definitions found for '{word}'.")
else:
    print("No word entered.")
