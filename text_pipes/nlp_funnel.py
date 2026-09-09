import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Download required NLTK assets (run once)
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

#for NER:
nltk.download('maxent_ne_chunker')
nltk.download('words')

def extract_search_terms_nltk(sentence):
    # Split sentence into individual words
    words = word_tokenize(sentence)
    # Tag each word with its part of speech
    tagged_words = pos_tag(words)
    
    # Filter for Nouns (NN, NNS, NNP, NNPS) and Adjectives (JJ, JJR, JJS)
    allowed_tags = {'NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS'}
    
    keywords = [word for word, tag in tagged_words if tag in allowed_tags]
    
    # Join keywords into a clean search query string
    #return " ".join(keywords)
    return keywords

def extract_search_terms_nltk_NER(sentence):
    words = word_tokenize(sentence)
    tagged = pos_tag(words)
    # Groups words into named entity trees (like GPE for geopolitical entities)
    chunks = nltk.ne_chunk(tagged)
    
    extracted = []
    for chunk in chunks:
        # If it's a named entity tree (like a location or person)
        if hasattr(chunk, 'label'):
            entity_word = "".join([c[0] for c in chunk])
            extracted.append(entity_word)
        # If it's a regular word, check if it's a standard noun or adjective
        elif chunk[1] in {'NN', 'NNS', 'JJ'}:
            extracted.append(chunk[0])
            
    #return " ".join(extracted)
    return extracted


if __name__ == "__main__":
    # Example Usage
    sentence = "A fluffy golden retriever puppy happily chasing a bright red ball on the green grass."
    query = extract_search_terms_nltk(sentence)
    print(f"Original: {sentence}")
    print(f"SERP Query: {query}") 
    # Output: fluffy golden retriever puppy bright red ball green grass