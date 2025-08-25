import { useState } from "react";
import axios from "axios";
import api from "../api";

export default function LoginPage() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [err, setErr] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    try {
      const res = await api.post("/token/", form);
      localStorage.setItem("access", res.data.access);
      localStorage.setItem("refresh", res.data.refresh);
      // redirige : client -> dashboard, member -> mur
      // (tu peux appeler /api/me plus tard; pour l'instant choisis une page)
      window.location.href = "/wall";
    } catch (e) {
      setErr("Identifiants invalides");
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: "40px auto", padding: 24 }}>
      <h1>Connexion</h1>
      <form onSubmit={onSubmit} style={{ display: "grid", gap: 10 }}>
        <input
          placeholder="Nom d'utilisateur"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          required
        />
        <input
          type="password"
          placeholder="Mot de passe"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          required
        />
        <button type="submit">Se connecter</button>
      </form>
      {err && <div style={{ color: "crimson", marginTop: 8 }}>{err}</div>}
    </div>
  );
}
