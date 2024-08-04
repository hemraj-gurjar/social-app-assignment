# Social Networking API

This project is a social networking application built with Django and Django Rest Framework (DRF). It includes functionalities for user login/signup, searching users, sending/accepting/rejecting friend requests, listing friends, and listing pending friend requests.

## Installation Steps

### Prerequisites

- Python 3.x
- Docker and Docker Compose

### Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/social_network.git
   cd social_network
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:

   ```bash
   python manage.py migrate
   ```

5. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Using Docker

1. Build and start the containers:

   ```bash
   docker-compose up --build
   ```

2. The application will be accessible at `http://localhost:8000`.

## API Endpoints

You can find the Postman collection for the API endpoints [here](postman_collection.json).

### Endpoints

- `POST /api/signup/` - User signup
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `GET /api/search/?query=<keyword>` - Search users by email or name
- `POST /api/friend-request/send/` - Send friend request
- `POST/PUT /api/friend-request/respond/` - Accept or reject friend request
- `GET /api/friends/` - List friends
- `GET /api/friend-requests/pending/` - List pending friend requests
