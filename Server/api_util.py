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

def process_message(message: dict):
    try:
        #Informacion del encabezado
        message_id = message['id']
        email_data = message['payload']['headers']
        asunto = "No Especificado"
        remitente = "No Especificado"
        for d in email_data:
            if d['name'] == 'Subject':
                asunto = d['value']
            elif d['name'] == 'From':
                remitente = d['value']
        #Información del correo
        temp_part = message['payload']['parts'][0]['body']
        if temp_part.get('size') == 0:
            temp_part = message['payload']['parts'][0]['parts']
            part = temp_part[0]['body']['data']
        else:
            part = temp_part['data']
                    
        data = part.replace("-","+").replace("_","/")
        decoded_data = base64.b64decode(data)
        soup = BeautifulSoup(decoded_data , "lxml")
        body = soup.body()
        
        ret_message = email_message(message_id, asunto, remitente, message['snippet'], clean_string(str(body[0])))
        if forwarded_message(ret_message.message):
            ret_message = manage_forwarded(ret_message)
        else:
            ret_message.message = clean_message(ret_message.message)
        
        return ret_message
        
    except Exception as e:
        print(e)
        return None

        
def clean_string(string: str):
    
    string = re.sub(r'<[^>]*>', '', string)
    
    # Remove links (URLs)
    string= re.sub(r'https?://\S+', '', string)
    
    # Remove double white spaces
    string = re.sub(r'\s+', ' ', string).strip()
    
    return string.split()

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
    
'''
-------------------------------------------------------------------------------------------------------------------------------------------------
A PARTIR DE AQUI ES MANEJO DE MENSAJES REENVIADOS Y TODOS LOS METODOS RELACIONADOS
-------------------------------------------------------------------------------------------------------------------------------------------------
'''


'''
###################################################################################
[Proposito]: Determinar si el mensaje que se pasa por parametro es un mensaje reenviado
[Parametros]: message_content (Lista que contiene el cuerpo del mensaje)
[Retorna]: Retorna valor booleano relacionado a si es (True) o no es (False) un mensaje reenviado
###################################################################################
'''
def forwarded_message(message_content: list):
    
    for word in message_content:
        if word == 'Forwarded':
            return True
    return False


'''
###################################################################################
[Proposito]: Funcion general que engloba todo el tratamiento de un mensaje reenviado
[Parametros]: message (Variable de tipo 'email_message' que contiene toda la informacion del mensaje)
[Retorna]: Retorna el mensaje ya tratado (Tratado: Cambiar remitente al original, cambiar asunto al original, quitar formato de reenvio)
###################################################################################
'''
def manage_forwarded(message: email_message):
    message = clean_forward_message_format(message)
    message = update_email_author(message)
    message.check_data_integrity()
    return message    
    

'''
###################################################################################
[Proposito]: Eliminar formato de reenviado y extraer información valiosa de este formato para posterior tratamiento
[Parametros]: message (Variable de tipo 'email_message' que contiene toda la informacion del mensaje)
[Retorna]: Retorna mensaje ya tratado (Tratado: Cambiar remitente al original, cambiar asunto al original, quitar formato de reenvio)
###################################################################################
'''
def clean_forward_message_format(message: email_message):
        #Create list with the order of the message
    order = [('De:','From:'), ('Date:', 'Dia:'), ('Subject:', 'Asunto:'), ('To:', 'Para:')]
    specific_symbols = ('----------','---------','------------------------------','Forwarded', 'message')
    new_Message = []
    index = 0
    forwarded_part = False
    while index < len(message.message):
        if message.message[index] in order[0]:
            new_Message.clear()
            new_index = index + 1
            new_from = ""
            while message.message[new_index] not in order[1]:
                new_from += message.message[new_index] + " "
                new_index += 1
                
            new_index += 1
            new_Date = ""
            while message.message[new_index] not in order[2]:
                new_Date += message.message[new_index] + " "
                new_index += 1
                
            new_index += 1
            new_Subject = ""
            while message.message[new_index] not in order[3]:
                new_Subject += message.message[new_index] + " "
                new_index += 1
                
            index = new_index + 1
        else:
            if message.message[index] in specific_symbols:
                forwarded_part = True
            else:
                if forwarded_part:
                    new_Message.append(message.message[index].lower())
            index += 1
    
    message.subject = new_Subject.strip()
    #Call function to standarize the from message
    message.by_email = new_from.strip()
    message.by_name = new_from.strip()
    message.message = clean_message(new_Message)
    
    return message


'''
###################################################################################
[Proposito]: Reestablecer el autor y su email original del mensahe a traves del cuerpo del mensaje
[Parametros]: message (Variable de tipo 'email_message' que contiene toda la informacion del mensaje)
[Retorna]: Retorna mensaje ya actualizado con los autores o por consiguiente la misma version si no se encuetra como hacer la modificación
###################################################################################
''' 
def update_email_author(message: email_message):
    if message.by_name == message.by_email:
        if ';' in message.by_name:
            try:
                #Manage domain email part
                mail_index = message.by_email.index('@')
                new_mail = message.by_email[mail_index:]
                message.by_email = new_mail[:-1]
                #Manage name part
                name_index = message.by_name.index(';')
                new_name = message.by_name[:name_index]
                message.by_name = new_name
            except ValueError:
                return message
            finally:

                return message
        else:
            #Find if the pattern is hidden in the snipet
            name_split = message.by_name.split()
            try:
                index = message.snippet.index(name_split[-1])
                cont = 0
                new_email = ""
                while cont < 2:
                    if message.snippet[index] == ';':
                        cont += 1
                    if message.snippet[index] != ';' and cont > 0:
                        new_email += message.snippet[index]
                    index += 1
                mail_index = new_email.index('@')
                message.by_email = new_email[mail_index:]
            except ValueError:
                message.by_email = None
                     
            finally:
                return message     
    else:
        return message
                
    
if __name__ == '__main__':
    print("This file is a module that only provides functionality")