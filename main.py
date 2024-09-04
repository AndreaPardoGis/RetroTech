from flask import Flask, render_template, request, redirect, url_for, session
import os
import db
from models import Producto, Proveedor, Usuario, Cliente, Compras
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import seaborn as sns


app = Flask(__name__)


# Esta es la funcion de inicio
@app.route("/")
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    # Se carga  el  template  index.html


# Con esta funcion creamos un usuario
@app.route("/register")
def homeUsuario():
    return render_template("register.html")


# Esta funcion para los usuarios tipo cliente,
# nos muestra todos los productos que un cliente pueden comprar
@app.route("/client/<email_usuario>")
def homeClient(email_usuario):
    cliente = db.session.query(Cliente).filter_by(email=email_usuario).first()
    todos_los_productos = db.session.query(Producto).all()
    return render_template("client.html", cliente=cliente, todos_los_productos=todos_los_productos)


# Esta funcion es para los usuarios tipo administrador,
# nos muestra la informacion de productos, proveedores, clientes y las compras
@app.route("/admin/<email_usuario>")
def homeAdmin(email_usuario):
    usuario = db.session.query(Usuario).filter_by(email=email_usuario).first()
    todos_los_productos = db.session.query(Producto).all()
    todos_los_proveedores = db.session.query(Proveedor).all()
    todos_los_clientes = db.session.query(Cliente).all()
    todas_las_compras = db.session.query(Compras).all()

    return render_template("admin.html",
                           admin=usuario,
                           todos_los_productos=todos_los_productos,
                           todos_los_proveedores=todos_los_proveedores,
                           todos_los_clientes=todos_los_clientes,
                           todas_las_compras=todas_las_compras)


# Esta funcion nos envia a la pagina principal del usuario tipo proveedor
# se envian los datos del proveedor y sus productos relacionados
@app.route("/proveedor/<email_usuario>")
def homeProveedor(email_usuario):
    proveedor = db.session.query(Proveedor).filter_by(email=email_usuario).first()
    todos_los_productos = db.session.query(Producto).filter_by(id_provedor=proveedor.id).all()

    return render_template("provider.html", proveedor=proveedor, todos_los_productos=todos_los_productos)


# Esta funcion nos envia a la pagina donde el administrador
# puede visualizar las graficas relacionadas con las ventas
# se envia el correo del administrador
@app.route("/stats-admin/<email_admin>")
def lookShopStats(email_admin):
    admin = db.session.query(Usuario).filter_by(email=email_admin).first()
    todos_los_productos = db.session.query(Producto).all()
    todas_las_compras = db.session.query(Compras).all()

    global data_stats
    global data_stats_ventas
    global data_stats_producto
    global lista_cantidad_producto_comprado
    global lista_nombre_producto_comprado
    global lista_cantidad_producto_comprado
    global lista_nombre_producto
    global lista_categoria_producto

    data_stats = {}
    data_stats_ventas = {}
    data_stats_producto = {}
    lista_cantidad_producto_comprado = []
    lista_nombre_producto_comprado = []
    lista_categoria_producto_comprado = []
    lista_nombre_producto = []
    lista_categoria_producto = []

    for compra in todas_las_compras:
        compra_nombre = compra.nombre_producto
        compra_categoria = compra.categoria_producto
        compra_cantidad = compra.cantidad
        lista_cantidad_producto_comprado.append(compra_cantidad)
        lista_nombre_producto_comprado.append(compra_nombre)
        lista_categoria_producto_comprado.append(compra_categoria)
        data_stats.update({"nombre_producto_comprado": lista_nombre_producto_comprado,
                           "categoria_producto_comprado": lista_categoria_producto_comprado,
                           "cantidad_producto_comprado": lista_cantidad_producto_comprado})
        data_stats_ventas.update({"nombre_producto_comprado": lista_nombre_producto_comprado,
                           "categoria_producto_comprado": lista_categoria_producto_comprado,
                           "cantidad_producto_comprado": lista_cantidad_producto_comprado})

    for producto in todos_los_productos:
        nombre_producto = producto.nombre
        categoria_producto = producto.categoria
        lista_nombre_producto.append(nombre_producto)
        lista_categoria_producto.append(categoria_producto)
        data_stats.update({"nombre_producto_vendido": lista_nombre_producto,
                           "categoria_producto_vendido": lista_categoria_producto})
        data_stats_producto.update({"nombre_producto_vendido": lista_nombre_producto,
                                    "categoria_producto_vendido": lista_categoria_producto})

    # estructura de datos de los productos en la tienda
    df_productos = pd.DataFrame(data_stats_producto)

    # estructura de datos de las ventas en la tienda
    df_compras = pd.DataFrame(data_stats_ventas)
    # los ragrupamos por nombre productos
    df_nombre_compra_group = df_compras.groupby(by='nombre_producto_comprado').sum()
    # hacemos una estructura de datos con el index de esta nueva estructura de datos, que son los nombres de los productos
    dataframe_nombre_compra = df_nombre_compra_group.index.values
    # los productos comprados los ragrupamos por categorias
    df_categoria_compra_group = df_compras.groupby(by='categoria_producto_comprado').sum()
    # hacemos una estructura de datos con el index de ese nueva estructura de datos, que son las categorias de los productos
    dataframe_categoria_compra = df_categoria_compra_group.index.values

    # convertimos en array la cantidad de los productos comprados segun su nombre
    cantidad_nombre_producto_comprado = df_nombre_compra_group['cantidad_producto_comprado'].tolist()
    # convertimos en array los nombres de los productos
    nombre_producto_comprado = dataframe_nombre_compra.tolist()
    # convertimos en array la cantidad de los productos comprados segun su categoria
    cantidad_categoria_producto_comprado = df_categoria_compra_group['cantidad_producto_comprado'].tolist()
    # convertimos en array las categorias de los productos
    categoria_producto_comprado = dataframe_categoria_compra.tolist()

    chart_bar_nombre_vs_cantidad_url = createBarChartNombreCantidad(nombre_producto_comprado,
                                                                    cantidad_nombre_producto_comprado)

    chart_pie_nombre_vs_cantidad_url = createPieChartNombreCantidad(nombre_producto_comprado,
                                                                    cantidad_nombre_producto_comprado)

    chart_bar_categoria_vs_cantidad_url = createBarChartNombreCantidad(categoria_producto_comprado,
                                                                       cantidad_categoria_producto_comprado)

    chart_pie_categoria_vs_cantidad_url = createPieChartCategoriaCantidad(categoria_producto_comprado,
                                                                          cantidad_categoria_producto_comprado)

    return render_template("statsAdmin.html",
                           admin=admin,
                           chart_bar_nombre_vs_cantidad_url=chart_bar_nombre_vs_cantidad_url,
                           chart_bar_categoria_vs_cantidad_url=chart_bar_categoria_vs_cantidad_url,
                           chart_pie_nombre_vs_cantidad_url=chart_pie_nombre_vs_cantidad_url,
                           chart_pie_categoria_vs_cantidad_url=chart_pie_categoria_vs_cantidad_url)


# Grafico de barras de el nombre de
# los productos que se han comprado comprados y sus cantidades
def createBarChartNombreCantidad(nombre_producto_comprado, cantidad_nombre_producto_comprado):
    imgBarA = BytesIO()
    sns.set_style("white")
    barA = plt
    barA.figure(figsize=(10, 6), facecolor='#9f9f23')

    barA.bar(nombre_producto_comprado,
             cantidad_nombre_producto_comprado,
             width=0.3)

    barA.ylabel("Cantidad")
    barA.legend()
    barA.savefig(imgBarA, format='png')
    barA.close()
    imgBarA.seek(0)
    chart_bar_nombre_vs_cantidad_url = base64.b64encode(imgBarA.getvalue()).decode('utf8')
    return chart_bar_nombre_vs_cantidad_url


# Grafico de barras de el nombre de
# la categoria de los productos que se han comprado y sus cantidades
def createBarChartCategoriaCantidad(categoria_producto_comprado, cantidad_categoria_producto_comprado):
    imgBarB = BytesIO()
    sns.set_style("white")
    barB = plt
    barB.figure(figsize=(10, 6), facecolor='#9f9f23')
    barB.ylabel("Cantidad")

    barB.bar(categoria_producto_comprado,
             cantidad_categoria_producto_comprado,
             # color='green',
             width=0.3)

    barB.legend()
    barB.savefig(imgBarB, format='png')
    barB.close()
    imgBarB.seek(0)
    chart_bar_categoria_vs_cantidad_url = base64.b64encode(imgBarB.getvalue()).decode('utf8')
    return chart_bar_categoria_vs_cantidad_url


# Grafico de barras de el nombre de
# los productos que se han comprado comprados y sus cantidades
def createPieChartNombreCantidad(nombre_producto_comprado, cantidad_nombre_producto_comprado):
    imgPieA = BytesIO()
    pieA = plt
    fig = plt.figure(figsize=(10, 6), facecolor='#9f9f23')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('equal')
    pieA.pie(cantidad_nombre_producto_comprado,
            labels=nombre_producto_comprado,
            autopct='%1.1f%%')
    pieA.legend()
    pieA.savefig(imgPieA, format='png')
    pieA.close()
    imgPieA.seek(0)
    chart_pie_nombre_vs_cantidad_url = base64.b64encode(imgPieA.getvalue()).decode('utf8')
    return chart_pie_nombre_vs_cantidad_url


# Grafico de barras de el nombre de
# la categoria de los productos que se han comprado y sus cantidades
def createPieChartCategoriaCantidad(categoria_producto_comprado, cantidad_categoria_producto_comprado):
    imgPieB = BytesIO()
    pieB = plt
    fig = plt.figure(figsize=(10, 6), facecolor='#9f9f23')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('equal')
    pieB.pie(cantidad_categoria_producto_comprado,
            labels=categoria_producto_comprado,
            autopct='%1.2f%%')
    pieB.legend()
    pieB.savefig(imgPieB, format='png')
    pieB.close()
    imgPieB.seek(0)
    chart_pie_categoria_vs_cantidad_url = base64.b64encode(imgPieB.getvalue()).decode('utf8')
    return chart_pie_categoria_vs_cantidad_url


# Esta es la funcion para la pagina de los productos comprados el usuario de tipo cliente
@app.route("/client-orders/<id_cliente>")
def lookClientOrders(id_cliente):
    cliente = db.session.query(Cliente).filter_by(id=int(id_cliente)).first()
    id_cliente = cliente.id
    todas_las_compras = db.session.query(Compras).filter_by(id_comprador=int(id_cliente)).all()
    global lista_productos
    lista_productos = []
    for producto_comprado in todas_las_compras:
        id_producto_comprado = producto_comprado.id_producto
        producto = db.session.query(Producto).filter_by(id=int(id_producto_comprado)).first()
        lista_productos.append(producto)
        # lista_productos.append(producto_comprado.cantidad)

    return render_template("comprasCliente.html", cliente=cliente, lista_productos=lista_productos)


# Esta es la funcion para la pagina register
# Nos manda al inicio
@app.route("/back-register")
def backRegister():
    return redirect(url_for("home"))


# Esta es la funcion para la pagina donde creamos los productos
# nos envia al home del usuario del tipo proveedor
@app.route("/back-create-edit/<email_proveedor>")
def backCreate(email_proveedor):
    proveedor = db.session.query(Proveedor).filter_by(email=email_proveedor).first()
    email_proveedor = proveedor.email
    return redirect(url_for("homeProveedor", email_usuario=email_proveedor))


# Esta es la funcion para la pagina donde podemos acabar nuestra compra
# nos envia a la home del usuario de tipo cliente
@app.route("/back-client-home/<id_cliente>")
def backClient(id_cliente):
    cliente = db.session.query(Cliente).filter_by(id=int(id_cliente)).first()
    email_cliente = cliente.email
    return redirect(url_for("homeClient", email_usuario=email_cliente))


# Esta es la funcion para redirigir al usuario de tipo administrador a su página de inicio
@app.route("/back-admin-home/<email_admin>")
def backAdmin(email_admin):
    admin = db.session.query(Usuario).filter_by(email=email_admin).first()
    email_admin = admin.email
    return redirect(url_for("homeAdmin", email_usuario=email_admin))


# Esta es la funcion para el boton crear en la home del usuario de tipo proveedor
# nos envia a la pagina para poder crear un producto y envia los datos del proveedor
@app.route("/crear/<id_provedor>")
def crear(id_provedor):
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_provedor)).first()
    return render_template("createProduct.html", proveedor=proveedor)


# Esta es la funcion para el boton editar en la home del usuario de tipo proveedor
# nos envia a la pagina para poder editar un producto y envia los datos del proveedor y del producto seleccionado
@app.route("/editar/<id_producto><id_proveedor>")
def editar(id_producto, id_proveedor):
    producto = db.session.query(Producto).filter_by(id=int(id_producto)).first()
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_proveedor)).first()
    return render_template("editProduct.html", productoSeleccionado=producto, proveedor=proveedor)


# Esta es la funcion de login
# aqui buscamos en la base de datos todos lo usuarios registrados
# y se comprueba si el correo la contraseña son iguales
# segun el tipo de usuario se reenvia a su home
# Tambien aparecen los datos de error del formulario
# si algun campo se introduce incorrectamente
@app.route("/login", methods=['POST'])
def login():
    todos_los_usuarios = db.session.query(Usuario).all()
    email = request.form['email_usuario']
    password = request.form['password_usuario']
    error_general = False
    error_password = False
    error_both = False
    error_mail = False
    if todos_los_usuarios:
        for usuario in todos_los_usuarios:
            if ((email == usuario.email) and (password == usuario.password)):
                if (usuario.tipo_usuario == 'Cliente'):
                    session['logged_in'] = True
                    if (usuario.datas == 1):
                        email_usuario = usuario.email
                        return redirect(url_for("homeClient", email_usuario=email_usuario))
                    else:
                        return render_template("createClient.html", usuario=usuario)
                elif (usuario.tipo_usuario == 'Administrador'):
                    session['logged_in'] = True
                    email_usuario = usuario.email
                    return redirect(url_for("homeAdmin", email_usuario=email_usuario))
                elif (usuario.tipo_usuario == 'Proveedor'):
                    session['logged_in'] = True
                    if (usuario.datas == 1):
                        email_usuario = usuario.email
                        return redirect(url_for("homeProveedor", email_usuario=email_usuario))
                    else:
                        return render_template("createProvedor.html", usuario=usuario)
            elif not email and email == "" and not password and password == "":
                error_both = True
            elif not email and email == "":
                error_mail = True
            elif not password and password == "":
                error_password = True
            else:
                error_general = True
    else:
        error_general_no_users = "Los datos no son correctos"
        return render_template("index.html", error=error_general_no_users)

    if error_general:
        error_general_mensaje = "Los datos no son correctos"
        return render_template("index.html", error=error_general_mensaje)
    elif error_password:
        error_password_mensaje = "Es necesaria una password"
        return render_template("index.html", error=error_password_mensaje)
    elif error_both:
        error_both_mensaje = "Es necesaria una mail y una password"
        return render_template("index.html", error=error_both_mensaje)
    elif error_mail:
        error_mail_mensaje = "Es necesario una mail"
        return render_template("index.html", error=error_mail_mensaje)


# Esta es la funcion para la pagina register donde creamos un nuevo usuario
# registramos elcorreo y la contraseña y redirige a la home principal
# para poder hacer el login una vez registrado
# Tambien aparecen los datos de error del formulario
# si algun campo se introduce incorrectamente
@app.route('/crear-usuario', methods=['POST'])
def crearUsuario():
    new_email = request.form['nueva_email']
    new_password = request.form['nueva_password']
    todos_los_usuarios = db.session.query(Usuario).all()
    for usuario in todos_los_usuarios:
        if new_email == usuario.email:
            error_mail = "Email ya utilizada"
            return render_template("register.html", error_mail=error_mail)
    if not new_email and new_email == "" and not new_password and new_password == "":
        error_both = "Es necesaria una mail y una password"
        return render_template("register.html", error_both=error_both)
    elif not new_email and new_email == "":
        error_mail = "Es necesario una mail"
        return render_template("register.html", error_mail=error_mail)
    elif not new_password and new_password == "":
        error_password = "Es necesaria una password"
        return render_template("register.html", error_password=error_password)
    else:
        nuevo_usuario = Usuario(email=new_email,
                                password=new_password,
                                tipo_usuario=request.form['nuevo_tipo'])
        message = "El usuario se ha creado correctamente"

        db.session.add(nuevo_usuario)
        db.session.commit()
        db.session.close()

    return render_template("index.html", message=message)


# Esta es la funcion de logout, para salir de nuestra cuenta
# nos redirige a la home principal
@app.route("/logout", methods=['GET'])
def logout():
    session['logged_in'] = False
    return redirect(url_for("home"))


# Esta es la funcion donde se completaan los datos del proveedor
# si el usuario del tipo proveedor tiene el parametro datos en false (si es nuevo)
# despues del login reenviamos el usuairo de tipo proveedor a una pagina para completar el resto de sus datos
# con el id cogemos su correo y conectamos los datos que acabamos de rellenar al usuario de tipo proveedor
# se redirige a la home principal donde aparece el mensaje
# de confirmacion de que el perfil se ha completado puede hacer login
@app.route('/crear-provedor/<id_usuario>', methods=['POST'])
def crearProvedor(id_usuario):
    usuario = db.session.query(Usuario).filter_by(id=int(id_usuario)).first()
    nombre_empresa = request.form['nombre_empresa']
    telefono_empresa = request.form['telefono_empresa']
    direccion_empresa = request.form['direccion_empresa']
    ciudad_empresa = request.form['ciudad_empresa']
    provincia_empresa = request.form['provincia_empresa']
    iva_empresa = request.form['iva_empresa']

    if not nombre_empresa and nombre_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not telefono_empresa and telefono_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not direccion_empresa and direccion_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not ciudad_empresa and ciudad_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not provincia_empresa and provincia_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not iva_empresa and iva_empresa == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    else:
        proveedor = Proveedor(nombre_empresa=nombre_empresa,
                              telefono=telefono_empresa,
                              direccion=direccion_empresa,
                              email=usuario.email,
                              ciudad=ciudad_empresa,
                              provincia=provincia_empresa,
                              iva=iva_empresa)
        usuario.datas = True
        message = "Perfil completado correctamente"

    # id no es necesario asignarlo manualmente, porque la primary key se genera automaticamente
    db.session.add(proveedor)  # Añadir objeto Producto a la base de datos
    db.session.commit()  # Ejecutar operación pendiente de la base de datos
    db.session.close()
    return render_template("index.html", message=message)


# Esta es la funcion para crear un producto, accedemos mediante la funcion crear (proveedor)
# cuando se crea un producto se relaciona al proveedor a traves del id y el nombre de la empresa y
# luego se reenvia el usuario de tipo proveedor a su home
# y se envia el id para que se cargen todos sus productos
# y el manejo de errorres con sus respectivos mensajes
@app.route('/crear-producto/<id_provedor>', methods=['POST'])
def crearProducto(id_provedor):
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_provedor)).first()
    nombre = request.form['nombre_producto']
    descripcion = request.form['descripcion_producto']
    stock_maximo_str = request.form['stock_maximo_producto']
    deposito = request.form['deposito_producto']
    referencia = request.form['referencia_producto']
    categoria = request.form['categoria_producto']
    nombre_provedor = proveedor.nombre_empresa
    id_provedor = proveedor.id
    email_proveedor = proveedor.email
    precio_str = request.form['precio_producto']

    if stock_maximo_str:
        stock_maximo = int(stock_maximo_str)
    else:
        stock_maximo = 0

    if precio_str:
        precio = float(precio_str)
    else:
        precio = 0.0

    if not nombre and nombre == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not descripcion and descripcion == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not stock_maximo and stock_maximo == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not deposito and deposito == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not referencia and referencia == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not categoria and categoria == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif not precio and precio == "":
        error_general = "Son necesarios todos los datos requeridos"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif type(precio) == str:
        error_general = "Stock tiene que ser un numero entero"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    elif type(stock_maximo) == str or type(stock_maximo) == float:
        error_general = "Stock tiene que ser un numero entero"
        return render_template("createProduct.html", proveedor=proveedor, error_general=error_general)
    else:
        stock_minimo = ((stock_maximo * 90) / 100)
        stock_minimo_int = int(stock_minimo)
        producto = Producto(nombre=nombre,
                            descripcion=descripcion,
                            stock_maximo=stock_maximo,
                            stock=stock_maximo,
                            stock_minimo=stock_minimo_int,
                            deposito=deposito,
                            referencia=referencia,
                            categoria=categoria,
                            nombre_provedor=nombre_provedor,
                            id_provedor=id_provedor,
                            precio=precio)

    # id no es necesario asignarlo manualmente, porque la primary key se genera automaticamente
    db.session.add(producto)  # Añadir objeto Producto a la base de datos
    db.session.commit()  # Ejecutar operación pendiente de la base de datos
    db.session.close()
    return redirect(url_for("homeProveedor", email_usuario=email_proveedor))


@app.route('/recargar-producto/<id_producto><id_proveedor>')
def recargarProducto(id_producto, id_proveedor):
    # cojo el producto seleccionado
    producto = db.session.query(Producto).filter_by(id=int(id_producto)).first()
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_proveedor)).first()
    email_proveedor = proveedor.email

    producto.stock = producto.stock_maximo

    db.session.commit()  # Ejecutar la operación pendiente de la base de datos
    db.session.close()
    return redirect(url_for("homeProveedor", email_usuario=email_proveedor))

# Esta es la funcion para editar un producto
# desde la funcion editar que envia los datos del producto seleccionado y los datos del proveedor
# en la pagina de editing se envia el id del producto que queremos editar y el id del proveedor que esta editando
# se relaciona a traves del id
# cuando se ha modificado reenviamos el proveedor a su home y su id para que se cargen todos sus productos
@app.route('/editar-producto/<id_producto><id_proveedor>', methods=['POST'])
def editarProducto(id_producto, id_proveedor):
    # cojo el producto seleccionado
    producto = db.session.query(Producto).filter_by(id=int(id_producto)).first()
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_proveedor)).first()
    email_proveedor = proveedor.email
    # cogemos los datos
    vieja_nombre = request.form['vieja_nombre']
    nueva_nombre = request.form['nueva_nombre']
    if nueva_nombre:
        if nueva_nombre == "" or not nueva_nombre:
            producto.nombre = vieja_nombre
        else:
            producto.nombre = nueva_nombre
    else:
        producto.nombre = vieja_nombre
    vieja_descripcion = request.form['vieja_descripcion']
    nueva_descripcion = request.form['nueva_descripcion']
    if nueva_descripcion:
        if nueva_descripcion == "" or not nueva_descripcion:
            producto.descripcion = vieja_descripcion
        else:
            producto.descripcion = nueva_descripcion
    else:
        producto.descripcion = vieja_descripcion
    vieja_stock_maximo = request.form['vieja_stock_maximo']
    nueva_stock_maximo = request.form['nueva_stock_maximo']
    if nueva_stock_maximo:
        if nueva_stock_maximo == "" or not nueva_stock_maximo:
            producto.stock_maximo = vieja_stock_maximo
            producto.stock = vieja_stock_maximo
        else:
            producto.stock_maximo = nueva_stock_maximo
            producto.stock = nueva_stock_maximo
            stock_int = int(nueva_stock_maximo)
            stock_minimo = ((stock_int * 90) / 100)
            producto.stock_minimo = stock_minimo
    else:
        producto.stock_maximo = vieja_stock_maximo
        producto.stock = vieja_stock_maximo

    vieja_deposito = request.form['vieja_deposito']
    nueva_deposito = request.form['nueva_deposito']
    if nueva_deposito:
        if nueva_deposito == "" or not nueva_deposito:
            producto.deposito = vieja_deposito
        else:
            producto.deposito = nueva_deposito
    else:
        producto.deposito = vieja_deposito
    vieja_referencia = request.form['vieja_referencia']
    nueva_referencia = request.form['nueva_referencia']
    if nueva_referencia:
        if nueva_referencia == "" or not nueva_referencia:
            producto.referencia = vieja_referencia
        else:
            producto.referencia = nueva_referencia
    else:
        producto.referencia = vieja_referencia
    vieja_categoria = request.form['vieja_categoria']
    nueva_categoria = request.form['nueva_categoria']
    if nueva_categoria:
        if nueva_categoria == "" or not nueva_categoria:
            producto.categoria = vieja_categoria
        else:
            producto.categoria = nueva_categoria
    else:
        producto.categoria = vieja_categoria
    vieja_provedor = request.form['vieja_provedor']
    nueva_provedor = request.form['nueva_provedor']
    if nueva_provedor:
        if nueva_provedor == "" or not nueva_provedor:
            producto.provedor = vieja_provedor
        else:
            producto.provedor = nueva_provedor
    else:
        producto.provedor = vieja_provedor
    vieja_precio = request.form['vieja_precio']
    nueva_precio = request.form['nueva_precio']
    if nueva_precio:
        if nueva_precio == "" or not nueva_precio:
            producto.precio = vieja_precio
        else:
            producto.precio = nueva_precio
    else:
        producto.precio = vieja_precio

    db.session.commit()
    # Ejecutar la operación pendiente de la base de datos
    db.session.close()
    return redirect(url_for('homeProveedor', email_usuario=email_proveedor))


# Esta es la funcion para eliminar un producto
# se envia el id de un producto para seleccionar el que se va a eliminar
# se redirige a la home del usuario de tipo proveedor con su id para que se carguen todos sus productos
@app.route('/eliminar-producto/<id_producto><id_proveedor>')
def eliminarProducto(id_producto, id_proveedor):
    producto = db.session.query(Producto).filter_by(id=int(id_producto)).first()
    producto.activo = False
    proveedor = db.session.query(Proveedor).filter_by(id=int(id_proveedor)).first()
    email_proveedor = proveedor.email
    # en la base de datos se busca el id que coincide con
    # el registro que se quiere eliminar y se elimina
    db.session.commit()
    # Ejecutar la operación pendiente de la base de datos
    db.session.close()
    return redirect(url_for('homeProveedor', email_usuario=email_proveedor))
    # Esta parte nos redirige a la función home() y la tarea eliminada ya no aparece en el listado


# Esta es la funcion que sirve para completar los datos del cliente
# si el usuario de tipo cliente tiene el parametro datos en false (la primera vez)
# despues del login se redirige al usuairo de tipo cliente a una pagina donde completar sus datos
# con el id se determina el usuario y con su email conectamos el usuario al cliente
# redirigimos a la home principal donde aparece
# el mensaje de confirmacion de que el perfil se ha completado
# y el manejo de los errores
@app.route('/crear-cliente/<id_usuario>', methods=['POST'])
def crearCliente(id_usuario):
    usuario = db.session.query(Usuario).filter_by(id=int(id_usuario)).first()
    nombre_cliente = request.form['nombre_cliente']
    apellido_cliente = request.form['apellido_cliente']
    telefono_cliente = request.form['telefono_cliente']
    direccion_cliente = request.form['direccion_cliente']
    ciudad_cliente = request.form['ciudad_cliente']
    provincia_cliente = request.form['provincia_cliente']

    if not nombre_cliente and nombre_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not apellido_cliente and apellido_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not telefono_cliente and telefono_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not direccion_cliente and direccion_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not ciudad_cliente and ciudad_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    elif not provincia_cliente and provincia_cliente == "":
        error_general = "Son necesarios todos los datos"
        return render_template("createProvedor.html", error_general=error_general)
    else:
        cliente = Cliente(nombre=nombre_cliente,
                          apellido=apellido_cliente,
                          email=usuario.email,
                          telefono=telefono_cliente,
                          direccion=direccion_cliente,
                          ciudad=ciudad_cliente,
                          provincia=provincia_cliente)
        usuario.datas = True
        message = "Perfil completato correctamente"

    # id no es necesario asignarlo manualmente, porque la primary key se genera automaticamente
    db.session.add(cliente)  # Añadir objeto Producto a la base de datos
    db.session.commit()  # Ejecutar operación pendiente de la base de datos
    db.session.close()
    return render_template("index.html", message=message)


@app.route("/buy-redirect/<email_comprador><id_producto>")
def buyRedirect(email_comprador, id_producto):
    # con todos_los_productos seleccionamos el producto elegido
    todos_los_productos = db.session.query(Producto).filter_by(id=int(id_producto)).first()
    precio_producto = todos_los_productos.precio
    # con cliente seleccionamos quien esta comprando
    cliente = db.session.query(Cliente).filter_by(email=email_comprador).first()
    # con precio se envia el precio del producto comprado
    precio = precio_producto
    return render_template("comprar.html", producto=todos_los_productos, cliente=cliente, precio=precio)


# Esta es la funcion que nos redirige a la pagina para terminar la compra
# se envian los datos del proveedor, y los productos relacionados con el
@app.route("/comprar/<email_comprador><id_producto>", methods=["POST"])
def comprar(email_comprador, id_producto):
    # con todos_los_productos seleccionamos el producto elegido
    todos_los_productos = db.session.query(Producto).filter_by(id=id_producto).first()
    producto_comprado = todos_los_productos.id
    nombre_producto = todos_los_productos.nombre
    categoria_producto = todos_los_productos.categoria
    # con cliente seleccionamos quien esta comprando
    cliente = db.session.query(Cliente).filter_by(email=email_comprador).first()
    email_comprador = cliente.email
    nombre_comprador = cliente.nombre
    apellido_comprador = cliente.apellido
    id_comprador = cliente.id
    # con cantidad se envia la cantidad de ese producto que se ha comprado
    cantidad = request.form['cantidad_producto']
    cantidad_producto = cantidad
    if not cantidad_producto or cantidad_producto == 0:
        message = "Tienes que seleccionar una cantidad o vuelve atras"
        return render_template("comprar.html", producto=todos_los_productos, cliente=cliente, message=message)
    else:
        nueva_compra = Compras(id_producto=producto_comprado,
                               nombre_producto=nombre_producto,
                               categoria_producto=categoria_producto,
                               id_comprador=id_comprador,
                               nombre_comprador=nombre_comprador,
                               apellido_comprador=apellido_comprador,
                               cantidad=cantidad_producto)

        nuevo_stock = (int(todos_los_productos.stock) - int(cantidad_producto))
        todos_los_productos.stock = nuevo_stock


    db.session.add(nueva_compra)
    db.session.commit()
    db.session.close()
    return redirect(url_for("homeClient", email_usuario=email_comprador))


if __name__ == "__main__":

    # Estamos indicando a SQLAlchemy que cree, si no existen, las tablas de todos los modelos que encuentre en models.py
    db.Base.metadata.create_all(db.engine)
    app.secret_key = os.urandom(12)
    app.run(debug=True)
