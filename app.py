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

# Estilo avanzado para imitar fielmente la UI de Mercado Libre
st.markdown("""
    <style>
    /* Fondo general gris claro de Mercado Libre */
    .stApp, .main {
        background-color: #ebebeb !important;
    }
    
    /* Barra superior amarilla */
    header[data-testid="stHeader"] {
        background-color: #ffe600 !important;
        box-shadow: 0 1px 0 0 rgba(0,0,0,.1);
    }

    /* Estilos del Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e6e6e6;
    }

    /* Títulos generales */
    .titulo-principal {
        color: #333333;
        font-family: 'Proxima Nova', -apple-system, Roboto, Arial, sans-serif;
        font-weight: 600;
        font-size: 26px;
        margin-bottom: 20px;
        padding-top: 10px;
    }

    /* Personalización de los contenedores para que parezcan Tarjetas (Cards) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 1px 2px 0 rgba(0,0,0,.12) !important;
        transition: box-shadow 0.3s ease-in-out !important;
        padding: 0px !important;
        overflow: hidden;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 5px 15px 0 rgba(0,0,0,.2) !important;
    }

    /* Botón Primario (Azul Mercado Libre) */
    button[kind="primary"] {
        background-color: #3483fa !important;
        border-color: #3483fa !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 10px 0px !important;
        transition: background-color 0.2s !important;
    }
    button[kind="primary"]:hover {
        background-color: #2968c8 !important;
    }

    /* Botón Secundario */
    button[kind="secondary"] {
        color: #3483fa !important;
        border-color: #3483fa !important;
        background-color: transparent !important;
        font-weight: 600 !important;
    }
    button[kind="secondary"]:hover {
        background-color: rgba(52, 131, 250, 0.1) !important;
    }

    /* Clases de texto personalizadas para los productos */
    .precio-ml {
        font-size: 24px;
        color: #333333;
        font-weight: 400;
        margin-bottom: 0px;
        line-height: 1.2;
    }
    .envio-gratis {
        color: #00a650;
        font-weight: 600;
        font-size: 13px;
        margin-top: 2px;
        margin-bottom: 8px;
    }
    .nombre-prod {
        color: #666666;
        font-size: 14px;
        font-weight: 400;
        line-height: 1.3;
        margin-bottom: 15px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;  
        overflow: hidden;
        height: 36px;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# BASE DE DATOS SIMULADA (SESSION STATE)
# ==========================================
if 'productos' not in st.session_state:
    st.session_state.productos = [
        {
            "id": 1, 
            "nombre": "Smartphone Samsung Galaxy S23 Ultra 256gb", 
            "categoria": "Celulares", 
            "precio": 850.00, 
            "stock": 10, 
            "descripcion": "Teléfono de alta gama con cámara de 50MP y batería de larga duración.", 
            "imagen": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": 2, 
            "nombre": "Apple MacBook Pro 14 M2 512gb", 
            "categoria": "Computación", 
            "precio": 1999.00, 
            "stock": 5, 
            "descripcion": "Laptop ideal para trabajo y diseño con Chip M2, 16GB de RAM.", 
            "imagen": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": 3, 
            "nombre": "Audífonos Inalámbricos Sony Wh-1000xm4 Nc", 
            "categoria": "Electrónica", 
            "precio": 298.00, 
            "stock": 20, 
            "descripcion": "Audífonos inalámbricos con cancelación de ruido activa.", 
            "imagen": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=400&q=80"
        },
        {
            "id": 4, 
            "nombre": "Smart TV LG 55 Pulgadas 4K UHD", 
            "categoria": "Electrónica", 
            "precio": 450.00, 
            "stock": 8, 
            "descripcion": "Televisor inteligente con resolución 4K y webOS.", 
            "imagen": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=400&q=80"
        }
    ]

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

if 'chat_historial' not in st.session_state:
    st.session_state.chat_historial = [
        {"role": "assistant", "content": "¡Hola! Soy tu asistente de compras. ¿Qué estás buscando hoy?"}
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
    mensaje_lower = mensaje_usuario.lower()
    respuesta = ""
    productos_encontrados = []
    
    if any(saludo in mensaje_lower for saludo in ["hola", "buenas", "que tal", "saludos"]):
        return "¡Hola! ¿En qué te puedo ayudar hoy? Puedes preguntarme qué productos tenemos, buscar por categoría (ej. Celulares) o consultar precios."

    for prod in st.session_state.productos:
        if (prod["nombre"].lower() in mensaje_lower or 
            prod["categoria"].lower() in mensaje_lower or 
            any(palabra in mensaje_lower for palabra in prod["nombre"].lower().split())):
            productos_encontrados.append(prod)

    if "disponible" in mensaje_lower or "tienen" in mensaje_lower or "hay" in mensaje_lower or "busco" in mensaje_lower:
        if productos_encontrados:
            respuesta = "¡Sí! He encontrado esto en nuestro catálogo:\n\n"
            for p in productos_encontrados:
                disponibilidad = f"¡En stock! ({p['stock']} disponibles)" if p['stock'] > 0 else "Agotado."
                respuesta += f"- **{p['nombre']}** a ${p['precio']}. {disponibilidad}\n"
            return respuesta
        else:
            categorias = list(set([p['categoria'] for p in st.session_state.productos]))
            return f"No encontré eso exacto, pero tenemos productos en estas categorías: **{', '.join(categorias)}**."

    if productos_encontrados:
        respuesta = "Esto es lo que encontré:\n"
        for p in productos_encontrados:
            respuesta += f"- **{p['nombre']}** (${p['precio']})\n"
        return respuesta

    return "No estoy seguro de a qué te refieres. Intenta preguntar por un producto (ej. '¿Tienen laptops?')."


# ==========================================
# BARRA LATERAL (NAVEGACIÓN)
# ==========================================
# Usamos logo tipo ML
st.sidebar.image("https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.22.8/mercadolibre/logo__large_plus.png", width=140)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

opciones_menu = ["🏪 Ofertas de hoy", "🛒 Mi Carrito", "🤖 Preguntas y Ayuda", "⚙️ Vender (Admin)"]
seleccion = st.sidebar.radio("Navegación", opciones_menu, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.info(f"**Tu Carrito:** {len(st.session_state.carrito)} items")

# ==========================================
# VISTAS DE LA APLICACIÓN
# ==========================================

# ------------------------------------------
# VISTA: TIENDA PÚBLICA
# ------------------------------------------
if seleccion == "🏪 Ofertas de hoy":
    
    # Barra de búsqueda estilizada superior
    col_busqueda, col_filtro, col_espacio = st.columns([4, 2, 2])
    with col_busqueda:
        texto_busqueda = st.text_input("Buscador", placeholder="Buscar productos, marcas y más...", label_visibility="collapsed")
    with col_filtro:
        categorias_disponibles = ["Categorías"] + list(set([p["categoria"] for p in st.session_state.productos]))
        categoria_seleccionada = st.selectbox("Categorías", categorias_disponibles, label_visibility="collapsed")

    st.markdown('<h1 class="titulo-principal">Basado en tu última visita</h1>', unsafe_allow_html=True)

    # Filtrar productos
    productos_mostrar = st.session_state.productos
    if categoria_seleccionada != "Categorías":
        productos_mostrar = [p for p in productos_mostrar if p["categoria"] == categoria_seleccionada]
    if texto_busqueda:
        productos_mostrar = [p for p in productos_mostrar if texto_busqueda.lower() in p["nombre"].lower() or texto_busqueda.lower() in p["descripcion"].lower()]

    if not productos_mostrar:
        st.warning("No se encontraron productos.")
    else:
        # Crear filas de 4 columnas para un aspecto más de galería
        cols = st.columns(4)
        for i, producto in enumerate(productos_mostrar):
            col = cols[i % 4]
            with col:
                # Usamos st.container con borde para aprovechar el CSS que inyectamos
                with st.container(border=True):
                    # Imagen
                    if producto.get("imagen"):
                        st.image(producto["imagen"], use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x300?text=Sin+Imagen", use_container_width=True)
                    
                    # Contenido de la tarjeta
                    st.markdown(f"<p class='precio-ml'>$ {producto['precio']:,.0f}</p>", unsafe_allow_html=True)
                    
                    # Simular envío gratis si cuesta más de $200
                    if producto['precio'] > 200:
                        st.markdown("<p class='envio-gratis'>Llega gratis mañana</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p class='envio-gratis' style='color: transparent;'>-</p>", unsafe_allow_html=True) # Espaciador
                        
                    st.markdown(f"<p class='nombre-prod'>{producto['nombre']}</p>", unsafe_allow_html=True)
                    
                    # Botón
                    if producto['stock'] > 0:
                        st.button("Añadir al carrito", key=f"add_{producto['id']}", on_click=agregar_al_carrito, args=(producto,), use_container_width=True, type="primary")
                    else:
                        st.button("Agotado", key=f"out_{producto['id']}", disabled=True, use_container_width=True)

# ------------------------------------------
# VISTA: CARRITO DE COMPRAS
# ------------------------------------------
elif seleccion == "🛒 Mi Carrito":
    st.markdown('<h1 class="titulo-principal">Carrito de compras</h1>', unsafe_allow_html=True)
    
    if len(st.session_state.carrito) == 0:
        with st.container(border=True):
            st.info("Tu carrito está vacío.")
            st.write("¿No sabes qué comprar? ¡Miles de productos te esperan!")
            if st.button("Descubrir productos", type="primary"):
                st.rerun()
    else:
        col_listado, col_resumen = st.columns([2, 1])
        
        total = 0
        with col_listado:
            with st.container(border=True):
                st.subheader("Productos")
                st.divider()
                for i, item in enumerate(st.session_state.carrito):
                    c1, c2, c3 = st.columns([1, 3, 1])
                    with c1:
                        st.image(item["imagen"], width=80)
                    with c2:
                        st.markdown(f"**{item['nombre']}**")
                        st.button("Eliminar", key=f"del_{i}", on_click=eliminar_del_carrito, args=(i,), type="secondary")
                    with c3:
                        st.markdown(f"<h3 style='margin:0;'>${item['precio']:,.0f}</h3>", unsafe_allow_html=True)
                        total += item['precio']
                    st.divider()

        with col_resumen:
            with st.container(border=True):
                st.subheader("Resumen de compra")
                st.markdown(f"**Productos ({len(st.session_state.carrito)}):** ${total:,.0f}")
                st.markdown("**Envío:** ¡Gratis!")
                st.divider()
                st.markdown(f"### Total: ${total:,.0f}")
                
                if st.button("Continuar compra", type="primary", use_container_width=True):
                    st.success("¡Compra simulada con éxito!")
                    st.balloons()
                    st.session_state.carrito = [] 

# ------------------------------------------
# VISTA: PANEL DE VENDEDOR (ADMIN)
# ------------------------------------------
elif seleccion == "⚙️ Vender (Admin)":
    st.markdown('<h1 class="titulo-principal">Publicaciones</h1>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.subheader("Publicar un artículo")
        
        with st.form("form_nuevo_producto", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nuevo_nombre = st.text_input("Título de la publicación*")
                nueva_categoria = st.selectbox("Categoría*", ["Celulares", "Computación", "Electrónica", "Ropa", "Hogar", "Otros"])
            with col2:
                nuevo_precio = st.number_input("Precio ($)*", min_value=0.0, step=10.0)
                nuevo_stock = st.number_input("Stock disponible*", min_value=0, step=1, value=1)
            
            nueva_img = st.text_input("URL de la Imagen", placeholder="https://...")
            nueva_desc = st.text_area("Descripción*")
            
            submit_btn = st.form_submit_button("Publicar", type="primary")
            
            if submit_btn:
                if nuevo_nombre and nueva_desc:
                    nuevo_id = max([p["id"] for p in st.session_state.productos], default=0) + 1
                    nuevo_item = {
                        "id": nuevo_id, "nombre": nuevo_nombre, "categoria": nueva_categoria,
                        "precio": nuevo_precio, "stock": nuevo_stock, "descripcion": nueva_desc,
                        "imagen": nueva_img if nueva_img else "https://via.placeholder.com/300x300?text=Sin+Imagen"
                    }
                    st.session_state.productos.append(nuevo_item)
                    st.success(f"¡Publicación activa!")
                else:
                    st.error("Completa el título y descripción.")
                    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Tus publicaciones activas")
    df_inventario = pd.DataFrame(st.session_state.productos)
    if not df_inventario.empty:
        st.dataframe(df_inventario[["id", "nombre", "precio", "stock"]], use_container_width=True, hide_index=True)

# ------------------------------------------
# VISTA: CHATBOT ASISTENTE
# ------------------------------------------
elif seleccion == "🤖 Preguntas y Ayuda":
    st.markdown('<h1 class="titulo-principal">Centro de Ayuda y Preguntas</h1>', unsafe_allow_html=True)
    
    with st.container(border=True):
        contenedor_chat = st.container(height=450)
        
        with contenedor_chat:
            for mensaje in st.session_state.chat_historial:
                with st.chat_message(mensaje["role"]):
                    st.markdown(mensaje["content"])

        if prompt := st.chat_input("Escribe tu duda aquí..."):
            st.session_state.chat_historial.append({"role": "user", "content": prompt})
            
            with contenedor_chat:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    respuesta = generar_respuesta_chatbot(prompt)
                    st.markdown(respuesta)
            
            st.session_state.chat_historial.append({"role": "assistant", "content": respuesta})
