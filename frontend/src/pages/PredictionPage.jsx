import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { TrendingUp, AlertCircle, Sliders, Calendar, MapPin, Wheat } from 'lucide-react';

const PredictionPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { t } = useLanguage();

  const [crops, setCrops] = useState([]);
  const [markets, setMarkets] = useState([]);

  const [commodity, setCommodity] = useState(searchParams.get('crop') || 'Tomato');
  const [market, setMarket] = useState(searchParams.get('market') || 'Bengaluru');
  const [horizon, setHorizon] = useState(7);

  // Advanced assumptions
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [farmerUrgency, setFarmerUrgency] = useState('Normal');
  const [hasColdStorage, setHasColdStorage] = useState(false);
  const [customArrivals, setCustomArrivals] = useState('');
  const [customRainfall, setCustomRainfall] = useState('');
  const [customTemp, setCustomTemp] = useState('');
  const [customHumidity, setCustomHumidity] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [cRes, mRes] = await Promise.all([
          api.get('/markets/crops'),
          api.get('/markets/list')
        ]);
        if (cRes.data?.crops) setCrops(cRes.data.crops);
        if (mRes.data?.markets) setMarkets(mRes.data.markets);
      } catch (err) {
        console.error("Metadata fetch error:", err);
      }
    };
    fetchMetadata();
  }, []);

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const assumptions = {
      farmer_urgency: farmerUrgency,
      has_cold_storage: hasColdStorage
    };
    if (customArrivals) assumptions.market_arrivals = parseFloat(customArrivals);
    if (customRainfall) assumptions.rainfall = parseFloat(customRainfall);
    if (customTemp) assumptions.temperature = parseFloat(customTemp);
    if (customHumidity) assumptions.humidity = parseFloat(customHumidity);

    try {
      const res = await api.post('/predictions/predict', {
        commodity,
        market,
        horizon_days: horizon,
        assumptions
      });

      if (res.data?.id) {
        navigate(`/result/${res.data.id}`, { state: { prediction: res.data } });
      }
    } catch (err) {
      console.error("Prediction error:", err);
      setError(err.response?.data?.error || "Price prediction failed. Please verify selected crop and market records.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="content-body" style={{ maxWidth: '900px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <TrendingUp color="#16a34a" size={26} />
          <span>{t('predictPrices')}</span>
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.92rem', marginTop: '4px' }}>
          Generate direct multi-horizon price forecasts (7, 15, or 30 days) and compute SHAP feature contributions for Karnataka APMC mandis.
        </p>
      </div>

      {error && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          background: '#ffe4e6',
          color: '#9f1239',
          padding: '14px 18px',
          borderRadius: '10px',
          marginBottom: '20px',
          fontSize: '0.9rem'
        }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="card">
        <form onSubmit={handlePredict}>
          <div className="grid-2">
            {/* Crop Selector */}
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Wheat size={16} color="#15803d" />
                <span>{t('selectCrop')}</span>
              </label>
              <select
                className="form-select"
                value={commodity}
                onChange={(e) => setCommodity(e.target.value)}
                required
              >
                {crops.length > 0 ? (
                  crops.map((c, i) => (
                    <option key={i} value={c.commodity}>
                      {c.commodity} ({c.category})
                    </option>
                  ))
                ) : (
                  <>
                    <option value="Tomato">Tomato</option>
                    <option value="Onion">Onion</option>
                    <option value="Potato">Potato</option>
                    <option value="Cabbage">Cabbage</option>
                    <option value="Green Chilli">Green Chilli</option>
                    <option value="Rice">Rice</option>
                    <option value="Maize">Maize</option>
                    <option value="Groundnut">Groundnut</option>
                  </>
                )}
              </select>
            </div>

            {/* Market Selector */}
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MapPin size={16} color="#15803d" />
                <span>{t('selectMarket')} (Karnataka APMC)</span>
              </label>
              <select
                className="form-select"
                value={market}
                onChange={(e) => setMarket(e.target.value)}
                required
              >
                {markets.length > 0 ? (
                  markets.map((m, i) => (
                    <option key={i} value={m.market}>
                      {m.market} ({m.district})
                    </option>
                  ))
                ) : (
                  <>
                    <option value="Bengaluru">Bengaluru (Bengaluru Urban)</option>
                    <option value="Mysuru">Mysuru (Mysuru)</option>
                    <option value="Hubballi">Hubballi (Dharwad)</option>
                    <option value="Mandya">Mandya (Mandya)</option>
                  </>
                )}
              </select>
            </div>
          </div>

          {/* Forecast Horizon Selector */}
          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Calendar size={16} color="#15803d" />
              <span>{t('selectHorizon')}</span>
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '14px', marginTop: '6px' }}>
              {[7, 15, 30].map((days) => (
                <button
                  type="button"
                  key={days}
                  onClick={() => setHorizon(days)}
                  style={{
                    padding: '14px',
                    borderRadius: '10px',
                    border: horizon === days ? '2px solid #16a34a' : '1px solid #e2e8f0',
                    background: horizon === days ? '#f0fdf4' : 'white',
                    color: horizon === days ? '#15803d' : '#334155',
                    fontWeight: 700,
                    cursor: 'pointer',
                    fontSize: '1rem',
                    textAlign: 'center',
                    transition: 'all 0.2s'
                  }}
                >
                  <div>{days} {t('days')}</div>
                  <div style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: 500, marginTop: '2px' }}>
                    {days === 7 ? 'Short-term tactical' : days === 15 ? 'Mid-term planning' : 'Monthly projection'}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Toggle Advanced Assumptions */}
          <div style={{ margin: '20px 0 16px 0' }}>
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="btn btn-secondary"
              style={{ padding: '6px 14px', fontSize: '0.82rem', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            >
              <Sliders size={14} />
              <span>{showAdvanced ? 'Hide Advanced Decision Parameters' : 'Customize Farmer Urgency & Condition Assumptions'}</span>
            </button>
          </div>

          {showAdvanced && (
            <div style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '22px'
            }}>
              <h4 style={{ fontSize: '0.92rem', fontWeight: 700, marginBottom: '14px', color: '#334155' }}>
                Decision-Support & Environmental Parameters
              </h4>
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Farmer Selling Urgency</label>
                  <select
                    className="form-select"
                    value={farmerUrgency}
                    onChange={(e) => setFarmerUrgency(e.target.value)}
                  >
                    <option value="Normal">Normal (Can store if profitable)</option>
                    <option value="High">High (Immediate cash required)</option>
                  </select>
                </div>

                <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingTop: '28px' }}>
                  <input
                    type="checkbox"
                    id="cold_storage"
                    checked={hasColdStorage}
                    onChange={(e) => setHasColdStorage(e.target.checked)}
                    style={{ width: '18px', height: '18px', accentColor: '#16a34a' }}
                  />
                  <label htmlFor="cold_storage" style={{ fontSize: '0.88rem', fontWeight: 600, color: '#334155', cursor: 'pointer' }}>
                    Has verified cold storage facility
                  </label>
                </div>

                <div className="form-group">
                  <label className="form-label">Custom Market Arrivals (Quintals, Optional)</label>
                  <input
                    type="number"
                    className="form-input"
                    placeholder="Leave empty to use verified mandi average"
                    value={customArrivals}
                    onChange={(e) => setCustomArrivals(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Ambient Temperature (°C, Optional)</label>
                  <input
                    type="number"
                    className="form-input"
                    placeholder="Leave empty to use historical average"
                    value={customTemp}
                    onChange={(e) => setCustomTemp(e.target.value)}
                  />
                </div>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', padding: '14px', fontSize: '1rem', marginTop: '10px' }}
          >
            {loading ? (
              <span>{t('predicting')}</span>
            ) : (
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TrendingUp size={20} />
                {t('predictButton')}
              </span>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PredictionPage;
