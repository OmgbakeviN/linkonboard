import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api"; // ou axios

export default function ClientDashboard() {
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("PENDING"); // filtre
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function load() {
    setLoading(true);
    setErr("");
    try {
      const res = await api.get(`/admin/submissions/`, { params: { status } });
      // si tu as une pagination DRF, res.data = { count, next, previous, results }
      const data = Array.isArray(res.data) ? res.data : res.data.results;
      setItems(data || []);
    } catch (e) {
      setErr("Impossible de charger la liste.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [status]);

  async function act(path) {
    try {
      await path();
      await load();
    } catch (e) {
      alert(e?.response?.data?.detail || "Action échouée");
    }
  }

  return (
    <div style={{ maxWidth: 980, margin: "20px auto", padding: 24 }}>
      <h1>Dashboard — Demandes</h1>
      <div>
        <Link to="/my-posts">Voir mes posts</Link>
      </div>

      <div style={{ display: "flex", gap: 8, alignItems: "center", margin: "12px 0" }}>
        <span>Filtrer :</span>
        {["PENDING", "APPROVED", "REJECTED"].map(s => (
          <button key={s} onClick={() => setStatus(s)} disabled={status===s}>
            {s}
          </button>
        ))}
        <button onClick={load} disabled={loading}>Rafraîchir</button>
      </div>

      {err && <div style={{ color:"crimson" }}>{err}</div>}
      {loading ? <div>Chargement…</div> : (
        <table width="100%" cellPadding="8" style={{ borderCollapse:"collapse" }}>
          <thead>
            <tr style={{ background:"#f5f5f5" }}>
              <th align="left">Nom</th>
              <th align="left">Email</th>
              <th align="left">Téléphone</th>
              <th align="left">Naissance</th>
              <th align="left">Statut</th>
              <th align="left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {items?.length ? items.map(row => (
              <tr key={row.id} style={{ borderBottom:"1px solid #eee" }}>
                <td>{row.full_name}</td>
                <td>{row.email}</td>
                <td>{row.phone}</td>
                <td>{row.birth_date}</td>
                <td>{row.status}</td>
                <td style={{ display:"flex", gap:8 }}>
                  <Link to={`/${row.token}`} target="_blank">Voir lien</Link>
                  {row.status === "PENDING" && (
                    <>
                      <button onClick={() => act(() => api.post(`/admin/submissions/${row.id}/approve/`))}>
                        Accepter
                      </button>
                      <button onClick={() => act(() => api.post(`/admin/submissions/${row.id}/reject/`))}>
                        Refuser
                      </button>
                    </>
                  )}
                </td>
              </tr>
            )) : (
              <tr><td colSpan="6">Aucune demande.</td></tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
