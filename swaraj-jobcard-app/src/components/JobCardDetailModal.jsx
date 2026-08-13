import React from 'react';
import { X, Printer, Edit3, Tractor, User, Phone, MapPin, Calendar, Clock, Wrench, Package, DollarSign } from 'lucide-react';
import { calculateJobCardTotals, formatCurrency, formatDate } from '../utils/formatters';

export const JobCardDetailModal = ({ jobCard, onClose, onEdit, onPrint }) => {
  if (!jobCard) return null;

  const totals = calculateJobCardTotals(jobCard);

  return (
    <div className="modal-backdrop">
      <div className="modal-container modal-large">
        <div className="modal-header">
          <div className="header-title">
            <Tractor size={26} className="icon-red" />
            <div>
              <h2>Job Card Details: {jobCard.jobCardNo}</h2>
              <span className="subtitle">Swaraj Authorized Workshop Record</span>
            </div>
          </div>
          <div className="header-actions">
            <button className="btn btn-secondary" onClick={() => onPrint(jobCard)}>
              <Printer size={16} /> Print Tax Invoice
            </button>
            <button className="btn btn-primary" onClick={() => onEdit(jobCard)}>
              <Edit3 size={16} /> Edit
            </button>
            <button className="close-btn" onClick={onClose}><X size={20} /></button>
          </div>
        </div>

        <div className="modal-body">
          {/* Top Banner Info */}
          <div className="detail-banner-grid">
            <div className="banner-card">
              <div className="banner-label"><User size={14} /> Customer</div>
              <div className="banner-val">{jobCard.customerName}</div>
              <div className="banner-sub"><Phone size={12} /> {jobCard.customerPhone}</div>
              <div className="banner-sub"><MapPin size={12} /> {jobCard.customerVillage}</div>
            </div>

            <div className="banner-card">
              <div className="banner-label"><Tractor size={14} /> Tractor Specs</div>
              <div className="banner-val">{jobCard.tractorModel}</div>
              <div className="banner-sub">Reg: {jobCard.regNo || 'N/A'}</div>
              <div className="banner-sub">Chassis: {jobCard.chassisNo || 'N/A'} | Meter: {jobCard.meterReading || 'N/A'}</div>
            </div>

            <div className="banner-card">
              <div className="banner-label"><Calendar size={14} /> Service Info</div>
              <div className="banner-val">{jobCard.serviceType}</div>
              <div className="banner-sub">Date: {formatDate(jobCard.dateInward)}</div>
              <div className="banner-sub">Tech: {jobCard.technician}</div>
            </div>

            <div className="banner-card highlight-card">
              <div className="banner-label"><DollarSign size={14} /> Net Payable</div>
              <div className="banner-val text-red">{formatCurrency(totals.grandTotal)}</div>
              <div className="banner-sub">Status: <strong>{jobCard.status}</strong></div>
              <div className="banner-sub">Payout: <strong>{jobCard.paymentStatus}</strong></div>
            </div>
          </div>

          {/* Complaints */}
          {jobCard.customerComplaints && jobCard.customerComplaints.length > 0 && (
            <div className="detail-section">
              <h3><Wrench size={16} /> Reported Complaints / Service Scope</h3>
              <ul className="detail-bullet-list">
                {jobCard.customerComplaints.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Used Parts Table */}
          <div className="detail-section">
            <h3><Wrench size={16} /> Used Parts Installed / Replaced ({(jobCard.usedParts || []).length})</h3>
            {(!jobCard.usedParts || jobCard.usedParts.length === 0) ? (
              <div className="empty-sub-state">No used parts recorded.</div>
            ) : (
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Part No</th>
                    <th>Part Name</th>
                    <th>Category</th>
                    <th>Qty</th>
                    <th>Unit Price</th>
                    <th>GST %</th>
                    <th>Total (Inc. Tax)</th>
                  </tr>
                </thead>
                <tbody>
                  {jobCard.usedParts.map((p, idx) => {
                    const base = p.quantity * p.unitPrice;
                    const tax = base * (p.gstRate / 100);
                    return (
                      <tr key={idx}>
                        <td><span className="part-code-badge">{p.partNumber}</span></td>
                        <td className="font-semibold">{p.partName}</td>
                        <td>{p.category}</td>
                        <td>{p.quantity} {p.unit || 'Pc'}</td>
                        <td>{formatCurrency(p.unitPrice)}</td>
                        <td>{p.gstRate}%</td>
                        <td className="font-bold">{formatCurrency(base + tax)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>

          {/* Remaining Parts Table */}
          <div className="detail-section">
            <h3><Package size={16} /> Remaining & Returned Parts Log ({(jobCard.remainingParts || []).length})</h3>
            {(!jobCard.remainingParts || jobCard.remainingParts.length === 0) ? (
              <div className="empty-sub-state">No remaining or returned parts logged.</div>
            ) : (
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Part No</th>
                    <th>Part Name / Description</th>
                    <th>Qty</th>
                    <th>Disposition</th>
                    <th>Notes / Remarks</th>
                  </tr>
                </thead>
                <tbody>
                  {jobCard.remainingParts.map((p, idx) => (
                    <tr key={idx}>
                      <td><span className="part-code-badge">{p.partNumber}</span></td>
                      <td className="font-semibold">{p.partName}</td>
                      <td>{p.quantity} {p.unit || 'Pc'}</td>
                      <td>
                        <span className={`disposition-pill ${p.disposition?.includes('Inventory') ? 'disp-inventory' : 'disp-customer'}`}>
                          {p.disposition}
                        </span>
                      </td>
                      <td>{p.notes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Labor & Grand Total Breakdown */}
          <div className="detail-two-col">
            <div className="detail-section flex-2">
              <h3><Wrench size={16} /> Labor Charges</h3>
              {(!jobCard.laborCharges || jobCard.laborCharges.length === 0) ? (
                <div className="empty-sub-state">No labor charges.</div>
              ) : (
                <ul className="detail-labor-list">
                  {jobCard.laborCharges.map((l, idx) => (
                    <li key={idx}>
                      <span>{l.description}</span>
                      <span className="font-bold">{formatCurrency(l.amount)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="detail-section billing-box">
              <h3>Financial Breakdown</h3>
              <div className="summary-line">
                <span>Parts Base:</span>
                <span>{formatCurrency(totals.partsTotal)}</span>
              </div>
              <div className="summary-line">
                <span>GST Tax (CGST+SGST):</span>
                <span>{formatCurrency(totals.partsTaxTotal)}</span>
              </div>
              <div className="summary-line">
                <span>Labor Total:</span>
                <span>{formatCurrency(totals.laborTotal)}</span>
              </div>
              <div className="summary-line text-red">
                <span>Discount:</span>
                <span>-{formatCurrency(totals.discount)}</span>
              </div>
              <hr />
              <div className="summary-grand-total">
                <span>Grand Total:</span>
                <span className="grand-price">{formatCurrency(totals.grandTotal)}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>Close</button>
          <button className="btn btn-primary" onClick={() => onPrint(jobCard)}>
            <Printer size={16} /> Print Full Invoice
          </button>
        </div>
      </div>
    </div>
  );
};
