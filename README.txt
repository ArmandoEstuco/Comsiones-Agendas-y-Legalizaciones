PROYECTO DE COMISIONES, AGENDAS Y LEGALIZACIONES
Nota: solo hay base de datos y docker

Requisitos:
- Docker Desktop o Docker Engine con el complemento Docker Compose.

Archivos:
- docker-compose.yml: levanta PostgreSQL y Adminer.
- Dockerfile: construye una imagen sencilla basada en Adminer.
- init/01-esquema.sql: crea el esquema inicial y datos de estados/roles.

Iniciar:
1. Copia .env.template como .env.
2. Revisa y cambia los valores de .env, especialmente POSTGRES_PASSWORD.
3. Ejecuta: docker compose up -d --build
4. Entra en http://localhost:8085 para Adminer.

El archivo .env contiene credenciales locales y está excluido de Git mediante
.gitignore. Nunca lo subas al repositorio. Publica únicamente .env.template
con valores de ejemplo.

Datos de acceso en Adminer:
- Sistema: PostgreSQL
- Servidor: db
- Usuario: el valor de POSTGRES_USER en .env
- Contraseña: el valor de POSTGRES_PASSWORD en .env
- Base de datos: el valor de POSTGRES_DB en .env

IMPORTANTE:
- El SQL de init se ejecuta automáticamente solo cuando PostgreSQL inicializa un volumen vacío.
- Si ya habías iniciado la base y quieres borrar los datos y volver a crearla desde cero:
  docker compose down -v
  docker compose up -d --build
  ADVERTENCIA: down -v elimina los datos guardados en el volumen.
- Cambia POSTGRES_PASSWORD en .env antes de usarlo fuera de un entorno local.
- El esquema es una propuesta inicial; valida las relaciones y reglas de negocio con el equipo.
