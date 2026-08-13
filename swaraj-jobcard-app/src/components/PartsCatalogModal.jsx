import React, { useState } from 'react';
import { X, Search, Package, Plus, Trash2, Edit2, Check, AlertTriangle } from 'lucide-react';
import { formatCurrency } from '../utils/formatters';

export const PartsCatalogModal = ({ isOpen, onClose, catalog, onSaveCatalog }) => {
  if (!isOpen) return null;

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  // New Part Form State
  const [showAddForm, setShowAddForm] = useState(false);
  const [newPartNumber, setNewPartNumber] = useState('');
  const [newPartName, setNewPartName] = useState('');
  const [newCategory, setNewCategory] = useState('Filters & Lubricants');
  const [newUnitPrice, setNewUnitPrice] = useState('');
  const [newGstRate, setNewGstRate] = useState(18);
  const [newStockQty, setNewStockQty] = useState(10);
  const [newUnit, setNewUnit] = useState('Pc');

  // Categories list
  const categories = ['ALL', 'Filters & Lubricants', 'Engine Parts', 'Clutch & Transmission', 'Brakes & Axle', 'Hydraulics', 'Electrical', 'Cooling & Radiator', 'Steering & Suspension'];

  const filteredParts = catalog.filter(part => {
    const matchesCat = selectedCategory === 'ALL' || part.category === selectedCategory;
    const q = searchTerm.toLowerCase().trim();
    if (!q) return matchesCat;

    const matchesSearch = 
      part.partNumber.toLowerCase().includes(q) ||
      part.partName.toLowerCase().includes(q) ||
      (part.compatibleModels && part.compatibleModels.some(m => m.toLowerCase().includes(q)));

    return matchesCat && matchesSearch;
  });

  const handleAddPart = (e) => {
    e.preventDefault();
    if (!newPartNumber.trim() || !newPartName.trim() || !newUnitPrice) {
      alert('Please fill out Part Number, Part Name, and Unit Price.');
      return;
    }

    const newItem = {
      id: `PART-${Date.now()}`,
      partNumber: newPartNumber.trim().toUpperCase(),
      partName: newPartName.trim(),
      category: newCategory,
      unitPrice: Number(newUnitPrice) || 0,
      gstRate: Number(newGstRate) || 18,
      stockQty: Number(newStockQty) || 0,
      unit: newUnit,
      compatibleModels: ["All Swaraj Models"]
    };

    onSaveCatalog([...catalog, newItem]);
    setNewPartNumber('');
    setNewPartName('');
    setNewUnitPrice('');
    setNewStockQty(10);
    setShowAddForm(false);
  };

  const handleStockUpdate = (id, delta) => {
    const updated = catalog.map(p => {
      if (p.id === id) {
        return { ...p, stockQty: Math.max(0, p.stockQty + delta) };
      }
      return p;
    });
    onSaveCatalog(updated);
  };

  const handleDeletePart = (id) => {
    if (window.confirm('Are you sure you want to delete this part from the showroom catalog?')) {
      onSaveCatalog(catalog.filter(p => p.id !== id));
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-container modal-large">
        <div className="modal-header">
          <div className="header-title">
            <Package size={24} className="icon-red" />
            <div>
              <h2>Swaraj Genuine Spare Parts Catalog</h2>
              <span className="subtitle">Showroom Store Inventory ({catalog.length} Total Items)</span>
            </div>
          </div>
          <div className="header-actions">
            <button className="btn btn-primary" onClick={() => setShowAddForm(!showAddForm)}>
              <Plus size={16} /> {showAddForm ? 'Close Add Form' : 'Add New Part to Catalog'}
            </button>
            <button className="close-btn" onClick={onClose}><X size={20} /></button>
          </div>
        </div>

        <div className="modal-body">
          {/* Add Part Form */}
          {showAddForm && (
            <form onSubmit={handleAddPart} className="add-part-card-form">
              <h3><Plus size={18} /> Register New Genuine Part in Catalog</h3>
              <div className="form-row">
                <div className="form-field">
                  <label>Part Number *</label>
                  <input 
                    type="text" 
                    required 
                    placeholder="e.g. SW-744-EF99"
                    value={newPartNumber}
                    onChange={e => setNewPartNumber(e.target.value)}
                  />
                </div>
                <div className="form-field flex-2">
                  <label>Part Name *</label>
                  <input 
                    type="text" 
                    required 
                    placeholder="e.g. Hydraulic Valve Seal Kit"
                    value={newPartName}
                    onChange={e => setNewPartName(e.target.value)}
                  />
                </div>
                <div className="form-field">
                  <label>Category</label>
                  <select value={newCategory} onChange={e => setNewCategory(e.target.value)}>
                    {categories.filter(c => c !== 'ALL').map((cat, i) => (
                      <option key={i} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label>Unit Price ₹ (Excl. Tax)</label>
                  <input 
                    type="number" 
                    required 
                    placeholder="MRP Price ₹"
                    value={newUnitPrice}
                    onChange={e => setNewUnitPrice(e.target.value)}
                  />
                </div>
                <div className="form-field">
                  <label>GST Rate %</label>
                  <select value={newGstRate} onChange={e => setNewGstRate(e.target.value)}>
                    <option value="18">18% GST</option>
                    <option value="28">28% GST</option>
                    <option value="12">12% GST</option>
                    <option value="0">0% GST</option>
                  </select>
                </div>
                <div className="form-field">
                  <label>Initial Stock Qty</label>
                  <input 
                    type="number" 
                    value={newStockQty}
                    onChange={e => setNewStockQty(e.target.value)}
                  />
                </div>
                <div className="form-field">
                  <label>Unit</label>
                  <select value={newUnit} onChange={e => setNewUnit(e.target.value)}>
                    <option value="Pc">Pc</option>
                    <option value="Set">Set</option>
                    <option value="Kit">Kit</option>
                    <option value="Can">Can</option>
                    <option value="Ltr">Ltr</option>
                    <option value="Pair">Pair</option>
                  </select>
                </div>
                <div className="form-field align-end">
                  <button type="submit" className="btn btn-primary">
                    <Check size={16} /> Save to Catalog
                  </button>
                </div>
              </div>
            </form>
          )}

          {/* Search & Category Filter */}
          <div className="filter-bar">
            <div className="search-box">
              <Search size={18} className="search-icon" />
              <input 
                type="text" 
                placeholder="Search by Part Name or Part Number..." 
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="category-select-wrapper">
              <label>Filter Category:</label>
              <select value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)}>
                {categories.map((c, i) => (
                  <option key={i} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Parts Grid / Table */}
          <div className="table-responsive margin-top-md">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Part Number</th>
                  <th>Part Name</th>
                  <th>Category</th>
                  <th>Unit Price (₹)</th>
                  <th>GST Rate</th>
                  <th>Stock Inventory</th>
                  <th className="text-center">Stock Control</th>
                  <th className="text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredParts.map(part => {
                  const isLowStock = part.stockQty < 10;
                  return (
                    <tr key={part.id}>
                      <td><span className="part-code-badge">{part.partNumber}</span></td>
                      <td className="font-semibold">{part.partName}</td>
                      <td><span className="category-pill">{part.category}</span></td>
                      <td className="font-bold">{formatCurrency(part.unitPrice)}</td>
                      <td>{part.gstRate}%</td>
                      <td>
                        <span className={`stock-badge ${isLowStock ? 'stock-low' : 'stock-ok'}`}>
                          {isLowStock && <AlertTriangle size={12} />}
                          {part.stockQty} {part.unit || 'Pcs'}
                        </span>
                      </td>
                      <td className="text-center">
                        <div className="stock-btn-group">
                          <button className="btn-qty-adj" onClick={() => handleStockUpdate(part.id, -1)}>-</button>
                          <span>{part.stockQty}</span>
                          <button className="btn-qty-adj" onClick={() => handleStockUpdate(part.id, +1)}>+</button>
                        </div>
                      </td>
                      <td className="text-center">
                        <button className="btn-danger-icon" onClick={() => handleDeletePart(part.id)}>
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-primary" onClick={onClose}>Done</button>
        </div>
      </div>
    </div>
  );
};
