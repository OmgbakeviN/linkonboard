import { useEffect, useState } from "react";
import api from "../api"; // ton axios.create avec header Bearer
import Linkified from "../components/Linkified";

export default function MemberWall() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get("/posts/mine/");
        setItems(res.data || []);
      } catch (e) {
        setErr("Impossible de charger vos messages.");
      }
    }
    load();
  }, []);

  return (
    <div style={{ maxWidth: 800, margin: "20px auto", padding: 24 }}>
      <h1>Mon mur</h1>
      {err && <div style={{ color: "crimson" }}>{err}</div>}
      {!items.length ? <p>Aucun message pour l’instant.</p> : (
        <div style={{ display:"grid", gap:12 }}>
          {items.map(p => (
            <div key={p.id} style={{ padding:12, border:"1px solid #eee", borderRadius:8 }}>
              {p.title && <h3 style={{ margin:"0 0 8px" }}>{p.title}</h3>}
              {p.images_out?.length ? (
                <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginTop:8 }}>
                  {p.images_out.map(img => (
                    <img key={img.id} src={img.image} alt="" style={{ maxWidth:200, borderRadius:8 }} />
                  ))}
                </div>
              ) : null}
              <Linkified text={p.body} />
              <div style={{ fontSize:12, opacity:.7, marginTop:8 }}>
                De: {p.author_name} • {new Date(p.created_at).toLocaleString()}
                {p.is_broadcast ? " • (Annonce à tous)" : ""}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
