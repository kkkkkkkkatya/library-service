# Library service REST API 

## Description
The Library Service REST API is an online management system for book borrowings. It will optimize the library administrators’ work and make the service much more user-friendly.


## **Features**
- JWT authenticated
- Admin panel /admin/
- Running using localhost
- The interactive API documentation powered by Swagger at `http://127.0.0.1:8000/api/doc/swagger/`.
- Managing books

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/kkkkkkkkatya/library-service.git
   cd library-service
   
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.sample .env
   ```
   Fill in the `.env` file with necessary configurations.

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Usage
- Visit `http://127.0.0.1:8000/` in your browser.

## Authentication
The API uses JWT (JSON Web Tokens) for authentication. To obtain a token:

1. **Register a user** (see the api/users/ endpoint in the API documentation).
2. **Login** with the registered credentials to receive a token (api/users/token/).
3. Include the token in the Authorization header for subsequent requests.


## Authors and Acknowledgment
Developed by Kateryna
