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
      <!-- Sidebar -->
      <div class="sidebar">
        <a @click="showAddJobForm">Add Job Description</a>
        <a @click="shortlistCandidates">Shortlist Candidates</a>
        <a @click="fetchRankingTable">Ranking Table</a>
      </div>

      <!-- Main Content Area -->
      <div class="main-content">
        <!-- Add Job Form -->
        <div v-if="isJobFormVisible">
          <h2>Add Job Description</h2>
          <form @submit.prevent="submitJobDescription">
            <div class="form-group">
              <label for="job-title">Job Title:</label>
              <input type="text" id="job-title" v-model="jobTitle" required />
            </div>
            <div class="form-group">
              <label for="job-description">Job Description:</label>
              <textarea id="job-description" v-model="jobDescription" required></textarea>
            </div>
            <div class="form-group">
        <label for="num-candidates">Number of Candidates to Shortlist:</label>
        <input type="number" id="num-candidates" v-model="numCandidates" required min="1" />
         </div>

            <button type="submit">Add Job</button>
          </form>
        </div>

        <!-- Shortlist Candidates Section -->
        <div v-if="isShortlistVisible">
          <h2>Shortlist Candidates</h2>
          <table>
            <thead>
              <tr>
                <th>Sr. No</th>
                <th>Name</th>
                <th>Download Resume</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(resume, index) in shortlistedResumes" :key="resume.id">
                <td>{{ index + 1 }}</td>
                <td>{{ resume.name }}</td>
                <td><button @click="downloadResume(resume.fileUrl)">Download Resume</button></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Ranking Table Section -->
        <div v-if="isRankingTableVisible">
          <h2>Ranking Table</h2>
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Name</th>
                <th>CGPA</th>
                <th>Experience (Years)</th>
                <th>Skills</th>
                <th>Achievements</th>
                <th>Download Resume</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(student, index) in rankedStudents" :key="student.id">
                <td>{{ index + 1 }}</td>
                <td>{{ student.name }}</td>
                <td>{{ student.cgpa }}</td>
                <td>{{ student.experience }}</td>
                <td>{{ student.skills.join(', ') }}</td>
                <td>{{ student.achievements }}</td>
                <td><button @click="downloadResume(student.fileUrl)">Download Resume</button></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else>
          <router-view></router-view>
        </div>
      </div>
    </div>
  </div>
</template>



<script>
export default {
  data() {
    return {
      dropdownVisible: false,
      isJobFormVisible: false,
      isResumesVisible: false,
      isRankingTableVisible: false,
      isShortlistVisible: false,
      isProfilesVisible: false,
      jobTitle: '',
      jobDescription: '',
      resumes: [], 
      rankedStudents: [], 
      shortlistedResumes: [], 
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
      
      this.isJobFormVisible = true;
      this.isResumesVisible = false;
      this.isRankingTableVisible = false;
      this.isShortlistVisible = false;
      this.isProfilesVisible = false;
    },
    shortlistCandidates() {
  this.shortlistedResumes = [
    { id: 1, name: 'John Doe', fileUrl: '/path/to/resume1.pdf' },
    { id: 2, name: 'Jane Smith', fileUrl: '/path/to/resume2.pdf' },
    { id: 3, name: 'Michael Johnson', fileUrl: '/path/to/resume3.pdf' },
  ];
  this.isShortlistVisible = true;
  this.isJobFormVisible = false;
  this.isResumesVisible = false;
  this.isRankingTableVisible = false;
  this.isProfilesVisible = false;
},

    fetchRankingTable() {
      this.isRankingTableVisible = true;
      this.isJobFormVisible = false;
      this.isShortlistVisible = false;
      this.isProfilesVisible = false;
      this.rankedStudents = [
    { id: 1, name: 'Student 1', cgpa: 8.5, experience: 2, skills: ['Java', 'Python'], achievements: 'Hackathon Winner', fileUrl: '/path/to/resume1.pdf' },
    { id: 2, name: 'Student 2', cgpa: 9.1, experience: 1, skills: ['React', 'Node.js'], achievements: 'AWS Certification', fileUrl: '/path/to/resume2.pdf' },
    { id: 3, name: 'Student 3', cgpa: 8.8, experience: 1, skills: ['C++', 'Django'], achievements: 'Top 10 in Coding Contest', fileUrl: '/path/to/resume3.pdf' },
  ];
    },
    submitJobDescription() {
      // Logic to submit job description
      alert(`Job "${this.jobTitle}" added successfully!`);
      this.jobTitle = '';
      this.jobDescription = '';
      this.isJobFormVisible = false; // Hide job form after submission
    },
    downloadResume(fileUrl) {
      // Logic to download resume
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = 'Resume.pdf';
      link.click();
      
    }
  },
};
</script>




<style scoped>
/* Same CSS as before */
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
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
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

button {
  padding: 10px 20px;
  background-color: #3f51b5;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #2c3e99;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

table, th, td {
  border: 1px solid #ddd;
}

th, td {
  padding: 10px;
  text-align: left;
}

th {
  background-color: #f4f4f4;
}
</style>
