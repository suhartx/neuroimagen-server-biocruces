import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

function App() {
  const [file, setFile] = useState(null);
  const [studies, setStudies] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  async function loadStudies() {
    const response = await fetch(`${API_BASE}/studies`);
    if (response.ok) {
      setStudies(await response.json());
    }
  }

  useEffect(() => {
    loadStudies();
    const timer = window.setInterval(loadStudies, 5000);
    return () => window.clearInterval(timer);
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setMessage('Seleccioná un fichero antes de enviar.');
      return;
    }
    setLoading(true);
    setMessage('Subiendo estudio...');
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE}/studies/upload`, { method: 'POST', body: formData });
    const payload = await response.json().catch(() => ({}));
    setLoading(false);
    if (!response.ok) {
      setMessage(payload.detail || 'No se pudo subir el estudio.');
      return;
    }
    setFile(null);
    setMessage(payload.message || 'Estudio encolado.');
    await loadStudies();
  }

  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">TFM - Neurorrehabilitación</p>
        <h1>Servicio de procesamiento de neuroimagen</h1>
        <p>
          Plataforma para subir estudios anonimizados, ejecutar procesamiento asíncrono y descargar el informe PDF generado.
        </p>
        <div className="notice">
          Los resultados son material de apoyo y requieren revisión clínica por personal cualificado. No introduzcas datos identificativos de pacientes.
        </div>
      </section>

      <section className="card">
        <h2>Subir estudio</h2>
        <form onSubmit={handleSubmit}>
          <input type="file" onChange={(event) => setFile(event.target.files?.[0] || null)} />
          <button disabled={loading}>{loading ? 'Subiendo...' : 'Enviar a procesamiento'}</button>
        </form>
        {message && <p className="message">{message}</p>}
      </section>

      <section className="card">
        <div className="section-title">
          <h2>Estudios registrados</h2>
          <button className="secondary" onClick={loadStudies}>Actualizar</button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Fichero</th>
                <th>Estado</th>
                <th>Fecha</th>
                <th>Informe</th>
              </tr>
            </thead>
            <tbody>
              {studies.map((study) => (
                <tr key={study.id}>
                  <td>{study.original_filename}</td>
                  <td><Status value={study.status} error={study.error_message} /></td>
                  <td>{new Date(study.created_at).toLocaleString('es-ES')}</td>
                  <td>
                    {study.has_pdf ? (
                      <a className="download" href={`${API_BASE}/studies/${study.id}/download`}>Descargar PDF</a>
                    ) : (
                      <span className="muted">No disponible</span>
                    )}
                  </td>
                </tr>
              ))}
              {studies.length === 0 && (
                <tr><td colSpan="4" className="muted">Todavía no hay estudios registrados.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

function Status({ value, error }) {
  const labels = {
    uploaded: 'Subido',
    queued: 'En cola',
    processing: 'Procesando',
    completed: 'Completado',
    failed: 'Fallido',
  };
  return (
    <span className={`status ${value}`} title={error || ''}>
      {labels[value] || value}{error ? `: ${error}` : ''}
    </span>
  );
}

createRoot(document.getElementById('root')).render(<App />);
