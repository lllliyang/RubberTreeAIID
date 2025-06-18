<template>
  <div class="input-data-container">
    <h1 class="title">Rubber Tree Information Management</h1>

    <!-- Query Tree Information -->
    <div class="input-group">
      <label for="treeId">Enter Rubber Tree ID:</label>
      <input type="text" v-model="inputId" placeholder="Enter Tree ID" class="input-field" />
      <button @click="fetchData" class="btn">Search</button>
    </div>

    <!-- Upload and Download Excel File -->
    <div class="upload-download-row">
      <label for="uploadExcel" class="upload-btn">
        📤 Upload Excel
      </label>
      <input
        id="uploadExcel"
        type="file"
        @change="handleFileUpload"
        accept=".xlsx, .xls"
        class="file-input"
      />
      <button @click="downloadFile" class="btn download-btn">📥 Download Template</button>
    </div>

    <!-- Display and Edit Tree Data -->
    <div v-if="treeData" class="form-container">
      <form @submit.prevent="submitData">
        <div class="form-grid">
          <div
            class="form-group"
            v-for="(value, key) in displayableFormData"
            :key="key"
          >
            <label :for="key">{{ formatLabel(key) }}:</label>
            <input
              v-if="isEditable(key)"
              type="text"
              v-model="formData[key]"
              class="input-field"
            />
            <input
              v-else
              type="text"
              :value="formData[key]"
              class="input-field read-only"
              readonly
            />
          </div>
        </div>
        <button type="submit" class="btn submit-btn">Submit Changes</button>
      </form>
    </div>
  </div>
</template>

<script>
import * as XLSX from 'xlsx';

export default {
  data() {
    return {
      inputId: null,
      treeData: null,
      formData: {
        id: '',
        longitude: '',
        latitude: '',
        elevation: '',
        tree_height: '',
        crown_diameter: '',
        cross_section_area: '',
        crown_area: '',
        qrcode: '',
        variety_name: '',
        rights_holder: '',
        variety_right_number: '',
        breeder: '',
        variety_origin: '',
        suitable_region: '',
        budding_date: '',
        planter_unit: '',
        planting_date: ''
      }
    };
  },
  computed: {
    displayableFormData() {
      const hiddenFields = [
        'image_name',
        'created_at',
        'tree_id',
        'authorization_date'
      ];
      return Object.keys(this.formData)
        .filter(key => !hiddenFields.includes(key))
        .reduce((obj, key) => {
          obj[key] = this.formData[key];
          return obj;
        }, {});
    }
  },
  methods: {
    isEditable(key) {
      const readOnlyFields = [
        'id', 'qrcode', 'variety_name', 'rights_holder',
        'variety_right_number', 'breeder', 'variety_origin',
        'suitable_region', 'budding_date', 'planter_unit', 'planting_date'
      ];
      return !readOnlyFields.includes(key);
    },

    async fetchData() {
      if (!this.inputId) {
        alert('Please enter a tree ID');
        return;
      }
      try {
        const res = await fetch(`http://localhost:5000/api/get_tree_data/${this.inputId}`);
        if (!res.ok) throw new Error('Failed to fetch tree data');
        const data = await res.json();
        this.treeData = data;
        Object.keys(this.formData).forEach(key => {
          this.formData[key] = data[key] !== null ? data[key] : '';
        });
      } catch (err) {
        alert(`Error: ${err.message}`);
      }
    },

    async submitData() {
      try {
        const res = await fetch('http://localhost:5000/api/input_tree_data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.formData)
        });
        if (!res.ok) throw new Error('Submission failed');
        alert('Data submitted successfully!');
      } catch (err) {
        alert(`Error: ${err.message}`);
      }
    },

    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const worksheet = workbook.Sheets[workbook.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: '' });
        console.log('Excel Data:', jsonData);
      };
      reader.readAsArrayBuffer(file);
    },

    downloadFile() {
      const headers = Object.keys(this.displayableFormData);
      const worksheet = XLSX.utils.json_to_sheet([headers.reduce((obj, key) => (obj[key] = '', obj), {})]);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Template');
      XLSX.writeFile(workbook, 'rubber_tree_data_template.xlsx');
    },

    formatLabel(key) {
      const map = {
        id: 'Record ID',
        longitude: 'Longitude',
        latitude: 'Latitude',
        elevation: 'Elevation',
        tree_height: 'Tree Height (m)',
        crown_diameter: 'Crown Diameter (m)',
        cross_section_area: 'Cross-Section Area (m²)',
        crown_area: 'Crown Area (m²)',
        qrcode: 'QR Code',
        variety_name: 'Variety Name',
        rights_holder: 'Rights Holder',
        variety_right_number: 'Variety Right No.',
        breeder: 'Breeder',
        variety_origin: 'Variety Origin',
        suitable_region: 'Suitable Region',
        budding_date: 'Budding Date',
        planter_unit: 'Planter Unit',
        planting_date: 'Planting Date'
      };
      return map[key] || key;
    }
  }
};
</script>

<style scoped>
.input-data-container {
  padding: 30px;
  background: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  font-family: 'Segoe UI', sans-serif;
}
.title {
  color: #4a90e2;
  font-weight: 600;
  font-size: 24px;
  margin-bottom: 30px;
  text-align: center;
}
.input-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 25px;
}
.upload-download-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 25px;
}
.input-group label {
  min-width: 180px;
}
.input-field {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  width: 240px;
  font-size: 14px;
  height: 40px;
}
.read-only {
  background-color: #f0f0f0;
  color: #666;
  cursor: not-allowed;
}
.btn,
.upload-btn,
.download-btn {
  display: inline-block;
  padding: 10px 16px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  text-align: center;
  line-height: 1.2;
  height: 40px;
}
.btn:hover,
.upload-btn:hover,
.download-btn:hover {
  background-color: #357abd;
}
.file-input {
  display: none;
}
.form-container {
  margin-top: 30px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}
.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #4a90e2;
}
.submit-btn {
  margin-top: 20px;
  background-color: #4a90e2;
}
</style>