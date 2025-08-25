# Overview

Monteiro Corretora is a comprehensive insurance brokerage management system built with Flask. The application provides a centralized platform for managing clients, sales operations, WhatsApp Business communications, Instagram/Facebook CRM, and business workflows through an integrated dashboard and Kanban board interface.

The system features full integration with Meta Business API for WhatsApp Business, Instagram Business, and Facebook Pages management. It includes comprehensive reporting capabilities with Excel and PDF export functionality, real-time social media management, and advanced analytics dashboard.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **CSS Framework**: Bootstrap 5 with custom CSS for branded styling
- **JavaScript**: Vanilla JavaScript with SortableJS for Kanban drag-and-drop functionality
- **Component Structure**: Base template with modular page templates for different sections (dashboard, clients, kanban, reports, etc.)

## Backend Architecture
- **Web Framework**: Flask with Flask-Login for session management
- **Authentication**: Username/password authentication with Werkzeug password hashing
- **Session Management**: Flask sessions with configurable secret key from environment variables
- **Middleware**: ProxyFix for handling reverse proxy deployments

## Data Storage
- **Current Implementation**: In-memory dictionaries for rapid development and demonstration
- **Data Models**: User, Client, KanbanCard, WhatsAppMessage, SocialAccount, and SocialPost models with static methods for CRUD operations
- **Future Migration Path**: Designed for easy transition to persistent database (PostgreSQL/MySQL)

## Application Structure
- **MVC Pattern**: Clear separation between models (models.py), views (templates/), and controllers (routes.py)
- **Modular Design**: Main app configuration in app.py, route handlers in routes.py, data models in models.py
- **Static Assets**: Organized CSS and JavaScript files in static/ directory

## User Management & Authorization
- **Role-Based Access**: Three user roles (admin, sales, atendimento) with different permission levels
- **User Authentication**: Flask-Login integration with secure password storage
- **Session Security**: Configurable session secret with environment variable fallback

## Business Logic Components
- **Kanban Pipeline**: Five-stage sales pipeline (Initial Contact → Proposal Sent → Sale in Progress → Sale Completed → Post-Sale)
- **Client Management**: Complete client profiles with contact information, insurance types, and interaction history
- **WhatsApp Business Integration**: Real-time messaging through Meta Business API with message synchronization
- **Social Media CRM**: Instagram Business and Facebook Pages management with unified posting and analytics
- **Advanced Reporting**: Excel and PDF report generation for clients, sales, and social media analytics
- **Analytics Dashboard**: Comprehensive KPIs including social media metrics and real-time status monitoring

# External Dependencies

## Frontend Dependencies
- **Bootstrap 5**: UI framework loaded via CDN for responsive design
- **Font Awesome 6**: Icon library for consistent iconography across the interface
- **SortableJS**: Drag-and-drop library for Kanban board functionality

## Backend Dependencies
- **Flask**: Core web framework for Python web application
- **Flask-Login**: User session management and authentication
- **Werkzeug**: WSGI utility library with ProxyFix for deployment and password security

## Active Integrations
- **Meta Business API**: Complete integration with WhatsApp Business, Instagram Business, and Facebook Pages
- **WhatsApp Business API**: Real-time messaging, message synchronization, and contact management
- **Instagram Business API**: Post creation, media management, and analytics insights
- **Facebook Graph API**: Page management, post scheduling, and engagement tracking
- **Report Generation**: OpenpyXL for Excel reports and ReportLab for PDF generation

## Future Enhancements
- **Database Migration**: PostgreSQL or MySQL for persistent data storage
- **Real-time Notifications**: WebSocket integration for live updates
- **Advanced Analytics**: Machine learning insights and predictive analytics

## Development & Deployment
- **Environment Configuration**: Environment variable support for sensitive configuration
- **Logging**: Python logging module with DEBUG level for development
- **WSGI Deployment**: Ready for production deployment with WSGI servers like Gunicorn