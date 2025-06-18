# RubberTreeAIID 🌿

**RubberTreeAIID** is an intelligent rubber plantation management system that integrates UAV-based remote sensing, advanced object detection (YOLOv11 with custom modules), geospatial coordinate extraction, and digital identity tracking via QR codes.

It provides a complete pipeline from image acquisition and processing to automated planting pit detection, geographic localization, and interactive information management through a Vue-based web interface.

---

## 🧠 Key Features

- 🔍 **High-accuracy detection** of rubber tree planting pits from UAV-derived orthophotos (DOM)
- 🌐 **Geolocation of planting pits** via affine transformation over DSM data
- 🧩 **Improved YOLOv11 model** with custom modules: `C3K2_DDF`, `SCDown`, and `iEMA`
- 🧾 **QR code generation** for individual planting pit identification and traceability
- 📊 **Web-based system** for real-time data editing, querying, and visualization
- 🗃️ **MySQL database integration** for persistent data storage and retrieval

---

## 📂 Project Structure

RubberTreeAIID/
├── backend/ # Flask backend server
│ ├── app.py # Main API entry
│ ├── config.py # Configuration settings
│ ├── input/ # Uploaded DOM/DSM files
│ ├── output/ # Detection results, coordinates, image tiles
│ ├── models/ # Model loading and inference logic
│ │ └── weights/ # Trained YOLOv11 weights (e.g., best.pt)
│ ├── utils/ # Core functional modules:
│ │ ├── inference/ # DOM tiling, image inference
│ │ ├── transform/ # Affine geolocation
│ │ ├── qrcode/ # QR-code generation and encoding
│ │ ├── database/ # MySQL interface
│ │ └── ultralytics/ # Custom YOLOv11 with Addmodule
├── frontend/ # Vue-based frontend
│ ├── src/ # Form UI, QR-code view, tree info editing
│ └── vue.config.js # Frontend config
├── requirements.txt # Python dependencies
└── README.md

yaml
Copy
Edit

---

## 🔧 Installation & Setup

### 1. Python Backend (Flask)

```bash
# Create virtual environment
conda create -n rubber_env python=3.9
conda activate rubber_env

# Install dependencies
pip install -r requirements.txt

# Launch backend server
cd backend
python app.py
Server will be running at: http://127.0.0.1:5000

2. Vue Frontend
bash
Copy
Edit
cd frontend
npm install
npm run serve
Frontend will be available at: http://localhost:8080

🧠 Model: YOLOv11 + Addmodule
This project uses a customized YOLOv11 model enhanced for small object detection and blurred-edge robustness, built with:

C3K2_DDF: Multi-scale depthwise dilated feature fusion

SCDown: Efficient downsampling block replacing standard convolution

iEMA: Improved Efficient Multi-scale Attention module

Model weight file:

bash
Copy
Edit
backend/models/weights/best.pt
Modified YOLO source located in:

bash
Copy
Edit
backend/utils/ultralytics/
🛰️ Spatial Localization
For each DOM tile with detected planting pits:

Extract pixel coordinates of bounding box centers

Match with DSM-derived pixel-to-geocoordinate mapping

Apply affine transformation to convert pixel points to EPSG:4326 (WGS84) geocoordinates

Store lat/lon/elevation in MySQL along with tree metadata

📷 Sample Workflow
css
Copy
Edit
[ UAV DOM/DSM Images ]
         ↓
[ Image Tiling (640×640) ]
         ↓
[ YOLOv11 Detection ]
         ↓
[ Affine Coordinate Extraction ]
         ↓
[ Result Saving: Detected Image + .txt + Geo CSV ]
         ↓
[ QR Code Generation ]
         ↓
[ Web Interface Visualization & Editing ]
📬 Output Format
Each detection will generate:

det_xxx.png: Annotated detection image

det_xxx.txt: Bounding box info (YOLO format)

det_xxx.csv: Geographic coordinates (lon, lat, elevation)

qrcode_xxx.png: QR code image embedding tree metadata

🛠 TODO (Roadmap)
 Integrate RTK-GNSS high-precision geolocation

 Add tree-level phenotypic traits (e.g., height, crown diameter)

 Web-based batch editing and Excel import/export

 Support for mobile-side QR scan entry

📄 License
This project is released under an academic use license.
For commercial licensing or collaboration inquiries, please contact the author.
