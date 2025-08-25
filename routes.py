from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app
from models import User, Client, KanbanCard, WhatsAppMessage
from datetime import datetime, timedelta
import json

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
    new_column = request.json.get('column')
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
