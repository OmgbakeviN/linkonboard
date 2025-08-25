import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App.jsx'
import InviteFormPage from './pages/InviteFormPage.jsx'
import WaitingPage from './pages/WaitingPage.jsx'
import ClientDashboard from './pages/ClientDashboard.jsx'
import LoginPage from './pages/LoginPage.jsx'
import MemberWall from './pages/MemberWall.jsx'
import ClientPostForm from './pages/ClientPostForm.jsx'
import NewInvitePage from './pages/NewInvitePage.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/:token', element: <InviteFormPage /> },
  { path: '/waiting/:token', element: <WaitingPage /> },
  { path: '/dashboard', element: <ClientDashboard /> },
  { path: '/login', element: <LoginPage /> },
  { path: "/new-invite", element: <NewInvitePage /> },
  { path: '/wall', element: <MemberWall /> },
  { path: '/post', element: <ClientPostForm /> },
])

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)

// // src/main.jsx
// import ProtectedRoute from "./components/ProtectedRoute.jsx";

// // …
// { path: "/dashboard", element: <ProtectedRoute allow="CLIENT"><ClientDashboard /></ProtectedRoute> },
// { path: "/post", element: <ProtectedRoute allow="CLIENT"><ClientPostForm /></ProtectedRoute> },
// { path: "/new-invite", element: <ProtectedRoute allow="CLIENT"><NewInvitePage /></ProtectedRoute> },
// { path: "/wall", element: <ProtectedRoute allow="MEMBER"><MemberWall /></ProtectedRoute> },
