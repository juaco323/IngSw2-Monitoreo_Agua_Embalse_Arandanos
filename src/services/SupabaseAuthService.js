import { supabase } from './supabaseClient'

/**
 * Crear un nuevo usuario en Supabase
 * @param {string} email 
 * @param {string} password 
 * @param {string} fullName 
 * @param {string} role - 'admin' o 'employee'
 * @returns {Promise<{success: boolean, error?: string, userId?: string}>}
 */
export async function createUserInSupabase(email, password, fullName, role) {
  try {
    // 1. Crear usuario en Auth de Supabase
    const { data: authData, error: authError } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true
    })

    if (authError) {
      console.error('Error creating auth user:', authError)
      return {
        success: false,
        error: authError.message || 'Error al crear usuario en autenticación'
      }
    }

    const userId = authData.user.id

    // 2. Insertar en tabla users_roles
    const { error: roleError } = await supabase
      .from('users_roles')
      .insert([
        {
          id: userId,
          email,
          full_name: fullName,
          role: role === 'admin' ? 'admin' : 'employee',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ])

    if (roleError) {
      console.error('Error inserting user role:', roleError)
      // Intentar limpiar el usuario de auth si algo falla en roles
      await supabase.auth.admin.deleteUser(userId)
      return {
        success: false,
        error: roleError.message || 'Error al asignar rol al usuario'
      }
    }

    return {
      success: true,
      userId
    }
  } catch (error) {
    console.error('Exception in createUserInSupabase:', error)
    return {
      success: false,
      error: error.message
    }
  }
}

/**
 * Obtener todos los usuarios
 * @returns {Promise<Array>}
 */
export async function getAllUsers() {
  try {
    const { data, error } = await supabase
      .from('users_roles')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching users:', error)
      return []
    }

    return data || []
  } catch (error) {
    console.error('Exception in getAllUsers:', error)
    return []
  }
}

/**
 * Obtener un usuario por ID
 * @param {string} userId 
 * @returns {Promise<Object|null>}
 */
export async function getUserById(userId) {
  try {
    const { data, error } = await supabase
      .from('users_roles')
      .select('*')
      .eq('id', userId)
      .single()

    if (error) {
      console.error('Error fetching user:', error)
      return null
    }

    return data
  } catch (error) {
    console.error('Exception in getUserById:', error)
    return null
  }
}

/**
 * Actualizar rol de un usuario
 * @param {string} userId 
 * @param {string} newRole - 'admin' o 'employee'
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function updateUserRole(userId, newRole) {
  try {
    const { error } = await supabase
      .from('users_roles')
      .update({
        role: newRole === 'admin' ? 'admin' : 'employee',
        updated_at: new Date().toISOString()
      })
      .eq('id', userId)

    if (error) {
      console.error('Error updating user role:', error)
      return {
        success: false,
        error: error.message
      }
    }

    return { success: true }
  } catch (error) {
    console.error('Exception in updateUserRole:', error)
    return {
      success: false,
      error: error.message
    }
  }
}

/**
 * Eliminar un usuario (de auth y de users_roles)
 * @param {string} userId 
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function deleteUserFromSupabase(userId) {
  try {
    // 1. Eliminar de users_roles
    const { error: roleError } = await supabase
      .from('users_roles')
      .delete()
      .eq('id', userId)

    if (roleError) {
      console.error('Error deleting user role:', roleError)
      return {
        success: false,
        error: roleError.message
      }
    }

    // 2. Eliminar de Auth
    const { error: authError } = await supabase.auth.admin.deleteUser(userId)

    if (authError) {
      console.error('Error deleting auth user:', authError)
      // No retornamos error aquí porque ya eliminamos del DB
    }

    return { success: true }
  } catch (error) {
    console.error('Exception in deleteUserFromSupabase:', error)
    return {
      success: false,
      error: error.message
    }
  }
}

/**
 * Obtener usuarios con un rol específico
 * @param {string} role - 'admin' o 'employee'
 * @returns {Promise<Array>}
 */
export async function getUsersByRole(role) {
  try {
    const { data, error } = await supabase
      .from('users_roles')
      .select('*')
      .eq('role', role)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching users by role:', error)
      return []
    }

    return data || []
  } catch (error) {
    console.error('Exception in getUsersByRole:', error)
    return []
  }
}

/**
 * Obtener usuario actual desde auth
 * @returns {Promise<Object|null>}
 */
export async function getCurrentUser() {
  try {
    const { data, error } = await supabase.auth.getUser()

    if (error) {
      console.error('Error getting current user:', error)
      return null
    }

    if (!data.user) return null

    // Obtener detalles adicionales de users_roles
    const userRole = await getUserById(data.user.id)

    return {
      id: data.user.id,
      email: data.user.email,
      ...userRole
    }
  } catch (error) {
    console.error('Exception in getCurrentUser:', error)
    return null
  }
}

/**
 * Guardar o actualizar límites de alerta para un sensor
 * @param {string} adminId - ID del usuario admin
 * @param {string} sensorType - 'ph', 'temperature', 'conductivity'
 * @param {number} minValue 
 * @param {number} maxValue 
 * @param {number} safeMaxValue 
 * @returns {Promise<{success: boolean, error?: string, data?: Object}>}
 */
export async function saveAlertLimits(adminId, sensorType, minValue, maxValue, safeMaxValue) {
  try {
    const { data, error } = await supabase
      .from('alert_limits')
      .upsert({
        admin_id: adminId,
        sensor_type: sensorType,
        min_value: minValue,
        max_value: maxValue,
        safe_max: safeMaxValue,
        updated_at: new Date().toISOString()
      }, {
        onConflict: 'admin_id,sensor_type'
      })
      .select()

    if (error) {
      console.error('Error saving alert limits:', error)
      return {
        success: false,
        error: error.message
      }
    }

    return {
      success: true,
      data: data ? data[0] : null
    }
  } catch (error) {
    console.error('Exception in saveAlertLimits:', error)
    return {
      success: false,
      error: error.message
    }
  }
}

/**
 * Obtener límites de alerta para un sensor específico por admin
 * @param {string} adminId - ID del usuario admin
 * @param {string} sensorType - 'ph', 'temperature', 'conductivity'
 * @returns {Promise<Object|null>}
 */
export async function getAlertLimitsBySensorAndAdmin(adminId, sensorType) {
  try {
    const { data, error } = await supabase
      .from('alert_limits')
      .select('*')
      .eq('admin_id', adminId)
      .eq('sensor_type', sensorType)
      .single()

    if (error && error.code !== 'PGRST116') { // PGRST116 = no rows found
      console.error('Error fetching alert limits:', error)
      return null
    }

    return data || null
  } catch (error) {
    console.error('Exception in getAlertLimitsBySensorAndAdmin:', error)
    return null
  }
}

/**
 * Obtener todos los límites de alerta para un admin
 * @param {string} adminId - ID del usuario admin
 * @returns {Promise<Array>}
 */
export async function getAlertLimitsByAdmin(adminId) {
  try {
    const { data, error } = await supabase
      .from('alert_limits')
      .select('*')
      .eq('admin_id', adminId)
      .order('sensor_type', { ascending: true })

    if (error) {
      console.error('Error fetching alert limits for admin:', error)
      return []
    }

    return data || []
  } catch (error) {
    console.error('Exception in getAlertLimitsByAdmin:', error)
    return []
  }
}

/**
 * Obtener límites de alerta para un tipo de sensor (todos los admins)
 * @param {string} sensorType - 'ph', 'temperature', 'conductivity'
 * @returns {Promise<Array>}
 */
export async function getAlertLimitsBySensor(sensorType) {
  try {
    const { data, error } = await supabase
      .from('alert_limits')
      .select('*')
      .eq('sensor_type', sensorType)
      .order('updated_at', { ascending: false })

    if (error) {
      console.error('Error fetching alert limits for sensor:', error)
      return []
    }

    return data || []
  } catch (error) {
    console.error('Exception in getAlertLimitsBySensor:', error)
    return []
  }
}

/**
 * Eliminar límites de alerta
 * @param {string} id - ID del registro de alert_limits
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function deleteAlertLimit(id) {
  try {
    const { error } = await supabase
      .from('alert_limits')
      .delete()
      .eq('id', id)

    if (error) {
      console.error('Error deleting alert limit:', error)
      return {
        success: false,
        error: error.message
      }
    }

    return { success: true }
  } catch (error) {
    console.error('Exception in deleteAlertLimit:', error)
    return {
      success: false,
      error: error.message
    }
  }
}

export default {
  createUserInSupabase,
  getAllUsers,
  getUserById,
  updateUserRole,
  deleteUserFromSupabase,
  getUsersByRole,
  getCurrentUser,
  saveAlertLimits,
  getAlertLimitsBySensorAndAdmin,
  getAlertLimitsByAdmin,
  getAlertLimitsBySensor,
  deleteAlertLimit
}
