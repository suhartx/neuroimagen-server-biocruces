import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

function App() {
  const [file, setFile] = useState(null);
  const [subjectId, setSubjectId] = useState('');
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
    const response = await fetch(`${API_BASE}/studies/upload`, { method: 'POST', body: formData });
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

  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">TFM - Neurorrehabilitación</p>
        <h1>Servicio de procesamiento de neuroimagen</h1>
        <p>
          Plataforma para subir imágenes anatómicas T1w anonimizadas, ejecutar procesamiento asíncrono y descargar resultados técnicos.
        </p>
        <div className="notice">
          Los resultados son material de apoyo y requieren revisión clínica por personal cualificado. No introduzcas datos identificativos de pacientes.
        </div>
      </section>

      <section className="card">
        <h2>Subir estudio</h2>
        <p className="hint">
          Se espera una imagen anatómica T1w en formato <strong>.nii.gz</strong>. Indicá un identificador BIDS como <code>sub-O01</code>; si lo dejás vacío, el sistema generará uno seguro y preparará automáticamente la estructura BIDS.
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
          <button disabled={loading}>{loading ? 'Subiendo...' : 'Enviar a procesamiento'}</button>
        </form>
        <p className="hint">El procesamiento puede tardar entre 10 minutos y 1 hora. El worker renderiza outputs NIfTI a PNG con FSL slicer y genera un PDF técnico, no clínico.</p>
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
                <th>Sujeto</th>
                <th>Estado</th>
                <th>Fecha</th>
                <th>Resultados</th>
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
                      <a className="download" href={`${API_BASE}/studies/${study.id}/download/pdf`}>PDF técnico</a>
                    ) : (
                      <span className="muted">PDF no disponible</span>
                    )}
                    {study.has_output_zip && <a className="download secondary-download" href={`${API_BASE}/studies/${study.id}/download/zip`}>ZIP outputs</a>}
                  </td>
                </tr>
              ))}
              {studies.length === 0 && (
                <tr><td colSpan="5" className="muted">Todavía no hay estudios registrados.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
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
