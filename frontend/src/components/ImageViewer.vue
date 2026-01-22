<template>
  <Teleport to="body">
    <div v-if="isOpen" class="image-viewer-overlay" @click="handleOverlayClick">
      <!-- Close button -->
      <button class="close-btn" @click="close" aria-label="Close">
        <X :size="24" />
      </button>

      <!-- Image counter -->
      <div class="image-counter">{{ currentIndex + 1 }} / {{ images.length }}</div>

      <!-- Navigation arrows (desktop) -->
      <button v-if="images.length > 1" class="nav-btn nav-prev" @click.stop="prevImage" aria-label="Previous image">
        <ChevronLeft :size="24" />
      </button>
      <button v-if="images.length > 1" class="nav-btn nav-next" @click.stop="nextImage" aria-label="Next image">
        <ChevronRight :size="24" />
      </button>

      <!-- Image container -->
      <div
        class="image-container"
        ref="containerRef"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
        @wheel="handleWheel"
      >
        <img
          :src="currentImageUrl"
          :style="imageStyle"
          class="viewer-image"
          @load="onImageLoad"
          draggable="false"
          ref="imageRef"
        />
      </div>

      <!-- Thumbnail strip -->
      <div v-if="images.length > 1" class="thumbnail-strip">
        <div
          v-for="(img, idx) in images"
          :key="img.id"
          class="thumbnail"
          :class="{ active: idx === currentIndex }"
          @click.stop="currentIndex = idx; resetZoom()"
        >
          <img :src="getThumbnailUrl(img.id)" alt="" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import api from '../services/api'
import { X, ChevronLeft, ChevronRight } from 'lucide-vue-next'

export default {
  name: 'ImageViewer',
  components: {
    X,
    ChevronLeft,
    ChevronRight
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    images: {
      type: Array,
      required: true
    },
    startIndex: {
      type: Number,
      default: 0
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const currentIndex = ref(props.startIndex)
    const containerRef = ref(null)
    const imageRef = ref(null)

    // Zoom and pan state
    const scale = ref(1)
    const translateX = ref(0)
    const translateY = ref(0)

    // Touch state
    const touchStartX = ref(0)
    const touchStartY = ref(0)
    const lastTouchDistance = ref(0)
    const isSwiping = ref(false)
    const swipeStartX = ref(0)
    const isPinching = ref(false)
    const lastPanX = ref(0)
    const lastPanY = ref(0)

    const isOpen = computed(() => props.modelValue)

    const currentImageUrl = computed(() => {
      if (props.images.length === 0) return ''
      return api.getImageUrl(props.images[currentIndex.value].id, false)
    })

    const imageStyle = computed(() => ({
      transform: `translate(${translateX.value}px, ${translateY.value}px) scale(${scale.value})`,
      transition: isSwiping.value || isPinching.value ? 'none' : 'transform 0.2s ease-out'
    }))

    const getThumbnailUrl = (imageId) => {
      return api.getImageUrl(imageId, true)
    }

    const resetZoom = () => {
      scale.value = 1
      translateX.value = 0
      translateY.value = 0
    }

    const close = () => {
      emit('update:modelValue', false)
      resetZoom()
    }

    const handleOverlayClick = (e) => {
      // Close only if clicking the overlay itself (not image or controls)
      if (e.target.classList.contains('image-viewer-overlay') ||
          e.target.classList.contains('image-container')) {
        close()
      }
    }

    const prevImage = () => {
      if (currentIndex.value > 0) {
        currentIndex.value--
        resetZoom()
      } else {
        currentIndex.value = props.images.length - 1
        resetZoom()
      }
    }

    const nextImage = () => {
      if (currentIndex.value < props.images.length - 1) {
        currentIndex.value++
        resetZoom()
      } else {
        currentIndex.value = 0
        resetZoom()
      }
    }

    const onImageLoad = () => {
      resetZoom()
    }

    // Touch handlers for swipe and pinch-to-zoom
    const handleTouchStart = (e) => {
      if (e.touches.length === 2) {
        // Pinch start
        isPinching.value = true
        lastTouchDistance.value = getTouchDistance(e.touches)
        const center = getTouchCenter(e.touches)
        lastPanX.value = center.x
        lastPanY.value = center.y
      } else if (e.touches.length === 1) {
        // Swipe or pan start
        touchStartX.value = e.touches[0].clientX
        touchStartY.value = e.touches[0].clientY
        swipeStartX.value = e.touches[0].clientX
        isSwiping.value = true
        lastPanX.value = e.touches[0].clientX
        lastPanY.value = e.touches[0].clientY
      }
    }

    const handleTouchMove = (e) => {
      e.preventDefault()

      if (e.touches.length === 2 && isPinching.value) {
        // Pinch zoom
        const newDistance = getTouchDistance(e.touches)
        const scaleChange = newDistance / lastTouchDistance.value
        const newScale = Math.min(Math.max(scale.value * scaleChange, 1), 5)
        scale.value = newScale
        lastTouchDistance.value = newDistance

        // Pan while pinching
        const center = getTouchCenter(e.touches)
        if (scale.value > 1) {
          translateX.value += center.x - lastPanX.value
          translateY.value += center.y - lastPanY.value
        }
        lastPanX.value = center.x
        lastPanY.value = center.y
      } else if (e.touches.length === 1 && isSwiping.value) {
        const currentX = e.touches[0].clientX
        const currentY = e.touches[0].clientY

        if (scale.value > 1) {
          // Pan when zoomed
          translateX.value += currentX - lastPanX.value
          translateY.value += currentY - lastPanY.value
          lastPanX.value = currentX
          lastPanY.value = currentY
        }
      }
    }

    const handleTouchEnd = (e) => {
      if (isPinching.value) {
        isPinching.value = false
        if (scale.value <= 1) {
          resetZoom()
        }
        return
      }

      if (isSwiping.value && scale.value === 1 && props.images.length > 1) {
        const swipeDistance = e.changedTouches[0].clientX - swipeStartX.value
        const swipeThreshold = 50

        if (swipeDistance > swipeThreshold) {
          prevImage()
        } else if (swipeDistance < -swipeThreshold) {
          nextImage()
        }
      }

      isSwiping.value = false

      // Constrain pan bounds when zoomed
      if (scale.value > 1) {
        constrainPan()
      }
    }

    const handleWheel = (e) => {
      e.preventDefault()
      const delta = e.deltaY > 0 ? 0.9 : 1.1
      const newScale = Math.min(Math.max(scale.value * delta, 1), 5)
      scale.value = newScale

      if (newScale <= 1) {
        resetZoom()
      }
    }

    const getTouchDistance = (touches) => {
      const dx = touches[0].clientX - touches[1].clientX
      const dy = touches[0].clientY - touches[1].clientY
      return Math.sqrt(dx * dx + dy * dy)
    }

    const getTouchCenter = (touches) => {
      return {
        x: (touches[0].clientX + touches[1].clientX) / 2,
        y: (touches[0].clientY + touches[1].clientY) / 2
      }
    }

    const constrainPan = () => {
      // Basic pan constraints when zoomed
      const maxPan = 200 * (scale.value - 1)
      translateX.value = Math.min(Math.max(translateX.value, -maxPan), maxPan)
      translateY.value = Math.min(Math.max(translateY.value, -maxPan), maxPan)
    }

    // Keyboard navigation
    const handleKeydown = (e) => {
      if (!props.modelValue) return

      switch (e.key) {
        case 'Escape':
          close()
          break
        case 'ArrowLeft':
          prevImage()
          break
        case 'ArrowRight':
          nextImage()
          break
      }
    }

    watch(() => props.startIndex, (newIndex) => {
      currentIndex.value = newIndex
      resetZoom()
    })

    watch(() => props.modelValue, (isOpen) => {
      if (isOpen) {
        document.body.style.overflow = 'hidden'
        currentIndex.value = props.startIndex
      } else {
        document.body.style.overflow = ''
      }
    })

    onMounted(() => {
      window.addEventListener('keydown', handleKeydown)
    })

    onUnmounted(() => {
      window.removeEventListener('keydown', handleKeydown)
      document.body.style.overflow = ''
    })

    return {
      isOpen,
      currentIndex,
      currentImageUrl,
      imageStyle,
      containerRef,
      imageRef,
      close,
      handleOverlayClick,
      prevImage,
      nextImage,
      onImageLoad,
      handleTouchStart,
      handleTouchMove,
      handleTouchEnd,
      handleWheel,
      getThumbnailUrl,
      resetZoom
    }
  }
}
</script>

<style scoped>
.image-viewer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.image-counter {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  font-size: 14px;
  background: rgba(0, 0, 0, 0.5);
  padding: 6px 16px;
  border-radius: 20px;
  z-index: 10;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: background 0.2s;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-prev {
  left: 16px;
}

.nav-next {
  right: 16px;
}

@media (max-width: 768px) {
  .nav-btn {
    display: none;
  }
}

.image-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 16px 100px;
  box-sizing: border-box;
  touch-action: none;
}

.viewer-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  user-select: none;
  -webkit-user-drag: none;
}

.thumbnail-strip {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 8px;
  max-width: calc(100% - 32px);
  overflow-x: auto;
}

.thumbnail {
  width: 50px;
  height: 50px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.2s;
  border: 2px solid transparent;
}

.thumbnail.active {
  opacity: 1;
  border-color: white;
}

.thumbnail:hover {
  opacity: 0.8;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
