<template>
  <div>
    <h2>Add Job Description</h2>
    <form @submit.prevent="submitJobDescription">
      <div class="form-group">
        <label for="jobTitle">Job Title:</label>
        <input
          type="text"
          id="jobTitle"
          v-model="jobTitle"
          placeholder="Enter job title"
          required
        />
      </div>
      <div class="form-group">
        <label for="jobDescription">Job Description:</label>
        <textarea
          id="jobDescription"
          v-model="jobDescription"
          placeholder="Enter job description"
          required
        ></textarea>
      </div>
      <button type="submit">Submit</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      jobTitle: "", // Store the job title
      jobDescription: "", // Store the job description
    };
  },
  methods: {
    async submitJobDescription() {
      if (!this.jobDescription) {
        alert("Please fill in the job description.");
        return;
      }

      const jobData = {
        job_title: this.jobTitle,        // Include job title in the data sent to the backend
        job_description: this.jobDescription, // Send job description
      };

      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/hr-skills", // FastAPI endpoint for extracting skills
          jobData,
          { headers: { "Content-Type": "application/json" } }
        );

        console.log("Server Response:", response.data);
        alert("Job description and skills extracted successfully!");

        // Clear form fields after submission
        this.jobTitle = "";
        this.jobDescription = "";
      } catch (error) {
        console.error("Error submitting job description:", error);
        alert("Failed to submit job description. Please try again.");
      }
    },
  },
};
</script>

<style scoped>
/* Styling from your initial example */
.form-group {
  margin-bottom: 15px;
}
input,
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-bottom: 10px;
  box-sizing: border-box;
}
textarea {
  resize: vertical;
}
button {
  padding: 10px 20px;
  background-color: #3f51b5;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:hover {
  background-color: #303f9f;
}
</style>
