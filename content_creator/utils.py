import google.generativeai as genai
from django.conf import settings
from PIL import Image
import requests
from io import BytesIO
import random   
import re
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize

# Configure the Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_blog_content(title, keywords):
    prompt = f"Write a blog post with the title '{title}'. Use the following keywords: {keywords}. The blog post should be informative, engaging, unique content, in proper HTML format with no css and between 1000-1500 words, generate_unique_content with your own logic to ensure the generated content is truly unique and plagiarism-free."
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    max_attempts = 5
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = model.generate_content(prompt)
            
            if response.text:
                content = response.text
                content = re.sub(r'## (.*?)($|\n)', r'<h2>\1</h2>\2', content)
    
                content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
                
                content = re.sub(r'<br><b>(.*?)</b>', r'<br><b>\1</b>', content)
                
                content = re.sub(r'(\d+)\.\s+', r'<br> <b>\1. </b>', content)
                
                content = re.sub(r'^\*\s+', '<br> • ', content, flags=re.MULTILINE)
                return content
            
            attempt += 1
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            attempt += 1
    
    raise Exception("Generated content is not unique. Please try again.")

def is_valid_html(content):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        return soup.find() is not None
    except:
        return False

def convert_to_html(content):
    content = content.replace('\n', '<br>')
    
    if not re.match(r'^\s*<(div|p|h[1-6]|ul|ol|table|blockquote)', content, re.IGNORECASE):
        content = f'<p>{content}</p>'
    
    if not re.match(r'^\s*<html', content, re.IGNORECASE):
        content = f'<html><body>{content}</body></html>'
    
    return content

def get_image_from_pixabay(title):
    pixabay_api_key = settings.PIXABAY_API_KEY
    url = f"https://pixabay.com/api/?key={pixabay_api_key}&q='{title}'"
    print("url_images",url)
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['hits']:
            return data['hits'][0]['webformatURL']

    return f"https://via.placeholder.com/800x400?text={title.replace(' ', '+')}"

def generate_image(title):
    return get_image_from_pixabay(title)

def check_plagiarism(content):

    nltk.download('punkt', quiet=True)
    sentences = sent_tokenize(content)
    plagiarized_sentences = []

    for i, sentence in enumerate(sentences):
        if random.random() < 0.1:  # 10% chance of being "plagiarized"
            plagiarized_sentences.append({
                'index': i,
                'sentence': sentence
            })

    plagiarism_percentage = (len(plagiarized_sentences) / len(sentences)) * 100

    return round(plagiarism_percentage, 2), plagiarized_sentences

def remove_plagiarism(content):
    """
    Simple plagiarism removal function.
    In a real-world scenario, this would involve more sophisticated techniques
    or integration with a paraphrasing service.
    """
    # Download necessary NLTK data
    nltk.download('punkt', quiet=True)

    # Tokenize the content into sentences
    sentences = sent_tokenize(content)

    # Simulate plagiarism removal by slightly modifying each sentence
    # This is just for demonstration purposes
    modified_sentences = []
    for sentence in sentences:
        if random.random() < 0.1:  # Simulate that 10% of sentences need modification
            words = sentence.split()
            if len(words) > 3:
                # Swap two random words
                i, j = random.sample(range(len(words)), 2)
                words[i], words[j] = words[j], words[i]
            modified_sentence = ' '.join(words)
        else:
            modified_sentence = sentence
        modified_sentences.append(modified_sentence)

    # Join the modified sentences back into a single text
    clean_content = ' '.join(modified_sentences)

    return clean_content

def gemini_paraphrase(content):
    """
    Use Gemini to paraphrase the given content.
    This function requires a Google AI API key to be set in your Django settings.
    """
    genai.configure(api_key=settings.GEMINI_API_KEY)

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Paraphrase the following text to remove potential plagiarism while maintaining the original meaning:

        {content}

        Paraphrased version:
        """
        
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text.strip()
        else:
            print("Gemini returned an empty response.")
            return content  # Return original content if paraphrasing fails
    except Exception as e:
        print(f"Error in Gemini paraphrasing: {str(e)}")
        return content  # Return original content if paraphrasing fails

# @memory.cache
# def check_plagiarism(content):
#     sentences = re.split(r'(?<=[.!?])\s+', content)
#     total_sentences = len(sentences)
#     plagiarized_sentences = []
    
#     for i, sentence in enumerate(sentences):
#         search_url = f"https://www.google.com/search?q={sentence}"
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         response = requests.get(search_url, headers=headers)
        
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.text, 'html.parser')
#             search_results = soup.find_all('div', class_='g')
            
#             for result in search_results:
#                 snippet = result.find('div', class_='s')
#                 if snippet:
#                     similarity = SequenceMatcher(None, sentence, snippet.get_text()).ratio()
#                     if similarity > 0.8:
#                         plagiarized_sentences.append((i, sentence, similarity))
#                         break
    
#     plagiarism_percentage = (len(plagiarized_sentences) / total_sentences) * 100
#     return plagiarism_percentage, plagiarized_sentences

# def modify_content(content, plagiarism_percentage):
#     if plagiarism_percentage <= 10:
#         return content
    
#     sentences = re.split(r'(?<=[.!?])\s+', content)
#     modified_sentences = []
    
#     for sentence in sentences:
#         if random.random() < (plagiarism_percentage - 10) / 90:  # Probability of modifying based on how much we need to reduce
#             # Apply various modification techniques
#             modification = random.choice(['rephrase', 'expand', 'summarize'])
            
#             if modification == 'rephrase':
#                 modified_sentence = rephrase_sentence(sentence)
#             elif modification == 'expand':
#                 modified_sentence = expand_sentence(sentence)
#             else:
#                 modified_sentence = summarize_sentence(sentence)
            
#             modified_sentences.append(modified_sentence)
#         else:
#             modified_sentences.append(sentence)
    
#     return ' '.join(modified_sentences)

# def rephrase_sentence(sentence):
#     # Simple rephrasing logic (in practice, you'd use more sophisticated NLP techniques)
#     words = sentence.split()
#     if len(words) > 3:
#         mid = len(words) // 2
#         words[mid], words[mid-1] = words[mid-1], words[mid]
#     return ' '.join(words)

# def expand_sentence(sentence):
#     # Simple expansion logic
#     return f"{sentence} Furthermore, this point is crucial to understand the overall context."

# def summarize_sentence(sentence):
    # Simple summarization logic
    words = sentence.split()
    if len(words) > 5:
        return ' '.join(words[:len(words)//2]) + '.'
    return sentence