<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axios'
import { useToast } from 'vue-toastification'
import type { AxiosError } from 'axios'

const toast = useToast()
const router = useRouter()

const form = reactive({
  name: '',
  description: '',
  detail_url: '',
  image: null as File | null,
})

const imagePreview = ref<string>('')
const isLoading = ref(false)
const error = ref<string>('')

const handleImageSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files) return

  const file = files[0]

  // Validate file size (5MB max)
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'File size must be less than 5MB'
    toast.error('File size must be less than 5MB')
    return
  }

  // Validate file type
  if (!file.type.startsWith('image/')) {
    error.value = 'Please select a valid image file'
    toast.error('Please select a valid image file')
    return
  }

  form.image = file
  error.value = ''

  // Generate preview
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const removeImage = () => {
  form.image = null
  imagePreview.value = ''
  const fileInput = document.getElementById('imageInput') as HTMLInputElement
  if (fileInput) {
    fileInput.value = ''
  }
}

const handleSubmit = async () => {
  // Validation
  if (!form.name.trim()) {
    error.value = 'Advertisement name is required'
    toast.error('Advertisement name is required')
    return
  }

  if (!form.description.trim()) {
    error.value = 'Description is required'
    toast.error('Description is required')
    return
  }

  if (!form.image) {
    error.value = 'Image is required'
    toast.error('Image is required')
    return
  }

  if (!form.detail_url.trim()) {
    error.value = 'Detail URL is required'
    toast.error('Detail URL is required')
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const formData = new FormData()
    formData.append('name', form.name)
    formData.append('description', form.description)
    formData.append('detail_url', form.detail_url)
    formData.append('image', form.image)

    await axios.post('/enterprise/advertisements', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    toast.success('Advertisement submitted. Waiting for admin approval.')

    // Reset form
    form.name = ''
    form.description = ''
    form.detail_url = ''
    form.image = null
    imagePreview.value = ''
    const fileInput = document.getElementById('imageInput') as HTMLInputElement
    if (fileInput) {
      fileInput.value = ''
    }

    // Redirect to list page
    setTimeout(() => {
      router.push('/enterprise/advertisements/list')
    }, 500)
  } catch (err) {
    const error_msg =
      (err as AxiosError<{ detail: string }>)?.response?.data?.detail ||
      (err as Error)?.message ||
      'Failed to upload advertisement'
    error.value = error_msg
    toast.error(error_msg)
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  form.name = ''
  form.description = ''
  form.detail_url = ''
  form.image = null
  imagePreview.value = ''
  error.value = ''
  const fileInput = document.getElementById('imageInput') as HTMLInputElement
  if (fileInput) {
    fileInput.value = ''
  }
}
</script>

<template>
  <div class="upload-page">
    <div class="page-header">
      <h2 class="page-title">Upload New Advertisement</h2>
      <p class="page-subtitle">
        Submit your advertisement for admin review. It will appear in Advertisement List after
        approval.
      </p>
    </div>

    <form @submit.prevent="handleSubmit" class="upload-form">
      <!-- Error Message -->
      <div v-if="error" class="error-message">
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
            d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        {{ error }}
      </div>

      <!-- Advertisement Name -->
      <div class="form-group">
        <label for="name">Advertisement Name *</label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          placeholder="Enter advertisement name"
          required
        />
      </div>

      <!-- Description -->
      <div class="form-group">
        <label for="description">Description *</label>
        <textarea
          id="description"
          v-model="form.description"
          placeholder="Enter advertisement description"
          rows="4"
          required
        ></textarea>
      </div>

      <!-- Detail URL -->
      <div class="form-group">
        <label for="detailUrl">Detail URL *</label>
        <input
          id="detailUrl"
          v-model="form.detail_url"
          type="url"
          placeholder="https://example.com"
          required
        />
      </div>

      <!-- Image Upload -->
      <div class="form-group">
        <label>Image *</label>
        <div class="image-upload-container">
          <div v-if="imagePreview" class="image-preview">
            <img :src="imagePreview" alt="Preview" />
            <button type="button" class="remove-btn" @click="removeImage">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path
                  d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"
                />
              </svg>
            </button>
          </div>
          <div v-else class="image-upload-area" @drop.prevent="handleImageSelect" @dragover.prevent>
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
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <p>Drag and drop your image here, or click to select</p>
            <span class="file-hint">Supported formats: JPG, PNG, GIF (Max 5MB)</span>
            <input id="imageInput" type="file" accept="image/*" @change="handleImageSelect" />
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="resetForm" :disabled="isLoading">
          Reset
        </button>
        <button type="submit" class="btn btn-primary" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          {{ isLoading ? 'Uploading...' : 'Upload Advertisement' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.upload-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1f2937;
  margin: 0;
}

.page-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
  margin: 0;
}

.error-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  margin-bottom: 24px;
  font-size: 14px;
}

.error-message svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.upload-form {
  background: white;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  width: 100%;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  font-size: 14px;
}

.form-group input[type='text'],
.form-group input[type='url'],
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s ease;
}

.form-group input[type='text']:focus,
.form-group input[type='url']:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

.form-group textarea {
  resize: vertical;
}

.image-upload-container {
  margin-top: 8px;
}

.image-upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  background: #f8fafc;
}

.image-upload-area:hover {
  border-color: #22c55e;
  background: #f0fdf4;
}

.image-upload-area svg {
  width: 48px;
  height: 48px;
  color: #94a3b8;
  margin-bottom: 12px;
}

.image-upload-area p {
  font-weight: 500;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.file-hint {
  display: block;
  font-size: 12px;
  color: #64748b;
}

.image-upload-area input[type='file'] {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.image-preview {
  position: relative;
  display: inline-block;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  display: block;
  width: auto;
  height: auto;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: #ef4444;
}

.remove-btn svg {
  width: 18px;
  height: 18px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 32px;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f1f5f9;
  color: #1e293b;
  border: 1px solid #cbd5e1;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .upload-form {
    padding: 20px;
  }

  .page-title {
    font-size: 1.35rem;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
