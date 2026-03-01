import streamlit as st
import pandas as pd
import datetime
import re

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Mi E-Commerce",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado para imitar un poco los colores de Mercado Libre (Amarillo clásico)
st.markdown("""
    <style>
    .stApp > header {
        background-color: #FFF159;
    }
    .titulo-principal {
        color: #333333;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
    }
    .producto-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .precio {
        font-size: 24px;
        color: #333333;
        font-weight: 300;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# BASE DE DATOS SIMULADA (SESSION STATE)
# ==========================================
# Aquí guardamos los productos para que no se borren al recargar la página
if 'productos' not in st.session_state:
    st.session_state.productos = [
        {
            "id": 1, 
            "nombre": "Smartphone Galaxy S23", 
            "categoria": "Celulares", 
            "precio": 850.00, 
            "stock": 10, 
            "descripcion": "Teléfono de alta gama con cámara de 50MP y batería de larga duración.", 
            "imagen": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=300&q=80"
        },
        {
            "id": 2, 
            "nombre": "Laptop ProBook 15", 
            "categoria": "Computación", 
            "precio": 1200.00, 
            "stock": 5, 
            "descripcion": "Laptop ideal para trabajo y diseño con 16GB de RAM y procesador i7.", 
            "imagen": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=300&q=80"
        },
        {
            "id": 3, 
            "nombre": "Audífonos Bluetooth Noise Cancelling", 
            "categoria": "Electrónica", 
            "precio": 150.00, 
            "stock": 20, 
            "descripcion": "Audífonos inalámbricos con cancelación de ruido activa.", 
            "imagen": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=300&q=80"
        }
    ]

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

if 'chat_historial' not in st.session_state:
    st.session_state.chat_historial = [
        {"role": "assistant", "content": "¡Hola! Soy tu asistente de compras. Puedes preguntarme por productos, precios, disponibilidad o cualquier duda que tengas sobre nuestro catálogo."}
    ]

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def agregar_al_carrito(producto):
    st.session_state.carrito.append(producto)
    st.toast(f"✅ Se añadió '{producto['nombre']}' al carrito.", icon="🛒")

def eliminar_del_carrito(index):
    producto_eliminado = st.session_state.carrito.pop(index)
    st.toast(f"❌ Se eliminó '{producto_eliminado['nombre']}' del carrito.", icon="🗑️")

def vaciar_carrito():
    st.session_state.carrito = []
    st.toast("El carrito ha sido vaciado.", icon="🧹")

# ==========================================
# LÓGICA DEL CHATBOT INTELIGENTE
# ==========================================
def generar_respuesta_chatbot(mensaje_usuario):
    """
    Este chatbot lee el catálogo actual de st.session_state.productos.
    Para hacerlo 'capaz de responder cualquier pregunta' con IA real, 
    aquí se conectaría la API de OpenAI (ChatGPT) o Google Gemini.
    Por ahora, utiliza un motor de búsqueda avanzado simulado.
    """
    mensaje_lower = mensaje_usuario.lower()
    respuesta = ""
    productos_encontrados = []
    
    # Saludos básicos
    if any(saludo in mensaje_lower for saludo in ["hola", "buenas", "que tal", "saludos"]):
        return "¡Hola! ¿En qué te puedo ayudar hoy? Puedes preguntarme qué productos tenemos, buscar por categoría (ej. Celulares, Computación) o consultar precios."

    # Búsqueda en el catálogo
    for prod in st.session_state.productos:
        # Busca coincidencias en nombre, categoría o descripción
        if (prod["nombre"].lower() in mensaje_lower or 
            prod["categoria"].lower() in mensaje_lower or 
            any(palabra in mensaje_lower for palabra in prod["nombre"].lower().split())):
            productos_encontrados.append(prod)

    if "disponible" in mensaje_lower or "tienen" in mensaje_lower or "hay" in mensaje_lower or "busco" in mensaje_lower:
        if productos_encontrados:
            respuesta = "¡Sí, tenemos opciones para ti! He encontrado esto en nuestro catálogo:\n\n"
            for p in productos_encontrados:
                disponibilidad = f"¡En stock! ({p['stock']} disponibles)" if p['stock'] > 0 else "Agotado por el momento."
                respuesta += f"- **{p['nombre']}** a ${p['precio']}. {disponibilidad}\n  *Características:* {p['descripcion']}\n\n"
            respuesta += "¿Te gustaría que te ayude con algo más o quieres ir a la tienda a añadirlos a tu carrito?"
            return respuesta
        else:
            # Extraer posibles categorías del catálogo para sugerir
            categorias = list(set([p['categoria'] for p in st.session_state.productos]))
            cat_str = ", ".join(categorias)
            return f"Actualmente no encontré exactamente lo que buscas en nuestro catálogo activo. Sin embargo, tenemos productos en las categorías de: **{cat_str}**. ¿Te interesa explorar alguna de ellas?"

    if "precio" in mensaje_lower or "cuanto cuesta" in mensaje_lower:
        if productos_encontrados:
            respuesta = "Aquí tienes los precios que encontré:\n"
            for p in productos_encontrados:
                respuesta += f"- El **{p['nombre']}** cuesta **${p['precio']}**.\n"
            return respuesta

    if productos_encontrados:
        respuesta = "Esto es lo que encontré basado en tu consulta:\n"
        for p in productos_encontrados:
            respuesta += f"- **{p['nombre']}** (${p['precio']}) - Categoría: {p['categoria']}\n"
        return respuesta

    # Respuesta por defecto (Fallback)
    return ("No estoy muy seguro de a qué te refieres. "
            "Intenta preguntarme si tenemos un producto en específico (ej. '¿Tienen laptops?'), "
            "o pregunta por el precio de algo (ej. '¿Cuánto cuesta el smartphone?'). "
            "¡Estoy conectado directamente a nuestro inventario para darte la mejor respuesta!")


# ==========================================
# BARRA LATERAL (NAVEGACIÓN)
# ==========================================
st.sidebar.image("https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.22.8/mercadolibre/logo__large_plus.png", width=150)
st.sidebar.title("Navegación")
opciones_menu = ["🏪 Tienda (Compradores)", "🛒 Mi Carrito", "🤖 Asistente Virtual", "⚙️ Panel de Vendedor (Admin)"]
seleccion = st.sidebar.radio("Ir a:", opciones_menu)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Items en Carrito:** {len(st.session_state.carrito)}")

# ==========================================
# VISTAS DE LA APLICACIÓN
# ==========================================

# ------------------------------------------
# VISTA: TIENDA PÚBLICA
# ------------------------------------------
if seleccion == "🏪 Tienda (Compradores)":
    st.markdown('<h1 class="titulo-principal">Encuentra todo lo que buscas</h1>', unsafe_allow_html=True)
    
    # Buscador y Filtro
    col_busqueda, col_filtro = st.columns([3, 1])
    with col_busqueda:
        texto_busqueda = st.text_input("Buscar productos, marcas y más...", placeholder="Ej. Laptop, Samsung, Audífonos...")
    with col_filtro:
        categorias_disponibles = ["Todas"] + list(set([p["categoria"] for p in st.session_state.productos]))
        categoria_seleccionada = st.selectbox("Filtrar por Categoría", categorias_disponibles)

    # Filtrar productos
    productos_mostrar = st.session_state.productos
    if categoria_seleccionada != "Todas":
        productos_mostrar = [p for p in productos_mostrar if p["categoria"] == categoria_seleccionada]
    if texto_busqueda:
        productos_mostrar = [p for p in productos_mostrar if texto_busqueda.lower() in p["nombre"].lower() or texto_busqueda.lower() in p["descripcion"].lower()]

    st.markdown("---")

    # Mostrar productos en una cuadrícula
    if not productos_mostrar:
        st.warning("No se encontraron productos con esos filtros. ¡Intenta otra búsqueda!")
    else:
        # Crear filas de 3 columnas
        cols = st.columns(3)
        for i, producto in enumerate(productos_mostrar):
            col = cols[i % 3] # Distribuir en las columnas
            with col:
                st.markdown('<div class="producto-card">', unsafe_allow_html=True)
                
                # Imagen del producto
                if producto.get("imagen"):
                    st.image(producto["imagen"], use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x200?text=Sin+Imagen", use_container_width=True)
                
                st.markdown(f"**{producto['nombre']}**")
                st.markdown(f"<span class='precio'>${producto['precio']:,.2f}</span>", unsafe_allow_html=True)
                st.caption(f"Categoría: {producto['categoria']} | Stock: {producto['stock']}")
                
                with st.expander("Ver descripción"):
                    st.write(producto["descripcion"])
                
                # Botón añadir al carrito
                if producto['stock'] > 0:
                    st.button("Agregar al carrito", key=f"add_{producto['id']}", on_click=agregar_al_carrito, args=(producto,), use_container_width=True, type="primary")
                else:
                    st.button("Agotado", key=f"out_{producto['id']}", disabled=True, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# VISTA: CARRITO DE COMPRAS
# ------------------------------------------
elif seleccion == "🛒 Mi Carrito":
    st.markdown('<h1 class="titulo-principal">Tu Carrito de Compras</h1>', unsafe_allow_html=True)
    
    if len(st.session_state.carrito) == 0:
        st.info("Tu carrito está vacío. ¡Ve a la tienda para descubrir grandes productos!")
        if st.button("Ir a la tienda", type="primary"):
            st.rerun()
    else:
        total = 0
        for i, item in enumerate(st.session_state.carrito):
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
            with col1:
                st.image(item["imagen"], width=80)
            with col2:
                st.markdown(f"**{item['nombre']}**")
                st.caption(item["categoria"])
            with col3:
                st.markdown(f"**${item['precio']:,.2f}**")
                total += item['precio']
            with col4:
                st.button("❌ Eliminar", key=f"del_{i}", on_click=eliminar_del_carrito, args=(i,))
            st.divider()

        st.markdown(f"### Total a pagar: ${total:,.2f}")
        
        col_comprar, col_vaciar = st.columns([2, 1])
        with col_comprar:
            if st.button("Proceder al Pago (Checkout)", type="primary", use_container_width=True):
                st.success("¡Compra simulada con éxito! Gracias por probar el sistema.")
                st.balloons()
                st.session_state.carrito = [] # Vaciamos tras comprar
        with col_vaciar:
            st.button("Vaciar Carrito", on_click=vaciar_carrito, use_container_width=True)

# ------------------------------------------
# VISTA: PANEL DE VENDEDOR (ADMIN)
# ------------------------------------------
elif seleccion == "⚙️ Panel de Vendedor (Admin)":
    st.markdown('<h1 class="titulo-principal">Panel de Control del Vendedor</h1>', unsafe_allow_html=True)
    st.write("Sube tus productos aquí. Aparecerán instantáneamente en la tienda pública y el chatbot sabrá de ellos.")
    
    with st.form("form_nuevo_producto"):
        st.subheader("Subir Nuevo Producto")
        
        col1, col2 = st.columns(2)
        with col1:
            nuevo_nombre = st.text_input("Nombre del Producto*")
            nueva_categoria = st.selectbox("Categoría*", ["Celulares", "Computación", "Electrónica", "Ropa", "Hogar", "Otros", "Añadir nueva..."])
            if nueva_categoria == "Añadir nueva...":
                nueva_categoria = st.text_input("Escribe la nueva categoría")
        with col2:
            nuevo_precio = st.number_input("Precio ($)*", min_value=0.0, step=10.0)
            nuevo_stock = st.number_input("Stock disponible*", min_value=0, step=1, value=1)
        
        nueva_desc = st.text_area("Descripción y Características*")
        nueva_img = st.text_input("URL de la Imagen (opcional)", placeholder="https://ejemplo.com/imagen.jpg")
        
        submit_btn = st.form_submit_button("Publicar Producto", type="primary")
        
        if submit_btn:
            if nuevo_nombre and nueva_categoria and nueva_desc:
                nuevo_id = max([p["id"] for p in st.session_state.productos], default=0) + 1
                
                nuevo_item = {
                    "id": nuevo_id,
                    "nombre": nuevo_nombre,
                    "categoria": nueva_categoria,
                    "precio": nuevo_precio,
                    "stock": nuevo_stock,
                    "descripcion": nueva_desc,
                    "imagen": nueva_img if nueva_img else "https://via.placeholder.com/300x200?text=Sin+Imagen"
                }
                st.session_state.productos.append(nuevo_item)
                st.success(f"¡Producto '{nuevo_nombre}' publicado con éxito!")
            else:
                st.error("Por favor, completa los campos obligatorios (*).")
                
    st.markdown("---")
    st.subheader("Tu Inventario Actual")
    df_inventario = pd.DataFrame(st.session_state.productos)
    # Mostramos la tabla excluyendo algunas columnas técnicas para que se vea limpio
    if not df_inventario.empty:
        st.dataframe(df_inventario[["id", "nombre", "categoria", "precio", "stock"]], use_container_width=True)
    else:
        st.info("No tienes productos en tu inventario.")

# ------------------------------------------
# VISTA: CHATBOT ASISTENTE
# ------------------------------------------
elif seleccion == "🤖 Asistente Virtual":
    st.markdown('<h1 class="titulo-principal">Asistente Virtual IA</h1>', unsafe_allow_html=True)
    st.write("Soy tu bot conectado al catálogo. Pregúntame sobre disponibilidad, precios o características.")
    
    # Contenedor principal del chat
    contenedor_chat = st.container(height=400)
    
    # Mostrar historial
    with contenedor_chat:
        for mensaje in st.session_state.chat_historial:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])

    # Entrada de texto del usuario
    if prompt := st.chat_input("Escribe tu pregunta aquí (ej. ¿Tienen celulares?)..."):
        # Añadir mensaje del usuario al historial
        st.session_state.chat_historial.append({"role": "user", "content": prompt})
        
        # Mostrar mensaje del usuario inmediatamente
        with contenedor_chat:
            with st.chat_message("user"):
                st.markdown(prompt)
                
            # Mostrar que el bot está "pensando"
            with st.chat_message("assistant"):
                respuesta = generar_respuesta_chatbot(prompt)
                st.markdown(respuesta)
        
        # Guardar respuesta del bot
        st.session_state.chat_historial.append({"role": "assistant", "content": respuesta})
