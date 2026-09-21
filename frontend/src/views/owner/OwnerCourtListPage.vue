<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import axiosInstance from '@/utils/axios'

const toast = useToast()

interface Court {
  id: number
  name: string
  address: string
  ward: string
  city: string
  court_quantity: number
  opening_time: string
  closing_time: string
  individual_courts?: IndividualCourt[]
}

interface Booking {
  id: number
  booking_date: string
  start_time: string
  end_time: string
  phone_number: string
  status: string
  booking_status?: string
}

interface IndividualCourt {
  id: number
  court_id: number
  name: string
  is_available: boolean
  bookings?: Booking[]
}

interface CourtItem {
  id: number
  name: string
  isBooked: boolean
  bookedBy?: {
    phone: string
    timeSlot: string
    bookingDate: string
  }
  bookingId?: number
  isEditing: boolean
  tempName: string
}

interface BookingForm {
  booking_date: string
  start_time: string
  end_time: string
  phone_number: string
  customer_name: string
}

interface SuggestedCourt {
  id: number
  name: string
  court_name: string
}

const getNormalizedBookingStatus = (booking: Booking): string => {
  const status = (booking.status || '').toString().trim().toLowerCase()
  const bookingStatus = (booking.booking_status || '').toString().trim().toLowerCase()
  return bookingStatus || status
}

const getLocalDateString = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const isBookingCurrentlyInProgress = (booking: Booking): boolean => {
  const now = new Date()
  const today = getLocalDateString(now)
  const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`

  const bookingDate = booking.booking_date?.split('T')[0]

  // Check if booking is today and within time range
  if (bookingDate === today) {
    return booking.start_time <= currentTime && currentTime < booking.end_time
  }

  return false
}

const isActiveBooking = (booking: Booking): boolean => {
  const status = getNormalizedBookingStatus(booking)
  // Consider booking active if:
  // 1. Status is 'active' OR
  // 2. Status is 'confirmed' and it's currently within booking time range
  return status === 'active' || (status === 'confirmed' && isBookingCurrentlyInProgress(booking))
}

// Real data from API
const courts = ref<CourtItem[]>([])
const isLoading = ref(false)
const venueInfo = ref({
  name: 'No courts yet',
  totalCourts: 0,
  opening_time: '06:00',
  closing_time: '22:00',
})
const myVenues = ref<Court[]>([])

// Booking form state
const bookingForms = ref<Record<number, BookingForm>>({})
const isEditingBooking = ref<Record<number, boolean>>({})

// Suggested courts when conflict
const suggestedCourts = ref<SuggestedCourt[]>([])
const showSuggestionModal = ref(false)
const currentConflictCourtId = ref<number | null>(null)
const pendingBookingData = ref<unknown>(null)

// Initialize booking form for a court
const initBookingForm = (courtId: number) => {
  bookingForms.value[courtId] = {
    booking_date: '',
    start_time: '',
    end_time: '',
    phone_number: '',
    customer_name: '',
  }
}

// Initialize booking form with existing booking data
const initEditBookingForm = (court: CourtItem) => {
  if (court.bookedBy) {
    // Convert date format from "dd/mm/yyyy" to "yyyy-mm-dd"
    const dateParts = court.bookedBy.bookingDate.split('/')
    const formattedDate = `${dateParts[2]}-${dateParts[1].padStart(2, '0')}-${dateParts[0].padStart(2, '0')}`

    // Extract start and end time from timeSlot "HH:MM - HH:MM"
    const [startTime, endTime] = court.bookedBy.timeSlot.split(' - ')

    bookingForms.value[court.id] = {
      booking_date: formattedDate,
      start_time: startTime.trim(),
      end_time: endTime.trim(),
      phone_number: court.bookedBy.phone,
      customer_name: '',
    }
    isEditingBooking.value[court.id] = true
    court.isEditing = true
  }
}

// Generate courts based on quantity
const generateCourts = (quantity: number) => {
  const newCourts: CourtItem[] = []
  for (let i = 1; i <= quantity; i++) {
    newCourts.push({
      id: i,
      name: `Court ${i}`,
      isBooked: false,
      isEditing: false,
      tempName: `Court ${i}`,
    })
  }
  return newCourts
}

// Check if court is actually booked at current time
const checkAndUpdateExpiredBookings = (courtData: IndividualCourt[]) => {
  const now = new Date()
  const today = getLocalDateString(now)
  const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`

  courtData.forEach((ic) => {
    const activeBooking = ic.bookings?.find((b) => isActiveBooking(b))
    if (activeBooking) {
      const bookingDate = activeBooking.booking_date.split('T')[0]

      // Only mark as booked if:
      // 1. Booking date is TODAY
      // 2. Current time is WITHIN booking time range (start_time <= currentTime < end_time)
      if (bookingDate === today) {
        const isWithinTimeRange =
          activeBooking.start_time <= currentTime && currentTime < activeBooking.end_time

        if (isWithinTimeRange) {
          // Court is currently being used
          ic.is_available = false
          console.log(`🎾 Sân ${ic.name} đang được sử dụng:`, {
            bookingDate,
            timeRange: `${activeBooking.start_time} - ${activeBooking.end_time}`,
            currentTime,
          })
        } else {
          // Booking exists but not in active time range yet or already passed
          ic.is_available = true
          if (activeBooking.end_time < currentTime) {
            console.log(`⏰ Booking expired for court ${ic.name}:`, {
              bookingDate,
              endTime: activeBooking.end_time,
              currentTime,
            })
          } else {
            console.log(`⏳ Booking chưa bắt đầu cho sân ${ic.name}:`, {
              startTime: activeBooking.start_time,
              currentTime,
            })
          }
        }
      }
      // Booking date is in the future - court is available now
      else if (bookingDate > today) {
        console.log(`📅 Booking trong tương lai cho sân ${ic.name}:`, bookingDate)
        ic.is_available = true
      }
      // Booking date is in the past - court is available
      else if (bookingDate < today) {
        console.log(`📅 Booking đã qua cho sân ${ic.name}:`, bookingDate)
        ic.is_available = true
      }
    } else {
      // No active booking - court is available
      ic.is_available = true
    }
  })

  return courtData
}

// Fetch courts from API
const fetchMyCourts = async () => {
  isLoading.value = true
  try {
    const response = await axiosInstance.get<Court[]>('/courts/my')
    myVenues.value = response.data

    // If user has venues, show the first one
    if (myVenues.value.length > 0) {
      const firstVenue = myVenues.value[0]
      venueInfo.value = {
        name: firstVenue.name,
        totalCourts: firstVenue.court_quantity,
        opening_time: firstVenue.opening_time,
        closing_time: firstVenue.closing_time,
      }

      // Fetch individual courts with bookings for detailed info
      try {
        const detailResponse = await axiosInstance.get<IndividualCourt[]>(
          `/courts/${firstVenue.id}/individual-courts`,
        )

        console.log('📊 Individual courts data:', detailResponse.data)

        // Check and update expired bookings before processing
        const updatedCourts = checkAndUpdateExpiredBookings(detailResponse.data)

        courts.value = updatedCourts.map((ic) => {
          const activeBooking = ic.bookings?.find((b) => isActiveBooking(b))

          // Use is_available from checkAndUpdateExpiredBookings
          // Only show as booked if court is NOT available (currently in use)
          const isCurrentlyBooked = !ic.is_available

          console.log(`⚽ Sân ${ic.name}:`, {
            is_available: ic.is_available,
            isCurrentlyBooked,
            activeBooking,
          })

          return {
            id: ic.id,
            name: ic.name,
            isBooked: isCurrentlyBooked,
            bookedBy:
              activeBooking && isCurrentlyBooked
                ? {
                    phone: activeBooking.phone_number,
                    timeSlot: `${activeBooking.start_time} - ${activeBooking.end_time}`,
                    bookingDate: new Intl.DateTimeFormat('vi-VN', {
                      timeZone: 'Asia/Ho_Chi_Minh',
                    }).format(new Date(activeBooking.booking_date)),
                  }
                : undefined,
            bookingId: activeBooking?.id,
            isEditing: false,
            tempName: ic.name,
          }
        })
      } catch (detailError) {
        console.error('Error fetching individual courts details:', detailError)
        // Fallback to basic info
        if (firstVenue.individual_courts) {
          courts.value = firstVenue.individual_courts.map((ic) => ({
            id: ic.id,
            name: ic.name,
            isBooked: !ic.is_available,
            isEditing: false,
            tempName: ic.name,
          }))
        } else {
          courts.value = generateCourts(firstVenue.court_quantity)
        }
      }
    } else {
      courts.value = []
    }
  } catch (error) {
    console.error('Error fetching courts:', error)
    const err = error as { response?: { data?: { detail?: string } } }
    toast.error(err.response?.data?.detail || 'Unable to load court list')
  } finally {
    isLoading.value = false
  }
}

// Initialize courts on mount
onMounted(() => {
  fetchMyCourts()
})

const availableCourts = computed(() => courts.value.filter((c) => !c.isBooked).length)
const bookedCourts = computed(() => courts.value.filter((c) => c.isBooked).length)

const startEditCourtName = (court: CourtItem) => {
  court.isEditing = true
  court.tempName = court.name
  // Initialize booking form if court is available
  if (!court.isBooked) {
    initBookingForm(court.id)
  }
}

const cancelEditCourtName = (court: CourtItem) => {
  court.isEditing = false
  court.tempName = court.name
  // Clear booking form and edit mode
  delete bookingForms.value[court.id]
  delete isEditingBooking.value[court.id]
}

const saveCourtName = async (court: CourtItem) => {
  if (!court.tempName.trim()) {
    toast.error('Court name cannot be empty')
    return
  }

  try {
    // If booking form exists (either creating or editing), validate first
    if (bookingForms.value[court.id]) {
      const form = bookingForms.value[court.id]

      // Validate booking form if any field is filled
      const hasBookingData =
        form.booking_date || form.start_time || form.end_time || form.phone_number

      if (hasBookingData) {
        // Validate all fields are filled
        if (!form.booking_date || !form.start_time || !form.end_time || !form.phone_number) {
          toast.error('Please complete all booking information')
          return
        }

        // Validate phone number
        if (!/^\d{10}$/.test(form.phone_number)) {
          toast.error('Phone number must contain 10 digits')
          return
        }

        // Validate booking date and time is not in the past
        const now = new Date()
        const bookingDate = new Date(form.booking_date)
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        const selectedDate = new Date(
          bookingDate.getFullYear(),
          bookingDate.getMonth(),
          bookingDate.getDate(),
        )

        // Check if booking date is in the past
        if (selectedDate < today) {
          toast.error('Cannot book a court for a past date')
          return
        }

        // If booking is today, check if start time has already passed
        if (selectedDate.getTime() === today.getTime()) {
          const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
          if (form.start_time <= currentTime) {
            toast.error(
              'Cannot book a past time. Please choose a start time after the current time',
            )
            return
          }
        }

        // Validate time range
        if (form.end_time <= form.start_time) {
          toast.error('End time must be later than start time')
          return
        }

        // Validate minimum 1 hour duration
        const startTimeParts = form.start_time.split(':')
        const endTimeParts = form.end_time.split(':')
        const startMinutes = parseInt(startTimeParts[0]) * 60 + parseInt(startTimeParts[1])
        const endMinutes = parseInt(endTimeParts[0]) * 60 + parseInt(endTimeParts[1])
        const durationMinutes = endMinutes - startMinutes

        if (durationMinutes < 60) {
          toast.error('Booking duration must be at least 1 hour')
          return
        }

        // Validate time must be on the hour (:00) or half hour (:30)
        const startMinutesPart = parseInt(startTimeParts[1])
        const endMinutesPart = parseInt(endTimeParts[1])

        if (![0, 30].includes(startMinutesPart) || ![0, 30].includes(endMinutesPart)) {
          toast.error('Booking time must be on half-hour marks (e.g. 10:00, 10:30, 11:00, 11:30)')
          return
        }

        // Validate booking time within opening hours
        if (
          form.start_time < venueInfo.value.opening_time ||
          form.end_time > venueInfo.value.closing_time
        ) {
          toast.error(
            `Booking time must be within opening hours (${venueInfo.value.opening_time} - ${venueInfo.value.closing_time})`,
          )
          return
        }

        // Create or update booking
        if (isEditingBooking.value[court.id] && court.bookingId) {
          // Update existing booking
          await axiosInstance.put(`/bookings/${court.bookingId}`, {
            booking_date: bookingDate.toISOString(),
            start_time: form.start_time,
            end_time: form.end_time,
            phone_number: form.phone_number,
            customer_name: form.customer_name,
          })
        } else {
          // Create new booking
          await axiosInstance.post('/bookings', {
            individual_court_id: court.id,
            booking_date: bookingDate.toISOString(),
            start_time: form.start_time,
            end_time: form.end_time,
            phone_number: form.phone_number,
            customer_name: form.customer_name,
          })
        }
      }
    }

    // Update court name only if not in booking edit mode
    if (!isEditingBooking.value[court.id]) {
      await axiosInstance.put(`/individual-courts/${court.id}`, {
        name: court.tempName,
      })
    }

    court.name = court.tempName
    court.isEditing = false
    const wasEditingBooking = isEditingBooking.value[court.id]
    delete bookingForms.value[court.id]
    delete isEditingBooking.value[court.id]

    // Refresh courts list
    await fetchMyCourts()

    const successMessage = wasEditingBooking
      ? 'Booking updated successfully'
      : 'Updated successfully'
    toast.success(successMessage)
  } catch (error) {
    console.error('Error updating court:', error)
    const err = error as { response?: { status?: number; data?: { detail?: unknown } } }

    // Handle booking conflict with suggestions
    if (err.response?.status === 409 && err.response?.data?.detail) {
      const detail = err.response.data.detail as {
        message?: string
        suggested_courts?: Array<{ id: number; name: string; court_name: string }>
      }

      if (detail.suggested_courts && detail.suggested_courts.length > 0) {
        // Store conflict info
        suggestedCourts.value = detail.suggested_courts
        currentConflictCourtId.value = court.id
        pendingBookingData.value = {
          booking_date: new Date(bookingForms.value[court.id].booking_date).toISOString(),
          start_time: bookingForms.value[court.id].start_time,
          end_time: bookingForms.value[court.id].end_time,
          phone_number: bookingForms.value[court.id].phone_number,
          customer_name: bookingForms.value[court.id].customer_name,
        }
        showSuggestionModal.value = true
        toast.warning(detail.message || 'Court is already booked. Please choose another.')
      } else {
        toast.error(detail.message || 'Court is booked and no other courts are available.')
      }
    } else {
      const errorMsg =
        typeof err.response?.data?.detail === 'string' ? err.response.data.detail : 'Update failed'
      toast.error(errorMsg)
    }
  }
}

const getCourtStatusClass = (court: CourtItem) => {
  return court.isBooked ? 'court-booked' : 'court-available'
}

const cancelBooking = async (court: CourtItem) => {
  if (!court.bookingId) {
    toast.error('Booking information not found')
    return
  }

  if (!confirm(`Are you sure you want to cancel booking "${court.name}"?`)) {
    return
  }

  try {
    // Update status to cancelled instead of deleting
    await axiosInstance.put(`/bookings/${court.bookingId}`, { status: 'cancelled' })
    toast.success('Booking cancelled successfully')
    await fetchMyCourts()
  } catch (error) {
    console.error('Error canceling booking:', error)
    const err = error as { response?: { data?: { detail?: string } } }
    toast.error(err.response?.data?.detail || 'Failed to cancel booking')
  }
}

const selectSuggestedCourt = async (suggestedCourtId: number) => {
  if (!pendingBookingData.value) return

  try {
    // Create booking with suggested court
    await axiosInstance.post('/bookings', {
      individual_court_id: suggestedCourtId,
      ...pendingBookingData.value,
    })

    toast.success('Replacement court booked successfully!')

    // Close modal and reset
    showSuggestionModal.value = false
    suggestedCourts.value = []
    currentConflictCourtId.value = null
    pendingBookingData.value = null

    // Refresh courts
    await fetchMyCourts()
  } catch (error) {
    console.error('Error booking suggested court:', error)
    const err = error as { response?: { data?: { detail?: unknown } } }
    toast.error((err.response?.data?.detail as string) || 'Unable to book replacement court')
  }
}

const closeSuggestionModal = () => {
  showSuggestionModal.value = false
  suggestedCourts.value = []
  currentConflictCourtId.value = null
  pendingBookingData.value = null
}

const refreshCourts = async () => {
  await fetchMyCourts()
  toast.success('List refreshed')
}
</script>

<template>
  <div class="court-list-page">
    <!-- Suggestion Modal -->
    <div v-if="showSuggestionModal" class="modal-overlay" @click="closeSuggestionModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>🏟️ Available Court Suggestions</h3>
          <button class="modal-close" @click="closeSuggestionModal">✕</button>
        </div>
        <div class="modal-body">
          <p class="modal-message">
            Your selected court is booked. Here are available courts in the same time slot:
          </p>
          <div class="suggested-courts-list">
            <div
              v-for="court in suggestedCourts"
              :key="court.id"
              class="suggested-court-item"
              @click="selectSuggestedCourt(court.id)"
            >
              <div class="court-info">
                <strong>{{ court.name }}</strong>
                <span class="court-venue">{{ court.court_name }}</span>
              </div>
              <button class="btn-select">Choose this court</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Page Header -->
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
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
          Court List
        </h1>
        <p class="page-subtitle">Manage and monitor your court status</p>
      </div>
      <button class="refresh-btn" @click="refreshCourts" :disabled="isLoading">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          :class="{ 'animate-spin': isLoading }"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon-total">
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
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">Total Courts</span>
          <span class="stat-value">{{ courts.length }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-available">
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
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">Available Courts</span>
          <span class="stat-value">{{ availableCourts }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-booked">
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
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">Booked Courts</span>
          <span class="stat-value">{{ bookedCourts }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-rate">
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
              d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
            />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">Booking Rate</span>
          <span class="stat-value"
            >{{ courts.length > 0 ? Math.round((bookedCourts / courts.length) * 100) : 0 }}%</span
          >
        </div>
      </div>
    </div>

    <!-- Courts Table -->
    <div class="courts-table-container">
      <div class="table-header">
        <h2 class="table-title">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <rect x="4" y="10" width="16" height="8" rx="2" fill="#10b981" />
            <rect x="7" y="6" width="10" height="4" rx="2" fill="#fbbf24" />
            <rect x="9" y="2" width="6" height="4" rx="2" fill="#3b82f6" />
          </svg>
          Court Details
        </h2>
      </div>

      <div class="table-wrapper">
        <table class="courts-table">
          <thead>
            <tr>
              <th>STT</th>
              <th>Court Name</th>
              <th>Status</th>
              <th>Booking Date</th>
              <th>Time Slot</th>
              <th>Customer Phone</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(court, index) in courts" :key="court.id">
              <tr :class="[getCourtStatusClass(court), { 'editing-row': court.isEditing }]">
                <td>{{ index + 1 }}</td>
                <td class="court-name-cell">
                  <template v-if="!court.isEditing">
                    <span class="court-name">{{ court.name }}</span>
                  </template>
                  <template v-else>
                    <input
                      v-model="court.tempName"
                      type="text"
                      class="court-name-input"
                      @keyup.enter="saveCourtName(court)"
                      @keyup.esc="cancelEditCourtName(court)"
                    />
                  </template>
                </td>
                <td>
                  <span
                    class="status-badge"
                    :class="court.isBooked ? 'status-booked' : 'status-available'"
                  >
                    <svg
                      v-if="court.isBooked"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                      />
                    </svg>
                    <svg
                      v-else
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    {{ court.isBooked ? 'Booked' : 'Available' }}
                  </span>
                </td>
                <td>
                  <span v-if="court.isBooked && court.bookedBy" class="booking-date">
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
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    {{ court.bookedBy.bookingDate }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <span v-if="court.isBooked && court.bookedBy" class="time-slot">
                    {{ court.bookedBy.timeSlot }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <a
                    v-if="court.isBooked && court.bookedBy"
                    :href="`tel:${court.bookedBy.phone}`"
                    class="phone-link"
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
                        d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                      />
                    </svg>
                    {{ court.bookedBy.phone }}
                  </a>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <div class="action-buttons">
                    <template v-if="!court.isEditing">
                      <!-- Nếu sân đang được đặt: hiển thị nút Chỉnh sửa đơn và Hủy đơn -->
                      <template v-if="court.isBooked">
                        <button
                          class="btn-edit"
                          @click="initEditBookingForm(court)"
                          title="Edit booking"
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
                              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                            />
                          </svg>
                        </button>
                        <button
                          class="btn-cancel-booking"
                          @click="cancelBooking(court)"
                          title="Cancel booking"
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
                          Cancel booking
                        </button>
                      </template>
                      <!-- Nếu sân trống: hiển thị nút Chỉnh sửa tên sân -->
                      <button
                        v-else
                        class="btn-edit"
                        @click="startEditCourtName(court)"
                        title="Edit"
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
                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                          />
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button class="btn-save" @click="saveCourtName(court)" title="Save">
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
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      </button>
                      <button class="btn-cancel" @click="cancelEditCourtName(court)" title="Cancel">
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
                    </template>
                  </div>
                </td>
              </tr>

              <!-- Booking Form Expansion (for available courts or editing existing booking) -->
              <tr v-if="court.isEditing && bookingForms[court.id]" class="booking-form-row">
                <td colspan="7">
                  <div class="booking-form-container">
                    <div class="booking-form-header">
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
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                        />
                      </svg>
                      <h4>
                        {{
                          isEditingBooking[court.id]
                            ? 'Edit booking'
                            : 'Create customer booking (Optional)'
                        }}
                      </h4>
                    </div>

                    <div class="booking-form-grid">
                      <div class="form-group">
                        <label>
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
                              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                            />
                          </svg>
                          Booking date
                        </label>
                        <input
                          v-model="bookingForms[court.id].booking_date"
                          type="date"
                          class="form-input"
                        />
                      </div>

                      <div class="form-group">
                        <label>
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
                              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                          </svg>
                          Start time
                        </label>
                        <input
                          v-model="bookingForms[court.id].start_time"
                          type="time"
                          class="form-input"
                        />
                      </div>

                      <div class="form-group">
                        <label>
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
                              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                          </svg>
                          End time
                        </label>
                        <input
                          v-model="bookingForms[court.id].end_time"
                          type="time"
                          class="form-input"
                        />
                      </div>

                      <div class="form-group">
                        <label>
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
                              d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                            />
                          </svg>
                          Phone number
                        </label>
                        <input
                          v-model="bookingForms[court.id].phone_number"
                          type="tel"
                          placeholder="Enter 10 digits"
                          maxlength="10"
                          class="form-input"
                        />
                      </div>

                      <div class="form-group">
                        <label>
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
                              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                            />
                          </svg>
                          Customer name
                        </label>
                        <input
                          v-model="bookingForms[court.id].customer_name"
                          type="text"
                          placeholder="Enter customer name"
                          class="form-input"
                        />
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <div v-if="courts.length === 0" class="empty-state">
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
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
          />
        </svg>
        <p class="empty-text">No courts available</p>
        <p class="empty-hint">
          Upload courts and set court quantity to generate the list automatically
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.court-list-page {
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
  display: flex;
  align-items: center;
}

.page-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
  margin: 0;
}

.refresh-btn {
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

.refresh-btn:hover:not(:disabled) {
  border-color: #2d5016;
  color: #2d5016;
  background: #f0fdf4;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn svg {
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.stat-icon-total {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-icon-available {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-icon-booked {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-icon-rate {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1f2937;
}

/* Courts Table */
.courts-table-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.table-header {
  padding: 24px 28px;
  border-bottom: 2px solid #f3f4f6;
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
}

.table-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-title svg {
  width: 28px;
  height: 28px;
}

.table-wrapper {
  overflow-x: auto;
}

.courts-table {
  width: 100%;
  border-collapse: collapse;
}

.courts-table thead {
  background: #f9fafb;
}

.courts-table th {
  padding: 16px 20px;
  text-align: left;
  font-size: 0.85rem;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e5e7eb;
}

.courts-table tbody tr {
  transition: all 0.3s ease;
  border-bottom: 1px solid #f3f4f6;
}

.courts-table tbody tr:hover {
  background: #f9fafb;
}

.courts-table tbody tr.court-available {
  background: linear-gradient(90deg, #f0fdf4 0%, #ffffff 100%);
}

.courts-table tbody tr.court-booked {
  background: linear-gradient(90deg, #fef3c7 0%, #ffffff 100%);
}

.courts-table td {
  padding: 18px 20px;
  font-size: 0.95rem;
  color: #374151;
}

.court-name-cell {
  font-weight: 600;
}

.court-name {
  color: #1f2937;
}

.court-name-input {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid #2d5016;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  outline: none;
  transition: all 0.3s ease;
}

.court-name-input:focus {
  box-shadow: 0 0 0 3px rgba(45, 80, 22, 0.1);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-badge svg {
  width: 16px;
  height: 16px;
}

.status-available {
  background: #dcfce7;
  color: #166534;
}

.status-booked {
  background: #fef3c7;
  color: #92400e;
}

.time-slot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f3f4f6;
  border-radius: 6px;
  font-weight: 600;
  color: #374151;
}

.phone-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #dbeafe;
  border-radius: 6px;
  font-weight: 600;
  color: #1e40af;
  text-decoration: none;
  transition: all 0.3s ease;
}

.phone-link:hover {
  background: #3b82f6;
  color: white;
}

.phone-link svg {
  width: 14px;
  height: 14px;
}

.booking-date {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #fef3c7;
  border-radius: 6px;
  font-weight: 600;
  color: #92400e;
}

.booking-date svg {
  width: 14px;
  height: 14px;
}

.text-muted {
  color: #9ca3af;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-edit,
.btn-save,
.btn-cancel {
  width: 36px;
  height: 36px;
  padding: 0;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-edit:hover {
  background: #dbeafe;
  border-color: #3b82f6;
}

.btn-edit svg {
  width: 18px;
  height: 18px;
  color: #3b82f6;
}

.btn-save:hover {
  background: #dcfce7;
  border-color: #10b981;
}

.btn-save svg {
  width: 18px;
  height: 18px;
  color: #10b981;
}

.btn-cancel:hover {
  background: #fee2e2;
  border-color: #ef4444;
}

.btn-cancel svg {
  width: 18px;
  height: 18px;
  color: #ef4444;
}

.btn-cancel-booking {
  padding: 8px 14px;
  border: 2px solid #ef4444;
  border-radius: 8px;
  background: white;
  color: #ef4444;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-cancel-booking:hover {
  background: #ef4444;
  color: white;
}

.btn-cancel-booking svg {
  width: 16px;
  height: 16px;
}

/* Empty State */
.empty-state {
  padding: 64px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  text-align: center;
}

.empty-state svg {
  width: 80px;
  height: 80px;
  color: #d1d5db;
}

.empty-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #6b7280;
  margin: 0;
}

.empty-hint {
  font-size: 0.95rem;
  color: #9ca3af;
  margin: 0;
  max-width: 400px;
}

/* Editing Row Highlight */
.editing-row {
  background: linear-gradient(90deg, #dbeafe 0%, #ffffff 100%) !important;
  border-left: 4px solid #3b82f6;
}

/* Booking Form Expansion Row */
.booking-form-row {
  background: #f8fafc;
  border-bottom: 2px solid #e5e7eb;
}

.booking-form-container {
  padding: 24px;
  background: white;
  border-radius: 12px;
  margin: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.booking-form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.booking-form-header svg {
  width: 24px;
  height: 24px;
  color: #3b82f6;
}

.booking-form-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
}

.booking-form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 6px;
}

.form-group label svg {
  width: 16px;
  height: 16px;
  color: #6b7280;
}

.form-input {
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s ease;
}

.form-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .page-header h1 {
    font-size: 1.75rem;
  }

  .courts-table {
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 20px 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .add-btn {
    width: 100%;
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 1.75rem;
  }

  .stat-label {
    font-size: 0.85rem;
  }

  .section-card {
    padding: 20px;
  }

  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .courts-table {
    min-width: 640px;
    font-size: 13px;
  }

  .courts-table th,
  .courts-table td {
    padding: 10px 8px;
  }

  .booking-form-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .modal-content {
    width: 95%;
    max-width: none;
    margin: 20px auto;
    max-height: 90vh;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .modal-body {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 16px 12px;
  }

  .page-header h1 {
    font-size: 1.35rem;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .stat-label {
    font-size: 0.8rem;
  }

  .section-card {
    padding: 16px;
  }

  .courts-table {
    font-size: 12px;
    min-width: 560px;
  }

  .courts-table th,
  .courts-table td {
    padding: 8px 6px;
  }

  .action-btn {
    padding: 6px 10px;
    font-size: 0.8rem;
  }

  .modal-header h2 {
    font-size: 1.1rem;
  }

  .modal-body {
    padding: 16px;
  }
}

/* Suggestion Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #1f2937;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  max-height: calc(80vh - 80px);
}

.modal-message {
  margin: 0 0 20px 0;
  color: #6b7280;
  font-size: 0.95rem;
  line-height: 1.5;
}

.suggested-courts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggested-court-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggested-court-item:hover {
  border-color: #10b981;
  background: #f0fdf4;
  transform: translateX(4px);
}

.court-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.court-info strong {
  color: #1f2937;
  font-size: 1rem;
}

.court-venue {
  color: #6b7280;
  font-size: 0.85rem;
}

.btn-select {
  background: #10b981;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-select:hover {
  background: #059669;
  transform: scale(1.05);
}
</style>
