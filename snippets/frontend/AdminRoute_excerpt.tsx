/**
 * AdminRoute — guard de ruta para el panel de administración.
 *
 * Composición de dos verificaciones sobre AuthContext:
 *   1. Si no está autenticado → redirige a /login.
 *   2. Si está autenticado pero no es superadmin → redirige a /dashboard.
 *
 * Muestra un spinner mientras el contexto carga (evita el flash de redireccionamiento).
 * Usa React Router v7 <Outlet /> para renderizar rutas anidadas.
 */
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export function AdminRoute() {
  const { isAuthenticated, isSuperAdmin, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-950">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!isSuperAdmin) return <Navigate to="/dashboard" replace />;

  return <Outlet />;
}
