# CODEBASE MAP

> Tự động sinh bởi script `scripts/update_map.py`.

```text
pharmacy_ai_system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── ai.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── batches.py
│   │   │   │   ├── categories.py
│   │   │   │   ├── invoices.py
│   │   │   │   ├── medicines.py
│   │   │   │   └── suppliers.py
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   └── inventory_service.py
│   │   └── main.py
│   ├── uploads/
│   │   └── medicines/
│   ├── .env.example
│   ├── pharmacy.db
│   └── requirements.txt
├── docs/
│   ├── ai_collaboration_log_phase1.md
│   └── system_analysis_and_design.md
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── views/
│   │   │   ├── AIChat.vue
│   │   │   ├── Batches.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── Invoices.vue
│   │   │   ├── Login.vue
│   │   │   ├── Medicines.vue
│   │   │   ├── POS.vue
│   │   │   └── Suppliers.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   └── update_map.py
├── .geminirules
├── .gitignore
├── architecture.md
├── README.md
└── user_stories.md
```
