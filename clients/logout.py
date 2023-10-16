from client import Client

if __name__ == "__main__":
    # this will either prompt a login process
    # or just run with current stored data
    client: Client = Client()
    client.logout()