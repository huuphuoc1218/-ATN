<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import axiosInstance from '@/utils/axios'

const toast = useToast()
const authStore = useAuthStore()
const backendOrigin = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(
  /\/api\/?$/,
  '',
)

const resolveImageUrl = (imagePath: string) => {
  if (!imagePath) return ''
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) return imagePath
  if (imagePath.startsWith('/')) return `${backendOrigin}${imagePath}`
  return `${backendOrigin}/${imagePath}`
}

const toRelativeImagePath = (url: string) => {
  if (!url) return ''
  if (url.startsWith('/')) return url
  if (url.startsWith(backendOrigin)) {
    const relative = url.slice(backendOrigin.length)
    return relative.startsWith('/') ? relative : `/${relative}`
  }
  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      const parsed = new URL(url)
      if (parsed.pathname.startsWith('/uploads/')) {
        return parsed.pathname
      }
      // Keep external CDN URLs (e.g. Cloudinary) unchanged.
      return url
    } catch {
      return ''
    }
  }
  return ''
}

const normalizeTimeInput = (value: string): string => {
  const cleaned = String(value || '').trim()
  if (!cleaned) return ''

  const matched = cleaned.match(/^(\d{1,2})(?::?(\d{1,2}))?$/)
  if (!matched) return cleaned

  const hour = Number(matched[1])
  const minute = Number(matched[2] ?? '0')
  if (Number.isNaN(hour) || Number.isNaN(minute)) return cleaned
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return cleaned

  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
}

const isValidTimeValue = (value: string): boolean => {
  return /^([01]\d|2[0-3]):[0-5]\d$/.test(String(value || '').trim())
}

const isSlotFilled = (slot: TimeSlot): boolean => {
  const hasPrice = Number(slot.price) > 0
  return isValidTimeValue(slot.startTime) && isValidTimeValue(slot.endTime) && hasPrice
}

// Time slots for pricing
interface TimeSlot {
  id: string
  startTime: string
  endTime: string
  price: string
}

// Form data
const courtForm = ref({
  name: '',
  address: '',
  ward: '',
  city: '',
  description: '',
  court_quantity: 1,
  opening_time: '06:00',
  closing_time: '22:00',
  facilities: [] as string[],
  contact_phone: '',
  contact_email: '',
})

// Bank account info
const bankForm = ref({
  bank_account_number: '',
  bank_account_name: '',
  bank_name: '',
  bank_code: '',
})

// Vietnamese banks list
const vietnameseBanks = [
  { code: '970436', name: 'Vietcombank' },
  { code: '970415', name: 'Vietinbank' },
  { code: '970405', name: 'Agribank' },
  { code: '970422', name: 'MB Bank' },
  { code: '970407', name: 'Techcombank' },
  { code: '970416', name: 'ACB' },
  { code: '970432', name: 'VPBank' },
  { code: '970423', name: 'TPBank' },
  { code: '970403', name: 'Sacombank' },
  { code: '970448', name: 'OCB' },
  { code: '970414', name: 'Oceanbank' },
  { code: '970419', name: 'NCB' },
  { code: '970418', name: 'BIDV' },
  { code: '970406', name: 'DongA Bank' },
  { code: '970409', name: 'BacA Bank' },
  { code: '970437', name: 'HDBank' },
  { code: '970438', name: 'BVBank' },
  { code: '970440', name: 'Seabank' },
  { code: '970443', name: 'SHB' },
  { code: '970431', name: 'Eximbank' },
  { code: '970426', name: 'MSB' },
  { code: '970441', name: 'VIB' },
  { code: '970427', name: 'VietCapital Bank' },
  { code: '970428', name: 'Nam A Bank' },
  { code: '970429', name: 'SCB' },
  { code: '970433', name: 'VietBank' },
  { code: '970439', name: 'Public Bank' },
  { code: '970442', name: 'HongLeong Bank' },
  { code: '970449', name: 'LienVietPostBank' },
  { code: '970454', name: 'VietABank' },
  { code: '970455', name: 'IBK - Industrial Bank of Korea' },
  { code: '970456', name: 'IBKHCM' },
  { code: '970458', name: 'UOB' },
  { code: '970410', name: 'StandardChartered' },
  { code: '970412', name: 'PBVN' },
  { code: '970424', name: 'Shinhan Bank' },
  { code: '970446', name: 'Coop Bank' },
  { code: '970425', name: 'ABBank' },
  { code: '970408', name: 'GPBank' },
  { code: '970430', name: 'PGBank' },
  { code: '970434', name: 'IndovinaBank' },
  { code: '970452', name: 'KienLongBank' },
  { code: '970444', name: 'CBBank' },
]

const timeSlots = ref<TimeSlot[]>([])
let nextSlotId = 1

const currentCourtId = ref<number | null>(null)
const isEditMode = ref(false)

// Fetch approved court if exists
const fetchApprovedCourt = async () => {
  try {
    const response = await axiosInstance.get('/courts/my')
    if (response.data && response.data.length > 0) {
      const court = response.data[0]
      currentCourtId.value = court.id
      isEditMode.value = true

      // Load court data into form
      courtForm.value = {
        name: court.name,
        address: court.address,
        ward: court.ward,
        city: court.city,
        description: court.description || '',
        court_quantity: court.court_quantity,
        opening_time: court.opening_time,
        closing_time: court.closing_time,
        facilities: court.facilities || [],
        contact_phone: court.contact_phone,
        contact_email: court.contact_email || '',
      }

      // Load time slots
      if (court.time_slots && court.time_slots.length > 0) {
        timeSlots.value = court.time_slots.map(
          (slot: { start_time: string; end_time: string; price: number }, index: number) => ({
            id: String(index + 1),
            startTime: slot.start_time,
            endTime: slot.end_time,
            price: String(slot.price),
          }),
        )
        nextSlotId = timeSlots.value.length + 1
      }

      // Load existing images
      if (court.images && court.images.length > 0) {
        imagePreviews.value = court.images.map((img: string) => resolveImageUrl(img))
      }
    }
  } catch (error) {
    console.log('No approved court found or error:', error)
  }
}

// Load user info on mount
onMounted(async () => {
  if (authStore.user) {
    courtForm.value.contact_phone = authStore.user.phone_number || ''
    courtForm.value.contact_email = authStore.user.email || ''

    // Load bank account info if available
    bankForm.value.bank_account_number = authStore.user.bank_account_number || ''
    bankForm.value.bank_account_name = authStore.user.bank_account_name || ''
    bankForm.value.bank_name = authStore.user.bank_name || ''
    bankForm.value.bank_code = authStore.user.bank_code || ''

    // Try to fetch approved court
    await fetchApprovedCourt()
  }
})

// Auto uppercase bank account name
const handleBankAccountNameInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  bankForm.value.bank_account_name = target.value.toUpperCase()
}

const images = ref<File[]>([])
const imagePreviews = ref<string[]>([])

// Court editing removed - using request workflow only

// Available facilities
const availableFacilities = [
  { id: 'parking', label: 'Parking', icon: '🚗' },
  { id: 'locker', label: 'Locker', icon: '🔐' },
  { id: 'shower', label: 'Shower', icon: '🚿' },
  { id: 'water', label: 'Drinking Water', icon: '💧' },
  { id: 'toilet', label: 'Restroom', icon: '🚻' },
  { id: 'lighting', label: 'Lighting', icon: '💡' },
  { id: 'wifi', label: 'WiFi', icon: '📶' },
  { id: 'shop', label: 'Shop', icon: '🏪' },
]

const isSaving = ref(false)

const addTimeSlot = () => {
  timeSlots.value.push({
    id: String(nextSlotId++),
    startTime: '',
    endTime: '',
    price: '',
  })
}

const removeTimeSlot = (id: string) => {
  const index = timeSlots.value.findIndex((slot) => slot.id === id)
  if (index > -1) {
    timeSlots.value.splice(index, 1)
  }
}

const toggleFacility = (facilityId: string) => {
  const index = courtForm.value.facilities.indexOf(facilityId)
  if (index > -1) {
    courtForm.value.facilities.splice(index, 1)
  } else {
    courtForm.value.facilities.push(facilityId)
  }
}

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])

  if (images.value.length + files.length > 10) {
    toast.error('Maximum 10 images allowed')
    return
  }

  files.forEach((file) => {
    if (!file.type.startsWith('image/')) {
      toast.error('Only image files are accepted')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image size must not exceed 5MB')
      return
    }

    images.value.push(file)

    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreviews.value.push(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  })
}

// Remove existing image (for edit mode)
const removeExistingImage = (index: number) => {
  imagePreviews.value.splice(index, 1)
  toast.success('Image removed')
}

// Remove new image
const removeNewImage = (index: number) => {
  images.value.splice(index, 1)
  toast.success('Image removed')
}

// Helper to get image preview URL
const getImagePreview = (file: File) => {
  return URL.createObjectURL(file)
}

const resetForm = () => {
  courtForm.value = {
    name: '',
    address: '',
    ward: '',
    city: '',
    description: '',
    court_quantity: 1,
    opening_time: '06:00',
    closing_time: '22:00',
    facilities: [] as string[],
    contact_phone: authStore.user?.phone_number || '',
    contact_email: authStore.user?.email || '',
  }
  timeSlots.value = []
  images.value = []
  imagePreviews.value = []
  nextSlotId = 1
}

const validateForm = () => {
  // Normalize manual inputs before validating and rendering conditions.
  courtForm.value.opening_time = normalizeTimeInput(courtForm.value.opening_time)
  courtForm.value.closing_time = normalizeTimeInput(courtForm.value.closing_time)
  timeSlots.value.forEach((slot) => {
    slot.startTime = normalizeTimeInput(slot.startTime)
    slot.endTime = normalizeTimeInput(slot.endTime)
  })

  if (!courtForm.value.name.trim()) {
    toast.error('Please enter court name')
    return false
  }
  if (!courtForm.value.court_quantity || courtForm.value.court_quantity < 1) {
    toast.error('Court quantity must be at least 1')
    return false
  }

  if (!courtForm.value.address.trim()) {
    toast.error('Please enter address')
    return false
  }

  if (!courtForm.value.ward.trim()) {
    toast.error('Please enter ward')
    return false
  }

  if (!courtForm.value.city.trim()) {
    toast.error('Please enter city')
    return false
  }

  // Validate time slots
  if (timeSlots.value.length === 0) {
    toast.error('Please add at least one time slot')
    return false
  }

  for (const slot of timeSlots.value) {
    if (!slot.startTime || !slot.endTime) {
      toast.error('Please enter start and end time for all slots')
      return false
    }
    if (!isValidTimeValue(slot.startTime) || !isValidTimeValue(slot.endTime)) {
      toast.error('Time format must be HH:MM (e.g. 06:00, 18:30)')
      return false
    }
    if (slot.startTime >= slot.endTime) {
      toast.error(`End time (${slot.endTime}) must be later than start time (${slot.startTime})`)
      return false
    }
    if (!slot.price || parseFloat(slot.price) <= 0) {
      toast.error('Please enter valid price for all slots')
      return false
    }
  }

  // Validate time slots coverage
  if (!courtForm.value.opening_time || !courtForm.value.closing_time) {
    toast.error('Please enter opening and closing time')
    return false
  }

  if (
    !isValidTimeValue(courtForm.value.opening_time) ||
    !isValidTimeValue(courtForm.value.closing_time)
  ) {
    toast.error('Opening and closing time must be HH:MM (e.g. 06:00, 22:00)')
    return false
  }

  if (courtForm.value.opening_time >= courtForm.value.closing_time) {
    toast.error(
      `Closing time (${courtForm.value.closing_time}) must be later than opening time (${courtForm.value.opening_time})`,
    )
    return false
  }

  // Check if time slots cover the entire opening hours
  const openingTime = courtForm.value.opening_time
  const closingTime = courtForm.value.closing_time
  const sortedSlots = [...timeSlots.value].sort((a, b) => a.startTime.localeCompare(b.startTime))

  // Check if first slot starts at opening time
  if (sortedSlots[0].startTime !== openingTime) {
    toast.error(
      `The first slot must start at opening time (${openingTime}). Current start: ${sortedSlots[0].startTime}`,
    )
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return false
  }

  // Check if last slot ends at closing time
  if (sortedSlots[sortedSlots.length - 1].endTime !== closingTime) {
    toast.error(
      `The last slot must end at closing time (${closingTime}). Current end: ${sortedSlots[sortedSlots.length - 1].endTime}`,
    )
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return false
  }

  // Check for gaps between time slots
  for (let i = 0; i < sortedSlots.length - 1; i++) {
    if (sortedSlots[i].endTime !== sortedSlots[i + 1].startTime) {
      toast.error(
        `There is a gap between slots (${sortedSlots[i].endTime} - ${sortedSlots[i + 1].startTime}). Please cover all time slots from ${openingTime} to ${closingTime}`,
      )
      window.scrollTo({ top: 0, behavior: 'smooth' })
      return false
    }
  }

  if (!courtForm.value.contact_phone.trim()) {
    toast.error('Please enter contact phone number')
    return false
  }

  if (!/^[0-9]{10}$/.test(courtForm.value.contact_phone.trim())) {
    toast.error('Phone number must contain 10 digits')
    return false
  }

  // Validate bank account info (required for payment receiving)
  if (!bankForm.value.bank_account_number.trim()) {
    toast.error('Please enter bank account number for receiving payments')
    return false
  }

  if (!bankForm.value.bank_account_name.trim()) {
    toast.error('Please enter account holder name')
    return false
  }

  if (!bankForm.value.bank_name || !bankForm.value.bank_code) {
    toast.error('Please select a bank')
    return false
  }

  // Validate images (only for new court, not edit mode)
  if (!isEditMode.value && images.value.length < 5) {
    toast.error(`Please upload at least 5 images (current: ${images.value.length}/5)`)
    return false
  }

  // For edit mode, check total images (existing + new)
  if (isEditMode.value) {
    const totalImages = imagePreviews.value.length + images.value.length
    if (totalImages < 5) {
      toast.error(`At least 5 images are required (current: ${totalImages}/5)`)
      return false
    }
  }

  return true
}

const handleSubmit = async () => {
  const isValid = validateForm()
  if (!isValid) {
    return
  }

  // Kiểm tra authentication token
  if (!authStore.token) {
    toast.error('Session expired. Please log in again!')
    return
  }

  isSaving.value = true
  try {
    // Update bank account info first
    try {
      const bankUpdateResponse = await axiosInstance.put('/users/me', {
        bank_account_number: bankForm.value.bank_account_number.trim(),
        bank_account_name: bankForm.value.bank_account_name.trim().toUpperCase(),
        bank_name: bankForm.value.bank_name,
        bank_code: bankForm.value.bank_code,
      })

      // Update auth store with new user data
      if (bankUpdateResponse.data) {
        authStore.user = bankUpdateResponse.data
        localStorage.setItem('user', JSON.stringify(bankUpdateResponse.data))
      }
    } catch (bankError) {
      console.error('Failed to update bank info:', bankError)
      toast.error('Unable to update bank information. Please try again.')
      return
    }

    let imageUrls: string[] = []

    // Upload new images if any
    if (images.value.length > 0) {
      const formData = new FormData()
      images.value.forEach((image) => {
        formData.append('images', image)
      })

      const uploadResponse = await axiosInstance.post('/upload-images', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      imageUrls = uploadResponse.data.urls
    }

    // Merge new images with existing ones
    const existingImages = imagePreviews.value
      .map((url) => toRelativeImagePath(url))
      .filter((url) => Boolean(url))

    const allImages = [...existingImages, ...imageUrls]

    // Create court request for both new submission and edits.
    // If owner already has a court, admin approval will update existing data.
    const courtRequestData = {
      name: courtForm.value.name,
      address: courtForm.value.address,
      ward: courtForm.value.ward,
      city: courtForm.value.city,
      description: courtForm.value.description,
      court_quantity: courtForm.value.court_quantity,
      opening_time: courtForm.value.opening_time,
      closing_time: courtForm.value.closing_time,
      facilities: JSON.stringify(courtForm.value.facilities),
      contact_phone: courtForm.value.contact_phone,
      contact_email: courtForm.value.contact_email,
      time_slots: JSON.stringify(
        timeSlots.value.map((slot) => ({
          start_time: slot.startTime,
          end_time: slot.endTime,
          price: parseFloat(slot.price),
        })),
      ),
      images: allImages.length > 0 ? JSON.stringify(allImages) : null,
    }

    await axiosInstance.post('/court-requests', courtRequestData)

    if (!isEditMode.value) {
      resetForm()
    } else {
      await fetchApprovedCourt()
    }

    toast.success(
      isEditMode.value
        ? 'Court update request submitted. It will be applied after admin approval.'
        : 'Court submission sent! Admin will review and approve it as soon as possible.',
    )

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    const err = error as { response?: { data?: { detail?: string } } }
    toast.error(err.response?.data?.detail || 'Action failed. Please try again!')
  } finally {
    isSaving.value = false
  }
}

// Court editing removed - now using request workflow
// Owner submits request → Admin approves → System creates court
// Court management moved to separate Court List page

const formatCurrency = (value: string | number) => {
  const numValue = typeof value === 'string' ? value.replace(/[^0-9]/g, '') : String(value)
  const num = parseFloat(numValue)
  if (isNaN(num)) return ''
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatTimeWithPeriod = (time: string) => {
  if (!time) return ''
  const [hours] = time.split(':')
  const hour = parseInt(hours)
  if (hour < 12) {
    return `${time} SA`
  } else {
    return `${time} CH`
  }
}
</script>

<template>
  <div class="court-upload-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            style="
              width: 40px;
              height: 40px;
              display: inline-block;
              vertical-align: middle;
              margin-right: 8px;
            "
          >
            <rect x="4" y="10" width="16" height="8" rx="2" fill="#10b981" />
            <rect x="7" y="6" width="10" height="4" rx="2" fill="#fbbf24" />
            <rect x="9" y="2" width="6" height="4" rx="2" fill="#3b82f6" />
          </svg>
          Upload Court
        </h1>
        <p class="page-subtitle">Fill in all required details to upload your court</p>
      </div>
      <button class="preview-btn" type="button">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
          />
        </svg>
        Preview
      </button>
    </div>

    <div class="request-workflow-card">
      <div class="workflow-title-row">
        <span class="workflow-badge">Approval Workflow</span>
        <strong>{{ isEditMode ? 'Update Mode' : 'Create Mode' }}</strong>
      </div>
      <p class="workflow-text">
        {{
          isEditMode
            ? 'Changes are submitted as an update request and will only be applied after admin approval.'
            : 'Your court data is submitted as a request and will appear after admin approval.'
        }}
      </p>
      <div class="workflow-steps">
        <span>1. Submit request</span>
        <span>2. Admin reviews</span>
        <span>3. Data is published</span>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="court-form">
      <!-- Basic Information -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Basic Information
          </h2>
        </div>

        <div class="form-grid">
          <div class="form-group full-width">
            <label class="form-label required">Court Name</label>
            <input
              v-model="courtForm.name"
              type="text"
              class="form-input"
              placeholder="Ex: Pickleball Court VIP A1"
            />
          </div>

          <div class="form-group full-width">
            <label class="form-label required">Address</label>
            <input
              v-model="courtForm.address"
              type="text"
              class="form-input"
              placeholder="Ex: 123 Nguyen Van A"
            />
          </div>

          <div class="form-group">
            <label class="form-label required">Ward</label>
            <input
              v-model="courtForm.ward"
              type="text"
              class="form-input"
              placeholder="Ex: Ward 1"
            />
          </div>

          <div class="form-group">
            <label class="form-label required">City</label>
            <input
              v-model="courtForm.city"
              type="text"
              class="form-input"
              placeholder="Ex: Ho Chi Minh City"
            />
          </div>

          <div class="form-group">
            <label class="form-label required">Court Quantity</label>
            <input
              v-model.number="courtForm.court_quantity"
              type="number"
              class="form-input"
              placeholder="VD: 5"
              min="1"
              step="1"
            />
          </div>

          <div class="form-group full-width">
            <label class="form-label">Description</label>
            <textarea
              v-model="courtForm.description"
              class="form-textarea"
              rows="4"
              placeholder="Detailed description of your court..."
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Pricing & Hours -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Time-slot Pricing
          </h2>
          <span class="section-subtitle">Add time slots with corresponding pricing</span>
        </div>

        <div v-if="timeSlots.length === 0" class="empty-slots">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            class="empty-icon"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <p class="empty-text">No time slots yet. Click the button below to add one.</p>
        </div>

        <div v-else class="time-slots-list">
          <div
            v-for="slot in timeSlots"
            :key="slot.id"
            class="time-slot-item"
            :class="{
              filled: isSlotFilled(slot),
            }"
          >
            <div class="slot-inputs">
              <div class="slot-input-group">
                <label class="slot-label">From</label>
                <input v-model="slot.startTime" type="time" class="slot-time-input" step="60" />
              </div>

              <span class="slot-separator">→</span>

              <div class="slot-input-group">
                <label class="slot-label">To</label>
                <input v-model="slot.endTime" type="time" class="slot-time-input" step="60" />
              </div>

              <div class="slot-input-group slot-price-group">
                <label class="slot-label">Price</label>
                <div class="slot-price-input-wrapper">
                  <input
                    v-model="slot.price"
                    type="number"
                    class="slot-price-input"
                    placeholder="VD: 150000"
                    min="0"
                    step="1000"
                  />
                  <span class="price-unit">VND/hour</span>
                </div>
              </div>
            </div>

            <button
              type="button"
              class="remove-slot-btn"
              @click="removeTimeSlot(slot.id)"
              title="Delete time slot"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>

            <div v-if="isSlotFilled(slot)" class="slot-preview">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                style="
                  width: 18px;
                  height: 18px;
                  display: inline-block;
                  vertical-align: middle;
                  margin-right: 6px;
                "
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {{ formatTimeWithPeriod(slot.startTime) }} -
              {{ formatTimeWithPeriod(slot.endTime) }} • {{ formatCurrency(slot.price) }} VND/hour
            </div>
          </div>
        </div>

        <button type="button" class="add-slot-btn" @click="addTimeSlot">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            />
          </svg>
          <span>Add time slot</span>
        </button>

        <div class="form-grid" style="margin-top: 24px">
          <div class="form-group">
            <label class="form-label">Opening time</label>
            <input
              v-model="courtForm.opening_time"
              type="time"
              class="form-input"
              title="Ex: 06:00 (6 AM)"
              step="60"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Closing time</label>
            <input
              v-model="courtForm.closing_time"
              type="time"
              class="form-input"
              title="Ex: 22:00 (10 PM)"
              step="60"
            />
          </div>
        </div>

        <div
          v-if="courtForm.opening_time && courtForm.closing_time"
          class="operating-hours-preview"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            style="
              width: 18px;
              height: 18px;
              display: inline-block;
              vertical-align: middle;
              margin-right: 6px;
            "
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          {{ formatTimeWithPeriod(courtForm.opening_time) }} -
          {{ formatTimeWithPeriod(courtForm.closing_time) }}
        </div>
      </div>

      <!-- Facilities -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
            Amenities
          </h2>
          <span class="section-subtitle">Select available amenities for this court</span>
        </div>

        <div class="facilities-grid">
          <button
            v-for="facility in availableFacilities"
            :key="facility.id"
            type="button"
            class="facility-btn"
            :class="{ active: courtForm.facilities.includes(facility.id) }"
            @click="toggleFacility(facility.id)"
          >
            <span class="facility-icon">{{ facility.icon }}</span>
            <span class="facility-label">{{ facility.label }}</span>
            <svg
              v-if="courtForm.facilities.includes(facility.id)"
              class="facility-check"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Images -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            Images
          </h2>
          <span class="section-subtitle">
            {{
              isEditMode
                ? `Minimum 5 images required (Current: ${imagePreviews.length + images.length}/10)`
                : '5 court photos are required for submission'
            }}
          </span>
        </div>

        <div class="images-section">
          <!-- Existing images (for edit mode) -->
          <div v-if="isEditMode && imagePreviews.length > 0" class="existing-images-section">
            <h3 class="subsection-title">Current images</h3>
            <div class="images-preview">
              <div
                v-for="(preview, index) in imagePreviews"
                :key="'existing-' + index"
                class="preview-item"
              >
                <img :src="preview" :alt="'Existing image ' + (index + 1)" />
                <button
                  type="button"
                  class="remove-btn"
                  @click="removeExistingImage(index)"
                  title="Delete this image"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
                <span v-if="index === 0" class="primary-badge">Primary image</span>
              </div>
            </div>
          </div>

          <!-- New images -->
          <div v-if="images.length > 0" class="new-images-section">
            <h3 v-if="isEditMode" class="subsection-title">Newly added images</h3>
            <div class="images-preview">
              <div v-for="(image, index) in images" :key="'new-' + index" class="preview-item">
                <img :src="getImagePreview(image)" :alt="'New image ' + (index + 1)" />
                <button
                  type="button"
                  class="remove-btn"
                  @click="removeNewImage(index)"
                  title="Delete this image"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
                <span class="new-badge">New</span>
              </div>
            </div>
          </div>

          <!-- Upload button -->
          <div class="image-upload-area">
            <input
              type="file"
              id="image-upload"
              multiple
              accept="image/*"
              @change="handleImageUpload"
              style="display: none"
            />
            <label for="image-upload" class="upload-label">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4v16m8-8H4"
                />
              </svg>
              <span>{{ isEditMode ? 'Add new images' : 'Add images' }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Contact Information -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
              />
            </svg>
            Contact Information
          </h2>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label class="form-label required">Phone Number</label>
            <input
              v-model="courtForm.contact_phone"
              type="tel"
              class="form-input"
              placeholder="VD: 0901234567"
              maxlength="10"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              v-model="courtForm.contact_email"
              type="email"
              class="form-input"
              placeholder="VD: contact@example.com"
            />
          </div>
        </div>
      </div>

      <!-- Bank Account Information -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="
                width: 24px;
                height: 24px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 8px;
              "
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
              />
            </svg>
            Bank Account
          </h2>
          <p class="section-description">Account information for receiving customer payments</p>
        </div>

        <div class="form-grid">
          <div class="form-group full-width">
            <label class="form-label required">Bank</label>
            <select
              v-model="bankForm.bank_code"
              class="form-input"
              @change="
                (e) => {
                  const selected = vietnameseBanks.find(
                    (b) => b.code === (e.target as HTMLSelectElement).value,
                  )
                  if (selected) {
                    bankForm.bank_name = selected.name
                  }
                }
              "
            >
              <option value="">-- Select bank --</option>
              <option v-for="bank in vietnameseBanks" :key="bank.code" :value="bank.code">
                {{ bank.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label required">Account Number</label>
            <input
              v-model="bankForm.bank_account_number"
              type="text"
              class="form-input"
              placeholder="VD: 1234567890"
              maxlength="20"
            />
          </div>

          <div class="form-group">
            <label class="form-label required">Account Holder Name</label>
            <input
              v-model="bankForm.bank_account_name"
              type="text"
              class="form-input"
              placeholder="VD: NGUYEN VAN A"
              @input="handleBankAccountNameInput"
            />
            <small style="color: #6b7280; font-size: 12px; margin-top: 4px; display: block">
              Account holder name must match the bank account name (auto-uppercase)
            </small>
          </div>

          <div class="bank-info-notice">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style="width: 20px; height: 20px; flex-shrink: 0"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <strong>Note:</strong> Bank account details are used to receive customer payments.
              Please ensure all information is accurate to avoid transaction issues.
            </div>
          </div>
        </div>
      </div>

      <!-- Individual Courts List (if created) -->
      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" @click="handleSubmit" class="btn-submit" :disabled="isSaving">
          <svg
            v-if="!isSaving"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
          <svg
            v-else
            class="animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          {{
            isSaving
              ? 'Submitting request...'
              : isEditMode
                ? 'Submit Update Request'
                : 'Submit Court Request'
          }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.court-upload-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.page-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
  margin: 0;
}

.preview-btn {
  padding: 12px 24px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.preview-btn:hover {
  border-color: #2d5016;
  color: #2d5016;
  background: #f0fdf4;
}

.preview-btn svg {
  width: 18px;
  height: 18px;
}

.request-workflow-card {
  background: linear-gradient(135deg, #eff6ff 0%, #ecfeff 100%);
  border: 1px solid #bfdbfe;
  border-radius: 14px;
  padding: 16px 18px;
}

.workflow-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.workflow-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: #dbeafe;
  color: #1d4ed8;
}

.workflow-text {
  margin: 0;
  color: #1e3a8a;
  font-size: 0.9rem;
}

.workflow-steps {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #334155;
  font-size: 0.82rem;
  font-weight: 600;
}

/* Form */
.court-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  background: white;
  padding: 28px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section-header {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.section-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
  line-height: 1.5;
}

.section-subtitle {
  color: #6b7280;
  font-size: 0.85rem;
  margin: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.time-display {
  font-size: 0.875rem;
  color: #2d5016;
  font-weight: 600;
  margin-top: 4px;
  padding: 6px 12px;
  background: #f0fdf4;
  border-radius: 6px;
  display: inline-block;
  width: fit-content;
}

.form-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #374151;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-input,
.form-textarea {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-input::-webkit-calendar-picker-indicator {
  filter: invert(0.5);
  cursor: pointer;
}

.form-input::-webkit-datetime-edit-ampm-field {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

input[type='time'].form-input {
  -webkit-appearance: none;
  appearance: none;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #2d5016;
  box-shadow: 0 0 0 3px rgba(45, 80, 22, 0.1);
}

.form-textarea {
  resize: vertical;
}

.form-hint {
  font-size: 0.85rem;
  color: #2d5016;
  font-weight: 600;
}

/* Time Slots */
.empty-slots {
  padding: 48px 24px;
  background: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #6b7280;
}

.empty-text {
  font-size: 0.95rem;
  color: #6b7280;
  margin: 0;
}

.time-slots-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
}

.operating-hours-preview {
  margin-top: 12px;
  padding: 12px 16px;
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #2d5016;
  font-weight: 600;
  text-align: center;
}

.time-slot-item {
  padding: 20px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.3s ease;
  position: relative;
}

.time-slot-item:hover {
  background: #f0fdf4;
  border-color: #86efac;
}

.time-slot-item.filled {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #2d5016;
}

.slot-inputs {
  display: grid;
  grid-template-columns: 1fr auto 1fr 1.5fr;
  gap: 16px;
  align-items: end;
}

.slot-input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.slot-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
}

.slot-time-input {
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.slot-time-input::-webkit-calendar-picker-indicator {
  filter: invert(0.5);
  cursor: pointer;
}

.slot-time-input::-webkit-datetime-edit-ampm-field {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

input[type='time']::-webkit-datetime-edit-ampm-field {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

input[type='time'] {
  -webkit-appearance: none;
  -moz-appearance: textfield;
  appearance: none;
}

input[type='time']::-webkit-inner-spin-button,
input[type='time']::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.slot-time-input:focus {
  outline: none;
  border-color: #2d5016;
  box-shadow: 0 0 0 3px rgba(45, 80, 22, 0.1);
}

.slot-separator {
  font-size: 1.2rem;
  color: #6b7280;
  padding-bottom: 10px;
}

.slot-price-group {
  flex: 1.5;
}

.slot-price-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding-right: 12px;
  transition: all 0.3s ease;
}

.slot-price-input-wrapper:focus-within {
  border-color: #2d5016;
  box-shadow: 0 0 0 3px rgba(45, 80, 22, 0.1);
}

.slot-price-input {
  flex: 1;
  padding: 10px 14px;
  border: none;
  font-size: 0.95rem;
  outline: none;
}

.price-unit {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 600;
  white-space: nowrap;
}

.remove-slot-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  padding: 0;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-slot-btn:hover {
  background: #fee2e2;
  border-color: #ef4444;
}

.remove-slot-btn svg {
  width: 18px;
  height: 18px;
  color: #6b7280;
}

.remove-slot-btn:hover svg {
  color: #ef4444;
}

.slot-preview {
  font-size: 0.9rem;
  color: #2d5016;
  font-weight: 600;
  padding: 10px 14px;
  background: #dcfce7;
  border-radius: 8px;
  text-align: center;
}

.add-slot-btn {
  width: 100%;
  padding: 14px 24px;
  background: white;
  border: 2px dashed #d1d5db;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  color: #374151;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.add-slot-btn:hover {
  background: #f0fdf4;
  border-color: #2d5016;
  color: #2d5016;
}

.add-slot-btn svg {
  width: 20px;
  height: 20px;
}

/* Facilities */
.facilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  justify-items: stretch;
}

.facility-btn {
  padding: 16px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.facility-btn:hover {
  background: #f0fdf4;
  border-color: #86efac;
}

.facility-btn.active {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #2d5016;
}

.facility-icon {
  font-size: 2rem;
}

.facility-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
  text-align: center;
}

.facility-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 20px;
  height: 20px;
  background: #2d5016;
  color: white;
  border-radius: 50%;
  padding: 3px;
}

/* Images */
.images-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.image-upload-area {
  display: flex;
  justify-content: center;
}

.upload-label {
  padding: 32px 48px;
  background: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-label:hover {
  background: #f0fdf4;
  border-color: #2d5016;
}

.upload-label svg {
  width: 48px;
  height: 48px;
  color: #6b7280;
}

.upload-label span {
  font-weight: 600;
  font-size: 0.95rem;
  color: #374151;
}

.images-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid #e5e7eb;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: #ef4444;
}

.remove-btn svg {
  width: 16px;
  height: 16px;
  color: white;
}

.primary-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
}

.new-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
}

/* Image sections */
.existing-images-section,
.new-images-section {
  margin-bottom: 20px;
}

.subsection-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
  padding-left: 4px;
  border-left: 3px solid #10b981;
}

/* Individual Courts Grid */
.courts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.court-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.court-card.available {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-color: #86efac;
}

.court-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.court-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.court-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.court-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.court-status.available {
  background: #10b981;
  color: white;
}

.court-status.booked {
  background: #ef4444;
  color: white;
}

.court-status svg {
  width: 16px;
  height: 16px;
}

/* Booking functionality removed - CSS cleaned up */

.action-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #eff6ff;
  border: 1px solid #93c5fd;
  border-radius: 10px;
  margin-top: 16px;
}

.action-banner svg {
  width: 24px;
  height: 24px;
  color: #3b82f6;
  flex-shrink: 0;
}

.action-banner p {
  margin: 0;
  color: #1e40af;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Bank Account Notice */
.bank-info-notice {
  grid-column: 1 / -1;
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  background: #fef3c7;
  border: 1px solid #fbbf24;
  border-radius: 10px;
  margin-top: 8px;
  color: #92400e;
  font-size: 0.9rem;
  line-height: 1.6;
}

.bank-info-notice strong {
  color: #78350f;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  flex-wrap: wrap;
}

.btn-reset,
.btn-submit,
.btn-view-list {
  padding: 14px 32px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
  transition: all 0.3s ease;
}

.btn-reset {
  background: #f3f4f6;
  color: #6b7280;
  border: 2px solid #e5e7eb;
}

.btn-reset:hover:not(:disabled) {
  background: #e5e7eb;
  border-color: #d1d5db;
}

.btn-submit {
  background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(45, 80, 22, 0.3);
}

.btn-view-list {
  background: #3b82f6;
  color: white;
}

.btn-view-list:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}

.btn-reset:disabled,
.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-reset svg,
.btn-submit svg,
.btn-view-list svg {
  width: 18px;
  height: 18px;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .page-header {
    gap: 16px;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .form-section {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .court-upload-page {
    gap: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-title {
    font-size: 1.35rem;
  }

  .page-title svg {
    width: 32px !important;
    height: 32px !important;
    margin-right: 6px !important;
  }

  .page-subtitle {
    font-size: 0.875rem;
  }

  .preview-btn {
    width: 100%;
    justify-content: center;
    padding: 10px 20px;
    font-size: 0.9rem;
  }

  .form-section {
    padding: 16px;
    border-radius: 12px;
  }

  .section-title {
    font-size: 1.1rem;
  }

  .section-title svg {
    width: 20px !important;
    height: 20px !important;
    margin-right: 6px !important;
  }

  .section-subtitle {
    font-size: 0.8rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .slot-inputs {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .slot-separator {
    display: none;
  }

  .remove-slot-btn {
    top: 8px;
    right: 8px;
    width: 28px;
    height: 28px;
  }

  .facilities-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 12px;
  }

  .facility-btn {
    padding: 12px 8px;
  }

  .facility-icon {
    font-size: 1.5rem;
  }

  .facility-label {
    font-size: 0.8rem;
  }

  .images-preview {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 12px;
  }

  .form-actions {
    flex-direction: column-reverse;
    padding-top: 16px;
  }

  .btn-reset,
  .btn-submit,
  .btn-view-list {
    width: 100%;
    justify-content: center;
    padding: 12px 24px;
    font-size: 0.95rem;
  }

  .courts-grid {
    grid-template-columns: 1fr;
  }

  .upload-label {
    padding: 24px 32px;
  }

  .upload-label svg {
    width: 36px;
    height: 36px;
  }

  .upload-label span {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.2rem;
  }

  .page-title svg {
    width: 28px !important;
    height: 28px !important;
  }

  .form-section {
    padding: 12px;
  }

  .section-title {
    font-size: 1rem;
  }

  .section-title svg {
    width: 18px !important;
    height: 18px !important;
    margin-right: 4px !important;
  }

  .form-input,
  .form-textarea {
    padding: 10px 12px;
    font-size: 0.9rem;
  }

  .time-slot-item {
    padding: 16px;
  }

  .slot-label {
    font-size: 0.8rem;
  }

  .slot-time-input,
  .slot-price-input {
    padding: 8px 12px;
    font-size: 0.9rem;
  }

  .price-unit {
    font-size: 0.8rem;
  }

  .add-slot-btn {
    padding: 12px 20px;
    font-size: 0.9rem;
  }

  .facilities-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 10px;
  }

  .facility-btn {
    padding: 10px 6px;
  }

  .facility-icon {
    font-size: 1.25rem;
  }

  .facility-label {
    font-size: 0.75rem;
  }

  .images-preview {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 10px;
  }

  .upload-label {
    padding: 20px 24px;
  }

  .upload-label svg {
    width: 32px;
    height: 32px;
  }

  .upload-label span {
    font-size: 0.85rem;
  }

  .btn-submit svg,
  .btn-reset svg {
    width: 16px;
    height: 16px;
  }
}
</style>
