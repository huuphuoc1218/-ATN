<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import axiosInstance from '@/utils/axios'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const toast = useToast()
const backendOrigin = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(
  /\/api\/?$/,
  '',
)

interface TimeSlot {
  start_time: string
  end_time: string
  price: number
}

interface IndividualCourt {
  id: number
  name: string
  is_active?: boolean
  is_available: boolean
  bookings?: Array<{
    booking_date: string
    start_time: string
    end_time: string
    status?: string
  }>
}

interface ApiError {
  response?: {
    data?: {
      detail?: string
    }
  }
}

interface CourtOwner {
  id: number
  full_name: string
  email: string
  phone_number?: string | null
}

interface Court {
  id: number
  name: string
  address: string
  ward: string
  city: string
  opening_time: string
  closing_time: string
  images: string[]
  time_slots?: TimeSlot[]
  individual_courts?: IndividualCourt[]
  contact_phone: string
  contact_email?: string
  owner_id: number
  owner?: CourtOwner
}

const court = ref<Court | null>(null)
const isLoading = ref(false)
const currentStep = ref(1)

// Date selection
const selectedDate = ref<Date>(new Date())
const availableDates = ref<Date[]>([])

// Time selection
const selectedTimeSlots = ref<string[]>([])

// Step 2: User Information
const userInfo = ref({
  name: '',
  email: '',
  phone: '',
})

// Step 3: Payment
const bookingId = ref<number | null>(null)
const paymentInfo = ref<{
  qr_code_url: string
  bank_name: string
  account_number: string
  account_name: string
  amount: number
  content: string
  booking_id?: number | null
  expires_at: string
} | null>(null)
const isCreatingBooking = ref(false)
const isVerifyingPayment = ref(false)
const paymentVerified = ref(false)

// Generate available dates (next 7 days)
const generateAvailableDates = () => {
  const dates: Date[] = []
  const today = new Date()
  for (let i = 0; i < 7; i++) {
    const date = new Date(today)
    date.setDate(today.getDate() + i)
    dates.push(date)
  }
  availableDates.value = dates
}

// Date navigation
const currentDateIndex = computed(() => {
  return availableDates.value.findIndex(
    (date) => date.toDateString() === selectedDate.value.toDateString(),
  )
})

const visibleDates = computed(() => {
  const index = currentDateIndex.value
  // Show 6 dates at a time
  const startIndex = Math.max(0, Math.min(index, availableDates.value.length - 6))
  return availableDates.value.slice(startIndex, startIndex + 6)
})

const canGoPrev = computed(() => currentDateIndex.value > 0)
const canGoNext = computed(() => currentDateIndex.value < availableDates.value.length - 1)

const previousDate = () => {
  if (canGoPrev.value) {
    selectedDate.value = availableDates.value[currentDateIndex.value - 1]
  }
}

const nextDate = () => {
  if (canGoNext.value) {
    selectedDate.value = availableDates.value[currentDateIndex.value + 1]
  }
}

const selectDate = (date: Date) => {
  selectedDate.value = date
  selectedTimeSlots.value = []
}

// Format date
const formatDateShort = (date: Date) => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const months = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
  ]
  return {
    day: days[date.getDay()],
    date: date.getDate(),
    month: months[date.getMonth()],
  }
}

const formatDateFull = (date: Date) => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ]
  return `${days[date.getDay()]}, ${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`
}

const formatDateForBooking = (date: Date) => {
  const months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ]
  return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`
}

const formatDateKeyLocal = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const formatBookingDatePayload = (date: Date): string => {
  return `${formatDateKeyLocal(date)}T00:00:00`
}

// Generate time slots (30-minute intervals)
const generateTimeSlots = () => {
  if (!court.value) return []

  const slots: string[] = []
  const [startHour] = court.value.opening_time.split(':').map(Number)
  const [endHour] = court.value.closing_time.split(':').map(Number)

  // Generate 30-minute intervals
  for (let hour = startHour; hour < endHour; hour++) {
    slots.push(`${String(hour).padStart(2, '0')}:00`)
    slots.push(`${String(hour).padStart(2, '0')}:30`)
  }
  // Add final hour slot
  slots.push(`${String(endHour).padStart(2, '0')}:00`)

  return slots
}

const timeSlots = computed(() => generateTimeSlots())

// Check if a time slot is in the past
const isSlotInPast = (slot: string): boolean => {
  const today = new Date()
  const isToday = selectedDate.value.toDateString() === today.toDateString()

  if (!isToday) {
    // If selected date is in the future, no slots are in the past
    return selectedDate.value < today
  }

  // For today, check if the slot time has passed
  const [slotHour, slotMinute] = slot.split(':').map(Number)
  const currentHour = today.getHours()
  const currentMinute = today.getMinutes()

  // Compare slot time with current time
  if (slotHour < currentHour) {
    return true
  } else if (slotHour === currentHour && slotMinute <= currentMinute) {
    return true
  }

  return false
}

const isBlockingBookingStatus = (status?: string): boolean => {
  return status === 'pending' || status === 'active' || status === 'confirmed'
}

const isCourtBookedAtSlot = (courtData: IndividualCourt, slot: string): boolean => {
  if (!courtData.bookings || courtData.bookings.length === 0) {
    return false
  }

  const selectedDateStr = formatDateKeyLocal(selectedDate.value)

  return courtData.bookings.some((booking) => {
    if (!isBlockingBookingStatus(booking.status)) return false

    const bookingDate = booking.booking_date?.split('T')[0]
    if (bookingDate !== selectedDateStr) return false

    return slot >= booking.start_time && slot < booking.end_time
  })
}

const isSlotFullyBooked = (slot: string): boolean => {
  const activeCourts = (court.value?.individual_courts || []).filter((c) => c.is_active !== false)

  if (activeCourts.length === 0) {
    return true
  }

  return activeCourts.every((c) => isCourtBookedAtSlot(c, slot))
}

// Toggle time slot selection (range selection with start and end)
const toggleTimeSlot = (slot: string) => {
  // Check if slot is in the past
  if (isSlotInPast(slot)) {
    toast.error('Cannot book a past time slot')
    return
  }

  if (isSlotFullyBooked(slot)) {
    toast.error('This time slot is fully booked across all courts. Please choose another.')
    return
  }

  const index = selectedTimeSlots.value.indexOf(slot)

  if (index > -1) {
    // If clicking on an already selected slot, clear selection
    selectedTimeSlots.value = []
    return
  }

  if (selectedTimeSlots.value.length === 0) {
    // First selection: set as start time
    selectedTimeSlots.value = [slot]
  } else if (selectedTimeSlots.value.length === 1) {
    // Second selection: set as end time and fill range
    const startSlot = selectedTimeSlots.value[0]
    const allSlots = timeSlots.value
    const startIndex = allSlots.indexOf(startSlot)
    const endIndex = allSlots.indexOf(slot)

    if (endIndex <= startIndex) {
      // If end is before or same as start, set new start
      selectedTimeSlots.value = [slot]
    } else {
      // Check if any slot in the range is in the past
      const rangeSlots = allSlots.slice(startIndex, endIndex + 1)
      const hasPastSlot = rangeSlots.some((s) => isSlotInPast(s))
      const hasFullyBookedSlot = rangeSlots.some((s) => isSlotFullyBooked(s))

      if (hasPastSlot) {
        toast.error('Cannot book a range that includes past time')
        selectedTimeSlots.value = []
        return
      }

      if (hasFullyBookedSlot) {
        toast.error('Your selected range is fully booked across all courts. Please choose again.')
        selectedTimeSlots.value = []
        return
      }

      // Fill all slots between start and end (inclusive)
      selectedTimeSlots.value = rangeSlots
    }
  } else {
    // Reset and start new selection
    selectedTimeSlots.value = [slot]
  }
}

const isSlotSelected = (slot: string) => {
  return selectedTimeSlots.value.includes(slot)
}

// Get price for a specific time slot
const getPriceForSlot = (slot: string): number => {
  if (!court.value?.time_slots || court.value.time_slots.length === 0) {
    return 100000 // Default price
  }

  // Find the price tier that this slot falls into
  const timeSlot = court.value.time_slots.find((ts) => {
    return slot >= ts.start_time && slot < ts.end_time
  })

  return timeSlot?.price || court.value.time_slots[0].price
}

// Calculate booking details with multi-tier pricing
const bookingDetails = computed(() => {
  if (selectedTimeSlots.value.length === 0) {
    return {
      startTime: '',
      endTime: '',
      totalHours: 0,
      totalPrice: 0,
      priceBreakdown: [],
    }
  }

  const sortedSlots = [...selectedTimeSlots.value].sort()
  const startTime = sortedSlots[0]
  const endTime = sortedSlots[sortedSlots.length - 1]

  // Calculate total hours (each slot is 30 minutes, end is inclusive)
  // Total hours = (number of slots - 1) * 0.5
  const totalHours = (sortedSlots.length - 1) * 0.5

  // Calculate price with multi-tier support and track breakdown
  const priceMap = new Map<number, number>() // price -> hours
  let totalPrice = 0

  for (let i = 0; i < sortedSlots.length - 1; i++) {
    const slotPrice = getPriceForSlot(sortedSlots[i])
    totalPrice += slotPrice * 0.5 // 30 minutes = 0.5 hour

    // Track hours per price tier
    const currentHours = priceMap.get(slotPrice) || 0
    priceMap.set(slotPrice, currentHours + 0.5)
  }

  // Convert to array for display
  const priceBreakdown = Array.from(priceMap.entries()).map(([price, hours]) => ({
    price,
    hours,
    subtotal: price * hours,
  }))

  return {
    startTime,
    endTime,
    totalHours,
    totalPrice,
    priceBreakdown,
  }
})

// Format price
const formatPrice = (price: number) => {
  const formatted = new Intl.NumberFormat('vi-VN').format(price / 1000)
  return `${formatted}k`
}

// Fetch court details
const fetchCourtDetails = async () => {
  isLoading.value = true
  try {
    const courtId = route.params.id
    const response = await axiosInstance.get(`/courts/${courtId}`)
    court.value = response.data

    // Fetch individual courts for this court
    if (court.value) {
      const individualCourtsResponse = await axiosInstance.get(
        `/courts/${courtId}/individual-courts`,
      )
      court.value.individual_courts = individualCourtsResponse.data
    }
  } catch (error) {
    console.error('Error fetching court details:', error)
    toast.error('Unable to load court information. Please try again.')
  } finally {
    isLoading.value = false
  }
}

// Get court banner image
const courtBanner = computed(() => {
  if (!court.value || !court.value.images || court.value.images.length === 0) {
    return 'https://i.pinimg.com/1200x/0e/c0/4d/0ec04dde4f138cac5ec5e928edef20e9.jpg'
  }
  const img = court.value.images[0]
  if (img.startsWith('http://') || img.startsWith('https://')) {
    return img
  }
  if (img.startsWith('/')) {
    return `${backendOrigin}${img}`
  }
  return `${backendOrigin}/${img}`
})

// Navigation
const goBack = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  } else {
    router.back()
  }
}

const goNext = async () => {
  if (currentStep.value === 1) {
    if (selectedTimeSlots.value.length === 0) {
      toast.error('Please select start and end time slots')
      return
    }
    // Check minimum 1 hour (2 slots of 30 minutes: start and end)
    if (selectedTimeSlots.value.length < 3) {
      toast.error('Minimum booking duration is 1 hour')
      return
    }
    // Pre-fill user info from auth store if available
    if (authStore.user) {
      userInfo.value.name = authStore.user.full_name || ''
      userInfo.value.email = authStore.user.email || ''
      userInfo.value.phone = authStore.user.phone_number || ''
    }
    currentStep.value = 2
  } else if (currentStep.value === 2) {
    // Validate user information
    if (!userInfo.value.name.trim()) {
      toast.error('Please enter your full name')
      return
    }
    if (!userInfo.value.email.trim()) {
      toast.error('Please enter your email')
      return
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(userInfo.value.email)) {
      toast.error('Invalid email address')
      return
    }
    if (!userInfo.value.phone.trim()) {
      toast.error('Please enter your phone number')
      return
    }
    if (!/^[0-9]{10,11}$/.test(userInfo.value.phone.replace(/\s/g, ''))) {
      toast.error('Invalid phone number (10-11 digits)')
      return
    }
    // Move to payment step with payment preview only (no booking created yet)
    await preparePaymentPreview()
  } else if (currentStep.value === 3) {
    // Create booking only when user presses Complete on payment step
    await verifyPayment()
  }
}

const preparePaymentPreview = async () => {
  if (!court.value) return

  isCreatingBooking.value = true
  try {
    const response = await axiosInstance.post('/bookings/payment-preview', {
      court_id: court.value.id,
      booking_date: formatBookingDatePayload(selectedDate.value),
      start_time: bookingDetails.value.startTime,
      end_time: bookingDetails.value.endTime,
    })

    paymentInfo.value = response.data
    currentStep.value = 3
  } catch (error: unknown) {
    console.error('Error preparing payment preview:', error)
    const errorMsg =
      (error as ApiError).response?.data?.detail ||
      'Unable to create payment information. Please try again.'
    toast.error(errorMsg)
  } finally {
    isCreatingBooking.value = false
  }
}

// Create booking with payment
const createBooking = async () => {
  if (isCreatingBooking.value) return

  isCreatingBooking.value = true
  try {
    // Backend will always allocate from first available court to last.
    // We only pass a valid court id in this venue as a reference.
    const individualCourt = court.value?.individual_courts?.find(
      (c: IndividualCourt) => c.is_active !== false,
    )

    if (!individualCourt) {
      toast.error('No courts are available. Please try again later.')
      return
    }

    const bookingData = {
      individual_court_id: individualCourt.id,
      booking_date: formatBookingDatePayload(selectedDate.value),
      start_time: bookingDetails.value.startTime,
      end_time: bookingDetails.value.endTime,
      phone_number: userInfo.value.phone,
      customer_name: userInfo.value.name,
      customer_email: userInfo.value.email,
      payment_method: 'vietqr',
    }

    const response = await axiosInstance.post('/bookings', bookingData)

    if (response.data) {
      bookingId.value = response.data.id
      return true
    }

    return false
  } catch (error: unknown) {
    console.error('Error creating booking:', error)
    const errorMsg =
      (error as ApiError).response?.data?.detail || 'Unable to create booking. Please try again.'
    toast.error(errorMsg)
    return false
  } finally {
    isCreatingBooking.value = false
  }
}

// Verify payment
const verifyPayment = async () => {
  if (isVerifyingPayment.value) return

  isVerifyingPayment.value = true
  try {
    const created = await createBooking()
    if (!created) {
      return
    }

    paymentVerified.value = true
  } finally {
    isVerifyingPayment.value = false
  }
}

// Copy to clipboard
const copyToClipboard = async (text: string, label: string) => {
  try {
    await navigator.clipboard.writeText(text)
    toast.success(`Copied ${label}!`)
  } catch {
    toast.error('Unable to copy. Please copy manually.')
  }
}

const showManagement = computed(() => authStore.user?.role === 'owner')
const showAdvertisement = computed(() => authStore.user?.role === 'enterprise')

onMounted(() => {
  if (!authStore.user || !authStore.token) {
    router.push('/login')
    return
  }
  fetchCourtDetails()
  generateAvailableDates()
})
</script>

<template>
  <div class="booking-page">
    <AppHeader :showManagement="showManagement" :showAdvertisement="showAdvertisement" />

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading...</p>
    </div>

    <!-- Booking Content -->
    <div v-else-if="court" class="booking-content">
      <!-- Banner -->
      <div class="banner-section">
        <img :src="courtBanner" :alt="court.name" class="banner-image" />
      </div>

      <!-- Progress Indicator -->
      <div class="progress-section">
        <div class="progress-container">
          <div
            class="progress-step"
            :class="{ active: currentStep >= 1, completed: currentStep > 1 }"
          >
            <div class="step-number">1</div>
            <span class="step-label">Time & Date</span>
          </div>
          <div class="progress-line" :class="{ active: currentStep >= 2 }"></div>
          <div
            class="progress-step"
            :class="{ active: currentStep >= 2, completed: currentStep > 2 }"
          >
            <div class="step-number">2</div>
            <span class="step-label">Order confirmation</span>
          </div>
          <div class="progress-line" :class="{ active: currentStep >= 3 }"></div>
          <div class="progress-step" :class="{ active: currentStep >= 3 }">
            <div class="step-number">3</div>
            <span class="step-label">Payment</span>
          </div>
        </div>
      </div>

      <!-- Main Booking Section -->
      <div class="main-section" v-if="currentStep === 1">
        <div class="booking-container">
          <!-- Left: Date & Time Selection -->
          <div class="selection-panel">
            <!-- Instructions -->
            <div class="instructions-box">
              <h2 class="section-title">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                >
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="2" />
                  <line x1="16" y1="2" x2="16" y2="6" stroke-width="2" />
                  <line x1="8" y1="2" x2="8" y2="6" stroke-width="2" />
                  <line x1="3" y1="10" x2="21" y2="10" stroke-width="2" />
                </svg>
                Select Date & Time
              </h2>
            </div>

            <!-- Date Picker -->
            <div class="picker-section">
              <h3 class="picker-label">
                <span class="label-icon">📅</span>
                Choose Date
              </h3>
              <div class="date-picker">
                <button class="date-nav-btn" @click="previousDate" :disabled="!canGoPrev">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 19l-7-7 7-7"
                    />
                  </svg>
                </button>

                <div class="dates-container">
                  <div
                    v-for="date in visibleDates"
                    :key="date.toISOString()"
                    class="date-card"
                    :class="{ selected: date.toDateString() === selectedDate.toDateString() }"
                    @click="selectDate(date)"
                  >
                    <div class="date-day">{{ formatDateShort(date).day }}</div>
                    <div class="date-number">
                      {{ formatDateShort(date).date }}
                    </div>
                    <div class="date-month">{{ formatDateShort(date).month }}</div>
                  </div>
                </div>

                <button class="date-nav-btn" @click="nextDate" :disabled="!canGoNext">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Time Slots -->
            <div class="picker-section">
              <div class="picker-header">
                <h3 class="picker-label">
                  <span class="label-icon">⏰</span>
                  Choose Time Slots
                </h3>
                <button
                  v-if="selectedTimeSlots.length > 0"
                  class="clear-btn"
                  @click="selectedTimeSlots = []"
                >
                  Clear All
                </button>
              </div>

              <div class="time-slots-grid">
                <button
                  v-for="slot in timeSlots"
                  :key="slot"
                  class="time-slot-btn"
                  :class="{
                    selected: isSlotSelected(slot),
                    disabled: isSlotInPast(slot) || isSlotFullyBooked(slot),
                  }"
                  :disabled="isSlotInPast(slot) || isSlotFullyBooked(slot)"
                  @click="toggleTimeSlot(slot)"
                >
                  <span class="slot-time">{{ slot }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Right: Booking Details -->
          <div class="details-panel">
            <div class="details-card">
              <h3 class="details-title">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
                BOOKING SUMMARY
              </h3>

              <div class="details-content">
                <!-- Date -->
                <div class="detail-group">
                  <div class="detail-label">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                    >
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="2" />
                      <line x1="16" y1="2" x2="16" y2="6" stroke-width="2" />
                      <line x1="8" y1="2" x2="8" y2="6" stroke-width="2" />
                      <line x1="3" y1="10" x2="21" y2="10" stroke-width="2" />
                    </svg>
                    <span>Date</span>
                  </div>
                  <div class="detail-value">{{ formatDateFull(selectedDate) }}</div>
                </div>

                <!-- Time Range -->
                <div class="detail-group" v-if="bookingDetails.startTime">
                  <div class="detail-label">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                    >
                      <circle cx="12" cy="12" r="10" stroke-width="2" />
                      <polyline points="12 6 12 12 16 14" stroke-width="2" />
                    </svg>
                    <span>Time</span>
                  </div>
                  <div class="detail-value time-range">
                    <span class="time-start">{{ bookingDetails.startTime }}</span>
                    <span class="time-separator">→</span>
                    <span class="time-end">{{ bookingDetails.endTime }}</span>
                  </div>
                </div>

                <!-- Duration -->
                <div class="detail-group" v-if="bookingDetails.totalHours > 0">
                  <div class="detail-label">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                    >
                      <circle cx="12" cy="12" r="10" stroke-width="2" />
                      <polyline points="12 6 12 12 16 14" stroke-width="2" />
                    </svg>
                    <span>Duration</span>
                  </div>
                  <div class="detail-value">{{ bookingDetails.totalHours }} hour(s)</div>
                </div>

                <!-- Price Breakdown -->
                <div v-if="bookingDetails.totalPrice > 0" class="price-breakdown">
                  <!-- Show detailed breakdown if multiple price tiers -->
                  <template
                    v-if="bookingDetails.priceBreakdown && bookingDetails.priceBreakdown.length > 1"
                  >
                    <div class="breakdown-header">Price per hour (detailed)</div>
                    <div
                      v-for="(tier, index) in bookingDetails.priceBreakdown"
                      :key="index"
                      class="breakdown-item tier-item"
                    >
                      <span>{{ formatPrice(tier.price) }}/h × {{ tier.hours }}h</span>
                      <span>{{ formatPrice(tier.subtotal) }}</span>
                    </div>
                  </template>

                  <!-- Show simple breakdown if single price tier -->
                  <template v-else>
                    <div class="breakdown-item">
                      <span>Price per hour</span>
                      <span>{{
                        formatPrice(bookingDetails.priceBreakdown?.[0]?.price || 100000)
                      }}</span>
                    </div>
                    <div class="breakdown-item">
                      <span>Duration</span>
                      <span>{{ bookingDetails.totalHours }}h</span>
                    </div>
                  </template>

                  <div class="breakdown-divider"></div>
                  <div class="breakdown-total">
                    <span>Total Amount</span>
                    <span class="total-amount">{{ formatPrice(bookingDetails.totalPrice) }}</span>
                  </div>
                </div>

                <!-- Empty State -->
                <div v-else class="empty-state">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p>Select time slots to see booking details</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 2: Order Confirmation -->
      <div class="main-section" v-if="currentStep === 2">
        <div class="confirmation-container">
          <div class="confirmation-card">
            <!-- Booking Details -->
            <div class="info-section">
              <h3 class="section-heading">BOOKING DETAILS</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>Date</label>
                  <div class="info-value">{{ formatDateForBooking(selectedDate) }}</div>
                </div>
                <div class="info-item">
                  <label>Start time</label>
                  <div class="info-value">{{ bookingDetails.startTime }}</div>
                </div>
                <div class="info-item">
                  <label>End time</label>
                  <div class="info-value">{{ bookingDetails.endTime }}</div>
                </div>
              </div>
            </div>

            <!-- Your Information -->
            <div class="info-section">
              <h3 class="section-heading">YOUR INFORMATION</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>Name</label>
                  <input
                    v-model="userInfo.name"
                    type="text"
                    class="info-input"
                    placeholder="Enter your name"
                  />
                </div>
                <div class="info-item">
                  <label>Email</label>
                  <input
                    v-model="userInfo.email"
                    type="email"
                    class="info-input"
                    placeholder="Enter your email"
                  />
                </div>
                <div class="info-item">
                  <label>Phone</label>
                  <input
                    v-model="userInfo.phone"
                    type="tel"
                    class="info-input"
                    placeholder="Enter your phone number"
                  />
                </div>
              </div>
            </div>

            <!-- Contact Information -->
            <div class="info-section">
              <h3 class="section-heading">CONTACT INFORMATION</h3>
              <div class="info-grid">
                <div class="info-item">
                  <label>Name</label>
                  <div class="info-value">{{ court?.owner?.full_name || 'N/A' }}</div>
                </div>
                <div class="info-item">
                  <label>Email</label>
                  <div class="info-value">{{ court?.contact_email || 'N/A' }}</div>
                </div>
                <div class="info-item">
                  <label>Phone</label>
                  <div class="info-value">{{ court?.contact_phone || 'N/A' }}</div>
                </div>
              </div>
            </div>

            <!-- Payment Information -->
            <div class="info-section payment-section">
              <h3 class="section-heading">PAYMENT INFORMATION</h3>
              <div class="payment-summary">
                <div class="payment-row">
                  <span class="payment-label">Subtotal</span>
                  <span class="payment-value"
                    >{{
                      new Intl.NumberFormat('vi-VN').format(bookingDetails.totalPrice)
                    }}
                    VND</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: Payment -->
      <div class="main-section" v-if="currentStep === 3">
        <div class="payment-container">
          <div class="payment-card">
            <!-- Payment Status Banner -->
            <div class="payment-status-banner" :class="{ verified: paymentVerified }">
              <div class="status-icon">
                <svg
                  v-if="!paymentVerified"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                >
                  <circle cx="12" cy="12" r="10" stroke-width="2" />
                  <polyline points="12 6 12 12 16 14" stroke-width="2" />
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="3"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <div class="status-content">
                <span class="status-badge" v-if="paymentVerified">Verified</span>
                <h3 class="status-title">
                  {{ paymentVerified ? 'Payment Confirmed' : 'Pending Payment' }}
                </h3>
                <p class="status-subtitle">
                  {{
                    paymentVerified
                      ? 'Your transfer has been recorded. Booking is waiting for owner approval.'
                      : 'Please scan the QR code and complete payment'
                  }}
                </p>
              </div>
            </div>

            <!-- Payment Content -->
            <div class="payment-content" v-if="paymentInfo && !paymentVerified">
              <!-- QR Code Section -->
              <div class="qr-section">
                <h3 class="section-heading">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <rect x="3" y="3" width="7" height="7" rx="1" stroke-width="2" />
                    <rect x="14" y="3" width="7" height="7" rx="1" stroke-width="2" />
                    <rect x="14" y="14" width="7" height="7" rx="1" stroke-width="2" />
                    <rect x="3" y="14" width="7" height="7" rx="1" stroke-width="2" />
                  </svg>
                  SCAN QR CODE TO PAY
                </h3>
                <div class="qr-code-container">
                  <img :src="paymentInfo.qr_code_url" alt="QR Code" class="qr-code-image" />
                  <p class="qr-instruction">
                    Open your banking app and scan this QR code to complete payment
                  </p>
                </div>
              </div>

              <!-- Bank Details Section -->
              <div class="bank-details-section">
                <h3 class="section-heading">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                    />
                  </svg>
                  OR TRANSFER MANUALLY
                </h3>

                <div class="bank-info-grid">
                  <div class="bank-info-item">
                    <label>Bank Name</label>
                    <div class="info-value-copy">
                      <span>{{ paymentInfo.bank_name }}</span>
                      <button
                        class="copy-btn"
                        @click="copyToClipboard(paymentInfo.bank_name, 'bank name')"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                        >
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke-width="2" />
                          <path
                            d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                            stroke-width="2"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div class="bank-info-item">
                    <label>Account Number</label>
                    <div class="info-value-copy">
                      <span>{{ paymentInfo.account_number }}</span>
                      <button
                        class="copy-btn"
                        @click="copyToClipboard(paymentInfo.account_number, 'account number')"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                        >
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke-width="2" />
                          <path
                            d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                            stroke-width="2"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div class="bank-info-item">
                    <label>Account Name</label>
                    <div class="info-value-copy">
                      <span>{{ paymentInfo.account_name }}</span>
                      <button
                        class="copy-btn"
                        @click="copyToClipboard(paymentInfo.account_name, 'account name')"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                        >
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke-width="2" />
                          <path
                            d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                            stroke-width="2"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div class="bank-info-item highlight">
                    <label>Amount</label>
                    <div class="info-value-copy">
                      <span class="amount-value"
                        >{{ new Intl.NumberFormat('vi-VN').format(paymentInfo.amount) }} VND</span
                      >
                      <button
                        class="copy-btn"
                        @click="copyToClipboard(paymentInfo.amount.toString(), 'amount')"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                        >
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke-width="2" />
                          <path
                            d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                            stroke-width="2"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Important Notice -->
                <div class="payment-notice">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <div>
                    <strong>Important:</strong> Please scan the QR code or transfer manually with
                    the exact amount shown above. Your booking will be confirmed via email by the
                    owner after they verify the payment. If you have any issues, please contact the
                    owner directly using the contact information provided above.
                  </div>
                </div>

                <!-- Verify Payment Button -->
                <button
                  class="verify-payment-btn"
                  @click="verifyPayment"
                  :disabled="isVerifyingPayment"
                >
                  <svg
                    v-if="!isVerifyingPayment"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
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
                  {{ isVerifyingPayment ? 'Verifying...' : 'I have completed the payment' }}
                </button>
              </div>
            </div>

            <!-- Success State -->
            <div class="payment-success" v-if="paymentVerified">
              <div class="success-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="3"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h2>Booking Submitted Successfully</h2>
              <p class="success-main-text">Your payment information has been recorded.</p>
              <div class="success-info-box">
                <div class="info-icon-wrap email" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 6h16v12H4z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 8l8 6 8-6"
                    />
                  </svg>
                </div>
                <div class="success-copy">
                  <h4>Email Confirmation</h4>
                  <p class="success-description">
                    Please check your <strong>email</strong> to receive final confirmation after the
                    owner verifies your transfer.
                  </p>
                </div>
              </div>
              <div class="success-info-box secondary">
                <div class="info-icon-wrap status" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="9" stroke-width="2" />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 7v5l3 2"
                    />
                  </svg>
                </div>
                <div class="success-copy">
                  <h4>Booking Status</h4>
                  <p class="success-description">
                    Current booking state is <strong>Pending confirmation</strong>. Approval is
                    usually completed shortly.
                  </p>
                </div>
              </div>
              <div class="booking-id-display" v-if="bookingId">
                <span class="label">Booking reference</span>
                <span class="value">#{{ bookingId }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Buttons -->
      <div
        class="navigation-section"
        v-if="currentStep < 3 || (currentStep === 3 && !paymentVerified)"
      >
        <div class="navigation-container">
          <button class="nav-btn btn-back" @click="goBack">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back
          </button>
          <button
            v-if="currentStep < 3"
            class="nav-btn btn-next"
            @click="goNext"
            :disabled="isCreatingBooking"
          >
            <span v-if="!isCreatingBooking">Next</span>
            <span v-else>Creating Booking...</span>
            <svg
              v-if="!isCreatingBooking"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M14 5l7 7m0 0l-7 7m7-7H3"
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
          </button>
        </div>
      </div>
    </div>

    <AppFooter />
  </div>
</template>

<style scoped>
.booking-page {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #2d5016;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Banner */
.banner-section {
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: #1f2937;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.7;
}

/* Progress Indicator */
.progress-section {
  background: white;
  padding: 30px 40px;
  border-bottom: 1px solid #e5e7eb;
}

.progress-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #d1d5db;
  color: #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 700;
  transition: all 0.3s;
}

.progress-step.active .step-number,
.progress-step.completed .step-number {
  background: #2d5016;
  color: white;
}

.step-label {
  font-size: 0.9rem;
  color: #6b7280;
  font-weight: 500;
}

.progress-step.active .step-label {
  color: #2d5016;
  font-weight: 700;
}

.progress-line {
  width: 100px;
  height: 3px;
  background: #d1d5db;
  transition: all 0.3s;
}

.progress-line.active {
  background: #2d5016;
}

/* Main Section */
.main-section {
  padding: 40px;
  background: #f8f9fa;
}

.booking-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 40px;
}

/* Selection Panel */
.selection-panel {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* Instructions Box */
.instructions-box {
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border-left: 4px solid #2d5016;
  padding: 20px 24px;
  border-radius: 12px;
  margin-bottom: 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.3rem;
  font-weight: 800;
  color: #2d5016;
  margin: 0;
}

.section-title svg {
  width: 24px;
  height: 24px;
  stroke-width: 2.5;
}

/* Picker Section */
.picker-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 2px solid #f3f4f6;
}

.picker-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.picker-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 20px 0;
}

.label-icon {
  font-size: 1.3rem;
}

.clear-btn {
  padding: 8px 16px;
  background: #fee2e2;
  color: #991b1b;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.clear-btn:hover {
  background: #fecaca;
  transform: translateY(-1px);
}

/* Date Picker */
.date-picker {
  display: flex;
  align-items: center;
  gap: 16px;
}

.date-nav-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid #e5e7eb;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  flex-shrink: 0;
}

.date-nav-btn:not(:disabled):hover {
  border-color: #2d5016;
  background: #f0fdf4;
}

.date-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.date-nav-btn svg {
  width: 20px;
  height: 20px;
  color: #2d5016;
}

.dates-container {
  display: flex;
  gap: 12px;
  flex: 1;
  overflow-x: auto;
  scroll-behavior: smooth;
}

.date-card {
  flex: 1;
  min-width: 80px;
  padding: 16px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.date-card:hover {
  border-color: #2d5016;
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(45, 80, 22, 0.15);
}

.date-card.selected {
  background: linear-gradient(135deg, #2d5016 0%, #3d6620 100%);
  border-color: #2d5016;
  color: white;
  box-shadow: 0 6px 16px rgba(45, 80, 22, 0.3);
}

.date-day {
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 8px;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.date-number {
  font-size: 1.8rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 4px;
}

.date-month {
  font-size: 0.85rem;
  font-weight: 600;
  opacity: 0.9;
}

/* Time Slots Grid */
.time-slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 12px;
}

.time-slot-btn {
  padding: 18px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 56px;
}

.time-slot-btn:hover:not(:disabled) {
  border-color: #2d5016;
  background: #f0fdf4;
  transform: translateY(-2px);
  box-shadow: 0 3px 10px rgba(45, 80, 22, 0.15);
}

.time-slot-btn.selected {
  background: linear-gradient(135deg, #2d5016 0%, #3d6620 100%);
  border-color: #2d5016;
  box-shadow: 0 3px 10px rgba(45, 80, 22, 0.3);
}

.time-slot-btn.disabled,
.time-slot-btn:disabled {
  background: #f3f4f6;
  border-color: #e5e7eb;
  cursor: not-allowed;
  opacity: 0.5;
}

.time-slot-btn.disabled .slot-time,
.time-slot-btn:disabled .slot-time {
  color: #9ca3af;
  text-decoration: line-through;
}

.slot-time {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
}

.time-slot-btn.selected .slot-time {
  color: white;
  font-weight: 800;
}

/* Details Panel */
.details-panel {
  position: sticky;
  top: 100px;
  height: fit-content;
}

.details-card {
  background: white;
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.details-title {
  font-size: 1rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  padding: 1.5rem 2rem;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  letter-spacing: 0.5px;
}

.details-title svg {
  width: 24px;
  height: 24px;
  stroke-width: 2;
}

.details-content {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-label svg {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

.detail-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a1a1a;
  padding-left: 1.5rem;
}

.time-range {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.time-start,
.time-end {
  padding: 0.5rem 1rem;
  background: #f0f9ff;
  border-radius: 8px;
  color: #2563eb;
  font-weight: 600;
}

.time-separator {
  color: #2563eb;
  font-weight: 700;
  font-size: 1.2rem;
}

.price-breakdown {
  margin-top: 1rem;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.breakdown-header {
  font-size: 0.85rem;
  font-weight: 700;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
  color: #4b5563;
}

.breakdown-item.tier-item {
  padding-left: 0.75rem;
  border-left: 3px solid #e5e7eb;
  margin-bottom: 0.5rem;
}

.breakdown-item span:last-child {
  font-weight: 600;
  color: #1a1a1a;
}

.breakdown-divider {
  height: 1px;
  background: linear-gradient(to right, transparent, #e5e7eb, transparent);
  margin: 0.5rem 0;
}

.breakdown-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 2px solid #2563eb;
}

.breakdown-total span:first-child {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a1a;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.total-amount {
  font-size: 1.75rem;
  font-weight: 800;
  color: #2563eb;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #9ca3af;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  opacity: 0.3;
  stroke-width: 1.5;
}

.empty-state p {
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Navigation */
.navigation-section {
  padding: 30px 40px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.navigation-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.nav-btn {
  padding: 14px 32px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
}

.nav-btn svg {
  width: 20px;
  height: 20px;
}

.btn-back {
  background: #e5e7eb;
  color: #1f2937;
}

.btn-back:hover {
  background: #d1d5db;
  transform: translateX(-4px);
}

.btn-next {
  background: #0a2463;
  color: white;
}

.btn-next:hover {
  background: #0d3380;
  transform: translateX(4px);
}

.btn-next:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
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

/* Order Confirmation (Step 2) */
.confirmation-container {
  max-width: 800px;
  margin: 0 auto;
}

.confirmation-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.info-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 2px solid #f3f4f6;
}

.info-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.section-heading {
  font-size: 1rem;
  font-weight: 700;
  color: #0a2463;
  margin: 0 0 24px 0;
  letter-spacing: 0.5px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #6b7280;
}

.info-value {
  font-size: 1rem;
  font-weight: 500;
  color: #1f2937;
  padding: 12px 0;
}

.info-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  color: #1f2937;
  transition: all 0.3s;
  background: white;
}

.info-input:focus {
  outline: none;
  border-color: #0a2463;
  box-shadow: 0 0 0 3px rgba(10, 36, 99, 0.1);
}

.info-input::placeholder {
  color: #9ca3af;
}

.payment-section {
  background: #f8fafc;
  padding: 24px;
  border-radius: 12px;
  margin-top: 32px;
}

.payment-section .section-heading {
  margin-bottom: 16px;
}

.payment-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.payment-label {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.payment-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0a2463;
}

/* Payment Section (Step 3) */
.payment-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
}

.payment-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.payment-status-banner {
  background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
  padding: 28px 36px;
  display: flex;
  align-items: center;
  gap: 24px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.payment-status-banner::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.3;
  }
}

.payment-status-banner.verified {
  background: linear-gradient(135deg, #059669 0%, #0f766e 100%);
}

.payment-status-banner.verified::before {
  animation: none;
}

.status-icon {
  width: 68px;
  height: 68px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.status-icon svg {
  width: 38px;
  height: 38px;
  color: white;
  stroke-width: 2.5;
}

.status-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  margin-bottom: 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.35);
  color: #ecfeff;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}

.status-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: white;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-subtitle {
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  font-weight: 500;
}

.payment-content {
  padding: 48px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  background: linear-gradient(to bottom, #f8fafc 0%, white 100%);
}

.section-heading {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1rem;
  font-weight: 800;
  color: #1e293b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 3px solid #e2e8f0;
}

.section-heading svg {
  width: 24px;
  height: 24px;
  color: #16a34a;
  stroke-width: 2.5;
}

.qr-section,
.bank-details-section {
  display: flex;
  flex-direction: column;
}

.qr-code-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 32px;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border-radius: 16px;
  border: 3px dashed #86efac;
  box-shadow: 0 4px 16px rgba(34, 197, 94, 0.1);
  transition: all 0.3s;
}

.qr-code-container:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(34, 197, 94, 0.15);
}

.qr-code-image {
  width: 100%;
  max-width: 360px;
  height: auto;
  border-radius: 12px;
  background: white;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transition: all 0.3s;
}

.qr-code-image:hover {
  transform: scale(1.02);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.qr-instruction {
  text-align: center;
  font-size: 0.95rem;
  color: #16a34a;
  font-weight: 600;
  line-height: 1.6;
  margin: 0;
}

.bank-info-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bank-info-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all 0.3s;
}

.bank-info-item:hover {
  transform: translateY(-2px);
}

.bank-info-item.highlight {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  padding: 16px;
  border-radius: 12px;
  border: 2px solid #fbbf24;
  box-shadow: 0 4px 16px rgba(251, 191, 36, 0.2);
}

.bank-info-item label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value-copy {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  transition: all 0.2s;
}

.info-value-copy:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.bank-info-item.highlight .info-value-copy {
  border-color: #fbbf24;
  background: rgba(255, 255, 255, 0.9);
}

.amount-value {
  color: #dc2626;
  font-size: 1.4rem;
  font-weight: 900;
}

.content-value {
  font-family: 'Courier New', monospace;
  color: #dc2626;
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: 1px;
}

.copy-btn {
  padding: 10px;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.copy-btn:hover {
  background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
}

.copy-btn:hover svg {
  color: white;
}

.copy-btn:active {
  transform: scale(0.95);
}

.copy-btn svg {
  width: 20px;
  height: 20px;
  color: #64748b;
  stroke-width: 2;
  transition: color 0.2s;
}

.help-text {
  font-size: 0.85rem;
  color: #92400e;
  margin: 8px 0 0 0;
  line-height: 1.5;
  font-weight: 600;
}

.payment-notice {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border: 2px solid #60a5fa;
  border-radius: 10px;
  margin-top: 24px;
  color: #1e40af;
  font-size: 0.9rem;
  line-height: 1.6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.payment-notice svg {
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  stroke-width: 2.5;
  color: #2563eb;
}

.payment-notice strong {
  color: #1e3a8a;
  font-weight: 800;
}

.verify-payment-btn {
  width: 100%;
  padding: 18px 28px;
  background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.15rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 28px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 16px rgba(22, 163, 74, 0.3);
  position: relative;
  overflow: hidden;
}

.verify-payment-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition:
    width 0.6s,
    height 0.6s;
}

.verify-payment-btn:hover:not(:disabled)::before {
  width: 400px;
  height: 400px;
}

.verify-payment-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 6px 24px rgba(22, 163, 74, 0.4);
}

.verify-payment-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.verify-payment-btn svg {
  width: 24px;
  height: 24px;
  stroke-width: 2;
}

.payment-success {
  padding: 60px 40px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  animation: fadeIn 0.6s ease-out;
  background:
    radial-gradient(circle at 8% 10%, rgba(6, 182, 212, 0.08), transparent 28%),
    radial-gradient(circle at 92% 86%, rgba(14, 165, 233, 0.09), transparent 32%), #f8fafc;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.success-icon {
  width: 104px;
  height: 104px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: scaleIn 0.5s ease-out;
  box-shadow: 0 10px 40px rgba(16, 185, 129, 0.3);
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.success-icon svg {
  width: 56px;
  height: 56px;
  color: white;
  stroke-width: 3;
}

.payment-success h2 {
  font-size: 1.95rem;
  font-weight: 800;
  color: #0f766e;
  margin: 0;
}

.success-main-text {
  font-size: 1.12rem;
  color: #0f766e;
  font-weight: 700;
  margin: 0;
}

.success-info-box {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 18px;
  background: linear-gradient(135deg, #e0f2fe 0%, #eff6ff 100%);
  border-radius: 12px;
  border: 1px solid #bfdbfe;
  max-width: 540px;
  width: 100%;
  text-align: left;
  animation: slideIn 0.6s ease-out 0.25s both;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.1);
}

.success-info-box.secondary {
  background: linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%);
  border-color: #fde68a;
  animation-delay: 0.4s;
  box-shadow: 0 8px 24px rgba(217, 119, 6, 0.12);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.info-icon-wrap {
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: #2563eb;
  color: #ffffff;
  flex-shrink: 0;
  box-shadow: 0 8px 16px rgba(37, 99, 235, 0.2);
}

.info-icon-wrap svg {
  width: 22px;
  height: 22px;
}

.success-info-box.secondary .info-icon-wrap {
  background: #d97706;
  box-shadow: 0 8px 16px rgba(217, 119, 6, 0.2);
}

.success-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.success-copy h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: #1e293b;
}

.success-description {
  font-size: 0.95rem;
  color: #374151;
  margin: 0;
  line-height: 1.55;
}

.success-description strong {
  color: #1e293b;
  font-weight: 700;
}

.booking-id-display {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 14px 22px;
  background: #ffffff;
  border-radius: 10px;
  border: 1px dashed #93c5fd;
  margin-top: 8px;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.08);
}

.booking-id-display .label {
  font-size: 0.78rem;
  color: #475569;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.booking-id-display .value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #2563eb;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
}

/* Responsive */
@media (max-width: 1024px) {
  .booking-container {
    grid-template-columns: 1fr;
  }

  .details-panel {
    position: static;
  }
}

@media (max-width: 768px) {
  .main-section,
  .navigation-section {
    padding: 20px;
  }

  .selection-panel {
    padding: 20px;
  }

  .time-slots-grid {
    grid-template-columns: repeat(auto-fill, minmax(85px, 1fr));
    gap: 8px;
  }

  .progress-container {
    gap: 12px;
  }

  .progress-line {
    width: 60px;
  }

  .step-label {
    font-size: 0.8rem;
  }

  .section-title {
    font-size: 1.1rem;
  }

  .instructions-box {
    padding: 16px 20px;
  }

  .date-card {
    min-width: 80px;
    padding: 12px 8px;
  }

  .date-number {
    font-size: 1.5rem;
  }

  .picker-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .date-picker {
    gap: 10px;
  }

  .date-nav-btn {
    width: 38px;
    height: 38px;
  }

  .date-nav-btn svg {
    width: 18px;
    height: 18px;
  }

  .time-slot-btn {
    min-height: 48px;
    padding: 12px 8px;
  }

  .slot-time {
    font-size: 0.92rem;
  }

  .navigation-container {
    flex-direction: column;
  }

  .nav-btn {
    width: 100%;
    justify-content: center;
  }

  .details-title {
    padding: 1rem 1.25rem;
    font-size: 0.92rem;
    gap: 0.5rem;
  }

  .details-title svg {
    width: 20px;
    height: 20px;
  }

  .details-content {
    padding: 1rem;
    gap: 1rem;
  }

  .detail-value {
    padding-left: 0;
    font-size: 0.95rem;
    word-break: break-word;
  }

  .time-range {
    flex-wrap: wrap;
    gap: 0.4rem;
  }

  .price-breakdown {
    padding: 1rem;
  }

  .breakdown-item {
    gap: 10px;
    align-items: flex-start;
  }

  .breakdown-item span:first-child {
    flex: 1;
    min-width: 0;
    word-break: break-word;
  }

  .breakdown-item span:last-child {
    white-space: nowrap;
  }

  .breakdown-total {
    gap: 10px;
    align-items: flex-start;
  }

  .total-amount {
    font-size: 1.35rem;
    white-space: nowrap;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .confirmation-card {
    padding: 24px;
  }

  .payment-content {
    grid-template-columns: 1fr;
    padding: 24px;
    gap: 32px;
  }

  .success-info-box {
    align-items: flex-start;
  }

  .bank-info-grid {
    gap: 14px;
  }

  .qr-code-image {
    max-width: 280px;
  }

  .payment-container {
    padding: 12px;
  }

  .payment-status-banner {
    padding: 20px;
    gap: 16px;
  }

  .status-icon {
    width: 56px;
    height: 56px;
  }

  .status-icon svg {
    width: 32px;
    height: 32px;
  }

  .status-title {
    font-size: 1.3rem;
  }

  .status-subtitle {
    font-size: 0.95rem;
  }

  .payment-content {
    padding: 28px 20px;
  }

  .section-heading {
    font-size: 0.9rem;
  }

  .section-heading svg {
    width: 20px;
    height: 20px;
  }

  .qr-code-container {
    padding: 24px 16px;
  }

  .bank-info-item.highlight {
    padding: 16px;
  }

  .payment-notice {
    padding: 16px;
    font-size: 0.88rem;
  }

  .verify-payment-btn {
    padding: 16px 20px;
    font-size: 1.05rem;
  }
}

@media (max-width: 480px) {
  .main-section,
  .navigation-section {
    padding: 14px 10px;
  }

  .selection-panel {
    padding: 14px;
  }

  .time-slots-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
  }

  .dates-container {
    gap: 6px;
  }

  .date-card {
    min-width: 64px;
    padding: 8px 5px;
  }

  .date-number {
    font-size: 1.15rem;
  }

  .section-title {
    font-size: 1rem;
  }

  .picker-label {
    font-size: 1rem;
  }

  .details-title {
    padding: 0.85rem 0.9rem;
    font-size: 0.84rem;
  }

  .details-content {
    padding: 0.85rem;
    gap: 0.85rem;
  }

  .detail-label {
    font-size: 0.75rem;
  }

  .detail-value {
    font-size: 0.88rem;
  }

  .time-start,
  .time-end {
    padding: 0.4rem 0.6rem;
    font-size: 0.84rem;
  }

  .price-breakdown {
    padding: 0.85rem;
  }

  .breakdown-header,
  .breakdown-item {
    font-size: 0.8rem;
  }

  .breakdown-total span:first-child {
    font-size: 0.85rem;
  }

  .total-amount {
    font-size: 1.12rem;
  }

  .confirmation-card {
    padding: 20px;
  }

  .section-heading {
    font-size: 0.9rem;
  }

  .time-slot-btn {
    min-height: 44px;
    padding: 10px 6px;
  }

  .slot-time {
    font-size: 0.84rem;
  }

  .payment-status-banner {
    padding: 14px 12px;
    gap: 10px;
  }

  .status-icon {
    width: 44px;
    height: 44px;
  }

  .status-icon svg {
    width: 24px;
    height: 24px;
  }

  .status-title {
    font-size: 1.02rem;
  }

  .status-subtitle {
    font-size: 0.82rem;
  }

  .payment-content {
    padding: 14px 10px;
    gap: 18px;
  }

  .qr-code-container {
    padding: 14px 10px;
  }

  .qr-code-image {
    max-width: 220px;
    padding: 10px;
  }

  .verify-payment-btn {
    font-size: 0.92rem;
    padding: 12px 14px;
  }
}
</style>
