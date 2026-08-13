import React, { useState, useEffect } from 'react';
import { 
  X, Plus, Trash2, Search, Tractor, User, Wrench, Package, 
  DollarSign, Check, AlertCircle, RefreshCw, FilePlus 
} from 'lucide-react';
import { SWARAJ_MODELS, TECHNICIANS } from '../data/swarajCatalog';
import { calculateJobCardTotals, formatCurrency } from '../utils/formatters';

export const JobCardFormModal = ({ 
  isOpen, 
  onClose, 
  onSave, 
  editingJobCard, 
  catalog 
}) => {
  if (!isOpen) return null;

  // Active Tab state
  const [activeTab, setActiveTab] = useState('BASIC');

  // Form Fields
  const [jobCardNo, setJobCardNo] = useState('');
  const [dateInward, setDateInward] = useState(new Date().toISOString().split('T')[0]);
  const [timeInward, setTimeInward] = useState('10:00 AM');
  const [expectedDelivery, setExpectedDelivery] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerVillage, setCustomerVillage] = useState('');
  const [customerAddress, setCustomerAddress] = useState('');
  const [tractorModel, setTractorModel] = useState(SWARAJ_MODELS[0]);
  const [regNo, setRegNo] = useState('');
  const [chassisNo, setChassisNo] = useState('');
  const [engineNo, setEngineNo] = useState('');
  const [meterReading, setMeterReading] = useState('');
  const [serviceType, setServiceType] = useState('Paid Service');
  const [technician, setTechnician] = useState(TECHNICIANS[0]);
  const [status, setStatus] = useState('In Service');
  const [paymentStatus, setPaymentStatus] = useState('Unpaid');
  const [notes, setNotes] = useState('');
  const [discount, setDiscount] = useState(0);

  // Complaints checklist
  const [complaintInput, setComplaintInput] = useState('');
  const [complaints, setComplaints] = useState([]);

  // Used Parts list
  const [usedParts, setUsedParts] = useState([]);
  // Quick Add Part from Catalog State
  const [selectedCatalogPartId, setSelectedCatalogPartId] = useState('');
  const [catalogSearch, setCatalogSearch] = useState('');
  const [partQtyInput, setPartQtyInput] = useState(1);

  // Custom Used Part modal state if part not in catalog
  const [customPartNumber, setCustomPartNumber] = useState('');
  const [customPartName, setCustomPartName] = useState('');
  const [customUnitPrice, setCustomUnitPrice] = useState('');
  const [customGstRate, setCustomGstRate] = useState(18);

  // Remaining / Returned Parts list
  const [remainingParts, setRemainingParts] = useState([]);
  const [remPartNumber, setRemPartNumber] = useState('');
  const [remPartName, setRemPartName] = useState('');
  const [remQty, setRemQty] = useState(1);
  const [remUnit, setRemUnit] = useState('Pc');
  const [remDisposition, setRemDisposition] = useState('Returned to Showroom Inventory');
  const [remNotes, setRemNotes] = useState('');

  // Labor Charges list
  const [laborCharges, setLaborCharges] = useState([]);
  const [laborDesc, setLaborDesc] = useState('');
  const [laborAmount, setLaborAmount] = useState('');

  // Initialize or populate editing state
  useEffect(() => {
    if (editingJobCard) {
      setJobCardNo(editingJobCard.jobCardNo || '');
      setDateInward(editingJobCard.dateInward || new Date().toISOString().split('T')[0]);
      setTimeInward(editingJobCard.timeInward || '10:00 AM');
      setExpectedDelivery(editingJobCard.expectedDelivery || '');
      setCustomerName(editingJobCard.customerName || '');
      setCustomerPhone(editingJobCard.customerPhone || '');
      setCustomerVillage(editingJobCard.customerVillage || '');
      setCustomerAddress(editingJobCard.customerAddress || '');
      setTractorModel(editingJobCard.tractorModel || SWARAJ_MODELS[0]);
      setRegNo(editingJobCard.regNo || '');
      setChassisNo(editingJobCard.chassisNo || '');
      setEngineNo(editingJobCard.engineNo || '');
      setMeterReading(editingJobCard.meterReading || '');
      setServiceType(editingJobCard.serviceType || 'Paid Service');
      setTechnician(editingJobCard.technician || TECHNICIANS[0]);
      setStatus(editingJobCard.status || 'In Service');
      setPaymentStatus(editingJobCard.paymentStatus || 'Unpaid');
      setNotes(editingJobCard.notes || '');
      setDiscount(editingJobCard.discount || 0);
      setComplaints(editingJobCard.customerComplaints || []);
      setUsedParts(editingJobCard.usedParts || []);
      setRemainingParts(editingJobCard.remainingParts || []);
      setLaborCharges(editingJobCard.laborCharges || []);
    } else {
      // Auto-generate Job Card Number
      const randomNum = Math.floor(100 + Math.random() * 900);
      setJobCardNo(`SW-JC-${new Date().getFullYear()}-${randomNum}`);
      setDateInward(new Date().toISOString().split('T')[0]);
      setTimeInward(new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
      setExpectedDelivery('');
      setCustomerName('');
      setCustomerPhone('');
      setCustomerVillage('');
      setCustomerAddress('');
      setTractorModel(SWARAJ_MODELS[0]);
      setRegNo('');
      setChassisNo('');
      setEngineNo('');
      setMeterReading('');
      setServiceType('Paid Service');
      setTechnician(TECHNICIANS[0]);
      setStatus('In Service');
      setPaymentStatus('Unpaid');
      setNotes('');
      setDiscount(0);
      setComplaints(['Routine oil change and multi-point check']);
      setUsedParts([]);
      setRemainingParts([]);
      setLaborCharges([{ id: 'L-1', description: 'General Service & Inspection Labor', amount: 350 }]);
    }
  }, [editingJobCard, isOpen]);

  // Complaints Handlers
  const handleAddComplaint = () => {
    if (!complaintInput.trim()) return;
    setComplaints([...complaints, complaintInput.trim()]);
    setComplaintInput('');
  };

  const handleRemoveComplaint = (index) => {
    setComplaints(complaints.filter((_, i) => i !== index));
  };

  // Add Used Part from Catalog
  const handleAddCatalogPart = () => {
    if (!selectedCatalogPartId) return;
    const item = catalog.find(p => p.id === selectedCatalogPartId);
    if (!item) return;

    // Check if already in list
    const existingIndex = usedParts.findIndex(p => p.partNumber === item.partNumber);
    if (existingIndex >= 0) {
      const updated = [...usedParts];
      updated[existingIndex].quantity += Number(partQtyInput);
      setUsedParts(updated);
    } else {
      setUsedParts([
        ...usedParts,
        {
          id: `UP-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
          partNumber: item.partNumber,
          partName: item.partName,
          category: item.category,
          unitPrice: item.unitPrice,
          gstRate: item.gstRate,
          unit: item.unit || 'Pc',
          quantity: Number(partQtyInput) || 1
        }
      ]);
    }
    setSelectedCatalogPartId('');
    setCatalogSearch('');
    setPartQtyInput(1);
  };

  // Add Custom Used Part
  const handleAddCustomUsedPart = () => {
    if (!customPartName.trim()) return;
    setUsedParts([
      ...usedParts,
      {
        id: `UP-${Date.now()}`,
        partNumber: customPartNumber.trim().toUpperCase() || `SW-CUST-${Math.floor(100 + Math.random() * 900)}`,
        partName: customPartName.trim(),
        category: 'Custom Part',
        unitPrice: Number(customUnitPrice) || 0,
        gstRate: Number(customGstRate) || 18,
        unit: 'Pc',
        quantity: 1
      }
    ]);
    setCustomPartNumber('');
    setCustomPartName('');
    setCustomUnitPrice('');
    setCustomGstRate(18);
  };

  const handleRemoveUsedPart = (id) => {
    setUsedParts(usedParts.filter(p => p.id !== id));
  };

  const handleUpdateUsedPartQty = (id, newQty) => {
    const qty = Math.max(1, Number(newQty) || 1);
    setUsedParts(usedParts.map(p => p.id === id ? { ...p, quantity: qty } : p));
  };

  // Add Remaining Part
  const handleAddRemainingPart = () => {
    if (!remPartName.trim()) return;
    setRemainingParts([
      ...remainingParts,
      {
        id: `RP-${Date.now()}`,
        partNumber: remPartNumber.trim().toUpperCase() || 'N/A',
        partName: remPartName.trim(),
        quantity: Number(remQty) || 1,
        unit: remUnit,
        disposition: remDisposition,
        notes: remNotes.trim() || 'No additional note'
      }
    ]);
    setRemPartNumber('');
    setRemPartName('');
    setRemQty(1);
    setRemNotes('');
  };

  const handleRemoveRemainingPart = (id) => {
    setRemainingParts(remainingParts.filter(p => p.id !== id));
  };

  // Labor Handlers
  const handleAddLabor = () => {
    if (!laborDesc.trim() || !laborAmount) return;
    setLaborCharges([
      ...laborCharges,
      {
        id: `L-${Date.now()}`,
        description: laborDesc.trim(),
        amount: Number(laborAmount) || 0
      }
    ]);
    setLaborDesc('');
    setLaborAmount('');
  };

  const handleRemoveLabor = (id) => {
    setLaborCharges(laborCharges.filter(l => l.id !== id));
  };

  // Form Submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!customerName.trim() || !customerPhone.trim()) {
      alert('Please fill out Customer Name and Phone Number.');
      setActiveTab('BASIC');
      return;
    }

    const cardData = {
      id: editingJobCard ? editingJobCard.id : `JC-${Date.now()}`,
      jobCardNo,
      dateInward,
      timeInward,
      expectedDelivery,
      customerName,
      customerPhone,
      customerVillage,
      customerAddress,
      tractorModel,
      regNo,
      chassisNo,
      engineNo,
      meterReading,
      serviceType,
      technician,
      status,
      paymentStatus,
      notes,
      discount: Number(discount) || 0,
      customerComplaints: complaints,
      usedParts,
      remainingParts,
      laborCharges
    };

    onSave(cardData);
  };

  // Filter Catalog by search query (matching Name OR Part Number)
  const filteredCatalog = catalog.filter(item => {
    if (!catalogSearch) return true;
    const q = catalogSearch.toLowerCase();
    return (
      item.partName.toLowerCase().includes(q) ||
      item.partNumber.toLowerCase().includes(q) ||
      item.category.toLowerCase().includes(q)
    );
  });

  const totals = calculateJobCardTotals({ usedParts, laborCharges, discount });

  return (
    <div className="modal-backdrop">
      <div className="modal-container modal-large">
        <div className="modal-header">
          <div className="header-title">
            <Tractor size={24} className="icon-red" />
            <div>
              <h2>{editingJobCard ? 'Edit Job Card' : 'New Swaraj Job Card Entry'}</h2>
              <span className="subtitle">Job Card #: <strong>{jobCardNo}</strong></span>
            </div>
          </div>
          <button className="close-btn" onClick={onClose}><X size={20} /></button>
        </div>

        {/* Modal Tabs Navigation */}
        <div className="modal-tabs">
          <button 
            type="button"
            className={`modal-tab ${activeTab === 'BASIC' ? 'active' : ''}`}
            onClick={() => setActiveTab('BASIC')}
          >
            <User size={16} /> 1. Customer & Tractor
          </button>

          <button 
            type="button"
            className={`modal-tab ${activeTab === 'USED_PARTS' ? 'active' : ''}`}
            onClick={() => setActiveTab('USED_PARTS')}
          >
            <Wrench size={16} /> 2. Used Parts ({usedParts.length})
          </button>

          <button 
            type="button"
            className={`modal-tab ${activeTab === 'REMAINING_PARTS' ? 'active' : ''}`}
            onClick={() => setActiveTab('REMAINING_PARTS')}
          >
            <Package size={16} /> 3. Remaining / Returned Parts ({remainingParts.length})
          </button>

          <button 
            type="button"
            className={`modal-tab ${activeTab === 'LABOR_BILLING' ? 'active' : ''}`}
            onClick={() => setActiveTab('LABOR_BILLING')}
          >
            <DollarSign size={16} /> 4. Labor & Billing Total
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {/* TAB 1: BASIC CUSTOMER & TRACTOR DETAILS */}
            {activeTab === 'BASIC' && (
              <div className="form-section-grid">
                <div className="form-group-box">
                  <h3><User size={16} /> Customer Details</h3>
                  <div className="form-row">
                    <div className="form-field">
                      <label>Customer Full Name *</label>
                      <input 
                        type="text" 
                        required 
                        placeholder="e.g. Ramesh Bhai Patel"
                        value={customerName}
                        onChange={e => setCustomerName(e.target.value)}
                      />
                    </div>
                    <div className="form-field">
                      <label>Mobile Number *</label>
                      <input 
                        type="tel" 
                        required 
                        placeholder="e.g. 9876543210"
                        value={customerPhone}
                        onChange={e => setCustomerPhone(e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-field">
                      <label>Village / Taluka</label>
                      <input 
                        type="text" 
                        placeholder="e.g. Anand, Kheda"
                        value={customerVillage}
                        onChange={e => setCustomerVillage(e.target.value)}
                      />
                    </div>
                    <div className="form-field">
                      <label>Full Address</label>
                      <input 
                        type="text" 
                        placeholder="House/Farm address..."
                        value={customerAddress}
                        onChange={e => setCustomerAddress(e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                <div className="form-group-box">
                  <h3><Tractor size={16} /> Tractor Technical Specifications</h3>
                  <div className="form-row">
                    <div className="form-field">
                      <label>Swaraj Tractor Model</label>
                      <select 
                        value={tractorModel}
                        onChange={e => setTractorModel(e.target.value)}
                      >
                        {SWARAJ_MODELS.map((m, idx) => (
                          <option key={idx} value={m}>{m}</option>
                        ))}
                      </select>
                    </div>

                    <div className="form-field">
                      <label>Registration Number</label>
                      <input 
                        type="text" 
                        placeholder="e.g. GJ-23-AB-4589"
                        value={regNo}
                        onChange={e => setRegNo(e.target.value.toUpperCase())}
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-field">
                      <label>Chassis Number</label>
                      <input 
                        type="text" 
                        placeholder="e.g. MA1S744FEK01982"
                        value={chassisNo}
                        onChange={e => setChassisNo(e.target.value.toUpperCase())}
                      />
                    </div>
                    <div className="form-field">
                      <label>Engine Number</label>
                      <input 
                        type="text" 
                        placeholder="e.g. E744FE89123"
                        value={engineNo}
                        onChange={e => setEngineNo(e.target.value.toUpperCase())}
                      />
                    </div>
                    <div className="form-field">
                      <label>Hour Meter (HR Reading)</label>
                      <input 
                        type="text" 
                        placeholder="e.g. 1250 HR"
                        value={meterReading}
                        onChange={e => setMeterReading(e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                <div className="form-group-box">
                  <h3><Wrench size={16} /> Inward & Workshop Assignment</h3>
                  <div className="form-row">
                    <div className="form-field">
                      <label>Service / Repair Category</label>
                      <select value={serviceType} onChange={e => setServiceType(e.target.value)}>
                        <option value="1st Free Service">1st Free Service</option>
                        <option value="2nd Free Service">2nd Free Service</option>
                        <option value="Paid Service">Paid Service</option>
                        <option value="Engine Overhaul">Engine Overhaul</option>
                        <option value="Transmission & Hydraulics">Transmission & Hydraulics</option>
                        <option value="Brake & Clutch Repair">Brake & Clutch Repair</option>
                        <option value="Electrical & Battery Service">Electrical & Battery Service</option>
                        <option value="Emergency Field Repair">Emergency Field Repair</option>
                      </select>
                    </div>

                    <div className="form-field">
                      <label>Assigned Technician / Mechanic</label>
                      <select value={technician} onChange={e => setTechnician(e.target.value)}>
                        {TECHNICIANS.map((tech, i) => (
                          <option key={i} value={tech}>{tech}</option>
                        ))}
                      </select>
                    </div>

                    <div className="form-field">
                      <label>Inward Date</label>
                      <input type="date" value={dateInward} onChange={e => setDateInward(e.target.value)} />
                    </div>
                  </div>

                  {/* Customer Complaints List */}
                  <div className="complaints-section">
                    <label>Customer Reported Complaints / Work Requested</label>
                    <div className="add-input-group">
                      <input 
                        type="text" 
                        placeholder="Describe issue (e.g. Hydraulic lift noise, Clutch slipping...)"
                        value={complaintInput}
                        onChange={e => setComplaintInput(e.target.value)}
                        onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddComplaint(); } }}
                      />
                      <button type="button" className="btn btn-secondary" onClick={handleAddComplaint}>
                        <Plus size={16} /> Add Issue
                      </button>
                    </div>

                    <ul className="complaint-tags-list">
                      {complaints.map((item, idx) => (
                        <li key={idx} className="complaint-tag">
                          <span>• {item}</span>
                          <button type="button" onClick={() => handleRemoveComplaint(idx)}>×</button>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 2: USED PARTS ENTRY (NAME & NUMBER) */}
            {activeTab === 'USED_PARTS' && (
              <div className="form-section-box">
                <div className="section-header-row">
                  <div>
                    <h3><Wrench size={18} /> Used Parts Installed / Replaced</h3>
                    <p className="section-desc">
                      Enter all genuine Swaraj parts installed during servicing. Auto-lookup by <strong>Part Name</strong> or <strong>Part Number</strong>.
                    </p>
                  </div>
                </div>

                {/* Catalog Quick Selector */}
                <div className="part-selector-box">
                  <div className="selector-title">Select Part from Showroom Store Catalog:</div>
                  <div className="selector-row">
                    <div className="form-field flex-2">
                      <div className="search-input-wrapper">
                        <Search size={16} className="search-icon-inside" />
                        <input 
                          type="text" 
                          placeholder="Type Part Name (e.g. Filter, Oil, Clutch) or Part No (e.g. SW-744...)..." 
                          value={catalogSearch}
                          onChange={e => setCatalogSearch(e.target.value)}
                        />
                      </div>
                      
                      <select 
                        className="catalog-dropdown"
                        value={selectedCatalogPartId}
                        onChange={e => setSelectedCatalogPartId(e.target.value)}
                      >
                        <option value="">-- Select from {filteredCatalog.length} Matching Catalog Parts --</option>
                        {filteredCatalog.map(item => (
                          <option key={item.id} value={item.id}>
                            [{item.partNumber}] {item.partName} - ₹{item.unitPrice} (Stock: {item.stockQty} {item.unit})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="form-field flex-short">
                      <label>Qty</label>
                      <input 
                        type="number" 
                        min="1" 
                        value={partQtyInput}
                        onChange={e => setPartQtyInput(e.target.value)}
                      />
                    </div>

                    <button 
                      type="button" 
                      className="btn btn-primary btn-add-part"
                      onClick={handleAddCatalogPart}
                      disabled={!selectedCatalogPartId}
                    >
                      <Plus size={16} /> Add Used Part
                    </button>
                  </div>
                </div>

                {/* Used Parts Table */}
                {usedParts.length === 0 ? (
                  <div className="empty-sub-state">
                    <AlertCircle size={24} />
                    <span>No used parts added yet. Select a part above to add to this job card.</span>
                  </div>
                ) : (
                  <div className="table-responsive">
                    <table className="custom-table">
                      <thead>
                        <tr>
                          <th>Part Number</th>
                          <th>Part Name</th>
                          <th>Category</th>
                          <th>Qty</th>
                          <th>Unit Price (₹)</th>
                          <th>GST %</th>
                          <th>Line Total (Inc. Tax)</th>
                          <th className="text-center">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {usedParts.map((part) => {
                          const base = part.quantity * part.unitPrice;
                          const tax = base * (part.gstRate / 100);
                          const total = base + tax;

                          return (
                            <tr key={part.id}>
                              <td>
                                <span className="part-code-badge">{part.partNumber}</span>
                              </td>
                              <td className="font-semibold">{part.partName}</td>
                              <td><span className="category-pill">{part.category}</span></td>
                              <td>
                                <input 
                                  type="number" 
                                  min="1" 
                                  className="table-qty-input"
                                  value={part.quantity}
                                  onChange={e => handleUpdateUsedPartQty(part.id, e.target.value)}
                                />
                              </td>
                              <td>{formatCurrency(part.unitPrice)}</td>
                              <td>{part.gstRate}%</td>
                              <td className="font-bold text-red">{formatCurrency(total)}</td>
                              <td className="text-center">
                                <button 
                                  type="button" 
                                  className="btn-danger-icon"
                                  onClick={() => handleRemoveUsedPart(part.id)}
                                >
                                  <Trash2 size={16} />
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Add Custom Part Collapsible */}
                <div className="custom-part-accordion">
                  <h4>Can't find part in catalog? Add custom used part manually:</h4>
                  <div className="custom-part-row">
                    <input 
                      type="text" 
                      placeholder="Part Number (e.g. SW-CUST-01)"
                      value={customPartNumber}
                      onChange={e => setCustomPartNumber(e.target.value)}
                    />
                    <input 
                      type="text" 
                      placeholder="Part Name (e.g. Custom O-Ring Washer)"
                      value={customPartName}
                      onChange={e => setCustomPartName(e.target.value)}
                    />
                    <input 
                      type="number" 
                      placeholder="Unit Price ₹"
                      value={customUnitPrice}
                      onChange={e => setCustomUnitPrice(e.target.value)}
                    />
                    <select value={customGstRate} onChange={e => setCustomGstRate(e.target.value)}>
                      <option value="18">GST 18%</option>
                      <option value="28">GST 28%</option>
                      <option value="12">GST 12%</option>
                      <option value="0">GST 0%</option>
                    </select>
                    <button type="button" className="btn btn-secondary" onClick={handleAddCustomUsedPart}>
                      <Plus size={15} /> Add Custom
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: REMAINING & RETURNED PARTS ENTRY */}
            {activeTab === 'REMAINING_PARTS' && (
              <div className="form-section-box">
                <div className="section-header-row">
                  <div>
                    <h3><Package size={18} /> Remaining Parts & Returned Items Log</h3>
                    <p className="section-desc">
                      Track unused remaining parts returned to showroom store OR old worn parts handed over to customer.
                    </p>
                  </div>
                </div>

                {/* Add Remaining Part Form */}
                <div className="add-remaining-card">
                  <h4>Log a Remaining or Replaced Worn Part</h4>
                  <div className="form-row">
                    <div className="form-field">
                      <label>Part Number</label>
                      <input 
                        type="text" 
                        placeholder="Part No (e.g. SW-744-EF12-OLD)"
                        value={remPartNumber}
                        onChange={e => setRemPartNumber(e.target.value)}
                      />
                    </div>
                    <div className="form-field flex-2">
                      <label>Part Name / Item Description *</label>
                      <input 
                        type="text" 
                        placeholder="e.g. Unused 1L Oil Balance / Old Clutch Disc"
                        value={remPartName}
                        onChange={e => setRemPartName(e.target.value)}
                      />
                    </div>
                    <div className="form-field flex-short">
                      <label>Qty</label>
                      <input 
                        type="number" 
                        min="1"
                        value={remQty}
                        onChange={e => setRemQty(e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-field">
                      <label>Disposition / Status</label>
                      <select value={remDisposition} onChange={e => setRemDisposition(e.target.value)}>
                        <option value="Returned to Showroom Inventory">Returned to Showroom Store Stock</option>
                        <option value="Handed over to Customer">Handed Over to Customer</option>
                        <option value="Retained for Scrap Inspection">Retained in Workshop Scrap</option>
                        <option value="Sent for Warranty Claim">Sent to Company for Warranty Claim</option>
                      </select>
                    </div>

                    <div className="form-field flex-2">
                      <label>Technician Notes / Reason</label>
                      <input 
                        type="text" 
                        placeholder="e.g. Balance oil added back to store / Old worn part handed in scrap box"
                        value={remNotes}
                        onChange={e => setRemNotes(e.target.value)}
                      />
                    </div>

                    <div className="form-field align-end">
                      <button type="button" className="btn btn-secondary" onClick={handleAddRemainingPart}>
                        <Plus size={16} /> Log Remaining Part
                      </button>
                    </div>
                  </div>
                </div>

                {/* Remaining Parts Table */}
                {remainingParts.length === 0 ? (
                  <div className="empty-sub-state">
                    <Package size={24} />
                    <span>No remaining/returned parts logged for this job card yet.</span>
                  </div>
                ) : (
                  <div className="table-responsive">
                    <table className="custom-table">
                      <thead>
                        <tr>
                          <th>Part No</th>
                          <th>Part Description</th>
                          <th>Qty</th>
                          <th>Disposition</th>
                          <th>Technician Remarks</th>
                          <th className="text-center">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {remainingParts.map((item) => (
                          <tr key={item.id}>
                            <td><span className="part-code-badge">{item.partNumber}</span></td>
                            <td className="font-semibold">{item.partName}</td>
                            <td>{item.quantity} {item.unit || 'Pc'}</td>
                            <td>
                              <span className={`disposition-pill ${item.disposition?.includes('Inventory') ? 'disp-inventory' : 'disp-customer'}`}>
                                {item.disposition}
                              </span>
                            </td>
                            <td className="text-muted">{item.notes}</td>
                            <td className="text-center">
                              <button 
                                type="button" 
                                className="btn-danger-icon"
                                onClick={() => handleRemoveRemainingPart(item.id)}
                              >
                                <Trash2 size={16} />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* TAB 4: LABOR & BILLING TOTAL */}
            {activeTab === 'LABOR_BILLING' && (
              <div className="form-section-grid">
                <div className="form-group-box flex-2">
                  <h3><Wrench size={16} /> Workshop Labor & Service Operations</h3>
                  <div className="add-labor-row">
                    <input 
                      type="text" 
                      placeholder="Labor Description (e.g. Engine Overhaul, Washing & Greasing...)"
                      value={laborDesc}
                      onChange={e => setLaborDesc(e.target.value)}
                    />
                    <input 
                      type="number" 
                      placeholder="Amount ₹"
                      value={laborAmount}
                      onChange={e => setLaborAmount(e.target.value)}
                    />
                    <button type="button" className="btn btn-secondary" onClick={handleAddLabor}>
                      <Plus size={16} /> Add Labor
                    </button>
                  </div>

                  <ul className="labor-list">
                    {laborCharges.map((item) => (
                      <li key={item.id} className="labor-item">
                        <span>{item.description}</span>
                        <div className="labor-right">
                          <span className="font-bold">{formatCurrency(item.amount)}</span>
                          <button type="button" onClick={() => handleRemoveLabor(item.id)}>×</button>
                        </div>
                      </li>
                    ))}
                  </ul>

                  <div className="form-field margin-top-md">
                    <label>Workshop Technician Final Remarks / Notes</label>
                    <textarea 
                      rows="3" 
                      placeholder="Enter final test run notes, recommendations for next service..."
                      value={notes}
                      onChange={e => setNotes(e.target.value)}
                    ></textarea>
                  </div>
                </div>

                {/* Financial Summary Card */}
                <div className="billing-summary-card">
                  <h3>Bill Summary & Calculation</h3>
                  <div className="summary-line">
                    <span>Used Parts Base Total:</span>
                    <span>{formatCurrency(totals.partsTotal)}</span>
                  </div>
                  <div className="summary-line text-muted">
                    <span>GST Output Tax (CGST + SGST):</span>
                    <span>{formatCurrency(totals.partsTaxTotal)}</span>
                  </div>
                  <div className="summary-line">
                    <span>Labor Charges Total:</span>
                    <span>{formatCurrency(totals.laborTotal)}</span>
                  </div>

                  <hr className="summary-divider" />

                  <div className="form-field discount-field">
                    <label>Special Discount (₹)</label>
                    <input 
                      type="number" 
                      min="0"
                      value={discount}
                      onChange={e => setDiscount(e.target.value)}
                    />
                  </div>

                  <div className="summary-grand-total">
                    <span>Net Amount Payable:</span>
                    <span className="grand-price">{formatCurrency(totals.grandTotal)}</span>
                  </div>

                  <div className="form-field margin-top-md">
                    <label>Payment Payout Status</label>
                    <select value={paymentStatus} onChange={e => setPaymentStatus(e.target.value)}>
                      <option value="Unpaid">Unpaid / Payment Pending</option>
                      <option value="Paid (Cash)">Paid via Cash</option>
                      <option value="Paid (UPI)">Paid via UPI / PhonePe / GPay</option>
                      <option value="Paid (Card)">Paid via Card</option>
                      <option value="Paid (Bank Transfer)">Paid via Bank Transfer</option>
                    </select>
                  </div>

                  <div className="form-field margin-top-sm">
                    <label>Job Card Workflow Status</label>
                    <select value={status} onChange={e => setStatus(e.target.value)}>
                      <option value="In Service">In Service (Workshop)</option>
                      <option value="Ready for Delivery">Ready for Delivery</option>
                      <option value="Delivered">Delivered & Closed</option>
                      <option value="Open">Open / Pending Inspection</option>
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="modal-footer">
            <div className="footer-left">
              <span className="footer-live-total">
                Grand Total: <strong>{formatCurrency(totals.grandTotal)}</strong>
              </span>
            </div>
            <div className="footer-right">
              <button type="button" className="btn btn-ghost" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary btn-save">
                <Check size={18} /> {editingJobCard ? 'Update Job Card' : 'Save & Issue Job Card'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
