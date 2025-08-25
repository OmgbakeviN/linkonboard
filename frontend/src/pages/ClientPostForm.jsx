import { useEffect, useState } from "react";
import api from "../api";

export default function ClientPostForm() {
  const [members, setMembers] = useState([]);
  const [checked, setChecked] = useState([]); // ids
  const [form, setForm] = useState({ title: "", body: "", is_broadcast: false });
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [files, setFiles] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get("/members/");
        setMembers(res.data || []);
      } catch (e) {
        setErr("Impossible de récupérer la liste des membres.");
      }
    }
    load();
  }, []);

  function toggle(id) {
    setChecked(prev => prev.includes(id) ? prev.filter(x => x!==id) : [...prev, id]);
  }

  async function onSubmit(e) {
    e.preventDefault();
    setMsg(""); setErr("");
    try {
      const fd = new FormData();
      fd.append("title", form.title);
      fd.append("body", form.body);
      fd.append("is_broadcast", String(form.is_broadcast));
      if (!form.is_broadcast) checked.forEach(id => fd.append("recipient_ids", id));
      files.forEach(f => fd.append("images", f));
      await api.post("/posts/", fd, { headers: { "Content-Type":"multipart/form-data" } });
      setMsg("Message publié !");
      setForm({ title:"", body:"", is_broadcast:false });
      setChecked([]); setFiles([]);
    } catch (e) { setErr(e?.response?.data?.detail || "Échec de la publication."); }
  }

  return (
    <div style={{ maxWidth: 900, margin: "20px auto", padding: 24 }}>
      <h1>Publier un message</h1>

      <form onSubmit={onSubmit} style={{ display:"grid", gap:12, marginBottom:16 }}>
        <input type="file" multiple accept="image/*" onChange={(e)=>setFiles(Array.from(e.target.files))} />
        <input placeholder="Titre (facultatif)" value={form.title} onChange={e=>setForm({...form, title:e.target.value})} />
        <textarea placeholder="Contenu…" rows={6} value={form.body} onChange={e=>setForm({...form, body:e.target.value})} required />
        <label style={{ display:"flex", alignItems:"center", gap:8 }}>
          <input type="checkbox" checked={form.is_broadcast} onChange={e=>setForm({...form, is_broadcast:e.target.checked})} />
          Envoyer à tous les membres (broadcast)
        </label>

        {!form.is_broadcast && (
          <div style={{ border:"1px solid #eee", borderRadius:8, padding:12 }}>
            <strong>Choisir les murs ciblés :</strong>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(240px, 1fr))", gap:8, marginTop:8 }}>
              {members.map(m => (
                <label key={m.id} style={{ display:"flex", gap:8 }}>
                  <input type="checkbox" checked={checked.includes(m.id)} onChange={()=>toggle(m.id)} />
                  <span>{m.username} — {m.email}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        <button type="submit">Publier</button>
      </form>

      {msg && <div style={{ color:"green" }}>{msg}</div>}
      {err && <div style={{ color:"crimson" }}>{err}</div>}
    </div>
  );
}
