# Aplicación Web de Gestión de Ventas y Compras

Este proyecto es una aplicación web desarrollada con Flask, un framework de Python para construir aplicaciones web. 
La aplicación tiene como objetivo proporcionar un sistema integral de gestión de ventas y compras para una tienda retro de tecnología.

Con una interfaz de usuario intuitiva y funcionalidades robustas, la aplicación ofrece una solución sencilla para administrar el negocio de una manera eficiente y efectiva.

## Tipos de Usuarios

La aplicación permite el registro y acceso a tres tipos de usuarios:

1. **Administrador**: Tiene acceso a la información sobre proveedores, clientes, productos y sus ventas.
2. **Proveedor**: Registra su empresa en la aplicación y sus productos para venderlos.
3. **Cliente**: Compra los productos disponibles en la aplicación.

## Estructura de la Aplicación

La aplicación está estructurada en varios módulos, cada uno con un propósito específico:

### Base de Datos

Utilizando SQLAlchemy, la aplicación interactúa con una base de datos SQLite para almacenar y gestionar información relacionada con usuarios, 
proveedores, clientes, productos y compras. Los modelos de datos están definidos de manera clara y concisa, siguiendo prácticas de diseño de bases de datos relacionales.

### Controladores

Los controladores manejan las solicitudes HTTP y coordinan la lógica de negocio de la aplicación. 
Estas funciones se encargan de procesar las peticiones del usuario, realizar operaciones en la base de datos y generar respuestas adecuadas. 
Cada controlador está asociado a una ruta específica de la aplicación y sigue un enfoque de diseño orientado a objetos para mantener el código modular y reutilizable.

### Plantillas HTML

La aplicación utiliza el motor de plantillas Jinja2 para generar contenido dinámico en las vistas HTML. 
Las plantillas están diseñadas de manera cuidadosa para proporcionar una experiencia de usuario fluida y atractiva. 
Se aplican principios de diseño web responsivo para garantizar que la aplicación sea accesible desde una variedad de dispositivos y tamaños de pantalla.

### Estilos CSS

Los estilos CSS definen la apariencia visual de la aplicación, incluyendo colores, tipografías, márgenes y espaciados. 
Se sigue una metodología de diseño basada en componentes para mantener la coherencia y la consistencia en toda la interfaz de usuario. 
Además, se utilizan técnicas avanzadas de CSS, como flexbox y grid, para crear diseños flexibles y adaptables.
