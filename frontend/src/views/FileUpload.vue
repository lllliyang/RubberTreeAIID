<template>
  <div class="upload-container card">
    <div class="card-body">
      <h2 class="card-title text-center">Select Files</h2>

      <!-- 文件选择部分 -->
      <div class="file-selection">
        <div class="mb-4">
          <h3>Select the DOM file</h3>
          <input type="file" class="form-control file-input" @change="handleDomFileUpload" />
        </div>
        <div class="mb-4">
          <h3>Select the DSM file</h3>
          <input type="file" class="form-control file-input" @change="handleDsmFileUpload" />
        </div>
        <button class="btn btn-primary upload-btn" @click="uploadFiles">Upload Files</button>
      </div>

      <!-- 文件上传过程中的步骤 -->
      <div v-if="isCutting" class="mt-4 cutting-steps card">
        <div class="card-body">
          <h2 class="card-title">Processing</h2>
          <ul class="list-group">
            <li v-for="(step, index) in cuttingSteps" :key="index" class="list-group-item">
              {{ step.message }} <span v-if="step.completed" class="text-success">✔️</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- 上传成功后的提示信息 -->
      <div v-if="showSuccessMessage" class="mt-4 alert alert-success">
        <h2 class="text-center">Upload Successful!</h2>
        <div class="button-group">
          <button class="btn btn-primary" @click="goToLogin">End Upload</button>
          <button class="btn btn-secondary" @click="resetUpload">Continue Uploading</button>
          <button class="btn btn-info" @click="showVisualizationDialog">Visualization</button>
          <button class="btn btn-success" @click="generateQRCode">Generate QR Code</button>
        </div>
      </div>

      <!-- 可视化对话框 -->
      <div v-if="showVisDialog" class="visualization-dialog card">
        <div class="card-body">
          <h3>Select Save Path</h3>
          <div class="mb-3">
            <label class="form-label">Save Directory:</label>
            <input type="text" class="form-control" v-model="savePath" placeholder="Please enter the save path" />
          </div>
          <div class="mb-3">
            <label class="form-label">Visualization Type:</label>
            <select class="form-select" v-model="visType">
              <option value="2d">2D Visualization</option>
              <option value="3d">3D Visualization</option>
            </select>
          </div>
          <div class="dialog-buttons">
            <button class="btn btn-primary" @click="generateVisualization">Generate</button>
            <button class="btn btn-secondary" @click="closeVisualizationDialog">Cancel</button>
          </div>
        </div>
      </div>

      <!-- 二维码显示对话框 -->
      <div v-if="showQRCode" class="qrcode-dialog card">
        <div class="card-body">
          <h3>QR Code</h3>
          <img v-if="qrcodeImage" :src="'data:image/png;base64,' + qrcodeImage" alt="QR Code" />
          <div class="dialog-buttons">
            <button class="btn btn-secondary" @click="showQRCode = false">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      domFile: null,
      dsmFile: null,
      isCutting: false,
      cuttingSteps: [],
      showSuccessMessage: false,
      showVisDialog: false,
      savePath: '',
      visType: '2d',
      showQRCode: false,
      qrcodeImage: null,
    };
  },
  methods: {
    handleDomFileUpload(event) {
      this.domFile = event.target.files[0];
    },
    handleDsmFileUpload(event) {
      this.dsmFile = event.target.files[0];
    },
    async uploadFiles() {
      if (!this.domFile || !this.dsmFile) {
        alert('Please make sure to select both DOM and DSM files!');
        return;
      }

      this.isCutting = true;
      this.cuttingSteps = [
        { message: 'Step 1: Uploading DOM...', completed: false },
        { message: 'Step 2: Uploading DSM...', completed: false },
        { message: 'Step 3: Processing...', completed: false },
      ];

      try {
        // 上传 DOM 文件
        const domForm = new FormData();
        domForm.append('domFile', this.domFile);
        await axios.post('http://localhost:5000/api/upload/dom', domForm);
        this.cuttingSteps[0].completed = true;

        // 上传 DSM 文件
        const dsmForm = new FormData();
        dsmForm.append('dsmFile', this.dsmFile);
        await axios.post('http://localhost:5000/api/upload/dsm', dsmForm);
        this.cuttingSteps[1].completed = true;

        // 后续处理流程
        await this.confirmCutting();
      } catch (error) {
        console.error('Upload failed:', error);
        alert('Upload failed. Please check the console for details.');
      }
    }
    ,
    async confirmCutting() {
      try {
        await axios.post('http://localhost:5000/api/process', {});
        this.cuttingSteps[0].completed = true;

        await axios.post('http://localhost:5000/api/detect', {});
        this.cuttingSteps[1].completed = true;

        await axios.post('http://localhost:5000/api/process_coordinates', {});
        const coordinatesData = await this.getCoordinatesData();
        await axios.post('http://localhost:5000/api/save_coordinates', coordinatesData);
        this.cuttingSteps[2].completed = true;

        this.showSuccessMessage = true;
      } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please check the console for more information.');
      } finally {
        this.isCutting = false;
      }
    },
    async getCoordinatesData() {
      return [{ lat: 12.34, lon: 56.78, elevation: 200 }];
    },
    resetUpload() {
      this.domFile = null;
      this.dsmFile = null;
      this.isCutting = false;
      this.cuttingSteps = [];
      this.showSuccessMessage = false;
    },
    showVisualizationDialog() {
      this.showVisDialog = true;
    },
    closeVisualizationDialog() {
      this.showVisDialog = false;
      this.savePath = '';
    },
    async generateVisualization() {
      if (!this.savePath) {
        alert('Please enter the save path!');
        return;
      }

      try {
        const response = await axios.post('http://localhost:5000/api/visualization/generate', {
          savePath: this.savePath,
          type: this.visType,
        });

        if (response.data.status === 'success') {
          alert('Visualization generated successfully!');
          this.closeVisualizationDialog();
        } else {
          alert('Generation failed: ' + response.data.message);
        }
      } catch (error) {
        console.error('Visualization generation failed:', error);
        alert('Generation failed, please check the console for more information.');
      }
    },
    goToLogin() {
      this.$router.push('/login');
    },
    async generateQRCode() {
      try {
        const response = await axios.post('http://localhost:5000/api/generate_qrcode');
        if (response.data.status === 'success') {
          this.$message.success('QR code generated successfully!');
          this.showQRCodeDialog(response.data.qrcode);
        } else {
          this.$message.error('Failed to generate QR code');
        }
      } catch (error) {
        console.error('Generate QR code failed:', error);
        this.$message.error('Failed to generate QR code');
      }
    },
    showQRCodeDialog(qrcodeBase64) {
      this.qrcodeImage = qrcodeBase64;
      this.showQRCode = true;
    }
  },
};
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.card-title {
  color: #4a90e2;
  font-weight: 600;
  font-size: 24px;
  margin-bottom: 30px;
  text-align: center;
}

.file-selection {
  margin-bottom: 2rem;
}

.file-input {
  margin-bottom: 1rem;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  width: 100%;
}

.upload-btn {
  width: 100%;
  padding: 12px 16px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  margin-top: 1rem;
  cursor: pointer;
}

.upload-btn:hover {
  background-color: #357abd;
}

.cutting-steps {
  margin-top: 2rem;
}

.visualization-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 400px;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  background-color: white;
}

.qrcode-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  background-color: white;
  padding: 20px;
}

.qrcode-dialog img {
  width: 100%;
  height: auto;
  margin: 20px 0;
}

.dialog-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-info {
  margin-left: 10px;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #218838;
}

.form-label {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.form-select {
  width: 100%;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
}

.button-group button {
  margin-top: 10px;
  margin-right: 10px;
}

.alert-success {
  background-color: #e8f5e9;
  border-color: #c8e6c9;
  color: #388e3c;
  padding: 1.5rem;
  text-align: center;
}
</style>