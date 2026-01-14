import datetime



#------------------------------------------------------------------------------------------------
# INVOICE SCHEMA 
#------------------------------------------------------------------------------------------------

InvoiceSchema = {
  "invoice_id": {
    "value": "INV-2024-001",
    "confidence": 0.98,
    "source_page": 1
  },

  "invoice_date": {
    "value": "2024-03-12",
    "confidence": 0.99,
    "source_page": 1
  },

  "due_date": {
    "value": "2024-03-27",
    "confidence": 0.95,
    "source_page": 1
  },

  "seller": {
    "name": {
      "value": "ABC Pvt Ltd",
      "confidence": 0.97,
      "source_page": 1
    },
    "tax_id": {
      "value": "27ABCDE1234F1Z5",
      "confidence": 0.96,
      "source_page": 1
    }
  },

  "buyer": {
    "name": {
      "value": "XYZ Enterprises",
      "confidence": 0.97,
      "source_page": 1
    },
    "tax_id": {
      "value": "29XYZDE5678A1Z9",
      "confidence": 0.95,
      "source_page": 1
    }
  },

  "line_items": [
    {
      "description": {
        "value": "Software Subscription",
        "confidence": 0.96,
        "source_page": 2
      },
      "quantity": {
        "value": 2,
        "confidence": 0.98,
        "source_page": 2
      },
      "unit_price": {
        "value": 25000,
        "currency": "INR",
        "confidence": 0.97,
        "source_page": 2
      },
      "line_total": {
        "value": 50000,
        "currency": "INR",
        "confidence": 0.99,
        "source_page": 2
      }
    }
  ],

  "subtotal": {
    "value": 50000,
    "currency": "INR",
    "confidence": 0.99,
    "source_page": 2
  },

  "tax": {
    "value": 9000,
    "currency": "INR",
    "confidence": 0.96,
    "source_page": 2
  },

  "total_amount": {
    "value": 59000,
    "currency": "INR",
    "confidence": 0.99,
    "source_page": 2
  },

  "payment_terms": {
    "value": "Net 15",
    "confidence": 0.90,
    "source_page": 1
  }
}

#------------------------------------------------------------------------------------------------
# BANKSTATEMENT SCHEMA 
#------------------------------------------------------------------------------------------------

BankStatementSchema = {
  "account": {
    "account_number": {
      "value": "XXXX1234",
      "confidence": 0.95,
      "source_page": 1
    },
    "bank_name": {
      "value": "HDFC Bank",
      "confidence": 0.98,
      "source_page": 1
    }
  },

  "statement_period": {
    "start_date": {
      "value": "2024-03-01",
      "confidence": 0.99,
      "source_page": 1
    },
    "end_date": {
      "value": "2024-03-31",
      "confidence": 0.99,
      "source_page": 1
    }
  },

  "opening_balance": {
    "value": 150000,
    "currency": "INR",
    "confidence": 0.98,
    "source_page": 1
  },

  "transactions": [
    {
      "transaction_date": {
        "value": "2024-03-05",
        "confidence": 0.99,
        "source_page": 2
      },
      "description": {
        "value": "NEFT-INVOICE-INV-2024-001",
        "confidence": 0.96,
        "source_page": 2
      },
      "debit": {
        "value": 0,
        "currency": "INR",
        "confidence": 0.99,
        "source_page": 2
      },
      "credit": {
        "value": 59000,
        "currency": "INR",
        "confidence": 0.99,
        "source_page": 2
      },
      "balance_after": {
        "value": 209000,
        "currency": "INR",
        "confidence": 0.98,
        "source_page": 2
      }
    }
  ],

  "closing_balance": {
    "value": 209000,
    "currency": "INR",
    "confidence": 0.99,
    "source_page": 3
  }
}

#------------------------------------------------------------------------------------------------
# PANDL SCHEMA 
#------------------------------------------------------------------------------------------------

PAndLSchema = {
  "period": {
    "start_date": {
      "value": "2024-01-01",
      "confidence": 0.99,
      "source_page": 1
    },
    "end_date": {
      "value": "2024-03-31",
      "confidence": 0.99,
      "source_page": 1
    }
  },

  "revenue": {
    "value": 1200000,
    "currency": "INR",
    "confidence": 0.97,
    "source_page": 1
  },

  "expenses": [
    {
      "category": {
        "value": "Marketing",
        "confidence": 0.95,
        "source_page": 2
      },
      "amount": {
        "value": 300000,
        "currency": "INR",
        "confidence": 0.96,
        "source_page": 2
      }
    }
  ],

  "total_expenses": {
    "value": 700000,
    "currency": "INR",
    "confidence": 0.98,
    "source_page": 3
  },

  "net_profit": {
    "value": 500000,
    "currency": "INR",
    "confidence": 0.98,
    "source_page": 3
  }
}
