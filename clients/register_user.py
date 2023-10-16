from client import Client


def input_user(role):
    user_email = input(f"Enter {role} email : ")
    user_firstname = input(f"Enter {role} first name : ")
    user_lastname = input(f"Enter {role} last name : ")
    user_password = input(f"Enter {role} password : ")

    user = {
        'email': user_email,
        'first_name': user_firstname,
        'last_name': user_lastname,
        'password': user_password,
    }

    return user

def input_user_role():
    print("Choose user role")
    print("1: Consumer")
    print("2: Staff")
    print("3: Superuser")
    print("Any value Other than 1,2,3 will be considered as 1:Consumer")

    string_role = input("Enter 1,2 or 3 : ")
    role = 1

    try:
        role = int(string_role)
    except ValueError:
        pass

    if role not in [1,2,3]:
        return 1
    return role

if __name__ == "__main__":
    # this will either prompt a login process
    # or just run with current stored data
    client: Client = Client()
    is_authenticated = client.user_is_authenticated()
    if not is_authenticated:
        print("You are about to register your self as a new consumer")
        user = input_user(role="self")
        registered_user = client.register(user)
        print(registered_user)
    
    elif client.user_is_staff_only():
        print("Hello Staff, You are about to register a new consumer")
        user = input_user(role="consumer")
        registered_user = client.register(user)
        print(registered_user)

    elif client.user_is_superuser():
        print("Hello Superuser, You are about to register a new user [consumer,staff,superuser]")
        user = input_user(role="user")
        role = input_user_role() #1: Consumer, 2: Staff, 3: Superuser
        is_staff = False
        is_superuser = False
        
        if role == 1:
            pass
        elif role == 2:
            is_staff = True
        else:
            is_staff = True
            is_superuser = True
        
        user['is_satff'] = is_staff
        user['is_superuser'] = is_superuser

        registered_user = client.register(user)
        print(registered_user)

    # At this point : Authenticated Consumer
    print("You are Consumer, you don't have permission to register a new user")

