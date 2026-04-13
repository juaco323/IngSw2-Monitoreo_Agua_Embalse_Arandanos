# Instrucciones para crear la tabla alert_limits en Supabase

## Paso 1: Acceder a Supabase

1. Ve a https://supabase.com
2. Inicia sesión en tu cuenta
3. Selecciona el proyecto correspondiente
4. Ve a "SQL Editor" en el panel izquierdo

## Paso 2: Ejecutar el script SQL

1. Haz clic en "New Query"
2. Copia el contenido del archivo `CREATE_ALERT_LIMITS_TABLE.sql`
3. Pégalo en el editor SQL
4. Haz clic en "Run" (o presiona Ctrl+Enter)

## Paso 3: Verificar que se creó correctamente

1. Ve a "Table editor" en el panel izquierdo
2. Deberías ver una tabla llamada `alert_limits`
3. Verifica que tenga las siguientes columnas:
   - id (bigint)
   - admin_id (uuid)
   - sensor_type (text)
   - min_value (numeric)
   - max_value (numeric)
   - safe_max (numeric)
   - created_at (timestamp)
   - updated_at (timestamp)

## Paso 4: Verificar las políticas RLS

1. Ve a "Authentication" > "Policies" en el panel izquierdo
2. Selecciona la tabla `alert_limits`
3. Deberías ver las siguientes políticas:
   - Admins can manage their alert limits
   - Admins can view all alert limits
   - Users can view alert limits
   - Only admins can create alert limits
   - Only admins can update alert limits
   - Only admins can delete alert limits

## Ahora la aplicación puede:

✅ Guardar límites de alerta cuando un admin los modifica
✅ Cargar límites de alerta desde la base de datos
✅ Guardar automáticamente en Supabase (sin depender solo de localStorage)

## Nota importante:

La tabla usa `admin_id` como referencia a `auth.users(id)`. Cuando crees un admin en la aplicación, automáticamente se creará un registro en `users_roles` con `role = 'admin'`.
