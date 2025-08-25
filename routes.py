from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, Response
from flask_login import login_user, logout_user, login_required, current_user
from app import app
from models import User, Client, KanbanCard, WhatsAppMessage, SocialAccount, SocialPost
from services.meta_api import MetaBusinessAPI
from services.report_generator import ReportGenerator
from datetime import datetime, timedelta
import json
import os

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Calculate dashboard metrics
    total_clients = len(Client.get_all())
    total_cards = len(KanbanCard.get_all())
    unread_messages = len([msg for msg in WhatsAppMessage.get_all() if not msg.read])
    
    # Sales pipeline stats
    pipeline_stats = {
        'atendimento_inicial': len(KanbanCard.get_by_column('atendimento_inicial')),
        'proposta_enviada': len(KanbanCard.get_by_column('proposta_enviada')),
        'venda_andamento': len(KanbanCard.get_by_column('venda_andamento')),
        'venda_concluida': len(KanbanCard.get_by_column('venda_concluida')),
        'pos_venda': len(KanbanCard.get_by_column('pos_venda'))
    }
    
    # Recent activities (last 10 cards)
    recent_cards = sorted(KanbanCard.get_all(), key=lambda x: x.updated_at, reverse=True)[:5]
    
    return render_template('dashboard.html', 
                         total_clients=total_clients,
                         total_cards=total_cards,
                         unread_messages=unread_messages,
                         pipeline_stats=pipeline_stats,
                         recent_cards=recent_cards)

@app.route('/clients')
@login_required
def clients():
    search = request.args.get('search', '')
    if search:
        client_list = Client.search(search)
    else:
        client_list = Client.get_all()
    
    return render_template('clients.html', clients=client_list, search=search)

@app.route('/clients/new', methods=['GET', 'POST'])
@login_required
def new_client():
    if request.method == 'POST':
        client = Client(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            cpf_cnpj=request.form['cpf_cnpj'],
            address=request.form.get('address', ''),
            insurance_type=request.form.get('insurance_type', ''),
            notes=request.form.get('notes', '')
        )
        Client.save(client)
        flash('Cliente criado com sucesso!', 'success')
        return redirect(url_for('clients'))
    
    return render_template('clients.html', show_form=True)

@app.route('/clients/<int:client_id>/edit', methods=['POST'])
@login_required
def edit_client(client_id):
    client = Client.get(client_id)
    if client:
        client.name = request.form['name']
        client.email = request.form['email']
        client.phone = request.form['phone']
        client.cpf_cnpj = request.form['cpf_cnpj']
        client.address = request.form.get('address', '')
        client.insurance_type = request.form.get('insurance_type', '')
        client.notes = request.form.get('notes', '')
        Client.save(client)
        flash('Cliente atualizado com sucesso!', 'success')
    else:
        flash('Cliente não encontrado!', 'danger')
    
    return redirect(url_for('clients'))

@app.route('/clients/<int:client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    if Client.delete(client_id):
        flash('Cliente excluído com sucesso!', 'success')
    else:
        flash('Cliente não encontrado!', 'danger')
    
    return redirect(url_for('clients'))

@app.route('/kanban')
@login_required
def kanban():
    columns = {
        'atendimento_inicial': KanbanCard.get_by_column('atendimento_inicial'),
        'proposta_enviada': KanbanCard.get_by_column('proposta_enviada'),
        'venda_andamento': KanbanCard.get_by_column('venda_andamento'),
        'venda_concluida': KanbanCard.get_by_column('venda_concluida'),
        'pos_venda': KanbanCard.get_by_column('pos_venda')
    }
    
    clients = Client.get_all()
    users = User.get_all()
    
    return render_template('kanban.html', columns=columns, clients=clients, users=users)

@app.route('/kanban/card/new', methods=['POST'])
@login_required
def new_kanban_card():
    card = KanbanCard(
        title=request.form['title'],
        description=request.form.get('description', ''),
        client_id=int(request.form['client_id']) if request.form['client_id'] else None,
        assigned_to=int(request.form['assigned_to']) if request.form['assigned_to'] else None,
        column=request.form.get('column', 'atendimento_inicial')
    )
    KanbanCard.save(card)
    flash('Cartão criado com sucesso!', 'success')
    return redirect(url_for('kanban'))

@app.route('/kanban/card/<card_id>/move', methods=['POST'])
@login_required
def move_kanban_card(card_id):
    data = request.get_json() or {}
    new_column = data.get('column')
    if KanbanCard.move_to_column(card_id, new_column):
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/kanban/card/<card_id>/delete', methods=['POST'])
@login_required
def delete_kanban_card(card_id):
    if KanbanCard.delete(card_id):
        flash('Cartão excluído com sucesso!', 'success')
    else:
        flash('Cartão não encontrado!', 'danger')
    
    return redirect(url_for('kanban'))

@app.route('/whatsapp')
@login_required
def whatsapp():
    messages = WhatsAppMessage.get_all()
    clients = Client.get_all()
    return render_template('whatsapp.html', messages=messages, clients=clients)

@app.route('/whatsapp/send', methods=['POST'])
@login_required
def send_whatsapp_message():
    # Mock WhatsApp message sending for MVP
    message = WhatsAppMessage(
        sender=current_user.name,
        message=request.form['message'],
        message_type='sent',
        client_id=int(request.form['client_id']) if request.form['client_id'] else None
    )
    WhatsAppMessage.save(message)
    flash('Mensagem enviada! (Mock para MVP)', 'success')
    return redirect(url_for('whatsapp'))

@app.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem gerenciar usuários.', 'danger')
        return redirect(url_for('dashboard'))
    
    user_list = User.get_all()
    return render_template('users.html', users=user_list)

@app.route('/users/new', methods=['POST'])
@login_required
def new_user():
    if current_user.role != 'admin':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User(
        username=request.form['username'],
        email=request.form['email'],
        name=request.form['name'],
        role=request.form['role']
    )
    user.set_password(request.form['password'])
    User.save(user)
    flash('Usuário criado com sucesso!', 'success')
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    
    if user_id == current_user.id:
        flash('Você não pode excluir sua própria conta!', 'danger')
        return redirect(url_for('users'))
    
    if User.delete(user_id):
        flash('Usuário excluído com sucesso!', 'success')
    else:
        flash('Usuário não encontrado!', 'danger')
    
    return redirect(url_for('users'))

@app.route('/reports')
@login_required
def reports():
    # Generate basic reports
    total_clients = len(Client.get_all())
    total_sales = len(KanbanCard.get_by_column('venda_concluida'))
    pipeline_conversion = {
        'leads': len(KanbanCard.get_by_column('atendimento_inicial')),
        'proposals': len(KanbanCard.get_by_column('proposta_enviada')),
        'in_progress': len(KanbanCard.get_by_column('venda_andamento')),
        'closed': len(KanbanCard.get_by_column('venda_concluida'))
    }
    
    # Monthly performance (mock data for MVP)
    monthly_performance = [
        {'month': 'Janeiro', 'sales': 15, 'revenue': 45000},
        {'month': 'Fevereiro', 'sales': 18, 'revenue': 54000},
        {'month': 'Março', 'sales': 22, 'revenue': 66000},
        {'month': 'Abril', 'sales': 20, 'revenue': 60000},
        {'month': 'Maio', 'sales': 25, 'revenue': 75000},
        {'month': 'Junho', 'sales': 28, 'revenue': 84000}
    ]
    
    return render_template('reports.html', 
                         total_clients=total_clients,
                         total_sales=total_sales,
                         pipeline_conversion=pipeline_conversion,
                         monthly_performance=monthly_performance)

# WhatsApp Business Integration Routes
@app.route('/whatsapp/real-send', methods=['POST'])
@login_required
def send_real_whatsapp_message():
    """Enviar mensagem real via WhatsApp Business API"""
    try:
        meta_api = MetaBusinessAPI()
        to_number = request.form['to_number']
        message = request.form['message']
        
        result = meta_api.send_whatsapp_message(to_number, message)
        
        if result:
            # Salvar mensagem enviada no banco
            whatsapp_msg = WhatsAppMessage(
                sender=current_user.name,
                message=message,
                message_type='sent',
                client_id=int(request.form['client_id']) if request.form.get('client_id') else None
            )
            WhatsAppMessage.save(whatsapp_msg)
            flash('Mensagem WhatsApp enviada com sucesso!', 'success')
        else:
            flash('Erro ao enviar mensagem WhatsApp. Verifique a configuração da API.', 'danger')
    except Exception as e:
        flash(f'Erro na integração WhatsApp: {str(e)}', 'danger')
    
    return redirect(url_for('whatsapp'))

@app.route('/whatsapp/sync')
@login_required
def sync_whatsapp_messages():
    """Sincronizar mensagens do WhatsApp Business"""
    try:
        meta_api = MetaBusinessAPI()
        messages = meta_api.get_whatsapp_messages()
        
        if messages and 'data' in messages:
            for msg_data in messages['data']:
                # Processar e salvar mensagens recebidas
                # Implementar lógica de sincronização
                pass
            flash(f'Sincronizadas {len(messages["data"])} mensagens do WhatsApp', 'success')
        else:
            flash('Nenhuma mensagem nova encontrada', 'info')
    except Exception as e:
        flash(f'Erro na sincronização: {str(e)}', 'danger')
    
    return redirect(url_for('whatsapp'))

# Social Media Management Routes
@app.route('/social')
@login_required
def social_media():
    """Página principal de gerenciamento de redes sociais"""
    meta_api = MetaBusinessAPI()
    
    # Obter contas conectadas
    social_accounts = SocialAccount.get_all()
    
    # Obter posts recentes
    recent_posts = SocialPost.get_all()[:10]
    
    # Obter insights unificados
    try:
        insights = meta_api.get_unified_insights()
    except:
        insights = {}
    
    return render_template('social_media.html', 
                         accounts=social_accounts,
                         recent_posts=recent_posts,
                         insights=insights)

@app.route('/social/connect')
@login_required
def connect_social_accounts():
    """Conectar contas de redes sociais"""
    try:
        meta_api = MetaBusinessAPI()
        all_accounts = meta_api.get_all_social_accounts()
        
        # Salvar contas encontradas
        for platform, accounts in all_accounts.items():
            if accounts and 'data' in accounts:
                for account_data in accounts['data']:
                    if platform == 'instagram' and 'instagram_business_account' in account_data:
                        ig_account = account_data['instagram_business_account']
                        social_account = SocialAccount(
                            platform='instagram',
                            account_id=ig_account['id'],
                            name=account_data.get('name', 'Instagram Business')
                        )
                        SocialAccount.save(social_account)
                    elif platform == 'facebook':
                        social_account = SocialAccount(
                            platform='facebook',
                            account_id=account_data['id'],
                            name=account_data['name'],
                            access_token=account_data.get('access_token')
                        )
                        SocialAccount.save(social_account)
        
        flash('Contas de redes sociais conectadas com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao conectar contas: {str(e)}', 'danger')
    
    return redirect(url_for('social_media'))

@app.route('/social/post/new', methods=['POST'])
@login_required
def create_social_post():
    """Criar novo post nas redes sociais"""
    try:
        platform = request.form['platform']
        content = request.form['content']
        account_id = request.form['account_id']
        
        # Criar post
        post = SocialPost(
            account_id=account_id,
            content=content,
            platform=platform
        )
        
        # Se for para publicar imediatamente
        if request.form.get('publish_now'):
            meta_api = MetaBusinessAPI()
            
            if platform == 'facebook':
                account = next((acc for acc in SocialAccount.get_all() if acc.id == int(account_id)), None)
                if account:
                    result = meta_api.create_facebook_post(account.account_id, account.access_token, content)
                    if result:
                        post.published = True
                        post.published_at = datetime.now()
            
            elif platform == 'instagram':
                # Para Instagram seria necessário ter uma imagem
                flash('Para Instagram é necessário adicionar uma imagem', 'warning')
        
        SocialPost.save(post)
        flash('Post criado com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao criar post: {str(e)}', 'danger')
    
    return redirect(url_for('social_media'))

# Reports Routes
@app.route('/reports/export/clients')
@login_required
def export_clients_report():
    """Exportar relatório de clientes"""
    try:
        report_type = request.args.get('type', 'excel')
        clients = Client.get_all()
        
        report_generator = ReportGenerator()
        
        if report_type == 'excel':
            filepath = report_generator.generate_client_report_excel(clients)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
        elif report_type == 'pdf':
            filepath = report_generator.generate_client_report_pdf(clients)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
        else:
            flash('Tipo de relatório não suportado', 'danger')
            return redirect(url_for('reports'))
            
    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/export/sales')
@login_required
def export_sales_report():
    """Exportar relatório de vendas"""
    try:
        report_type = request.args.get('type', 'excel')
        cards = KanbanCard.get_all()
        
        # Dados de performance mensal (mock para demonstração)
        monthly_performance = [
            {'month': 'Janeiro', 'sales': 15, 'revenue': 45000},
            {'month': 'Fevereiro', 'sales': 18, 'revenue': 54000},
            {'month': 'Março', 'sales': 22, 'revenue': 66000},
            {'month': 'Abril', 'sales': 20, 'revenue': 60000},
            {'month': 'Maio', 'sales': 25, 'revenue': 75000},
            {'month': 'Junho', 'sales': 28, 'revenue': 84000}
        ]
        
        report_generator = ReportGenerator()
        
        if report_type == 'excel':
            filepath = report_generator.generate_sales_report_excel(cards)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
        elif report_type == 'pdf':
            filepath = report_generator.generate_sales_report_pdf(cards, monthly_performance)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
        else:
            flash('Tipo de relatório não suportado', 'danger')
            return redirect(url_for('reports'))
            
    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/export/social')
@login_required
def export_social_report():
    """Exportar relatório de redes sociais"""
    try:
        meta_api = MetaBusinessAPI()
        social_data = meta_api.get_unified_insights()
        
        report_generator = ReportGenerator()
        filepath = report_generator.generate_social_media_report_pdf(social_data)
        
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
    except Exception as e:
        flash(f'Erro ao gerar relatório de redes sociais: {str(e)}', 'danger')
        return redirect(url_for('reports'))

# API Routes for AJAX calls
@app.route('/api/social/insights')
@login_required
def get_social_insights():
    """API para obter insights das redes sociais"""
    try:
        meta_api = MetaBusinessAPI()
        insights = meta_api.get_unified_insights()
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/whatsapp/status')
@login_required
def get_whatsapp_status():
    """API para verificar status da conexão WhatsApp"""
    try:
        meta_api = MetaBusinessAPI()
        accounts = meta_api.get_whatsapp_business_accounts()
        
        if accounts and 'data' in accounts:
            return jsonify({'connected': True, 'accounts': len(accounts['data'])})
        else:
            return jsonify({'connected': False, 'accounts': 0})
    except Exception as e:
        return jsonify({'connected': False, 'error': str(e)})

# Dashboard enhancements
@app.route('/dashboard/refresh')
@login_required
def refresh_dashboard():
    """Atualizar dados do dashboard"""
    try:
        # Recalcular métricas
        total_clients = len(Client.get_all())
        total_cards = len(KanbanCard.get_all())
        unread_messages = len([msg for msg in WhatsAppMessage.get_all() if not msg.read])
        
        # Status das redes sociais
        social_accounts = len(SocialAccount.get_all())
        
        data = {
            'total_clients': total_clients,
            'total_cards': total_cards,
            'unread_messages': unread_messages,
            'social_accounts': social_accounts,
            'last_updated': datetime.now().strftime('%H:%M:%S')
        }
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
