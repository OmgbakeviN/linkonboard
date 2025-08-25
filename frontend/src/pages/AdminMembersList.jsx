// src/pages/AdminMembersList.jsx
import { useEffect, useState } from "react";
import api from "../api";

export default function AdminMembersList() {
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.get("/admin/members-with-form/")
      .then(res => setRows(res.data || []))
      .catch(() => setErr("Impossible de charger la liste"));
  }, []);

  return (
    <div style={{ maxWidth: 1100, margin: "20px auto", padding: 24 }}>
      <h1>Membres & Formulaires</h1>
      {err && <div style={{ color:"crimson" }}>{err}</div>}
      <table width="100%" cellPadding="8" style={{ borderCollapse:"collapse" }}>
        <thead>
          <tr style={{ background:"#f5f5f5" }}>
            <th>Nom</th><th>Email</th><th>Téléphone</th><th>Naissance</th>
            <th>Invite</th><th>Utilisateur</th><th>Rôle</th><th>Soumis le</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r,i)=>(
            <tr key={i} style={{ borderBottom:"1px solid #eee" }}>
              <td>{r.full_name}</td>
              <td>{r.email}</td>
              <td>{r.phone}</td>
              <td>{r.birth_date}</td>
              <td>{r.invite_status} / {r.token.slice(0,8)}…</td>
              <td>{r.username || "-"}</td>
              <td>{r.role}</td>
              <td>{new Date(r.submission_created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
