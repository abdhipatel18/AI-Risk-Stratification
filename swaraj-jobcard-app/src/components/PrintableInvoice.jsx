import React from 'react';
import { X, Printer, Tractor, CheckCircle } from 'lucide-react';
import { calculateJobCardTotals, formatCurrency, formatDate } from '../utils/formatters';

export const PrintableInvoice = ({ jobCard, onClose }) => {
  if (!jobCard) return null;

  const totals = calculateJobCardTotals(jobCard);

  const handlePrintAction = () => {
    window.print();
  };

  return (
    <div className="modal-backdrop print-overlay">
      <div className="print-modal-actions no-print">
        <button className="btn btn-primary btn-print-trigger" onClick={handlePrintAction}>
          <Printer size={18} /> Click to Print Official Job Card Invoice
        </button>
        <button className="btn btn-ghost" onClick={onClose}>
          <X size={18} /> Close Preview
        </button>
      </div>

      {/* Printable Sheet */}
      <div className="invoice-sheet" id="printable-invoice">
        {/* Dealership Header */}
        <div className="invoice-header">
          <div className="dealership-brand">
            <div className="swaraj-badge-logo">SWARAJ</div>
            <div>
              <h1 className="dealership-title">SWARAJ TRACTORS AUTHORIZED WORKSHOP</h1>
              <p className="dealership-sub">PATEL TRACTORS & SPARES | SALES • SERVICE • GENUINE PARTS</p>
              <p className="dealership-contact">NH-8 Service Road, Anand, Gujarat - 388001 | Ph: +91 98765 00000 / 02692-245890</p>
              <p className="dealership-gst"><strong>GSTIN:</strong> 24ABCDE1234F1Z5 | <strong>Dealer Code:</strong> SW-GJ-4412</p>
            </div>
          </div>
          <div className="invoice-doc-type">
            <h2>JOB CARD & TAX INVOICE</h2>
            <div className="doc-number">{jobCard.jobCardNo}</div>
            <div className="doc-date">Date: {formatDate(jobCard.dateInward)}</div>
          </div>
        </div>

        <div className="invoice-divider"></div>

        {/* Customer & Tractor Info Grid */}
        <div className="info-grid">
          <div className="info-box">
            <div className="box-title">CUSTOMER DETAILS</div>
            <table className="info-table">
              <tbody>
                <tr>
                  <td><strong>Name:</strong></td>
                  <td>{jobCard.customerName}</td>
                </tr>
                <tr>
                  <td><strong>Phone:</strong></td>
                  <td>{jobCard.customerPhone}</td>
                </tr>
                <tr>
                  <td><strong>Village/Taluka:</strong></td>
                  <td>{jobCard.customerVillage || 'N/A'}</td>
                </tr>
                <tr>
                  <td><strong>Address:</strong></td>
                  <td>{jobCard.customerAddress || 'N/A'}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="info-box">
            <div className="box-title">TRACTOR & SERVICE DETAILS</div>
            <table className="info-table">
              <tbody>
                <tr>
                  <td><strong>Tractor Model:</strong></td>
                  <td><strong>{jobCard.tractorModel}</strong></td>
                </tr>
                <tr>
                  <td><strong>Reg No:</strong></td>
                  <td>{jobCard.regNo || 'N/A'}</td>
                </tr>
                <tr>
                  <td><strong>Chassis No:</strong></td>
                  <td>{jobCard.chassisNo || 'N/A'}</td>
                </tr>
                <tr>
                  <td><strong>Engine No:</strong></td>
                  <td>{jobCard.engineNo || 'N/A'}</td>
                </tr>
                <tr>
                  <td><strong>Meter Reading:</strong></td>
                  <td>{jobCard.meterReading || 'N/A'}</td>
                </tr>
                <tr>
                  <td><strong>Service Type:</strong></td>
                  <td>{jobCard.serviceType}</td>
                </tr>
                <tr>
                  <td><strong>Technician:</strong></td>
                  <td>{jobCard.technician}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Complaints Section */}
        {jobCard.customerComplaints && jobCard.customerComplaints.length > 0 && (
          <div className="invoice-section">
            <div className="section-title">WORK REQUESTED / CUSTOMER COMPLAINTS</div>
            <ul className="complaints-print-list">
              {jobCard.customerComplaints.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Used Parts Table */}
        <div className="invoice-section">
          <div className="section-title">1. USED PARTS INSTALLED / REPLACED</div>
          <table className="invoice-table">
            <thead>
              <tr>
                <th style={{ width: '40px' }}>S.N.</th>
                <th>Part Number</th>
                <th>Part Name / Description</th>
                <th style={{ width: '50px' }}>Qty</th>
                <th style={{ width: '90px' }}>Rate (₹)</th>
                <th style={{ width: '60px' }}>GST %</th>
                <th style={{ width: '100px' }} className="text-right">Total (₹)</th>
              </tr>
            </thead>
            <tbody>
              {(!jobCard.usedParts || jobCard.usedParts.length === 0) ? (
                <tr>
                  <td colSpan="7" className="text-center italic">No used parts installed on this job card.</td>
                </tr>
              ) : (
                jobCard.usedParts.map((p, idx) => {
                  const base = p.quantity * p.unitPrice;
                  const tax = base * (p.gstRate / 100);
                  const total = base + tax;

                  return (
                    <tr key={idx}>
                      <td className="text-center">{idx + 1}</td>
                      <td><strong>{p.partNumber}</strong></td>
                      <td>{p.partName}</td>
                      <td className="text-center">{p.quantity} {p.unit || 'Pc'}</td>
                      <td>{formatCurrency(p.unitPrice)}</td>
                      <td>{p.gstRate}%</td>
                      <td className="text-right font-bold">{formatCurrency(total)}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Remaining / Returned Parts Log */}
        {jobCard.remainingParts && jobCard.remainingParts.length > 0 && (
          <div className="invoice-section">
            <div className="section-title">2. REMAINING & RETURNED PARTS LOG</div>
            <table className="invoice-table">
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>S.N.</th>
                  <th>Part Number</th>
                  <th>Part Name / Description</th>
                  <th style={{ width: '60px' }}>Qty</th>
                  <th>Disposition / Status</th>
                  <th>Technician Remarks</th>
                </tr>
              </thead>
              <tbody>
                {jobCard.remainingParts.map((p, idx) => (
                  <tr key={idx}>
                    <td className="text-center">{idx + 1}</td>
                    <td><strong>{p.partNumber}</strong></td>
                    <td>{p.partName}</td>
                    <td className="text-center">{p.quantity} {p.unit || 'Pc'}</td>
                    <td><strong>{p.disposition}</strong></td>
                    <td>{p.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Labor Charges Table */}
        <div className="invoice-section">
          <div className="section-title">3. LABOR & SERVICE CHARGES</div>
          <table className="invoice-table">
            <thead>
              <tr>
                <th style={{ width: '40px' }}>S.N.</th>
                <th>Labor Operation Description</th>
                <th style={{ width: '120px' }} className="text-right">Amount (₹)</th>
              </tr>
            </thead>
            <tbody>
              {(!jobCard.laborCharges || jobCard.laborCharges.length === 0) ? (
                <tr>
                  <td colSpan="3" className="text-center italic">No labor charges.</td>
                </tr>
              ) : (
                jobCard.laborCharges.map((l, idx) => (
                  <tr key={idx}>
                    <td className="text-center">{idx + 1}</td>
                    <td>{l.description}</td>
                    <td className="text-right font-bold">{formatCurrency(l.amount)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Financial Totals & Signatures Grid */}
        <div className="totals-sign-grid">
          <div className="terms-box">
            <div className="terms-title">Terms & Conditions:</div>
            <ol className="terms-list">
              <li>Genuine Swaraj Spare Parts are guaranteed as per manufacturer warranty policy.</li>
              <li>Old parts logged above are handed over to customer / scrapped as per disposition choice.</li>
              <li>Tractor delivery taken post satisfactory test run by customer.</li>
            </ol>
            {jobCard.notes && (
              <div className="remarks-box">
                <strong>Technician Remarks:</strong> {jobCard.notes}
              </div>
            )}
          </div>

          <div className="calculation-box">
            <table className="calc-table">
              <tbody>
                <tr>
                  <td>Parts Base Subtotal:</td>
                  <td className="text-right">{formatCurrency(totals.partsTotal)}</td>
                </tr>
                <tr>
                  <td>CGST (Output 9%):</td>
                  <td className="text-right">{formatCurrency(totals.cgst)}</td>
                </tr>
                <tr>
                  <td>SGST (Output 9%):</td>
                  <td className="text-right">{formatCurrency(totals.sgst)}</td>
                </tr>
                <tr>
                  <td>Labor Charges Total:</td>
                  <td className="text-right">{formatCurrency(totals.laborTotal)}</td>
                </tr>
                {totals.discount > 0 && (
                  <tr className="discount-row">
                    <td>Special Discount:</td>
                    <td className="text-right">-{formatCurrency(totals.discount)}</td>
                  </tr>
                )}
                <tr className="grand-total-row">
                  <td><strong>GRAND TOTAL:</strong></td>
                  <td className="text-right"><strong>{formatCurrency(totals.grandTotal)}</strong></td>
                </tr>
                <tr>
                  <td>Payment Status:</td>
                  <td className="text-right"><strong>{jobCard.paymentStatus}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Signature Line Footer */}
        <div className="signatures-row">
          <div className="sig-block">
            <div className="sig-line"></div>
            <div>Customer Signature</div>
            <div className="sig-sub">(Acknowledged Receipt of Tractor & Parts)</div>
          </div>

          <div className="sig-block">
            <div className="sig-line"></div>
            <div>Technician / Mechanic</div>
            <div className="sig-sub">({jobCard.technician})</div>
          </div>

          <div className="sig-block">
            <div className="sig-line"></div>
            <div>For PATEL SWARAJ TRACTORS</div>
            <div className="sig-sub">Authorized Signatory & Seal</div>
          </div>
        </div>
      </div>
    </div>
  );
};
