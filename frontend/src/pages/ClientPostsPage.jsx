import { useEffect, useState } from "react";
import api from "../api";

export default function ClientPostsPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function load() {
    setLoading(true);
    setErr("");
    try {
      const res = await api.get("/posts/client/");
      // si DRF renvoie {count, results}, on gère les deux cas
      const data = Array.isArray(res.data) ? res.data : res.data.results;
      setRows(data || []);
    } catch (e) {
      setErr("Impossible de charger vos posts.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function togglePin(id) {
    await api.post(`/posts/${id}/pin/`);
    await load();
  }
  async function remove(id) {
    if (!confirm("Supprimer ce post ?")) return;
    await api.delete(`/posts/${id}/`);
    await load();
  }

  return (
    <div style={{ maxWidth: 1100, margin: "20px auto", padding: 24 }}>
      <h1>Mes posts</h1>
      <div style={{ margin: "12px 0" }}>
        <button onClick={load} disabled={loading}>Rafraîchir</button>
      </div>

      {err && <div style={{ color: "crimson", marginBottom: 12 }}>{err}</div>}
      {loading ? <div>Chargement…</div> : (
        <table width="100%" cellPadding="8" style={{ borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#f5f5f5" }}>
              <th align="left">Titre</th>
              <th align="left">Broadcast</th>
              <th align="left">Dest.</th>
              <th align="left">Épinglé</th>
              <th align="left">Créé le</th>
              <th align="left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {(rows || []).length ? rows.map(p => (
              <tr key={p.id} style={{ borderBottom: "1px solid #eee" }}>
                <td>
                  <div style={{ fontWeight: 600 }}>{p.title || "(sans titre)"}</div>
                  <div style={{ fontSize: 13, opacity: .8, whiteSpace: "pre-wrap" }}>
                    {p.body?.slice(0, 140)}{p.body && p.body.length > 140 ? "…" : ""}
                  </div>
                </td>
                <td>{p.is_broadcast ? "Oui" : "Non"}</td>
                <td>{p.is_broadcast ? "-" : (p.recipients_count ?? 0)}</td>
                <td>{p.is_pinned ? "Oui" : "Non"}</td>
                <td>{new Date(p.created_at).toLocaleString()}</td>
                <td style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <button onClick={() => togglePin(p.id)}>
                    {p.is_pinned ? "Désépingler" : "Épingler"}
                  </button>
                  <button onClick={() => remove(p.id)}>Supprimer</button>
                </td>
              </tr>
            )) : (
              <tr><td colSpan="6">Aucun post.</td></tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
