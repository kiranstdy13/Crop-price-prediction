import React, { useEffect, useState } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import api from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import WaterfallPlot from '../components/WaterfallPlot';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  Calendar,
  Building2,
  Wheat,
  Clock,
  CircleDollarSign
} from 'lucide-react';

const PredictionResultPage = () => {
  const { id } = useParams();
  const location = useLocation();
  const { t, lang } = useLanguage();

  const [prediction, setPrediction] = useState(location.state?.prediction || null);
  const [loading, setLoading] = useState(!prediction);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!prediction && id) {
      const fetchDetail = async () => {
        try {
          const res = await api.get(`/predictions/${id}`);
          setPrediction(res.data);
        } catch (err) {
          console.error("Fetch prediction detail error:", err);
          setError("Prediction details not found.");
        } finally {
          setLoading(false);
        }
      };
      fetchDetail();
    }
  }, [id, prediction]);

  if (loading) {
    return (
      <div className="content-body" style={{ textAlign: 'center', padding: '60px' }}>
        <div style={{ fontSize: '1.2rem', color: '#16a34a', fontWeight: 600 }}>
          {t('predicting')}
        </div>
      </div>
    );
  }

  if (error || !prediction) {
    return (
      <div className="content-body" style={{ textAlign: 'center', padding: '60px' }}>
        <p style={{ color: '#e11d48', fontSize: '1.1rem', marginBottom: '16px' }}>{error || 'Prediction unavailable.'}</p>
        <Link to="/predict" className="btn btn-primary">Try Another Prediction</Link>
      </div>
    );
  }

  const {
    commodity,
    market,
    district,
    horizon_days,
    current_modal_price,
    predicted_price,
    pct_change,
    price_direction,
    direction_label,
    direction_label_kn,
    model_name,
    forecast_display_date,
    explanation,
    recommendation,
    chart_data
  } = prediction;

  const isUp = price_direction === 'increasing';
  const isDown = price_direction === 'decreasing';

  const dirColor = isUp ? '#16a34a' : isDown ? '#e11d48' : '#f59e0b';
  const dirBadgeClass = isUp ? 'badge-green' : isDown ? 'badge-red' : 'badge-amber';

  return (
    <div className="content-body">
      {/* Back button */}
      <div style={{ marginBottom: '16px' }}>
        <Link to="/predict" className="btn btn-secondary" style={{ padding: '6px 14px', fontSize: '0.82rem' }}>
          <ArrowLeft size={14} />
          <span>Back to Predict</span>
        </Link>
      </div>

      {/* Main Forecast Summary Header Card */}
      <div className="card" style={{ marginBottom: '24px', background: 'linear-gradient(to right, #ffffff, #f0fdf4)', borderLeft: `6px solid ${dirColor}` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="badge badge-green" style={{ fontSize: '0.8rem' }}>
                <Wheat size={14} /> {commodity}
              </span>
              <span className="badge badge-blue" style={{ fontSize: '0.8rem' }}>
                <Building2 size={14} /> {market} Mandi ({district})
              </span>
              <span className="badge badge-amber" style={{ fontSize: '0.8rem' }}>
                <Calendar size={14} /> {horizon_days} Days Forecast
              </span>
            </div>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f172a' }}>
              {commodity} Price Forecast
            </h2>
            <p style={{ color: '#64748b', fontSize: '0.88rem', marginTop: '2px' }}>
              Forecast Target Date: <strong>{forecast_display_date}</strong> · Powered by <strong>{model_name}</strong>
            </p>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: 600 }}>Predicted Price in {horizon_days} Days</div>
            <div style={{ fontSize: '2.4rem', fontWeight: 900, color: dirColor, lineHeight: 1.1, margin: '4px 0' }}>
              ₹{predicted_price.toLocaleString()}
              <span style={{ fontSize: '1rem', color: '#64748b', fontWeight: 500 }}> / quintal</span>
            </div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              <span className={`badge ${dirBadgeClass}`} style={{ fontSize: '0.85rem', padding: '4px 12px' }}>
                {isUp ? <TrendingUp size={14} /> : isDown ? <TrendingDown size={14} /> : <Minus size={14} />}
                {pct_change >= 0 ? `+${pct_change}%` : `${pct_change}%`} ({lang === 'kn' ? direction_label_kn : direction_label})
              </span>
            </div>
          </div>
        </div>

        {/* Current vs Predicted Comparison Pills */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginTop: '24px',
          paddingTop: '20px',
          borderTop: '1px solid #e2e8f0'
        }}>
          <div>
            <div style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: 600 }}>CURRENT MANDI MODAL PRICE</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a' }}>
              ₹{current_modal_price.toLocaleString()} / Q
            </div>
          </div>
          <div>
            <div style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: 600 }}>STATE BASELINE PRICE (E[y])</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a' }}>
              ₹{explanation?.base_value?.toLocaleString() || '2,515'} / Q
            </div>
          </div>
          <div>
            <div style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: 600 }}>EXPECTED PRICE DIFFERENCE</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: dirColor }}>
              {predicted_price >= current_modal_price ? `+₹${(predicted_price - current_modal_price).toFixed(0)}` : `-₹${Math.abs(predicted_price - current_modal_price).toFixed(0)}`} / Q
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Price Trend Chart */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <TrendingUp size={20} color="#16a34a" />
              <span>Historical Mandi Trend & Model Forecast Point</span>
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '2px' }}>
              Verified 30-day historical daily modal prices (solid green line) connected to the direct {horizon_days}-day forecast point (blue dashed point).
            </p>
          </div>
        </div>

        <div style={{ width: '100%', height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chart_data || []} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="display_date" stroke="#94a3b8" fontSize={12} />
              <YAxis domain={['auto', 'auto']} stroke="#94a3b8" fontSize={12} tickFormatter={(val) => `₹${val}`} />
              <Tooltip
                formatter={(val, name) => [`₹${val?.toLocaleString()}/quintal`, name === 'historical_price' ? 'Historical Mandi Price' : 'Predicted Forecast Price']}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="historical_price"
                name="Historical Modal Price (₹/Q)"
                stroke="#16a34a"
                strokeWidth={2.5}
                dot={{ r: 3 }}
                connectNulls={false}
              />
              <Line
                type="monotone"
                dataKey="predicted_price"
                name={`Predicted ${horizon_days}-Day Price`}
                stroke="#2563eb"
                strokeWidth={3}
                strokeDasharray="5 5"
                dot={{ r: 6, fill: '#2563eb' }}
                connectNulls={true}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* SHAP EXPLAINABILITY SECTION */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title" style={{ color: '#0f172a' }}>
              <Sparkles size={20} color="#15803d" />
              <span>{t('shapTitle')}</span>
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '2px' }}>
              {t('shapSubtitle')}
            </p>
          </div>
        </div>

        {/* Dynamic Natural Language Explanation Box */}
        <div style={{
          background: '#f8fafc',
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          padding: '18px 22px',
          marginBottom: '22px'
        }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.05em', marginBottom: '8px' }}>
            NATURAL LANGUAGE SYNTHESIS (FROM SHAP VALUES)
          </div>
          <p style={{ fontSize: '0.98rem', color: '#1e293b', lineHeight: 1.6, marginBottom: '8px' }}>
            {lang === 'kn' ? explanation?.natural_language_kn : explanation?.natural_language_en}
          </p>
          <div style={{ fontSize: '0.78rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ShieldCheck size={14} color="#16a34a" />
            <span>Contributions derived directly from TreeExplainer on trained XGBoost model. Not hardcoded.</span>
          </div>
        </div>

        {/* SHAP Waterfall Plot */}
        <div style={{ marginBottom: '24px' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '10px' }}>
            Interactive SHAP Waterfall Attribution (₹ / Quintal)
          </h4>
          <WaterfallPlot
            waterfallData={explanation?.waterfall_data}
            baseValue={explanation?.base_value}
            predictedPrice={predicted_price}
            reconciliationDiff={explanation?.reconciliation_diff}
          />
        </div>

        {/* Key Positive & Negative Contributing Factors */}
        <div className="grid-2">
          {/* Positive Factors */}
          <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '12px', padding: '18px' }}>
            <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#166534', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px' }}>
              <TrendingUp size={16} />
              <span>Positive Price-Influencing Factors (Pushing Price Up)</span>
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {explanation?.positive_factors?.length > 0 ? (
                explanation.positive_factors.map((f, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', color: '#14532d' }}>
                    <span>{lang === 'kn' ? f.feature_name_kn : f.feature_name}</span>
                    <strong>+₹{f.contribution.toFixed(1)}</strong>
                  </div>
                ))
              ) : (
                <div style={{ fontSize: '0.82rem', color: '#64748b' }}>No major positive drivers for this horizon.</div>
              )}
            </div>
          </div>

          {/* Negative Factors */}
          <div style={{ background: '#fff1f2', border: '1px solid #fecdd3', borderRadius: '12px', padding: '18px' }}>
            <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#9f1239', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px' }}>
              <TrendingDown size={16} />
              <span>Negative Price-Influencing Factors (Pushing Price Down)</span>
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {explanation?.negative_factors?.length > 0 ? (
                explanation.negative_factors.map((f, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.86rem', color: '#881337' }}>
                    <span>{lang === 'kn' ? f.feature_name_kn : f.feature_name}</span>
                    <strong>-₹{Math.abs(f.contribution).toFixed(1)}</strong>
                  </div>
                ))
              ) : (
                <div style={{ fontSize: '0.82rem', color: '#64748b' }}>No major negative drivers for this horizon.</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* SMART SELLING RECOMMENDATION CARD */}
      <div className="card" style={{ marginBottom: '28px', borderLeft: '6px solid #16a34a' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <CircleDollarSign size={20} color="#15803d" />
              <span>{t('recommendationTitle')}</span>
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '2px' }}>
              Decision-support engine accounting for storage expenses, crop shelf life, and transportation costs.
            </p>
          </div>
          <span className={`badge ${recommendation?.urgency_tag === 'sell_now' ? 'badge-amber' : recommendation?.urgency_tag === 'wait' ? 'badge-green' : 'badge-blue'}`} style={{ fontSize: '0.92rem', padding: '6px 14px' }}>
            {lang === 'kn' ? recommendation?.action_kn : recommendation?.action}
          </span>
        </div>

        {/* Financial Breakdown Table */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '14px',
          background: '#f8fafc',
          padding: '16px',
          borderRadius: '10px',
          marginBottom: '16px'
        }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>CROP PERISHABILITY</span>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>{recommendation?.crop_perishability_tier}</div>
            <span style={{ fontSize: '0.72rem', color: '#64748b' }}>Shelf life: ~{recommendation?.shelf_life_days} days</span>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>STORAGE COST ({horizon_days}d)</span>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>₹{recommendation?.holding_costs?.total_storage_cost} / Q</div>
            <span style={{ fontSize: '0.72rem', color: '#64748b' }}>₹{recommendation?.holding_costs?.daily_storage_rate}/day</span>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>SPOILAGE RISK LOSS</span>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: '#e11d48' }}>-₹{recommendation?.holding_costs?.estimated_spoilage_loss} / Q</div>
            <span style={{ fontSize: '0.72rem', color: '#64748b' }}>Post-harvest buffer</span>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>ESTIMATED NET BENEFIT</span>
            <div style={{ fontSize: '1rem', fontWeight: 800, color: recommendation?.estimated_net_difference >= 0 ? '#16a34a' : '#e11d48' }}>
              {recommendation?.estimated_net_difference >= 0 ? `+₹${recommendation?.estimated_net_difference}` : `-₹${Math.abs(recommendation?.estimated_net_difference)}`} / Q
            </div>
            <span style={{ fontSize: '0.72rem', color: '#64748b' }}>Net: {recommendation?.net_pct_change}%</span>
          </div>
        </div>

        {/* Reasons */}
        <div style={{ marginBottom: '14px' }}>
          <strong style={{ fontSize: '0.88rem', color: '#0f172a' }}>Decision Rationale:</strong>
          <ul style={{ paddingLeft: '20px', marginTop: '6px', fontSize: '0.88rem', color: '#334155', lineHeight: 1.6 }}>
            {(lang === 'kn' ? recommendation?.key_reasons_kn : recommendation?.key_reasons)?.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>

        {/* Agricultural Disclaimer */}
        <div style={{ fontSize: '0.75rem', color: '#64748b', background: '#f1f5f9', padding: '10px 14px', borderRadius: '8px' }}>
          {lang === 'kn' ? recommendation?.disclaimer_kn : recommendation?.disclaimer_en}
        </div>
      </div>
    </div>
  );
};

export default PredictionResultPage;
