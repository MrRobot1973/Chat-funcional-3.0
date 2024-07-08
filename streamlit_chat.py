import streamlit as st
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import hashlib

# Configuración de la base de datos
DATABASE_URL = "sqlite:///chat_app.db"
Base = declarative_base()

# Definición de la tabla de usuarios
class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True, unique=True)
    password = Column(String)

# Definición de la tabla de mensajes
class Message(Base):
    __tablename__ = 'messages'
    id = Column(String, primary_key=True, unique=True)
    username = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Crear la base de datos
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Función para encriptar contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Función para verificar el usuario
def check_user(username, password):
    user = session.query(User).filter_by(username=username, password=hash_password(password)).first()
    return user is not None

# Función para registrar un nuevo usuario
def register_user(username, password):
    if session.query(User).filter_by(username=username).first():
        return False
    new_user = User(username=username, password=hash_password(password))
    session.add(new_user)
    session.commit()
    return True

# Función para agregar un mensaje a la base de datos
def add_message(username, message):
    new_message = Message(id=hashlib.sha256(f"{username}{datetime.utcnow()}".encode()).hexdigest(), username=username, message=message)
    session.add(new_message)
    session.commit()

# Función para obtener los mensajes de la base de datos
def get_messages():
    messages = session.query(Message).order_by(Message.timestamp).all()
    return messages

# Interfaz de Streamlit
st.title("Aplicación de Chat")

# Autenticación del usuario
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

if not st.session_state.authenticated:
    option = st.selectbox("Seleccione una opción", ["Iniciar sesión", "Registrarse"])
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if option == "Iniciar sesión":
        if st.button("Iniciar sesión"):
            if check_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Sesión iniciada con éxito")
            else:
                st.error("Usuario o contraseña incorrectos")
    
    elif option == "Registrarse":
        if st.button("Registrarse"):
            if register_user(username, password):
                st.success("Usuario registrado con éxito. Ahora puede iniciar sesión.")
            else:
                st.error("El nombre de usuario ya existe. Por favor, elija otro.")
else:
    st.write(f"Bienvenido, {st.session_state.username}")
    message = st.text_area("Mensaje")
    if st.button("Enviar"):
        if message.strip():
            add_message(st.session_state.username, message)
            st.success("Mensaje enviado")
    
    # Mostrar los mensajes
    messages = get_messages()
    st.subheader("Chat")
    for msg in messages:
        st.write(f"{msg.username} ({msg.timestamp}): {msg.message}")
    
    if st.button("Cerrar sesión"):
        st.session_state.authenticated = False
        st.session_state.username = ""
