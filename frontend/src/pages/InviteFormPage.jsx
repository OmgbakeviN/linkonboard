import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function InviteFormPage() {
  const { token } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [invite, setInvite] = useState(null)
  const [error, setError] = useState("")
  const [form, setForm] = useState({ full_name:"", email:"", phone:"", birth_date:"" })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let mounted = true
    async function fetchInvite() {
      try {
        const res = await axios.get(`/api/invites/${token}/`)
        if (!mounted) return
        if (res.data.status === "EXPIRED") {
          setError("Lien expiré.")
        } else {
          setInvite(res.data)
        }
      } catch(e) {
        setError("Lien invalide.")
      } finally {
        setLoading(false)
      }
    }
    fetchInvite()
    return () => { mounted = false }
  }, [token])

  function onChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  async function onSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError("")
    try {
      await axios.post(`/api/invites/${token}/submit/`, form)
      navigate(`/waiting/${token}`)
    } catch(e) {
      setError(e?.response?.data?.detail || "Erreur lors de l’envoi.")
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div style={{ padding:24 }}>Chargement…</div>
  if (error) return <div style={{ padding:24, color:"crimson" }}>{error}</div>

  return (
    <div style={{ maxWidth: 520, margin: "32px auto", padding: 24 }}>
      <h1>Formulaire d’invitation</h1>
      <p>Token: {token}</p>
      <form onSubmit={onSubmit} style={{ display:"grid", gap:12 }}>
        <label>Nom complet
          <input name="full_name" value={form.full_name} onChange={onChange} required />
        </label>
        <label>Email
          <input name="email" type="email" value={form.email} onChange={onChange} required />
        </label>
        <label>Numéro de téléphone
          <input name="phone" value={form.phone} onChange={onChange} required />
        </label>
        <label>Date de naissance
          <input name="birth_date" type="date" value={form.birth_date} onChange={onChange} required />
        </label>
        <button disabled={submitting} type="submit">{submitting ? "Envoi…" : "Envoyer"}</button>
      </form>
      {invite?.target_email ? <p style={{ marginTop:12, fontSize:14 }}>Invité: {invite.target_email}</p> : null}
    </div>
  )
}
