<template>
  <div>
    <div class="header">
      <div class="header-title">Eduplus Campus | HR MANAGER</div>
      <div class="header-right">
        <button class="profile-btn" @click="toggleDropdown">H</button>
        <div class="dropdown" v-if="dropdownVisible">
          <router-link to="/profile">Profile</router-link>
          <router-link to="/login" @click="logout">Logout</router-link>
        </div>
      </div>
    </div>

    <div class="content">
      <div class="sidebar">
        <a @click="showAddJobForm">Add Job Description</a>
        <a @click="shortlistCandidates">Shortlist Candidates</a>
        <a @click="fetchRankingTable">Ranking Table</a>
      </div>

      <div class="main-content">
        <!-- Add Job Description Form -->
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

        <!-- Display shortlisted skills -->
        <div v-if="skills.length > 0" class="skills-section">
          <h3>Shortlisted Skills:</h3>
          <ul>
            <li v-for="(skill, index) in skills" :key="index">{{ skill }}</li>
          </ul>
        </div>

        <!-- Display shortlisted candidates -->
        <div v-if="candidates.length > 0" class="shortlisted-candidates-section">
          <h3>Shortlisted Candidates</h3>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>10th Grade</th>
                <th>12th Grade</th>
                <th>CGPA</th>
                <th>Skills</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(candidate, index) in candidates" :key="index">
                <td>{{ candidate.name }}</td>
                <td>{{ candidate.tenGrade }}</td>
                <td>{{ candidate.twelveGrade }}</td>
                <td>{{ candidate.cgpa }}</td>
                <td>{{ candidate.skills.join(', ') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      jobTitle: "", // Store the job title
      jobDescription: "", // Store the job description
      skills: [], // Array to store shortlisted skills
      candidates: [], // Array to store shortlisted candidates' details
      dropdownVisible: false,
    };
  },
  methods: {
    toggleDropdown() {
      this.dropdownVisible = !this.dropdownVisible;
    },
    logout() {
      this.$router.push("/login");
    },
    showAddJobForm() {
      this.jobTitle = "";
      this.jobDescription = "";
      this.skills = []; // Clear skills when the form is reset
    },
    async submitJobDescription() {
      if (!this.jobDescription) {
        alert("Please fill in the job description.");
        return;
      }

      const jobData = {
        job_title: this.jobTitle, // Include job title in the data sent to the backend
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

        // Store extracted skills in the array
        this.skills = response.data.skills;

        // Clear form fields after submission
        this.jobTitle = "";
        this.jobDescription = "";
      } catch (error) {
        console.error("Error submitting job description:", error);
        alert("Failed to submit job description. Please try again.");
      }
    },
    shortlistCandidates() {
      // Fetch shortlisted candidates data (This can be from an API or mock data)
      const mockCandidatesData = [
        {
          name: "John Doe",
          tenGrade: "90%",
          twelveGrade: "85%",
          cgpa: "8.7",
          skills: ["Java", "Python", "Machine Learning"],
        },
        {
          name: "Jane Smith",
          tenGrade: "88%",
          twelveGrade: "80%",
          cgpa: "9.1",
          skills: ["JavaScript", "Vue.js", "React"],
        },
        {
          name: "Alex Johnson",
          tenGrade: "92%",
          twelveGrade: "89%",
          cgpa: "8.9",
          skills: ["C++", "Data Structures", "Algorithms"],
        },
      ];

      // Update candidates list
      this.candidates = mockCandidatesData;
    },
    fetchRankingTable() {
      // Implement the functionality to fetch the ranking table
    },
  },
};
</script>

<style scoped>
/* Styling from your first page */
.header {
  background-color: #3f51b5;
  color: white;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 20px;
}

.header-right {
  position: relative;
  display: inline-block;
}

.dropdown {
  position: absolute;
  background-color: #f9f9f9;
  min-width: 100px;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  z-index: 1;
  right: 0;
}

.dropdown a {
  color: black;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
}

.dropdown a:hover {
  background-color: #f1f1f1;
}

.profile-btn {
  cursor: pointer;
  background-color: #fff;
  border: none;
  padding: 10px;
  border-radius: 50%;
  font-size: 18px;
}

.content {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 200px;
  background-color: #f4f4f4;
  padding: 20px;
}

.sidebar a {
  display: block;
  padding: 10px;
  text-decoration: none;
  color: #333;
  cursor: pointer;
}

.sidebar a:hover {
  background-color: #ddd;
}

.main-content {
  flex-grow: 1;
  padding: 20px;
  background-color: white;
}

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

.skills-section {
  margin-top: 20px;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 5px;
}

.skills-section h3 {
  margin-top: 0;
}

.skills-section ul {
  list-style-type: none;
  padding-left: 0;
}

.skills-section li {
  padding: 5px;
  background-color: #e0e0e0;
  margin: 5px 0;
  border-radius: 3px;
}

.shortlisted-candidates-section {
  margin-top: 20px;
}

.shortlisted-candidates-section table {
  width: 100%;
  border-collapse: collapse;
}

.shortlisted-candidates-section th,
.shortlisted-candidates-section td {
  padding: 10px;
  text-align: left;
  border: 1px solid #ddd;
}

.shortlisted-candidates-section th {
  background-color: #f4f4f4;
}
</style>
