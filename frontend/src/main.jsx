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
  const [adminDashboard, setAdminDashboard] = useState(null);
  const [selectedDetail, setSelectedDetail] = useState(null);
  const [selectedLogs, setSelectedLogs] = useState(null);
  const [shareStudy, setShareStudy] = useState(null);
  const [shareLinks, setShareLinks] = useState([]);
  const [generatedShareUrl, setGeneratedShareUrl] = useState('');
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

  async function loadAdminDashboard() {
    if (!token || user?.role !== 'admin') return;
    const response = await authFetch(`${API_BASE}/admin/dashboard`);
    if (response.ok) {
      setAdminDashboard(await response.json());
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
    loadAdminDashboard();
  }, [user, token]);

  useEffect(() => {
    if (!token || user?.role !== 'admin') return undefined;
    const timer = window.setInterval(loadAdminDashboard, 10000);
    return () => window.clearInterval(timer);
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
    setAdminDashboard(null);
    setShareStudy(null);
    setShareLinks([]);
    setGeneratedShareUrl('');
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
    await loadAdminDashboard();
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
    await loadAdminDashboard();
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

  async function openSharePanel(study) {
    setGeneratedShareUrl('');
    setShareStudy(study);
    const response = await authFetch(`${API_BASE}/studies/${study.id}/share-links`);
    const payload = await response.json().catch(() => ([]));
    if (!response.ok) {
      setMessage(payload.detail || 'No se pudieron cargar los links compartidos.');
      return;
    }
    setShareLinks(payload);
  }

  async function createShareLink() {
    if (!shareStudy) return;
    const response = await authFetch(`${API_BASE}/studies/${shareStudy.id}/share-links`, { method: 'POST' });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      setMessage(payload.detail || 'No se pudo crear el link compartido.');
      return;
    }
    setGeneratedShareUrl(payload.url);
    setShareLinks([payload, ...shareLinks]);
    setMessage('Link temporal creado. Copialo y compartilo solo con destinatarios autorizados.');
  }

  async function revokeShareLink(link) {
    if (!shareStudy) return;
    if (!window.confirm('¿Seguro que querés revocar este link?')) return;
    const response = await authFetch(`${API_BASE}/studies/${shareStudy.id}/share-links/${link.id}/revoke`, { method: 'POST' });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      setMessage(payload.detail || 'No se pudo revocar el link.');
      return;
    }
    setShareLinks(shareLinks.map((item) => (item.id === payload.id ? payload : item)));
    setMessage('Link revocado.');
  }

  async function copyShareUrl() {
    if (!generatedShareUrl) return;
    try {
      await navigator.clipboard.writeText(generatedShareUrl);
      setMessage('Link copiado al portapapeles.');
    } catch {
      const input = document.querySelector('.share-url input');
      input?.focus();
      input?.select();
      if (document.execCommand?.('copy')) {
        setMessage('Link copiado al portapapeles.');
        return;
      }
      setMessage('No se pudo copiar automáticamente; el link quedó seleccionado. Usá Ctrl+C.');
    }
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
    setShareStudy(null);
    setShareLinks([]);
    setGeneratedShareUrl('');
    await loadStudies();
    await loadAdminDashboard();
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

          {user.role === 'admin' && adminDashboard && (
            <section className="card admin-dashboard">
              <div className="section-title">
                <div>
                  <p className="eyebrow dark">Panel operativo</p>
                  <h2>Dashboard de administración</h2>
                </div>
                <button className="secondary" onClick={loadAdminDashboard}>Actualizar dashboard</button>
              </div>

              <div className="metric-grid">
                <MetricCard label="En cola" value={adminDashboard.queue.queued} />
                <MetricCard label="Procesando" value={adminDashboard.queue.processing} />
                <MetricCard label="Fallidos" value={adminDashboard.queue.failed} tone={adminDashboard.queue.failed ? 'danger' : ''} />
                <MetricCard label="Usuarios activos" value={`${adminDashboard.users.active}/${adminDashboard.users.total}`} />
                <MetricCard label="Estudios" value={sumValues(adminDashboard.studies_by_status)} />
                <MetricCard label="Subidas registradas" value={formatBytes(adminDashboard.storage.studies_bytes)} />
              </div>

              <div className="dashboard-columns">
                <div>
                  <h3>Servicios</h3>
                  <div className="service-list">
                    {adminDashboard.services.map((service) => (
                      <ServiceStatus key={service.name} service={service} />
                    ))}
                  </div>
                </div>
                <div>
                  <h3>Alertas básicas</h3>
                  {adminDashboard.alerts.length === 0 ? (
                    <p className="muted">Sin alertas operativas.</p>
                  ) : (
                    <ul className="alert-list">
                      {adminDashboard.alerts.map((alert) => <li key={alert}>{alert}</li>)}
                    </ul>
                  )}
                </div>
              </div>

              <div className="dashboard-columns">
                <div>
                  <h3>Estudios por estado</h3>
                  <StatusBreakdown values={adminDashboard.studies_by_status} />
                </div>
                <div>
                  <h3>Jobs por estado</h3>
                  <StatusBreakdown values={adminDashboard.jobs_by_status} />
                </div>
              </div>

              <p className="hint">
                Última actualización: {new Date(adminDashboard.generated_at).toLocaleString('es-ES')}. Disco libre: {formatBytes(adminDashboard.storage.disk_free_bytes)}.
              </p>
            </section>
          )}

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
                        {study.has_pdf && study.status === 'completed' && <button className="secondary compact" onClick={() => openSharePanel(study)}>Compartir</button>}
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

          {shareStudy && (
            <section className="card detail-card">
              <div className="section-title">
                <div>
                  <h2>Compartir informe</h2>
                  <p className="hint">Crea un link temporal para descargar solo el PDF técnico de <strong>{shareStudy.original_filename}</strong>.</p>
                </div>
                <button className="secondary" onClick={() => setShareStudy(null)}>Cerrar</button>
              </div>
              <div className="share-actions">
                <button onClick={createShareLink}>Crear link temporal</button>
                {generatedShareUrl && (
                  <div className="share-url">
                    <input type="url" value={generatedShareUrl} readOnly onFocus={(event) => event.target.select()} />
                    <button className="secondary" onClick={copyShareUrl}>Copiar</button>
                  </div>
                )}
              </div>
              <div className="table-wrap small-table">
                <table>
                  <thead>
                    <tr>
                      <th>Creado</th>
                      <th>Caduca</th>
                      <th>Accesos</th>
                      <th>Estado</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {shareLinks.map((link) => (
                      <tr key={link.id}>
                        <td>{formatDate(link.created_at)}</td>
                        <td>{formatDate(link.expires_at)}</td>
                        <td>{link.access_count}</td>
                        <td>{shareLinkStatus(link)}</td>
                        <td>
                          {!link.is_revoked && !link.is_expired ? (
                            <button className="danger compact" onClick={() => revokeShareLink(link)}>Revocar</button>
                          ) : (
                            <span className="muted">Sin acciones</span>
                          )}
                        </td>
                      </tr>
                    ))}
                    {shareLinks.length === 0 && (
                      <tr><td colSpan="5" className="muted">No hay links compartidos para este estudio.</td></tr>
                    )}
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
    canceled: 'Cancelado',
  };
  return (
    <span className={`status ${value}`} title={error || warnings || ''}>
      {labels[value] || value}{error ? `: ${error}` : ''}{!error && warnings ? ' con avisos' : ''}
    </span>
  );
}

function MetricCard({ label, value, tone = '' }) {
  return (
    <article className={`metric-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function ServiceStatus({ service }) {
  const label = service.status === 'ok' ? 'Operativo' : service.status === 'warning' ? 'Aviso' : service.status === 'unknown' ? 'No verificable' : 'Caído';
  return (
    <div className="service-item">
      <span className={`service-dot ${service.status}`} />
      <div>
        <strong>{service.name}</strong>
        <p>{label}{service.detail ? `: ${service.detail}` : ''}</p>
      </div>
    </div>
  );
}

function StatusBreakdown({ values }) {
  const entries = Object.entries(values || {});
  if (entries.length === 0) return <p className="muted">Sin datos todavía.</p>;
  return (
    <div className="breakdown-list">
      {entries.map(([status, count]) => (
        <div key={status}>
          <Status value={status} />
          <strong>{count}</strong>
        </div>
      ))}
    </div>
  );
}

function sumValues(values) {
  return Object.values(values || {}).reduce((total, value) => total + value, 0);
}

function formatBytes(bytes) {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let value = bytes;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }
  return `${value.toFixed(value >= 10 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('es-ES') : 'No informado';
}

function shareLinkStatus(link) {
  if (link.is_revoked) return 'Revocado';
  if (link.is_expired) return 'Caducado';
  return 'Activo';
}

createRoot(document.getElementById('root')).render(<App />);
