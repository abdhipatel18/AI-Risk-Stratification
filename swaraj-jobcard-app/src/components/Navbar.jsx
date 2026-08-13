import React from 'react';
import { Wrench, Plus, Package, RotateCcw, Download, ShieldCheck, Tractor } from 'lucide-react';

export const Navbar = ({ onOpenCreate, onOpenCatalog, onResetDemo, onExportData, activeCount, lowStockCount }) => {
  return (
    <header className="navbar-container">
      <div className="navbar-content">
        <div className="brand-section">
          <div className="brand-logo">
            <Tractor size={32} className="brand-icon" />
          </div>
          <div>
            <div className="brand-title">
              <span className="brand-highlight">SWARAJ</span> TRACTORS
            </div>
            <div className="brand-subtitle">
              Authorized Showroom & Service Center | Job Card System
            </div>
          </div>
        </div>

        <div className="nav-actions">
          <div className="stats-badges">
            <span className="badge badge-active">
              <Wrench size={14} />
              {activeCount} Active Jobs
            </span>
            {lowStockCount > 0 && (
              <span className="badge badge-warning" title="Parts with stock < 10 Pcs">
                <Package size={14} />
                {lowStockCount} Low Stock Parts
              </span>
            )}
          </div>

          <button className="btn btn-secondary" onClick={onOpenCatalog}>
            <Package size={18} />
            <span>Parts Catalog ({'<'}No. & Name{'>'})</span>
          </button>

          <button className="btn btn-primary" onClick={onOpenCreate}>
            <Plus size={18} />
            <span>New Job Card</span>
          </button>

          <button className="btn btn-icon" onClick={onExportData} title="Export All Data (JSON)">
            <Download size={18} />
          </button>

          <button className="btn btn-icon btn-ghost" onClick={onResetDemo} title="Reset to Sample Data">
            <RotateCcw size={18} />
          </button>
        </div>
      </div>
    </header>
  );
};
