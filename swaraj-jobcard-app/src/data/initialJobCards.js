export const INITIAL_JOB_CARDS = [
  {
    id: "JC-2026-001",
    jobCardNo: "SW-JC-2026-001",
    dateInward: "2026-08-08",
    timeInward: "09:30 AM",
    expectedDelivery: "2026-08-10",
    customerName: "Ramesh Bhai Patel",
    customerPhone: "9876543210",
    customerVillage: "Anand, Kheda",
    customerAddress: "Plot 42, Farm Road, Anand",
    tractorModel: "Swaraj 744 FE (48 HP)",
    regNo: "GJ-23-AB-4589",
    chassisNo: "MA1S744FEK01982",
    engineNo: "E744FE89123",
    meterReading: "1240 HR",
    serviceType: "Paid Major 1000 HR Service",
    technician: "Vikram Sharma (Hydraulics Specialist)",
    status: "In Service",
    customerComplaints: [
      "Hydraulic lift slow during heavy cultivator usage",
      "Engine oil change and filter replacement required",
      "Brake pedal play excessive"
    ],
    usedParts: [
      {
        id: "UP-101",
        partNumber: "SW-744-EF12",
        partName: "Engine Oil Filter Assembly",
        category: "Filters & Lubricants",
        quantity: 1,
        unitPrice: 450,
        gstRate: 18,
        unit: "Pc"
      },
      {
        id: "UP-102",
        partNumber: "SW-HYD-15W40",
        partName: "Swaraj Genuine Hydraulic Oil 15W-40 (7.5L)",
        category: "Filters & Lubricants",
        quantity: 1,
        unitPrice: 2400,
        gstRate: 18,
        unit: "Can"
      },
      {
        id: "UP-103",
        partNumber: "SW-FF-001",
        partName: "Dual Fuel Filter Cartridge Set",
        category: "Filters & Lubricants",
        quantity: 1,
        unitPrice: 680,
        gstRate: 18,
        unit: "Set"
      }
    ],
    remainingParts: [
      {
        id: "RP-101",
        partNumber: "SW-HYD-15W40",
        partName: "Swaraj Genuine Hydraulic Oil (Unused Balance)",
        quantity: 1,
        unit: "Ltr",
        disposition: "Returned to Showroom Inventory",
        notes: "1.5 Litre unused oil returned to store stock"
      },
      {
        id: "RP-102",
        partNumber: "SW-744-EF12-OLD",
        partName: "Used Worn Engine Oil Filter & Fuel Filters",
        quantity: 1,
        unit: "Set",
        disposition: "Handed over to Customer",
        notes: "Old replaced filters handed over in scrap box"
      }
    ],
    laborCharges: [
      { id: "L-1", description: "Engine Oil & Filter Service Labor", amount: 350 },
      { id: "L-2", description: "Hydraulic Pump Overhaul & Valve Cleaning", amount: 750 },
      { id: "L-3", description: "Brake Shoe Adjustment & Greasing", amount: 250 }
    ],
    discount: 100,
    paymentStatus: "Unpaid",
    notes: "Tractor checked post test run. Hydraulic pressure restored to 180 Bar."
  },
  {
    id: "JC-2026-002",
    jobCardNo: "SW-JC-2026-002",
    dateInward: "2026-08-09",
    timeInward: "11:00 AM",
    expectedDelivery: "2026-08-11",
    customerName: "Suresh Chaudhari",
    customerPhone: "9428177234",
    customerVillage: "Bardoli, Surat",
    customerAddress: "Sugar Factory Road, Bardoli",
    tractorModel: "Swaraj 855 FE (52 HP)",
    regNo: "GJ-19-CD-1102",
    chassisNo: "MA1S855FEK08831",
    engineNo: "E855FE99411",
    meterReading: "3450 HR",
    serviceType: "Clutch & Overhaul Repair",
    technician: "Rajesh Parmar (Transmission Tech)",
    status: "Ready for Delivery",
    customerComplaints: [
      "Clutch slipping under trolley load",
      "Noise in clutch release bearing when pedal pressed"
    ],
    usedParts: [
      {
        id: "UP-201",
        partNumber: "SW-855-CP90",
        partName: "Heavy Duty Clutch Plate 280mm",
        category: "Clutch & Transmission",
        quantity: 1,
        unitPrice: 4200,
        gstRate: 28,
        unit: "Pc"
      },
      {
        id: "UP-202",
        partNumber: "SW-CRB-001",
        partName: "Clutch Release Bearing Heavy Duty",
        category: "Clutch & Transmission",
        quantity: 1,
        unitPrice: 850,
        gstRate: 18,
        unit: "Pc"
      }
    ],
    remainingParts: [
      {
        id: "RP-201",
        partNumber: "SW-855-CP90-OLD",
        partName: "Old Worn Out Clutch Plate Disc",
        quantity: 1,
        unit: "Pc",
        disposition: "Handed over to Customer",
        notes: "Old burnt clutch plate handed back to customer"
      }
    ],
    laborCharges: [
      { id: "L-201", description: "Clutch Housing Separation & Installation", amount: 1800 }
    ],
    discount: 200,
    paymentStatus: "Paid (UPI)",
    notes: "New clutch plate installed. Free pedal play set to 25mm."
  }
];
