import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function WaitingPage() {
  const { token } = useParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState('PENDING')
  const [error, setError] = useState('')
  const intervalRef = useRef(null)

  useEffect(() => {
    let mounted = true

    async function fetchStatus() {
      try {
        const res = await axios.get(`/api/invites/${token}/`)
        if (!mounted) return
        const s = res.data.status || 'PENDING'
        setStatus(s)
        // Redirections possibles selon le statut (tu pourras adapter)
        if (s === 'APPROVED') {
          // ex: on pourrait aller vers une page "set-password" ou "login"
          // navigate('/login')
        }
        if (s === 'REJECTED') {
          // tu peux envoyer vers une page "refus" ou reproposer le formulaire
          // navigate(`/${token}`)  // si tu autorises une nouvelle soumission
        }
      } catch (e) {
        setError("Impossible de récupérer le statut.")
      }
    }

    // premier fetch immédiat
    fetchStatus()
    // poll toutes 5s
    intervalRef.current = setInterval(fetchStatus, 5000)

    return () => {
      mounted = false
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [token, navigate])

  if (error) return <div style={{ padding:24, color:'crimson' }}>{error}</div>

  const message = {
    PENDING: "Votre demande est en cours de validation. Merci de patienter…",
    APPROVED: "Votre demande a été acceptée. Vous allez recevoir les instructions de connexion.",
    REJECTED: "Votre demande a été refusée. Vous pouvez réessayer ultérieurement.",
    EXPIRED: "Le lien d’invitation a expiré. Merci de contacter le support.",
  }[status] || "Statut inconnu."

  return (
    <div style={{ maxWidth: 620, margin: '40px auto', padding: 24 }}>
      <h1>Statut de votre demande</h1>
      <p><strong>Token :</strong> {token}</p>
      <p><strong>Statut :</strong> {status}</p>
      <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 8 }}>
        {message}
      </div>

      {/* Boutons optionnels selon le statut */}
      {status === 'REJECTED' && (
        <button style={{ marginTop: 16 }} onClick={() => navigate(`/${token}`)}>
          Revenir au formulaire
        </button>
      )}
      {status === 'APPROVED' && (
        <button style={{ marginTop: 16 }} onClick={() => navigate('/login')}>
          Aller à la connexion
        </button>
      )}
    </div>
  )
}
