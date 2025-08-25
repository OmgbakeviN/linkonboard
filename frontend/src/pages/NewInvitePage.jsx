import { useState } from "react";
import api from "../api";

export default function NewInvitePage() {
  const [invite, setInvite] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function createInvite() {
    setLoading(true);
    setErr("");
    setInvite(null);
    try {
      const res = await api.post("/invites/", {}); // pas de payload pour l’instant
      setInvite(res.data);
    } catch (e) {
      setErr("Impossible de générer un lien");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", padding: 24 }}>
      <h1>Nouvelle invitation</h1>
      <button onClick={createInvite} disabled={loading}>
        {loading ? "Création…" : "Générer un lien"}
      </button>

      {err && <div style={{ color: "crimson", marginTop: 16 }}>{err}</div>}

      {invite && (
        <div style={{ marginTop: 24, padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
          <p><strong>Lien généré :</strong></p>
          <input
            type="text"
            value={`${window.location.origin}/${invite.token}`}
            readOnly
            style={{ width: "100%", padding: 8 }}
          />
          <p style={{ fontSize: 14, marginTop: 8 }}>
            Copiez ce lien et envoyez-le à la personne que vous souhaitez inviter.
          </p>
        </div>
      )}
    </div>
  );
}
