import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';
const TOKEN_KEY = 'neuroimagen_access_token';

function App() {
  const [token, setToken] = useState(() => window.localStorage.getItem(TOKEN_KEY) || '');
  const [user, setUser] = useState(null);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [file, setFile] = useState(null);
  const [subjectId, setSubjectId] = useState('');
  const [studies, setStudies] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedDetail, setSelectedDetail] = useState(null);
  const [selectedLogs, setSelectedLogs] = useState(null);
  const [newUser, setNewUser] = useState({ email: '', full_name: '', password: '', role: 'researcher' });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  async function authFetch(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: { ...authHeaders, ...(options.headers || {}) },
    });
    if (response.status === 401) {
      handleLocalLogout();
      setMessage('La sesión expiró. Volvé a iniciar sesión.');
    }
    return response;
  }

  async function loadCurrentUser() {
    if (!token) return;
    const response = await authFetch(`${API_BASE}/auth/me`);
    if (!response.ok) {
      return;
    }
    setUser(await response.json());
  }

  async function loadStudies() {
    if (!token) return;
    const response = await authFetch(`${API_BASE}/studies`);
    if (response.ok) {
      setStudies(await response.json());
    }
  }

  async function loadUsers() {
    if (!token || user?.role !== 'admin') return;
    const response = await authFetch(`${API_BASE}/users`);
    if (response.ok) {
      setUsers(await response.json());
    }
  }

  useEffect(() => {
    if (!token) return undefined;
    loadCurrentUser();
    loadStudies();
    const timer = window.setInterval(loadStudies, 5000);
    return () => window.clearInterval(timer);
  }, [token]);

  useEffect(() => {
    loadUsers();
  }, [user, token]);

  async function handleLogin(event) {
    event.preventDefault();
    setLoading(true);
    setMessage('Iniciando sesión...');
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: loginEmail, password: loginPassword }),
    });
    const payload = await response.json().catch(() => ({}));
    setLoading(false);
    if (!response.ok) {
      setMessage(payload.detail || 'No se pudo iniciar sesión.');
      return;
    }
    window.localStorage.setItem(TOKEN_KEY, payload.access_token);
    setToken(payload.access_token);
    setUser(payload.user);
    setLoginPassword('');
    setMessage('Sesión iniciada.');
  }

  async function handleLogout() {
    if (token) {
      await authFetch(`${API_BASE}/auth/logout`, { method: 'POST' }).catch(() => null);
    }
    handleLocalLogout();
  }

  function handleLocalLogout() {
    window.localStorage.removeItem(TOKEN_KEY);
    setToken('');
    setUser(null);
    setStudies([]);
    setUsers([]);
    setMessage('');
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setMessage('Selecciona un fichero antes de enviar.');
      return;
    }
    const normalizedSubject = subjectId.trim();
    if (normalizedSubject && !/^sub-[A-Za-z0-9]+$/.test(normalizedSubject)) {
      setMessage('El identificador BIDS debe tener formato sub-XXXX, por ejemplo sub-O01.');
      return;
    }
    setLoading(true);
    setMessage('Subiendo estudio...');
    const formData = new FormData();
    formData.append('file', file);
    if (normalizedSubject) {
      formData.append('bids_subject_id', normalizedSubject);
    }
    const response = await authFetch(`${API_BASE}/studies/upload`, { method: 'POST', body: formData });
    const payload = await response.json().catch(() => ({}));
    setLoading(false);
    if (!response.ok) {
      setMessage(payload.detail || 'No se pudo subir el estudio.');
      return;
    }
    setFile(null);
    setSubjectId('');
    setMessage(payload.message || 'Estudio encolado.');
    await loadStudies();
  }

  async function handleCreateUser(event) {
    event.preventDefault();
    setLoading(true);
    setMessage('Creando usuario...');
    const response = await authFetch(`${API_BASE}/users`, {
      method: 'POST',
      headers: { ...authHeaders, 'Content-Type': 'application/json' },
      body: JSON.stringify(newUser),
    });
    const payload = await response.json().catch(() => ({}));
    setLoading(false);
    if (!response.ok) {
      setMessage(payload.detail || 'No se pudo crear el usuario.');
      return;
    }
    setNewUser({ email: '', full_name: '', password: '', role: 'researcher' });
    setMessage(`Usuario creado: ${payload.email}`);
    await loadUsers();
  }

  async function downloadArtifact(study, type) {
    const response = await authFetch(`${API_BASE}/studies/${study.id}/download/${type}`);
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      setMessage(payload.detail || 'No se pudo descargar el resultado.');
      return;
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = type === 'pdf' ? `informe-tecnico-${study.id}.pdf` : `outputs-${study.id}.zip`;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  async function loadStudyDetail(study) {
    const response = await authFetch(`${API_BASE}/studies/${study.id}/detail`);
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      setMessage(payload.detail || 'No se pudo cargar el detalle.');
      return;
    }
    setSelectedDetail(payload);
    setSelectedLogs(null);
  }

  async function loadStudyLogs(study) {
    const response = await authFetch(`${API_BASE}/studies/${study.id}/logs?lines=200`);
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      setMessage(payload.detail || 'No se pudieron cargar los logs.');
      return;
    }
    setSelectedLogs(payload);
    setSelectedDetail(null);
  }

  async function runStudyAction(study, action) {
    const labels = {
      cancel: 'cancelar este job en cola',
      retry: 'reintentar este estudio',
      delete: 'borrar este estudio y sus ficheros',
    };
    if (!window.confirm(`¿Seguro que querés ${labels[action]}?`)) return;
    const response = await authFetch(`${API_BASE}/studies/${study.id}${action === 'delete' ? '' : `/${action}`}`, {
      method: action === 'delete' ? 'DELETE' : 'POST',
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      setMessage(payload.detail || 'No se pudo completar la operación.');
      return;
    }
    setMessage(payload.message || 'Operación completada.');
    setSelectedDetail(null);
    setSelectedLogs(null);
    await loadStudies();
  }

  return (
    <main className="page">
      <section className="hero">
        <div className="topbar">
          <p className="eyebrow">TFM - Neurorrehabilitación</p>
          {user && (
            <button className="secondary light" onClick={handleLogout}>Cerrar sesión</button>
          )}
        </div>
        <h1>Servicio de procesamiento de neuroimagen</h1>
        <p>
          Plataforma para subir imágenes anatómicas T1w anonimizadas, ejecutar procesamiento asíncrono y descargar resultados técnicos.
        </p>
        {user ? (
          <div className="notice">Sesión activa: {user.full_name} ({user.role === 'admin' ? 'admin' : 'researcher'}).</div>
        ) : (
          <div className="notice">Inicia sesión con tu cuenta institucional o de proyecto para acceder a tus estudios.</div>
        )}
      </section>

      {!user ? (
        <section className="card auth-card">
          <h2>Login</h2>
          <form onSubmit={handleLogin}>
            <input type="email" value={loginEmail} onChange={(event) => setLoginEmail(event.target.value)} placeholder="email@institucion.org" required />
            <input type="password" value={loginPassword} onChange={(event) => setLoginPassword(event.target.value)} placeholder="Contraseña" required />
            <button disabled={loading}>{loading ? 'Entrando...' : 'Entrar'}</button>
          </form>
          <p className="hint">Los usuarios se crean desde administración. No hay registro público abierto.</p>
          {message && <p className="message">{message}</p>}
        </section>
      ) : (
        <>
          <section className="card">
            <h2>Subir estudio</h2>
            <p className="hint">
              Se espera una imagen anatómica T1w en formato <strong>.nii.gz</strong>. Indica un identificador BIDS como <code>sub-O01</code>; si lo dejas vacío, el sistema generará uno seguro.
            </p>
            <form onSubmit={handleSubmit}>
              <input type="file" accept=".nii.gz" onChange={(event) => setFile(event.target.files?.[0] || null)} />
              <input
                type="text"
                value={subjectId}
                onChange={(event) => setSubjectId(event.target.value)}
                placeholder="sub-O01"
                aria-label="Identificador de sujeto BIDS"
              />
              <button disabled={loading}>{loading ? 'Trabajando...' : 'Enviar a procesamiento'}</button>
            </form>
            <p className="hint">El procesamiento puede tardar entre 10 minutos y 1 hora.</p>
            {message && <p className="message">{message}</p>}
          </section>

          <section className="card">
            <div className="section-title">
              <h2>{user.role === 'admin' ? 'Estudios registrados' : 'Mis estudios'}</h2>
              <button className="secondary" onClick={loadStudies}>Actualizar</button>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Fichero</th>
                    <th>Sujeto</th>
                    <th>Estado</th>
                    <th>Fecha</th>
                    <th>Resultados</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {studies.map((study) => (
                    <tr key={study.id}>
                      <td>{study.original_filename}</td>
                      <td>{study.bids_subject_id || <span className="muted">No aplica</span>}</td>
                      <td><Status value={study.status} error={study.error_message} warnings={study.processing_warnings} /></td>
                      <td>{new Date(study.created_at).toLocaleString('es-ES')}</td>
                      <td>
                        {study.has_pdf ? (
                          <button className="download" onClick={() => downloadArtifact(study, 'pdf')}>PDF</button>
                        ) : (
                          <span className="muted">PDF no disponible</span>
                        )}
                        {study.has_output_zip && <button className="download secondary-download" onClick={() => downloadArtifact(study, 'zip')}>ZIP outputs</button>}
                      </td>
                      <td className="actions-cell">
                        <button className="secondary compact" onClick={() => loadStudyDetail(study)}>Detalle</button>
                        <button className="secondary compact" onClick={() => loadStudyLogs(study)}>Logs</button>
                        {study.status === 'queued' && <button className="secondary compact" onClick={() => runStudyAction(study, 'cancel')}>Cancelar</button>}
                        {study.status === 'failed' && <button className="secondary compact" onClick={() => runStudyAction(study, 'retry')}>Reintentar</button>}
                        {study.status !== 'processing' && <button className="danger compact" onClick={() => runStudyAction(study, 'delete')}>Borrar</button>}
                      </td>
                    </tr>
                  ))}
                  {studies.length === 0 && (
                    <tr><td colSpan="6" className="muted">Todavía no hay estudios registrados.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {selectedDetail && (
            <section className="card detail-card">
              <div className="section-title">
                <h2>Detalle de estudio</h2>
                <button className="secondary" onClick={() => setSelectedDetail(null)}>Cerrar</button>
              </div>
              <dl className="detail-grid">
                <dt>ID</dt><dd>{selectedDetail.id}</dd>
                <dt>Fichero</dt><dd>{selectedDetail.original_filename}</dd>
                <dt>Estado</dt><dd><Status value={selectedDetail.status} error={selectedDetail.error_message} warnings={selectedDetail.processing_warnings} /></dd>
                <dt>Sujeto</dt><dd>{selectedDetail.bids_subject_id || 'No aplica'}</dd>
                <dt>Pipeline</dt><dd>{selectedDetail.processor_backend || 'No informado'}</dd>
                <dt>Checksum</dt><dd>{selectedDetail.checksum || 'No informado'}</dd>
              </dl>
              <h3>Jobs</h3>
              <div className="table-wrap small-table">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Estado</th>
                      <th>Intento</th>
                      <th>Worker</th>
                      <th>Inicio</th>
                      <th>Fin</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedDetail.jobs.map((job) => (
                      <tr key={job.id}>
                        <td><code>{job.id.slice(0, 8)}</code></td>
                        <td>{job.status}</td>
                        <td>{job.retry_count}</td>
                        <td>{job.worker_name || <span className="muted">No asignado</span>}</td>
                        <td>{job.started_at ? new Date(job.started_at).toLocaleString('es-ES') : <span className="muted">Pendiente</span>}</td>
                        <td>{job.finished_at ? new Date(job.finished_at).toLocaleString('es-ES') : <span className="muted">Pendiente</span>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {selectedLogs && (
            <section className="card detail-card">
              <div className="section-title">
                <h2>Logs del estudio</h2>
                <button className="secondary" onClick={() => setSelectedLogs(null)}>Cerrar</button>
              </div>
              {selectedLogs.logs.length === 0 && <p className="muted">No hay logs disponibles todavía.</p>}
              {selectedLogs.logs.map((log) => (
                <article key={log.name} className="log-block">
                  <h3>{log.name}{log.truncated ? ' (truncado)' : ''}</h3>
                  <pre>{log.content || 'Log vacío'}</pre>
                </article>
              ))}
            </section>
          )}

          {user.role === 'admin' && (
            <section className="card">
              <div className="section-title">
                <h2>Gestión básica de usuarios</h2>
                <button className="secondary" onClick={loadUsers}>Actualizar usuarios</button>
              </div>
              <form onSubmit={handleCreateUser}>
                <input type="email" value={newUser.email} onChange={(event) => setNewUser({ ...newUser, email: event.target.value })} placeholder="email@institucion.org" required />
                <input type="text" value={newUser.full_name} onChange={(event) => setNewUser({ ...newUser, full_name: event.target.value })} placeholder="Nombre completo" required />
                <input type="password" value={newUser.password} onChange={(event) => setNewUser({ ...newUser, password: event.target.value })} placeholder="Contraseña inicial" required />
                <select value={newUser.role} onChange={(event) => setNewUser({ ...newUser, role: event.target.value })}>
                  <option value="researcher">researcher</option>
                  <option value="admin">admin</option>
                </select>
                <button disabled={loading}>Crear usuario</button>
              </form>
              <div className="table-wrap small-table">
                <table>
                  <thead>
                    <tr>
                      <th>Email</th>
                      <th>Nombre</th>
                      <th>Rol</th>
                      <th>Activo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((item) => (
                      <tr key={item.id}>
                        <td>{item.email}</td>
                        <td>{item.full_name}</td>
                        <td>{item.role}</td>
                        <td>{item.is_active ? 'Sí' : 'No'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}
    </main>
  );
}

function Status({ value, error, warnings }) {
  const labels = {
    uploaded: 'Subido',
    queued: 'En cola',
    processing: 'Procesando',
    completed: 'Completado',
    failed: 'Fallido',
  };
  return (
    <span className={`status ${value}`} title={error || warnings || ''}>
      {labels[value] || value}{error ? `: ${error}` : ''}{!error && warnings ? ' con avisos' : ''}
    </span>
  );
}

createRoot(document.getElementById('root')).render(<App />);
