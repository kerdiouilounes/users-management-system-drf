from dataclasses import dataclass
import jwt 
import requests
from getpass import getpass
import pathlib 
import json


@dataclass
class Client:
    
    access:str = None
    refresh:str = None
    header_type: str = "Bearer"
    base_endpoint = "http://localhost:8000/api"
    cred_path: pathlib.Path = pathlib.Path("creds.json")

    def __post_init__(self):
        pass

    def user_is_authenticated(self):
        creds = self.load_creds()
        if creds is not None:
            self.read_creds(creds)
            token_validated = self.validate_token()
            return token_validated
        return False
    
    def validate_token(self):
        token_verified = self.verify_token()
        if token_verified:
            return True
        token_refreshed = self.perform_refresh()
        return token_refreshed

    
    def authenticate(self):
        creds = self.load_creds()
        if creds is None:
                """ 
                Clear stored creds and
                Run login process
                """
                self.clear_tokens()
                self.perform_auth()
        else:
            """
            `creds.json` was not tampered with
            Verify token -> 
            if necessary, Refresh token ->
            if necessary, Run login process
            """
            self.read_creds(creds)
            token_validated = self.validate_token()
            if not token_validated:
                self.clear_tokens()
                self.perform_auth()
    
    def read_creds(self, creds):
        self.access = creds.get('access')
        self.refresh = creds.get('refresh')

    def load_creds(self):
        creds = None
        if self.cred_path.exists(): 
            """
            You have stored creds,
            let's verify them
            and refresh them.
            If that fails,
            restart login process.
            """
            try:
                creds = json.loads(self.cred_path.read_text())
            except Exception:
                print("Assuming creds has been tampered with")
                pass
        return creds

        
    def get_headers(self, header_type=None):
        """
        Default headers for HTTP requests
        including the JWT token
        """
        _type = header_type or self.header_type
        token = self.access
        if not token:
            return {}
        return {
                "Authorization": f"{_type} {token}"
        }

    def perform_auth(self):
        """
        Simple way to perform authentication
        Without exposing password(s) during the
        collection process.
        """
        endpoint = f"{self.base_endpoint}/token/" 
        email = input("What is your email?\n")
        password = getpass("What is your password?\n")
        r = requests.post(endpoint, json={'email': email, 'password': password}) 
        if r.status_code != 200:
            raise Exception(f"Access not granted: {r.text}")
        print('access granted')
        self.write_creds(r.json())

    def write_creds(self, data:dict):
        """
        Store credentials as a local file
        and update instance with correct
        data.
        """
        if self.cred_path is not None:
            self.access = data.get('access')
            self.refresh = data.get('refresh')
            if self.access and self.refresh:
                self.cred_path.write_text(json.dumps(data))
    
    def verify_token(self):
        """
        Simple method for verifying your
        token data. This method only verifies
        your `access` token. A 200 HTTP status
        means success, anything else means failure.
        """
        data = {
            "token": f"{self.access}"
        }
        endpoint = f"{self.base_endpoint}/token/verify/" 
        r = requests.post(endpoint, json=data)
        return r.status_code == 200
    
    def clear_tokens(self):
        """
        Remove any/all JWT token data
        from instance as well as stored
        creds file.
        """
        self.access = None
        self.refresh = None
        if self.cred_path.exists():
            self.cred_path.unlink()

    def login(self):
        self.authenticate()
    
    def logout(self):
        self.clear_tokens()
    
    def perform_refresh(self):
        """
        Refresh the access token by using the correct
        auth headers and the refresh token.
        """
        print("Refreshing token.")
        headers = self.get_headers()
        data = {
            "refresh": f"{self.refresh}"
        }
        endpoint = f"{self.base_endpoint}/token/refresh/" 
        r = requests.post(endpoint, json=data, headers=headers)
        if r.status_code != 200:
            self.clear_tokens()
            return False
        refresh_data = r.json()
        if not 'access' in refresh_data:
            self.clear_tokens()
            return False
        stored_data = {
            'access': refresh_data.get('access'),
            'refresh': self.refresh
        }
        self.write_creds(stored_data)
        return True
    
    def get_user_id(self):
        token = self.access
        user_id = None 
        try:
            # Decode the token
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            # Extract the user ID
            user_id = decoded_token.get("user_id")
    
            if user_id:
                print(f"Your User ID: {user_id}")
            else:
                print("User ID not found in the token.")
        except jwt.ExpiredSignatureError:
                print("Token has expired.")
        except jwt.DecodeError:
                print("Failed to decode the token.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        return user_id

    def list_users(self, endpoint=None, limit=3):
        """
        List users.
        """
        headers = self.get_headers()
        if endpoint is None or self.base_endpoint not in str(endpoint):
            endpoint = f"{self.base_endpoint}/users/?limit={limit}" 
        r = requests.get(endpoint, headers=headers) 
        if r.status_code != 200:
            raise Exception(f"Request not complete {r.text}")
        data = r.json()
        return data
    
    def register(self, user):
        """
        Register a new user.
        """
        headers = self.get_headers()
        endpoint = f"{self.base_endpoint}/users/" 
        r = requests.post(endpoint, json=user, headers=headers) 
        if r.status_code != 200 or r.status_code != 201:
            print("Failed to register new user")
            raise Exception(f"Request not complete {r.text}")
        data = r.json()
        return data
    
    def user_detail(self, user_id=None):
        """
        Get user details. 
        If user_id is None, get this authenticated user detail

        """
        headers = self.get_headers()

        if user_id is None:
            user_id = self.get_user_id()

        if user_id is None:
            return None
        
        # If we want to get this authenticated user detail, we can also use
        # f"{self.base_endpoint}/users/me/" endpoint without the need of getting
        # user_id from the client, but this f"{self.base_endpoint}/users/{user_id}/"
        # is more generale in case we want to get [If has permission] the details
        # of a user other than this authenticated user. for example:
        # staff or superuser wants to get the consumer detail
        endpoint = f"{self.base_endpoint}/users/{user_id}/" 
        r = requests.get(endpoint, headers=headers) 
        if r.status_code != 200:
            raise Exception(f"Request not complete {r.text}")
        data = r.json()
        return data
    
    def user_has_permission_to_list(self, user_id=None):
        """
        Check if user has permission to list users
        """
        user = self.user_detail(user_id)
        if user is None:
            raise Exception(f"Cannot check permissions : user data not available")
        is_staff = user.get("is_staff")
        is_superuser = user.get("is_superuser")

        if is_staff or is_superuser:
            return True
        return False
    
    def user_is_staff_only(self,user_id=None):
        """
        Check if user role is staff
        """
        user = self.user_detail(user_id)
        if user is None:
            raise Exception(f"Cannot check user role : user data not available")
        is_staff = user.get("is_staff")
        is_superuser = user.get("is_superuser")

        if is_staff and (not is_superuser):
            return True
        return False
    
    def user_is_superuser(self, user_id=None):
        """
        Check if user role is superuser
        """
        user = self.user_detail(user_id)
        if user is None:
            raise Exception(f"Cannot check user role : user data not available")
        is_superuser = user.get("is_superuser")

        if is_superuser:
            return True
        return False
    
    def user_is_consumer(self, user_id=None):
        """
        Check if user role is consumer
        """
        user = self.user_detail(user_id)
        if user is None:
            raise Exception(f"Cannot check user role : user data not available")
        is_staff = user.get("is_staff")
        is_superuser = user.get("is_superuser")

        if is_staff or is_superuser:
            return False
        return True
    
