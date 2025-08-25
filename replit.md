# Overview

Monteiro Corretora is a comprehensive insurance brokerage management system built with Flask. The application provides a centralized platform for managing clients, sales operations, WhatsApp communications, and business workflows through an integrated dashboard and Kanban board interface.

The system is designed as an MVP (Minimum Viable Product) with plans for future integration with WhatsApp Business API, social media platforms (Instagram/Facebook), and advanced reporting capabilities. Currently, it operates with in-memory data storage for rapid prototyping and demonstration purposes.

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
- **Current Implementation**: In-memory dictionaries for rapid MVP development
- **Data Models**: User, Client, KanbanCard, and WhatsAppMessage models with static methods for CRUD operations
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
- **Communication Hub**: Centralized WhatsApp message interface (mock implementation ready for API integration)
- **Analytics Dashboard**: Key performance indicators and pipeline metrics

# External Dependencies

## Frontend Dependencies
- **Bootstrap 5**: UI framework loaded via CDN for responsive design
- **Font Awesome 6**: Icon library for consistent iconography across the interface
- **SortableJS**: Drag-and-drop library for Kanban board functionality

## Backend Dependencies
- **Flask**: Core web framework for Python web application
- **Flask-Login**: User session management and authentication
- **Werkzeug**: WSGI utility library with ProxyFix for deployment and password security

## Planned Integrations
- **WhatsApp Business API**: Meta's official API for WhatsApp business messaging
- **Instagram Basic Display API**: For social media management and engagement tracking
- **Facebook Graph API**: For Facebook page management and advertising insights
- **Database System**: PostgreSQL or MySQL for persistent data storage (architecture supports easy migration)

## Development & Deployment
- **Environment Configuration**: Environment variable support for sensitive configuration
- **Logging**: Python logging module with DEBUG level for development
- **WSGI Deployment**: Ready for production deployment with WSGI servers like Gunicorn