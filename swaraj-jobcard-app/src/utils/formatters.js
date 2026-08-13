export const formatCurrency = (amount) => {
  const num = Number(amount) || 0;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
    minimumFractionDigits: 0
  }).format(num);
};

export const calculateJobCardTotals = (jobCard) => {
  if (!jobCard) return { partsTotal: 0, partsTaxTotal: 0, laborTotal: 0, subTotal: 0, discount: 0, grandTotal: 0 };

  let partsTotal = 0;
  let partsTaxTotal = 0;

  (jobCard.usedParts || []).forEach(part => {
    const qty = Number(part.quantity) || 0;
    const price = Number(part.unitPrice) || 0;
    const gst = Number(part.gstRate) || 0;

    const baseAmount = qty * price;
    const taxAmount = baseAmount * (gst / 100);

    partsTotal += baseAmount;
    partsTaxTotal += taxAmount;
  });

  const laborTotal = (jobCard.laborCharges || []).reduce((acc, curr) => acc + (Number(curr.amount) || 0), 0);

  const discount = Number(jobCard.discount) || 0;
  const subTotal = partsTotal + laborTotal;
  const grandTotal = Math.max(0, subTotal + partsTaxTotal - discount);

  return {
    partsTotal,
    partsTaxTotal,
    laborTotal,
    subTotal,
    discount,
    grandTotal,
    cgst: partsTaxTotal / 2,
    sgst: partsTaxTotal / 2
  };
};

export const formatDate = (dateStr) => {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch (e) {
    return dateStr;
  }
};
