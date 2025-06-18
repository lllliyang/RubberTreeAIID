<template>
  <div class="container">
    <h2 class="title">🌳 Rubber Tree Information - ID: {{ tree.id }}</h2>

    <div class="section" v-for="(group, groupName) in groupedData" :key="groupName">
      <h3 class="section-title">{{ sectionTitles[groupName] || groupName }}</h3>
      <ul class="info-list">
        <li v-for="(value, key) in group" :key="key">
          <span class="label">{{ fieldLabels[key] || key }}:</span>
          <span class="value">{{ value || '—' }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const tree = ref({})
const groupedData = ref({})

// ❌ Hidden fields
const excludedFields = ['qrcode', 'yield', 'crown_volume', 'biomass', 'branch_height', 'create_at', 'image_name', 'tree_id']

// ✅ Visible section headers
const sectionTitles = {
  variety: '🌿 Variety Rights Information',
  nursery: '🧬 Nursery & Propagation',
  planting: '🌱 Planting Details',
  others: '📦 Other Information'
}

// ✅ Field name mapping (sorted)
const fieldLabels = {
  // 🌿 Variety Rights
  variety_name: 'Variety Name',
  variety_right_number: 'Variety Right Number',
  authorization_date: 'Authorization Date',
  rights_holder: 'Plant Variety Right Holder',
  breeder: 'Breeder',
  variety_origin: 'Variety Origin',
  suitable_region: 'Suitable Planting Region',

  // 🧬 Nursery
  nursery_unit: 'Nursery Unit',
  responsible_person: 'Person in Charge',
  propagation_generation: 'Propagation Generation',
  budding_date: 'Budding Date',
  budding_location: 'Budding Location',
  budding_operator: 'Budding Operator',
  nursery_exit_date: 'Outplanting Date',
  nursery_exit_location: 'Outplanting Location',

  // 🌱 Planting
  planter_unit: 'Planter',
  planting_date: 'Planting Time',
  longitude: 'Planting Longitude',
  latitude: 'Planting Latitude',
  elevation: 'Planting Altitude',

  // 📦 Others (tree traits)
  measurement_time: 'Measurement Time',
  stem_girth: 'Stem Girth',
  canopy_width: 'Canopy Width',
  tree_height: 'Tree Height',
  number_of_leaf_clusters: 'Number of Leaf Clusters'
}

onMounted(async () => {
  const id = route.params.id
  const res = await axios.get(`http://localhost:5000/api/get_tree_data/${id}`)
  tree.value = res.data
  groupTreeData()
})

function groupTreeData() {
  const data = tree.value
  const group = {
    variety: {},
    nursery: {},
    planting: {},
    others: {}
  }

  for (const key in data) {
    if (excludedFields.includes(key)) continue
    if (!(key in fieldLabels)) continue

    if (key.startsWith('variety') || key === 'rights_holder' || key === 'breeder' || key === 'variety_origin' || key === 'suitable_region') {
      group.variety[key] = data[key]
    } else if (
      key.startsWith('nursery') || key === 'responsible_person' ||
      key.startsWith('budding') || key.startsWith('propagation')
    ) {
      group.nursery[key] = data[key]
    } else if (
      key.startsWith('planter') ||
      ['planting_date', 'longitude', 'latitude', 'elevation'].includes(key)
    ) {
      group.planting[key] = data[key]
    } else {
      group.others[key] = data[key]
    }
  }

  groupedData.value = group
}
</script>

<style scoped>
.container {
  max-width: 850px;
  margin: 30px auto;
  padding: 24px;
  font-family: "Segoe UI", sans-serif;
  background: #ffffff;
}
.title {
  text-align: center;
  font-size: 30px;
  font-weight: bold;
  color: #2d4059;
  margin-bottom: 28px;
}
.section {
  background: #f4f6f9;
  border-left: 6px solid #4a90e2;
  padding: 18px 22px;
  margin-bottom: 24px;
  border-radius: 12px;
}
.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #34495e;
  margin-bottom: 12px;
}
.info-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.info-list li {
  display: flex;
  padding: 6px 0;
  border-bottom: 1px dashed #dcdde1;
}
.label {
  width: 200px;
  font-weight: 500;
  color: #333;
}
.value {
  flex: 1;
  color: #2f3542;
  word-break: break-word;
}
</style>
