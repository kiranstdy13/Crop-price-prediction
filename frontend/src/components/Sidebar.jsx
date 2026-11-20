import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import {
  LayoutDashboard,
  TrendingUp,
  GitCompare,
  BookmarkCheck,
  History,
  ShieldCheck,
  Info
} from 'lucide-react';

const Sidebar = () => {
  const { user, isAdmin } = useAuth();
  const { t } = useLanguage();

  const navItems = [
    { to: '/', label: t('dashboard'), icon: LayoutDashboard },
    { to: '/predict', label: t('predictPrices'), icon: TrendingUp },
    { to: '/compare', label: t('marketComparison'), icon: GitCompare },
    { to: '/saved', label: t('savedCrops'), icon: BookmarkCheck },
    { to: '/history', label: t('history'), icon: History },
  ];

  if (isAdmin) {
    navItems.push({ to: '/admin', label: t('adminPortal'), icon: ShieldCheck });
  }

  return (
    <aside className="sidebar">
      <div style={{ padding: '24px 20px', flex: 1 }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#94a3b8', letterSpacing: '0.05em', marginBottom: '12px', paddingLeft: '8px' }}>
          Navigation
        </div>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '11px 14px',
                  borderRadius: '10px',
                  textDecoration: 'none',
                  fontSize: '0.92rem',
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? '#15803d' : '#475569',
                  background: isActive ? '#dcfce7' : 'transparent',
                  transition: 'all 0.2s ease',
                })}
              >
                <Icon size={19} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Dataset & System Badge */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid #e2e8f0', background: '#f8fafc' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
          <Info size={16} color="#16a34a" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div style={{ fontSize: '0.75rem', color: '#64748b', lineHeight: 1.4 }}>
            <strong style={{ color: '#0f172a' }}>Verified Source:</strong><br />
            AGMARKNET & IMD<br />
            Karnataka Mandis (2022-2025)
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
