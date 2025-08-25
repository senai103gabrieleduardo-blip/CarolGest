import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class MetaBusinessAPI:
    """Integração com Meta Business API para WhatsApp, Instagram e Facebook"""
    
    def __init__(self):
        self.access_token = os.environ.get('META_API_TOKEN')
        self.base_url = "https://graph.facebook.com/v18.0"
        self.whatsapp_phone_id = None  # Will be set based on business account
        
    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    # WhatsApp Business API Methods
    def get_whatsapp_business_accounts(self):
        """Obter contas do WhatsApp Business"""
        try:
            url = f"{self.base_url}/me/businesses"
            response = requests.get(url, headers=self.get_headers())
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao obter contas WhatsApp Business: {e}")
            return None
    
    def send_whatsapp_message(self, to_number: str, message: str, message_type: str = "text"):
        """Enviar mensagem via WhatsApp Business API"""
        try:
            # Remove formatting from phone number
            clean_number = ''.join(filter(str.isdigit, to_number))
            if not clean_number.startswith('55'):
                clean_number = '55' + clean_number
                
            url = f"{self.base_url}/{self.whatsapp_phone_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_number,
                "type": message_type,
                "text": {"body": message}
            }
            
            response = requests.post(url, headers=self.get_headers(), json=payload)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao enviar mensagem WhatsApp: {e}")
            return None
    
    def get_whatsapp_messages(self, limit: int = 50):
        """Obter mensagens recebidas do WhatsApp"""
        try:
            url = f"{self.base_url}/{self.whatsapp_phone_id}/messages"
            params = {"limit": limit}
            response = requests.get(url, headers=self.get_headers(), params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao obter mensagens WhatsApp: {e}")
            return None
    
    def mark_message_as_read(self, message_id: str):
        """Marcar mensagem como lida"""
        try:
            url = f"{self.base_url}/{self.whatsapp_phone_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            response = requests.post(url, headers=self.get_headers(), json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Erro ao marcar mensagem como lida: {e}")
            return False
    
    # Instagram Business API Methods
    def get_instagram_accounts(self):
        """Obter contas conectadas do Instagram"""
        try:
            url = f"{self.base_url}/me/accounts"
            params = {"fields": "instagram_business_account"}
            response = requests.get(url, headers=self.get_headers(), params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao obter contas Instagram: {e}")
            return None
    
    def get_instagram_media(self, instagram_account_id: str, limit: int = 25):
        """Obter mídia do Instagram"""
        try:
            url = f"{self.base_url}/{instagram_account_id}/media"
            params = {
                "fields": "id,caption,media_type,media_url,thumbnail_url,timestamp,like_count,comments_count",
                "limit": limit
            }
            response = requests.get(url, headers=self.get_headers(), params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao obter mídia Instagram: {e}")
            return None
    
    def get_instagram_insights(self, instagram_account_id: str, period: str = "day"):
        """Obter insights do Instagram"""
        try:
            url = f"{self.base_url}/{instagram_account_id}/insights"
            params = {
                "metric": "impressions,reach,profile_views,website_clicks",
                "period": period
            }
            response = requests.get(url, headers=self.get_headers(), params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao obter insights Instagram: {e}")
            return None
    
    def create_instagram_post(self, instagram_account_id: str, image_url: str, caption: str):
        """Criar post no Instagram"""
        try:
            # Primeiro, criar o container da mídia
            url = f"{self.base_url}/{instagram_account_id}/media"
            payload = {
                "image_url": image_url,
                "caption": caption
            }
            response = requests.post(url, headers=self.get_headers(), json=payload)
            
            if response.status_code == 200:
                creation_id = response.json().get('id')
                
                # Depois, publicar a mídia
                publish_url = f"{self.base_url}/{instagram_account_id}/media_publish"
                publish_payload = {"creation_id": creation_id}
                publish_response = requests.post(publish_url, headers=self.get_headers(), json=publish_payload)
                
                return publish_response.json() if publish_response.status_code == 200 else None
            return None
        except Exception as e:
            print(f"Erro ao criar post Instagram: {e}")
            return None
    
    # Facebook Pages API Methods
    def get_facebook_pages(self):
        """Obter páginas do Facebook"""
        try:
            url = f"{self.base_url}/me/accounts"
            params = {"fields": "id,name,access_token,category,fan_count"}
            response = requests.get(url, headers=self.get_headers(), params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao obter páginas Facebook: {e}")
            return None
    
    def get_facebook_page_insights(self, page_id: str, page_access_token: str):
        """Obter insights da página do Facebook"""
        try:
            url = f"{self.base_url}/{page_id}/insights"
            headers = {
                'Authorization': f'Bearer {page_access_token}',
                'Content-Type': 'application/json'
            }
            params = {
                "metric": "page_impressions,page_engaged_users,page_post_engagements,page_fans"
            }
            response = requests.get(url, headers=headers, params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao obter insights Facebook: {e}")
            return None
    
    def create_facebook_post(self, page_id: str, page_access_token: str, message: str, link: str = None):
        """Criar post no Facebook"""
        try:
            url = f"{self.base_url}/{page_id}/feed"
            headers = {
                'Authorization': f'Bearer {page_access_token}',
                'Content-Type': 'application/json'
            }
            payload = {"message": message}
            if link:
                payload["link"] = link
                
            response = requests.post(url, headers=headers, json=payload)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao criar post Facebook: {e}")
            return None
    
    def get_facebook_messages(self, page_id: str, page_access_token: str):
        """Obter mensagens da página do Facebook"""
        try:
            url = f"{self.base_url}/{page_id}/conversations"
            headers = {
                'Authorization': f'Bearer {page_access_token}',
                'Content-Type': 'application/json'
            }
            params = {"fields": "participants,updated_time,message_count"}
            response = requests.get(url, headers=headers, params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao obter mensagens Facebook: {e}")
            return None
    
    # Unified Social Media Management
    def get_all_social_accounts(self):
        """Obter todas as contas de redes sociais conectadas"""
        accounts = {
            'whatsapp': self.get_whatsapp_business_accounts(),
            'instagram': self.get_instagram_accounts(),
            'facebook': self.get_facebook_pages()
        }
        return accounts
    
    def get_unified_insights(self):
        """Obter insights unificados de todas as plataformas"""
        insights = {}
        
        # Instagram insights
        instagram_accounts = self.get_instagram_accounts()
        if instagram_accounts and 'data' in instagram_accounts:
            for account in instagram_accounts['data']:
                if 'instagram_business_account' in account:
                    ig_id = account['instagram_business_account']['id']
                    insights['instagram'] = self.get_instagram_insights(ig_id)
        
        # Facebook insights
        facebook_pages = self.get_facebook_pages()
        if facebook_pages and 'data' in facebook_pages:
            insights['facebook'] = []
            for page in facebook_pages['data']:
                page_insights = self.get_facebook_page_insights(page['id'], page['access_token'])
                insights['facebook'].append({
                    'page_id': page['id'],
                    'page_name': page['name'],
                    'insights': page_insights
                })
        
        return insights