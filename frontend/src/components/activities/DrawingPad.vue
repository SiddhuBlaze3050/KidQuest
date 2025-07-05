<template>
    <div class="drawing-pad-overlay" @click.self="$emit('close')">
        <div class="drawing-pad-container">
            <div class="header">
                <div class="title-section">
                    <h2 class="title">🎨 Creative Canvas</h2>
                    <div v-if="referenceImage" class="reference-title">
                        <span>📝 Trying to draw: {{ referenceImage.title }}</span>
                        <button @click="changeReference" class="change-ref-btn" title="Change Reference">🔄</button>
                    </div>
                </div>
                <div class="header-actions">
                    <div class="timer-display">
                        <span class="timer">⏱️ {{ formatTime(elapsedTime) }}</span>
                        <span v-if="isTimerStopped" class="timer-status">⏸️</span>
                    </div>
                    <button @click="saveToGallery" class="save-btn gallery" :disabled="isSaving">
                        {{ isSaving ? 'Saving...' : '💾 Save' }}
                    </button>
                    <button @click="downloadImage" class="save-btn download" :disabled="isDownloading">
                        {{ isDownloading ? 'Downloading...' : '📥 Download' }}
                    </button>
                    <button @click="$emit('close')" class="close-btn">×</button>
                </div>
            </div>

            <!-- Success/Error Message -->
            <div v-if="message" class="message" :class="messageType">
                {{ message }}
                <button @click="message = ''" class="message-close">×</button>
            </div>

            <!-- Naming Modal -->
            <div v-if="showNamingModal" class="naming-modal-overlay" @click.self="showNamingModal = false">
                <div class="naming-modal">
                    <div class="naming-header">
                        <h3>🎨 Name Your Artwork</h3>
                    </div>
                    <div class="naming-content">
                        <p>Give your drawing a special name!</p>
                        <input 
                            v-model="drawingName" 
                            type="text" 
                            placeholder="My Amazing Drawing..." 
                            class="drawing-name-input"
                            maxlength="100"
                            @keyup.enter="confirmSave"
                            ref="drawingNameInput"
                        >
                        <div class="name-suggestions">
                            <p>💡 Ideas:</p>
                            <div class="suggestion-buttons">
                                <button @click="drawingName = suggestion" 
                                        v-for="suggestion in nameSuggestions" 
                                        :key="suggestion" 
                                        class="suggestion-btn">
                                    {{ suggestion }}
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="naming-actions">
                        <button @click="showNamingModal = false" class="cancel-btn">❌ Cancel</button>
                        <button @click="confirmSave" class="confirm-btn" :disabled="!drawingName.trim()">
                            💾 Save Drawing
                        </button>
                    </div>
                </div>
            </div>

            <!-- Gallery View -->
            <div v-if="showGallery" class="gallery-overlay" @click.self="showGallery = false">
                <div class="gallery-container">
                    <div class="gallery-header">
                        <h3>🖼️ My Art Gallery</h3>
                        <button @click="showGallery = false" class="close-btn">×</button>
                    </div>
                    <div class="gallery-content">
                        <!-- Local Storage Drawings -->
                        <div v-if="savedDrawings.length > 0" class="gallery-section">
                            <h4>📱 Local Gallery</h4>
                            <div class="gallery-grid">
                                <div v-for="(drawing, index) in savedDrawings" :key="`local-${index}`" class="gallery-item">
                                    <img :src="drawing.dataURL" :alt="drawing.name" @click="loadDrawing(drawing)">
                                    <div class="item-info">
                                        <p>{{ drawing.name }}</p>
                                        <small>{{ drawing.date }}</small>
                                        <div v-if="drawing.timeTaken" class="drawing-stats">
                                            <small>⏱️ {{ formatTime(drawing.timeTaken) }}</small>
                                        </div>
                                        <div v-if="drawing.referenceTitle" class="reference-info">
                                            <small>📝 {{ drawing.referenceTitle }}</small>
                                        </div>
                                        <button @click="deleteDrawing(index)" class="delete-btn">🗑️</button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Database Drawings -->
                        <div v-if="databaseDrawings.length > 0" class="gallery-section">
                            <h4>💾 Saved Drawings</h4>
                            <div class="gallery-grid">
                                <div v-for="drawing in databaseDrawings" :key="`db-${drawing.id}`" class="gallery-item">
                                    <div class="db-drawing-preview" @click="loadDatabaseDrawing(drawing)">
                                        <div class="preview-placeholder">🎨</div>
                                        <span class="file-status" :class="{ 'file-exists': drawing.file_exists }">
                                            {{ drawing.file_exists ? '✅' : '❌' }}
                                        </span>
                                    </div>
                                    <div class="item-info">
                                        <p>{{ drawing.description }}</p>
                                        <div v-if="drawing.ref_image_title" class="reference-info">
                                            <small>📝 {{ drawing.ref_image_title }}</small>
                                        </div>
                                        <div class="drawing-stats">
                                            <small>⏱️ {{ formatTime(drawing.time_taken) }}</small>
                                            <small>📅 {{ new Date(drawing.timestamp).toLocaleDateString() }}</small>
                                        </div>
                                        <button @click="deleteDatabaseDrawing(drawing)" class="delete-btn">🗑️</button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Empty state -->
                        <div v-if="savedDrawings.length === 0 && databaseDrawings.length === 0" class="empty-gallery">
                            <p>🎨 No drawings saved yet!</p>
                            <p>Create something amazing and save it to your gallery!</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="toolbar">
                <div class="tool-group">
                    <label>Color:</label>
                    <input type="color" v-model="brushColor" class="color-picker" title="Select Color">
                </div>
                <div class="tool-group">
                    <label>Size:</label>
                    <input type="range" min="2" max="50" v-model="brushSize" class="size-slider"
                        title="Adjust Brush Size">
                    <span>{{ brushSize }}</span>
                </div>
                <div class="tool-group">
                    <button @click="setTool('brush')" class="tool-btn" :class="{ active: drawingTool === 'brush' }"
                        title="Brush">🖌️</button>
                    <button @click="setTool('rectangle')" class="tool-btn"
                        :class="{ active: drawingTool === 'rectangle' }" title="Rectangle">▭</button>
                    <button @click="setTool('circle')" class="tool-btn" :class="{ active: drawingTool === 'circle' }"
                        title="Circle">⚪</button>
                    <button @click="setTool('triangle')" class="tool-btn"
                        :class="{ active: drawingTool === 'triangle' }" title="Triangle">△</button>
                </div>
                <div class="tool-group">
                    <button @click="toggleRainbowMode" class="tool-btn" :class="{ active: isRainbowMode }"
                        title="Rainbow Mode">🌈</button>
                    <button @click="activateEraser" class="tool-btn" :class="{ active: isErasing }"
                        title="Eraser">🧼</button>
                    <button @click="clearCanvas" class="tool-btn" title="Clear All">🗑️</button>
                    <button @click="showGallery = true" class="tool-btn" title="View Gallery">📁</button>
                </div>
            </div>

            <!-- Main Drawing Area with Reference Image -->
            <div class="drawing-area">
                <!-- Canvas Container -->
                <div class="canvas-container">
                    <canvas ref="canvasRef" @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing"
                        @mouseleave="stopDrawing" :class="getCanvasCursorClass()"></canvas>
                </div>
                
                <!-- Reference Image Panel -->
                <div v-if="referenceImage && showReference" class="reference-panel">
                    <div class="reference-header">
                        <h4>🎯 Reference Image</h4>
                        <div class="reference-controls">
                            <button @click="showReference = false" class="hide-ref-btn" title="Hide Reference">👁️</button>
                            <button @click="changeReference" class="change-ref-btn" title="Change Reference">🔄</button>
                        </div>
                    </div>
                    <div class="reference-image-container">
                        <img :src="`${API_BASE}${referenceImage.url}`" :alt="referenceImage.title" class="reference-image" />
                        <p class="reference-caption">{{ referenceImage.title }}</p>
                    </div>
                </div>
                
                <!-- Show Reference Button when hidden -->
                <div v-if="referenceImage && !showReference" class="show-reference-panel">
                    <button @click="showReference = true" class="show-ref-btn">
                        <span>👁️</span>
                        <span>Show Reference</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
    userId: {
        type: Number,
        default: 1 // Default user ID
    }
});

const emit = defineEmits(['close']);
const canvasRef = ref(null);
let ctx = null;

const isDrawing = ref(false);
const brushColor = ref('#000000');
const brushSize = ref(10);
const isErasing = ref(false);
const isRainbowMode = ref(false);
const drawingTool = ref('brush');
const startPos = ref({ x: 0, y: 0 });
let canvasSnapshot = null;
let hue = 0;

// Save functionality
const isSaving = ref(false);
const isDownloading = ref(false);
const message = ref('');
const messageType = ref('success'); // 'success' or 'error'

// Gallery functionality
const showGallery = ref(false);
const savedDrawings = ref([]);
const databaseDrawings = ref([]);

// Naming functionality
const showNamingModal = ref(false);
const drawingName = ref('');
const drawingNameInput = ref(null);

// Add name suggestions array
const nameSuggestions = [
    '🌟 My Masterpiece',
    '🌈 Rainbow Art',
    '🏠 My House',
    '🐱 Cute Cat',
    '🌺 Beautiful Flower',
    '🚗 Cool Car',
    '🎈 Happy Day',
    '🦋 Butterfly Dream'
];

// Timer and Reference Image functionality
const startTime = ref(null);
const elapsedTime = ref(0);
const timerInterval = ref(null);
const referenceImage = ref(null);
const showReference = ref(true);
const sessionId = ref(null);
const isTimerStopped = ref(false); // Track if timer is stopped

// API Configuration
const API_BASE = 'http://localhost:5000';

// Function to get appropriate cursor class for canvas
const getCanvasCursorClass = () => {
    if (isErasing.value) {
        return 'eraser-cursor';
    } else if (drawingTool.value === 'brush') {
        return 'brush-cursor';
    } else if (drawingTool.value === 'rectangle') {
        return 'crosshair-cursor';
    } else if (drawingTool.value === 'circle') {
        return 'crosshair-cursor';
    } else if (drawingTool.value === 'triangle') {
        return 'crosshair-cursor';
    }
    return 'default-cursor';
};

// Timer functions
const startTimer = () => {
    startTime.value = Date.now();
    elapsedTime.value = 0;
    isTimerStopped.value = false;
    
    timerInterval.value = setInterval(() => {
        if (startTime.value && !isTimerStopped.value) {
            elapsedTime.value = Math.floor((Date.now() - startTime.value) / 1000);
        }
    }, 1000);
};

const stopTimer = () => {
    if (timerInterval.value) {
        clearInterval(timerInterval.value);
        timerInterval.value = null;
    }
    isTimerStopped.value = true;
};

const pauseTimer = () => {
    isTimerStopped.value = true;
};

const resumeTimer = () => {
    if (!isTimerStopped.value) return;
    
    // Adjust start time to account for paused duration
    const pausedTime = elapsedTime.value * 1000;
    startTime.value = Date.now() - pausedTime;
    isTimerStopped.value = false;
};

const formatTime = (seconds) => {
    if (!seconds || seconds < 0) return "0:00";
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

// Reference image functions
const loadRandomReference = async () => {
    try {
        const response = await fetch(`${API_BASE}/api/drawings/random-reference`);
        
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                referenceImage.value = result.reference;
                showReference.value = true;
            }
        }
    } catch (error) {
        // Silent error - reference images are optional
    }
};

const changeReference = async () => {
    await loadRandomReference();
};

// Define resizeCanvas in the setup scope to be accessible for cleanup
const resizeCanvas = () => {
    const canvas = canvasRef.value;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
};

onMounted(() => {
    const canvas = canvasRef.value;
    if (canvas) {
        ctx = canvas.getContext('2d');
        window.addEventListener('resize', resizeCanvas);
        requestAnimationFrame(resizeCanvas);
    }
    
    // Load saved drawings from localStorage
    loadGalleryFromStorage();
    // Load drawings from database
    loadDatabaseDrawings();
    // Load random reference image
    loadRandomReference();
    // Start timer
    startTimer();
});

onUnmounted(() => {
    window.removeEventListener('resize', resizeCanvas);
    stopTimer();
});

const getMousePos = (e) => {
    const rect = canvasRef.value.getBoundingClientRect();
    return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
    };
};

const startDrawing = (e) => {
    isDrawing.value = true;
    const pos = getMousePos(e);
    startPos.value = pos;
    ctx.beginPath();

    // Only move to the starting position for the brush tool
    if (drawingTool.value === 'brush' || isErasing.value) {
        ctx.moveTo(pos.x, pos.y);
    }

    // Save the canvas state before drawing a shape
    if (drawingTool.value !== 'brush' && !isErasing.value) {
        canvasSnapshot = ctx.getImageData(0, 0, canvasRef.value.width, canvasRef.value.height);
    }
};

const draw = (e) => {
    if (!isDrawing.value) return;

    ctx.lineWidth = brushSize.value;
    ctx.globalCompositeOperation = isErasing.value ? 'destination-out' : 'source-over';

    if (isErasing.value) {
        ctx.strokeStyle = 'rgba(0,0,0,1)';
    } else if (isRainbowMode.value) {
        ctx.strokeStyle = `hsl(${hue++}, 100%, 50%)`;
    } else {
        ctx.strokeStyle = brushColor.value;
    }

    const currentPos = getMousePos(e);

    if (drawingTool.value === 'brush' || isErasing.value) {
        ctx.lineTo(currentPos.x, currentPos.y);
        ctx.stroke();
    } else if (drawingTool.value !== 'brush') {
        if (canvasSnapshot) {
            ctx.putImageData(canvasSnapshot, 0, 0);
        }

        ctx.beginPath(); // Start a new path for the shape
        if (drawingTool.value === 'rectangle') {
            ctx.strokeRect(startPos.value.x, startPos.value.y, currentPos.x - startPos.value.x, currentPos.y - startPos.value.y);
        } else if (drawingTool.value === 'circle') {
            const radius = Math.sqrt(Math.pow(currentPos.x - startPos.value.x, 2) + Math.pow(currentPos.y - startPos.value.y, 2));
            ctx.arc(startPos.value.x, startPos.value.y, radius, 0, 2 * Math.PI);
        } else if (drawingTool.value === 'triangle') {
            ctx.moveTo(startPos.value.x, startPos.value.y);
            ctx.lineTo(currentPos.x, currentPos.y);
            ctx.lineTo(startPos.value.x * 2 - currentPos.x, currentPos.y);
            ctx.closePath();
        }
        ctx.stroke();
    }
};

const stopDrawing = (e) => {
    if (!isDrawing.value) return;
    // For shapes, draw the final shape on the actual canvas
    if (drawingTool.value !== 'brush' && !isErasing.value) {
        draw(e);
    }
    isDrawing.value = false;
    canvasSnapshot = null;
    ctx.closePath();
};

const setTool = (tool) => {
    drawingTool.value = tool;
    isErasing.value = false;
    isRainbowMode.value = tool === 'brush' ? isRainbowMode.value : false;
};

const clearCanvas = () => {
    if (confirm('Are you sure you want to clear the canvas?')) {
        ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
    }
};

const activateEraser = () => {
    isErasing.value = !isErasing.value;
    drawingTool.value = 'brush'; // Eraser is a form of brush
    isRainbowMode.value = false;
};

const toggleRainbowMode = () => {
    isRainbowMode.value = !isRainbowMode.value;
    drawingTool.value = 'brush';
    isErasing.value = false;
};

// Save to gallery function - opens naming modal first
const saveToGallery = async () => {
    // Show naming modal first
    showNamingModal.value = true;
    drawingName.value = ''; // Reset name
    
    // Focus on input after modal opens
    setTimeout(() => {
        if (drawingNameInput.value) {
            drawingNameInput.value.focus();
        }
    }, 100);
};

// Add this new function to handle the actual saving
const confirmSave = async () => {
    if (!drawingName.value.trim()) {
        return; // Don't save if no name
    }
    
    showNamingModal.value = false;
    isSaving.value = true;
    
    // Stop the timer when saving
    const finalDrawingTime = elapsedTime.value;
    stopTimer();
    
    try {
        const canvas = canvasRef.value;
        
        // Create a temporary canvas with white background
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        
        // Set same dimensions as original canvas
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        
        // Fill with white background
        tempCtx.fillStyle = '#FFFFFF';
        tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
        
        // Draw the original canvas content on top of white background
        tempCtx.drawImage(canvas, 0, 0);
        
        // Get dataURL from temporary canvas (with white background)
        const dataURL = tempCanvas.toDataURL('image/png');
        
        // Save to localStorage with user-provided name
        const localDrawing = {
            name: drawingName.value.trim(),
            dataURL: dataURL,
            date: new Date().toLocaleDateString(),
            timestamp: Date.now(),
            timeTaken: finalDrawingTime,
            referenceTitle: referenceImage.value?.title
        };
        
        savedDrawings.value.push(localDrawing);
        saveGalleryToStorage();
        
        // Save to database with user-provided name
        try {
            const requestData = {
                user_id: props.userId,
                image_data: dataURL,
                description: drawingName.value.trim(), // Use user-provided name
                time_taken: finalDrawingTime,
                ref_image_path: referenceImage.value?.path,
                ref_image_title: referenceImage.value?.title
            };
            
            const response = await fetch(`${API_BASE}/api/drawings/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Server returned HTML instead of JSON - Flask app may not be running');
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                await loadDatabaseDrawings();
                message.value = `🎉 "${drawingName.value}" saved! Time: ${formatTime(finalDrawingTime)}`;
                messageType.value = 'success';
            } else {
                message.value = `🎉 "${drawingName.value}" saved locally! Time: ${formatTime(finalDrawingTime)} (Database: ${result.error})`;
                messageType.value = 'success';
            }
        } catch (dbError) {
            if (dbError.message.includes('Flask')) {
                message.value = `🎉 "${drawingName.value}" saved locally! Time: ${formatTime(finalDrawingTime)} (Start Flask with: python app.py)`;
            } else {
                message.value = `🎉 "${drawingName.value}" saved locally! Time: ${formatTime(finalDrawingTime)} (Database unavailable)`;
            }
            messageType.value = 'success';
        }
        
        // Clear the drawing name for next time
        drawingName.value = '';
        
        setTimeout(() => {
            message.value = '';
        }, 3000);
        
    } catch (error) {
        message.value = '❌ Failed to save drawing';
        messageType.value = 'error';
        
        setTimeout(() => {
            message.value = '';
        }, 3000);
    } finally {
        isSaving.value = false;
    }
};

// Load drawings from database
const loadDatabaseDrawings = async () => {
    try {
        const response = await fetch(`${API_BASE}/api/drawings/${props.userId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            return;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            databaseDrawings.value = result.drawings;
        }
    } catch (error) {
        // Silent error handling for database connection issues
    }
};

// Load drawing from database
const loadDatabaseDrawing = async (drawing) => {
    if (!confirm('Load this drawing from database? Current drawing will be replaced and timer will restart.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/drawings/image/${drawing.id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Server returned HTML instead of JSON');
        }
        
        const result = await response.json();
        
        if (result.success) {
            const img = new Image();
            img.onload = () => {
                ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
                ctx.drawImage(img, 0, 0);
                showGallery.value = false;
                
                // Restart timer when loading a drawing
                startTimer();
                
                message.value = '🎨 Drawing loaded from database! Timer restarted.';
                messageType.value = 'success';
                setTimeout(() => {
                    message.value = '';
                }, 2000);
            };
            img.src = result.image_data;
        } else {
            message.value = `❌ Failed to load drawing: ${result.error}`;
            messageType.value = 'error';
            setTimeout(() => {
                message.value = '';
            }, 3000);
        }
    } catch (error) {
        message.value = '❌ Error loading drawing from database';
        messageType.value = 'error';
        setTimeout(() => {
            message.value = '';
        }, 3000);
    }
};

// Delete drawing from database
const deleteDatabaseDrawing = async (drawing) => {
    if (!confirm('Are you sure you want to delete this drawing from the database? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/drawings/delete/${drawing.id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Server returned HTML instead of JSON');
        }
        
        const result = await response.json();
        
        if (result.success) {
            databaseDrawings.value = databaseDrawings.value.filter(d => d.id !== drawing.id);
            
            message.value = '🗑️ Drawing deleted from database';
            messageType.value = 'success';
            setTimeout(() => {
                message.value = '';
            }, 2000);
        } else {
            message.value = `❌ Failed to delete: ${result.error}`;
            messageType.value = 'error';
            setTimeout(() => {
                message.value = '';
            }, 3000);
        }
    } catch (error) {
        message.value = '❌ Error deleting drawing';
        messageType.value = 'error';
        setTimeout(() => {
            message.value = '';
        }, 3000);
    }
};

// Download image function - downloads directly to user's computer
const downloadImage = () => {
    isDownloading.value = true;
    
    try {
        const canvas = canvasRef.value;
        
        // Create a temporary canvas with white background
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        
        // Set same dimensions as original canvas
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        
        // Fill with white background
        tempCtx.fillStyle = '#FFFFFF';
        tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
        
        // Draw the original canvas content on top of white background
        tempCtx.drawImage(canvas, 0, 0);
        
        // Get dataURL from temporary canvas (with white background)
        const dataURL = tempCanvas.toDataURL('image/png');
        
        // Create download link with reference info if available
        const link = document.createElement('a');
        const refTitle = referenceImage.value ? `_${referenceImage.value.title.replace(/\s+/g, '_')}` : '';
        link.download = `drawing${refTitle}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
        link.href = dataURL;
        
        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Show success message
        message.value = '📥 Image downloaded to your computer!';
        messageType.value = 'success';
        
        setTimeout(() => {
            message.value = '';
        }, 3000);
        
    } catch (error) {
        message.value = '❌ Failed to download image';
        messageType.value = 'error';
        
        setTimeout(() => {
            message.value = '';
        }, 3000);
    } finally {
        isDownloading.value = false;
    }
};

// Gallery management functions
const saveGalleryToStorage = () => {
    try {
        localStorage.setItem('drawingGallery', JSON.stringify(savedDrawings.value));
    } catch (error) {
        // Silent error handling
    }
};

const loadGalleryFromStorage = () => {
    try {
        const stored = localStorage.getItem('drawingGallery');
        if (stored) {
            savedDrawings.value = JSON.parse(stored);
        }
    } catch (error) {
        savedDrawings.value = [];
    }
};

const loadDrawing = (drawing) => {
    if (confirm('Load this drawing? Current drawing will be replaced and timer will restart.')) {
        const img = new Image();
        img.onload = () => {
            ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
            ctx.drawImage(img, 0, 0);
            showGallery.value = false;
            
            // Restart timer when loading a drawing
            startTimer();
            
            message.value = '🎨 Drawing loaded! Timer restarted.';
            messageType.value = 'success';
            setTimeout(() => {
                message.value = '';
            }, 2000);
        };
        img.src = drawing.dataURL;
    }
};

const deleteDrawing = (index) => {
    if (confirm('Are you sure you want to delete this drawing?')) {
        savedDrawings.value.splice(index, 1);
        saveGalleryToStorage();
        
        message.value = '🗑️ Drawing deleted from gallery';
        messageType.value = 'success';
        setTimeout(() => {
            message.value = '';
        }, 2000);
    }
};
</script>

<style scoped>
.drawing-pad-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(5px);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.drawing-pad-container {
    background: rgba(46, 38, 70, 0.95);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    border-radius: 20px;
    padding: 1.5rem;
    width: 95%;
    max-width: 1400px;
    height: 90vh;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.title-section {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.title {
    margin: 0;
    font-size: 1.8rem;
}

.reference-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.25rem;
    font-size: 0.9rem;
    color: #FFD700;
}

.change-ref-btn {
    background: none;
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    border-radius: 4px;
    padding: 0.2rem 0.4rem;
    cursor: pointer;
    font-size: 0.8rem;
}

.change-ref-btn:hover {
    background: rgba(255, 255, 255, 0.1);
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.timer-display {
    background: rgba(0, 0, 0, 0.3);
    padding: 0.5rem 1rem;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.timer {
    font-weight: bold;
    color: #FFD700;
    font-size: 1rem;
}

.timer-status {
    color: #ff6b6b;
    font-size: 0.9rem;
}

.save-btn {
    border: none;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s;
    min-width: 100px;
}

.save-btn.gallery {
    background: #667eea;
}

.save-btn.gallery:hover:not(:disabled) {
    background: #5a67d8;
}

.save-btn.download {
    background: #4CAF50;
}

.save-btn.download:hover:not(:disabled) {
    background: #45a049;
}

.save-btn:disabled {
    background: #666;
    cursor: not-allowed;
}

.close-btn {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    font-size: 1.8rem;
    cursor: pointer;
    transition: color 0.3s;
}

.close-btn:hover {
    color: white;
}

.message {
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    animation: slideDown 0.3s ease-out;
}

.message.success {
    background: #4CAF50;
    color: white;
}

.message.error {
    background: #f44336;
    color: white;
}

.message-close {
    background: none;
    border: none;
    color: inherit;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
    margin-left: 1rem;
}

/* Naming Modal Styles */
.naming-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1002;
}

.naming-modal {
    background: rgba(46, 38, 70, 0.98);
    border: 2px solid #FFD700;
    border-radius: 20px;
    padding: 2rem;
    width: 90%;
    max-width: 500px;
    color: white;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
    from {
        transform: translateY(-50px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.naming-header {
    text-align: center;
    margin-bottom: 1.5rem;
}

.naming-header h3 {
    margin: 0;
    color: #FFD700;
    font-size: 1.5rem;
}

.naming-content {
    margin-bottom: 2rem;
}

.naming-content p {
    text-align: center;
    margin-bottom: 1rem;
    color: rgba(255, 255, 255, 0.9);
}

.drawing-name-input {
    width: 100%;
    padding: 1rem;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.1);
    color: white;
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 1.5rem;
    transition: all 0.3s;
    box-sizing: border-box;
}

.drawing-name-input:focus {
    outline: none;
    border-color: #FFD700;
    background: rgba(255, 255, 255, 0.15);
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}

.drawing-name-input::placeholder {
    color: rgba(255, 255, 255, 0.6);
}

.name-suggestions {
    text-align: center;
}

.name-suggestions p {
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.8);
}

.suggestion-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
}

.suggestion-btn {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.3s;
}

.suggestion-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: #FFD700;
    transform: scale(1.05);
}

.naming-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

.cancel-btn, .confirm-btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: bold;
    transition: all 0.3s;
    min-width: 120px;
}

.cancel-btn {
    background: #f44336;
    color: white;
}

.cancel-btn:hover {
    background: #d32f2f;
    transform: scale(1.05);
}

.confirm-btn {
    background: #4CAF50;
    color: white;
}

.confirm-btn:hover:not(:disabled) {
    background: #45a049;
    transform: scale(1.05);
}

.confirm-btn:disabled {
    background: #666;
    cursor: not-allowed;
    transform: none;
}

/* Gallery Styles */
.gallery-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1001;
}

.gallery-container {
    background: rgba(46, 38, 70, 0.98);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 15px;
    padding: 2rem;
    width: 90%;
    max-width: 900px;
    height: 80vh;
    color: white;
    display: flex;
    flex-direction: column;
}

.gallery-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.gallery-header h3 {
    margin: 0;
}

.gallery-content {
    overflow-y: auto;
    flex-grow: 1;
}

.gallery-section {
    margin-bottom: 2rem;
}

.gallery-section h4 {
    margin: 0 0 1rem 0;
    color: #667eea;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    padding-bottom: 0.5rem;
    font-size: 1.1rem;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
}

.gallery-item {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    overflow: hidden;
    transition: transform 0.3s;
}

.gallery-item:hover {
    transform: scale(1.05);
}

.gallery-item img {
    width: 100%;
    height: 100px;
    object-fit: cover;
    cursor: pointer;
}

.db-drawing-preview {
    position: relative;
    height: 100px;
    background: rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 8px 8px 0 0;
}

.preview-placeholder {
    font-size: 2rem;
    color: rgba(255, 255, 255, 0.6);
}

.file-status {
    position: absolute;
    top: 5px;
    right: 5px;
    font-size: 0.8rem;
}

.file-status.file-exists {
    color: #4CAF50;
}

.item-info {
    padding: 0.5rem;
    text-align: center;
}

.item-info p {
    margin: 0.25rem 0;
    font-size: 0.9rem;
    word-break: break-word;
}

.reference-info {
    margin: 0.25rem 0;
}

.reference-info small {
    color: #FFD700;
    font-size: 0.7rem;
}

.drawing-stats {
    display: flex;
    justify-content: space-between;
    margin: 0.25rem 0;
}

.drawing-stats small {
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.65rem;
}

.item-info small {
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.75rem;
}

.delete-btn {
    background: #f44336;
    border: none;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
    margin-top: 0.5rem;
}

.delete-btn:hover {
    background: #d32f2f;
}

.empty-gallery {
    text-align: center;
    padding: 2rem;
    color: rgba(255, 255, 255, 0.7);
}

@keyframes slideDown {
    from {
        transform: translateY(-20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.toolbar {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    background: rgba(0, 0, 0, 0.2);
    padding: 0.75rem;
    border-radius: 15px;
    margin-bottom: 1rem;
}

.tool-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0 0.5rem;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.tool-group:last-child {
    border-right: none;
}

.tool-group label {
    font-weight: bold;
}

.color-picker {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    width: 35px;
    height: 35px;
    background-color: transparent;
    border: none;
    cursor: pointer;
}

.color-picker::-webkit-color-swatch {
    border-radius: 50%;
    border: 2px solid white;
}

.color-picker::-moz-color-swatch {
    border-radius: 50%;
    border: 2px solid white;
}

.size-slider {
    width: 100px;
}

.tool-btn {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    font-size: 1.3rem;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    justify-content: center;
    align-items: center;
}

.tool-btn:hover {
    background: rgba(255, 255, 255, 0.2);
}

.tool-btn.active {
    background: #667eea;
    box-shadow: 0 0 10px #667eea;
}

/* Main Drawing Area Layout */
.drawing-area {
    display: flex;
    gap: 1rem;
    flex-grow: 1;
    min-height: 0;
}

.canvas-container {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

/* Improved Canvas Cursor Styles */
canvas {
    flex-grow: 1;
    width: 100%;
    border-radius: 15px;
    background-color: #ffffff;
    min-height: 0;
    touch-action: none;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}

.default-cursor {
    cursor: default;
}

.crosshair-cursor {
    cursor: crosshair;
}

.brush-cursor {
    cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="1" fill="black"/><circle cx="12" cy="12" r="8" fill="none" stroke="black" stroke-width="1" opacity="0.5"/></svg>') 12 12, auto;
}

.eraser-cursor {
    cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><rect x="6" y="9" width="12" height="6" fill="none" stroke="red" stroke-width="2" rx="1"/><line x1="8" y1="11" x2="16" y2="13" stroke="red" stroke-width="1"/><line x1="8" y1="13" x2="16" y2="11" stroke="red" stroke-width="1"/></svg>') 12 12, auto;
}

/* Reference Panel Styles */
.reference-panel {
    width: 300px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 15px;
    padding: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    display: flex;
    flex-direction: column;
}

.reference-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.reference-header h4 {
    margin: 0;
    color: #FFD700;
    font-size: 1rem;
}

.reference-controls {
    display: flex;
    gap: 0.5rem;
}

.hide-ref-btn {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 0.3rem 0.6rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8rem;
}

.hide-ref-btn:hover {
    background: rgba(255, 255, 255, 0.2);
}

.reference-image-container {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.reference-image {
    width: 100%;
    max-width: 250px;
    height: auto;
    aspect-ratio: 1;
    object-fit: cover;
    border-radius: 10px;
    border: 2px solid #FFD700;
    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
}

.reference-caption {
    margin-top: 1rem;
    text-align: center;
    color: #FFD700;
    font-weight: bold;
    font-size: 0.9rem;
}

/* Show Reference Panel When Hidden */
.show-reference-panel {
    width: 80px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.show-ref-btn {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 1rem 0.5rem;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.8rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    writing-mode: vertical-rl;
    text-orientation: mixed;
    transition: all 0.3s;
}

.show-ref-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(1.05);
}

.show-ref-btn span:first-child {
    font-size: 1.2rem;
    writing-mode: initial;
}

/* Mobile responsiveness for naming modal */
@media (max-width: 768px) {
    .naming-modal {
        width: 95%;
        padding: 1.5rem;
    }
    
    .naming-header h3 {
        font-size: 1.3rem;
    }
    
    .drawing-name-input {
        font-size: 1rem;
        padding: 0.8rem;
    }
    
    .suggestion-buttons {
        gap: 0.3rem;
    }
    
    .suggestion-btn {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
    }
    
    .naming-actions {
        flex-direction: column;
        gap: 0.8rem;
    }
    
    .cancel-btn, .confirm-btn {
        min-width: 100%;
    }
}

/* Responsive design */
@media (max-width: 1200px) {
    .drawing-area {
        flex-direction: column;
    }
    
    .reference-panel {
        width: 100%;
        max-height: 200px;
        flex-direction: row;
        align-items: center;
        gap: 1rem;
    }
    
    .reference-image-container {
        flex-grow: 0;
    }
    
    .reference-image {
        width: 150px;
        height: 150px;
    }
    
    .show-reference-panel {
        width: 100%;
        height: 60px;
    }
    
    .show-ref-btn {
        flex-direction: row;
        padding: 0.5rem 1rem;
        writing-mode: initial;
        text-orientation: initial;
    }
}

@media (max-width: 768px) {
    .drawing-pad-container {
        width: 95%;
        height: 95vh;
        padding: 1rem;
        max-width: 95vw;
    }
    
    .header {
        flex-direction: column;
        gap: 0.5rem;
        text-align: center;
    }
    
    .title-section {
        align-items: center;
    }
    
    .header-actions {
        flex-direction: row;
        gap: 0.25rem;
        width: 100%;
        justify-content: center;
    }
    
    .timer-display {
        padding: 0.3rem 0.6rem;
    }
    
    .timer {
        font-size: 0.9rem;
    }
    
    .save-btn {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
        min-width: 80px;
    }
    
    .reference-panel {
        max-height: 150px;
    }
    
    .reference-image {
        width: 120px;
        height: 120px;
    }
    
    .gallery-grid {
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    }
    
    .gallery-container {
        width: 95%;
        height: 85vh;
        padding: 1rem;
    }
    
    .toolbar {
        gap: 0.5rem;
    }
    
    .tool-group {
        padding: 0 0.25rem;
    }
}

@media (max-width: 480px) {
    .title {
        font-size: 1.4rem;
    }
    
    .header-actions {
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .save-btn {
        width: 100%;
        max-width: 120px;
    }
    
    .reference-title {
        font-size: 0.8rem;
    }
    
    .reference-image {
        width: 100px;
        height: 100px;
    }
}
</style>