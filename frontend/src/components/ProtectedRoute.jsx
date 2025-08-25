// src/components/ProtectedRoute.jsx
import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children, allow = "ANY" }) {
  const access = localStorage.getItem("access");
  const role = localStorage.getItem("role"); // à setter au login
  if (!access) return <Navigate to="/login" replace />;

  if (allow === "CLIENT" && role !== "CLIENT") return <Navigate to="/wall" replace />;
  if (allow === "MEMBER" && role !== "MEMBER") return <Navigate to="/dashboard" replace />;

  return children;
}
