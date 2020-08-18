# Instructions

1. Clone this repository running the command `git clone <project name>`
2. Run the commmand `python3 -m venv venv` in project directory
3. Run `source venv/bin/activate` or if you are using Windows `venv\Scripts\activate`
4. Run `pip install -r requirements.txt`
5. Run `python manage.py makemigrations`
6. Run `python manage.py migrate`
7. Run `python mange.py startserver`
8. Open GraphQL playground on `http://localhost:8000/graphql` and run queries or mutations

### Notice:

Tokens can be obtained using authToken mutation with provided username and password.

For every request that reguires auth token make sure you have proper request headers in this format: {"Authorization":"JWT token"}

For file uploads in GraphQL I recommend using Altair GraphQL client.
