import React, { useState } from 'react';
import { 
  Search, Filter, Wrench, CheckCircle2, Clock, AlertTriangle, 
  Eye, Edit3, Trash2, Printer, FileText, User, Phone, MapPin, 
  Calendar, CreditCard, ChevronRight, PackageCheck, Tractor 
} from 'lucide-react';
import { formatCurrency, calculateJobCardTotals, formatDate } from '../utils/formatters';

export const DashboardOverview = ({ 
  jobCards, 
  onSelectJobCard, 
  onEditJobCard, 
  onDeleteJobCard, 
  onPrintInvoice, 
  onNewJobCard 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Stats calculation
  const totalCards = jobCards.length;
  const inServiceCards = jobCards.filter(c => c.status === 'In Service' || c.status === 'Open');
  const readyCards = jobCards.filter(c => c.status === 'Ready for Delivery');
  const deliveredCards = jobCards.filter(c => c.status === 'Delivered' || c.status === 'Completed');

  const totalRevenue = jobCards.reduce((acc, card) => {
    const totals = calculateJobCardTotals(card);
    return acc + totals.grandTotal;
  }, 0);

  // Search & Filter logic
  const filteredCards = jobCards.filter(card => {
    const matchesStatus = statusFilter === 'ALL' || card.status === statusFilter;

    const query = searchTerm.toLowerCase().trim();
    if (!query) return matchesStatus;

    const matchesBasic = 
      card.jobCardNo.toLowerCase().includes(query) ||
      card.customerName.toLowerCase().includes(query) ||
      card.customerPhone.includes(query) ||
      card.tractorModel.toLowerCase().includes(query) ||
      card.regNo.toLowerCase().includes(query) ||
      (card.chassisNo && card.chassisNo.toLowerCase().includes(query)) ||
      (card.technician && card.technician.toLowerCase().includes(query));

    // Also match if part name or part number matches in used parts or remaining parts!
    const matchesUsedPart = (card.usedParts || []).some(
      p => (p.partName && p.partName.toLowerCase().includes(query)) ||
           (p.partNumber && p.partNumber.toLowerCase().includes(query))
    );

    const matchesRemainingPart = (card.remainingParts || []).some(
      p => (p.partName && p.partName.toLowerCase().includes(query)) ||
           (p.partNumber && p.partNumber.toLowerCase().includes(query))
    );

    return matchesStatus && (matchesBasic || matchesUsedPart || matchesRemainingPart);
  });

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'In Service': return 'badge-status badge-service';
      case 'Ready for Delivery': return 'badge-status badge-ready';
      case 'Delivered':
      case 'Completed': return 'badge-status badge-completed';
      case 'Open': return 'badge-status badge-open';
      default: return 'badge-status';
    }
  };

  return (
    <div className="dashboard-container">
      {/* Metrics Row */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span>Total Job Cards</span>
            <div className="metric-icon icon-blue"><FileText size={20} /></div>
          </div>
          <div className="metric-value">{totalCards}</div>
          <div className="metric-footer">Lifetime Showroom Inward</div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>In Service / Open</span>
            <div className="metric-icon icon-orange"><Clock size={20} /></div>
          </div>
          <div className="metric-value">{inServiceCards.length}</div>
          <div className="metric-footer">Tractors currently in bay</div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>Ready for Delivery</span>
            <div className="metric-icon icon-green"><PackageCheck size={20} /></div>
          </div>
          <div className="metric-value">{readyCards.length}</div>
          <div className="metric-footer">Service done, pending payout</div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>Total Billing Value</span>
            <div className="metric-icon icon-red"><CreditCard size={20} /></div>
          </div>
          <div className="metric-value">{formatCurrency(totalRevenue)}</div>
          <div className="metric-footer">Parts + Labor Total</div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="filter-bar">
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input 
            type="text" 
            placeholder="Search by Job Card #, Customer Name, Phone, Tractor Model, Part Name or Part Number..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button className="clear-search" onClick={() => setSearchTerm('')}>×</button>
          )}
        </div>

        <div className="status-tabs">
          <button 
            className={`tab-btn ${statusFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => setStatusFilter('ALL')}
          >
            All Cards ({totalCards})
          </button>
          <button 
            className={`tab-btn ${statusFilter === 'In Service' ? 'active' : ''}`}
            onClick={() => setStatusFilter('In Service')}
          >
            In Service ({inServiceCards.length})
          </button>
          <button 
            className={`tab-btn ${statusFilter === 'Ready for Delivery' ? 'active' : ''}`}
            onClick={() => setStatusFilter('Ready for Delivery')}
          >
            Ready ({readyCards.length})
          </button>
          <button 
            className={`tab-btn ${statusFilter === 'Delivered' ? 'active' : ''}`}
            onClick={() => setStatusFilter('Delivered')}
          >
            Delivered ({deliveredCards.length})
          </button>
        </div>
      </div>

      {/* Job Cards List / Table */}
      {filteredCards.length === 0 ? (
        <div className="empty-state">
          <Tractor size={48} className="empty-icon" />
          <h3>No Job Cards Found</h3>
          <p>Try clearing your search filters or create a new Swaraj Job Card entry.</p>
          <button className="btn btn-primary" onClick={onNewJobCard}>
            <Wrench size={16} /> Create Job Card Now
          </button>
        </div>
      ) : (
        <div className="cards-grid">
          {filteredCards.map(card => {
            const totals = calculateJobCardTotals(card);
            const usedPartsCount = (card.usedParts || []).length;
            const remainingPartsCount = (card.remainingParts || []).length;

            return (
              <div className="job-card-item" key={card.id}>
                <div className="card-top">
                  <div>
                    <span className="job-card-no">{card.jobCardNo}</span>
                    <span className="card-date"><Calendar size={12} /> {formatDate(card.dateInward)}</span>
                  </div>
                  <span className={getStatusBadgeClass(card.status)}>
                    {card.status}
                  </span>
                </div>

                <div className="card-customer">
                  <div className="customer-name"><User size={15} /> {card.customerName}</div>
                  <div className="customer-info">
                    <span><Phone size={13} /> {card.customerPhone}</span>
                    <span><MapPin size={13} /> {card.customerVillage}</span>
                  </div>
                </div>

                <div className="card-tractor-pill">
                  <Tractor size={16} />
                  <div>
                    <div className="tractor-model">{card.tractorModel}</div>
                    <div className="tractor-reg">Reg: {card.regNo || 'N/A'} | Chassis: {card.chassisNo || 'N/A'}</div>
                  </div>
                </div>

                <div className="card-parts-summary">
                  <div className="parts-summary-item">
                    <span className="label">Used Parts Installed:</span>
                    <span className="value text-red">{usedPartsCount} Parts</span>
                  </div>
                  <div className="parts-summary-item">
                    <span className="label">Remaining / Returned:</span>
                    <span className="value text-blue">{remainingPartsCount} Items</span>
                  </div>
                </div>

                {/* Used Parts list preview */}
                {usedPartsCount > 0 && (
                  <div className="parts-mini-list">
                    {card.usedParts.slice(0, 2).map((p, idx) => (
                      <div key={idx} className="mini-part-tag">
                        <span className="part-code">{p.partNumber}</span>
                        <span className="part-name-truncate">{p.partName}</span>
                        <span className="part-qty">x{p.quantity}</span>
                      </div>
                    ))}
                    {usedPartsCount > 2 && (
                      <span className="more-parts">+{usedPartsCount - 2} more parts</span>
                    )}
                  </div>
                )}

                <div className="card-billing">
                  <div className="bill-amount">
                    <span className="bill-label">Grand Total:</span>
                    <span className="bill-value">{formatCurrency(totals.grandTotal)}</span>
                  </div>
                  <span className={`payment-pill ${card.paymentStatus?.toLowerCase().includes('paid') ? 'paid' : 'unpaid'}`}>
                    {card.paymentStatus || 'Unpaid'}
                  </span>
                </div>

                <div className="card-actions">
                  <button className="btn-icon-label" onClick={() => onSelectJobCard(card)}>
                    <Eye size={15} /> View
                  </button>
                  <button className="btn-icon-label" onClick={() => onEditJobCard(card)}>
                    <Edit3 size={15} /> Edit
                  </button>
                  <button className="btn-icon-label text-print" onClick={() => onPrintInvoice(card)}>
                    <Printer size={15} /> Print
                  </button>
                  <button className="btn-icon-label text-delete" onClick={() => onDeleteJobCard(card.id)}>
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
