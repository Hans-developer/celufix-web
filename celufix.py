import streamlit as st
import pandas as pd
import csv
import os

# Configuración de la página
st.set_page_config(page_title="Celufix", page_icon="📱", layout="wide")

# Archivos de datos
USERS_FILE = "users.txt"
PARTS_FILE = "repuestos.csv"

# Crear archivos si no existen
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        f.write("admin:admin123\n")

if not os.path.exists(PARTS_FILE):
    with open(PARTS_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Marca", "Modelo", "Repuesto", "Precio"])

# Función para verificar credenciales
def check_credentials(username, password):
    with open(USERS_FILE, "r") as f:
        for line in f:
            stored_user, stored_pass = line.strip().split(":")
            if username == stored_user and password == stored_pass:
                return True
    return False

# Función para manejar el archivo CSV
def get_parts():
    return pd.read_csv(PARTS_FILE)

def save_parts(df):
    df.to_csv(PARTS_FILE, index=False)

# Sidebar
st.sidebar.title("Celufix 📱")
menu = st.sidebar.radio("Menú", ["Inicio", "Iniciar Sesión"])

if menu == "Inicio":
    st.title("Bienvenido a Celufix")
    st.subheader("Buscar repuestos por modelo de teléfono")
    
    search_term = st.text_input("Ingrese el modelo del teléfono:")
    
    if search_term:
        parts_df = get_parts()
        results = parts_df[parts_df['Modelo'].str.contains(search_term, case=False)]
        
        if not results.empty:
            st.write("Resultados de la búsqueda:")
            st.dataframe(results)
        else:
            st.warning("No se encontraron repuestos para ese modelo.")

elif menu == "Iniciar Sesión":
    st.title("Inicio de Sesión")
    
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        if check_credentials(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Inicio de sesión exitoso!")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# Dashboard (solo accesible si está logueado)
if st.session_state.get("logged_in", False):
    st.sidebar.empty()
    st.sidebar.title(f"Bienvenido, {st.session_state.username}")
    logout = st.sidebar.button("Cerrar Sesión")
    
    if logout:
        del st.session_state.logged_in
        st.experimental_rerun()
    
    st.title("Dashboard de Celufix")
    
    option = st.sidebar.selectbox(
        "Opciones",
        ["Ver Repuestos", "Agregar Repuesto", "Editar Repuesto", "Eliminar Repuesto"]
    )
    
    parts_df = get_parts()
    
    if option == "Ver Repuestos":
        st.subheader("Todos los repuestos")
        st.dataframe(parts_df)
        
    elif option == "Agregar Repuesto":
        st.subheader("Agregar nuevo repuesto")
        
        with st.form("add_form", clear_on_submit=True):
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            repuesto = st.text_input("Repuesto")
            precio = st.number_input("Precio", min_value=0.0, step=0.01)
            
            submitted = st.form_submit_button("Agregar")
            
            if submitted:
                if marca and modelo and repuesto and precio:
                    new_id = parts_df['ID'].max() + 1 if not parts_df.empty else 1
                    new_row = pd.DataFrame([[new_id, marca, modelo, repuesto, precio]], 
                                         columns=["ID", "Marca", "Modelo", "Repuesto", "Precio"])
                    parts_df = pd.concat([parts_df, new_row], ignore_index=True)
                    save_parts(parts_df)
                    st.success("Repuesto agregado correctamente!")
                else:
                    st.warning("Por favor complete todos los campos")
    
    elif option == "Editar Repuesto":
        st.subheader("Editar repuesto existente")
        
        edit_option = st.radio("Buscar por:", ["ID", "Modelo"])
        
        if edit_option == "ID":
            id_to_edit = st.number_input("ID del repuesto a editar", min_value=1, step=1)
            part_to_edit = parts_df[parts_df['ID'] == id_to_edit]
        else:
            model_to_edit = st.text_input("Modelo del repuesto a editar")
            part_to_edit = parts_df[parts_df['Modelo'] == model_to_edit]
        
        if not part_to_edit.empty:
            st.write("Repuesto a editar:")
            st.write(part_to_edit)
            
            with st.form("edit_form"):
                marca = st.text_input("Marca", value=part_to_edit.iloc[0]['Marca'])
                modelo = st.text_input("Modelo", value=part_to_edit.iloc[0]['Modelo'])
                repuesto = st.text_input("Repuesto", value=part_to_edit.iloc[0]['Repuesto'])
                precio = st.number_input("Precio", 
                                       value=float(part_to_edit.iloc[0]['Precio']), 
                                       min_value=0.0, step=0.01)
                
                submitted = st.form_submit_button("Actualizar")
                
                if submitted:
                    idx = part_to_edit.index[0]
                    parts_df.at[idx, 'Marca'] = marca
                    parts_df.at[idx, 'Modelo'] = modelo
                    parts_df.at[idx, 'Repuesto'] = repuesto
                    parts_df.at[idx, 'Precio'] = precio
                    save_parts(parts_df)
                    st.success("Repuesto actualizado correctamente!")
        else:
            st.warning("No se encontró el repuesto")
    
    elif option == "Eliminar Repuesto":
        st.subheader("Eliminar repuesto")
        
        id_to_delete = st.number_input("ID del repuesto a eliminar", min_value=1, step=1)
        part_to_delete = parts_df[parts_df['ID'] == id_to_delete]
        
        if not part_to_delete.empty:
            st.write("Repuesto a eliminar:")
            st.write(part_to_delete)
            
            if st.button("Confirmar eliminación"):
                parts_df = parts_df[parts_df['ID'] != id_to_delete]
                save_parts(parts_df)
                st.success("Repuesto eliminado correctamente!")
        else:
            st.warning("No se encontró el repuesto con ese ID")
