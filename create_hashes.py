from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


users = {
    'user': 'user',
    'admin': 'admin',
}

env_content = ''
print('\nCopy the following lines into your .env file:\n')
for username, plain_password in users.items():
    hashed_password = pwd_context.hash(plain_password)
    env_line = f"USER_{username.upper()}_HASH=\"{hashed_password}\""
    print(env_line)
    env_content += env_line + '\n'
