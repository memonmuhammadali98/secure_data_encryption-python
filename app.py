import streamlit as st
from cryptography.fernet import Fernet
import hashlib
import base64


stored_data = {}
login_attempts = {}
AUTHORIZED = {"is_logged_in": True}


def generate_key(passkey: str) -> bytes:
    hashed = hashlib.sha256(passkey.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

def encrypt_data(data: str, passkey: str) -> str:
    key = generate_key(passkey)
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(token: str, passkey: str) -> str:
    key = generate_key(passkey)
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()


st.set_page_config(
    page_title="🔐 Secure Data Encryption",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown(
    "<h1 style='text-align: center; color: #000000;'>🔐 Secure Data Encryption System</h1>",
    unsafe_allow_html=True
)

# ---- Sidebar Navigation ----
menu = st.sidebar.radio("📂 Navigation", ["🏠 Home", "📥 Store Data", "🔓 Retrieve Data", "🔑 Login"])

# ---- Home Page ----
if menu == "🏠 Home":
    st.subheader("Welcome to the Secure Encryption System")
    st.markdown("""
        - ✅ Encrypt and store text securely with a hashed passkey  
        - 🔐 Retrieve it only using the correct passkey  
        - 🚫 3 wrong attempts? You'll be locked out and asked to re-login  
    """)
    st.info("Use the sidebar to get started.")

# ---- Store Data Page ----
elif menu == "📥 Store Data":
    st.subheader("Store Encrypted Data")

    username = st.text_input("👤 Username")
    passkey = st.text_input("🔑 Passkey", type="password")
    data = st.text_area("📝 Enter your secret data")

    if st.button("🔒 Encrypt & Store"):
        if username and passkey and data:
            encrypted_text = encrypt_data(data, passkey)
            hashed_passkey = hashlib.sha256(passkey.encode()).hexdigest()

            stored_data[username] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_passkey
            }
            login_attempts[username] = 0
            st.success("✅ Your data was securely encrypted and stored.")
        else:
            st.warning("⚠️ All fields are required!")

# ---- Retrieve Data Page ----
elif menu == "🔓 Retrieve Data":
    st.subheader("Retrieve & Decrypt Data")

    if not AUTHORIZED.get("is_logged_in"):
        st.warning("⚠️ You're locked out due to too many failed attempts.")
        st.info("Please go to the **Login** page to reauthorize.")
        st.stop()

    username = st.text_input("👤 Username")
    passkey = st.text_input("🔑 Passkey", type="password")

    if st.button("🔍 Decrypt & Retrieve"):
        if username in stored_data:
            if login_attempts.get(username, 0) >= 3:
                AUTHORIZED["is_logged_in"] = False
                st.error("🚫 Locked out. Too many failed attempts.")
                st.stop()

            hashed_input = hashlib.sha256(passkey.encode()).hexdigest()
            stored = stored_data[username]

            if hashed_input == stored["passkey"]:
                try:
                    decrypted = decrypt_data(stored["encrypted_text"], passkey)
                    st.success("✅ Decryption successful!")
                    st.text_area("🔓 Your Decrypted Data:", decrypted, height=150)
                    login_attempts[username] = 0
                except:
                    login_attempts[username] += 1
                    st.error(f"❌ Decryption failed. Attempt {login_attempts[username]}/3")
            else:
                login_attempts[username] += 1
                st.error(f"❌ Incorrect passkey. Attempt {login_attempts[username]}/3")
        else:
            st.error("❌ Username not found.")

# ---- Login Page ----
elif menu == "🔑 Login":
    st.subheader("Reauthorize Access")

    username = st.text_input("👤 Username")
    passkey = st.text_input("🔑 Passkey", type="password")

    if st.button("🔓 Login"):
        if username in stored_data:
            stored = stored_data[username]
            hashed_input = hashlib.sha256(passkey.encode()).hexdigest()

            if hashed_input == stored["passkey"]:
                AUTHORIZED["is_logged_in"] = True
                login_attempts[username] = 0
                st.success("✅ Login successful! You can now access your data.")
            else:
                st.error("❌ Invalid passkey.")
        else:
            st.error("❌ Username not found.")
