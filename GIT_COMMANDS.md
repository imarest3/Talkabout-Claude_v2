# 🚀 Comandos para Guardar en GitHub

## Paso 1: Verificar el estado actual
```bash
git status
```

## Paso 2: Añadir archivos importantes al staging area
```bash
# Añadir archivos modificados
git add backend/Dockerfile
git add backend/entrypoint.sh
git add docker-compose.yml
git add .gitignore

# Añadir la guía de Postman
git add POSTMAN_GUIDE.md
```

## Paso 3: Ver qué se va a commitear
```bash
git status
```

## Paso 4: Hacer el commit con un mensaje descriptivo
```bash
git commit -m "feat: Fix Docker entrypoint and database configuration

- Added entrypoint.sh for database migrations and static files
- Installed netcat-openbsd in Dockerfile for healthcheck
- Fixed PostgreSQL healthcheck to use POSTGRES_DB
- Updated .gitignore to exclude Celery and test files
- Added comprehensive Postman testing guide"
```

## Paso 5: Subir los cambios a GitHub
```bash
git push origin ivan/second-main
```

## Paso 6: Verificar que se subió correctamente
```bash
git log --oneline -5
```

---

## 📋 Resumen de Cambios que se Guardarán

### Archivos Modificados:
- ✅ `backend/Dockerfile` - Añadido netcat-openbsd y ENTRYPOINT
- ✅ `backend/entrypoint.sh` - Script de inicialización (NUEVO)
- ✅ `docker-compose.yml` - Healthcheck mejorado
- ✅ `.gitignore` - Excluye archivos temporales

### Archivos Nuevos:
- ✅ `POSTMAN_GUIDE.md` - Guía completa de pruebas

### Archivos Excluidos (en .gitignore):
- ❌ `celerybeat-schedule` - Archivo temporal de Celery
- ❌ `verify_api.py` - Script de pruebas (no para producción)
- ❌ `create_test_data.py` - Script de pruebas (no para producción)

---

## 🔄 Comandos Rápidos (Todo en Uno)

Si quieres hacerlo todo de una vez:

```bash
# Añadir archivos
git add backend/Dockerfile backend/entrypoint.sh docker-compose.yml .gitignore POSTMAN_GUIDE.md

# Commit
git commit -m "feat: Fix Docker entrypoint and database configuration

- Added entrypoint.sh for database migrations and static files
- Installed netcat-openbsd in Dockerfile for healthcheck
- Fixed PostgreSQL healthcheck to use POSTGRES_DB
- Updated .gitignore to exclude Celery and test files
- Added comprehensive Postman testing guide"

# Push
git push origin ivan/second-main
```

---

## ✅ Verificación Post-Push

Después de hacer push, verifica en GitHub:
1. Ve a tu repositorio en GitHub
2. Verifica que aparezca el nuevo commit
3. Revisa que los archivos estén actualizados

---

## 💡 Tips

- **Mensaje de commit**: Usa el formato `tipo: descripción` (feat, fix, docs, etc.)
- **Commits frecuentes**: Haz commits pequeños y frecuentes
- **Branch**: Estás en `ivan/second-main`, asegúrate de que sea la correcta
- **Pull antes de Push**: Si trabajas en equipo, haz `git pull` antes de `git push`
