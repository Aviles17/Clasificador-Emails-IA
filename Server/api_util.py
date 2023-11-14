import base64
from bs4 import BeautifulSoup
import re
import nltk 
from nltk.corpus import stopwords
from email_message import email_message


def get_stopwords(lan : str = 'spanish'):
    
    nltk.download('stopwords', quiet= True)
    stw= stopwords.words(lan)
    
    return stw
        
def clean_message(message: list):
    #Crear nueva lista de palabras
    new_word_bag = []
    for word in message:
        #Crear directorios con strings predeterminados para limpiar
        text_symbols = ['+', '-', '*', '/', '%','==', '!=', '<', '>', '<=', '>=','=', '+=', '-=', 
                        '*=', '/=', '%=','&', '|', '^', '~', '<<', '>>',',', ':', ';', '.', '(', ')'
                        '[',']', '{', '}', ':']
        delete_word = False
        #Revise stopwords with nltk
        if not delete_word:
            stopwords = get_stopwords('spanish')
                
            for stopword in stopwords:
                if str(stopword) == word:
                    delete_word = True
                    break
        #Revise text symbols in unitary form
        if not delete_word:
            for symbol in text_symbols:
                if symbol == word:
                    delete_word = True
                    break
                
        #Revise if there is a extra email in the word_bag
        if not delete_word:
            if '@' in list(word):
                delete_word = True
            
        #If it passes all filters add to the new bag of words
        if not delete_word:
            new_word_bag.append(delete_extra_symbols(word.lower()))
                
        
    return new_word_bag
            
def delete_extra_symbols(working_string: str):
    pattern = r'^[*,.\-]*([\w\s]+)[*,.\-]*$'
    match = re.match(pattern, working_string)
    
    if match:
        clean_string = match.group(1)
        return clean_string
    else:
        return working_string
    
    
if __name__ == '__main__':
    print("This file is a module that only provides functionality")