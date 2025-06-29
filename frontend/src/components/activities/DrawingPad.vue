<template>
    <div class="drawing-pad-overlay" @click.self="$emit('close')">
        <div class="drawing-pad-container">
            <div class="header">
                <h2 class="title">🎨 Creative Canvas</h2>
                <button @click="$emit('close')" class="close-btn">×</button>
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
                </div>
            </div>

            <canvas ref="canvasRef" @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing"
                @mouseleave="stopDrawing" :class="{ 'brush-cursor': drawingTool === 'brush' && !isErasing }"></canvas>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

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

// Define resizeCanvas in the setup scope to be accessible for cleanup
const resizeCanvas = () => {
    const canvas = canvasRef.value;
    if (!canvas) return;
    // Match the drawing buffer to the canvas's CSS-defined size
    if (canvas.width !== canvas.clientWidth || canvas.height !== canvas.clientHeight) {
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;
    }
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
};

onMounted(() => {
    const canvas = canvasRef.value;
    if (canvas) {
        ctx = canvas.getContext('2d');
        window.addEventListener('resize', resizeCanvas);
        // We use requestAnimationFrame to ensure layout is calculated before first resize
        requestAnimationFrame(resizeCanvas);
    }
});

onUnmounted(() => {
    window.removeEventListener('resize', resizeCanvas);
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
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
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
    width: 90%;
    max-width: 800px;
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

.title {
    margin: 0;
    font-size: 1.8rem;
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

canvas {
    flex-grow: 1;
    width: 100%;
    border-radius: 15px;
    background-color: #ffffff;
    cursor: crosshair;
    min-height: 0;
}

canvas.brush-cursor {
    cursor: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAPFJREFUGEt1lr0NwjAURc+NASIiJIRCF1I4QGAiIgJFTAk5QBEZgA7IAD2AjsgAStYpX8knaa3p5Zfcn+/uLgqj+M8X+DkY+N0DAw8YBlwA7gC3gDngBhhKa8BfA4eB+wAwwANwA/grsAL8AL4C8A6MHiAczIEvQAXQywf4A8AGEI+gA+gBfAP8A64fBswBC4AnwGHgDHgC7AE3gAegm8wD3gPlWgCXgDHgAVgC7gD/mn/s+sFgwA54XwA2wA2wAnwA3gP2bT/fAMuA+wD45fIAHwApQGv/AVgE/hX+A+wAjg/8Bfye2gD/n6EAAAAASUVORK5CYII='), auto;
}
</style>