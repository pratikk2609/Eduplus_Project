<template>
    <div>
      <h2>Upload Your Resume</h2>
      <form @submit.prevent="submitResume">
        <div class="form-group">
          <label for="resume">Choose Resume File:</label>
          <input type="file" id="resume" @change="handleFileUpload" />
        </div>
        <button type="submit">Upload</button>
      </form>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        resumeFile: null,
      };
    },
    methods: {
      handleFileUpload(event) {
        this.resumeFile = event.target.files[0];
      },
      submitResume() {
        if (!this.resumeFile) {
          alert("Please select a file.");
          return;
        }

        let formData = new FormData();
        formData.append("resume", this.resumeFile);
        // axios.post('your-upload-endpoint', formData).then(response => { ... });
  
        alert("Resume uploaded successfully!");
      },
    },
  };
  </script>
  
  <style scoped>
  .form-group {
    margin-bottom: 15px;
  }
  button {
    padding: 10px 20px;
    background-color: #3f51b5;
    color: white;
    border: none;
    border-radius: 5px;
  }
  </style>
  