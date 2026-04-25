# Geofuse

## Project Structure

```text
geofuse/
├── backend/
│   ├── ingestion/
│   │   ├── gps_parser.py          ← yours ✅
│   │   ├── address_geocoder.py    ← yours ✅
│   │   ├── plus_code_converter.py ← yours ✅
│   │   └── normalizer.py          ← yours ✅
│   ├── fusion/
│   │   ├── fuser.py               ← Person B ✅
│   │   ├── outlier_detector.py    ← Person B ✅
│   │   └── weighter.py            ← Person B ✅
│   ├── risk/
│   │   ├── __init__.py            ← Person C ✅
│   │   ├── dispatch_status.py     ← Person C ✅
│   │   └── environment.py         ← Person C ✅
│   ├── main.py                    ← Person C ✅
│   ├── models.py                  ← shared ✅
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── locate.ts          ← Person D ✅
│   │   ├── components/
│   │   │   ├── InputForm.tsx      ← Person D ✅
│   │   │   ├── MapView.tsx        ← Person D ✅
│   │   │   ├── StatusBanner.tsx   ← Person D ✅
│   │   │   └── XDPanel.tsx        ← Person D ✅
│   │   ├── App.tsx                ← Person D ✅
│   │   ├── App.css
│   │   ├── main.tsx
│   │   ├── mockResponse.ts
│   │   └── types.ts
│   └── index.html
│
└── README.md
```