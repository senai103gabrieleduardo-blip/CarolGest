from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, date
import uuid

# In-memory storage for MVP
users_db = {}
clients_db = {}
kanban_cards_db = {}
whatsapp_messages_db = {}

class User(UserMixin):
    def __init__(self, username, email, name, role='atendimento'):
        self.id = len(users_db) + 1
        self.username = username
        self.email = email
        self.name = name
        self.role = role  # admin, sales, atendimento
        self.password_hash = None
        self.created_at = datetime.now()
        self.active = True
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def save(user):
        users_db[user.id] = user
        return user
    
    @staticmethod
    def get(user_id):
        return users_db.get(user_id)
    
    @staticmethod
    def get_by_username(username):
        for user in users_db.values():
            if user.username == username:
                return user
        return None
    
    @staticmethod
    def get_all():
        return list(users_db.values())
    
    @staticmethod
    def delete(user_id):
        if user_id in users_db:
            del users_db[user_id]
            return True
        return False

class Client:
    def __init__(self, name, email, phone, cpf_cnpj, address='', insurance_type='', notes=''):
        self.id = len(clients_db) + 1
        self.name = name
        self.email = email
        self.phone = phone
        self.cpf_cnpj = cpf_cnpj
        self.address = address
        self.insurance_type = insurance_type
        self.notes = notes
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.status = 'ativo'
    
    @staticmethod
    def save(client):
        if hasattr(client, 'id') and client.id:
            client.updated_at = datetime.now()
        else:
            client.id = len(clients_db) + 1
        clients_db[client.id] = client
        return client
    
    @staticmethod
    def get(client_id):
        return clients_db.get(client_id)
    
    @staticmethod
    def get_all():
        return list(clients_db.values())
    
    @staticmethod
    def delete(client_id):
        if client_id in clients_db:
            del clients_db[client_id]
            return True
        return False
    
    @staticmethod
    def search(query):
        results = []
        query = query.lower()
        for client in clients_db.values():
            if (query in client.name.lower() or 
                query in client.email.lower() or 
                query in client.phone.lower() or
                query in client.cpf_cnpj.lower()):
                results.append(client)
        return results

class KanbanCard:
    def __init__(self, title, description, client_id, assigned_to, column='atendimento_inicial'):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.client_id = client_id
        self.assigned_to = assigned_to
        self.column = column  # atendimento_inicial, proposta_enviada, venda_andamento, venda_concluida, pos_venda
        self.priority = 'medium'  # low, medium, high
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.due_date = None
    
    @staticmethod
    def save(card):
        card.updated_at = datetime.now()
        kanban_cards_db[card.id] = card
        return card
    
    @staticmethod
    def get(card_id):
        return kanban_cards_db.get(card_id)
    
    @staticmethod
    def get_all():
        return list(kanban_cards_db.values())
    
    @staticmethod
    def get_by_column(column):
        return [card for card in kanban_cards_db.values() if card.column == column]
    
    @staticmethod
    def delete(card_id):
        if card_id in kanban_cards_db:
            del kanban_cards_db[card_id]
            return True
        return False
    
    @staticmethod
    def move_to_column(card_id, new_column):
        card = kanban_cards_db.get(card_id)
        if card:
            card.column = new_column
            card.updated_at = datetime.now()
            return True
        return False

class WhatsAppMessage:
    def __init__(self, sender, message, message_type='received', client_id=None):
        self.id = len(whatsapp_messages_db) + 1
        self.sender = sender
        self.message = message
        self.message_type = message_type  # received, sent
        self.client_id = client_id
        self.timestamp = datetime.now()
        self.read = False
    
    @staticmethod
    def save(message):
        whatsapp_messages_db[message.id] = message
        return message
    
    @staticmethod
    def get_all():
        return sorted(whatsapp_messages_db.values(), key=lambda x: x.timestamp, reverse=True)
    
    @staticmethod
    def get_by_client(client_id):
        return [msg for msg in whatsapp_messages_db.values() if msg.client_id == client_id]
    
    @staticmethod
    def mark_as_read(message_id):
        message = whatsapp_messages_db.get(message_id)
        if message:
            message.read = True
            return True
        return False
