from client import Client

if __name__ == "__main__":
    # this will either prompt a login process
    # or just run with current stored data
    client: Client = Client()
    client.authenticate()

    has_perm = client.user_has_permission_to_list()

    if not has_perm:
        print("You don't have permission to list users")
    else:
        # simple instance method to perform an HTTP
        # request to our /api/users/ endpoint
        lookup_1_data = client.list_users(limit=5)
        # We used pagination at our endpoint so we have:
        results = lookup_1_data.get('results')
        next_url = lookup_1_data.get('next')
        print("First lookup result length", len(results))
        if next_url:
            lookup_2_data = client.list_users(endpoint=next_url)
            results += lookup_2_data.get('results')
            print("Second lookup result length", len(results))