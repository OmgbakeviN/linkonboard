import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App.jsx'
import InviteFormPage from './pages/InviteFormPage.jsx'
import WaitingPage from './pages/WaitingPage.jsx'
const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/:token', element: <InviteFormPage /> },
  { path: '/waiting/:token', element: <WaitingPage /> },
])

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
