import requests

from transformers import pipeline
from bs4 import BeautifulSoup as BeautifulSoup
from transformers import AutoTokenizer


class TextProcessing:
    def __init__(self, 
                 url, 
                 summarizer_model = "t5-base", 
                 translation_model = "Helsinki-NLP/opus-mt-es-en"):
        """
        Initialize the RAGFunctions class.

        :param url: The base URL for the API.
        """
        self.url = url
        self.summarizer_model = summarizer_model
        self.translation_model = translation_model


    def scrape_web_page_body(self):
        """
        Scrapes the content of a given web page URL.
        """
        try:
            headers = {'Accept-Language': 'es',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers)
            print(f"Response status code for {self.url}: {response.status_code}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Detect the language
                lang = soup.find("html").get("lang", "Unknown")
                print(f"Detected language for {self.url}: {lang}")

                # Remove unwanted tags such as menus, footers, and headers
                for tag in soup.find_all(["nav", "header", "footer", "script", "style"]):
                    tag.decompose()  # Remove the tag from the soup

                # Check main
                body = soup.main

                if body:
                    page_text = soup.get_text(separator="\n", strip=True)
                    return lang, page_text
                else:
                    print(f"Failed to retrieve page: {response.status_code}")
                    return ""
            
            else:
                print(f"Failed to retrieve page: {response.status_code if response else 'No response'}")
                return ""
            
        except Exception as e:
            print(f"Error occurred while scraping {self.url}: {e}")
            return ""
        
        
    def translate_text_to_english(self, text, max_tokens=400):
        """
        Translates Spanish text to English in chunks based on token limits.

        Args:
            text (str): The text to translate.
            max_tokens (int): The maximum number of tokens for chunking.

        Returns:
            str: Translated text in English.
        """
        try:
            # Validate input
            if not text or len(text.strip()) == 0:
                return "No text to translate."

            # Tokenizer and translator are assumed to be initialized during object creation
            tokenizer = AutoTokenizer.from_pretrained(self.translation_model)
            translator = pipeline("translation", model=self.translation_model)

            # Encode text into token IDs
            input_ids = tokenizer.encode(text, return_tensors="pt", add_special_tokens=False)[0]

            # Split tokens into chunks
            chunks = [input_ids[i:i + max_tokens] for i in range(0, len(input_ids), max_tokens)]

            translated_chunks = []
            for chunk in chunks:
                # Decode tokens back into text
                chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
                
                # Translate the chunk
                translation = translator(chunk_text, max_length=max_tokens)
                translated_chunks.append(translation[0]['translation_text'])

            # Combine all translated chunks
            return " ".join(translated_chunks)

        except Exception as e:
            return f"Error in translation: {e}"
            
    
    def process_with_open_model(self, text, coffee_name):
        """
        Uses an open-source summarization model to extract coffee characteristics from text.
        """

        prompt = f"""
        You are an expert in coffee tasting and analysis. Your task is to extract and organize detailed coffee characteristics from the following text for the coffee named "{coffee_name}".

        Please provide the extracted information in a structured table format with each characteristic clearly labeled and explained. Ensure all information is concise, accurate, and based only on the provided text.

        Format your output as follows:
        - **Altitude**: [Specify the altitude, e.g., 1,600m, including units if available.]
        - **Origin**: [Specify the geographical origin or region.]
        - **Flavor Profile**: [List key flavor notes, e.g., fruity, chocolate, citrus.]
        - **Roast Level**: [Specify the roast level, e.g., light, medium, dark.]
        - **Processing Method**: [Describe the coffee's processing method, e.g., natural, washed.]
        - **Notes**: [Include any additional information about the coffee, such as its aroma, texture, or unique characteristics.]

        Text to analyze:
        {text}
        """

        summarizer = pipeline("summarization", model=self.summarizer_model)

        try:
            # Use the summarization pipeline to parse the text
            summary = summarizer(prompt, max_length=500, min_length=50, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            return f"Error with open model processing: {e}"