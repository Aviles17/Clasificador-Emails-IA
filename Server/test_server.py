import unittest
import json
from main_server import app # Import app

class TestServer(unittest.TestCase):
    
    #Inicializar el servidor para las pruebas unitarias
    def setUp(self):
        self.app = app.test_client()
    #Prueba de que el servidor fue ejecutado correctamente y el root esta desplegado  
    def test_server_is_up(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    #Prueba de que el modelo de Naive Bayes esta corriendo y calculando correctamente
    def test_naive_bayes_predict(self):
        with open('Server/recursos/email_1.json') as f:
           test_data = json.load(f)
        response = self.app.post('/NaiveBayesPredict', json=test_data)
        c_good_response = response.status_code == 200
        c_good_predict = response.text == "0.0"
        self.assertEqual(c_good_response and c_good_predict, True)

if __name__ == '__main__':
  unittest.main()