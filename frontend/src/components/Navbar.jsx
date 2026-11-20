import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { Sprout, Globe, User, LogOut, ShieldCheck } from 'lucide-react';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const { lang, toggleLanguage, t } = useLanguage();

  return (
    <header style={{
      background: '#ffffff',
      borderBottom: '1px solid #e2e8f0',
      padding: '14px 32px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          background: '#dcfce7',
          color: '#15803d',
          padding: '8px',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Sprout size={24} />
        </div>
        <div>
          <Link to="/" style={{ textDecoration: 'none', color: '#0f172a' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: '800', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>{t('appTitle')}</span>
              <span className="badge badge-green" style={{ fontSize: '0.72rem', padding: '2px 8px' }}>
                Karnataka APMC
              </span>
            </h1>
          </Link>
          <p style={{ fontSize: '0.75rem', color: '#64748b' }}>
            {t('subTitle')}
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Language Switcher */}
        <button
          onClick={toggleLanguage}
          className="btn btn-outline"
          style={{ padding: '7px 14px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <Globe size={16} />
          <span>{lang === 'en' ? 'ಕನ್ನಡ (KN)' : 'English (EN)'}</span>
        </button>

        {isAuthenticated ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '9999px'
            }}>
              {user?.role === 'admin' ? (
                <ShieldCheck size={18} color="#15803d" />
              ) : (
                <User size={18} color="#16a34a" />
              )}
              <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{user?.name}</span>
              <span className={`badge ${user?.role === 'admin' ? 'badge-blue' : 'badge-green'}`} style={{ fontSize: '0.7rem' }}>
                {user?.role?.toUpperCase()}
              </span>
            </div>
            <button
              onClick={logout}
              className="btn btn-secondary"
              style={{ padding: '7px 12px', fontSize: '0.85rem' }}
              title="Sign Out"
            >
              <LogOut size={16} />
              <span>{t('logout')}</span>
            </button>
          </div>
        ) : (
          <Link to="/login" className="btn btn-primary" style={{ padding: '8px 18px', fontSize: '0.85rem' }}>
            <User size={16} />
            <span>{t('login')}</span>
          </Link>
        )}
      </div>
    </header>
  );
};

export default Navbar;
