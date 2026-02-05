import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [formData, setFormData] = useState({
    anio: '',
    mes: '',
    turismo_alto: false,
    temperatura_media: '',
    viento_media: ''
  })

  const meses = [
    { value: 1, label: 'Enero' },
    { value: 2, label: 'Febrero' },
    { value: 3, label: 'Marzo' },
    { value: 4, label: 'Abril' },
    { value: 5, label: 'Mayo' },
    { value: 6, label: 'Junio' },
    { value: 7, label: 'Julio' },
    { value: 8, label: 'Agosto' },
    { value: 9, label: 'Septiembre' },
    { value: 10, label: 'Octubre' },
    { value: 11, label: 'Noviembre' },
    { value: 12, label: 'Diciembre' }
  ]

  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setPrediction(null)

    try {
      const response = await axios.post('https://proyecto-ml-x9fc.onrender.com/predict', {
        anio: parseInt(formData.anio),
        mes: parseInt(formData.mes),
        turismo_alto: formData.turismo_alto ? 1 : 0,
        temperatura_media: parseFloat(formData.temperatura_media),
        viento_media: parseFloat(formData.viento_media)
      }, {
        timeout: 20000 // 20 segundos de timeout
      })

      setPrediction(response.data.prediction)
    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError('La llamada tardó demasiado tiempo. Inténtalo de nuevo.')
      } else {
        setError('Error al realizar la predicción: ' + (err.response?.data?.detail || err.message))
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <h1>Predicción de Consumo de Energía</h1>
          <p>Introduce los datos para obtener una estimación del consumo</p>
        </div>

        <form onSubmit={handleSubmit} className="prediction-form">
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="anio">Año</label>
              <input
                type="number"
                id="anio"
                name="anio"
                value={formData.anio}
                onChange={handleChange}
                required
                min="2000"
                max="2100"
                placeholder="Ej: 2024"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="mes">Mes</label>
              <select
                id="mes"
                name="mes"
                value={formData.mes}
                onChange={handleChange}
                required
                className="form-input"
              >
                <option value="">Selecciona un mes</option>
                {meses.map(mes => (
                  <option key={mes.value} value={mes.value}>
                    {mes.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="temperatura_media">Temperatura (°C)</label>
              <input
                type="number"
                id="temperatura_media"
                name="temperatura_media"
                value={formData.temperatura_media}
                onChange={handleChange}
                required
                step="0.1"
                placeholder="Ej: 25.5"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="viento_media">Viento (km/h)</label>
              <input
                type="number"
                id="viento_media"
                name="viento_media"
                value={formData.viento_media}
                onChange={handleChange}
                required
                step="0.1"
                min="0"
                placeholder="Ej: 15.2"
                className="form-input"
              />
            </div>
          </div>

          <div className="checkbox-group">
            <label htmlFor="turismo_alto" className="checkbox-label">
              <input
                type="checkbox"
                id="turismo_alto"
                name="turismo_alto"
                checked={formData.turismo_alto}
                onChange={handleChange}
                className="checkbox-input"
              />
              <span className="checkbox-custom"></span>
              Temporada alta de turismo
            </label>
          </div>

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? (
              <>
                <span className="spinner"></span>
                Calculando...
              </>
            ) : (
              'Calcular Consumo'
            )}
          </button>
        </form>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {prediction !== null && (
          <div className="prediction-result">
            <h2>Resultado del Cálculo</h2>
            <div className="prediction-value">
              <span className="prediction-text">
                En el año {formData.anio} en {meses.find(m => m.value === parseInt(formData.mes))?.label || formData.mes} se consumirán {prediction.toFixed(2)} Gwh
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
