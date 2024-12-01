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
   
        <div v-if="isJobFormVisible">
          <h2>Add Job Description</h2>
          <form @submit.prevent="submitJobDescription">
            <div class="form-group">
              <label for="job-title">Job Title</label>
              <input type="text" id="job-title" v-model="jobTitle" placeholder="Enter job title" required />
            </div>
            <div class="form-group">
              <label for="job-description">Job Description</label>
              <textarea id="job-description" v-model="jobDescription" placeholder="Enter job description" required></textarea>
            </div>
            <button type="submit">Submit Job Description</button>
          </form>
        </div>

        <div v-if="isShortlistVisible">
          <h3>Apply Filters</h3>
 
          <div class="filter-chips">
            <span v-for="filter in selectedFilters" :key="filter" class="chip">
              {{ filter }} <button @click="removeFilter(filter)">x</button>
            </span>
          </div>

          <div class="filter-options">
            <label class="filter-option" v-for="option in filterOptions" :key="option.name">
              <input type="checkbox" :value="option.name" v-model="selectedFilters" />
              <i :class="option.icon"></i> {{ option.name }}
            </label>
          </div>

          <div v-if="selectedFilters.includes('10th')">
            <label for="10th-score">10th Percentage:</label>
            <input type="number" v-model="filter10th" placeholder="Enter 10th percentage" />
          </div>

          <div v-if="selectedFilters.includes('12th')">
            <label for="12th-score">12th Percentage:</label>
            <input type="number" v-model="filter12th" placeholder="Enter 12th percentage" />
          </div>

          <div v-if="selectedFilters.includes('CGPA')">
            <label for="cgpa">CGPA:</label>
            <input type="number" v-model="filterCGPA" placeholder="Enter CGPA" />
          </div>

          <div v-if="selectedFilters.includes('Skills')">
            <label for="skills">Skills (comma separated):</label>
            <input type="text" v-model="filterSkills" placeholder="Enter skills" />
          </div>

          <button @click="applyFilters">Apply Filters</button>
        </div>


        <div v-if="isShortlistVisible && shortlistedResumes.length > 0">
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
              <tr v-for="(resume, index) in filteredResumes" :key="resume.id">
                <td>{{ index + 1 }}</td>
                <td>{{ resume.name }}</td>
                <td><button @click="downloadResume(resume.fileUrl)">Download Resume</button></td>
              </tr>
            </tbody>
          </table>
        </div>

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
      isShortlistVisible: false,
      isRankingTableVisible: false,
      jobTitle: '',
      jobDescription: '',
      resumes: [],
      rankedStudents: [],
      shortlistedResumes: [],
      selectedFilters: [],
      filterOptions: [
        { name: '10th', icon: 'fa fa-graduation-cap' },
        { name: '12th', icon: 'fa fa-graduation-cap' },
        { name: 'CGPA', icon: 'fa fa-trophy' },
        { name: 'Skills', icon: 'fa fa-cogs' }
      ],
      filter10th: '',
      filter12th: '',
      filterCGPA: '',
      filterSkills: '',
      filteredResumes: []
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
      this.isShortlistVisible = false;
      this.isRankingTableVisible = false;
    },
    shortlistCandidates() {
      this.isJobFormVisible = false;
      this.isRankingTableVisible = false;
      this.isShortlistVisible = true;
      this.shortlistedResumes = [
        { id: 1, name: 'John Doe', fileUrl: '/path/to/resume1.pdf' },
        { id: 2, name: 'Jane Smith', fileUrl: '/path/to/resume2.pdf' },
        { id: 3, name: 'Michael Johnson', fileUrl: '/path/to/resume3.pdf' },
      ];
      this.filteredResumes = [...this.shortlistedResumes];
    },
    fetchRankingTable() {
      this.isJobFormVisible = false;
      this.isShortlistVisible = false;
      this.isRankingTableVisible = true;
      this.rankedStudents = [
        { id: 1, name: 'Student 1', cgpa: 8.5, experience: 2, skills: ['Java', 'Python'], achievements: 'Hackathon Winner', fileUrl: '/path/to/resume1.pdf' },
        { id: 2, name: 'Student 2', cgpa: 9.1, experience: 1, skills: ['React', 'Node.js'], achievements: 'AWS Certification', fileUrl: '/path/to/resume2.pdf' },
        { id: 3, name: 'Student 3', cgpa: 8.8, experience: 1, skills: ['C++', 'Django'], achievements: 'Top 10 in Coding Contest', fileUrl: '/path/to/resume3.pdf' },
      ];
    },
    submitJobDescription() {
      console.log('Job Description Submitted:', this.jobTitle, this.jobDescription);
      this.jobTitle = '';
      this.jobDescription = '';
    },
    applyFilters() {
      this.filteredResumes = this.shortlistedResumes.filter(resume => {
        let match = true;
        if (this.selectedFilters.includes('10th') && this.filter10th) {
          match = match && resume['10th'] >= this.filter10th;
        }
        if (this.selectedFilters.includes('12th') && this.filter12th) {
          match = match && resume['12th'] >= this.filter12th;
        }
        if (this.selectedFilters.includes('CGPA') && this.filterCGPA) {
          match = match && resume['CGPA'] >= this.filterCGPA;
        }
        if (this.selectedFilters.includes('Skills') && this.filterSkills) {
          match = match && resume['skills'].includes(this.filterSkills);
        }
        return match;
      });
    },
    removeFilter(filter) {
      const index = this.selectedFilters.indexOf(filter);
      if (index !== -1) {
        this.selectedFilters.splice(index, 1);
      }
    },
    downloadResume(fileUrl) {
      window.location.href = fileUrl;
    }
  }
};
</script>

<style scoped>
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

.filter-chips {
  margin-bottom: 10px;
}

.chip {
  display: inline-block;
  background-color: #3f51b5;
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  margin-right: 5px;
}

.chip button {
  background-color: transparent;
  color: white;
  border: none;
  cursor: pointer;
}

.filter-options {
  margin-bottom: 20px;
}

.filter-option {
  display: flex;
  align-items: center;
}

.filter-option input {
  margin-right: 10px;
}

.filter-option i {
  margin-right: 5px;
}
</style>