import streamlit_authenticator as stauth

def generate_hashes():
    """
    Utility script to generate password hashes for the initial configuration.
    Using the correct API for streamlit-authenticator 0.4.x
    """
    passwords = ['admin123', 'doctor123']
    
    # In newer versions, we call hash_passwords class method
    hashed_passwords = stauth.Hasher.hash_passwords(passwords)
    
    print("--- Generated Password Hashes ---")
    print(f"admin (admin123): {hashed_passwords[0]}")
    print(f"doctor (doctor123): {hashed_passwords[1]}")

if __name__ == "__main__":
    generate_hashes()
